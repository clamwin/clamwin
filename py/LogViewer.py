#!/usr/bin/python

#-----------------------------------------------------------------------------
# Name:        wxDialogLogViewer.py
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


import wx
import os
#from I18N import getClamString as _


def create(parent, text, scroll_down = False):
    return LogViewer(parent, text, scroll_down)

##
##[wxID_WXDIALOGLOGVIEW, wxID_WXDIALOGLOGVIEWBUTTONOK,
## wxID_WXDIALOGLOGVIEWTEXTCTRL,
##] = map(lambda _init_ctrls: wxNewId(), range(3))

class LogViewer(wx.Dialog):
    def __init__(self, parent, text, scroll_down = False):
        
        self._init_ctrls(parent)
        self._init_sizers()

        # set window icons
        icons = wx.IconBundle()
        icons.AddIconFromFile('img/FrameIcon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcons(icons)

        text = text.decode('utf-8')
        self.textCtrl.AppendText(text)
        self._scroll_down = scroll_down        
        

    def _init_sizers(self):
        # create sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.textCtrl,1,wx.TOP | wx.RIGHT | wx.LEFT | wx.GROW, 5)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.buttonClear)
        sizer1.Add((20,-1))
        sizer1.Add(self.buttonOK)
        

        sizer.Add(sizer1, 0, wx.BOTTOM | wx.TOP | wx.ALIGN_CENTER, 10)
        self.SetSizer(sizer)

    def _init_ctrls(self, parent):
        # create dialog and control
        wx.Dialog.__init__(self, parent,
                           wx.ID_ANY,
                           _('ClamWin Log Viewer'),
                           style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE,
                           )
        self.SetClientSize(wx.Size(558, 401))
        self.Center(wx.BOTH)

        self.textCtrl = wx.TextCtrl(self,
                                    wx.ID_ANY,
                                    style=wx.TE_RICH | wx.TE_MULTILINE | wx.TE_READONLY,
                                    )

        self.buttonOK = wx.Button(self,wx.ID_ANY,_('OK'))

        self.buttonClear = wx.Button(self,wx.ID_ANY,_('Clear'))

        #Register events
        self.Bind(wx.EVT_CHAR_HOOK, self.OnCharHook)
        self.Bind(wx.EVT_INIT_DIALOG, self.OnInitDialog)
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.buttonOK)

    def OnOK(self, event):
        self.EndModal(wx.ID_OK)

    def OnCharHook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

    def OnInitDialog(self, event):
        if self._scroll_down:
            self.textCtrl.SetInsertionPointEnd()
            self.textCtrl.ShowPosition(self.textCtrl.GetLastPosition())
        else:
            self.textCtrl.SetInsertionPoint(0)
            self.textCtrl.ShowPosition(0)
        event.Skip()
        



if __name__ == '__main__':
    app = wx.App()
    msg = "Test Message Line\n"*20

    dlg = create(None, msg, True)
    dlg.ShowModal()
    dlg.Destroy()

    app.MainLoop()


