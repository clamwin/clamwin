#-----------------------------------------------------------------------------
#Boa:Dialog:wxAboutDlg

#-----------------------------------------------------------------------------
# Name:        wxDialogAbout.py
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



import wx
import wx.lib.hyperlink as hyperlink
import Process
import os, time, tempfile, locale
import DialogUtils
import Utils
import version


class AboutDlg(wx.Dialog):
    def __init__(self, parent, config=None):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, _('About ClamWin Free Antivirus'),style=wx.DEFAULT_DIALOG_STYLE)
        self.SetClientSize(wx.Size(463, 336))
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.SetAutoLayout(False)
        self.SetToolTipString(_('About ClamWin Free Antivirus'))
        self.Center(wx.BOTH)
        self.Bind(wx.EVT_CHAR_HOOK, self.OnCharHook)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer1 = wx.BoxSizer(wx.VERTICAL)

        self.staticBitmapClamWin = wx.StaticBitmap(self,wx.ID_ANY,wx.Bitmap('img/Title.png',wx.BITMAP_TYPE_PNG))
        sizer1.Add(self.staticBitmapClamWin)
                                            
        self.staticTextWinClamVer = wx.StaticText(self,wx.ID_ANY,_('Version ')  + version.clamwin_version)
        self.staticTextWinClamVer.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD, False))
        sizer1.Add(self.staticTextWinClamVer)

        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
    
        self.staticTextClamWinHome = wx.StaticText(self, wx.ID_ANY,_('Website:'))
        sizer3.Add(self.staticTextClamWinHome)

        self.genStaticTextClamWinHome2 = hyperlink.HyperLinkCtrl(self,wx.ID_ANY,_('http://www.clamwin.com'),URL=_('http://www.clamwin.com'))
        self.genStaticTextClamWinHome2.SetToolTipString(_('ClamWin Free Antivirus Homepage'))
        self.Bind(hyperlink.EVT_HYPERLINK_LEFT, self.OnClamWinHomePage, self.genStaticTextClamWinHome2)
        sizer3.Add(self.genStaticTextClamWinHome2)

        sizer1.Add(sizer3)

        sizer1.Add((-1,10))

        self.staticTextClamVer = wx.StaticText(self,wx.ID_ANY,_('ClamAV Version gets here'))
        sizer1.Add(self.staticTextClamVer)

        self.staticTextDBUpdated1 = wx.StaticText(self,wx.ID_ANY,_('Protecting from %i Viruses'))
        sizer1.Add(self.staticTextDBUpdated1)

        self.staticTextDBUpdated2 = wx.StaticText(self, wx.ID_ANY,_('Virus DB Version: (main: %i; daily: %i)'))
        sizer1.Add(self.staticTextDBUpdated2)

        self.staticTextDBUpdated3 = wx.StaticText(self, wx.ID_ANY, _('Updated: %s'))
        sizer1.Add(self.staticTextDBUpdated3)

        sizer1.Add((-1,10))

        self.staticTextAuthor1 = wx.StaticText(self,wx.ID_ANY,_('Author: alch <alch@users.sourceforge.net>'))
        sizer1.Add(self.staticTextAuthor1)
        
        self.staticTextAuthor2 = wx.StaticText(self, wx.ID_ANY, 'Gianluigi Tiesi <sherpya@users.sourceforge.net>')
        sizer1.Add(self.staticTextAuthor2)

        sizer1.Add((-1,5))

        self.staticTextCopyright = wx.StaticText(self,wx.ID_ANY,_('Copyright (c) 2004 - 2007'))
        sizer1.Add(self.staticTextCopyright)

        self.staticTextFreeSW = wx.StaticText(self,wx.ID_ANY,_('This program is free software'))
        sizer1.Add(self.staticTextFreeSW)

        sizer2 = wx.BoxSizer(wx.VERTICAL)
        
        self.staticBitmapClam = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap('img/Clam.png',wx.BITMAP_TYPE_PNG))
        self.staticBitmapClam.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.staticBitmapClam.SetToolTipString(_('ClamWin Free Antivirus Homepage'))
        self.Bind(wx.EVT_LEFT_DOWN,self.OnClamWinHomePage,self.staticBitmapClam)
        sizer2.Add(self.staticBitmapClam,0,wx.ALIGN_RIGHT)

        self.staticBitmapSupport = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap('img/Support.png',wx.BITMAP_TYPE_PNG))
        self.staticBitmapSupport.SetToolTipString(_('Donate to ClamWin'))
        self.staticBitmapSupport.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.Bind(wx.EVT_LEFT_DOWN, self.OnDonateClamWin,self.staticBitmapSupport)
        sizer2.Add(self.staticBitmapSupport,0,wx.ALIGN_RIGHT)

        sizer5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer5.Add(sizer1)
        sizer5.Add(sizer2)

        sizer.Add(sizer5,0,wx.EXPAND|wx.ALL,10)

        self.staticLine1 = wx.StaticLine(self,wx.ID_ANY)
        sizer.Add(self.staticLine1,0,wx.EXPAND|wx.ALL,10)

        sizer4 = wx.BoxSizer(wx.HORIZONTAL)

        self.staticBitmapClamAV = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap('img/ClamAV.png',wx.BITMAP_TYPE_PNG))
        self.staticBitmapClamAV.SetToolTipString(_('ClamAV Homepage'))
        self.staticBitmapClamAV.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClamAVHomePage,self.staticBitmapClamAV)
        sizer4.Add(self.staticBitmapClamAV,0,wx.RIGHT | wx.LEFT,5)

        self.staticBitmapNetfarm = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap('img/netfarm.png', wx.BITMAP_TYPE_PNG))
        self.staticBitmapNetfarm.SetToolTipString(_('Netfarm Homepage'))
        self.staticBitmapNetfarm.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.Bind(wx.EVT_LEFT_DOWN, self.OnNetfarmHomepage, self.staticBitmapNetfarm)
        sizer4.Add(self.staticBitmapNetfarm,0,wx.RIGHT | wx.LEFT,5)

        self.staticBitmapFDLogo = wx.StaticBitmap(self,wx.ID_ANY,wx.Bitmap('img/FD-logo.png', wx.BITMAP_TYPE_PNG))
        self.staticBitmapFDLogo.SetToolTipString(_('Finndesign Homepage'))
        self.staticBitmapFDLogo.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.Bind(wx.EVT_LEFT_DOWN, self.OnFDHomePage, self.staticBitmapFDLogo)
        sizer4.Add(self.staticBitmapFDLogo,0,wx.RIGHT | wx.LEFT,5)

        sizer.Add(sizer4,0,wx.ALIGN_CENTER_HORIZONTAL | wx.ALL,10)

        self.buttonOK = wx.Button(self, wx.ID_OK, _('OK'))
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.buttonOK)
        sizer.Add(self.buttonOK,0,wx.ALIGN_CENTER_HORIZONTAL|wx.ALL,10)

        self.SetSizer(sizer)

        self.config = config
        self._SetClamVersion()
        self._SetDBInfo()
        self.SetDefaultItem(self.buttonOK)
        self.buttonOK.SetDefault()
        self.staticTextClamVer.SetSize(wx.Size(255, 36))

    def OnOK(self, event):
        self.EndModal(wx.ID_OK)

    def OnCharHook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        event.Skip()

    def OnClamAVHomePage(self, event):
        DialogUtils.GoToInternetUrl('http://www.clamav.net')

    def OnClamWinHomePage(self, event):
        DialogUtils.GoToInternetUrl(_('http://www.clamwin.com'))

    def OnNetfarmHomepage(self, event):
        DialogUtils.GoToInternetUrl('http://oss.netfarm.it/clamav/')

    def OnDonateClamWin(self, event):
        DialogUtils.GoToInternetUrl('http://sourceforge.net/donate/index.php?group_id=105508')

    def OnFDHomePage(self, event):
        DialogUtils.GoToInternetUrl('http://www.finndesign.fi')

    def _SetClamVersion(self):
        if self.config is None:
            return
        if not os.path.exists(self.config.Get('ClamAV', 'ClamScan')):
            ver  = _('Could not locate ClamScan executable')
        else:
            cmd = '"' + self.config.Get('ClamAV', 'ClamScan')  + '" --stdout --version'
            proc = None
            try:
                proc = Process.ProcessOpen(cmd)
                proc.wait()
                ver = proc.stdout.readline()
                # remove date from the clamav version
                # for some reason it is 01/01/1970 for cygwin builds
                pos = ver.rfind('/')
                ver = ver[:pos]
            except:
                ver = _('Unable to retrieve ClamAV version')        
            if proc is not None:
                proc.close()
        self.staticTextClamVer.SetLabel(ver)

    def _SetDBInfo(self):
        try:
            dbpath =  self.config.Get('ClamAV', 'Database')
            mainver, mainnumv = Utils.GetDBInfo(os.path.join(dbpath, 'main.cvd'))[:2]
            if mainver is None:
                mainver, mainnumv = Utils.GetDBInfo(os.path.join(os.path.join(dbpath, 'main.inc'), 'main.info'))[:2]                
            if mainver is None:
                raise Exception()
            dailyver, dailynumv, updated = Utils.GetDBInfo(os.path.join(dbpath, 'daily.cvd'))
            if dailyver is None:            
                dailyver, dailynumv, updated = Utils.GetDBInfo(os.path.join(os.path.join(dbpath, 'daily.inc'), 'daily.info'))
            if dailyver is None:                            
                raise Exception()
            else:
                # set user's locale
                loc = locale.setlocale(locale.LC_TIME, '')
                try:
                    updatedstr = time.strftime('%H:%M %d %b %Y', time.localtime(updated))
                finally:
                    # restore the locale back to what it was
                    locale.setlocale(locale.LC_TIME, loc)
        except:
            dailyver, dailynumv = (0, 0)
            mainver, mainnumv = (0, 0)
            updatedstr = _('Unable to retrieve database verison')        
        self.staticTextDBUpdated1.SetLabel(self.staticTextDBUpdated1.GetLabel() % \
            (mainnumv + dailynumv))
        self.staticTextDBUpdated2.SetLabel(self.staticTextDBUpdated2.GetLabel() % \
            (mainver, dailyver))
        self.staticTextDBUpdated3.SetLabel(self.staticTextDBUpdated3.GetLabel() % \
            updatedstr)

if __name__ == '__main__':
    
    app = wx.App()
    dlg = AboutDlg(None)
    dlg.ShowModal()
    app.MainLoop()
    dlg.Destroy()
