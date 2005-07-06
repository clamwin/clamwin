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
import win32gui, win32con, win32api
import time
import RedirectStd

def CloseWindow(hwnd, appWindows):                    
    if(win32gui.GetClassName(hwnd), win32gui.GetWindowText(hwnd)) in appWindows:
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    return True
            
    
def CloseClamWin():    
    appWindows = (('wxWindowClass', 'ClamWin Free Antivirus'),    
                    ('#32770', 'ClamWin Internet Update Status'),
                    ('#32770', 'ClamWin Preferences'),
                    ('ClamWinTrayWindow', 'ClamWin'))        
    win32gui.EnumWindows(CloseWindow, appWindows)  
    
if __name__=='__main__':        
    CloseClamWin()    
    time.sleep(3.0) 