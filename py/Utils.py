#-----------------------------------------------------------------------------
# Name:        Utils.py
# Product:     ClamWin Free Antivirus
#
# Author:      alch [alch at users dot sourceforge dot net]
#
# Created:     2004/22/04
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

#-----------------------------------------------------------------------------
import os, sys, time, tempfile, shutil, locale
import Config, ConfigParser
import re, fnmatch, urllib2
import _winreg

import win32api, win32con, win32gui, win32event, win32con, pywintypes
from win32com.shell import shell, shellcon
if win32api.GetVersionEx()[3] != win32con.VER_PLATFORM_WIN32_WINDOWS:
    import win32security

from ctypes import *
from ctypes.wintypes import DWORD

EM_AUTOURLDETECT=1115
EM_HIDESELECTION=1087
CONFIG_EVENT='ClamWinConfigUpdateEvent01'
_FRESHCLAM_CONF_GENERAL = """
DNSDatabaseInfo current.cvd.clamav.net
DatabaseMirror %s
MaxAttempts 3
"""
_FRESHCLAM_CONF_PROXY = """
HTTPProxyServer %s
HTTPProxyPort %s
"""
_FRESHCLAM_CONF_PROXY_USER = """
HTTPProxyUsername %s
HTTPProxyPassword %s
"""

def _ShowOwnBalloon(title, text, icon, hwnd, timeout):
    import BalloonTip
    hwnd = win32gui.FindWindow("Shell_TrayWnd", "")
    hwnd = win32gui.FindWindowEx(hwnd, 0, "TrayNotifyWnd", "")
    rect = win32gui.GetWindowRect(hwnd)
    flags = BalloonTip.SHOW_CLOSE_BUTTON|BalloonTip.SHOW_INNER_SHADOW|\
            BalloonTip.SHOW_TOPMOST|BalloonTip.CLOSE_ON_KEYPRESS|\
            BalloonTip.CLOSE_ON_LBUTTON_DOWN|\
            BalloonTip.CLOSE_ON_MBUTTON_DOWN|\
            BalloonTip.CLOSE_ON_RBUTTON_DOWN

    # find and close existing notification
    hExistingWnd = None
    wnd_classes = (BalloonTip.SHADOWED_CLASS, BalloonTip.SHADOWLESS_CLASS)
    for wnd_class in wnd_classes:
        try:
            hExistingWnd = win32gui.FindWindow(wnd_class, None)
            break
        except Exception, e:
            pass
    if hExistingWnd is not None:
        win32api.SendMessage(hExistingWnd, win32con.WM_CLOSE, 0, 0)

    #display balloon tooltip
    BalloonTip.ShowBalloonTip(title, text, (rect[0], rect[1]), icon,
                            flags, hwnd, '', timeout)

# balloon_info tuple contains 2 tuples for error and success notifications
# each tuple has (HeaderMessage, Expected Retcode, ICON_ID, Timeout)
def ShowBalloon(ret_code, balloon_info, hwnd = None, wait = False):
    if sys.platform.startswith("win"):
        # no hwnd supplied - find it
        if hwnd is None:
            try:
                hwnd = win32gui.FindWindow('ClamWinTrayWindow', 'ClamWin')
            except:
                return
        try:
            if balloon_info[0] is None:
                tuple = balloon_info[1]
            elif balloon_info[1] is None:
                tuple = balloon_info[0]
            elif ret_code == balloon_info[0][1]:
                tuple = balloon_info[0]
            elif ret_code != balloon_info[1][1]:
                tuple = balloon_info[1]
            else:
                return

            title = 'ClamWin Free Antivirus'
            txt = tuple[0]
            icon = tuple[2]
            timeout = tuple[3]

            # there is not balloon tips on windows 95/98/NT
            # (windows ME with balloons implemented has version 4.9)
            # need to display custom notification
            version = win32api.GetVersionEx()
            if version[0] == 4 and version[1] < 90:
                if icon == win32gui.NIIF_INFO:
                    icon = win32con.IDI_INFORMATION
                elif icon == win32gui.NIIF_WARNING:
                    icon = win32con.IDI_WARNING
                elif icon == win32gui.NIIF_ERROR:
                    icon = win32con.IDI_ERROR
                elif icon == win32gui.NIIF_NONE:
                    icon = 0
                _ShowOwnBalloon(title, txt, icon, hwnd, timeout)
                if wait:
                    i = 0
                    while i < timeout/500:
                        win32gui.PumpWaitingMessages()
                        time.sleep(0.5)
                        i+=1
            else:
                nid = (hwnd, 0, win32gui.NIF_INFO, 0, 0, "", txt, timeout, title, icon)
                win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)
        except Exception, e:
            print 'Could not display notification. Error: %s' % str(e)

def GetCurrentDir(bUnicode):
    if sys.platform.startswith("win") and hasattr(sys, "frozen"):
        # get current dir where the file was executed form
        if sys.frozen == "dll":
            this_filename = win32api.GetModuleFileName(sys.frozendllhandle)
        else:
            this_filename = sys.executable
        currentDir = os.path.split(this_filename)[0]

        # attempt to read the config from the working folder
        conf = Config.Settings(os.path.join(currentDir, 'ClamWin.conf'))

        # not a standalone version
        if not conf.Read() or conf.Get('UI', 'Standalone') != '1':
            try:
                # try HKCU first and then HKLM keys
                # (this is to enable non admin user to install and use clamwin)
                try:
                    key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, 'Software\\ClamWin')
                except win32api.error:
                    key = win32api.RegOpenKeyEx(win32con.HKEY_LOCAL_MACHINE, 'Software\\ClamWin')
                currentDir = SafeExpandEnvironmentStrings(win32api.RegQueryValueEx(key, 'Path')[0])
            except win32api.error:
                pass
    else:
        try:
            currentDir = os.path.split(os.path.abspath(__file__))[0]
        except NameError: # No __file__ attribute (in boa debugger)
            currentDir = os.path.split(os.path.abspath(sys.argv[0]))[0]
    if bUnicode and sys.platform.startswith("win"):
        # change encoding to proper unicode
        currentDir = pywintypes.Unicode(currentDir)
    return currentDir

def GetProfileDir(bUnicode):
    try:
        if sys.platform.startswith("win"):
            # read template config file
            conf = Config.Settings(os.path.join(GetCurrentDir(bUnicode), 'ClamWin.conf'))
            if conf.Read(template = True) and conf.Get('UI', 'Standalone') == '1':
                profileDir = GetCurrentDir(bUnicode)
            else:
                profileDir = shell.SHGetSpecialFolderPath(0, shellcon.CSIDL_APPDATA, True)
                profileDir = os.path.join(profileDir, '.clamwin')
                # change encoding to proper unicode
                if bUnicode:
                    profileDir = pywintypes.Unicode(profileDir)
        else:
            profileDir = os.path.join(os.path.expanduser('~'), '.clamwin')
    except Exception, e:
        print 'Could not get the profile folder. Error: %s' % str(e)
        profileDir = GetCurrentDir(bUnicode)
    return profileDir

def CopyFile(src, dst, overwrite = False):
    copied = False
    if overwrite or \
        (not os.path.isfile(dst) and os.path.isfile(src)):
        try:
            shutil.copyfile(src, dst)
            copied = True
        except Exception, e:
            print 'Could not copy %s to %s. Error: %s' % (src, dst, str(e))
    return copied


# since ver 0.34 config files are stored in user's home directory
# but installer puts the template version to the program folder
# which an admin can preconfigure for all new users
# then confing and scheduler info files are copied
# at runtime to user's home dir
# only if these files are not yet present in the home dir
def CreateProfile():
    curDir = GetCurrentDir(True)
    profileDir = GetProfileDir(True)

    # read template config file
    conf = Config.Settings(os.path.join(curDir, 'ClamWin.conf'))
    if not conf.Read(template = True):
        return

    # check for standalone flag and exit (don't copy anything)
    if conf.Get('UI', 'Standalone') == '1':
        return

    # create profile dir
    try:
        if not os.path.isdir(profileDir):
            os.makedirs(profileDir)
    except Exception, e:
        print 'Could not create profile directory %s. Error: %s' % (profileDir, str(e))

    # copy configuration file
    copied = CopyFile(os.path.join(curDir, 'ClamWin.conf'),
                     os.path.join(profileDir, 'ClamWin.conf'))
    if copied:
        # copy scheduled scans info
        shelvePath = conf.Get('Schedule', 'Path')
        # no [Schedule]-Path in conf file, copy schedule info across
        if not shelvePath:
            CopyFile(os.path.join(curDir, 'ScheduledScans'),
                    os.path.join(profileDir, 'ScheduledScans'))

def GetScheduleShelvePath(config):
    # In some rare cases (clamwin plugin to BartPE <http://oss.netfarm.it/winpe/>)
    # path to Shelve may be not in the current dir
    shelvePath = config.Get('Schedule', 'Path')
    if not len(shelvePath):
        shelvePath = GetProfileDir(True)
    else:
        if sys.platform.startswith("win"):
            shelvePath = pywintypes.Unicode(shelvePath)
            shelvePath = SafeExpandEnvironmentStrings(shelvePath)
    return shelvePath

# we want to be user-friendly and determine should
# we use 24 or 12 hour clock
# on Win32 this is a bit of a hack because GetTimeFormat() is
# not available and time.strftime('%X', t) tends to return
# 24 hr format regardless the regional settings
# therefore we use repr(pywintypes.Time()) that calls
# GetTimeFormat() internally. This should work unless
# pywintypes.Time().repr() changes
def IsTime24():
    # set C locale, otherwise python and wxpython complain
    locale.setlocale(locale.LC_ALL, 'C')
    t = time.localtime()
    if sys.platform.startswith("win"):
        import pywintypes
        timestr = repr(pywintypes.Time(t))
    else:
        timestr = time.strftime('%X', t)
    return not time.strftime('%p', t) in timestr


# use secure mkstemp() in python 2.3 and less secure mktemp/open combination in 2.2
def SafeTempFile():
    fd = -1
    name = ''
    try:
        if sys.version_info[0] < 2 or sys.version_info[1] < 3:
            name = tempfile.mktemp()
            fd = os.open(name, os.O_WRONLY|os.O_CREAT)
        else:
            fd, name = tempfile.mkstemp(text=True)
    except Exception, e:
        print 'cannot create temp file. Error: ' + str(e)
    return (fd, name)

def SaveFreshClamConf(config):
        data = _FRESHCLAM_CONF_GENERAL % config.Get('Updates', 'DBMirror')
        if len(config.Get('Proxy', 'Host')):
            data += _FRESHCLAM_CONF_PROXY % \
                    (config.Get('Proxy', 'Host'), config.Get('Proxy', 'Port'))
        if len(config.Get('Proxy', 'User')):
            data += _FRESHCLAM_CONF_PROXY_USER % \
                (config.Get('Proxy', 'User'), config.Get('Proxy', 'Password'))
                
        if len(config.Get('ClamAV', 'FreshClamParams')):
            data += '\n' + config.Get('ClamAV', 'FreshClamParams')
            
        print 'freshclam.conf:\n', data

        fd, name = SafeTempFile()
        try:
            os.write(fd, data)
        finally:
            if fd != -1:
                os.close(fd)
        return name

def GetExcludeSysLockedFiles():
    configDir = os.path.join(win32api.GetSystemDirectory(), 'config')
    regFiles = ('default', 'SAM', 'SECURITY',
             'software', 'software.alt', 'system',
             'system.alt')
    ret = ''
    for regFile in regFiles:
        ret += ' --exclude="%s"' % os.path.join(configDir, regFile).replace('\\', '\\\\')
    # add --exlude=win386.swp to fix the bug 939877
    # see http://sourceforge.net/tracker/index.php?func=detail&aid=939877&group_id=105508&atid=641462
    if win32api.GetVersionEx()[3] == win32con.VER_PLATFORM_WIN32_WINDOWS:
        ret += ' --exclude=win386.swp --exclude=pagefile.sys'

    return ret


def GetScanCmd(config, path, scanlog, noprint = False):
    # append \ to a DRIVE letter for regex matcher
    # i.e C: will become C:\


    # if path is None then we are scanning computer memory
    if path != None:
        path = re.sub('([A-Za-z]):("|$)', r'\1:\\\\\2', path)
        print "Scanning: %s" % path
    else:
        print "Scanning computer memory"


    # shared params between memory and file scanning
    cmd = '--tempdir "%s"' % tempfile.gettempdir().rstrip('\\')


    # 22 July 2006
    # added --keep-mbox to leave thunderbird files intact when removing or quarantining
    cmd += ' --keep-mbox --stdout --database="%s" --log="%s"' % \
            (config.Get('ClamAV', 'Database'), scanlog)

    # 1 Nov 2008
    # enable phishing through advanced params for GuitarBob                    
    clamscanParams = config.Get('ClamAV', 'ClamScanParams')
    if clamscanParams != '':
        if clamscanParams.find('--enable-phishing') == -1:
            cmd += ' --no-phishing-sigs --no-phishing-scan-urls'
        else:
            clamscanParams = clamscanParams.replace('--enable-phishing', '')
        cmd += ' ' + clamscanParams
        

    if config.Get('ClamAV', 'Debug') == '1':
        cmd += ' --debug'
    #this disables oversized zip checking
    # no longer needed >= 0.93
    #cmd += ' --max-ratio=0'
    
    if config.Get('ClamAV', 'ScanOle2') != '1':
        cmd += ' --no-ole2'
    #if config.Get('ClamAV', 'DetectPUA') == '1':
    #    cmd += ' --detect-pua'
    if config.Get('ClamAV', 'InfectedOnly') == '1' or noprint:
        cmd += ' --infected'
    if config.Get('ClamAV', 'ScanArchives') == '1':
        cmd += ' --max-files=%i --max-scansize=%iM --max-recursion=%i' % \
            (int(config.Get('ClamAV', 'MaxFiles')),
            int(config.Get('ClamAV', 'MaxScanSize')),
            int(config.Get('ClamAV', 'MaxRecursion')))
    else:
        cmd += ' --no-archive'

    cmd += ' --max-filesize=%iM' % int(config.Get('ClamAV', 'MaxFileSize'))

    if not noprint and config.Get('ClamAV', 'ShowProgress') == '1':
        cmd += ' --show-progress'

    if config.Get('ClamAV', 'RemoveInfected') == '1':
        cmd += ' --remove'
    elif config.Get('ClamAV', 'MoveInfected') == '1':
        quarantinedir = config.Get('ClamAV', 'QuarantineDir')
        # create quarantine folder before scanning
        if quarantinedir and not os.path.exists(quarantinedir):
            try:
                os.makedirs(quarantinedir)
            except:
                pass
        cmd += ' --move="%s"' % quarantinedir

    # file scan only params
    if path != None:
        if config.Get('ClamAV', 'ScanRecursive') == '1':
            cmd += ' --recursive'
        # add annoying registry files to exclude as they're locked by OS
        # no longer needed >= 0.93
        # cmd += GetExcludeSysLockedFiles()

        # FIX 8 August 2006
        # added root drive detection: os.path.splitdrive(path_element)[1]=='\\'
        # new 22 July 2006
        # now check if the path contains any dirs  or drives
        # if not (only files selected to scan) then do not apply the include/exclude patterns
        has_dirs = False
        for path_element in path.split('" "'):
            path_element = path_element.strip(' "')
            if os.path.isdir(path_element) or os.path.splitdrive(path_element)[1]=='\\':
                has_dirs = True
                break
        if has_dirs:
            # add include and exclude patterns
            for patterns in (['--include', config.Get('ClamAV', 'IncludePatterns')],
                            ['--exclude', config.Get('ClamAV', 'ExcludePatterns')]):
                for pat in patterns[1].split(Config.REGEX_SEPARATOR):
                    if len(pat):
                        # proper regular expressions are started with ':'
                        if pat.startswith('<') and pat.endswith('>'):
                            pat = pat[1:len(pat)-1]
                        else:
                            # not a regular expression
                            # translate glob style to regex
                            pat = fnmatch.translate(pat)

                            # '?' and '*' in the glob pattern become '.' and '.*' in the RE, which
                            # IMHO is wrong -- '?' and '*' aren't supposed to match slash in Unix,
                            # and by extension they shouldn't match such "special characters" under
                            # any OS.  So change all non-escaped dots in the RE to match any
                            # character except the special characters.
                            # XXX currently the "special characters" are just slash -- i.e. this is
                            # Unix-only.

                            pat = re.sub(r'(^|[^\\])\.', r'\1[^\\]', pat)

                        cmd += ' %s="%s"' % (patterns[0], pat)


        # append \\ when we have a DRIVE letter path only otherwise CRT gets messd up argv in clamav
        # i.e C:\ will become C:\\
        path = re.sub('([A-Za-z]):("\\|$)', r'\1:\\\2', path)
    else:
        path = "--memory"

    # 21 November 2006
    # added --kill option to unload processes from mem

    if config.Get('ClamAV', 'Kill') == '1':
        cmd += ' --kill'

    cmd = '"%s" %s %s' % (config.Get('ClamAV', 'ClamScan'), cmd, path)

    print 'clamscan.exe command line: ', cmd

    return cmd


def CleanupTemp(pid):
    # we search for folders and files ending with 0x8pid.clamtmp
    # and then remove them

    print 'Cleanup for process %08x' % pid
    mask = '.%08x.clamtmp' % pid
    try:
        (root, dirs, files) = os.walk(tempfile.gettempdir()).next()
    except:
        return
    for tmpdir in dirs:
        if tmpdir.endswith(mask):
            try:
                print 'removing temp dir', tmpdir
                shutil.rmtree(os.path.join(root, tmpdir), True)
            except Exception, e:
                print 'Could not remove %s. Error: %s' % (os.path.join(root, tmpdir), str(e))
    for tmpfile in files:
        if tmpfile.endswith(mask):
            try:
                print 'removing temp file', tmpfile
                os.remove(os.path.join(root, tmpfile))
            except Exception, e:
                print 'Could not remove %s. Error: %s' % (os.path.join(root, tmpdir), str(e))


def AppendLogFile(logfile, appendfile, maxsize):
    try:
        # create logs folder before appending
        if logfile:
            logsdir = os.path.split(logfile)[0]
            if logsdir and not os.path.exists(logsdir):
                os.makedirs(logsdir)

        # we need to synchronise log file access here
        # to avoid race conditions
        if sys.platform.startswith("win"):
            name = 'ClamWinLogFileUpdate-' + os.path.split(logfile)[1]
            try:
                # try to acquire our logupdate mutex
                hMutex = win32event.OpenMutex(win32con.SYNCHRONIZE, False, name)
                # wait until it is released
                win32event.WaitForSingleObject(hMutex, win32event.INFINITE)
                win32api.CloseHandle(hMutex)
            except win32api.error:
                pass
            # create and own the mutex now to prevent others from modifying the log file
            # whilst we append to it
            hMutex = None
            try:
                hMutex = win32event.CreateMutex(None, True, name)
            except win32api.error, e:
                print('Could not create mutex %s. Error: %s' % (name, str(e)))

        ftemp = file(appendfile, 'rt')

        # check if the file is larger then maxsize and read last maxsize bytes
        # go to end of file
        ftemp.seek(0, 2)
        tempsize = ftemp.tell()
        if tempsize > maxsize:
            ftemp.seek(-maxsize, 2)
            tempsize = maxsize
        else:
            # read from the beginning
            ftemp.seek(0, 0)

        # open main file for appending
        f = file(logfile, 'a+t')
        # get the file size
        f.seek(0, 2)
        # empty the file if longer than log size limit
        # shall implement rotation here, when have time
        if f.tell() > maxsize - tempsize:
            f.truncate(0)

        # copy data in using 64Kb buffer
        bufsize = 65535
        pos = 0
        while pos < tempsize:
            # read text from our temporary log file
            text = ftemp.read(min(bufsize, tempsize - pos)).replace('\r\n', '\n')
            f.write(text)
            pos = pos + bufsize
    except IOError, e:
        print('Could not write to the log file %s. Error: %s' % (logfile, str(e)))

    # release our synchronisation mutex
    if sys.platform.startswith("win") and hMutex is not None:
        try:
            win32event.ReleaseMutex(hMutex)
        except win32api.error, e:
            print('Could not release mutex %s Error: %s' % (name, str(e)))

def GetDBInfo(filename):
    try:
        # first 100 bytes of the file are definitely text
        f = file(filename, 'rt')
        # read first 100 bytes
        data = f.read(100)
        data = data.split(':')
        updatestr, ver, numv = data[1:4]

        # set C locale, otherwise python and wxpython complain
        locale.setlocale(locale.LC_ALL, 'C')

        # parse datestr to local time
        # time is in following format '12 May 2004 15-55 +0200' or
        # '%d %b %Y %H-%M %z', since strptime on windows has no %z flag,
        # we need to process it separately
        sep = updatestr.rfind(' ')
        # get the time differnece relative to GMT
        tzhour = time.strptime(updatestr[sep + 2:], '%H%M').tm_hour

        # deduct or add tzhour to the time based on timezone
        if updatestr[sep + 1] == '-':
            tzhour = -tzhour

        updatestr = updatestr[:sep]
        # set default C locale, as *.cvd timestring uses that
        loc = locale.setlocale(locale.LC_TIME, 'C')
        try:
            update_tm = time.strptime(updatestr, '%d %b %Y %H-%M %Z')
        except:
            update_tm = time.strptime(updatestr, '%d %b %Y %H-%M')
        # restore the locale
        locale.setlocale(locale.LC_TIME, loc)
        #get the final update time and add the UTC difference
        updated = time.mktime(update_tm) - tzhour*3600.0 - time.altzone
        return int(ver), int(numv), updated
    except Exception, e:
        print 'Unable to retrieve %s version. Error: %s' % (filename, str(e))
        return None, None, 0

def GetHostName():
    hostname = ''
    if sys.platform.startswith('win'):
        # ignore errors retrieving domain name
        try:
            try:
                # there is no win32api.GetDomainName()
                # on 9x, therefore try: except: block
                dom_name = win32api.GetDomainName()
            except:
                dom_name = None
            comp_name = win32api.GetComputerName()
            # on computers that are not members of domain
            # GetDomainName returns computer name
            # we don't want to duplicate it
            hostname = comp_name
            if (dom_name is not None) and (dom_name != comp_name):
                    hostname = dom_name + '\\' + hostname
        except:
            hostname = 'Unknown'
    else:
        import socket
        try:
            hostname = socket.gethostbyaddr(socket.gethostbyname(socket.gethostname()))[0]
        except:
            hostname = 'Unknown'
    return hostname

def SpawnPyOrExe(wait, filename, *params):
    if wait:
        flag = os.P_WAIT
    else:
        flag = os.P_NOWAIT
    if not hasattr(sys, 'frozen'):
        #win32api.ShellExecute(0, 'open', filename + '.py', filename + '.py ' + ' '.join(params), None, win32con.SW_SHOWNORMAL)
        ret = os.spawnl(flag, sys.executable, ' '  + filename + '.py ' + ' '.join(params))
    else:
        ret = os.spawnl(flag, filename + '.exe', *params)
    print "SpawnPyOrExe %s returned " % filename, ret
    return ret



def SafeExpandEnvironmentStrings(s):
    if sys.platform.startswith('win'):
        try:
            s = win32api.ExpandEnvironmentStrings(s)
        except Exception,e:
            print "An Error occured in ExpandEnvironmentStrings: %s" % str(e)
    return s



def ReformatLog(data, rtf, err_text):
    data = ReplaceClamAVWarnings(data.replace('\r\n', '\n'))
    # retrieve the pure report strings
    rex = re.compile('(.*)(-- summary --.*)(Infected files: \d*?\n)(.*)', re.M|re.S)
    r = rex.search(data)
    # we have 2 different formats depending on what's happened in clamscan
    # so cater for both
    if r is None:
        rex = re.compile('(.*)(----------- SCAN SUMMARY -----------.*)(Infected files: \d*?\n)(.*)', re.M|re.S)
        r = rex.search(data)

    fp = False
    if r is not None:
        found = ''
        other = ''
        lines = r.group(1).splitlines()
        # get all infections first
        for line in lines:
            if line.endswith('FOUND'):
                if rtf:
                    found += '\\cf1\\b %s\\cf0\\b0\n' % line.replace('\\', '\\\\')
                else:
                    found += line + '\n'

            elif not line.endswith('OK'):
                if rtf:
                    other += line.replace('\\', '\\\\') + '\n'
                else:
                    other += line + '\n'

        data = '%s%s' + r.group(2) + "%s" + r.group(4)
        # line with number of infected files
        infected = r.group(3)
        if rtf:
            num = re.match('.*?(\d*?)$', infected)
            if num is not None and int(num.group(1)) > 0:
                # print in red
                infected = '\\cf1\\b %s\\cf0\\b0\n' % infected
            else:
                # print in green
                infected = '\\cf2\\b %s\\cf0\\b0\n' % infected
            data = data.replace('\\', '\\\\')
        data %= (other, found, infected)
        data += "\n"
        lines = err_text.split("\n")
        for line in lines:
            if line.endswith('FALSE POSITIVE FOUND'):
                if not fp: # first FP in the list - print header
                    data += "The following files are Digitally Signed by Microsoft and have been incorrectly detected as viruses:\n"
                    #if rtf:
                    #    data += "\\cf3\\b %s\\cf0\\b0" % hdr                    
                        
                fp = True
                if rtf:
                    data += '\\cf3\\b %s\\cf0\\b0\n' % line.replace('\\', '\\\\')
                else:
                    data += line + '\n'
            else:
                data += line + '\n'
          
        if fp:            
            if rtf:
                data += "Please do not be alarmed and help us by submitting the files identified above " +\
                        "as \\cf3\\b FALSE POSITIVE \\cf0\\b0 at http://www.clamav.net/sendvirus/\n"
            else:
                data += "Please do not be alarmed and help us by submitting the files identified above " +\
                        "as FALSE POSITIVE at http://www.clamav.net/sendvirus/\n"                   
            
        if rtf:
            data = r'{\rtf1{\colortbl ;\red128\green0\blue0;;\red0\green128\blue0;;\red0\green0\blue255;}%s}' % data.replace('\n', '\\par\r\n')
    return data

# removes clamav warnings
def ReplaceClamAVWarnings(data):
    data = data.replace('Please check if ClamAV tools are linked against proper version of libclamav\n', '')
    data = data.replace('WARNING: Your ClamAV installation is OUTDATED!\n', '')
    data = re.sub("DON'T PANIC! Read .*\n", '', data)
    data = re.sub('WARNING: Current functionality level = \d+, recommended = \d+\n', '', data)
    data = re.sub('WARNING: Local version: \d+\.??\d*?\.??\d*? Recommended version: \d+\.??\d*?\.??\d*?\n', '', data)


    data = data.replace('LibClamAV Warning: ********************************************************\n', '')
    data = data.replace('LibClamAV Warning: ***  This version of the ClamAV engine is outdated.  ***\n', '')
    data = re.sub("LibClamAV Warning: \*\*\* DON'T PANIC! .* \*\*\*\n", '', data)

    # remove XXX: Excluded lines
    data = re.sub('.*\: Excluded\n', '', data)

    # remove incremental db update warnings and errors
    data = re.sub('ERROR: getfile: .* not found on remote server \(IP: .*\)\n', '', data)
    data = re.sub('ERROR: getpatch: Can\'t download .* from .*\n', '', data)
    data = data.replace('WARNING: Incremental update failed, trying to download daily.cvd\n', '')

    return data

# returns tuple (version, url, changelog)
# exception on error
def GetOnlineVersion(config):
     import version
     tmpfile = None
     url = config.Get('Updates', 'CheckVersionURL')
     try:
         # add proxy info
         if config.Get('Proxy', 'Host') != '':
             proxy_info = {
                 'user' : config.Get('Proxy', 'User'),
                 'pass' : config.Get('Proxy', 'Password'),
                 'host' : config.Get('Proxy', 'Host'),
                 'port' : config.Get('Proxy', 'Port')
                 }
             if proxy_info['user'] != '':
                 proxy_url = "http://%(user)s:%(pass)s@%(host)s:%(port)s"
             else:
                 proxy_url = "http://%(host)s:%(port)s"

             proxy_url = proxy_url % proxy_info

             proxy_support = urllib2.ProxyHandler({"http": proxy_url})
             opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler())
             urllib2.install_opener(opener)
         f = urllib2.urlopen(url + '?ver=%s' % version.clamwin_version)
         verinfo = f.read()
         #write to a temp file
         tmpfile = tempfile.mktemp()
         file(tmpfile, 'wt').write(verinfo)

         # read ini file
         conf = ConfigParser.ConfigParser()
         conf.read(tmpfile)
         os.unlink(tmpfile)
         tmpfile = None

         # get our data
         version = conf.get('VERSION', 'VER')

         if conf.has_option('CHANGELOG', 'HTML'):
             changelog = conf.get('CHANGELOG', 'HTML')
         elif conf.has_option('CHANGELOG', 'TEXT'):
             changelog = conf.get('CHANGELOG', 'TEXT')
         else:
             changelog = None
         changelog = changelog.replace('\\n', '\n')

         url = conf.get('DOWNLOAD', 'WEB')
     except Exception, e:
         if tmpfile is not None:
             try:
                 os.unlink(tmpfile)
             except:
                 pass
         raise e
     return (version, url, changelog)

def CheckDatabase(config):
    path = config.Get('ClamAV', 'Database')
    if path == '':
        return False
    return (os.path.isfile(os.path.join(path, 'main.cvd')) or \
           os.path.isfile(os.path.join(path, 'main.cld'))) and \
           (os.path.isfile(os.path.join(path, 'daily.cvd'))  or  \
            os.path.isfile(os.path.join(path, 'daily.cld')))


def RegKeyExists(key, subkey):
    # try to open the regkey
    try:
        hKey = _winreg.OpenKey(key, subkey);
        _winreg.CloseKey(hKey);
        return True;
    except:
        return False;

def IsOutlookInstalled():
    return (RegKeyExists(_winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Office\\Outlook') or
        RegKeyExists(_winreg.HKEY_LOCAL_MACHINE, 'Software\\Microsoft\\Office\\Outlook') or
        RegKeyExists(_winreg.HKEY_LOCAL_MACHINE, 'Software\\Microsoft\\Office\\9.0\\Outlook') or
        RegKeyExists(_winreg.HKEY_LOCAL_MACHINE, 'Software\\Microsoft\\Office\\10.0\\Outlook') or
        RegKeyExists(_winreg.HKEY_LOCAL_MACHINE, 'Software\\Microsoft\\Office\\11.0\\Outlook'))


def IsOnline():
    #try:
    #    wininet = windll.wininet
    #    flags = DWORD()
    #    connected = wininet.InternetGetConnectedState(byref(flags), None)
    #    print "Internet online: %i" % connected
    #    return connected == 1
    #except Exception, e:
    #    print "InternetGetConnectedState failed %s", str(e)

    try:
        import socket
        addrs = socket.gethostbyname_ex(socket.gethostname())[2]
        for addr in addrs:
            if addr[:3] not in('127', '169') and addr != '0.0.0.0':
                print "Internet online: 1"
                return True
    except Exception, e:
        print 'gethostbyname_ex Error: %s' % str(e)
    return False


#def IsOutlookAddinEnabled():
#    key = _winreg.HKEY_LOCAL_MACHINE
#    subKey = ''
#    enabled = False
#    if (RegKeyExists(_winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Office\\Outlook\\Addins\\ClamWin.OutlookAddin')):
#        key = _winreg.HKEY_CURRENT_USER
#        subKey = 'Software\\Microsoft\\Office\\Outlook\\Addins\\ClamWin.OutlookAddin'
#    if (RegKeyExists(_winreg.HKEY_LOCAL_MACHINE, 'Software\\Microsoft\\Office\\Outlook\\Addins\\ClamWin.OutlookAddin')):
#        key = _winreg.HKEY_LOCAL_MACHINE
#        subKey = 'Software\\Microsoft\\Office\\Outlook\\Addins\\ClamWin.OutlookAddin'
#    if (RegKeyExists(_winreg.HKEY_LOCAL_MACHINE, 'Software\\Microsoft\\Office\\9.0\\Outlook\\Addins\\ClamWin.OutlookAddin')):
#        key = _winreg.HKEY_LOCAL_MACHINE
#        subKey = 'Software\\Microsoft\\Office\\9.0\\Outlook\\Addins\\ClamWin.OutlookAddin'
#    if (RegKeyExists(_winreg.HKEY_LOCAL_MACHINE, 'Software\\Microsoft\\Office\\10.0\\Outlook\\Addins\\ClamWin.OutlookAddin')):
#        key = _winreg.HKEY_LOCAL_MACHINE
#        subKey = 'Software\\Microsoft\\Office\\10.0\\Outlook\\Addins\\ClamWin.OutlookAddin'
#    if (RegKeyExists(_winreg.HKEY_LOCAL_MACHINE, 'Software\\Microsoft\\Office\\11.0\\Outlook\\Addins\\ClamWin.OutlookAddin')):
#        key = _winreg.HKEY_LOCAL_MACHINE
#        subKey = 'Software\\Microsoft\\Office\\11.0\\Outlook\\Addins\\ClamWin.OutlookAddin'
#    if (subKey != ''):
#        hKey = _winreg.OpenKey(key, subKey);
#        enabled = int(_winreg.QueryValueEx(hKey, "LoadBehavior")[0])==3;
#        _winreg.CloseKey(hKey)
#    return enabled

#def EnableOutlookAddin(enable):
#    # Find the key and subkey to set
#    key = _winreg.HKEY_LOCAL_MACHINE
#    subKey = ''
#    if (RegKeyExists(_winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Office\\Outlook\\Addins\\ClamWin.OutlookAddin')):
#        key = _winreg.HKEY_CURRENT_USER
#        subKey = 'Software\\Microsoft\\Office\\Outlook\\Addins\\ClamWin.OutlookAddin'
#    if (RegKeyExists(_winreg.HKEY_LOCAL_MACHINE, 'Software\\Microsoft\\Office\\Outlook\\Addins\\ClamWin.OutlookAddin')):
#        key = _winreg.HKEY_LOCAL_MACHINE
#        subKey = 'Software\\Microsoft\\Office\\Outlook\\Addins\\ClamWin.OutlookAddin'
#    if (RegKeyExists(_winreg.HKEY_LOCAL_MACHINE, 'Software\\Microsoft\\Office\\9.0\\Outlook\\Addins\\ClamWin.OutlookAddin')):
#        key = _winreg.HKEY_LOCAL_MACHINE
#        subKey = 'Software\\Microsoft\\Office\\9.0\\Outlook\\Addins\\ClamWin.OutlookAddin'
#    if (RegKeyExists(_winreg.HKEY_LOCAL_MACHINE, 'Software\\Microsoft\\Office\\10.0\\Outlook\\Addins\\ClamWin.OutlookAddin')):
#        key = _winreg.HKEY_LOCAL_MACHINE
#        subKey = 'Software\\Microsoft\\Office\\10.0\\Outlook\\Addins\\ClamWin.OutlookAddin'
#    if (RegKeyExists(_winreg.HKEY_LOCAL_MACHINE, 'Software\\Microsoft\\Office\\11.0\\Outlook\\Addins\\ClamWin.OutlookAddin')):
#        key = _winreg.HKEY_LOCAL_MACHINE
#        subKey = 'Software\\Microsoft\\Office\\11.0\\Outlook\\Addins\\ClamWin.OutlookAddin'
#    print '   Subkey = ' + subKey
#    if (subKey != ''):
#        hKey = _winreg.OpenKey(key, subKey, 0,_winreg.KEY_WRITE);
#        if enable:
#            print '   Writing value to 3...'
#            _winreg.SetValueEx(hKey, 'LoadBehavior', 0, _winreg.REG_DWORD, 3)
#        else:
#            print '   Writing value to 2...'
#            _winreg.SetValueEx(hKey, 'LoadBehavior', 0, _winreg.REG_DWORD, 2)
#        _winreg.CloseKey(hKey)



if __name__ == '__main__':
    #AppendLogFile('c:\\1.txt',  'C:\\MSDE2kLog.txt', 30000)
    #currentDir = GetCurrentDir(True)
    #os.chdir(currentDir)
    #CreateProfile()
    #config_file = os.path.join(GetProfileDir(True),'ClamWin.conf')
    #config = Config.Settings(config_file)
    #b = config.Read()
    #print GetOnlineVersion(config)
#    print CheckDatabase(config)
    #dbpath =  config.Get('ClamAV', 'Database')
    #daily = os.path.join(dbpath, 'daily.cld')
    #if not os.path.isfile(daily):
    #    daily = os.path.join(dbpath, 'daily.cvd')
    #print GetDBInfo(daily)
    print IsOnline()

