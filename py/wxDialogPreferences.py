#-----------------------------------------------------------------------------
#Boa:Dialog:wxPreferencesDlg

#-----------------------------------------------------------------------------
# Name:        wxDialogPreferences.py
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
from wxPython.gizmos import *
from wxPython.lib.intctrl import *
from wxPython.lib.timectrl import *
import MsgBox, Utils, EmailAlert, Config
import os, sys, time, locale
import wxDialogScheduledScan

def create(parent, config=None, switchToSchedule=False):
    return wxPreferencesDlg(parent, config, switchToSchedule)

[wxID_WXPREFERENCESDLG, wxID_WXPREFERENCESDLGBUTTONBROWSECLAMSCAN, 
 wxID_WXPREFERENCESDLGBUTTONBROWSEFRESHCLAM, 
 wxID_WXPREFERENCESDLGBUTTONBROWSEQUARANTINE, 
 wxID_WXPREFERENCESDLGBUTTONBROWSESCANLOG, 
 wxID_WXPREFERENCESDLGBUTTONBROWSEUPDATELOG, 
 wxID_WXPREFERENCESDLGBUTTONCANCEL, wxID_WXPREFERENCESDLGBUTTONOK, 
 wxID_WXPREFERENCESDLGBUTTONSENDTESTEMAIL, 
 wxID_WXPREFERENCESDLGBUTTONTASKACTIVATE, wxID_WXPREFERENCESDLGBUTTONTASKADD, 
 wxID_WXPREFERENCESDLGBUTTONTASKDEACTIVATE, 
 wxID_WXPREFERENCESDLGBUTTONTASKEDIT, wxID_WXPREFERENCESDLGBUTTONTASKREMOVE, 
 wxID_WXPREFERENCESDLGBUTTONVIRDB, wxID_WXPREFERENCESDLGCHECKBOXCHECKVERSION, 
 wxID_WXPREFERENCESDLGCHECKBOXENABLEAUTOUPDATE, 
 wxID_WXPREFERENCESDLGCHECKBOXENABLEMBOX, 
 wxID_WXPREFERENCESDLGCHECKBOXENABLEOLE2, 
 wxID_WXPREFERENCESDLGCHECKBOXINFECTEDONLY, 
 wxID_WXPREFERENCESDLGCHECKBOXOUTLOOKSCANINCOMING, 
 wxID_WXPREFERENCESDLGCHECKBOXOUTLOOKSCANOUTGOING, 
 wxID_WXPREFERENCESDLGCHECKBOXSCANARCHIVES, 
 wxID_WXPREFERENCESDLGCHECKBOXSCANEXEONLY, 
 wxID_WXPREFERENCESDLGCHECKBOXSCANRECURSIVE, 
 wxID_WXPREFERENCESDLGCHECKBOXSHOWPROGRESS, 
 wxID_WXPREFERENCESDLGCHECKBOXSMTPENABLE, 
 wxID_WXPREFERENCESDLGCHECKBOXTRAYNOTIFY, wxID_WXPREFERENCESDLGCHECKBOXUNLOAD, 
 wxID_WXPREFERENCESDLGCHECKBOXUPDATELOGON, 
 wxID_WXPREFERENCESDLGCHOICEPRIORITY, wxID_WXPREFERENCESDLGCHOICEUPDATEDAY, 
 wxID_WXPREFERENCESDLGCHOICEUPDATEFREQUENCY, 
 wxID_WXPREFERENCESDLGEDITABLELISTBOXFILTERSEXCLUDE, 
 wxID_WXPREFERENCESDLGEDITABLELISTBOXFILTERSINCLUDE, 
 wxID_WXPREFERENCESDLGINTCTRLPROXYPORT, wxID_WXPREFERENCESDLGINTCTRLSMTPPORT, 
 wxID_WXPREFERENCESDLGLISTVIEWSCHEDULEDTASKS, wxID_WXPREFERENCESDLGNOTEBOOK, 
 wxID_WXPREFERENCESDLGRADIOBUTTONQUARANTINE, 
 wxID_WXPREFERENCESDLGRADIOBUTTONREMOVEINFECTED, 
 wxID_WXPREFERENCESDLGRADIOBUTTONREPORT, 
 wxID_WXPREFERENCESDLGSPINBUTTONUPDATETIME, 
 wxID_WXPREFERENCESDLGSPINCTRLARCHIVEFILES, 
 wxID_WXPREFERENCESDLGSPINCTRLARCHIVESIZE, 
 wxID_WXPREFERENCESDLGSPINCTRLMAXLOGSIZE, 
 wxID_WXPREFERENCESDLGSPINCTRLRECURSION, 
 wxID_WXPREFERENCESDLGSTATICBOXEMAILDETAILS, 
 wxID_WXPREFERENCESDLGSTATICBOXINFECTED, 
 wxID_WXPREFERENCESDLGSTATICBOXOUTLOOKADDIN, 
 wxID_WXPREFERENCESDLGSTATICBOXSCANOPTIONS, 
 wxID_WXPREFERENCESDLGSTATICBOXSMTPCONNECTION, 
 wxID_WXPREFERENCESDLGSTATICLINEUPDATETIMECTRL, 
 wxID_WXPREFERENCESDLGSTATICTEXT1, wxID_WXPREFERENCESDLGSTATICTEXT2, 
 wxID_WXPREFERENCESDLGSTATICTEXTADDITIONALPARAMS, 
 wxID_WXPREFERENCESDLGSTATICTEXTCLAMSCAN, 
 wxID_WXPREFERENCESDLGSTATICTEXTDBUPDATELOGFILE, 
 wxID_WXPREFERENCESDLGSTATICTEXTEXPLAIN, wxID_WXPREFERENCESDLGSTATICTEXTFILES, 
 wxID_WXPREFERENCESDLGSTATICTEXTFILTERSEXCLUDE, 
 wxID_WXPREFERENCESDLGSTATICTEXTFILTERSINCLUDE, 
 wxID_WXPREFERENCESDLGSTATICTEXTFILTREDESC1, 
 wxID_WXPREFERENCESDLGSTATICTEXTFRESHCLAM, 
 wxID_WXPREFERENCESDLGSTATICTEXTLIMITFILES, 
 wxID_WXPREFERENCESDLGSTATICTEXTLOGFILE, 
 wxID_WXPREFERENCESDLGSTATICTEXTMAXLOGSIZE, 
 wxID_WXPREFERENCESDLGSTATICTEXTMAXSIZE, wxID_WXPREFERENCESDLGSTATICTEXTMB1, 
 wxID_WXPREFERENCESDLGSTATICTEXTMB2, 
 wxID_WXPREFERENCESDLGSTATICTEXTNOPERSONAL, 
 wxID_WXPREFERENCESDLGSTATICTEXTPRIORITY, 
 wxID_WXPREFERENCESDLGSTATICTEXTPROXYHOST, 
 wxID_WXPREFERENCESDLGSTATICTEXTPROXYPASSWORD, 
 wxID_WXPREFERENCESDLGSTATICTEXTPROXYPORT, 
 wxID_WXPREFERENCESDLGSTATICTEXTPROXYUSER, 
 wxID_WXPREFERENCESDLGSTATICTEXTRECURSION, 
 wxID_WXPREFERENCESDLGSTATICTEXTSCHEDULEDTASKS, 
 wxID_WXPREFERENCESDLGSTATICTEXTSMTPFROM, 
 wxID_WXPREFERENCESDLGSTATICTEXTSMTPHOST, 
 wxID_WXPREFERENCESDLGSTATICTEXTSMTPPASSWORD, 
 wxID_WXPREFERENCESDLGSTATICTEXTSMTPPORT, 
 wxID_WXPREFERENCESDLGSTATICTEXTSMTPSUBJECT, 
 wxID_WXPREFERENCESDLGSTATICTEXTSMTPTO, 
 wxID_WXPREFERENCESDLGSTATICTEXTSMTPUSERNAME, 
 wxID_WXPREFERENCESDLGSTATICTEXTSUBARCHIVES, 
 wxID_WXPREFERENCESDLGSTATICTEXTUPDATEDAY, 
 wxID_WXPREFERENCESDLGSTATICTEXTUPDATEFREQUENCY, 
 wxID_WXPREFERENCESDLGSTATICTEXTUPDATETIME, 
 wxID_WXPREFERENCESDLGSTATICTEXTVIRDB, 
 wxID_WXPREFERENCESDLGTEXTCTRLADDITIONALPARAMS, 
 wxID_WXPREFERENCESDLGTEXTCTRLCLAMSCAN, wxID_WXPREFERENCESDLGTEXTCTRLDBMIRROR, 
 wxID_WXPREFERENCESDLGTEXTCTRLFRESHCLAM, 
 wxID_WXPREFERENCESDLGTEXTCTRLPROXYHOST, 
 wxID_WXPREFERENCESDLGTEXTCTRLPROXYPASSWORD, 
 wxID_WXPREFERENCESDLGTEXTCTRLPROXYUSER, 
 wxID_WXPREFERENCESDLGTEXTCTRLQUARANTINE, 
 wxID_WXPREFERENCESDLGTEXTCTRLSCANLOGFILE, 
 wxID_WXPREFERENCESDLGTEXTCTRLSMTPFROM, wxID_WXPREFERENCESDLGTEXTCTRLSMTPHOST, 
 wxID_WXPREFERENCESDLGTEXTCTRLSMTPPASSWORD, 
 wxID_WXPREFERENCESDLGTEXTCTRLSMTPSUBJECT, 
 wxID_WXPREFERENCESDLGTEXTCTRLSMTPTO, wxID_WXPREFERENCESDLGTEXTCTRLSMTPUSER, 
 wxID_WXPREFERENCESDLGTEXTCTRLUPDATELOGFILE, 
 wxID_WXPREFERENCESDLGTEXTCTRLVIRDB, wxID_WXPREFERENCESDLG_PANELADVANCED, 
 wxID_WXPREFERENCESDLG_PANELARCHIVES, wxID_WXPREFERENCESDLG_PANELEMAILALERTS, 
 wxID_WXPREFERENCESDLG_PANELEMAILSCANNING, wxID_WXPREFERENCESDLG_PANELFILES, 
 wxID_WXPREFERENCESDLG_PANELFILTERS, 
 wxID_WXPREFERENCESDLG_PANELINTERNETUPDATE, 
 wxID_WXPREFERENCESDLG_PANELOPTIONS, wxID_WXPREFERENCESDLG_PANELPROXY, 
 wxID_WXPREFERENCESDLG_PANELREPORTS, wxID_WXPREFERENCESDLG_PANELSCHEDULER, 
] = map(lambda _init_ctrls: wxNewId(), range(118))

class wxPreferencesDlg(wxDialog):
    def _init_coll_imageListScheduler_Images(self, parent):
        # generated method, don't edit

        parent.Add(bitmap=wxBitmap('img/ListScan.png', wxBITMAP_TYPE_PNG),
              mask=wxNullBitmap)

    def _init_coll_notebook_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self._panelOptions, select=True,
              text='General')
        parent.AddPage(imageId=-1, page=self._panelFilters, select=False,
              text='Filters')
        parent.AddPage(imageId=-1, page=self._panelInternetUpdate, select=False,
              text='Internet Updates')
        parent.AddPage(imageId=-1, page=self._panelProxy, select=False,
              text='Proxy')
        parent.AddPage(imageId=-1, page=self._panelScheduler, select=False,
              text='Scheduled Scans')
        parent.AddPage(imageId=-1, page=self._panelEmailAlerts, select=False,
              text='Email Alerts')
        parent.AddPage(imageId=-1, page=self._panelArchives, select=False,
              text='Archives')
        parent.AddPage(imageId=-1, page=self._panelFiles, select=False,
              text='File Locations')
        parent.AddPage(imageId=-1, page=self._panelReports, select=False,
              text='Reports')
        parent.AddPage(imageId=-1, page=self._panelEmailScanning, select=False,
              text='Email Scanning')
        parent.AddPage(imageId=-1, page=self._panelAdvanced, select=False,
              text='Advanced')

    def _init_coll_listViewScheduledTasks_Columns(self, parent):
        # generated method, don't edit

        parent.InsertColumn(col=0, format=wxLIST_FORMAT_LEFT,
              heading='Description', width=-1)
        parent.InsertColumn(col=1, format=wxLIST_FORMAT_LEFT, heading='Path',
              width=-1)
        parent.InsertColumn(col=2, format=wxLIST_FORMAT_LEFT,
              heading='Frequency', width=-1)

    def _init_utils(self):
        # generated method, don't edit
        self.imageListScheduler = wxImageList(height=16, width=16)
        self._init_coll_imageListScheduler_Images(self.imageListScheduler)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_WXPREFERENCESDLG, name='', parent=prnt,
              pos=wxPoint(523, 301), size=wxSize(419, 351),
              style=wxDEFAULT_DIALOG_STYLE, title='ClamWin Preferences')
        self._init_utils()
        self.SetClientSize(wxSize(411, 324))
        self.SetAutoLayout(False)
        self.Center(wxBOTH)
        EVT_CHAR_HOOK(self, self.OnCharHook)

        self.notebook = wxNotebook(id=wxID_WXPREFERENCESDLGNOTEBOOK,
              name='notebook', parent=self, pos=wxPoint(7, 7), size=wxSize(398,
              278), style=wxNB_MULTILINE)
        self.notebook.SetAutoLayout(true)
        self.notebook.SetToolTipString('')

        self._panelOptions = wxPanel(id=wxID_WXPREFERENCESDLG_PANELOPTIONS,
              name='_panelOptions', parent=self.notebook, pos=wxPoint(0, 0),
              size=wxSize(390, 234), style=wxTAB_TRAVERSAL)
        self._panelOptions.SetAutoLayout(False)

        self._panelInternetUpdate = wxPanel(id=wxID_WXPREFERENCESDLG_PANELINTERNETUPDATE,
              name='_panelInternetUpdate', parent=self.notebook, pos=wxPoint(0,
              0), size=wxSize(390, 234), style=wxTAB_TRAVERSAL)
        self._panelInternetUpdate.SetAutoLayout(False)

        self._panelProxy = wxPanel(id=wxID_WXPREFERENCESDLG_PANELPROXY,
              name='_panelProxy', parent=self.notebook, pos=wxPoint(0, 0),
              size=wxSize(390, 234), style=wxTAB_TRAVERSAL)
        self._panelProxy.SetAutoLayout(False)

        self._panelFiles = wxPanel(id=wxID_WXPREFERENCESDLG_PANELFILES,
              name='_panelFiles', parent=self.notebook, pos=wxPoint(0, 0),
              size=wxSize(390, 234), style=wxTAB_TRAVERSAL)
        self._panelFiles.SetAutoLayout(False)

        self._panelArchives = wxPanel(id=wxID_WXPREFERENCESDLG_PANELARCHIVES,
              name='_panelArchives', parent=self.notebook, pos=wxPoint(0, 0),
              size=wxSize(390, 234), style=wxTAB_TRAVERSAL)
        self._panelArchives.SetAutoLayout(False)

        self._panelReports = wxPanel(id=wxID_WXPREFERENCESDLG_PANELREPORTS,
              name='_panelReports', parent=self.notebook, pos=wxPoint(0, 0),
              size=wxSize(390, 234), style=wxTAB_TRAVERSAL)
        self._panelReports.SetAutoLayout(False)

        self._panelEmailScanning = wxPanel(id=wxID_WXPREFERENCESDLG_PANELEMAILSCANNING,
              name='_panelEmailScanning', parent=self.notebook, pos=wxPoint(0,
              0), size=wxSize(390, 234), style=wxTAB_TRAVERSAL)

        self._panelAdvanced = wxPanel(id=wxID_WXPREFERENCESDLG_PANELADVANCED,
              name='_panelAdvanced', parent=self.notebook, pos=wxPoint(0, 0),
              size=wxSize(390, 234), style=wxTAB_TRAVERSAL)
        self._panelAdvanced.SetAutoLayout(False)

        self.buttonOK = wxButton(id=wxID_WXPREFERENCESDLGBUTTONOK, label='OK',
              name='buttonOK', parent=self, pos=wxPoint(128, 294),
              size=wxSize(72, 23), style=0)
        self.buttonOK.SetToolTipString('Closes the window and saves the changes')
        self.buttonOK.SetDefault()
        EVT_BUTTON(self.buttonOK, wxID_WXPREFERENCESDLGBUTTONOK, self.OnOK)

        self.buttonCancel = wxButton(id=wxID_WXPREFERENCESDLGBUTTONCANCEL,
              label='Cancel', name='buttonCancel', parent=self, pos=wxPoint(209,
              294), size=wxSize(75, 23), style=0)
        self.buttonCancel.SetToolTipString('Closes the window without saving the changes')
        EVT_BUTTON(self.buttonCancel, wxID_WXPREFERENCESDLGBUTTONCANCEL,
              self.OnCancel)

        self.staticTextProxyHost = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTPROXYHOST,
              label='Proxy &Server:', name='staticTextProxyHost',
              parent=self._panelProxy, pos=wxPoint(6, 61), size=wxSize(80, 15),
              style=0)

        self.textCtrlProxyHost = wxTextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLPROXYHOST,
              name='textCtrlProxyHost', parent=self._panelProxy, pos=wxPoint(91,
              57), size=wxSize(199, 21), style=0, value='')
        self.textCtrlProxyHost.SetToolTipString('Proxy Server domain name or IP address')

        self.staticTextProxyPort = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTPROXYPORT,
              label='P&ort:', name='staticTextProxyPort',
              parent=self._panelProxy, pos=wxPoint(296, 61), size=wxSize(34,
              15), style=0)

        self.intCtrlProxyPort = wxIntCtrl(allow_long=False, allow_none=False,
              default_color=wxBLACK, id=wxID_WXPREFERENCESDLGINTCTRLPROXYPORT,
              limited=False, max=65535, min=0, name='intCtrlProxyPort',
              oob_color=wxRED, parent=self._panelProxy, pos=wxPoint(332, 57),
              size=wxSize(54, 21), style=0, value=3128)
        self.intCtrlProxyPort.SetBounds((0, 65535))
        self.intCtrlProxyPort.SetToolTipString('Proxy Server port number (0-65535)')

        self.staticTextProxyUser = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTPROXYUSER,
              label='&User Name:', name='staticTextProxyUser',
              parent=self._panelProxy, pos=wxPoint(6, 97), size=wxSize(80, 15),
              style=0)

        self.textCtrlProxyUser = wxTextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLPROXYUSER,
              name='textCtrlProxyUser', parent=self._panelProxy, pos=wxPoint(91,
              93), size=wxSize(295, 21), style=0, value='')
        self.textCtrlProxyUser.SetToolTipString('Proxy Server Account Name (optional)')

        self.staticTextProxyPassword = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTPROXYPASSWORD,
              label='&Password:', name='staticTextProxyPassword',
              parent=self._panelProxy, pos=wxPoint(6, 135), size=wxSize(80, 15),
              style=0)

        self.textCtrlProxyPassword = wxTextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLPROXYPASSWORD,
              name='textCtrlProxyPassword', parent=self._panelProxy,
              pos=wxPoint(91, 131), size=wxSize(295, 21), style=wxTE_PASSWORD,
              value='')
        self.textCtrlProxyPassword.SetToolTipString('Proxy Server account password (optional)')

        self.staticTextExplain = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTEXPLAIN,
              label='Leave these fields blank if you do not connect via Proxy Server',
              name='staticTextExplain', parent=self._panelProxy, pos=wxPoint(6,
              15), size=wxSize(378, 27), style=0)
        self.staticTextExplain.SetToolTipString('')

        self.staticBoxScanOptions = wxStaticBox(id=wxID_WXPREFERENCESDLGSTATICBOXSCANOPTIONS,
              label='Scanning Options', name='staticBoxScanOptions',
              parent=self._panelOptions, pos=wxPoint(6, 11), size=wxSize(376,
              87), style=0)

        self.checkBoxEnableAutoUpdate = wxCheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXENABLEAUTOUPDATE,
              label='&Enable Automatic Virus Database Updates',
              name='checkBoxEnableAutoUpdate', parent=self._panelInternetUpdate,
              pos=wxPoint(6, 11), size=wxSize(322, 20), style=0)
        self.checkBoxEnableAutoUpdate.SetToolTipString('Enable automatic virus database downloads ')
        EVT_CHECKBOX(self.checkBoxEnableAutoUpdate,
              wxID_WXPREFERENCESDLGCHECKBOXENABLEAUTOUPDATE,
              self.OnCheckBoxEnableAutoUpdate)

        self.staticText1 = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXT1,
              label='Download &Site :', name='staticText1',
              parent=self._panelInternetUpdate, pos=wxPoint(24, 43),
              size=wxSize(81, 13), style=0)

        self.textCtrlDBMirror = wxTextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLDBMIRROR,
              name='textCtrlDBMirror', parent=self._panelInternetUpdate,
              pos=wxPoint(126, 37), size=wxSize(243, 21), style=0, value='')
        self.textCtrlDBMirror.SetToolTipString('Specify Database Mirror Site here. Usually this is database.clamav.net')

        self.staticTextUpdateFrequency = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTUPDATEFREQUENCY,
              label='&Update Frequency:', name='staticTextUpdateFrequency',
              parent=self._panelInternetUpdate, pos=wxPoint(23, 70),
              size=wxSize(98, 18), style=0)
        self.staticTextUpdateFrequency.SetToolTipString('')

        self.choiceUpdateFrequency = wxChoice(choices=['Hourly', 'Daily',
              'Workdays', 'Weekly'],
              id=wxID_WXPREFERENCESDLGCHOICEUPDATEFREQUENCY,
              name='choiceUpdateFrequency', parent=self._panelInternetUpdate,
              pos=wxPoint(126, 67), size=wxSize(110, 21), style=0)
        self.choiceUpdateFrequency.SetColumns(2)
        self.choiceUpdateFrequency.SetToolTipString('How often virus database is downloaded')
        self.choiceUpdateFrequency.SetStringSelection('Daily')
        EVT_CHOICE(self.choiceUpdateFrequency,
              wxID_WXPREFERENCESDLGCHOICEUPDATEFREQUENCY,
              self.OnChoiceUpdateFrequency)

        self.staticTextClamScan = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTCLAMSCAN,
              label='&ClamScan Location:', name='staticTextClamScan',
              parent=self._panelFiles, pos=wxPoint(6, 15), size=wxSize(354, 13),
              style=0)
        self.staticTextClamScan.SetToolTipString('')

        self.textCtrlClamScan = wxTextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLCLAMSCAN,
              name='textCtrlClamScan', parent=self._panelFiles, pos=wxPoint(6,
              33), size=wxSize(356, 20), style=0, value='')
        self.textCtrlClamScan.SetToolTipString('Specify location of clamscan')

        self.buttonBrowseClamScan = wxButton(id=wxID_WXPREFERENCESDLGBUTTONBROWSECLAMSCAN,
              label='...', name='buttonBrowseClamScan', parent=self._panelFiles,
              pos=wxPoint(363, 34), size=wxSize(20, 20), style=0)
        self.buttonBrowseClamScan.SetToolTipString('Click to browse for clamscan')
        EVT_BUTTON(self.buttonBrowseClamScan,
              wxID_WXPREFERENCESDLGBUTTONBROWSECLAMSCAN,
              self.OnButtonBrowseClamScan)

        self.staticTextFreshClam = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTFRESHCLAM,
              label='&FreshClam Location:', name='staticTextFreshClam',
              parent=self._panelFiles, pos=wxPoint(6, 65), size=wxSize(354, 13),
              style=0)
        self.staticTextFreshClam.SetToolTipString('')

        self.textCtrlFreshClam = wxTextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLFRESHCLAM,
              name='textCtrlFreshClam', parent=self._panelFiles, pos=wxPoint(6,
              83), size=wxSize(355, 20), style=0, value='')
        self.textCtrlFreshClam.SetToolTipString('Specify location of freshclam')

        self.buttonBrowseFreshClam = wxButton(id=wxID_WXPREFERENCESDLGBUTTONBROWSEFRESHCLAM,
              label='...', name='buttonBrowseFreshClam',
              parent=self._panelFiles, pos=wxPoint(363, 83), size=wxSize(20,
              20), style=0)
        self.buttonBrowseFreshClam.SetToolTipString('Click to browse for freshclam')
        EVT_BUTTON(self.buttonBrowseFreshClam,
              wxID_WXPREFERENCESDLGBUTTONBROWSEFRESHCLAM,
              self.OnButtonBrowseFreshClam)

        self.staticTextVirDB = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTVIRDB,
              label='&Virus Database Folder:', name='staticTextVirDB',
              parent=self._panelFiles, pos=wxPoint(6, 115), size=wxSize(354,
              13), style=0)
        self.staticTextVirDB.SetToolTipString('')

        self.textCtrlVirDB = wxTextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLVIRDB,
              name='textCtrlVirDB', parent=self._panelFiles, pos=wxPoint(6,
              133), size=wxSize(355, 20), style=0, value='')
        self.textCtrlVirDB.SetToolTipString('Specify location of virus database files')

        self.buttonVirDB = wxButton(id=wxID_WXPREFERENCESDLGBUTTONVIRDB,
              label='...', name='buttonVirDB', parent=self._panelFiles,
              pos=wxPoint(362, 133), size=wxSize(20, 20), style=0)
        self.buttonVirDB.SetToolTipString('Click to browse for a virus database folder')
        EVT_BUTTON(self.buttonVirDB, wxID_WXPREFERENCESDLGBUTTONVIRDB,
              self.OnButtonBrowseVirDB)

        self.checkBoxScanRecursive = wxCheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXSCANRECURSIVE,
              label='&Scan in Subdirectories', name='checkBoxScanRecursive',
              parent=self._panelOptions, pos=wxPoint(15, 50), size=wxSize(354,
              18), style=0)
        self.checkBoxScanRecursive.SetToolTipString('Select if you wish to scan in subdirectories recursively')
        self.checkBoxScanRecursive.SetValue(False)

        self.staticTextUpdateTime = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTUPDATETIME,
              label='&Time:', name='staticTextUpdateTime',
              parent=self._panelInternetUpdate, pos=wxPoint(240, 70),
              size=wxSize(33, 18), style=0)

        self.spinButtonUpdateTime = wxSpinButton(id=wxID_WXPREFERENCESDLGSPINBUTTONUPDATETIME,
              name='spinButtonUpdateTime', parent=self._panelInternetUpdate,
              pos=wxPoint(353, 65), size=wxSize(16, 23),
              style=wxSP_ARROW_KEYS | wxSP_VERTICAL)
        self.spinButtonUpdateTime.SetToolTipString('')

        self.checkBoxScanArchives = wxCheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXSCANARCHIVES,
              label='&Scan In Archives', name='checkBoxScanArchives',
              parent=self._panelArchives, pos=wxPoint(6, 15), size=wxSize(322,
              20), style=0)
        self.checkBoxScanArchives.SetValue(False)
        EVT_CHECKBOX(self.checkBoxScanArchives,
              wxID_WXPREFERENCESDLGCHECKBOXSCANARCHIVES,
              self.OnCheckBoxScanArchives)

        self.staticTextMaxSize = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTMAXSIZE,
              label='Do Not Scan Archives Larger Than',
              name='staticTextMaxSize', parent=self._panelArchives,
              pos=wxPoint(24, 49), size=wxSize(200, 15), style=0)

        self.spinCtrlArchiveSize = wxSpinCtrl(id=wxID_WXPREFERENCESDLGSPINCTRLARCHIVESIZE,
              initial=0, max=4096, min=1, name='spinCtrlArchiveSize',
              parent=self._panelArchives, pos=wxPoint(229, 45), size=wxSize(72,
              21), style=wxSP_ARROW_KEYS)

        self.staticTextMB1 = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTMB1,
              label='MegaBytes', name='staticTextMB1',
              parent=self._panelArchives, pos=wxPoint(310, 49), size=wxSize(80,
              16), style=0)

        self.staticTextLimitFiles = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTLIMITFILES,
              label='Do Not Extract More Than ', name='staticTextLimitFiles',
              parent=self._panelArchives, pos=wxPoint(24, 82), size=wxSize(200,
              17), style=0)

        self.spinCtrlArchiveFiles = wxSpinCtrl(id=wxID_WXPREFERENCESDLGSPINCTRLARCHIVEFILES,
              initial=0, max=1073741824, min=1, name='spinCtrlArchiveFiles',
              parent=self._panelArchives, pos=wxPoint(229, 79), size=wxSize(72,
              21), style=wxSP_ARROW_KEYS)

        self.staticTextFiles = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTFILES,
              label='Files', name='staticTextFiles', parent=self._panelArchives,
              pos=wxPoint(310, 82), size=wxSize(80, 16), style=0)

        self.staticTextRecursion = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTRECURSION,
              label='Do Not Extract More Than ', name='staticTextRecursion',
              parent=self._panelArchives, pos=wxPoint(24, 118), size=wxSize(200,
              19), style=0)

        self.spinCtrlRecursion = wxSpinCtrl(id=wxID_WXPREFERENCESDLGSPINCTRLRECURSION,
              initial=0, max=999, min=1, name='spinCtrlRecursion',
              parent=self._panelArchives, pos=wxPoint(229, 115), size=wxSize(72,
              21), style=wxSP_ARROW_KEYS)

        self.staticTextSubArchives = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTSUBARCHIVES,
              label='Sub-Archives', name='staticTextSubArchives',
              parent=self._panelArchives, pos=wxPoint(310, 118), size=wxSize(82,
              16), style=0)

        self.checkBoxEnableMbox = wxCheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXENABLEMBOX,
              label='&Treat Files As Mailboxes', name='checkBoxEnableMbox',
              parent=self._panelAdvanced, pos=wxPoint(6, 11), size=wxSize(384,
              18), style=0)
        self.checkBoxEnableMbox.SetToolTipString('Select if you wish to scan mailboxes')
        self.checkBoxEnableMbox.SetValue(False)

        self.checkBoxEnableOLE2 = wxCheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXENABLEOLE2,
              label='&Extract Attachments and Macros from MS Office Documents',
              name='checkBoxEnableOLE2', parent=self._panelAdvanced,
              pos=wxPoint(6, 33), size=wxSize(381, 18), style=0)
        self.checkBoxEnableOLE2.SetToolTipString('Select if you wish to scan OLE attachments and macros in MS Office Documents')
        self.checkBoxEnableOLE2.SetValue(False)

        self.checkBoxScanExeOnly = wxCheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXSCANEXEONLY,
              label='Try to Scan &Executable Files Only',
              name='checkBoxScanExeOnly', parent=self._panelAdvanced,
              pos=wxPoint(6, 55), size=wxSize(381, 18), style=0)
        self.checkBoxScanExeOnly.SetToolTipString('Select if you wish to scan files that can be executed on MS Windows platform')
        self.checkBoxScanExeOnly.SetValue(False)

        self.staticTextAdditionalParams = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTADDITIONALPARAMS,
              label='&Additional Clamscan Command Line Parameters:',
              name='staticTextAdditionalParams', parent=self._panelAdvanced,
              pos=wxPoint(6, 79), size=wxSize(378, 13), style=0)

        self.textCtrlAdditionalParams = wxTextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLADDITIONALPARAMS,
              name='textCtrlAdditionalParams', parent=self._panelAdvanced,
              pos=wxPoint(6, 97), size=wxSize(379, 21), style=0, value='')
        self.textCtrlAdditionalParams.SetToolTipString('Specify any additional parameters for clamscan.exe')

        self.staticTextMaxLogSize = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTMAXLOGSIZE,
              label='Limit Log File Size To:', name='staticTextMaxLogSize',
              parent=self._panelAdvanced, pos=wxPoint(6, 136), size=wxSize(170,
              17), style=0)

        self.spinCtrlMaxLogSize = wxSpinCtrl(id=wxID_WXPREFERENCESDLGSPINCTRLMAXLOGSIZE,
              initial=0, max=4096, min=1, name='spinCtrlMaxLogSize',
              parent=self._panelAdvanced, pos=wxPoint(6, 155), size=wxSize(129,
              21), style=wxSP_ARROW_KEYS)
        self.spinCtrlMaxLogSize.SetToolTipString('Select maximum size for the logfile')
        self.spinCtrlMaxLogSize.SetValue(1)

        self.staticTextLogFIle = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTLOGFILE,
              label='&Scan Report File:', name='staticTextLogFIle',
              parent=self._panelReports, pos=wxPoint(6, 15), size=wxSize(354,
              19), style=0)
        self.staticTextLogFIle.SetToolTipString('')

        self.textCtrlScanLogFile = wxTextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLSCANLOGFILE,
              name='textCtrlScanLogFile', parent=self._panelReports,
              pos=wxPoint(6, 35), size=wxSize(360, 20), style=0, value='')
        self.textCtrlScanLogFile.SetToolTipString('Specify location for a scan reports log file')

        self.buttonBrowseScanLog = wxButton(id=wxID_WXPREFERENCESDLGBUTTONBROWSESCANLOG,
              label='...', name='buttonBrowseScanLog',
              parent=self._panelReports, pos=wxPoint(366, 35), size=wxSize(20,
              20), style=0)
        self.buttonBrowseScanLog.SetToolTipString('Click to browse for a log file')
        EVT_BUTTON(self.buttonBrowseScanLog,
              wxID_WXPREFERENCESDLGBUTTONBROWSESCANLOG,
              self.OnButtonBrowseScanLog)

        self.staticTextDBUpdateLogFile = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTDBUPDATELOGFILE,
              label='&Virus Database Update Report File:',
              name='staticTextDBUpdateLogFile', parent=self._panelReports,
              pos=wxPoint(6, 66), size=wxSize(354, 19), style=0)
        self.staticTextDBUpdateLogFile.SetToolTipString('')

        self.textCtrlUpdateLogFile = wxTextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLUPDATELOGFILE,
              name='textCtrlUpdateLogFile', parent=self._panelReports,
              pos=wxPoint(6, 86), size=wxSize(360, 20), style=0, value='')
        self.textCtrlUpdateLogFile.SetToolTipString('Specify location for a database updates log file')

        self.buttonBrowseUpdateLog = wxButton(id=wxID_WXPREFERENCESDLGBUTTONBROWSEUPDATELOG,
              label='...', name='buttonBrowseUpdateLog',
              parent=self._panelReports, pos=wxPoint(366, 86), size=wxSize(20,
              20), style=0)
        self.buttonBrowseUpdateLog.SetToolTipString('Click to browse for a log file')
        EVT_BUTTON(self.buttonBrowseUpdateLog,
              wxID_WXPREFERENCESDLGBUTTONBROWSEUPDATELOG,
              self.OnButtonBrowseUpdateLog)

        self.staticLineUpdateTimeCtrl = wxStaticLine(id=wxID_WXPREFERENCESDLGSTATICLINEUPDATETIMECTRL,
              name='staticLineUpdateTimeCtrl', parent=self._panelInternetUpdate,
              pos=wxPoint(277, 66), size=wxSize(74, 22), style=0)
        self.staticLineUpdateTimeCtrl.Show(False)
        self.staticLineUpdateTimeCtrl.SetToolTipString('When the download should be started')

        self.staticTextUpdateDay = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTUPDATEDAY,
              label='&Day Of The Week:', name='staticTextUpdateDay',
              parent=self._panelInternetUpdate, pos=wxPoint(23, 104),
              size=wxSize(96, 18), style=0)
        self.staticTextUpdateDay.SetToolTipString('')

        self._panelScheduler = wxPanel(id=wxID_WXPREFERENCESDLG_PANELSCHEDULER,
              name='_panelScheduler', parent=self.notebook, pos=wxPoint(0, 0),
              size=wxSize(390, 234), style=wxTAB_TRAVERSAL)
        self._panelScheduler.SetToolTipString('')

        self.listViewScheduledTasks = wxListView(id=wxID_WXPREFERENCESDLGLISTVIEWSCHEDULEDTASKS,
              name='listViewScheduledTasks', parent=self._panelScheduler,
              pos=wxPoint(6, 34), size=wxSize(298, 158),
              style=wxLC_REPORT | wxLC_SINGLE_SEL)
        self.listViewScheduledTasks.SetToolTipString('List of Scheduled Scans')
        self.listViewScheduledTasks.SetImageList(self.imageListScheduler,
              wxIMAGE_LIST_NORMAL)
        self.listViewScheduledTasks.SetImageList(self.imageListScheduler,
              wxIMAGE_LIST_SMALL)
        self._init_coll_listViewScheduledTasks_Columns(self.listViewScheduledTasks)
        EVT_LIST_ITEM_SELECTED(self.listViewScheduledTasks,
              wxID_WXPREFERENCESDLGLISTVIEWSCHEDULEDTASKS,
              self.OnScheduledTasksUpdate)
        EVT_LIST_ITEM_DESELECTED(self.listViewScheduledTasks,
              wxID_WXPREFERENCESDLGLISTVIEWSCHEDULEDTASKS,
              self.OnScheduledTasksUpdate)
        EVT_LEFT_DCLICK(self.listViewScheduledTasks,
              self.OnButtonEditScheduledScan)

        self.staticTextScheduledTasks = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTSCHEDULEDTASKS,
              label='Scheduled Scans:', name='staticTextScheduledTasks',
              parent=self._panelScheduler, pos=wxPoint(6, 14), size=wxSize(154,
              16), style=0)
        self.staticTextScheduledTasks.SetToolTipString('')

        self.buttonTaskAdd = wxButton(id=wxID_WXPREFERENCESDLGBUTTONTASKADD,
              label='&Add', name='buttonTaskAdd', parent=self._panelScheduler,
              pos=wxPoint(311, 34), size=wxSize(75, 23), style=0)
        EVT_BUTTON(self.buttonTaskAdd, wxID_WXPREFERENCESDLGBUTTONTASKADD,
              self.OnButtonAddScheduledScan)

        self.buttonTaskRemove = wxButton(id=wxID_WXPREFERENCESDLGBUTTONTASKREMOVE,
              label='&Remove', name='buttonTaskRemove',
              parent=self._panelScheduler, pos=wxPoint(311, 67), size=wxSize(75,
              23), style=0)
        EVT_BUTTON(self.buttonTaskRemove, wxID_WXPREFERENCESDLGBUTTONTASKREMOVE,
              self.OnButtonRemoveScheduledScan)

        self.buttonTaskEdit = wxButton(id=wxID_WXPREFERENCESDLGBUTTONTASKEDIT,
              label='&Edit', name='buttonTaskEdit', parent=self._panelScheduler,
              pos=wxPoint(311, 101), size=wxSize(75, 23), style=0)
        EVT_BUTTON(self.buttonTaskEdit, wxID_WXPREFERENCESDLGBUTTONTASKEDIT,
              self.OnButtonEditScheduledScan)

        self.checkBoxInfectedOnly = wxCheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXINFECTEDONLY,
              label='&Display Infected Files Only', name='checkBoxInfectedOnly',
              parent=self._panelOptions, pos=wxPoint(15, 29), size=wxSize(354,
              18), style=0)
        self.checkBoxInfectedOnly.SetValue(False)
        self.checkBoxInfectedOnly.SetToolTipString('Select if you wish to display infected files only in the scan progress window')

        self.choiceUpdateDay = wxChoice(choices=['Monday', 'Tuesday',
              'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
              id=wxID_WXPREFERENCESDLGCHOICEUPDATEDAY, name='choiceUpdateDay',
              parent=self._panelInternetUpdate, pos=wxPoint(126, 101),
              size=wxSize(110, 21), style=0)
        self.choiceUpdateDay.SetColumns(2)
        self.choiceUpdateDay.SetToolTipString('When update frequency is weekly select day of the week for an update')
        self.choiceUpdateDay.SetStringSelection('Tuesday')

        self.checkBoxUpdateLogon = wxCheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXUPDATELOGON,
              label='&Update Virus Database On Logon',
              name='checkBoxUpdateLogon', parent=self._panelInternetUpdate,
              pos=wxPoint(6, 139), size=wxSize(322, 20), style=0)
        self.checkBoxUpdateLogon.SetToolTipString('Select if you wish to update the virus databases just after you logged on')
        self.checkBoxUpdateLogon.SetValue(False)
        EVT_CHECKBOX(self.checkBoxUpdateLogon,
              wxID_WXPREFERENCESDLGCHECKBOXUPDATELOGON,
              self.OnCheckBoxEnableAutoUpdate)

        self.staticBoxInfected = wxStaticBox(id=wxID_WXPREFERENCESDLGSTATICBOXINFECTED,
              label='Infected Files', name='staticBoxInfected',
              parent=self._panelOptions, pos=wxPoint(6, 101), size=wxSize(376,
              123), style=0)

        self.radioButtonReport = wxRadioButton(id=wxID_WXPREFERENCESDLGRADIOBUTTONREPORT,
              label='&Report Only', name='radioButtonReport',
              parent=self._panelOptions, pos=wxPoint(15, 119), size=wxSize(354,
              18), style=0)
        self.radioButtonReport.SetValue(False)
        EVT_RADIOBUTTON(self.radioButtonReport,
              wxID_WXPREFERENCESDLGRADIOBUTTONREPORT, self.OnRadioInfected)

        self.radioButtonRemoveInfected = wxRadioButton(id=wxID_WXPREFERENCESDLGRADIOBUTTONREMOVEINFECTED,
              label='R&emove (Use Carefully)', name='radioButtonRemoveInfected',
              parent=self._panelOptions, pos=wxPoint(15, 137), size=wxSize(354,
              18), style=0)
        self.radioButtonRemoveInfected.SetValue(False)
        EVT_RADIOBUTTON(self.radioButtonRemoveInfected,
              wxID_WXPREFERENCESDLGRADIOBUTTONREMOVEINFECTED,
              self.OnRadioInfected)

        self.radioButtonQuarantine = wxRadioButton(id=wxID_WXPREFERENCESDLGRADIOBUTTONQUARANTINE,
              label='&Move To Quarantine Folder:', name='radioButtonQuarantine',
              parent=self._panelOptions, pos=wxPoint(15, 156), size=wxSize(354,
              18), style=0)
        self.radioButtonQuarantine.SetValue(False)
        EVT_RADIOBUTTON(self.radioButtonQuarantine,
              wxID_WXPREFERENCESDLGRADIOBUTTONQUARANTINE, self.OnRadioInfected)

        self.textCtrlQuarantine = wxTextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLQUARANTINE,
              name='textCtrlQuarantine', parent=self._panelOptions,
              pos=wxPoint(31, 176), size=wxSize(319, 20), style=0, value='')
        self.textCtrlQuarantine.SetToolTipString('Specify location for a quarantine folder')

        self.buttonBrowseQuarantine = wxButton(id=wxID_WXPREFERENCESDLGBUTTONBROWSEQUARANTINE,
              label='...', name='buttonBrowseQuarantine',
              parent=self._panelOptions, pos=wxPoint(351, 176), size=wxSize(20,
              20), style=0)
        self.buttonBrowseQuarantine.SetToolTipString('Click to browse for a quarantine folder')
        EVT_BUTTON(self.buttonBrowseQuarantine,
              wxID_WXPREFERENCESDLGBUTTONBROWSEQUARANTINE,
              self.OnButtonBrowseQuarantine)

        self._panelEmailAlerts = wxPanel(id=wxID_WXPREFERENCESDLG_PANELEMAILALERTS,
              name='_panelEmailAlerts', parent=self.notebook, pos=wxPoint(0, 0),
              size=wxSize(390, 234), style=wxTAB_TRAVERSAL)
        self._panelEmailAlerts.SetToolTipString('')

        self.checkBoxSMTPEnable = wxCheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXSMTPENABLE,
              label='&Send Email Alert On Virus Detection',
              name='checkBoxSMTPEnable', parent=self._panelEmailAlerts,
              pos=wxPoint(6, 11), size=wxSize(362, 15), style=0)
        self.checkBoxSMTPEnable.SetValue(False)
        self.checkBoxSMTPEnable.SetToolTipString('Select if you wish to receive email alerts when ClamWin detects a virus')
        EVT_CHECKBOX(self.checkBoxSMTPEnable,
              wxID_WXPREFERENCESDLGCHECKBOXSMTPENABLE,
              self.OnCheckBoxSMTPEnable)

        self.staticBoxSMTPConnection = wxStaticBox(id=wxID_WXPREFERENCESDLGSTATICBOXSMTPCONNECTION,
              label='SMTP Connection Details', name='staticBoxSMTPConnection',
              parent=self._panelEmailAlerts, pos=wxPoint(16, 27),
              size=wxSize(368, 71), style=0)
        self.staticBoxSMTPConnection.SetToolTipString('')

        self.staticTextSMTPHost = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTSMTPHOST,
              label='&Mail Server:', name='staticTextSMTPHost',
              parent=self._panelEmailAlerts, pos=wxPoint(24, 49),
              size=wxSize(71, 16), style=0)
        self.staticTextSMTPHost.SetToolTipString('')

        self.textCtrlSMTPHost = wxTextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLSMTPHOST,
              name='textCtrlSMTPHost', parent=self._panelEmailAlerts,
              pos=wxPoint(104, 46), size=wxSize(192, 21), style=0, value='')
        self.textCtrlSMTPHost.SetToolTipString('SMTP Server domain name or IP address')

        self.staticTextSMTPPort = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTSMTPPORT,
              label='P&ort:', name='staticTextSMTPPort',
              parent=self._panelEmailAlerts, pos=wxPoint(300, 49),
              size=wxSize(31, 16), style=0)

        self.intCtrlSMTPPort = wxIntCtrl(allow_long=False, allow_none=False,
              default_color=wxBLACK, id=wxID_WXPREFERENCESDLGINTCTRLSMTPPORT,
              limited=False, max=65535, min=0, name='intCtrlSMTPPort',
              oob_color=wxRED, parent=self._panelEmailAlerts, pos=wxPoint(330,
              46), size=wxSize(47, 21), style=0, value=25)
        self.intCtrlSMTPPort.SetBounds((0, 65535))
        self.intCtrlSMTPPort.SetToolTipString('Mail Server port number (0-65535)')

        self.staticTextSMTPUserName = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTSMTPUSERNAME,
              label='&User Name:', name='staticTextSMTPUserName',
              parent=self._panelEmailAlerts, pos=wxPoint(24, 72),
              size=wxSize(79, 16), style=0)
        self.staticTextSMTPUserName.SetToolTipString('')

        self.textCtrlSMTPUser = wxTextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLSMTPUSER,
              name='textCtrlSMTPUser', parent=self._panelEmailAlerts,
              pos=wxPoint(104, 69), size=wxSize(101, 21), style=0, value='')
        self.textCtrlSMTPUser.SetToolTipString('Mail Server Account Name (optional)')

        self.staticTextSMTPPassword = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTSMTPPASSWORD,
              label='&Password:', name='staticTextSMTPPassword',
              parent=self._panelEmailAlerts, pos=wxPoint(209, 72),
              size=wxSize(66, 16), style=0)
        self.staticTextSMTPPassword.SetToolTipString('')

        self.textCtrlSMTPPassword = wxTextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLSMTPPASSWORD,
              name='textCtrlSMTPPassword', parent=self._panelEmailAlerts,
              pos=wxPoint(276, 69), size=wxSize(101, 21), style=wxTE_PASSWORD,
              value='')
        self.textCtrlSMTPPassword.SetToolTipString('Mail Server account password (optional)')

        self.staticBoxEmailDetails = wxStaticBox(id=wxID_WXPREFERENCESDLGSTATICBOXEMAILDETAILS,
              label='Email Message Details', name='staticBoxEmailDetails',
              parent=self._panelEmailAlerts, pos=wxPoint(16, 102),
              size=wxSize(368, 95), style=0)
        self.staticBoxEmailDetails.SetToolTipString('')

        self.staticTextSMTPFrom = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTSMTPFROM,
              label='&From:', name='staticTextSMTPFrom',
              parent=self._panelEmailAlerts, pos=wxPoint(24, 124),
              size=wxSize(63, 16), style=0)
        self.staticTextSMTPFrom.SetToolTipString('')

        self.textCtrlSMTPFrom = wxTextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLSMTPFROM,
              name='textCtrlSMTPFrom', parent=self._panelEmailAlerts,
              pos=wxPoint(104, 118), size=wxSize(273, 21), style=0, value='')
        self.textCtrlSMTPFrom.SetToolTipString('Specify an email address from which the notification will be sent.')

        self.staticTextSMTPTo = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTSMTPTO,
              label='&To:', name='staticTextSMTPTo',
              parent=self._panelEmailAlerts, pos=wxPoint(24, 148),
              size=wxSize(63, 16), style=0)
        self.staticTextSMTPTo.SetToolTipString('')

        self.textCtrlSMTPTo = wxTextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLSMTPTO,
              name='textCtrlSMTPTo', parent=self._panelEmailAlerts,
              pos=wxPoint(104, 143), size=wxSize(273, 21), style=0, value='')
        self.textCtrlSMTPTo.SetToolTipString('Specify an email address where the email alert will be delivered.  Separate multiple addresses with commas.')

        self.staticTextSMTPSubject = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTSMTPSUBJECT,
              label='Su&bject:', name='staticTextSMTPSubject',
              parent=self._panelEmailAlerts, pos=wxPoint(24, 171),
              size=wxSize(63, 16), style=0)
        self.staticTextSMTPSubject.SetToolTipString('')

        self.textCtrlSMTPSubject = wxTextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLSMTPSUBJECT,
              name='textCtrlSMTPSubject', parent=self._panelEmailAlerts,
              pos=wxPoint(104, 167), size=wxSize(273, 21), style=0, value='')
        self.textCtrlSMTPSubject.SetToolTipString("Specify Recipient's email address where the email alert will be delivered")

        self.buttonSendTestEmail = wxButton(id=wxID_WXPREFERENCESDLGBUTTONSENDTESTEMAIL,
              label='Send &Test Email', name='buttonSendTestEmail',
              parent=self._panelEmailAlerts, pos=wxPoint(120, 205),
              size=wxSize(149, 23), style=0)
        self.buttonSendTestEmail.SetToolTipString('Click to send a test email message')
        EVT_BUTTON(self.buttonSendTestEmail,
              wxID_WXPREFERENCESDLGBUTTONSENDTESTEMAIL,
              self.OnButtonSendTestEmail)

        self.checkBoxTrayNotify = wxCheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXTRAYNOTIFY,
              label='&Display Pop-up Notification Messages In Taskbar ',
              name='checkBoxTrayNotify', parent=self._panelReports,
              pos=wxPoint(6, 123), size=wxSize(354, 18), style=0)
        self.checkBoxTrayNotify.SetValue(False)
        self.checkBoxTrayNotify.SetToolTipString('Select if you wish to receive Tray notification pop-up messages')

        self._panelFilters = wxPanel(id=wxID_WXPREFERENCESDLG_PANELFILTERS,
              name='_panelFilters', parent=self.notebook, pos=wxPoint(0, 0),
              size=wxSize(390, 234), style=wxTAB_TRAVERSAL)

        self.staticTextFiltreDesc1 = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTFILTREDESC1,
              label='Specify Filename Patterns to include and/or exclude in scanning',
              name='staticTextFiltreDesc1', parent=self._panelFilters,
              pos=wxPoint(6, 11), size=wxSize(383, 16), style=0)

        self.staticText2 = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXT2,
              label='(To specify a regular expression include your pattern within <...>)',
              name='staticText2', parent=self._panelFilters, pos=wxPoint(6, 28),
              size=wxSize(382, 16), style=0)

        self.staticTextFiltersExclude = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTFILTERSEXCLUDE,
              label='&Exclude Matching Filenames:',
              name='staticTextFiltersExclude', parent=self._panelFilters,
              pos=wxPoint(6, 50), size=wxSize(184, 16), style=0)

        self.editableListBoxFiltersExclude = wxEditableListBox(id=wxID_WXPREFERENCESDLGEDITABLELISTBOXFILTERSEXCLUDE,
              label='Patterns', name='editableListBoxFiltersExclude',
              parent=self._panelFilters, pos=wxPoint(6, 69), size=wxSize(182,
              151))

        self.staticTextFiltersInclude = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTFILTERSINCLUDE,
              label='&Scan Only Matching Filenames:',
              name='staticTextFiltersInclude', parent=self._panelFilters,
              pos=wxPoint(202, 51), size=wxSize(187, 16), style=0)

        self.editableListBoxFiltersInclude = wxEditableListBox(id=wxID_WXPREFERENCESDLGEDITABLELISTBOXFILTERSINCLUDE,
              label='Patterns', name='editableListBoxFiltersInclude',
              parent=self._panelFilters, pos=wxPoint(200, 69), size=wxSize(184,
              151))

        self.buttonTaskDeactivate = wxButton(id=wxID_WXPREFERENCESDLGBUTTONTASKDEACTIVATE,
              label='&Deactivate', name='buttonTaskDeactivate',
              parent=self._panelScheduler, pos=wxPoint(311, 169),
              size=wxSize(75, 23), style=0)
        EVT_BUTTON(self.buttonTaskDeactivate,
              wxID_WXPREFERENCESDLGBUTTONTASKDEACTIVATE,
              self.OnButtonTaskDeactivate)

        self.buttonTaskActivate = wxButton(id=wxID_WXPREFERENCESDLGBUTTONTASKACTIVATE,
              label='A&ctivate', name='buttonTaskActivate',
              parent=self._panelScheduler, pos=wxPoint(311, 135),
              size=wxSize(75, 23), style=0)
        EVT_BUTTON(self.buttonTaskActivate,
              wxID_WXPREFERENCESDLGBUTTONTASKACTIVATE,
              self.OnButtonTaskActivate)

        self.checkBoxCheckVersion = wxCheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXCHECKVERSION,
              label='&Notify About New ClamWin Releases',
              name='checkBoxCheckVersion', parent=self._panelInternetUpdate,
              pos=wxPoint(6, 172), size=wxSize(322, 20), style=0)
        self.checkBoxCheckVersion.SetToolTipString('Select if you wish to get a notification message when ClamWin Free Antivirus program has been updated')
        self.checkBoxCheckVersion.SetValue(False)
        EVT_CHECKBOX(self.checkBoxCheckVersion,
              wxID_WXPREFERENCESDLGCHECKBOXCHECKVERSION,
              self.OnCheckBoxCheckVersionCheckbox)

        self.staticTextNoPersonal = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTNOPERSONAL,
              label='(No personal information is transmitted during this check)',
              name='staticTextNoPersonal', parent=self._panelInternetUpdate,
              pos=wxPoint(27, 193), size=wxSize(265, 13), style=0)

        self.staticTextMB2 = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTMB2,
              label='MegaBytes', name='staticTextMB2',
              parent=self._panelAdvanced, pos=wxPoint(144, 156), size=wxSize(74,
              16), style=0)

        self.staticTextPriority = wxStaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTPRIORITY,
              label='Scanner &Priority:', name='staticTextPriority',
              parent=self._panelAdvanced, pos=wxPoint(252, 136),
              size=wxSize(103, 17), style=0)

        self.choicePriority = wxChoice(choices=['Low', 'Normal'],
              id=wxID_WXPREFERENCESDLGCHOICEPRIORITY, name='choicePriority',
              parent=self._panelAdvanced, pos=wxPoint(252, 155),
              size=wxSize(134, 21), style=0)
        self.choicePriority.SetToolTipString('Specify the process priority for the virus scanner.')
        self.choicePriority.SetStringSelection('Normal')
        self.choicePriority.SetLabel('')

        self.checkBoxShowProgress = wxCheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXSHOWPROGRESS,
              label='Display &File Scanned % Progress Indicator',
              name='checkBoxShowProgress', parent=self._panelOptions,
              pos=wxPoint(15, 73), size=wxSize(354, 17), style=0)
        self.checkBoxShowProgress.SetValue(False)
        self.checkBoxShowProgress.SetToolTipString('Select if you wish to display infected files only in the scan progress window')

        self.checkBoxUnload = wxCheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXUNLOAD,
              label='&Unload Infected Programs from Computer Memory',
              name='checkBoxUnload', parent=self._panelOptions, pos=wxPoint(15,
              202), size=wxSize(354, 17), style=0)
        self.checkBoxUnload.SetValue(False)
        self.checkBoxUnload.SetToolTipString('Select if you wish to unload infected programs from computer memory so they can be quarantined or removed')

        self.staticBoxOutlookAddin = wxStaticBox(id=wxID_WXPREFERENCESDLGSTATICBOXOUTLOOKADDIN,
              label='Microsoft Outlook', name='staticBoxOutlookAddin',
              parent=self._panelEmailScanning, pos=wxPoint(6, 11),
              size=wxSize(376, 77), style=0)

        self.checkBoxOutlookScanIncoming = wxCheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXOUTLOOKSCANINCOMING,
              label='&Scan &Incoming Email Messages',
              name='checkBoxOutlookScanIncoming',
              parent=self._panelEmailScanning, pos=wxPoint(15, 32),
              size=wxSize(354, 18), style=0)
        self.checkBoxOutlookScanIncoming.SetValue(False)
        self.checkBoxOutlookScanIncoming.SetToolTipString('Select if you wish to enable scanning of incoming email messages in MS Outlook')
        EVT_CHECKBOX(self.checkBoxOutlookScanIncoming,
              wxID_WXPREFERENCESDLGCHECKBOXOUTLOOKSCANINCOMING,
              self.OnCheckBoxOutlookAddinEnabledCheckbox)

        self.checkBoxOutlookScanOutgoing = wxCheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXOUTLOOKSCANOUTGOING,
              label='&Scan &Outgoing Email Messages',
              name='checkBoxOutlookScanOutgoing',
              parent=self._panelEmailScanning, pos=wxPoint(15, 57),
              size=wxSize(354, 18), style=0)
        self.checkBoxOutlookScanOutgoing.SetValue(False)
        self.checkBoxOutlookScanOutgoing.SetToolTipString('Select if you wish to enable scanning of outgoing email messages in MS Outlook')
        EVT_CHECKBOX(self.checkBoxOutlookScanOutgoing,
              wxID_WXPREFERENCESDLGCHECKBOXOUTLOOKSCANOUTGOING,
              self.OnCheckBoxOutlookScanOutgoingCheckbox)

        self._init_coll_notebook_Pages(self.notebook)

    def __init__(self, parent, config, switchToSchedule):
        self._config = None
        self._config = config
        if sys.platform.startswith("win"):
            self._scheduledScans = wxDialogScheduledScan.LoadPersistentScheduledScans(
                os.path.join(Utils.GetScheduleShelvePath(self._config), 'ScheduledScans'))
        self._init_ctrls(parent)

        # set window icons
        icons = wxIconBundle()
        icons.AddIconFromFile('img/FrameIcon.ico', wxBITMAP_TYPE_ICO)
        self.SetIcons(icons)

        # wxWidgets notebook bug workaround
        # http://sourceforge.net/tracker/index.php?func=detail&aid=645323&group_id=9863&atid=109863
        s = self.notebook.GetSize();
        self.notebook.SetSize(wxSize(s.GetWidth() - 1, s.GetHeight()));
        self.notebook.SetSize(s);


        init_pages = [self._OptionsPageInit, self._FiltersPageInit, self._ScheduledScanPageInit,
                        self._InternetUpdatePageInit, self._EmailAlertsPageInit,
                        self._ProxyPageInit,
                        self._FilesPageInit, self._ArchivesPageInit,
                        self._ReportsPageInit,
                        self._EmailScanningPageInit,
                        self._AdvancedPageInit]
        # added check for self._config.Get('UI', 'Standalone')
        # to enable running the scanner only with no scheduler
        # needed in clamwin plugin to BartPE <http://oss.netfarm.it/winpe/>
        if self._config.Get('UI', 'Standalone') == '1':
            init_pages.remove(self._EmailScanningPageInit)
            init_pages.remove(self._InternetUpdatePageInit)
            init_pages.remove(self._ScheduledScanPageInit)                        
            self.notebook.RemovePage(9)
            self.notebook.RemovePage(4)
            self.notebook.RemovePage(2)
        else:            
            # remove "Email Scanning page if there is no MS Outlook
            if not Utils.IsOutlookInstalled():
                self.notebook.RemovePage(9)


        for init_page in init_pages:
            init_page()

        for i in range(0, self.notebook.GetPageCount()):
            self.notebook.GetPage(i).TransferDataToWindow()

        self.UpdateScheduledTasksButtons()

        if switchToSchedule:
            self.notebook.SetSelection(4)


    def OnCancel(self, event):
        self.EndModal(wxID_CANCEL)

    def OnOK(self, event):
        if self._Apply():
            self.EndModal(wxID_OK)


    def _Apply(self):
            pages = range(0, self.notebook.GetPageCount())
            # rearrange pages in order to validate the current one first
            for page in pages:
                if self.notebook.GetSelection() == page:
                    tmp = pages[0]
                    pages[0] = pages[page]
                    pages[page] = tmp

            # validate and apply each page
            for page in pages:
                if not self.notebook.GetPage(page).Validate():
                    # activate the invalid page
                    self.notebook.SetSelection(page)
                    return False
                self.notebook.GetPage(page).TransferDataFromWindow()
            
            # save config to properties file
            if not self._config.Write():
                MsgBox.ErrorBox(self, 'An error occured whilst saving configuration file %s. Please check that you have write permsiison to the configuratuion file.' % self._config.GetFilename())
                return False

            # raise the event so other programs can reload config
            if sys.platform.startswith("win"):
                # Save scheduled scans separately
                wxDialogScheduledScan.SavePersistentScheduledScans(
                    os.path.join(Utils.GetScheduleShelvePath(self._config), 'ScheduledScans'),
                    self._scheduledScans)

                import win32event, win32api
                hEvent = None
                try:
                    hEvent = win32event.CreateEvent(None, True, False, Utils.CONFIG_EVENT);
                    win32event.PulseEvent(hEvent)
                    win32api.CloseHandle(hEvent)
                except win32api.error, e:
                    if hEvent is not None:
                        win32api.CloseHandle(hEvent)
                    print "Event Failed", str(e)
            return True



    def _EnableOptionsControls(self, init):
        if init:
            self._config.Get('ClamAV', 'RemoveInfected') == '1'
            enable = self._config.Get('ClamAV', 'MoveInfected') == '1' and \
                        len(self._config.Get('ClamAV', 'QuarantineDir'))
        else:
            enable = self.radioButtonQuarantine.GetValue()

        self.textCtrlQuarantine.Enable(enable)
        self.buttonBrowseQuarantine.Enable(enable)


    def _OptionsPageInit(self):
        self.choicePriority.SetValidator(MyValidator(config=self._config, section='ClamAV', value='Priority'))
        self.checkBoxInfectedOnly.SetValidator(MyValidator(config=self._config, section='ClamAV', value='InfectedOnly'))
        self.checkBoxShowProgress.SetValidator(MyValidator(config=self._config, section='ClamAV', value='ShowProgress'))
        self.checkBoxScanRecursive.SetValidator(MyValidator(config=self._config, section='ClamAV', value='ScanRecursive'))
        self.radioButtonReport.SetValidator(MyValidator(config=self._config, section='UI', value='ReportInfected'))
        self.radioButtonRemoveInfected.SetValidator(MyValidator(config=self._config, section='ClamAV', value='RemoveInfected'))
        self.radioButtonQuarantine.SetValidator(MyValidator(config=self._config, section='ClamAV', value='MoveInfected'))
        self.textCtrlQuarantine.SetValidator(MyValidator(config=self._config, section='ClamAV', value='QuarantineDir', canEmpty = False))
        self.checkBoxUnload.SetValidator(MyValidator(config=self._config, section='ClamAV', value='Kill'))
        self._EnableOptionsControls(True)

    def _FiltersPageInit(self):
        self.editableListBoxFiltersInclude.SetValidator(MyPatternValidator(config=self._config, section='ClamAV', value='IncludePatterns'))
        self.editableListBoxFiltersExclude.SetValidator(MyPatternValidator(config=self._config, section='ClamAV', value='ExcludePatterns'))
        if sys.platform.startswith('win'):
            EVT_CHAR(self.editableListBoxFiltersInclude.GetListCtrl(),
                  self.OnEditableListBoxChar)
            EVT_CHAR(self.editableListBoxFiltersExclude.GetListCtrl(),
                  self.OnEditableListBoxChar)

    def _EnableInternetUpdateControls(self, init):
        if sys.platform.startswith("win"):
            if init:
                enable = self._config.Get('Updates', 'Enable') == '1'
                enableDay = enable and self._config.Get('Updates', 'Frequency') == 'Weekly'
            else:
                enable = self.checkBoxEnableAutoUpdate.IsChecked()
                enableDay = enable and self.choiceUpdateFrequency.GetStringSelection() == 'Weekly'
            self.textCtrlDBMirror.Enable(enable)
            self.choiceUpdateDay.Enable(enableDay)
            self.choiceUpdateFrequency.Enable(enable)
            self.timeUpdate.Enable(enable)
            self.spinButtonUpdateTime.Enable(enable)

    def _InternetUpdatePageInit(self):
        locale.setlocale(locale.LC_ALL, 'C')
        self.timeUpdate = wxTimeCtrl(parent=self._panelInternetUpdate,
         pos=self.staticLineUpdateTimeCtrl.GetPosition(),
         size=self.staticLineUpdateTimeCtrl.GetSize(),  fmt24hr=Utils.IsTime24(),
         spinButton=self.spinButtonUpdateTime,
         useFixedWidthFont=False, display_seconds=True)
        self.timeUpdate.SetToolTipString(self.staticLineUpdateTimeCtrl.GetToolTip().GetTip())
        #self.timeUpdate.BindSpinButton(self.spinButtonUpdateTime)
        self.textCtrlDBMirror.SetValidator(MyValidator(config=self._config, section='Updates', value='DBMirror', canEmpty=False))
        self.checkBoxEnableAutoUpdate.SetValidator(MyValidator(config=self._config, section='Updates', value='Enable'))
        self.checkBoxCheckVersion.SetValidator(MyValidator(config=self._config, section='Updates', value='CheckVersion'))
        self.choiceUpdateFrequency.SetValidator(MyValidator(config=self._config, section='Updates', value='Frequency'))
        self.timeUpdate.SetValidator(MyValidator(config=self._config, section='Updates', value='Time'))
        if sys.platform.startswith('win'):
            self.checkBoxUpdateLogon.SetValidator(MyValidator(config=self._config, section='Updates', value='UpdateOnLogon'))
        else:
            self.checkBoxUpdateLogon.Hide()
        self.choiceUpdateDay.SetValidator(MyWeekDayValidator(config=self._config, section='Updates', value='WeekDay'))
        self._EnableInternetUpdateControls(True)

    def _ProxyPageInit(self):
        self.textCtrlProxyHost.SetValidator(MyValidator(config=self._config, section='Proxy', value='Host'))
        self.intCtrlProxyPort.SetValidator(MyValidator(config=self._config, section='Proxy', value='Port'))
        self.textCtrlProxyUser.SetValidator(MyValidator(config=self._config, section='Proxy', value='User'))
        self.textCtrlProxyPassword.SetValidator(MyValidator(config=self._config, section='Proxy', value='Password'))

    def _ScheduledScanPageInit(self):
        # adjust column witdh in the listview
        col_count = self.listViewScheduledTasks.GetColumnCount()
        col_size = self.listViewScheduledTasks.GetSize()[0]/col_count-1
        self.listViewScheduledTasks.SetColumnWidth(0, col_size + 30)
        self.listViewScheduledTasks.SetColumnWidth(1, col_size + 5)
        self.listViewScheduledTasks.SetColumnWidth(2, col_size - 35)
        for sc in self._scheduledScans:
           self._ListAddScheduledScan(sc)

    def _EnableEmailAlertsControls(self, init):
        if init:
            enable = self._config.Get('EmailAlerts', 'Enable') == '1'
        else:
            enable = self.checkBoxSMTPEnable.IsChecked()
        self.textCtrlSMTPHost.Enable(enable)
        self.intCtrlSMTPPort.Enable(enable)
        self.textCtrlSMTPUser.Enable(enable)
        self.textCtrlSMTPPassword.Enable(enable)
        self.textCtrlSMTPFrom.Enable(enable)
        self.textCtrlSMTPTo.Enable(enable)
        self.textCtrlSMTPSubject.Enable(enable)
        self.buttonSendTestEmail.Enable(enable)

    def _EmailAlertsPageInit(self):
        self.checkBoxSMTPEnable.SetValidator(MyValidator(config=self._config, section='EmailAlerts', value='Enable'))
        self.textCtrlSMTPHost.SetValidator(MyValidator(config=self._config, section='EmailAlerts', value='SMTPHost', canEmpty=False))
        self.intCtrlSMTPPort.SetValidator(MyValidator(config=self._config, section='EmailAlerts', value='SMTPPort', canEmpty=False))
        self.textCtrlSMTPUser.SetValidator(MyValidator(config=self._config, section='EmailAlerts', value='SMTPUser'))
        self.textCtrlSMTPPassword.SetValidator(MyValidator(config=self._config, section='EmailAlerts', value='SMTPPassword'))
        self.textCtrlSMTPFrom.SetValidator(MyValidator(config=self._config, section='EmailAlerts', value='From'))
        self.textCtrlSMTPTo.SetValidator(MyValidator(config=self._config, section='EmailAlerts', value='To', canEmpty=False))
        self.textCtrlSMTPSubject.SetValidator(MyValidator(config=self._config, section='EmailAlerts', value='Subject'))
        self._EnableEmailAlertsControls(True)

    def _FilesPageInit(self):
        self.textCtrlClamScan.SetValidator(MyValidator(config=self._config, section='ClamAV', value='ClamScan', canEmpty=False))
        self.textCtrlFreshClam.SetValidator(MyValidator(self._config, section='ClamAV', value='FreshClam', canEmpty=False))
        self.textCtrlVirDB.SetValidator(MyValidator(self._config, section='ClamAV', value='Database', canEmpty=False))

    def _EnableArchivesControls(self, init):
        if init:
            enable = self._config.Get('ClamAV', 'ScanArchives') == '1'
        else:
            enable = self.checkBoxScanArchives.IsChecked()
        self.spinCtrlArchiveFiles.Enable(enable)
        self.spinCtrlArchiveSize.Enable(enable)
        self.spinCtrlRecursion.Enable(enable)

    def _ArchivesPageInit(self):
        self.checkBoxScanArchives.SetValidator(MyValidator(config=self._config, section='ClamAV', value='ScanArchives'))
        self.spinCtrlArchiveSize.SetValidator(MyValidator(self._config, section='ClamAV', value='MaxSize', canEmpty=False))
        self.spinCtrlArchiveFiles.SetValidator(MyValidator(self._config, section='ClamAV', value='MaxFiles', canEmpty=False))
        self.spinCtrlRecursion.SetValidator(MyValidator(self._config, section='ClamAV', value='MaxRecursion', canEmpty=False))
        self._EnableArchivesControls(True)

    def _ReportsPageInit(self):
        self.textCtrlScanLogFile.SetValidator(MyValidator(config=self._config, section='ClamAV', value='LogFile', canEmpty=False))
        self.textCtrlUpdateLogFile.SetValidator(MyValidator(config=self._config, section='Updates', value='DBUpdateLogFile', canEmpty=False))
        if sys.platform.startswith('win') and self._config.Get('UI', 'Standalone') != '1':
            self.checkBoxTrayNotify.SetValidator(MyValidator(config=self._config, section='UI', value='TrayNotify'))
        else:
            self.checkBoxTrayNotify.Hide()

    def _EmailScanningPageInit(self):
        self.checkBoxOutlookScanIncoming.SetValidator(MyValidator(config=self._config, section='EmailScan', value='ScanIncoming'));
        self.checkBoxOutlookScanOutgoing.SetValidator(MyValidator(config=self._config, section='EmailScan', value='ScanOutgoing'));
        
    def _AdvancedPageInit(self):
        self.choicePriority.SetValidator(MyValidator(config=self._config, section='ClamAV', value='Priority'))
        self.spinCtrlMaxLogSize.SetValidator(MyValidator(self._config, section='ClamAV', value='MaxLogSize', canEmpty=False))
        self.checkBoxEnableMbox.SetValidator(MyValidator(config=self._config, section='ClamAV', value='EnableMbox'))
        self.checkBoxEnableOLE2.SetValidator(MyValidator(config=self._config, section='ClamAV', value='ScanOle2'))
        self.checkBoxScanExeOnly.SetValidator(MyValidator(config=self._config, section='ClamAV', value='ScanExeOnly'))
        self.textCtrlAdditionalParams.SetValidator(MyValidator(config=self._config, section='ClamAV', value='ClamScanParams', canEmpty=True))

    def _ListAddScheduledScan(self, sc, pos = -1):
        if pos == -1:
            pos = self.listViewScheduledTasks.GetItemCount()
        self.listViewScheduledTasks.InsertImageStringItem(pos, sc.Description, 0)
        self.listViewScheduledTasks.SetStringItem(pos, 1, sc.Path)
        self.listViewScheduledTasks.SetStringItem(pos, 2, sc.Frequency)
        item = self.listViewScheduledTasks.GetItem(pos)
        if sc.Active:
            item.SetTextColour(wxNullColour)
        else:
            item.SetTextColour(wxLIGHT_GREY)
        self.listViewScheduledTasks.SetItem(item)

    def OnCharHook(self, event):
        if event.GetKeyCode() == WXK_ESCAPE:
            self.EndModal(wxID_CANCEL)
        else:
            event.Skip()

    def OnButtonBrowseFreshClam(self, event):
        if sys.platform.startswith("win"):
            filename = 'freshclam.exe'
            mask = "Executable files (*.exe)|*.exe|All files (*.*)|*.*"
        else:
            filename = 'freshclam'
            mask = "All files (*)|*"
        dlg = wxFileDialog(self, "Choose a file", ".", filename, mask, wxOPEN)
        try:
            if dlg.ShowModal() == wxID_OK:
                filename = dlg.GetPath()
            self.textCtrlFreshClam.Clear()
            self.textCtrlFreshClam.WriteText(filename)
        finally:
            dlg.Destroy()

    def OnButtonBrowseClamScan(self, event):
        if sys.platform.startswith("win"):
            filename = 'clamscan.exe'
            mask = "Executable files (*.exe)|*.exe|All files (*.*)|*.*"
        else:
            filename = 'clamscan'
            mask = "All files (*)|*"
        dlg = wxFileDialog(self, "Choose a file", ".", filename, mask, wxOPEN)
        try:
            if dlg.ShowModal() == wxID_OK:
                filename = dlg.GetPath()
                self.textCtrlClamScan.Clear()
                self.textCtrlClamScan.WriteText(filename)
        finally:
            dlg.Destroy()

    def OnButtonBrowseVirDB(self, event):
        dlg = wxDirDialog(self)
        try:
            if dlg.ShowModal() == wxID_OK:
                dir = dlg.GetPath()
                self.textCtrlVirDB.Clear()
                self.textCtrlVirDB.WriteText(dir)
        finally:
            dlg.Destroy()

    def OnButtonBrowseScanLog(self, event):
        if sys.platform.startswith("win"):
            filename = 'ClamScanLog.txt'
            mask = "Text Files (*.txt)|*.txt|All files (*.*)|*.*"
        else:
            filename = 'ClamScanLog'
            mask = "All files (*)|*"
        dlg = wxFileDialog(self, "Choose a file", ".", filename, mask, wxSAVE)
        try:
            if dlg.ShowModal() == wxID_OK:
                filename = dlg.GetPath()
                self.textCtrlScanLogFile.Clear()
                self.textCtrlScanLogFile.WriteText(filename)
        finally:
            dlg.Destroy()

    def OnButtonBrowseUpdateLog(self, event):
        if sys.platform.startswith("win"):
            filename = 'ClamUpdateLog.txt'
            mask = "Text Files (*.txt)|*.txt|All files (*.*)|*.*"
        else:
            filename = 'ClamUpdateLog'
            mask = "All files (*)|*"
        dlg = wxFileDialog(self, "Choose a file", ".", filename, mask, wxSAVE)
        try:
            if dlg.ShowModal() == wxID_OK:
                filename = dlg.GetPath()
                self.textCtrlUpdateLogFile.Clear()
                self.textCtrlUpdateLogFile.WriteText(filename)
        finally:
            dlg.Destroy()

    def OnChoiceUpdateFrequency(self, event):
        self._EnableInternetUpdateControls(False)
        event.Skip()

    def OnCheckBoxEnableAutoUpdate(self, event):
        self._EnableInternetUpdateControls(False)
        event.Skip()


    def OnCheckBoxScanArchives(self, event):
        self._EnableArchivesControls(False)
        event.Skip()

    def OnButtonAddScheduledScan(self, event):
        if self.listViewScheduledTasks.GetItemCount() > 20:
            MsgBox.ErrorBox(self, 'Maximum amount of schdeuled items (20) has been reached.')
            return
        sc = wxDialogScheduledScan.ScheduledScanInfo()
        sc = wxDialogScheduledScan.ScheduledScanInfo()
        dlg = wxDialogScheduledScan.wxDialogScheduledScan(self, sc)
        try:
            if dlg.ShowModal() == wxID_OK:
               self._scheduledScans.append(sc)
               self._ListAddScheduledScan(sc)
               id = self.listViewScheduledTasks.GetItemCount() - 1
               self.listViewScheduledTasks.Select(id)
        finally:
            dlg.Destroy()

    def OnButtonRemoveScheduledScan(self, event):
        id = self.listViewScheduledTasks.GetFirstSelected()
        if id != -1:
            del self._scheduledScans[id]
            self.listViewScheduledTasks.DeleteItem(id)
            if self.listViewScheduledTasks.GetItemCount():
                if id > 0:
                    id -= 1
                self.listViewScheduledTasks.Select(id)

    def OnButtonEditScheduledScan(self, event):
        id = self.listViewScheduledTasks.GetFirstSelected()
        if id != -1:
            sc = self._scheduledScans[id]
            dlg = wxDialogScheduledScan.wxDialogScheduledScan(self, sc)
            try:
                if dlg.ShowModal() == wxID_OK:
                    self.listViewScheduledTasks.DeleteItem(id)
                    self._ListAddScheduledScan(sc, id)
                    item = self.listViewScheduledTasks.GetItem(id)
                    if sc.Active:
                        item.SetTextColour(wxNullColour)
                    else:
                        item.SetTextColour(wxLIGHT_GREY)
                    self.listViewScheduledTasks.SetItem(item)
                    self.listViewScheduledTasks.Select(id)
                    self._scheduledScans[id] = sc
            finally:
                dlg.Destroy()

    def UpdateScheduledTasksButtons(self):
        selected = self.listViewScheduledTasks.GetFirstSelected()
        enabled = (selected != -1)
        self.buttonTaskEdit.Enable(enabled)
        self.buttonTaskRemove.Enable(enabled)
        if selected != -1:
            sc = self._scheduledScans[selected]
            self.buttonTaskActivate.Enable(not sc.Active)
            self.buttonTaskDeactivate.Enable(sc.Active)
        else:
            self.buttonTaskActivate.Enable(False)
            self.buttonTaskDeactivate.Enable(False)

    def OnScheduledTasksUpdate(self, event):
        self.UpdateScheduledTasksButtons()
        event.Skip()

    def OnRadioInfected(self, event):
        self._EnableOptionsControls(False)

    def OnButtonBrowseQuarantine(self, event):
        dlg = wxDirDialog(self)
        try:
            if dlg.ShowModal() == wxID_OK:
                dir = dlg.GetPath()
                self.textCtrlQuarantine.Clear()
                self.textCtrlQuarantine.WriteText(dir)
        finally:
            dlg.Destroy()


    def OnCheckBoxSMTPEnable(self, event):
        self._EnableEmailAlertsControls(False)

    def OnButtonSendTestEmail(self, event):
        self.SetCursor(wxStockCursor(wxCURSOR_WAIT))
        try:
            msg = EmailAlert.VirusAlertMsg(self.textCtrlSMTPFrom.GetValue(),
                            self.textCtrlSMTPTo.GetValue(),
                            self.textCtrlSMTPSubject.GetValue() + ' (Testing)',
                            self.textCtrlSMTPHost.GetValue(),
                            self.intCtrlSMTPPort.GetValue(),
                            self.textCtrlSMTPUser.GetValue(),
                            self.textCtrlSMTPPassword.GetValue(),
                            Body='This is a test message sent during configuration of ClamWin Free Antivirus on the following computer: %s.\n'\
                                'Please do not be alarmed.\n' % Utils.GetHostName())
            status, msg = msg.Send(True)
            if not status:
                raise Exception(msg)
            MsgBox.InfoBox(self, 'Test Email has been sent successfully.')
        except Exception, e:
            MsgBox.ErrorBox(self, 'Could not send the email. Please ensure you are connected to the internet. Error: %s' % str(e))
        self.SetCursor(wxNullCursor)

    def OnEditableListBoxChar(self, event):
        # bind F2 key to edit label function
        if event.GetKeyCode() == WXK_F2:
            listCtrl = event.GetEventObject()
            selected = listCtrl.GetNextItem(-1, wxLIST_NEXT_ALL, wxLIST_STATE_SELECTED)
            if selected != -1:
                listCtrl.EditLabel(selected)
        else:
            event.Skip()

    def OnButtonTaskActivate(self, event):
        selected = self.listViewScheduledTasks.GetFirstSelected()
        if selected != -1:
            self._scheduledScans[selected].Active = True
        item = self.listViewScheduledTasks.GetItem(selected)
        item.SetTextColour(wxNullColour)
        self.listViewScheduledTasks.SetItem(item)
        self.UpdateScheduledTasksButtons()

    def OnButtonTaskDeactivate(self, event):
        selected = self.listViewScheduledTasks.GetFirstSelected()
        if selected != -1:
            self._scheduledScans[selected].Active = False
        item = self.listViewScheduledTasks.GetItem(selected)
        item.SetTextColour(wxLIGHT_GREY)
        self.listViewScheduledTasks.SetItem(item)
        self.UpdateScheduledTasksButtons()

    def OnCheckBoxCheckVersionCheckbox(self, event):
        event.Skip()

    def OnCheckBoxOutlookAddinEnabledCheckbox(self, event):
        event.Skip()

    def OnCheckBoxOutlookScanOutgoingCheckbox(self, event):
        event.Skip()

class MyBaseValidator(wxPyValidator):
     def __init__(self, config, section, value, canEmpty=True):
         wxPyValidator.__init__(self)
         self._config = config
         self._section = section
         self._value = value
         self._canEmpty = canEmpty

     def Clone(self):
         return self.__class__(self._config, self._section, self._value, self._canEmpty)

     def Validate(self, win):
         return True
        
class MyWeekDayValidator(MyBaseValidator):
     def TransferToWindow(self):
         value = self._config.Get(self._section, self._value)
         if not len(value):
             value = ''
         ctrl = self.GetWindow()
         ctrl.SetSelection(int(value))

     def TransferFromWindow(self):
         ctrl = self.GetWindow()
         value = ctrl.GetSelection()
         self._config.Set(self._section, self._value, str(value))

class MyValidator(MyBaseValidator):
    def Validate(self, win):
        ctrl = self.GetWindow()
        if not ctrl.IsEnabled():
            return True
        if isinstance(ctrl, (wxChoice, wxCheckBox, wxRadioButton)) or self._canEmpty:
            return True
        if isinstance(ctrl, (wxIntCtrl, wxSpinCtrl)):
            text = str(ctrl.GetValue())
        else:
            text = ctrl.GetValue()
        if len(text) == 0:
            page = self.GetWindow().GetParent()
            wxMessageBox("Value cannot be empty", "ClamWin Free Antivirus", style=wxICON_EXCLAMATION|wxOK)
            ctrl.SetBackgroundColour("yellow")
            ctrl.SetFocus()
            ctrl.Refresh()
            return False
        else:
            ctrl.SetBackgroundColour(wxSystemSettings_GetColour(wxSYS_COLOUR_WINDOW))
            ctrl.Refresh()
            return True

    def TransferToWindow(self):
        value = self._config.Get(self._section, self._value)
        ctrl = self.GetWindow()
        if isinstance(ctrl, (wxIntCtrl, wxCheckBox, wxRadioButton, wxSpinCtrl, wxIntCtrl)):
            value = int(value)
        else:
            if not len(value):
               value = ''

        if(isinstance(ctrl, wxChoice)):
            ctrl.SetStringSelection(value)
        else:
            ctrl.SetValue(value)


    def TransferFromWindow(self):
        ctrl = self.GetWindow()
        if(isinstance(ctrl, wxChoice)):
            value = ctrl.GetStringSelection()
        elif isinstance(ctrl, (wxCheckBox, wxRadioButton, wxIntCtrl, wxSpinCtrl)):
            value = str(ctrl.GetValue())
        elif isinstance(ctrl, wxTimeCtrl):
            # set C locale, otherwise python and wxpython complain
            locale.setlocale(locale.LC_ALL, 'C')
            value = ctrl.GetWxDateTime().Format('%H:%M:%S')
        else:
            value = ctrl.GetValue()

        if self._config is not None:
            self._config.Set(self._section, self._value, value)


class MyFolderPromptCreateValidator(MyValidator):
    def Validate(self, win):
        if not self.GetWindow().IsEnabled():
            return True
        if not MyValidator.Validate(self, win):
            return False
        ctrl = self.GetWindow()
        path = ctrl.GetValue()
        # offer to create a folder if it doesn't exist
        if not os.path.isdir(path):
            main_win = win.GetParent()
            choice = MsgBox.MessageBox(main_win, 'ClamWin Free Antivirus',
                        'The folder you selected does not exist. Would you like to create %s now?' % path,
                        wxYES_NO  | wxICON_QUESTION)
            if choice == wxID_YES:
                try:
                    os.mkdir(path)
                except Exception, e:
                    MsgBox.ErrorBox(main_win, 'Unable to create folder %s. Error: %s' % (path, str(e)))
        return True

class MyPatternValidator(MyBaseValidator):
    def Validate(self, win):
        ctrl = self.GetWindow()
        if not ctrl.IsEnabled() or self._canEmpty:
            return True
        strings = ctrl.GetStrings()
        if len(strings) == 0:
            page = self.GetWindow().GetParent()
            wxMessageBox("Value cannot be empty", "ClamWin Free Antivirus", style=wxICON_EXCLAMATION|wxOK)
            ctrl.GetListCtrl().SetBackgroundColour("yellow")
            ctrl.SetFocus()
            ctrl.Refresh()
            return False
        else:
            ctrl.SetBackgroundColour(wxSystemSettings_GetColour(wxSYS_COLOUR_WINDOW))
            return True

    def TransferToWindow(self):
        strings = self._config.Get(self._section, self._value)
        if len(strings) > 0:
            self.GetWindow().SetStrings(strings.split(Config.REGEX_SEPARATOR))

    def TransferFromWindow(self):
        # need this trick to enable saving edited label
        # when ok is clicked
        self.GetWindow().GetListCtrl().EditLabel(0)
        value = Config.REGEX_SEPARATOR.join(self.GetWindow().GetStrings())
        if self._config is not None:
            self._config.Set(self._section, self._value, value)
