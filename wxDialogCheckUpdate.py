#Boa:Dialog:wxDialogUpdateChecker

#-----------------------------------------------------------------------------
# Name:        wxDialogCheckUpdate.py
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
import wxDialogUtils
import wx
import wx.html


def create(parent, config, version, url, changelog):
    return wxDialogUpdateChecker(parent, config, version, url, changelog)

[wxID_WXDIALOGUPDATECHECKER, wxID_WXDIALOGUPDATECHECKERBUTTONCLOSE,
 wxID_WXDIALOGUPDATECHECKERBUTTONDOWNLOAD,
 wxID_WXDIALOGUPDATECHECKERCHECKBOXDONTCHECK,
 wxID_WXDIALOGUPDATECHECKERSTATICLINEHTML,
 wxID_WXDIALOGUPDATECHECKERSTATICTEXTANNOUNCE,
 wxID_WXDIALOGUPDATECHECKERSTATICTEXTCHANGELOG,
 wxID_WXDIALOGUPDATECHECKERSTATICTEXTINSTRUCTIONS,
] = map(lambda _init_ctrls: wx.NewId(), range(8))

class wxDialogUpdateChecker(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_WXDIALOGUPDATECHECKER,
              name='wxDialogUpdateChecker', parent=prnt, pos=wx.Point(229, 314),
              size=wx.Size(324, 272),
              style=wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP|wx.MINIMIZE_BOX,
              title='ClamWin Update')
        self.SetClientSize(wx.Size(316, 245))
        wx.EVT_CHAR_HOOK(self, self.OnCharHook)
        wx.EVT_INIT_DIALOG(self, self.OnInitDialog)

        self.staticTextAnnounce = wx.StaticText(id=wxID_WXDIALOGUPDATECHECKERSTATICTEXTANNOUNCE,
              label='An update of ClamWin Free Antivirus has been released. Please click on Download button and download the latest version %s',
              name='staticTextAnnounce', parent=self, pos=wx.Point(13, 8),
              size=wx.Size(296, 40), style=wx.ST_NO_AUTORESIZE)
        self.staticTextAnnounce.SetForegroundColour(wx.Colour(170, 0, 0))
        self.staticTextAnnounce.SetToolTipString('')
        self.staticTextAnnounce.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD, False, 'MS Shell Dlg'))

        self.staticTextInstructions = wx.StaticText(id=wxID_WXDIALOGUPDATECHECKERSTATICTEXTINSTRUCTIONS,
              label='After you download the latest version setup file simply run it and install over the existing version.',
              name='staticTextInstructions', parent=self, pos=wx.Point(13, 50),
              size=wx.Size(296, 28), style=0)
        self.staticTextInstructions.SetForegroundColour(wx.Colour(0, 0, 0))
        self.staticTextInstructions.SetToolTipString('')

        self.staticTextChangelog = wx.StaticText(id=wxID_WXDIALOGUPDATECHECKERSTATICTEXTCHANGELOG,
              label='List Of Changes in Version %s:',
              name='staticTextChangelog', parent=self, pos=wx.Point(13, 80),
              size=wx.Size(296, 13), style=wx.ST_NO_AUTORESIZE)
        self.staticTextChangelog.SetToolTipString('')

        self.staticLineHtml = wx.StaticLine(id=wxID_WXDIALOGUPDATECHECKERSTATICLINEHTML,
              name='staticLineHtml', parent=self, pos=wx.Point(9, 96),
              size=wx.Size(296, 85), style=0)
        self.staticLineHtml.Show(False)
        self.staticLineHtml.SetToolTipString('')

        self.checkBoxDontCheck = wx.CheckBox(id=wxID_WXDIALOGUPDATECHECKERCHECKBOXDONTCHECK,
              label='&Do Not Check for Updates in Future',
              name='checkBoxDontCheck', parent=self, pos=wx.Point(16, 190),
              size=wx.Size(288, 13), style=0)
        self.checkBoxDontCheck.SetValue(False)
        self.checkBoxDontCheck.SetToolTipString('')
        wx.EVT_CHECKBOX(self.checkBoxDontCheck,
              wxID_WXDIALOGUPDATECHECKERCHECKBOXDONTCHECK,
              self.OnCheckBoxDontCheckCheckbox)

        self.buttonDownload = wx.Button(id=wxID_WXDIALOGUPDATECHECKERBUTTONDOWNLOAD,
              label='&Download', name='buttonDownload', parent=self,
              pos=wx.Point(143, 212), size=wx.Size(75, 23), style=0)
        self.buttonDownload.SetToolTipString('')
        self.buttonDownload.SetDefault()
        wx.EVT_BUTTON(self.buttonDownload,
              wxID_WXDIALOGUPDATECHECKERBUTTONDOWNLOAD, self.OnButtonDownload)

        self.buttonClose = wx.Button(id=wxID_WXDIALOGUPDATECHECKERBUTTONCLOSE,
              label='Close', name='buttonClose', parent=self, pos=wx.Point(230,
              212), size=wx.Size(75, 23), style=0)
        self.buttonClose.SetToolTipString('')
        wx.EVT_BUTTON(self.buttonClose, wxID_WXDIALOGUPDATECHECKERBUTTONCLOSE,
              self.OnButtonClose)

    def __init__(self, parent, config, version, url, changelog):
        self._init_ctrls(parent)
        self.html = wx.html.HtmlWindow(parent = self, id = -1, pos = self.staticLineHtml.GetPosition(),
                    size = self.staticLineHtml.GetSize(), style = wx.STATIC_BORDER)


        #move window above tray
        try:
            import win32gui, win32api, win32con
            hwnd = win32gui.FindWindow("Shell_TrayWnd", "")
            hwnd = win32gui.FindWindowEx(hwnd, 0, "TrayNotifyWnd", "")
            rect = win32gui.GetWindowRect(hwnd)
            size = self.GetSize()
            self.Move((win32api.GetSystemMetrics(win32con.SM_CXSCREEN) - size.GetWidth(), rect[1] - size.GetHeight() - 5))
        except Exception, e:
            print e
            self.Center(wx.BOTH)


        # set window icons
        icons = wx.IconBundle()
        icons.AddIconFromFile('img/FrameIcon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcons(icons)

        self._url = url
        self._config = config
        self.html.AppendToPage(changelog)
        self.staticTextAnnounce.SetLabel(self.staticTextAnnounce.GetLabel() % version)
        self.staticTextChangelog.SetLabel(self.staticTextChangelog.GetLabel() % version)

        self.checkBoxDontCheck.SetValue(not int(self._config.Get('Updates', 'CheckVersion')))


    def OnCharHook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_OK)
        else:
            event.Skip()

    def OnInitDialog(self, event):
        #self.textCtrl.SetInsertionPoint(0)
        #self.textCtrl.ShowPosition(0)
        event.Skip()

    def OnButtonClose(self, event):
        self._config.Set('Updates', 'CheckVersion', int(not self.checkBoxDontCheck.GetValue()))
        self._config.Write()
        self.EndModal(wx.ID_OK)
        event.Skip()

    def OnButtonDownload(self, event):
        self._config.Set('Updates', 'CheckVersion', int(not self.checkBoxDontCheck.GetValue()))
        self._config.Write()
        self.EndModal(wx.ID_OK)
        wxDialogUtils.wxGoToInternetUrl(self._url)
        event.Skip()

    def OnCheckBoxDontCheckCheckbox(self, event):
        event.Skip()



if __name__ == '__main__':
    import Utils, Config
    currentDir = Utils.GetCurrentDir(True)
    os.chdir(currentDir)
    Utils.CreateProfile()
    config_file = os.path.join(Utils.GetProfileDir(True),'ClamWin.conf')
    config = Config.Settings(config_file)
    b = config.Read()
    version, url, changelog = Utils.GetOnlineVersion(config)

    app = wx.App()

    dlg = create(None, config, version, url, changelog)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()

    config.Write()
    app.MainLoop()


