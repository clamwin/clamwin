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


##from wxPython.wx import *
##from wxPython.html import *
import wx
import wx.html as  html
import os
import DialogUtils
#from I18N import getClamString as _

def create(parent, config, version, url, changelog):
    return DialogUpdateChecker(parent, config, version, url, changelog)

class DialogUpdateChecker(wx.Dialog):

    def __init__(self, parent, config, version, url, changelog):

        wx.Dialog.__init__(self,parent,title=_('ClamWin Update'),style=wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP|wx.MINIMIZE_BOX)
        self.SetClientSize(wx.Size(316, 245))
        self.Bind(wx.EVT_CHAR_HOOK, self.OnCharHook)

        self.staticTextAnnounce = wx.StaticText(self,wx.ID_ANY,
                                                _('An update of ClamWin Free Antivirus has been released. Please click on Download button and download the latest version %s'),
                                                size=(-1,40),
                                                )
                                                #style=wx.ST_NO_AUTORESIZE)
        self.staticTextAnnounce.SetForegroundColour(wx.Colour(170, 0, 0))
        self.staticTextAnnounce.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD, False, 'MS Shell Dlg'))

        self.staticTextInstructions = wx.StaticText(self,wx.ID_ANY,
                                                    _('After you download the latest version setup file simply run it and install over the existing version.'),
                                                    size=(-1,30)
                                                    )
     
        self.staticTextChangelog = wx.StaticText(self,wx.ID_ANY,_('List Of Changes in Version %s:')) #,style=wx.ST_NO_AUTORESIZE)


        self.checkBoxDontCheck = wx.CheckBox(self,wx.ID_ANY,_('&Do Not Check for Updates in Future'))
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckBoxDontCheckCheckbox,self.checkBoxDontCheck)

        self.buttonDownload = wx.Button(self,wx.ID_ANY,_('&Download'))
        self.buttonDownload.SetDefault()
        self.Bind(wx.EVT_BUTTON,self.OnButtonDownload,self.buttonDownload)

        self.buttonClose = wx.Button(self,wx.ID_ANY,_('Close'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonClose,self.buttonClose)

        self.html = html.HtmlWindow(self,style = wx.STATIC_BORDER)

        #sizers
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.staticTextAnnounce,0,wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT,10)
        sizer.Add(self.staticTextInstructions,0,wx.EXPAND|wx.RIGHT|wx.LEFT,10)
        sizer.Add(self.staticTextChangelog,0,wx.EXPAND|wx.RIGHT|wx.LEFT,10)
        sizer.Add(self.html,1,wx.EXPAND|wx.RIGHT|wx.LEFT,10)
        sizer.Add(self.checkBoxDontCheck,0,wx.EXPAND|wx.ALL,10)
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.buttonDownload)
        sizer1.Add((10,-1))
        sizer1.Add(self.buttonClose)
        sizer.Add(sizer1,0,wx.ALIGN_RIGHT|wx.BOTTOM |wx.RIGHT|wx.LEFT,10)

        self.SetSizer(sizer)


        #move window above tray
        client_size = wx.GetClientDisplayRect()
        size = self.GetSize()
        self.Move((client_size.GetWidth()-size.GetWidth()-5,client_size.GetHeight()-size.GetHeight()-5))

        # set window icons
        icons = wx.IconBundle()
        icons.AddIconFromFile('img/FrameIcon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcons(icons)

        self._url = url
        self._config = config
        self.html.AppendToPage(changelog)
        self.staticTextAnnounce.SetLabel(self.staticTextAnnounce.GetLabel() % version)
        self.staticTextChangelog.SetLabel(self.staticTextChangelog.GetLabel() % version)

        self.checkBoxDontCheck.SetValue(not bool(self._config.Get('Updates', 'CheckVersion')))


    def OnCharHook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_OK)
        else:
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
        DialogUtils.GoToInternetUrl(self._url)
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

    dlg = DialogUpdateChecker(None, config, version, url, changelog)
    dlg.ShowModal()
    dlg.Destroy()

    config.Write()
    app.MainLoop()


