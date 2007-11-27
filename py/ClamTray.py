#-----------------------------------------------------------------------------
# Name:        Tray.py
# Product:     ClamWin Free Antivirus
#
# Author:      alch [alch at users dot sourceforge dot net]
#
# Created:     2004/19/03
# Copyright:   Copyright alch (c) 2005
# Licence:
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

#-----------------------------------------------------------------------------
# this code is based on win32gui_taskbar.py demo from Mark Hammond's
# win32 extensions.

import SetUnicode
import RedirectStd
import sys, os, time, tempfile, locale, re, random
import win32api, win32gui, win32con, win32event
import win32process, win32event
import Scheduler
import Config
import Process
import EmailAlert
import threading
import Utils, wxDialogScheduledScan
import version
from I18N import getClamString as _

class MainWindow:
    MENU_OPEN_CLAM, MENU_UPDATE_DB, MENU_CHECK_UPDATE, MENU_CLAMWIN_WEB, MENU_CONFIGURE, MENU_SHOWSCANLOG, \
        MENU_SHOWUPDATELOG, MENU_EXIT, MENU_CONFIGURESCHEDULER,\
        MENU_TERMINATESCHEDULE, MENU_RUNSCHEDULE = range(1023, 1023 + 11)

    ACTIVE_MUTEX='ClamWinTrayMutex01'
    WM_TASKBAR_NOTIFY=win32con.WM_USER+20
    WM_CONFIG_UPDATED=win32con.WM_USER+21
    WM_SHOW_BALLOON=win32con.WM_USER+22

    def __init__(self, config, logon):
        self._config = config
        self._schedulers = []
        self._scheduledScans = []
        self._processes = []
        self._balloon_info = None
        self._balloonThreadLock = threading.Lock()
        msg_TaskbarRestart = win32gui.RegisterWindowMessage("TaskbarCreated");
        message_map = {
                msg_TaskbarRestart: self.OnRestart,
                win32con.WM_DESTROY: self.OnDestroy,
                win32con.WM_COMMAND: self.OnCommand,
                MainWindow.WM_TASKBAR_NOTIFY: self.OnTaskbarNotify,
                MainWindow.WM_CONFIG_UPDATED : self.OnConfigUpdated,
                MainWindow.WM_SHOW_BALLOON : self.OnShowBalloon
        }
        # Register the Window class.
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "ClamWinTrayWindow"
        wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
        wc.hCursor = win32gui.LoadCursor( 0, win32con.IDC_ARROW )
        wc.hbrBackground = win32con.COLOR_WINDOW
        wc.lpfnWndProc = message_map # could also specify a wndproc.
        classAtom = win32gui.RegisterClass(wc)
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow( classAtom, "ClamWin", style, \
                0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, \
                0, 0, hinst, None)
        win32gui.UpdateWindow(self.hwnd)

        # create mutex to prevent further instances
        self._hActiveMutex = win32event.CreateMutex(None, True, self.ACTIVE_MUTEX)
        self._DoCreateIcons()
        self._InitSchedulers(logon)

        # start config monitor thread
        self._configMonitor = MonitorConfig(self.NotifyConfig, (self.hwnd,))
        self._configMonitor.start()

    def _IsProcessRunning(self, proc, wait=False):
        if wait:
            timeout = 5
        else:
            timeout = 0
        try:
            proc.wait(timeout)
        except Exception, e:
            if isinstance(e, Process.ProcessError):
                if e.errno == Process.ProcessProxy.WAIT_TIMEOUT:
                    return True
                else:
                    return False
        return False

    def _StopProcesses(self):
        # check if process is still running
        for proc in self._processes:
            if self._IsProcessRunning(proc):
                # running - kill
                proc.kill()
                #wait to finish
                if self._IsProcessRunning(proc, True):
                    #still running - complain and terminate
                    win32gui.MessageBox(self.hwnd, _('Unable to stop scheduled process, terminating'), _('ClamWin Free Antivirus'), win32con.MB_OK | win32con.MB_ICONSTOP)
                    os._exit(0)
                proc.close()

        self._processes = []

    def _TerminateSchedules(self):
        self._StopProcesses()
        for scheduler in self._schedulers:
            try:
                scheduler.stop()
                # wait for completion
                scheduler.join(2)
            except Exception, e:
                print _('An error occurred whilst terminating scheduler thread. Error: %s') % str(e)
        self._schedulers = []

    def _InitSchedulers(self, logon=False):
        # close all running schedules
        self._TerminateSchedules()

        # load persistent scheduler
        self._scheduledScans = wxDialogScheduledScan.LoadPersistentScheduledScans(
                os.path.join(Utils.GetScheduleShelvePath(self._config), 'ScheduledScans'))

        # create an update schedule to run now if 'Update on Logon' is selected
        if logon and self._config.Get('Updates', 'UpdateOnLogon') == '1':
            # set C locale, otherwise python and wxpython complain
            locale.setlocale(locale.LC_ALL, 'C')

            start_time = time.localtime(time.time() + 120)
            weekday = int(time.strftime('%w', start_time))
            if weekday: weekday -= 1
            else: weekday = 6
            scheduler = Scheduler.Scheduler('Once',
                            time.strftime('%H:%M:%S', start_time),
                            weekday,
                            win32gui.SendMessage, (self.hwnd, win32con.WM_COMMAND, self.MENU_UPDATE_DB, 1),
                            ('ClamWin_Scheduler_Info', 'ClamWin_Upadte_Time'))
            scheduler.start()
            self._schedulers.append(scheduler)

        # create a scheduler thread for DB updates
        if self._config.Get('Updates', 'Enable') == '1':
            scheduler = Scheduler.Scheduler(self._config.Get('Updates', 'Frequency'),
                            self._config.Get('Updates', 'Time'),
                            int(self._config.Get('Updates', 'WeekDay')),
                            win32gui.SendMessage, (self.hwnd, win32con.WM_COMMAND, self.MENU_UPDATE_DB, 1),
                            ('ClamWin_Scheduler_Info', 'ClamWin_Upadte_Time'))
            scheduler.start()
            self._schedulers.append(scheduler)

        # create scheduler threads for all scheduled scans
        for scan in self._scheduledScans:
            if scan.Active:
                scheduler = Scheduler.Scheduler(scan.Frequency,
                            scan.Time,
                            int(scan.WeekDay),
                            self.ScanPath, (self, scan.Path, scan.Description, scan.ScanMemory))
                scheduler.start()
                self._schedulers.append(scheduler)

        # create scheduler thread for program version check
        if self._config.Get('Updates', 'CheckVersion') == '1':
            curDir = Utils.GetCurrentDir(True)
            scheduler = Scheduler.Scheduler('Daily', # check once aday
                            time.strftime('%H:%M:%S', time.localtime(time.time() + random.randint(300, 3600))), # 5 minutes to 1 hour after start
                            1, # unused
                            Utils.SpawnPyOrExe, (os.path.join(curDir, 'ClamWin'), ' --mode=checkversion'),
                            ('ClamWin_CheckVer_Info', 'ClamWin_CheckVer_Time'))
            scheduler.start()
            self._schedulers.append(scheduler)

    def _Terminate(self):
        # terminate running threads
        self._TerminateSchedules()
        if self._configMonitor is not None:
            self._configMonitor.stop()
            self._configMonitor.join(2)
            self._configMonitor = None

    def _DoCreateIcons(self):
        # Try and find a custom icon
        hinst =  win32api.GetModuleHandle(None)
        iconPathName = os.path.abspath(os.path.join(os.path.split(sys.executable)[0],"img/TrayIcon.ico"))
        if not os.path.isfile(iconPathName):
            # Look in the current folder tree.
            iconPathName = "img/TrayIcon.ico"
        if os.path.isfile(iconPathName):
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(hinst, iconPathName, win32con.IMAGE_ICON, 0, 0, icon_flags)
        else:
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, MainWindow.WM_TASKBAR_NOTIFY, hicon, "ClamWin Free Antivirus")
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)

    def OnRestart(self, hwnd, msg, wparam, lparam):
        self._DoCreateIcons()

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        self._Terminate()
        win32event.ReleaseMutex(self._hActiveMutex)
        win32api.CloseHandle(self._hActiveMutex)
        # Terminate the app.
        win32gui.PostQuitMessage(0)

    def OnTaskbarNotify(self, hwnd, msg, wparam, lparam):
        if lparam==win32con.WM_LBUTTONUP:
            pass
        elif lparam==win32con.WM_LBUTTONDBLCLK:
           self.OnCommand(hwnd, win32con.WM_COMMAND, self.MENU_OPEN_CLAM, 0)
        elif lparam==win32con.WM_RBUTTONUP:

            # create scheduler menu
            scheduler_popup = win32gui.CreatePopupMenu()
            win32gui.AppendMenu(scheduler_popup, win32con.MF_STRING,
                self.MENU_CONFIGURESCHEDULER, _("&Configure Scheduler"))

            if not self._processes:
                flags = win32con.MF_GRAYED
            else:
                flags = 0

            # create scheduled tasks menu
            tasks_popup = win32gui.CreatePopupMenu()
            i = 0
            for scan in self._scheduledScans:
                win32gui.AppendMenu(tasks_popup, win32con.MF_STRING,
                    self.MENU_RUNSCHEDULE + i, scan.Description)
                i+=1
            if not i:
                flags2 = win32con.MF_GRAYED
            else:
                flags2 = 0
            win32gui.InsertMenu(scheduler_popup, self.MENU_CONFIGURESCHEDULER,
                            win32con.MF_BYCOMMAND | win32con.MF_POPUP | flags2,
                            tasks_popup, _("&Run Scheduled Scan"))                                            

            win32gui.InsertMenu(scheduler_popup, flags,
                                win32con.MF_BYCOMMAND | win32con.MF_STRING | flags,
                                self.MENU_TERMINATESCHEDULE, _("&Stop All Running Tasks Now"))                        

            # create reports menu
            reports_popup = win32gui.CreatePopupMenu()
            if not len(self._config.Get('ClamAV', 'LogFile')):
                flags = win32con.MF_GRAYED
            else:
                flags = 0
            win32gui.InsertMenu( reports_popup, 0,
                                win32con.MF_BYCOMMAND | win32con.MF_STRING | flags,
                                self.MENU_SHOWSCANLOG, _("&Virus Scan Report"))                        
            if not len(self._config.Get('Updates', 'DBUpdateLogFile')):
                flags = win32con.MF_GRAYED
            else:
                flags = 0
            win32gui.InsertMenu( reports_popup, self.MENU_SHOWSCANLOG,
                                win32con.MF_BYCOMMAND | win32con.MF_STRING | flags,
                                self.MENU_SHOWUPDATELOG, _("&Virus Database Update Report"))                        

            # create main menu
            menu = win32gui.CreatePopupMenu()
            win32gui.AppendMenu( menu, win32con.MF_STRING, self.MENU_OPEN_CLAM, _("&Open ClamWin"))
            win32gui.AppendMenu( menu, win32con.MF_STRING, self.MENU_UPDATE_DB, _("&Download Virus Database Update"))
            win32gui.AppendMenu( menu, win32con.MF_STRING, self.MENU_CONFIGURE, _("&Configure ClamWin"))                   
            win32gui.AppendMenu( menu, win32con.MF_POPUP, scheduler_popup, _("&Scheduler"))                     
            win32gui.AppendMenu( menu, win32con.MF_POPUP, reports_popup, _("Display &Reports"))                
            win32gui.AppendMenu( menu, win32con.MF_SEPARATOR, 0, "" )
            win32gui.AppendMenu( menu, win32con.MF_STRING, self.MENU_CHECK_UPDATE, _("Check &Latest Version"))
            win32gui.AppendMenu( menu, win32con.MF_STRING, self.MENU_CLAMWIN_WEB, _("&Visit ClamWin Website"))
            win32gui.AppendMenu( menu, win32con.MF_SEPARATOR, 0, "" )
            win32gui.AppendMenu( menu, win32con.MF_STRING, self.MENU_EXIT, _("&Exit") )                        

            pos = win32gui.GetCursorPos()
            # See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winui/menus_0hdi.asp
            win32gui.SetForegroundWindow(self.hwnd)
            try:
                win32gui.SetMenuDefaultItem(menu, 0, 1)
            except NameError:
                pass

            win32gui.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, self.hwnd, None)
            win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)

        return 1

    def OnCommand(self, hwnd, msg, wparam, lparam):
        id = win32api.LOWORD(wparam)
        if id == self.MENU_OPEN_CLAM:
            self._ShowClamWin()
        elif id == self.MENU_UPDATE_DB:
            self._UpdateDB(lparam)
        elif id == self.MENU_CHECK_UPDATE:
            self._OpenWebPage(_('http://www.clamwin.com/index.php?option=content&task=view&id=40&Itemid=60&version=')+version.clamwin_version)
        elif id == self.MENU_CLAMWIN_WEB:
            self._OpenWebPage(_('http://www.clamwin.com'))
        elif id == self.MENU_CONFIGURE:
            self._ShowConfigure()
        elif id == self.MENU_SHOWSCANLOG:
            self._ShowLog(self._config.Get('ClamAV', 'LogFile'))
        elif id == self.MENU_SHOWUPDATELOG:
            self._ShowLog(self._config.Get('Updates', 'DBUpdateLogFile'))
        elif id == self.MENU_EXIT:
            self.OnExit()
        elif id == self.MENU_CONFIGURESCHEDULER:
            self._ShowConfigure(True)
        elif id == self.MENU_TERMINATESCHEDULE:
            self._TerminateSchedules()
            self._InitSchedulers()
        elif (id >= self.MENU_RUNSCHEDULE) and \
            (id < self.MENU_RUNSCHEDULE + len(self._scheduledScans)):
                try:
                    path = self._scheduledScans[id - self.MENU_RUNSCHEDULE].Path
                    if path[len(path)-1] == '\\':
                        path = path[:len(path)-1]
                    self._ShowClamWin(path)
                except Exception, e:
                    win32gui.MessageBox(self.hwnd,
                            _('Could not launch ClamWin Scanner. Error: %s') % str(e), 
                            _('ClamWin Free Antivirus'), win32con.MB_OK | win32con.MB_ICONERROR)


    def OnConfigUpdated(self, hwnd, msg, wparam, lparam):
        self._config.Read()
        self._InitSchedulers()

    def OnShowBalloon(self, hwnd, msg, wparam, lparam):
        if self._balloon_info is not None:
            try:
                Utils.ShowBalloon(wparam, self._balloon_info, self.hwnd)
            except Exception, e:
                print _('Could not display balloon tooltip. Error: %s') % str(e)

    def OnExit(self):
        win32gui.DestroyWindow(self.hwnd)

    def _ShowLog(self, logfile):
        try:
            curDir = Utils.GetCurrentDir(True)
            params = (' --mode=viewlog',  '--path="%s"' % logfile)
            Utils.SpawnPyOrExe(os.path.join(curDir, 'ClamWin'), *params)
        except Exception, e:
            win32gui.MessageBox(self.hwnd, _('An error occurred while displaying log file %s.\nError: %s') % (logfile, str(e)),
                                 _('ClamWin Free Antivirus'), win32con.MB_OK | win32con.MB_ICONERROR)                                                               

    def _ShowClamWin(self, path=''):
        try:
            if path:
                params = (' --mode=scanner',  ' --path=\"%s\"' % path)
            else:
                params = (' --mode=main',)
            Utils.SpawnPyOrExe(os.path.join(Utils.GetCurrentDir(True), 'ClamWin'), *params)
        except Exception, e:
            win32gui.MessageBox(self.hwnd, _('An error occurred while starting ClamWin Free Antivirus scanner.\n') + str(e), _('ClamWin Free Antivirus'), win32con.MB_OK | win32con.MB_ICONERROR)                              

    def _UpdateDB(self, hide):
        if not hide:
            try:
                params = (' --mode=update', ' --config_file="%s"' % self._config.GetFilename())
                Utils.SpawnPyOrExe(os.path.join(Utils.GetCurrentDir(True), 'ClamWin'), *params)
            except Exception, e:
                win32gui.MessageBox(self.hwnd, _('An error occurred while starting ClamWin Free Antivirus Update.\n') + str(e), _('ClamWin Free Antivirus'), win32con.MB_OK | win32con.MB_ICONERROR)                                  
        else:
            # update virus db silently
            freshclam_conf = Utils.SaveFreshClamConf(self._config)
            try:
                if not len(freshclam_conf):
                    win32gui.MessageBox(self.hwnd, _('Unable to create freshclam configuration file. Please check there is enough space on the disk'), _('Error'), win32con.MB_OK | win32con.MB_ICONSTOP)
                    return
                # create database folder before downloading
                dbdir = self._config.Get('ClamAV', 'Database')
                if dbdir and not os.path.exists(dbdir):
                    try:
                        os.makedirs(dbdir)
                    except:
                        pass
                updatelog = tempfile.mktemp()
                cmd = '--stdout --datadir="' + dbdir + '"' + \
                        ' --config-file="%s" --log="%s"' % (freshclam_conf, updatelog)
                cmd = '"%s" %s' % (self._config.Get('ClamAV', 'FreshClam'), cmd)
                try:
                    if self._config.Get('UI', 'TrayNotify') == '1':
                        balloon = ((_('Virus database has been updated.'), 0, 
                                   win32gui.NIIF_INFO, 10000),
                                   (_('An error occurred during Scheduled Virus Database Update. Please review the update report.'), 1, 
                                   win32gui.NIIF_WARNING, 30000))
                    else:
                        balloon = None
                    proc = self._SpawnProcess(cmd,
                        'n',
                        self.DBUpdateProcessFinished,
                        (self._config.Get('ClamAV', 'Database'),
                        self._config.Get('Updates', 'DBUpdateLogFile'),
                        updatelog, False,
                        balloon))
                    self._processes.append(proc)
                except Process.ProcessError, e:
                    print _('Unable to spawn scheduled process.\nCommand line: %s\nError: %s') % (cmd , str(e))
                    try:
                        os.remove(freshclam_conf)
                        os.remove(updatelog)
                    except:
                        pass
                    return
                # wait 2 seconds for the process to start, then delete
                # temp file
                try:
                    proc.wait(2)
                except:
                    pass
                os.remove(freshclam_conf)
            except Exception, e:
                print _('Error performing Scheduled Update.'), str(e)
                os.remove(freshclam_conf)

    def _OpenWebPage(self, url):
        try:
            import webbrowser
            webbrowser.open(url)
        except ImportError:
            win32gui.MessageBox(self.hwnd, _('Please point your browser at: %s') % url, _('ClamWin Free Antivirus'), win32con.MB_OK | win32con.MB_ICONINFORMATION)


    def _ShowConfigure(self, switchToSchedule = False):
        try:
            curDir = Utils.GetCurrentDir(True)
            if switchToSchedule:
                mode = 'configure_schedule'
            else:
                mode = 'configure'
            params = (' --mode=%s' % mode,
                        ' --config_file="%s"' % self._config.GetFilename())
            Utils.SpawnPyOrExe(os.path.join(curDir, 'ClamWin'), *params)
        except Exception, e:
            win32gui.MessageBox(self.hwnd, _('An error occurred while starting ClamWin Free Antivirus Preferences.\n') + str(e), _('ClamWin Free Antivirus'), win32con.MB_OK | win32con.MB_ICONERROR)

    # returns process and stdout buffer
    def _SpawnProcess(self, cmd, proc_priority, finished_func, finished_params):
        # initialise environment var TMPDIR
        # for clamav
        try:
            if os.getenv('TMPDIR') is None:
                os.putenv('TMPDIR', tempfile.gettempdir())
            #Utils.SetCygwinTemp()
        except Exception, e:
            print str(e)

        # check that we got the command line
        if cmd is None:
            raise Process.ProcessError(_('Could not start process. No Command Line specified'))                                                     

        # start our process
        try:
            # check if the file exists first
            executable = cmd.split('" ' ,1)[0].lstrip('"')
            if not os.path.exists(executable):
                raise Process.ProcessError(_('Could not start process.\n%s\nFile does not exist.') % executable)                            
            out = OutBuffer(self, finished_func, finished_params)
            proc = Process.ProcessProxy(cmd, stdout=out, priority=proc_priority)
            out.AttachProcess(proc)
            proc.wait(0)
        except Exception, e:
            if isinstance(e, Process.ProcessError):
                if e.errno != Process.ProcessProxy.WAIT_TIMEOUT:
                    raise Process.ProcessError(_('Could not start process:\n%s\nError: %s') % (cmd, str(e)))                     
            else:
                raise Process.ProcessError(_('Could not start process:\n%s\nError: %s') % (cmd, str(e)))                             
        return proc

    def ScanPath(self, path, description, scanMemory):
        scanlog = tempfile.mktemp()
        path = '"%s"' % path.rstrip('\\').strip('"')
        cmd = Utils.GetScanCmd(self._config, path, scanlog, True)
        if scanMemory:
            cmd += " --memory"
            print cmd
        try:
            if self._config.Get('UI', 'TrayNotify') == '1':
                balloon = ((_('Virus has been detected during scheduled scan! Please review the scan report.'), 1, 
                          win32gui.NIIF_ERROR, 30000),
                          (_('An error occurred during scheduled scan. Please review the scan report.'), 0, 
                          win32gui.NIIF_WARNING, 30000))
            else:
                balloon = None

            try:
                priority = self._config.Get('ClamAV', 'Priority')[:1].lower()
            except:
                priority = 'n'
            # clamav stopped writing start time of the scan to the log file
            try:
                file(scanlog, 'wt').write(_('\nScan Started %s') % I18N.getDateTimeString())
            except:
                pass
            proc = self._SpawnProcess(cmd,
                        priority,
                        self.ProcessFinished,
                        (self._config.Get('ClamAV', 'LogFile'),
                        scanlog,
                        self._config.Get('EmailAlerts', 'Enable') == '1',
                        balloon
                        ))
            self._processes.append(proc)
            result = 0
        except Process.ProcessError, e:
            result = -1
            try:
               os.remove(scanlog)
            except:
               pass
            print str(e)
        if self._config.Get('UI', 'TrayNotify') == '1':
            balloon_info = ((_('Running Scheduled Task:\n')+description, 0, 
                            win32gui.NIIF_INFO, 10000),
                            (_('An error occurred whilst running Running Scheduled Task ')+description, 1, 
                            win32gui.NIIF_WARNING, 30000))
            self.ShowBalloon(result, balloon_info)
    ScanPath = staticmethod(ScanPath)

    def NotifyConfig(hwnd):
        win32api.PostMessage(hwnd, MainWindow.WM_CONFIG_UPDATED, 0, 0)
    NotifyConfig = staticmethod(NotifyConfig)

    def DBUpdateProcessFinished(self, process, dbpath, log, appendlog, email_alert, balloon_info):
        self.ProcessFinished(self, process, log, appendlog, email_alert, balloon_info)
    DBUpdateProcessFinished = staticmethod(DBUpdateProcessFinished)


    def ProcessFinished(self, process, log, appendlog, email_alert, balloon_info):
        # send the notification alert if we need to
        if email_alert:
            try:
                if process.wait() == 1:
                    msg = EmailAlert.ConfigVirusAlertMsg(self._config, (appendlog,))
                    msg.Send()
            except Exception, e:
                print _('Could not send email alert. Error: %s') % str(e)

        if not process.isKilled() and balloon_info is not None:
            # show balloon
            self.ShowBalloon(process.wait(), balloon_info)

        # find and remove our process
        try:
            self._processes.remove(process)
        except ValueError:
            # ignore "not in list" errors
            pass

        time.sleep(1)
        maxsize = int(self._config.Get('ClamAV', 'MaxLogSize'))*1048576
        Utils.AppendLogFile(log, appendlog, maxsize)

        try:
            os.remove(appendlog)
        except Exception, e:
            print _('Could not remove file: %s. Error: %s') % (appendlog, str(e))
            
        Utils.CleanupTemp(process.getpid())

    ProcessFinished = staticmethod(ProcessFinished)

    # send message to the main window thread to display balloon notification
    # we need to enclose the call to SendMessage within Lock().acquire()/Lock.release()
    # to ensure that correct self._balloon_info is used when 2 threads want to
    # display balloons simultaneously
    def ShowBalloon(self, result, balloon_info):
        self._balloonThreadLock.acquire()
        try:
            self._balloon_info = balloon_info
            win32api.SendMessage(self.hwnd, MainWindow.WM_SHOW_BALLOON, result, 0)
        finally:
            self._balloon_info = None
            self._balloonThreadLock.release()


# stdout buffer used by ProcessProxy to notify main thread
# when execution is complete
class OutBuffer(Process.IOBuffer):
    def __init__(self, caller, notify, params):
        Process.IOBuffer.__init__(self)
        self.notify = notify
        self._caller = caller
        self._params = params
        self._proc = None

    # we don't need any input or output here
    def _doWrite(self, s):
        return
    def _doRead(self, n):
        return
    def write(self, s):
        return
    def writelines(self, list):
        return
    def read(self, n=-1):
        return
    def readline(self, n=None):
        return
    def readlines(self):
        return

    def _doClose(self):
        self.notify(self._caller, self._proc, *self._params)
        if self._proc:
            del self._proc
        Process.IOBuffer._doClose(self)

    def AttachProcess(self, proc):
        self._proc = proc



# this thread monitors changes to config files
#  and notifies tray to reload if a change occurs
class MonitorConfig(threading.Thread):
    def __init__(self, notify, args):
        self.notify = notify
        self.args = args
        self._terminate = False
        threading.Thread.__init__(self)

    def __del__(self):
        self.stop()

    def run(self):
        self._terminate = False
        try:
           hEvent = win32event.CreateEvent(None, True, False, Utils.CONFIG_EVENT)
        except win32api.error:
            return

        while not self._terminate:
            wait = win32event.WaitForSingleObject(hEvent, 1000);
            if wait != win32event.WAIT_TIMEOUT:
                self.notify(*self.args)

    def stop(self):
        if not self.isAlive():
            return
        self._terminate = True

    def is_cancelled(self):
        return self._cancelled

    def get_returnCode(self):
        return self._ret



def main():
    # set C locale, otherwise python and wxpython complain
    locale.setlocale(locale.LC_ALL, 'C')

    # get the directory of our exetutable file
    # when running as pyexe built module
    currentDir = Utils.GetCurrentDir(True)
    os.chdir(currentDir)

    Utils.CreateProfile()

    # see if we are already running and exit if so
    try:
        # try to acquire our active mutex
        hMutex = win32event.OpenMutex(win32con.SYNCHRONIZE, False, MainWindow.ACTIVE_MUTEX)
        # could open it - most likely another window is active
        # just to be sure wait for it to see if it is claimed
        if win32event.WaitForSingleObject(hMutex, 0) == win32event.WAIT_TIMEOUT:
            # mutex is claimed, another window is already running - terminate
            return
        win32api.CloseHandle(hMutex)
    except win32api.error:
        pass

    conf_file = None
    for arg in sys.argv[1:]:
        if arg.find('--config_file=') == 0:
            conf_file = Utils.SafeExpandEnvironmentStrings(arg[len('--config_file='):])
    if conf_file is None:
        conf_file = os.path.join(Utils.GetProfileDir(True),'ClamWin.conf')

    if not os.path.isfile(conf_file):
        conf_file = 'ClamWin.conf'
    config = Config.Settings(conf_file)
    config.Read()

    logon = False
    for arg in sys.argv[1:]:
        if arg == '--logon':
            logon = True
    w=MainWindow(config, logon)
    win32gui.PumpMessages()

if __name__=='__main__':
    main()
