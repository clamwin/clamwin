# mtprng_test.py
#
# Author: Jamie Hale
#   Date: November 21 2002
#
# This file tests the mtprng Python extension module.
#

import BalloonTip
import win32con, win32api, win32gui, time

if __name__ == "__main__":
    try:
        hExistingWnd = win32gui.FindWindow(BalloonTip.SHADOWED_CLASS, None)
    except:
        try:
            hExistingWnd = win32gui.FindWindow(BalloonTip.SHADOWLESS_CLASS, None)
        except:
            hExistingWnd = None
    if hExistingWnd is not None:
        win32api.SendMessage(hExistingWnd, win32con.WM_CLOSE, 0, 0)      
        
    hwnd = win32gui.FindWindow("Shell_TrayWnd", "")
    hwnd = win32gui.FindWindowEx(hwnd, 0, "TrayNotifyWnd", "")	    
    rect = win32gui.GetWindowRect(hwnd)
    BalloonTip.ShowBalloonTip('Test Title', 'Test Text\nTest Text2.', (rect[0], rect[1]),
         win32con.IDI_ERROR, 
         BalloonTip.SHOW_CLOSE_BUTTON|BalloonTip.SHOW_INNER_SHADOW|BalloonTip.SHOW_TOPMOST|\
         BalloonTip.CLOSE_ON_KEYPRESS|BalloonTip.CLOSE_ON_LBUTTON_DOWN|BalloonTip.CLOSE_ON_MBUTTON_DOWN|\
         BalloonTip.CLOSE_ON_RBUTTON_DOWN,
         0, '', 20000)			    
    win32gui.PumpMessages()
			