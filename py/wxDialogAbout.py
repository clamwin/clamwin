1#-----------------------------------------------------------------------------
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



from wxPython.wx import *
from wxPython.lib.stattext import wxGenStaticText
from wxPython.html import *
import Process
import os, time, tempfile, locale
import wxDialogUtils, Utils, version

def create(parent, config):
    return wxAboutDlg(parent, config)

[wxID_WXABOUTDLG, wxID_WXABOUTDLGBUTTONOK,
 wxID_WXABOUTDLGGENSTATICTEXTCLAMWINHOME2, wxID_WXABOUTDLGSTATICBITMAPCLAM,
 wxID_WXABOUTDLGSTATICBITMAPCLAMAV, wxID_WXABOUTDLGSTATICBITMAPCLAMWIN,
 wxID_WXABOUTDLGSTATICBITMAPFDLOGO, wxID_WXABOUTDLGSTATICBITMAPNETFARM,
 wxID_WXABOUTDLGSTATICBITMAPSUPPORT, wxID_WXABOUTDLGSTATICLINE1,
 wxID_WXABOUTDLGSTATICTEXTAUTHOR1, wxID_WXABOUTDLGSTATICTEXTAUTHOR2,
 wxID_WXABOUTDLGSTATICTEXTCLAMVER, wxID_WXABOUTDLGSTATICTEXTCLAMWINHOME,
 wxID_WXABOUTDLGSTATICTEXTCOPYRIGHT, wxID_WXABOUTDLGSTATICTEXTDBUPDATED1,
 wxID_WXABOUTDLGSTATICTEXTDBUPDATED2, wxID_WXABOUTDLGSTATICTEXTDBUPDATED3,
 wxID_WXABOUTDLGSTATICTEXTFREESW, wxID_WXABOUTDLGSTATICTEXTWINCLAMVER,
] = map(lambda _init_ctrls: wxNewId(), range(20))


class wxAboutDlg(wxDialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_WXABOUTDLG, name='wxAboutDlg',
              parent=prnt, pos=wxPoint(985, 463), size=wxSize(471, 363),
              style=wxDEFAULT_DIALOG_STYLE,
              title='About ClamWin Free Antivirus')
        self.SetClientSize(wxSize(463, 336))
        self.SetBackgroundColour(wxColour(255, 255, 255))
        self.SetAutoLayout(false)
        self.SetToolTipString('About ClamWin Free Antivirus')
        self.Center(wxBOTH)
        EVT_CHAR_HOOK(self, self.OnCharHook)

        self.staticBitmapClamWin = wxStaticBitmap(bitmap=wxBitmap('img/Title.png',
              wxBITMAP_TYPE_PNG), id=wxID_WXABOUTDLGSTATICBITMAPCLAMWIN,
              name='staticBitmapClamWin', parent=self, pos=wxPoint(6, 8),
              size=wxSize(256, 40), style=0)
        self.staticBitmapClamWin.SetToolTipString('')

        self.staticTextWinClamVer = wxStaticText(id=wxID_WXABOUTDLGSTATICTEXTWINCLAMVER,
              label='Version ' + version.clamwin_version, name='staticTextWinClamVer', parent=self,
              pos=wxPoint(13, 48), size=wxSize(52, 16), style=0)
        self.staticTextWinClamVer.SetFont(wxFont(10, wxSWISS, wxNORMAL, wxBOLD,
              False))
        self.staticTextWinClamVer.SetToolTipString('')

        self.staticTextClamVer = wxStaticText(id=wxID_WXABOUTDLGSTATICTEXTCLAMVER,
              label='ClamAV Version gets here', name='staticTextClamVer',
              parent=self, pos=wxPoint(13, 96), size=wxSize(291, 15), style=0)
        self.staticTextClamVer.SetToolTipString('')

        self.staticTextDBUpdated1 = wxStaticText(id=wxID_WXABOUTDLGSTATICTEXTDBUPDATED1,
              label='Protecting from %i Viruses', name='staticTextDBUpdated1',
              parent=self, pos=wxPoint(13, 112), size=wxSize(291, 15), style=0)
        self.staticTextDBUpdated1.SetToolTipString('')

        self.staticBitmapClam = wxStaticBitmap(bitmap=wxBitmap('img/Clam.png',
              wxBITMAP_TYPE_PNG), id=wxID_WXABOUTDLGSTATICBITMAPCLAM,
              name='staticBitmapClam', parent=self, pos=wxPoint(300, 10),
              size=wxSize(162, 163), style=0)
        self.staticBitmapClam.SetCursor(wxStockCursor(wxCURSOR_HAND))
        self.staticBitmapClam.SetToolTipString('ClamWin Free Antivirus Homepage')
        EVT_LEFT_DOWN(self.staticBitmapClam, self.OnClamWinHomePage)

        self.staticBitmapSupport = wxStaticBitmap(bitmap=wxBitmap('img/Support.png',
              wxBITMAP_TYPE_PNG), id=wxID_WXABOUTDLGSTATICBITMAPSUPPORT,
              name='staticBitmapSupport', parent=self, pos=wxPoint(365, 185),
              size=wxSize(88, 32), style=0)
        self.staticBitmapSupport.SetToolTipString('Donate to ClamWin')
        self.staticBitmapSupport.SetCursor(wxStockCursor(wxCURSOR_HAND))
        EVT_LEFT_DOWN(self.staticBitmapSupport, self.OnDonateClamWin)

        self.staticTextClamWinHome = wxStaticText(id=wxID_WXABOUTDLGSTATICTEXTCLAMWINHOME,
              label='Website:', name='staticTextClamWinHome', parent=self,
              pos=wxPoint(13, 68), size=wxSize(59, 15), style=0)
        self.staticTextClamWinHome.SetToolTipString('')

        self.genStaticTextClamWinHome2 = wxGenStaticText(ID=wxID_WXABOUTDLGGENSTATICTEXTCLAMWINHOME2,
              label='http://www.clamwin.com', name='genStaticTextClamWinHome2',
              parent=self, pos=wxPoint(69, 68), size=wxSize(187, 15),
              style=wxTRANSPARENT_WINDOW)
        self.genStaticTextClamWinHome2.SetForegroundColour(wxColour(0, 0, 255))
        self.genStaticTextClamWinHome2.SetCursor(wxStockCursor(wxCURSOR_HAND))
        self.genStaticTextClamWinHome2.SetToolTipString('ClamWin Free Antivirus Homepage')
        EVT_LEFT_DOWN(self.genStaticTextClamWinHome2, self.OnClamWinHomePage)

        self.staticTextAuthor1 = wxStaticText(id=wxID_WXABOUTDLGSTATICTEXTAUTHOR1,
              label='Authors: alch <alch@users.sourceforge.net>',
              name='staticTextAuthor1', parent=self, pos=wxPoint(13, 173),
              size=wxSize(210, 13), style=0)
        self.staticTextAuthor1.SetToolTipString('')

        self.staticTextCopyright = wxStaticText(id=wxID_WXABOUTDLGSTATICTEXTCOPYRIGHT,
              label='Copyright ClamWin Pty Ltd (c) 2004 - 2008',
              name='staticTextCopyright', parent=self, pos=wxPoint(13, 208),
              size=wxSize(200, 13), style=0)
        self.staticTextCopyright.SetToolTipString('')

        self.staticTextFreeSW = wxStaticText(id=wxID_WXABOUTDLGSTATICTEXTFREESW,
              label='This program is free software', name='staticTextFreeSW',
              parent=self, pos=wxPoint(13, 224), size=wxSize(135, 13), style=0)
        self.staticTextFreeSW.SetToolTipString('')

        self.staticLine1 = wxStaticLine(id=wxID_WXABOUTDLGSTATICLINE1,
              name='staticLine1', parent=self, pos=wxPoint(-2, 246),
              size=wxSize(480, 2), style=0)

        self.staticBitmapFDLogo = wxStaticBitmap(bitmap=wxBitmap('img/FD-logo.png',
              wxBITMAP_TYPE_PNG), id=wxID_WXABOUTDLGSTATICBITMAPFDLOGO,
              name='staticBitmapFDLogo', parent=self, pos=wxPoint(314, 257),
              size=wxSize(143, 33), style=0)
        self.staticBitmapFDLogo.SetToolTipString('Finndesign Homepage')
        self.staticBitmapFDLogo.SetCursor(wxStockCursor(wxCURSOR_HAND))
        EVT_LEFT_DOWN(self.staticBitmapFDLogo, self.OnFDHomePage)

        self.buttonOK = wxButton(id=wxID_WXABOUTDLGBUTTONOK, label='OK',
              name='buttonOK', parent=self, pos=wxPoint(192, 302),
              size=wxSize(71, 23), style=0)
        EVT_BUTTON(self.buttonOK, wxID_WXABOUTDLGBUTTONOK, self.OnOK)

        self.staticTextDBUpdated2 = wxStaticText(id=wxID_WXABOUTDLGSTATICTEXTDBUPDATED2,
              label='Virus DB Version: (main: %i; daily: %i)',
              name='staticTextDBUpdated2', parent=self, pos=wxPoint(13, 128),
              size=wxSize(291, 15), style=0)
        self.staticTextDBUpdated2.SetToolTipString('')

        self.staticTextDBUpdated3 = wxStaticText(id=wxID_WXABOUTDLGSTATICTEXTDBUPDATED3,
              label='Updated: %s', name='staticTextDBUpdated3', parent=self,
              pos=wxPoint(13, 144), size=wxSize(291, 16), style=0)
        self.staticTextDBUpdated3.SetToolTipString('')

        self.staticTextAuthor2 = wxStaticText(id=wxID_WXABOUTDLGSTATICTEXTAUTHOR2,
              label='Gianluigi Tiesi <sherpya@users.sourceforge.net>',
              name='staticTextAuthor2', parent=self, pos=wxPoint(13, 189),
              size=wxSize(230, 13), style=0)
        self.staticTextAuthor2.SetToolTipString('')

        self.staticBitmapNetfarm = wxStaticBitmap(bitmap=wxBitmap('img/netfarm.png',
              wxBITMAP_TYPE_PNG), id=wxID_WXABOUTDLGSTATICBITMAPNETFARM,
              name='staticBitmapNetfarm', parent=self, pos=wxPoint(143, 257),
              size=wxSize(160, 33), style=0)
        self.staticBitmapNetfarm.SetToolTipString('Netfarm Homepage')
        self.staticBitmapNetfarm.SetCursor(wxStockCursor(wxCURSOR_HAND))
        EVT_LEFT_DOWN(self.staticBitmapNetfarm, self.OnNetfarmHomepage)

        self.staticBitmapClamAV = wxStaticBitmap(bitmap=wxBitmap('img/ClamAV.png',
              wxBITMAP_TYPE_PNG), id=wxID_WXABOUTDLGSTATICBITMAPCLAMAV,
              name='staticBitmapClamAV', parent=self, pos=wxPoint(7, 256),
              size=wxSize(125, 34), style=0)
        self.staticBitmapClamAV.SetToolTipString('ClamAV Homepage')
        self.staticBitmapClamAV.SetCursor(wxStockCursor(wxCURSOR_HAND))
        EVT_LEFT_DOWN(self.staticBitmapClamAV, self.OnClamAVHomePage)

    def __init__(self, parent,  config=None):
        self._init_ctrls(parent)
        self. config = config
        self._SetClamVersion()
        self._SetDBInfo()
        self.SetDefaultItem(self.buttonOK)
        self.buttonOK.SetDefault()
        self.staticTextClamVer.SetSize(wxSize(255, 36));

    def OnOK(self, event):
        self.EndModal(wxID_OK)

    def OnCharHook(self, event):
        if event.GetKeyCode() == WXK_ESCAPE:
            self.EndModal(wxID_CANCEL)
        event.Skip()

    def OnClamAVHomePage(self, event):
        wxDialogUtils.wxGoToInternetUrl('http://www.clamav.net')

    def OnClamWinHomePage(self, event):
        wxDialogUtils.wxGoToInternetUrl('http://www.clamwin.com')

    def OnNetfarmHomepage(self, event):
        wxDialogUtils.wxGoToInternetUrl('http://oss.netfarm.it/clamav/')

    def OnDonateClamWin(self, event):
        wxDialogUtils.wxGoToInternetUrl('http://sourceforge.net/donate/index.php?group_id=105508')

    def OnFDHomePage(self, event):
        wxDialogUtils.wxGoToInternetUrl('http://www.finndesign.fi')

    def _SetClamVersion(self):
        if self.config is None:
            return
        if not os.path.exists(self.config.Get('ClamAV', 'ClamScan')):
            ver  = 'Could not locate ClamScan executable'
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
                ver = 'Unable to retrieve ClamAV version'
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
            updatedstr = 'Unable to retrieve database verison'
        self.staticTextDBUpdated1.SetLabel(self.staticTextDBUpdated1.GetLabel() % \
            (mainnumv + dailynumv))
        self.staticTextDBUpdated2.SetLabel(self.staticTextDBUpdated2.GetLabel() % \
            (mainver, dailyver))
        self.staticTextDBUpdated3.SetLabel(self.staticTextDBUpdated3.GetLabel() % \
            updatedstr)
