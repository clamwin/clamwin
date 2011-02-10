#-----------------------------------------------------------------------------
#Boa:Dialog:wxDialogStatus

#-----------------------------------------------------------------------------
# Name:        wxDialogStatus.py
# Product:     ClamWin Free Antivirus
#
# Author:      alch [alch at users dot sourceforge dot net]
#
# Created:     2004/19/03
# Copyright:   Copyright alch (c) 2004
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

from wxPython.wx import *
from wxPython.lib.throbber import Throbber
from threading import *
from throb import throbImages
import string
import time
import tempfile
import Process
import os, sys
import re
import MsgBox
import Utils
import wxDialogUtils
import win32gui
import platform

_WAIT_TIMEOUT = 5
if sys.platform.startswith("win"):
    import win32event, win32api, winerror, win32con, win32gui
    _KILL_SIGNAL = None
    _WAIT_NOWAIT = 0
    _NEWLINE_LEN=2
else:
    import signal, os
    _KILL_SIGNAL = signal.SIGKILL
    _WAIT_NOWAIT = os.WNOHANG
    _NEWLINE_LEN=1



class StatusUpdateBuffer(Process.IOBuffer):
    def __init__(self,  caller, update, notify):
        Process.IOBuffer.__init__(self)
        self._caller = caller
        self.update = update
        self.notify = notify

    def _doWrite(self, s):
        if self.update is not None:
            # sometimes there is more than one line in the buffer
            # so we need to call update method for every new line
            lines = s.replace('\r', '\n').splitlines(True)
            for line in lines:
                self.update(self._caller, line)
            # do not call original implementation
            # Process.IOBuffer._doWrite(self, s)

    def _doClose(self):
        if self.notify is not None:
            self.notify(self._caller)
        Process.IOBuffer._doClose(self)

# custom command events sent from worker thread when it finishes
# and when status message needs updating
# the handler updates buttons and status text
THREADFINISHED = wxNewEventType()
def EVT_THREADFINISHED( window, function ):
    window.Connect( -1, -1, THREADFINISHED, function )

class ThreadFinishedEvent(wxPyCommandEvent):
    eventType = THREADFINISHED
    def __init__(self, windowID):
        wxPyCommandEvent.__init__(self, self.eventType, windowID)

    def Clone( self ):
        self.__class__( self.GetId() )

THREADUPDATESTATUS = wxNewEventType()
def EVT_THREADUPDATESTATUS( window, function ):
    window.Connect( -1, -1, THREADUPDATESTATUS, function )

class ThreadUpdateStatusEvent(wxPyCommandEvent):
    eventType = THREADUPDATESTATUS
    def __init__(self, windowID, text, append, std_err=False):
        self.text = text
        self.append = append
        self.std_err = std_err
        wxPyCommandEvent.__init__(self, self.eventType, windowID)

    def Clone( self ):
        self.__class__( self.GetId() )

def create(parent, cmd, logfile, priority, bitmap_mask, notify_params=None):
    return wxDialogStatus(parent, cmd, logfile, priority, bitmap_mask, notify_params)

[wxID_WXDIALOGSTATUS, wxID_WXDIALOGSTATUSBUTTONSAVE,
 wxID_WXDIALOGSTATUSBUTTONSTOP, wxID_WXDIALOGSTATUSSTATICBITMAP1,
 wxID_WXDIALOGSTATUSTEXTCTRLSTATUS,
] = map(lambda _init_ctrls: wxNewId(), range(5))

class wxDialogStatus(wxDialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_WXDIALOGSTATUS, name='wxDialogStatus',
              parent=prnt, pos=wxPoint(449, 269), size=wxSize(568, 392),
              style=wxDEFAULT_DIALOG_STYLE, title='ClamWin Free Antivirus Status')
        self.SetClientSize(wxSize(560, 365))
        self.SetAutoLayout(false)
        self.Center(wxBOTH)
        self.SetToolTipString('')
        EVT_CLOSE(self, self.OnWxDialogStatusClose)
        EVT_INIT_DIALOG(self, self.OnInitDialog)

        winstyle = wxTAB_TRAVERSAL | wxTE_RICH | wxTE_MULTILINE | wxTE_READONLY
        # enable wxTE_AUTO_URL on XP only
        # 98 produces some weird scrolling behaviour
        if win32api.GetVersionEx()[0] >= 5 and not self._scan:
            winstyle = winstyle | wxTE_AUTO_URL

        self.textCtrlStatus = wxTextCtrl(id=wxID_WXDIALOGSTATUSTEXTCTRLSTATUS,
              name='textCtrlStatus', parent=self, pos=wxPoint(89, 11),
              size=wxSize(455, 300),
              style=winstyle, value='')

        self.staticBitmap1 = wxStaticBitmap(bitmap=wxNullBitmap,
              id=wxID_WXDIALOGSTATUSSTATICBITMAP1, name='staticBitmap1',
              parent=self, pos=wxPoint(16, 9), size=wxSize(56, 300),
              style=wxTRANSPARENT_WINDOW)

        self.buttonStop = wxButton(id=wxID_WXDIALOGSTATUSBUTTONSTOP,
              label='&Stop', name='buttonStop', parent=self, pos=wxPoint(291,
              328), size=wxSize(85, 24), style=0)
        self.buttonStop.Enable(True)
        self.buttonStop.SetDefault()
        EVT_BUTTON(self.buttonStop, wxID_WXDIALOGSTATUSBUTTONSTOP,
              self.OnButtonStop)

        self.buttonSave = wxButton(id=wxID_WXDIALOGSTATUSBUTTONSAVE,
              label='S&ave Report', name='buttonSave', parent=self,
              pos=wxPoint(192, 328), size=wxSize(86, 24), style=0)
        self.buttonSave.Enable(False)
        EVT_BUTTON(self.buttonSave, wxID_WXDIALOGSTATUSBUTTONSAVE,
              self.OnButtonSave)

    def __init__(self, parent, cmd, logfile, priority='n', bitmapMask="", notify_params=None):
        self._autoClose = False
        self._closeRetCode = None
        self._cancelled = False
        self._logfile = logfile
        self._returnCode = -1
        self.terminating = False
        self._out = None
        self._proc = None
        self._notify_params = notify_params
        self._scan = (bitmapMask != 'update')
        self._previousStart = 0
        self._alreadyCalled = False
        self._err_text = ""

        self._init_ctrls(parent)


        # bind thread notification events
        EVT_THREADFINISHED(self, self.OnThreadFinished)
        EVT_THREADUPDATESTATUS(self, self.OnThreadUpdateStatus)

        # add url click handler
        EVT_TEXT_URL(self, wxID_WXDIALOGSTATUSTEXTCTRLSTATUS, self.OnClickURL)

        # initilaise our throbber (an awkward way to display animated images)
        images = [throbImages.catalog[i].getBitmap()
                  for i in throbImages.index
                  if i.find(bitmapMask) != -1]
        self.throbber = Throbber(self, -1, images, frameDelay=0.1,
                  pos=self.staticBitmap1.GetPosition(), size=self.staticBitmap1.GetSize(),
                  style=self.staticBitmap1.GetWindowStyleFlag(), useParentBackground = True, name='staticThrobber')


        # set window icons
        icons = wxIconBundle()
        icons.AddIconFromFile('img/FrameIcon.ico', wxBITMAP_TYPE_ICO)
        self.SetIcons(icons)

        # change colour of read-only controls (gray)
        self.textCtrlStatus.SetBackgroundColour(wxSystemSettings_GetColour(wxSYS_COLOUR_BTNFACE))

        # spawn and monitor our process
        # clamav stopped writing start time of the scan to the log file
        try:
            file(logfile, 'wt').write('\nScan Started %s' % time.ctime(time.time()))
        except:
            pass
        try:
            self._SpawnProcess(cmd, priority)
        except Process.ProcessError, e:
            event = ThreadUpdateStatusEvent(self.GetId(), str(e), False)
            self.GetEventHandler().AddPendingEvent(event)
            #event = ThreadFinishedEvent(self.GetId())
            #self.GetEventHandler().AddPendingEvent(event)

    def SetAutoClose(self, autoClose, closeRetCode=None):
        self._autoClose = autoClose
        self._closeRetCode = closeRetCode


    def OnWxDialogStatusClose(self, event):
         self.terminating = True
         self._StopProcess()
         event.Skip()

    def _IsProcessRunning(self, wait=False):
        if self._proc is None:
            return False

        if wait:
            timeout = _WAIT_TIMEOUT
        else:
            timeout = _WAIT_NOWAIT
        try:
            self._proc.wait(timeout)
        except Exception, e:
            if isinstance(e, Process.ProcessError):
                if e.errno == Process.ProcessProxy.WAIT_TIMEOUT:
                    return True
                else:
                    return False
        return False

    def _StopProcess(self):
        # check if process is still running
        if self._IsProcessRunning():
            # still running - kill
            # terminate process and use KILL_SIGNAL to terminate gracefully
            # do not wait too long for the process to finish
            self._proc.kill(sig=_KILL_SIGNAL)

            #wait to finish
            if self._IsProcessRunning(True):
                # still running, huh
                # kill unconditionally
                try:
                    self._proc.kill()
                except Process.ProcessError:
                    pass

                # last resort if failed to kill the process
                if self._IsProcessRunning():
                    MsgBox.ErrorBox(self, 'Unable to stop runner thread, terminating')
                    os._exit(0)

            self._proc.close()
            self._out.close()
            self._err.close()

    def OnButtonStop(self, event):
        if self._IsProcessRunning():
            self._cancelled = True
            self._StopProcess()
        else:
            self.Close()

    def OnButtonSave(self, event):
        filename = "clamav_report_" + time.strftime("%d%m%y_%H%M%S")
        if sys.platform.startswith("win"):
            filename +=  ".txt"
            mask = "Report files (*.txt)|*.txt|All files (*.*)|*.*"
        else:
            mask = "All files (*)|*"
        dlg = wxFileDialog(self, "Choose a file", ".", filename, mask, wxSAVE)
        try:
            if dlg.ShowModal() == wxID_OK:
                filename = dlg.GetPath()
                try:
                    file(filename, "w").write(self.textCtrlStatus.GetLabel())
                except:
                    dlg = wxMessageDialog(self, 'Could not save report to the file ' + \
                                            filename + ". Please check that you have write "
                                            "permissions to the folder and there is enough space on the disk.",
                      'ClamWin Free Antivirus', wxOK | wxICON_ERROR)
                    try:
                        dlg.ShowModal()
                    finally:
                        dlg.Destroy()
        finally:
            dlg.Destroy()


    def ThreadFinished(owner):
        if owner.terminating:
            return
        event = ThreadFinishedEvent(owner.GetId())
        owner.GetEventHandler().AddPendingEvent(event)
    ThreadFinished = staticmethod(ThreadFinished)

    def ThreadUpdateStatus(owner, text, append=True):
        if owner.terminating:
            return
        event = ThreadUpdateStatusEvent(owner.GetId(), text, append)
        owner.GetEventHandler().AddPendingEvent(event)
    ThreadUpdateStatus = staticmethod(ThreadUpdateStatus)
    
    def ThreadUpdateStatusErr(owner, text, append=True):
        if owner.terminating:
            return

        event = ThreadUpdateStatusEvent(owner.GetId(), text, append, True)
        owner.GetEventHandler().AddPendingEvent(event)
    ThreadUpdateStatusErr = staticmethod(ThreadUpdateStatusErr)


    def OnThreadFinished(self, event):
        if self._alreadyCalled:
            return

        self._alreadyCalled = True

        time.sleep(0.5)

        Utils.CleanupTemp(self._proc.getpid())

        if(platform.win32_ver()[1] < '6.1') or (not Utils.IsWow64()):
		    self.buttonSave.Enable(True)
        self.throbber.Rest()
        self.buttonStop.SetFocus()
        self.buttonStop.SetLabel('&Close')
        
        if self._scan:
            self.SetTitle("ClamWin Free Antivirus: Scan Complete")
        else:
            self.SetTitle("ClamWin Free Antivirus: Download Complete")
        

        data = ""
        if self._logfile is not None:
            try:
                # read last 30000 bytes form the log file
                # as our edit control is incapable of displaying more
                maxsize = 29000
                flog = file(self._logfile, 'rt')
                flog.seek(0, 2)
                size = flog.tell()
                if size > maxsize:
                    flog.seek(-maxsize, 2)
                else:
                    flog.seek(0, 0)
                truncate_pos = flog.tell()
                data = data + flog.read()
                flog.close()
                flog = file(self._logfile, 'a+')
                flog.truncate(truncate_pos)
                
            except Exception, e:
                print 'OnThreadFinished: Could not read from log file %s. Error: %s' % (self._logfile, str(e))
                data = self.textCtrlStatus.GetLabel()

        rtfdata = Utils.ReformatLog(data, win32api.GetVersionEx()[0] >= 5, self._err_text)
        
        if self._logfile is not None:
            try:
                flog = file(self._logfile, 'a')
                flog.write(Utils.ReformatLog(data, False, self._err_text))
            except Exception, e:
                print 'OnThreadFinished: Could not write to log file %s. Error: %s' % (self._logfile, str(e))
                                                   

        if len(data.splitlines()) > 1:
            self.ThreadUpdateStatus(self, rtfdata, False)

        if not self._cancelled:
           self.ThreadUpdateStatus(self, "\n--------------------------------------\nCompleted\n--------------------------------------\n")
        else:
           self.ThreadUpdateStatus(self, "\n--------------------------------------\nCancelled\n--------------------------------------\n")

        win32api.PostMessage(self.textCtrlStatus.GetHandle(), win32con.EM_SCROLLCARET, 0, 0)
        
        self.textCtrlStatus.SetInsertionPointEnd()
        self.textCtrlStatus.ShowPosition(self.textCtrlStatus.GetLastPosition())


        try:
            self._returnCode = self._proc.wait(_WAIT_TIMEOUT)
        except:
            self._returnCode = -1

        if self._cancelled:
            self._returnCode = 0

        if (self._notify_params is not None) and (not self._cancelled) and (self._returnCode not in (54, 56)):
            Utils.ShowBalloon(self._returnCode, self._notify_params)

        # close the window automatically if requested
        if self._autoClose and \
           (self._closeRetCode is None or self._closeRetCode == self._returnCode):
            time.sleep(0)
            e = wxCommandEvent(wxEVT_COMMAND_BUTTON_CLICKED, self.buttonStop.GetId())
            self.buttonStop.AddPendingEvent(e)

    def OnThreadUpdateStatus(self, event):
        ctrl = self.textCtrlStatus
        lastPos = ctrl.GetLastPosition()
        text = event.text
        #if not self._scan:
        text = Utils.ReplaceClamAVWarnings(text)
        if event.std_err:
            self._err_text = self._err_text + text
            # print only FP from stderr and ignore the rest
            if not text.endswith('FALSE POSITIVE FOUND\n'):
                return
            
        if event.append == True:
            # Check if we reached 30000 characters
            # and need to purge topmost line
            if lastPos + len(text) + _NEWLINE_LEN >= 30000:
                ctrl.Clear()
                self._previousStart = 0
                lastPos = 0
            # detect progress message in the new text
            #print_over = re.search('\[( {0,2}\d{1,3}\%)?[|/\-\\\*]?\]',
            #    ctrl.GetRange(self._previousStart, lastPos)) is not None
            curtext = ctrl.GetRange(self._previousStart, lastPos)
            print_over = curtext.endswith(']\n') and \
                         (self._scan or \
                         not ctrl.GetRange(self._previousStart, lastPos).endswith('100%]\n'))
            if print_over:
                # prevent form blinking text by disabling richedit selection here
                win32api.SendMessage(ctrl.GetHandle(),Utils.EM_HIDESELECTION, 1, 0)
                # replace the text
                ctrl.Replace(self._previousStart, ctrl.GetLastPosition(), text)

                win32api.PostMessage(self.textCtrlStatus.GetHandle(), win32con.EM_SCROLLCARET, 0, 0)
                lastPos = self._previousStart
            else:
                if text != '\n':
                    ctrl.AppendText(text)
            # highlight FOUND entries in red
            # FP entries in BLUE
            if text.endswith(' FOUND\n'):
                if event.std_err:
                    col = wxColour(0,0,255)
                else:
                    col = wxColour(128,0,0)
                
                ctrl.SetStyle(lastPos, ctrl.GetLastPosition() - 1,
                        wxTextAttr(colText = col,
                        font = wxFont(0, wxDEFAULT, wxNORMAL, wxBOLD, False)))                                     
                
        else:
            ctrl.Clear()
            ctrl.SetDefaultStyle(wxTextAttr(wxNullColour))
            ctrl.SetValue(text)

        # this is thread unsafe however it doesn't matter as only one thread writes
        # to the status window
        self._previousStart = lastPos



    def GetExitCode(self):
        return self._returnCode

    def _SpawnProcess(self, cmd, priority):
        # initialise environment var TMPDIR
        try:
            if os.getenv('TMPDIR') is None:
                os.putenv('TMPDIR', tempfile.gettempdir())
        except Exception, e:
            print str(e)

        # check that we got the command line
        if cmd is None:
            raise Process.ProcessError('Could not start process. No Command Line specified')

        # start our process
        try:
            # check if the file exists first
            executable = cmd.split('" ' ,1)[0].lstrip('"')
            if not os.path.exists(executable):
                raise Process.ProcessError('Could not start process.\n%s\nFile does not exist.' % executable)
            # create our stdout/stderr implementation that updates status window
            self._alreadyCalled = False
            self._out = StatusUpdateBuffer(self, self.ThreadUpdateStatus, self.ThreadFinished)
            self._err = StatusUpdateBuffer(self, self.ThreadUpdateStatusErr, None)
            self._proc = Process.ProcessProxy(cmd, stdout=self._out, stderr=self._err, priority=priority)
            self._proc.wait(_WAIT_NOWAIT)
        except Exception, e:
            if isinstance(e, Process.ProcessError):
                if e.errno != Process.ProcessProxy.WAIT_TIMEOUT:
                    raise Process.ProcessError('Could not start process:\n%s\nError: %s' % (cmd, str(e)))
            else:
                raise Process.ProcessError('Could not start process:\n%s\nError: %s' % (cmd, str(e)))

    def OnInitDialog(self, event):
        # start animation
        # we need to have our window drawn before that
        # to display transparent animation properly
        # therefore start it in OnInitDialog
        try:
            self.throbber.Start()
            win32gui.SetForegroundWindow(self.GetHandle())
        except:
            pass
        event.Skip()

    def OnClickURL(self, event):
        if event.GetMouseEvent().LeftIsDown():
            url = self.textCtrlStatus.GetRange(event.GetURLStart(), event.GetURLEnd())
            try:
                wxDialogUtils.wxGoToInternetUrl(url)
            except:
                pass
        event.Skip()

