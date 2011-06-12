#-----------------------------------------------------------------------------
# Name:        CloseWindows.py
# Product:     ClamWin Free Antivirus
#
# Author:      alch [alch at users dot sourceforge dot net]
#
# Created:     2004/22/03
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
import SetUnicode
import win32gui, win32con, win32api, win32process
from win32com.shell import shell, shellcon
import os, time
import RedirectStd

def Close(hwnd, appWindows):
    if(win32gui.GetClassName(hwnd), win32gui.GetWindowText(hwnd)) in appWindows:
    
        # get process handle
        t, p = win32process.GetWindowThreadProcessId(hwnd)
        
        # try to close it with WM_CLOSE
	print 'sending WM_CLOSE to the process ', p
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        # wait for the process to exit gracefully
        time.sleep(5.0)
        # kill it forcefully if it did not exit
        try:
            handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, p)
            if handle:
                print 'terminating prosess forcefully ', p
                win32api.TerminateProcess(handle,0)
                win32api.CloseHandle(handle)
        except:
           pass
           
    return True


def RemoveShortcuts(hwnd, setupWindows):
    try:
        if(win32gui.GetClassName(hwnd), win32gui.GetWindowText(hwnd)) in setupWindows:    
        # delete leftover ClamWin shortcuts CSIDL_COMMON_PROGRAMS and CSIDL_PROGRAMS
        # C:\Documents and Settings\All Users\Start Menu\Programs\ClamWin Antivirus		
            s = shell.SHGetSpecialFolderPath(0, shellcon.CSIDL_COMMON_PROGRAMS, True)
            s = os.path.join(s, 'ClamWin Antivirus')
            s = os.path.join(s, 'Quarantine Browser.lnk')			            
            try:
                os.remove(s)
            except:
                pass
            s = shell.SHGetSpecialFolderPath(0, shellcon.CSIDL_PROGRAMS, True)
            s = os.path.join(s, 'ClamWin Antivirus')
            s = os.path.join(s, 'Quarantine Browser.lnk')			            
            try:
                os.remove(s)
            except:
                pass
                
    except Exception, e:
        print 'RemoveShortcuts exception', str(e)		
    return True



def CloseClamWinWindows():
    appWindows = (('ClamWinTrayWindow', 'ClamWin'),
                    ('wxWindowClass', 'ClamWin Free Antivirus'),
                    ('#32770', 'ClamWin Internet Update Status'),
                    ('#32770', 'ClamWin Preferences'))
    win32gui.EnumWindows(Close, appWindows)

def Cleanup():
    setupWindows = (('TUninstProgressForm', 'ClamWin Free Antivirus Uninstall'),)
    win32gui.EnumWindows(RemoveShortcuts, setupWindows)
		
    
    



if __name__=='__main__':    
    CloseClamWinWindows()
    Cleanup()
    
    
        
