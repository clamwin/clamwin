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


from wxPython.wx import *
import os

def create(parent, text, scroll_down = False):
    return wxDialogLogView(parent, text, scroll_down)

[wxID_WXDIALOGLOGVIEW, wxID_WXDIALOGLOGVIEWBUTTONOK, 
 wxID_WXDIALOGLOGVIEWTEXTCTRL, 
] = map(lambda _init_ctrls: wxNewId(), range(3))

class wxDialogLogView(wxDialog):
    def _init_coll_flexGridSizer_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.textCtrl, 0, border=5,
              flag=wxTOP | wxRIGHT | wxLEFT | wxGROW)
        parent.AddWindow(self.buttonOK, 0, border=10,
              flag=wxBOTTOM | wxTOP | wxALIGN_CENTER)

    def _init_coll_flexGridSizer_Growables(self, parent):
        # generated method, don't edit

        parent.AddGrowableRow(0)
        parent.AddGrowableCol(0)

    def _init_sizers(self):
        # generated method, don't edit
        self.flexGridSizer = wxFlexGridSizer(cols=1, hgap=0, rows=2, vgap=0)

        self._init_coll_flexGridSizer_Items(self.flexGridSizer)
        self._init_coll_flexGridSizer_Growables(self.flexGridSizer)

        self.SetSizer(self.flexGridSizer)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_WXDIALOGLOGVIEW, name='wxDialogLogView',
              parent=prnt, pos=wxPoint(450, 251), size=wxSize(566, 428),
              style=wxRESIZE_BORDER | wxDEFAULT_DIALOG_STYLE,
              title='ClamWin Log Viewer')
        self.SetClientSize(wxSize(558, 401))
        self.Center(wxBOTH)
        EVT_CHAR_HOOK(self, self.OnCharHook)
        EVT_INIT_DIALOG(self, self.OnInitDialog)

        self.textCtrl = wxTextCtrl(id=wxID_WXDIALOGLOGVIEWTEXTCTRL,
              name='textCtrl', parent=self, pos=wxPoint(5, 5), size=wxSize(548,
              353), style=wxTE_RICH | wxTE_MULTILINE | wxTE_READONLY, value='')
        self.textCtrl.SetToolTipString('')
        self.textCtrl.Center(wxBOTH)

        self.buttonOK = wxButton(id=wxID_WXDIALOGLOGVIEWBUTTONOK, label='OK',
              name='buttonOK', parent=self, pos=wxPoint(241, 368),
              size=wxSize(75, 23), style=0)
        self.buttonOK.SetToolTipString('')
        self.buttonOK.Center(wxBOTH)
        EVT_BUTTON(self.buttonOK, wxID_WXDIALOGLOGVIEWBUTTONOK, self.OnOK)

        self._init_sizers()

    def __init__(self, parent, text, scroll_down = False):        
        self._init_ctrls(parent)
        
        # set window icons
        icons = wxIconBundle()
        icons.AddIconFromFile('img/FrameIcon.ico', wxBITMAP_TYPE_ICO)
        self.SetIcons(icons)
        
        # we need to set controls heights to 0 and reinit sizers
        # to overcome boa sizers bug
        self.textCtrl.SetSize((-1, 0))
        self._init_sizers()
                
        self.textCtrl.AppendText(text)          
        self._scroll_down = scroll_down        
                        
    def OnOK(self, event):
        self.EndModal(wxID_OK)

    def OnCharHook(self, event):
        if event.GetKeyCode() == WXK_ESCAPE:
            self.EndModal(wxID_CANCEL)
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
    app = wxPySimpleApp()
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
    Test Message Line\nTest Message Line
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

 
