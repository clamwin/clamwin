#-----------------------------------------------------------------------------
# Name:        ExplorerShell.py
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

#-----------------------------------------------------------------------------

# This code is based on context_menu.py demo from Mark Hammond's win32 Extensions

import pythoncom

from win32com.shell import shell, shellcon
import win32gui, win32con, win32api
import Process
import os, sys, time
import RedirectStd


IContextMenu_Methods = ["QueryContextMenu", "InvokeCommand", "GetCommandString"]
IShellExtInit_Methods = ["Initialize"]

class ShellExtension:
    _reg_progid_ = "ClamWin.ShellExtension.ContextMenu"
    _reg_desc_ = "ClamWin Context Menu"
    _reg_clsid_ = "{94FDC9F6-8C9B-4a70-8DBB-7662FFE48EB4}"
    _com_interfaces_ = [shell.IID_IShellExtInit, shell.IID_IContextMenu]
    _public_methods_ = IContextMenu_Methods + IShellExtInit_Methods

    def Initialize(self, folder, dataobj, hkey):
        print 'Initialize'
        self.dataobj = dataobj

    def QueryContextMenu(self, hMenu, indexMenu, idCmdFirst, idCmdLast, uFlags):
        print 'QueryContextMenu'
        # Query the items clicked on
        format_etc = win32con.CF_HDROP, None, 1, -1, pythoncom.TYMED_HGLOBAL
        try:
            sm = self.dataobj.GetData(format_etc)
        except pythoncom.com_error:
            return 0
        num_files = shell.DragQueryFile(sm.data_handle, -1)
        msg = "Scan For Viruses With ClamWin"
        if num_files > 1:
            # we aren't handling multiple files
            return 0
        else:
            self._fname = shell.DragQueryFile(sm.data_handle, 0)
        idCmd = idCmdFirst
        items = []
        if (uFlags & 0x000F) == shellcon.CMF_NORMAL or uFlags & shellcon.CMF_EXPLORE:
            items.append(msg)

        win32gui.InsertMenu(hMenu, indexMenu,
                            win32con.MF_SEPARATOR|win32con.MF_BYPOSITION,
                            0, None)
        indexMenu += 1
        for item in items:
            win32gui.InsertMenu(hMenu, indexMenu,
                                win32con.MF_STRING|win32con.MF_BYPOSITION,
                                idCmd, item)
            indexMenu += 1
            idCmd += 1
        win32gui.InsertMenu(hMenu, indexMenu,
                            win32con.MF_SEPARATOR|win32con.MF_BYPOSITION,
                            0, None)
        indexMenu += 1
        return idCmd-idCmdFirst # Must return number of menu items we added.

    def InvokeCommand(self, ci):
        print 'InvokeCommand'
        mask, hwnd, verb, params, dir, nShow, hotkey, hicon = ci
        # get the directory of our dll
        try:
            if hasattr(sys, "frozen"):
                # attempt to read the folder form registry first
                key = None
                try:
                    key = win32api.RegOpenKeyEx(win32con.HKEY_LOCAL_MACHINE, 'Software\\ClamWin')
                    currentDir = win32api.RegQueryValueEx(key, 'Path')[0]
                    win32api.CloseHandle(key)
                except win32api.error:
                    if key is not None:
                        win32api.CloseHandle(key)
                    # couldnt find it in the registry
                    # get it from command line
                    if sys.frozen == "dll":
                        this_filename = win32api.GetModuleFileName(sys.frozendllhandle)
                    else:
                        this_filename = sys.executable
                    currentDir = os.path.split(this_filename)[0]
            else:
                currentDir = os.path.split(os.path.abspath(__file__))[0]
        except NameError:
            currentDir = os.path.split(os.path.abspath(sys.argv[0]))[0]
        os.chdir(currentDir)

        # we need to resort to calling external executable here
        # because wxPython has some threading issues when called from
        # multiple Windows Explorer instances
        # read this value from registry

        exe = os.path.join(currentDir, 'ClamWin.exe')
        if not os.path.exists(exe):
            win32gui.MessageBox(hwnd, 'Could not locate file: %s'% exe, 'ClamWin', win32con.MB_OK | win32con.MB_ICONEXCLAMATION)
        else:
            cmd = '"%s" --mode=scanner --path="%s"' % (exe, self._fname)
            try:
                proc = Process.ProcessOpen(cmd)
                proc.close()
            except Process.ProcessError:
                win32gui.MessageBox(hwnd, 'Could not execute %s.' % cmd, 'ClamWin', win32con.MB_OK | win32con.MB_ICONEXCLAMATION)

    def GetCommandString(self, cmd, typ):
        return "ClamWin Free Antivirus"

def DllRegisterServer():
    import _winreg
    keyNames = ("Folder\\shellex", "*\\shellex")
    for name in keyNames:
        key = _winreg.CreateKey(_winreg.HKEY_CLASSES_ROOT, name)
        subkey = _winreg.CreateKey(key, "ContextMenuHandlers")
        subkey2 = _winreg.CreateKey(subkey, "ClamWin")
        _winreg.SetValueEx(subkey2, None, 0, _winreg.REG_SZ, ShellExtension._reg_clsid_)
    print ShellExtension._reg_desc_, "registration complete."

def DllUnregisterServer():
    import _winreg
    try:
        keyNames = ("Folder\\shellex", "*\\shellex")
        for name in keyNames:
            key = _winreg.DeleteKey(_winreg.HKEY_CLASSES_ROOT,
                                name + "\\ContextMenuHandlers\\ClamWin")
    except WindowsError, details:
        import errno
        if details.errno != errno.ENOENT:
            raise
    print ShellExtension._reg_desc_, "unregistration complete."

if __name__ == '__main__':
    from win32com.server import register
    register.UseCommandLine(ShellExtension,
                   finalize_register = DllRegisterServer,
                   finalize_unregister = DllUnregisterServer)
