#Boa:Dialog:wxDialogLogView

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

import os
import sys
import wx

def create(parent, text, scroll_down = False):
    return wxDialogLogView(parent, text, scroll_down)

[wxID_WXDIALOGLOGVIEW, wxID_WXDIALOGLOGVIEWBUTTONOK,
 wxID_WXDIALOGLOGVIEWTEXTCTRL,
] = map(lambda _init_ctrls: wx.NewId(), range(3))

class wxDialogLogView(wx.Dialog):
    def _init_coll_flexGridSizer_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.textCtrl, 0, border=5,
              flag=wx.TOP | wx.RIGHT | wx.LEFT | wx.GROW)
        parent.AddWindow(self.buttonOK, 0, border=10,
              flag=wx.BOTTOM | wx.TOP | wx.ALIGN_CENTER)

    def _init_coll_flexGridSizer_Growables(self, parent):
        # generated method, don't edit

        parent.AddGrowableRow(0)
        parent.AddGrowableCol(0)

    def _init_sizers(self):
        # generated method, don't edit
        self.flexGridSizer = wx.FlexGridSizer(cols=1, hgap=0, rows=2, vgap=0)

        self._init_coll_flexGridSizer_Items(self.flexGridSizer)
        self._init_coll_flexGridSizer_Growables(self.flexGridSizer)

        self.SetSizer(self.flexGridSizer)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_WXDIALOGLOGVIEW, name='wxDialogLogView',
              parent=prnt, pos=wx.Point(450, 251), size=wx.Size(566, 428),
              style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE,
              title='ClamWin Log Viewer')
        self.SetClientSize(wx.Size(558, 401))
        self.Center(wx.BOTH)
        wx.EVT_CHAR_HOOK(self, self.OnCharHook)
        wx.EVT_INIT_DIALOG(self, self.OnInitDialog)

        self.textCtrl = wx.TextCtrl(id=wxID_WXDIALOGLOGVIEWTEXTCTRL,
              name='textCtrl', parent=self, pos=wx.Point(5, 5), size=wx.Size(548,
              353), style=wx.TE_RICH | wx.TE_MULTILINE | wx.TE_READONLY, value='')
        self.textCtrl.SetToolTipString('')
        self.textCtrl.Center(wx.BOTH)

        self.buttonOK = wx.Button(id=wxID_WXDIALOGLOGVIEWBUTTONOK, label='OK',
              name='buttonOK', parent=self, pos=wx.Point(241, 368),
              size=wx.Size(75, 23), style=0)
        self.buttonOK.SetToolTipString('')
        self.buttonOK.Center(wx.BOTH)
        wx.EVT_BUTTON(self.buttonOK, wxID_WXDIALOGLOGVIEWBUTTONOK, self.OnOK)

        self._init_sizers()

    def __init__(self, parent, text, scroll_down = False):
        self._init_ctrls(parent)

        # set window icons
        icons = wx.IconBundle()
        icons.AddIconFromFile('img/FrameIcon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcons(icons)

        # we need to set controls heights to 0 and reinit sizers
        # to overcome boa sizers bug
        self.textCtrl.SetSize((-1, 0))
        self._init_sizers()

        self.textCtrl.AppendText(text)
        self._scroll_down = scroll_down

    def OnOK(self, event):
        self.EndModal(wx.ID_OK)

    def OnCharHook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

    def OnInitDialog(self, event):
        if self._scroll_down:
            # to scroll richedit down correctly we need to use EM_SCROLLCARET,
            # wxWidgets SetInsertionPoint and ShowPosition fail on win9x
            if sys.platform.startswith('win'):
                import win32api, win32con
                win32api.PostMessage(self.textCtrl.GetHandle(), win32con.EM_SCROLLCARET, 0, 0)
            else:
                self.textCtrl.SetInsertionPointEnd()
                self.textCtrl.ShowPosition(self.textCtrl.GetLastPosition())
        else:
            self.textCtrl.SetInsertionPoint(0)
            self.textCtrl.ShowPosition(0)
        event.Skip()



if __name__ == '__main__':
    app = wx.App()
    msg = """Test Message Line
    Test Message Line\nTest Message Line
    Test Message Line\nTest Message Line
    Test Message Line\nTest Message Line
    Test Message Line\nTest Message Line
    Test Message Line\nTest Message Line
    Test Message Line\nTest Message Line
    Test Message Line\nTest Message Line
    Test Message Line\nTest Message Line
    Test Message Line\nTest Message Line
    Test Message Line\nTest Message Line
    Test Me`ssage Line\nTest Message Line
    Test Message Line\nTest Message Line
    Test Message Line\nTest Message Line
    Test Message Line\nTest Message Line
    Test Message Line\nTest Message Line
    """

    dlg = create(None, msg, True)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()

    app.MainLoop()


