# -*- coding: UTF-8 -*-

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

import wx
import wx.lib.intctrl as ICtrl
import wx.gizmos
import wx.lib.masked as masked
import Utils, EmailAlert, Config
import os, sys, time, locale
import DialogScheduledScan
import Scheduler

import I18N
#_ = I18N.getClamString

def create(parent, config=None, switchToSchedule=False):
    return PreferencesDlg(parent, config, switchToSchedule)

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
 wxID_WXPREFERENCESDLGCHECKBOXWARNDBOLD, wxID_WXPREFERENCESDLGCHOICEPRIORITY, 
 wxID_WXPREFERENCESDLGCHOICEUPDATEDAY, 
 wxID_WXPREFERENCESDLGCHOICEUPDATEFREQUENCY, 
 wxID_WXPREFERENCESDLGCHOICELANGUAGE,
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
 wxID_WXPREFERENCESDLGSTATICBOXLANGUAGE,
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
 wxID_WXPREFERENCESDLGSTATICTEXTLANGUAGE,
 wxID_WXPREFERENCESDLGSTATICTEXTLANGUAGEREMARK,
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
] = map(lambda _init_ctrls: wx.NewId(), range(123))


AVAILABLE_LANGUAGES = {'en_UK' : 'English',
                       'de_DE' : 'Deutsch',
                       'es_ES' : 'Espanol',
                       'fr_FR' : 'Francais',
                       'hu_HU' : 'Hungarian',
                       'it_IT' : 'Italian',
                       'nl_BE' : 'Nederlands',
                       'pl_PL' : 'Polish',
                       'ru_RU' : 'Russian'
                       }

WINDOWSUILANGUAGESTRING = _('Windows UI Language')

class PreferencesDlg(wx.Dialog):
    def _init_coll_imageListScheduler_Images(self, parent):
        # generated method, don't edit

        parent.Add(bitmap=wx.Bitmap('img/ListScan.png', wx.BITMAP_TYPE_PNG),
              mask=wx.NullBitmap)

    def _init_coll_notebook_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self._panelOptions, select=True,
              text=_('General'))
        parent.AddPage(imageId=-1, page=self._panelFilters, select=False,
              text=_('Filters'))
        parent.AddPage(imageId=-1, page=self._panelInternetUpdate, select=False,
              text=_('Internet Updates'))
        parent.AddPage(imageId=-1, page=self._panelProxy, select=False,
              text=_('Proxy'))
        parent.AddPage(imageId=-1, page=self._panelScheduler, select=False,
              text=_('Scheduled Scans'))
        parent.AddPage(imageId=-1, page=self._panelEmailAlerts, select=False,
              text=_('Email Alerts'))
        parent.AddPage(imageId=-1, page=self._panelArchives, select=False,
              text=_('Archives'))
        parent.AddPage(imageId=-1, page=self._panelFiles, select=False,
              text=_('File Locations'))
        parent.AddPage(imageId=-1, page=self._panelReports, select=False,
              text=_('Reports'))
        parent.AddPage(imageId=-1, page=self._panelEmailScanning, select=False,
              text=_('Email Scanning'))
        parent.AddPage(imageId=-1, page=self._panelAdvanced, select=False,
              text=_('Advanced'))

    def _init_coll_listViewScheduledTasks_Columns(self, parent):
        # generated method, don't edit

        parent.InsertColumn(col=0, format=wx.LIST_FORMAT_LEFT,
              heading=_('Description'), width=-1)
        parent.InsertColumn(col=1, format=wx.LIST_FORMAT_LEFT, heading=_('Path'),
              width=-1)
        parent.InsertColumn(col=2, format=wx.LIST_FORMAT_LEFT,
              heading=_('Frequency'), width=-1)

    def _init_utils(self):
        # generated method, don't edit
        self.imageListScheduler = wx.ImageList(height=16, width=16)
        self._init_coll_imageListScheduler_Images(self.imageListScheduler)

    def _init_ctrls(self, prnt):
        # generated method, don't edit

        INTERNETUPDATE_INPUTXPOS = 150
        wx.Dialog.__init__(self, id=wxID_WXPREFERENCESDLG, name='', parent=prnt,
              pos=wx.Point(604, 301), size=wx.Size(419, 391),
              style=wx.DEFAULT_DIALOG_STYLE, title=_('ClamWin Preferences'))
        self._init_utils()
        self.SetClientSize(wx.Size(411, 414))
        self.SetAutoLayout(False)
        self.Center(wx.BOTH)
        self.Bind(wx.EVT_CHAR_HOOK, self.OnCharHook)

        self.notebook = wx.Notebook(self,wx.ID_ANY,pos=wx.Point(7, 7), size=wx.Size(398,368), style=wx.NB_MULTILINE)
        self.notebook.SetAutoLayout(True)

        self._panelOptions = wx.Panel(self.notebook,wx.ID_ANY, pos=wx.Point(0, 0),
              size=wx.Size(390, 274), style=wx.TAB_TRAVERSAL)

        self._panelInternetUpdate = wx.Panel(self.notebook,wx.ID_ANY,pos=wx.Point(0,0), size=wx.Size(390, 274), style=wx.TAB_TRAVERSAL)

        self._panelProxy = wx.Panel(self.notebook,wx.ID_ANY,pos=wx.Point(0, 0),
              size=wx.Size(390, 274), style=wx.TAB_TRAVERSAL)

        self._panelFiles = wx.Panel(self.notebook,wx.ID_ANY,pos=wx.Point(0, 0),
              size=wx.Size(390, 254), style=wx.TAB_TRAVERSAL)

        self._panelArchives = wx.Panel(self.notebook,wx.ID_ANY, pos=wx.Point(0, 0),
              size=wx.Size(390, 274), style=wx.TAB_TRAVERSAL)

        self._panelReports = wx.Panel(self.notebook,wx.ID_ANY,pos=wx.Point(0, 0),
              size=wx.Size(390, 274), style=wx.TAB_TRAVERSAL)

        self._panelEmailScanning = wx.Panel(self.notebook,wx.ID_ANY,pos=wx.Point(0,
              0), size=wx.Size(390, 274), style=wx.TAB_TRAVERSAL)

        self._panelAdvanced = wx.Panel(self.notebook,wx.ID_ANY,pos=wx.Point(0, 0),
              size=wx.Size(390, 274), style=wx.TAB_TRAVERSAL)

        self.buttonOK = wx.Button(self,wx.ID_OK, label=_('OK'), pos=wx.Point(128, 384),
              size=wx.Size(72, 23))
        self.buttonOK.SetToolTipString(_('Closes the window and saves the changes'))
        self.buttonOK.SetDefault()
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.buttonOK)

        self.buttonCancel = wx.Button(self,wx.ID_CANCEL,label=_('Cancel'), pos=wx.Point(209,384), size=wx.Size(75, 23))
        self.buttonCancel.SetToolTipString(_('Closes the window without saving the changes'))
        self.Bind(wx.EVT_BUTTON,self.OnCancel,self.buttonCancel)


        #-----panel Proxy

        self.staticTextProxyHost = wx.StaticText(self._panelProxy,wx.ID_ANY,label=_('Proxy &Server:'), pos=wx.Point(6, 61), size=wx.Size(80, 15))
        
        self.textCtrlProxyHost = wx.TextCtrl(self._panelProxy,wx.ID_ANY, pos=wx.Point(91,57), size=wx.Size(199, 21))
        self.textCtrlProxyHost.SetToolTipString(_('Proxy Server domain name or IP address'))

        self.staticTextProxyPort = wx.StaticText(self._panelProxy,wx.ID_ANY, label=_('P&ort:'),pos=wx.Point(296, 61), size=wx.Size(34, 15))

        self.intCtrlProxyPort = ICtrl.IntCtrl(allow_long=False, allow_none=False,
              default_color=wx.BLACK, id=wxID_WXPREFERENCESDLGINTCTRLPROXYPORT,
              limited=False, max=65535, min=0, name='intCtrlProxyPort',
              oob_color=wx.RED, parent=self._panelProxy, pos=wx.Point(332, 57),
              size=wx.Size(54, 21), style=0, value=3128)
        self.intCtrlProxyPort.SetBounds((0, 65535))
        self.intCtrlProxyPort.SetToolTipString(_('Proxy Server port number (0-65535)'))

        self.staticTextProxyUser = wx.StaticText(self._panelProxy,wx.ID_ANY,
              label=_('&User Name:'), pos=wx.Point(6, 97), size=wx.Size(80, 15))

        self.textCtrlProxyUser = wx.TextCtrl(self._panelProxy,wx.ID_ANY,pos=wx.Point(91,93), size=wx.Size(295, 21))
        self.textCtrlProxyUser.SetToolTipString(_('Proxy Server Account Name (optional)'))

        self.staticTextProxyPassword = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTPROXYPASSWORD,
              label=_('&Password:'), name='staticTextProxyPassword',
              parent=self._panelProxy, pos=wx.Point(6, 135), size=wx.Size(80, 15))

        self.textCtrlProxyPassword = wx.TextCtrl(self._panelProxy,wx.ID_ANY,
              pos=wx.Point(91, 131), size=wx.Size(295, 21), style=wx.TE_PASSWORD)
        self.textCtrlProxyPassword.SetToolTipString(_('Proxy Server account password (optional)'))

        self.staticTextExplain = wx.StaticText(self._panelProxy,wx.ID_ANY,
              label=_('Leave these fields blank if you do not connect via Proxy Server'),
              pos=wx.Point(6,15), size=wx.Size(378, 27))

        #-----

        #-----Panel Options

        self.staticBoxScanOptions = wx.StaticBox(id=wxID_WXPREFERENCESDLGSTATICBOXSCANOPTIONS,
              label=_('Scanning Options'), name='staticBoxScanOptions',
              parent=self._panelOptions, pos=wx.Point(6, 11), size=wx.Size(376,
              87), style=0)

        self.staticTextLanguage = wx.StaticText(self._panelOptions,wx.ID_ANY,
                label=_('&Language:'), pos=wx.Point(15,243), size=wx.Size(100, 13))

        listLanguages = [WINDOWSUILANGUAGESTRING]
        for i in AVAILABLE_LANGUAGES.itervalues():
            listLanguages = listLanguages + [i]
        self.choiceLanguage = wx.Choice(self._panelOptions,wx.ID_ANY,choices=listLanguages,
            pos=wx.Point(100,243), size=wx.Size(200,21))
        self.choiceLanguage.SetSelection(1)
        self.choiceLanguage.SetToolTipString(_('Choose auto-detect or an available language'))
        loc = I18N.getLocale()
        self.choiceLanguage.SetStringSelection(WINDOWSUILANGUAGESTRING)
        self.Bind(wx.EVT_CHOICE,self.OnChoiceLanguage,self.choiceLanguage)


        self.staticTextLanguageRemark = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTLANGUAGEREMARK,
                label=_('The language will change next time ClamWin is started'), name='staticTextLanguageRemark',
                parent=self._panelOptions, pos=wx.Point(15,265), size=wx.Size(350, 13))
        #-----

        #-----Panel Internet Update

        self.checkBoxEnableAutoUpdate = wx.CheckBox(self._panelInternetUpdate,wx.ID_ANY,
              label=_('&Enable Automatic Virus Database Updates'),
              pos=wx.Point(6, 11), size=wx.Size(422, 20))
        self.checkBoxEnableAutoUpdate.SetToolTipString(_('Enable automatic virus database downloads '))
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckBoxEnableAutoUpdate,self.checkBoxEnableAutoUpdate)
    

        downloadSiteLabel = _('Download &Site :')
        if len(downloadSiteLabel) > 30:
            # Spread to two lines
            self.staticText1 = wx.StaticText(self._panelInternetUpdate,wx.ID_ANY,
                  label=downloadSiteLabel, pos=wx.Point(24, 34),
                  size=wx.Size(81, 26))
            
        else:
            self.staticText1 = wx.StaticText(self._panelInternetUpdate,wx.ID_ANY,
                  label=downloadSiteLabel, pos=wx.Point(24, 43),
                  size=wx.Size(81, 13))

        self.textCtrlDBMirror = wx.TextCtrl(self._panelInternetUpdate,wx.ID_ANY,
              pos=wx.Point(INTERNETUPDATE_INPUTXPOS, 37), size=wx.Size(180, 21))
        self.textCtrlDBMirror.SetToolTipString(_('Specify Database Mirror Site here. Usually this is database.clamav.net'))

        self.staticTextUpdateFrequency = wx.StaticText(self._panelInternetUpdate,wx.ID_ANY,
              label=_('&Update Frequency:'), pos=wx.Point(23, 70))


        self.choiceUpdateFrequency = wx.Choice(self._panelInternetUpdate,wx.ID_ANY,choices=[_('Hourly'), _('Daily'),_('Workdays'), _('Weekly')],
              pos=wx.Point(INTERNETUPDATE_INPUTXPOS, 67), size=wx.Size(140, 21))
        self.choiceUpdateFrequency.SetSelection(1)
        self.choiceUpdateFrequency.SetToolTipString(_('How often virus database is downloaded'))
        self.choiceUpdateFrequency.SetStringSelection(_('Daily'))
        self.Bind(wx.EVT_CHOICE,self.OnChoiceUpdateFrequency,self.choiceUpdateFrequency)

        #-----

        #-----Panel Files    

      
        self.staticTextClamScan = wx.StaticText(self._panelFiles,wx.ID_ANY,
              label=_('&ClamScan Location:'), pos=wx.Point(6, 15), size=wx.Size(354, 13))

        self.textCtrlClamScan = wx.TextCtrl(self._panelFiles,wx.ID_ANY, pos=wx.Point(6,33), size=wx.Size(356, 20))
        self.textCtrlClamScan.SetToolTipString(_('Specify location of clamscan'))

        self.buttonBrowseClamScan = wx.Button(self._panelFiles,wx.ID_ANY,label='...',
              pos=wx.Point(363, 34), size=wx.Size(20, 20))
        self.buttonBrowseClamScan.SetToolTipString(_('Click to browse for clamscan'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonBrowseClamScan,self.buttonBrowseClamScan)

        self.staticTextFreshClam = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTFRESHCLAM,
              label=_('&FreshClam Location:'), name='staticTextFreshClam',
              parent=self._panelFiles, pos=wx.Point(6, 65), size=wx.Size(354, 13),
              style=0)
        self.staticTextFreshClam.SetToolTipString('')

        self.textCtrlFreshClam = wx.TextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLFRESHCLAM,
              name='textCtrlFreshClam', parent=self._panelFiles, pos=wx.Point(6,
              83), size=wx.Size(355, 20), style=0, value='')
        self.textCtrlFreshClam.SetToolTipString(_('Specify location of freshclam'))

        self.buttonBrowseFreshClam = wx.Button(id=wxID_WXPREFERENCESDLGBUTTONBROWSEFRESHCLAM,
              label='...', name='buttonBrowseFreshClam',
              parent=self._panelFiles, pos=wx.Point(363, 83), size=wx.Size(20,
              20), style=0)
        self.buttonBrowseFreshClam.SetToolTipString(_('Click to browse for freshclam'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonBrowseFreshClam,self.buttonBrowseFreshClam)

        self.staticTextVirDB = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTVIRDB,
              label=_('&Virus Database Folder:'), name='staticTextVirDB',
              parent=self._panelFiles, pos=wx.Point(6, 115), size=wx.Size(354,
              13), style=0)
        self.staticTextVirDB.SetToolTipString('')

        self.textCtrlVirDB = wx.TextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLVIRDB,
              name='textCtrlVirDB', parent=self._panelFiles, pos=wx.Point(6,
              133), size=wx.Size(355, 20), style=0, value='')
        self.textCtrlVirDB.SetToolTipString(_('Specify location of virus database files'))

        self.buttonVirDB = wx.Button(id=wxID_WXPREFERENCESDLGBUTTONVIRDB,
              label='...', name='buttonVirDB', parent=self._panelFiles,
              pos=wx.Point(362, 133), size=wx.Size(20, 20), style=0)
        self.buttonVirDB.SetToolTipString(_('Click to browse for a virus database folder'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonBrowseVirDB,self.buttonVirDB)

        self.checkBoxScanRecursive = wx.CheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXSCANRECURSIVE,
              label=_('&Scan In Subdirectories'), name='checkBoxScanRecursive',
              parent=self._panelOptions, pos=wx.Point(15, 29), size=wx.Size(354,
              18), style=0)
        self.checkBoxScanRecursive.SetToolTipString(_('Select if you wish to scan in subdirectories recursively'))
        self.checkBoxScanRecursive.SetValue(False)

        self.staticTextUpdateTime = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTUPDATETIME,
              label=_('&Time:'), name='staticTextUpdateTime',
              parent=self._panelInternetUpdate, pos=wx.Point(23, 97),
              size=wx.Size(33, 18), style=0)

        self.staticTextUpdateDay = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTUPDATEDAY,
              label=_('&Day Of The Week:'), name='staticTextUpdateDay',
              parent=self._panelInternetUpdate, pos=wx.Point(23, 124),
              size=wx.Size(96, 18), style=0)
        self.staticTextUpdateDay.SetToolTipString('')

        self.staticLineUpdateTimeCtrl = wx.StaticLine(id=wxID_WXPREFERENCESDLGSTATICLINEUPDATETIMECTRL,
              name='staticLineUpdateTimeCtrl', parent=self._panelInternetUpdate,
              pos=wx.Point(INTERNETUPDATE_INPUTXPOS, 94), size=wx.Size(74, 22), style=0)
        self.staticLineUpdateTimeCtrl.Show(False)
        self.staticLineUpdateTimeCtrl.SetToolTipString(_('When the download should be started'))

        self.spinButtonUpdateTime = wx.SpinButton(id=wxID_WXPREFERENCESDLGSPINBUTTONUPDATETIME,
              name='spinButtonUpdateTime', parent=self._panelInternetUpdate,
              pos=wx.Point(INTERNETUPDATE_INPUTXPOS + 76, 94), size=wx.Size(16, 23),
              style=wx.SP_ARROW_KEYS | wx.SP_VERTICAL)
        self.spinButtonUpdateTime.SetToolTipString('')

        self.checkBoxScanArchives = wx.CheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXSCANARCHIVES,
              label=_('&Scan In Archives'), name='checkBoxScanArchives',
              parent=self._panelArchives, pos=wx.Point(6, 15), size=wx.Size(322,
              20), style=0)
        self.checkBoxScanArchives.SetValue(False)
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckBoxScanArchives,self.checkBoxScanArchives)

        self.staticTextMaxSize = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTMAXSIZE,
              label=_('Do Not Scan Archives Larger Than'),
              name='staticTextMaxSize', parent=self._panelArchives,
              pos=wx.Point(24, 49), size=wx.Size(200, 15), style=0)

        self.spinCtrlArchiveSize = wx.SpinCtrl(id=wxID_WXPREFERENCESDLGSPINCTRLARCHIVESIZE,
              initial=0, max=4096, min=1, name='spinCtrlArchiveSize',
              parent=self._panelArchives, pos=wx.Point(229, 45), size=wx.Size(72,
              21), style=wx.SP_ARROW_KEYS)

        self.staticTextMB1 = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTMB1,
              label=_('MegaBytes'), name='staticTextMB1',
              parent=self._panelArchives, pos=wx.Point(310, 49), size=wx.Size(80,
              16), style=0)

        self.staticTextLimitFiles = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTLIMITFILES,
              label=_('Do Not Extract More Than '), name='staticTextLimitFiles',
              parent=self._panelArchives, pos=wx.Point(24, 82), size=wx.Size(200,
              17), style=0)

        self.spinCtrlArchiveFiles = wx.SpinCtrl(id=wxID_WXPREFERENCESDLGSPINCTRLARCHIVEFILES,
              initial=0, max=1073741824, min=1, name='spinCtrlArchiveFiles',
              parent=self._panelArchives, pos=wx.Point(229, 79), size=wx.Size(72,
              21), style=wx.SP_ARROW_KEYS)

        self.staticTextFiles = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTFILES,
              label=_('Files'), name='staticTextFiles', parent=self._panelArchives,
              pos=wx.Point(310, 82), size=wx.Size(80, 16), style=0)

        self.staticTextRecursion = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTRECURSION,
              label=_('Do Not Extract More Than '), name='staticTextRecursion',
              parent=self._panelArchives, pos=wx.Point(24, 118), size=wx.Size(200,
              19), style=0)

        self.spinCtrlRecursion = wx.SpinCtrl(id=wxID_WXPREFERENCESDLGSPINCTRLRECURSION,
              initial=0, max=999, min=1, name='spinCtrlRecursion',
              parent=self._panelArchives, pos=wx.Point(229, 115), size=wx.Size(72,
              21), style=wx.SP_ARROW_KEYS)

        self.staticTextSubArchives = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTSUBARCHIVES,
              label=_('Sub-Archives'), name='staticTextSubArchives',
              parent=self._panelArchives, pos=wx.Point(310, 118), size=wx.Size(82,
              16), style=0)

        self.checkBoxEnableMbox = wx.CheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXENABLEMBOX,
              label=_('&Treat Files As Mailboxes'), name='checkBoxEnableMbox',
              parent=self._panelAdvanced, pos=wx.Point(6, 11), size=wx.Size(384,
              18), style=0)
        self.checkBoxEnableMbox.SetToolTipString(_('Select if you wish to scan mailboxes'))
        self.checkBoxEnableMbox.SetValue(False)

        self.checkBoxEnableOLE2 = wx.CheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXENABLEOLE2,
              label=_('&Extract Attachments and Macros from MS Office Documents'),
              name='checkBoxEnableOLE2', parent=self._panelAdvanced,
              pos=wx.Point(6, 37), size=wx.Size(381, 18), style=0)
        self.checkBoxEnableOLE2.SetToolTipString(_('Select if you wish to scan OLE attachments and macros in MS Office Documents'))
        self.checkBoxEnableOLE2.SetValue(False)

        self.checkBoxScanExeOnly = wx.CheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXSCANEXEONLY,
              label=_('Try to &Scan Executable Files Only'),
              name='checkBoxScanExeOnly', parent=self._panelAdvanced,
              pos=wx.Point(6, 55), size=wx.Size(381, 18), style=0)
        self.checkBoxScanExeOnly.SetToolTipString(_('Select if you only wish to scan files that can run on MS Windows platform'))
        self.checkBoxScanExeOnly.SetValue(False)

        self.staticTextAdditionalParams = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTADDITIONALPARAMS,
              label=_('&Additional Clamscan Command Line Parameters:'),
              name='staticTextAdditionalParams', parent=self._panelAdvanced,
              pos=wx.Point(6, 79), size=wx.Size(378, 13), style=0)

        self.textCtrlAdditionalParams = wx.TextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLADDITIONALPARAMS,
              name='textCtrlAdditionalParams', parent=self._panelAdvanced,
              pos=wx.Point(6, 97), size=wx.Size(379, 21), style=0, value='')
        self.textCtrlAdditionalParams.SetToolTipString(_('Specify any additional parameters for clamscan.exe'))

        self.staticTextMaxLogSize = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTMAXLOGSIZE,
              label=_('Limit Log File Size To:'), name='staticTextMaxLogSize',
              parent=self._panelAdvanced, pos=wx.Point(6, 136), size=wx.Size(220,
              17), style=0)

        self.spinCtrlMaxLogSize = wx.SpinCtrl(id=wxID_WXPREFERENCESDLGSPINCTRLMAXLOGSIZE,
              initial=0, max=4096, min=1, name='spinCtrlMaxLogSize',
              parent=self._panelAdvanced, pos=wx.Point(6, 155), size=wx.Size(129,
              21), style=wx.SP_ARROW_KEYS)
        self.spinCtrlMaxLogSize.SetToolTipString(_('Select maximum size for the logfile'))
        self.spinCtrlMaxLogSize.SetValue(1)

        self.staticTextLogFIle = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTLOGFILE,
              label=_('&Scan Report File:'), name='staticTextLogFIle',
              parent=self._panelReports, pos=wx.Point(6, 15), size=wx.Size(354,
              19), style=0)
        self.staticTextLogFIle.SetToolTipString('')

        self.textCtrlScanLogFile = wx.TextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLSCANLOGFILE,
              name='textCtrlScanLogFile', parent=self._panelReports,
              pos=wx.Point(6, 35), size=wx.Size(360, 20), style=0, value='')
        self.textCtrlScanLogFile.SetToolTipString(_('Specify location for a scan reports log file'))

        self.buttonBrowseScanLog = wx.Button(id=wxID_WXPREFERENCESDLGBUTTONBROWSESCANLOG,
              label='...', name='buttonBrowseScanLog',
              parent=self._panelReports, pos=wx.Point(366, 35), size=wx.Size(20,
              20), style=0)
        self.buttonBrowseScanLog.SetToolTipString(_('Click to browse for a log file'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonBrowseScanLog,self.buttonBrowseScanLog)

        self.staticTextDBUpdateLogFile = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTDBUPDATELOGFILE,
              label=_('&Virus Database Update Report File:'),
              name='staticTextDBUpdateLogFile', parent=self._panelReports,
              pos=wx.Point(6, 66), size=wx.Size(354, 19), style=0)
        self.staticTextDBUpdateLogFile.SetToolTipString('')

        self.textCtrlUpdateLogFile = wx.TextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLUPDATELOGFILE,
              name='textCtrlUpdateLogFile', parent=self._panelReports,
              pos=wx.Point(6, 86), size=wx.Size(360, 20), style=0, value='')
        self.textCtrlUpdateLogFile.SetToolTipString(_('Specify location for a database updates log file'))

        self.buttonBrowseUpdateLog = wx.Button(id=wxID_WXPREFERENCESDLGBUTTONBROWSEUPDATELOG,
              label='...', name='buttonBrowseUpdateLog',
              parent=self._panelReports, pos=wx.Point(366, 86), size=wx.Size(20,
              20), style=0)
        self.buttonBrowseUpdateLog.SetToolTipString(_('Click to browse for a log file'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonBrowseUpdateLog,self.buttonBrowseUpdateLog)

        self._panelScheduler = wx.Panel(id=wxID_WXPREFERENCESDLG_PANELSCHEDULER,
              name='_panelScheduler', parent=self.notebook, pos=wx.Point(0, 0),
              size=wx.Size(390, 234), style=wx.TAB_TRAVERSAL)
        self._panelScheduler.SetToolTipString('')

        self.listViewScheduledTasks = wx.ListView(id=wxID_WXPREFERENCESDLGLISTVIEWSCHEDULEDTASKS,
              name='listViewScheduledTasks', parent=self._panelScheduler,
              pos=wx.Point(6, 34), size=wx.Size(298, 158),
              style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.listViewScheduledTasks.SetToolTipString(_('List of Scheduled Scans'))
        self.listViewScheduledTasks.SetImageList(self.imageListScheduler,
              wx.IMAGE_LIST_NORMAL)
        self.listViewScheduledTasks.SetImageList(self.imageListScheduler,
              wx.IMAGE_LIST_SMALL)
        self._init_coll_listViewScheduledTasks_Columns(self.listViewScheduledTasks)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnScheduledTasksUpdate,self.listViewScheduledTasks)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED,self.OnScheduledTasksUpdate,self.listViewScheduledTasks)
        self.Bind(wx.EVT_LEFT_DCLICK,self.OnButtonEditScheduledScan,self.listViewScheduledTasks)

        self.staticTextScheduledTasks = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTSCHEDULEDTASKS,
              label=_('Scheduled Scans:'), name='staticTextScheduledTasks',
              parent=self._panelScheduler, pos=wx.Point(6, 14), size=wx.Size(154,
              16), style=0)
        self.staticTextScheduledTasks.SetToolTipString('')

        self.buttonTaskAdd = wx.Button(id=wxID_WXPREFERENCESDLGBUTTONTASKADD,
              label=_('&Add'), name='buttonTaskAdd', parent=self._panelScheduler,
              pos=wx.Point(311, 34), size=wx.Size(75, 23), style=0)
        self.Bind(wx.EVT_BUTTON,self.OnButtonAddScheduledScan,self.buttonTaskAdd)

        self.buttonTaskRemove = wx.Button(id=wxID_WXPREFERENCESDLGBUTTONTASKREMOVE,
              label=_('&Remove'), name='buttonTaskRemove',
              parent=self._panelScheduler, pos=wx.Point(311, 67), size=wx.Size(75,
              23), style=0)
        self.Bind(wx.EVT_BUTTON,self.OnButtonRemoveScheduledScan,self.buttonTaskRemove)

        self.buttonTaskEdit = wx.Button(id=wxID_WXPREFERENCESDLGBUTTONTASKEDIT,
              label=_('&Edit'), name='buttonTaskEdit', parent=self._panelScheduler,
              pos=wx.Point(311, 101), size=wx.Size(75, 23), style=0)
        self.Bind(wx.EVT_BUTTON,self.OnButtonEditScheduledScan,self.buttonTaskEdit)

        self.checkBoxInfectedOnly = wx.CheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXINFECTEDONLY,
              label=_('&Display Infected Files Only'), name='checkBoxInfectedOnly',
              parent=self._panelOptions, pos=wx.Point(15, 49), size=wx.Size(354,
              18), style=0)
        self.checkBoxInfectedOnly.SetValue(False)
        self.checkBoxInfectedOnly.SetToolTipString(_('Select if you wish to display infected files only in the scan progress window'))

        self.choiceUpdateDay = wx.Choice(choices=[_('Monday'), _('Tuesday'),
              _('Wednesday'), _('Thursday'), _('Friday'), _('Saturday'), _('Sunday')],
              id=wxID_WXPREFERENCESDLGCHOICEUPDATEDAY, name='choiceUpdateDay',
              parent=self._panelInternetUpdate, pos=wx.Point(INTERNETUPDATE_INPUTXPOS, 121),
              size=wx.Size(110, 21), style=0)
        self.choiceUpdateDay.SetSelection(1)
        self.choiceUpdateDay.SetToolTipString(_('When update frequency is weekly select day of the week for an update'))
        self.choiceUpdateDay.SetStringSelection(_('Tuesday'))

        self.checkBoxWarnDBOld = wx.CheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXWARNDBOLD,
              label=_('&Warn if Virus database is Out of Date'),
              name='checkBoxWarnDBOld', parent=self._panelInternetUpdate,
              pos=wx.Point(6, 140), size=wx.Size(322, 20), style=0)
        self.checkBoxWarnDBOld.SetToolTipString(_('Will display a reminder if the virus database is older than 3 days'))
        self.checkBoxWarnDBOld.SetValue(False)
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckBoxWarnDBOld,self.checkBoxWarnDBOld)

        self.staticBoxInfected = wx.StaticBox(id=wxID_WXPREFERENCESDLGSTATICBOXINFECTED,
              label=_('Infected Files'), name='staticBoxInfected',
              parent=self._panelOptions, pos=wx.Point(6, 100), size=wx.Size(376,
              123), style=0)

        self.staticBoxLanguage = wx.StaticBox(id=wxID_WXPREFERENCESDLGSTATICBOXLANGUAGE,
            label=_('Language Settings'), name='staticBoxLanguage',
            parent=self._panelOptions, pos=wx.Point(6, 225), size=wx.Size(376,
            58), style=0)

        self.radioButtonReport = wx.RadioButton(id=wxID_WXPREFERENCESDLGRADIOBUTTONREPORT,
              label=_('&Report Only'), name='radioButtonReport',
              parent=self._panelOptions, pos=wx.Point(15, 115), size=wx.Size(354,
              18), style=0)
        self.radioButtonReport.SetValue(False)
        self.Bind(wx.EVT_RADIOBUTTON,self.OnRadioInfected,self.radioButtonReport)

        self.radioButtonRemoveInfected = wx.RadioButton(id=wxID_WXPREFERENCESDLGRADIOBUTTONREMOVEINFECTED,
              label=_('&Remove (Use Carefully)'), name='radioButtonRemoveInfected',
              parent=self._panelOptions, pos=wx.Point(15, 133), size=wx.Size(354,
              18), style=0)
        self.radioButtonRemoveInfected.SetValue(False)
        self.Bind(wx.EVT_RADIOBUTTON,self.OnRadioInfected,self.radioButtonRemoveInfected)

        self.radioButtonQuarantine = wx.RadioButton(id=wxID_WXPREFERENCESDLGRADIOBUTTONQUARANTINE,
              label=_('&Move To Quarantine Folder:'), name='radioButtonQuarantine',
              parent=self._panelOptions, pos=wx.Point(15, 152), size=wx.Size(354,
              18), style=0)
        self.radioButtonQuarantine.SetValue(False)
        self.Bind(wx.EVT_RADIOBUTTON,self.OnRadioInfected,self.radioButtonQuarantine)

        self.textCtrlQuarantine = wx.TextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLQUARANTINE,
              name='textCtrlQuarantine', parent=self._panelOptions,
              pos=wx.Point(31, 175), size=wx.Size(319, 20), style=0, value='')
        self.textCtrlQuarantine.SetToolTipString(_('Specify location for a quarantine folder'))

        self.buttonBrowseQuarantine = wx.Button(id=wxID_WXPREFERENCESDLGBUTTONBROWSEQUARANTINE,
              label='...', name='buttonBrowseQuarantine',
              parent=self._panelOptions, pos=wx.Point(351, 175), size=wx.Size(20,
              20), style=0)
        self.buttonBrowseQuarantine.SetToolTipString(_('Click to browse for a quarantine folder'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonBrowseQuarantine,self.buttonBrowseQuarantine)

        self._panelEmailAlerts = wx.Panel(id=wxID_WXPREFERENCESDLG_PANELEMAILALERTS,
              name='_panelEmailAlerts', parent=self.notebook, pos=wx.Point(0, 0),
              size=wx.Size(390, 290), style=wx.TAB_TRAVERSAL)
        self._panelEmailAlerts.SetToolTipString('')

        self.checkBoxSMTPEnable = wx.CheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXSMTPENABLE,
              label=_('&Send Email Alert On Virus Detection'),
              name='checkBoxSMTPEnable', parent=self._panelEmailAlerts,
              pos=wx.Point(6, 11), size=wx.Size(362, 15), style=0)
        self.checkBoxSMTPEnable.SetValue(False)
        self.checkBoxSMTPEnable.SetToolTipString(_('Select if you wish to receive email alerts when ClamWin detects a virus'))
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckBoxSMTPEnable,self.checkBoxSMTPEnable)

        self.staticBoxSMTPConnection = wx.StaticBox(id=wxID_WXPREFERENCESDLGSTATICBOXSMTPCONNECTION,
              label=_('SMTP Connection Details'), name='staticBoxSMTPConnection',
              parent=self._panelEmailAlerts, pos=wx.Point(16, 27),
              size=wx.Size(368, 101), style=0)
        self.staticBoxSMTPConnection.SetToolTipString('')

        SMTPCONNECTION_STRETCH = 80

        self.staticTextSMTPHost = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTSMTPHOST,
              label=_('&Mail Server:'), name='staticTextSMTPHost',
              parent=self._panelEmailAlerts, pos=wx.Point(24, 49),
              size=wx.Size(71 + SMTPCONNECTION_STRETCH, 16), style=0)
        self.staticTextSMTPHost.SetToolTipString('')

        SMTPCONNECTION_XPOS = 124

        self.textCtrlSMTPHost = wx.TextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLSMTPHOST,
              name='textCtrlSMTPHost', parent=self._panelEmailAlerts,
              pos=wx.Point(SMTPCONNECTION_XPOS, 46), size=wx.Size(296-SMTPCONNECTION_XPOS, 21), style=0, value='')
        self.textCtrlSMTPHost.SetToolTipString(_('SMTP Server domain name or IP address'))

        self.staticTextSMTPPort = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTSMTPPORT,
              label=_('P&ort:'), name='staticTextSMTPPort',
              parent=self._panelEmailAlerts, pos=wx.Point(300, 49),
              size=wx.Size(31 + SMTPCONNECTION_STRETCH, 16), style=0)

        self.intCtrlSMTPPort = ICtrl.IntCtrl(allow_long=False, allow_none=False,
              default_color=wx.BLACK, id=wxID_WXPREFERENCESDLGINTCTRLSMTPPORT,
              limited=False, max=65535, min=0, name='intCtrlSMTPPort',
              oob_color=wx.RED, parent=self._panelEmailAlerts, pos=wx.Point(330,
              46), size=wx.Size(47, 21), style=0, value=25)
        self.intCtrlSMTPPort.SetBounds((0, 65535))
        self.intCtrlSMTPPort.SetToolTipString(_('Mail Server port number (0-65535)'))

        self.staticTextSMTPUserName = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTSMTPUSERNAME,
              label=_('&User Name:'), name='staticTextSMTPUserName',
              parent=self._panelEmailAlerts, pos=wx.Point(24, 72),
              size=wx.Size(79 + SMTPCONNECTION_STRETCH, 16), style=0)
        self.staticTextSMTPUserName.SetToolTipString('')

        self.textCtrlSMTPUser = wx.TextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLSMTPUSER,
              name='textCtrlSMTPUser', parent=self._panelEmailAlerts,
              pos=wx.Point(SMTPCONNECTION_XPOS, 69), size=wx.Size(101, 21), style=0, value='')
        self.textCtrlSMTPUser.SetToolTipString(_('Mail Server Account Name (optional)'))

        self.staticTextSMTPPassword = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTSMTPPASSWORD,
              label=_('&Password:'), name='staticTextSMTPPassword',
              parent=self._panelEmailAlerts, pos=wx.Point(24, 95),
              size=wx.Size(66 + SMTPCONNECTION_STRETCH, 16), style=0)
        self.staticTextSMTPPassword.SetToolTipString('')

        self.textCtrlSMTPPassword = wx.TextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLSMTPPASSWORD,
              name='textCtrlSMTPPassword', parent=self._panelEmailAlerts,
              pos=wx.Point(SMTPCONNECTION_XPOS, 92), size=wx.Size(101, 21), style=wx.TE_PASSWORD,
              value='')
        self.textCtrlSMTPPassword.SetToolTipString(_('Mail Server account password (optional)'))

        EMAILALERTS_MAINYPOS = 142

        self.staticBoxEmailDetails = wx.StaticBox(id=wxID_WXPREFERENCESDLGSTATICBOXEMAILDETAILS,
              label=_('Email Message Details'), name='staticBoxEmailDetails',
              parent=self._panelEmailAlerts, pos=wx.Point(16, EMAILALERTS_MAINYPOS),
              size=wx.Size(368, 95), style=0)
        self.staticBoxEmailDetails.SetToolTipString('')

        self.staticTextSMTPFrom = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTSMTPFROM,
              label=_('&From:'), name='staticTextSMTPFrom',
              parent=self._panelEmailAlerts, pos=wx.Point(24, EMAILALERTS_MAINYPOS + 22),
              size=wx.Size(63, 16), style=0)
        self.staticTextSMTPFrom.SetToolTipString('')

        self.textCtrlSMTPFrom = wx.TextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLSMTPFROM,
              name='textCtrlSMTPFrom', parent=self._panelEmailAlerts,
              pos=wx.Point(104, EMAILALERTS_MAINYPOS + 16), size=wx.Size(273, 21), style=0, value='')
        self.textCtrlSMTPFrom.SetToolTipString(_('Specify an email address from which the notification will be sent.'))

        self.staticTextSMTPTo = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTSMTPTO,
              label=_('&To:'), name='staticTextSMTPTo',
              parent=self._panelEmailAlerts, pos=wx.Point(24, EMAILALERTS_MAINYPOS + 46),
              size=wx.Size(63, 16), style=0)
        self.staticTextSMTPTo.SetToolTipString('')

        self.textCtrlSMTPTo = wx.TextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLSMTPTO,
              name='textCtrlSMTPTo', parent=self._panelEmailAlerts,
              pos=wx.Point(104, EMAILALERTS_MAINYPOS + 41), size=wx.Size(273, 21), style=0, value='')
        self.textCtrlSMTPTo.SetToolTipString(_('Specify an email address where the email alert will be delivered.  Separate multiple addresses with commas.'))

        self.staticTextSMTPSubject = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTSMTPSUBJECT,
              label=_('Su&bject:'), name='staticTextSMTPSubject',
              parent=self._panelEmailAlerts, pos=wx.Point(24, EMAILALERTS_MAINYPOS + 69),
              size=wx.Size(63, 16), style=0)
        self.staticTextSMTPSubject.SetToolTipString('')

        self.textCtrlSMTPSubject = wx.TextCtrl(id=wxID_WXPREFERENCESDLGTEXTCTRLSMTPSUBJECT,
              name='textCtrlSMTPSubject', parent=self._panelEmailAlerts,
              pos=wx.Point(104, EMAILALERTS_MAINYPOS + 65), size=wx.Size(273, 21), style=0, value='')
        self.textCtrlSMTPSubject.SetToolTipString(_("Specify Recipient's email address where the email alert will be delivered"))

        self.buttonSendTestEmail = wx.Button(id=wxID_WXPREFERENCESDLGBUTTONSENDTESTEMAIL,
              label=_('Send &Test Email'), name='buttonSendTestEmail',
              parent=self._panelEmailAlerts, pos=wx.Point(120, EMAILALERTS_MAINYPOS + 103),
              size=wx.Size(149, 23), style=0)
        self.buttonSendTestEmail.SetToolTipString(_('Click to send a test email message'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonSendTestEmail,self.buttonSendTestEmail)

        self.checkBoxTrayNotify = wx.CheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXTRAYNOTIFY,
              label=_('&Display Pop-up Notification Messages In Taskbar '),
              name='checkBoxTrayNotify', parent=self._panelReports,
              pos=wx.Point(6, 123), size=wx.Size(354, 18), style=0)
        self.checkBoxTrayNotify.SetValue(False)
        self.checkBoxTrayNotify.SetToolTipString(_('Select if you wish to receive Tray notification pop-up messages'))

        self._panelFilters = wx.Panel(id=wxID_WXPREFERENCESDLG_PANELFILTERS,
              name='_panelFilters', parent=self.notebook, pos=wx.Point(0, 0),
              size=wx.Size(390, 234), style=wx.TAB_TRAVERSAL)

        self.staticTextFiltreDesc1 = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTFILTREDESC1,
              label=_('Specify Filename Patterns to include and/or exclude in scanning'),
              name='staticTextFiltreDesc1', parent=self._panelFilters,
              pos=wx.Point(6, 11), size=wx.Size(383, 32), style=0)

        self.staticText2 = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXT2,
              label=_('(To specify a regular expression include your pattern within <...>)'),
              name='staticText2', parent=self._panelFilters, pos=wx.Point(6, 40),
              size=wx.Size(382, 32), style=0)

        self.staticTextFiltersExclude = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTFILTERSEXCLUDE,
              label=_('&Exclude Matching Filenames:'),
              name='staticTextFiltersExclude', parent=self._panelFilters,
              pos=wx.Point(6, 68), size=wx.Size(184, 32), style=0)

        self.editableListBoxFiltersExclude = wx.gizmos.EditableListBox(id=wxID_WXPREFERENCESDLGEDITABLELISTBOXFILTERSEXCLUDE,
              label=_('Patterns'), name='editableListBoxFiltersExclude',
              parent=self._panelFilters, pos=wx.Point(6, 99), size=wx.Size(182,
              151))

        self.buttonUpFiltersExclude = self.editableListBoxFiltersExclude.GetUpButton()
        self.buttonUpFiltersExclude.SetToolTipString(_('Move up'))

        self.buttonDownFiltersExclude = self.editableListBoxFiltersExclude.GetDownButton()
        self.buttonDownFiltersExclude.SetToolTipString(_('Move down'))

        self.buttonNewFiltersExclude = self.editableListBoxFiltersExclude.GetNewButton()
        self.buttonNewFiltersExclude.SetToolTipString(_('New item'))

        self.buttonDelFiltersExclude = self.editableListBoxFiltersExclude.GetDelButton()
        self.buttonDelFiltersExclude.SetToolTipString(_('Delete item'))

        self.buttonEditFiltersExclude = self.editableListBoxFiltersExclude.GetEditButton()
        self.buttonEditFiltersExclude.SetToolTipString(_('Edit item'))

        self.staticTextFiltersInclude = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTFILTERSINCLUDE,
              label=_('&Scan Only Matching Filenames:'),
              name='staticTextFiltersInclude', parent=self._panelFilters,
              pos=wx.Point(202, 68), size=wx.Size(187, 32), style=0)

        self.editableListBoxFiltersInclude = wx.gizmos.EditableListBox(id=wxID_WXPREFERENCESDLGEDITABLELISTBOXFILTERSINCLUDE,
              label=_('Patterns'), name='editableListBoxFiltersInclude',
              parent=self._panelFilters, pos=wx.Point(200, 99), size=wx.Size(184,
              151))

        self.buttonUpFiltersInclude = self.editableListBoxFiltersInclude.GetUpButton()
        self.buttonUpFiltersInclude.SetToolTipString(_('Move up'))

        self.buttonDownFiltersInclude = self.editableListBoxFiltersInclude.GetDownButton()
        self.buttonDownFiltersInclude.SetToolTipString(_('Move down'))

        self.buttonNewFiltersInclude = self.editableListBoxFiltersInclude.GetNewButton()
        self.buttonNewFiltersInclude.SetToolTipString(_('New item'))

        self.buttonDelFiltersInclude = self.editableListBoxFiltersInclude.GetDelButton()
        self.buttonDelFiltersInclude.SetToolTipString(_('Delete item'))

        self.buttonEditFiltersInclude = self.editableListBoxFiltersInclude.GetEditButton()
        self.buttonEditFiltersInclude.SetToolTipString(_('Edit item'))

        self.buttonTaskDeactivate = wx.Button(id=wxID_WXPREFERENCESDLGBUTTONTASKDEACTIVATE,
              label=_('&Deactivate'), name='buttonTaskDeactivate',
              parent=self._panelScheduler, pos=wx.Point(311, 169),
              size=wx.Size(75, 23), style=0)
        self.Bind(wx.EVT_BUTTON,self.OnButtonTaskDeactivate,self.buttonTaskDeactivate)

        self.buttonTaskActivate = wx.Button(id=wxID_WXPREFERENCESDLGBUTTONTASKACTIVATE,
              label=_('A&ctivate'), name='buttonTaskActivate',
              parent=self._panelScheduler, pos=wx.Point(311, 135),
              size=wx.Size(75, 23), style=0)
        self.Bind(wx.EVT_BUTTON,self.OnButtonTaskActivate,self.buttonTaskActivate)

        self.checkBoxUpdateLogon = wx.CheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXUPDATELOGON,
              label=_('&Update Virus Database On Logon'),
              name='checkBoxUpdateLogon', parent=self._panelInternetUpdate,
              pos=wx.Point(6, 168), size=wx.Size(322, 20), style=0)
        self.checkBoxUpdateLogon.SetToolTipString(_('Select if you wish to update the virus databases just after you logged on'))
        self.checkBoxUpdateLogon.SetValue(False)
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckBoxEnableAutoUpdate,self.checkBoxUpdateLogon)

        self.checkBoxCheckVersion = wx.CheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXCHECKVERSION,
              label=_('&Notify About New ClamWin Releases'),
              name='checkBoxCheckVersion', parent=self._panelInternetUpdate,
              pos=wx.Point(6, 195), size=wx.Size(322, 20), style=0)
        self.checkBoxCheckVersion.SetToolTipString(_('Select if you wish to get a notification message when ClamWin Free Antivirus program has been updated'))
        self.checkBoxCheckVersion.SetValue(False)
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckBoxCheckVersionCheckbox,self.checkBoxCheckVersion)

        self.staticTextNoPersonal = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTNOPERSONAL,
              label=_('(No personal information is transmitted during this check)'),
              name='staticTextNoPersonal', parent=self._panelInternetUpdate,
              pos=wx.Point(27, 215), size=wx.Size(350, 13), style=0)

        self.staticTextMB2 = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTMB2,
              label=_('MegaBytes'), name='staticTextMB2',
              parent=self._panelAdvanced, pos=wx.Point(144, 156), size=wx.Size(74,
              16), style=0)

        self.staticTextPriority = wx.StaticText(id=wxID_WXPREFERENCESDLGSTATICTEXTPRIORITY,
              label=_('Scanner &Priority:'), name='staticTextPriority',
              parent=self._panelAdvanced, pos=wx.Point(252, 136),
              size=wx.Size(103, 17), style=0)

        self.choicePriority = wx.Choice(choices=[_('Low'), _('Normal')],
              id=wxID_WXPREFERENCESDLGCHOICEPRIORITY, name='choicePriority',
              parent=self._panelAdvanced, pos=wx.Point(252, 155),
              size=wx.Size(134, 21), style=0)
        self.choicePriority.SetToolTipString(_('Specify the process priority for the virus scanner.'))
        self.choicePriority.SetStringSelection(_('Normal'))
        self.choicePriority.SetLabel('')

        self.checkBoxShowProgress = wx.CheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXSHOWPROGRESS,
              label=_('Display &File Scanned % Progress Indicator'),
              name='checkBoxShowProgress', parent=self._panelOptions,
              pos=wx.Point(15, 72), size=wx.Size(354, 18), style=0)
        self.checkBoxShowProgress.SetValue(False)
        self.checkBoxShowProgress.SetToolTipString(_('Select if you wish to display infected files only in the scan progress window'))

        self.checkBoxUnload = wx.CheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXUNLOAD,
              label=_('&Unload Infected Programs from Computer Memory'),
              name='checkBoxUnload', parent=self._panelOptions, pos=wx.Point(15,
              202), size=wx.Size(354, 17), style=0)
        self.checkBoxUnload.SetValue(False)
        self.checkBoxUnload.SetToolTipString( _('Select if you wish to unload infected programs from computer memory so they can be quarantined or removed'))

        self.staticBoxOutlookAddin = wx.StaticBox(id=wxID_WXPREFERENCESDLGSTATICBOXOUTLOOKADDIN,
              label=_('Microsoft Outlook'), name='staticBoxOutlookAddin',
              parent=self._panelEmailScanning, pos=wx.Point(6, 11),
              size=wx.Size(376, 77), style=0)

        self.checkBoxOutlookScanIncoming = wx.CheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXOUTLOOKSCANINCOMING,
              label=_('Scan &Incoming Email Messages'),
              name='checkBoxOutlookScanIncoming',
              parent=self._panelEmailScanning, pos=wx.Point(15, 32),
              size=wx.Size(354, 18), style=0)
        self.checkBoxOutlookScanIncoming.SetValue(False)
        self.checkBoxOutlookScanIncoming.SetToolTipString(_('Select if you wish to enable scanning of incoming email messages in MS Outlook'))
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckBoxOutlookAddinEnabledCheckbox,self.checkBoxOutlookScanIncoming)

        self.checkBoxOutlookScanOutgoing = wx.CheckBox(id=wxID_WXPREFERENCESDLGCHECKBOXOUTLOOKSCANOUTGOING,
              label=_('Scan &Outgoing Email Messages'),
              name='checkBoxOutlookScanOutgoing',
              parent=self._panelEmailScanning, pos=wx.Point(15, 57),
              size=wx.Size(354, 18), style=0)
        self.checkBoxOutlookScanOutgoing.SetValue(False)
        self.checkBoxOutlookScanOutgoing.SetToolTipString(_('Select if you wish to enable scanning of outgoing email messages in MS Outlook'))
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckBoxOutlookScanOutgoingCheckbox,self.checkBoxOutlookScanOutgoing)

        self._init_coll_notebook_Pages(self.notebook)

    def __init__(self, parent, config, switchToSchedule):
        
        self._config = config
        if sys.platform.startswith("win"):
            self._scheduledScans = Scheduler.LoadPersistentScheduledScans(
                os.path.join(Utils.GetScheduleShelvePath(self._config), 'ScheduledScans'))
        self._init_ctrls(parent)

        # set window icons
        icons = wx.IconBundle()
        icons.AddIconFromFile('img/FrameIcon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcons(icons)

        # wxWidgets notebook bug workaround
        # http://sourceforge.net/tracker/index.php?func=detail&aid=645323&group_id=9863&atid=109863
        s = self.notebook.GetSize();
        self.notebook.SetSize(wx.Size(s.GetWidth() - 1, s.GetHeight()));
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
        self.EndModal(wx.ID_CANCEL)

    def OnOK(self, event):
        if self._Apply():
            self.EndModal(wx.ID_OK)


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
                wx.MessageBox(_('An error occurred whilst saving configuration file %s. Please check that you have write permission to the configuration file.') % self._config.GetFilename(),_('Error'),wx.OK | wx.ICON_ERROR)
                return False

            # raise the event so other programs can reload config
            if sys.platform.startswith("win"):
                # Save scheduled scans separately
                Scheduler.SavePersistentScheduledScans(
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
                    print _("Event Failed"), str(e)
            return True



    def _EnableOptionsControls(self, init):
        if init:
            #self._config.Get('ClamAV', 'RemoveInfected') == '1'
            enable = bool(self._config.Get('ClamAV', 'MoveInfected'))# and len(self._config.Get('ClamAV', 'QuarantineDir')) > 0
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
        self.choiceLanguage.SetValidator(MyValidator(config=self._config, section='ClamAV', value='Language'))
        self._EnableOptionsControls(True)

    def _FiltersPageInit(self):
        self.editableListBoxFiltersInclude.SetValidator(MyPatternValidator(config=self._config, section='ClamAV', value='IncludePatterns'))
        self.editableListBoxFiltersExclude.SetValidator(MyPatternValidator(config=self._config, section='ClamAV', value='ExcludePatterns'))
        if sys.platform.startswith('win'):
            self.Bind(wx.EVT_CHAR,self.OnEditableListBoxChar,self.editableListBoxFiltersInclude.GetListCtrl())
            self.Bind(wx.EVT_CHAR,self.OnEditableListBoxChar,self.editableListBoxFiltersExclude.GetListCtrl())

    def _EnableInternetUpdateControls(self, init):
        if sys.platform.startswith("win"):
            if init:
                enable = bool(self._config.Get('Updates', 'Enable'))
                enableDay = enable and self._config.Get('Updates', 'Frequency') == 'Weekly'
            else:
                enable = self.checkBoxEnableAutoUpdate.IsChecked()
                enableDay = enable and self.choiceUpdateFrequency.GetStringSelection() == _('Weekly')
            self.textCtrlDBMirror.Enable(enable)
            self.choiceUpdateDay.Enable(enableDay)
            self.choiceUpdateFrequency.Enable(enable)
            self.timeUpdate.Enable(enable)
            self.spinButtonUpdateTime.Enable(enable)

    def _InternetUpdatePageInit(self):
        locale.setlocale(locale.LC_ALL, 'C')
        self.timeUpdate = masked.TimeCtrl(parent=self._panelInternetUpdate,
         pos=self.staticLineUpdateTimeCtrl.GetPosition(),
         size=self.staticLineUpdateTimeCtrl.GetSize(),  fmt24hr=Utils.IsTime24(),
         spinButton=self.spinButtonUpdateTime,
         useFixedWidthFont=False, display_seconds=True)
        self.timeUpdate.SetToolTipString(self.staticLineUpdateTimeCtrl.GetToolTip().GetTip())
        self.textCtrlDBMirror.SetValidator(MyValidator(config=self._config, section='Updates', value='DBMirror', canEmpty=False))
        self.checkBoxEnableAutoUpdate.SetValidator(MyValidator(config=self._config, section='Updates', value='Enable'))
        self.checkBoxCheckVersion.SetValidator(MyValidator(config=self._config, section='Updates', value='CheckVersion'))
        self.choiceUpdateFrequency.SetValidator(MyValidator(config=self._config, section='Updates', value='Frequency'))
        self.timeUpdate.SetValidator(MyValidator(config=self._config, section='Updates', value='Time'))
        self.checkBoxUpdateLogon.SetValidator(MyValidator(config=self._config, section='Updates', value='UpdateOnLogon'))
        self.checkBoxWarnDBOld.SetValidator(MyValidator(config=self._config, section='Updates', value='WarnOutOfDate'))
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
            enable = bool(self._config.Get('EmailAlerts', 'Enable'))
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
            enable = bool(self._config.Get('ClamAV', 'ScanArchives'))
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
        freq = Scheduler._getFrequencies()[sc.Frequency]
        self.listViewScheduledTasks.SetStringItem(pos, 2, freq)
        item = self.listViewScheduledTasks.GetItem(pos)
        if sc.Active:
            item.SetTextColour(wx.NullColour)
        else:
            item.SetTextColour(wx.LIGHT_GREY)
        self.listViewScheduledTasks.SetItem(item)

    def OnCharHook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

    def OnButtonBrowseFreshClam(self, event):
        if sys.platform.startswith("win"):
            filename = 'freshclam.exe'
            mask = _("Executable files (*.exe)|*.exe|All files (*.*)|*.*")
        else:
            filename = 'freshclam'
            mask = _("All files (*)|*")
        dlg = wx.FileDialog(self, _("Choose a file"), ".", filename, mask, wx.OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
            self.textCtrlFreshClam.Clear()
            self.textCtrlFreshClam.WriteText(filename)
        finally:
            dlg.Destroy()

    def OnButtonBrowseClamScan(self, event):
        if sys.platform.startswith("win"):
            filename = 'clamscan.exe'
            mask = _("Executable files (*.exe)|*.exe|All files (*.*)|*.*")
        else:
            filename = 'clamscan'
            mask = _("All files (*)|*")
        dlg = wx.FileDialog(self, _("Choose a file"), ".", filename, mask, wx.OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                self.textCtrlClamScan.Clear()
                self.textCtrlClamScan.WriteText(filename)
        finally:
            dlg.Destroy()

    def OnButtonBrowseVirDB(self, event):
        dlg = wx.DirDialog(self, _('Select a directory'))
        try:
            if dlg.ShowModal() == wx.ID_OK:
                dir = dlg.GetPath()
                self.textCtrlVirDB.Clear()
                self.textCtrlVirDB.WriteText(dir)
        finally:
            dlg.Destroy()

    def OnButtonBrowseScanLog(self, event):
        if sys.platform.startswith("win"):
            filename = 'ClamScanLog.txt'
            mask = _("Text Files (*.txt)|*.txt|All files (*.*)|*.*")
        else:
            filename = 'ClamScanLog'
            mask = _("All files (*)|*")
        dlg = wx.FileDialog(self, _("Choose a file"), ".", filename, mask, wx.SAVE)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                self.textCtrlScanLogFile.Clear()
                self.textCtrlScanLogFile.WriteText(filename)
        finally:
            dlg.Destroy()

    def OnButtonBrowseUpdateLog(self, event):
        if sys.platform.startswith("win"):
            filename = 'ClamUpdateLog.txt'
            mask = _("Text Files (*.txt)|*.txt|All files (*.*)|*.*")
        else:
            filename = 'ClamUpdateLog'
            mask = _("All files (*)|*")
        dlg = wx.FileDialog(self, _("Choose a file"), ".", filename, mask, wx.SAVE)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                self.textCtrlUpdateLogFile.Clear()
                self.textCtrlUpdateLogFile.WriteText(filename)
        finally:
            dlg.Destroy()

    def OnChoiceLanguage(self, event):
        self._EnableOptionsControls(False)
        event.Skip()

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
            wx.MessageBox(_('Maximum amount of scheduled items (20) has been reached.'),_('Error'),wx.OK | wx.ICON_ERROR)
            return
        sc = Scheduler.ScheduledScanInfo()
        dlg = DialogScheduledScan.DialogScheduledScan(self, sc)
        try:
            if dlg.ShowModal() == wx.ID_OK:
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
            dlg = DialogScheduledScan.DialogScheduledScan(self, sc)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    self.listViewScheduledTasks.DeleteItem(id)
                    self._ListAddScheduledScan(sc, id)
                    item = self.listViewScheduledTasks.GetItem(id)
                    if sc.Active:
                        item.SetTextColour(wx.NullColour)
                    else:
                        item.SetTextColour(wx.LIGHT_GREY)
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
        dlg = wx.DirDialog(self, _('Select a directory'))
        try:
            if dlg.ShowModal() == wx.ID_OK:
                dir = dlg.GetPath()
                self.textCtrlQuarantine.Clear()
                self.textCtrlQuarantine.WriteText(dir)
        finally:
            dlg.Destroy()


    def OnCheckBoxSMTPEnable(self, event):
        self._EnableEmailAlertsControls(False)

    def OnButtonSendTestEmail(self, event):
        self.SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
        try:
            msg = EmailAlert.VirusAlertMsg(self.textCtrlSMTPFrom.GetValue(),
                            self.textCtrlSMTPTo.GetValue(),
                            self.textCtrlSMTPSubject.GetValue() + _(' (Testing)'),
                            self.textCtrlSMTPHost.GetValue(),
                            self.intCtrlSMTPPort.GetValue(),
                            self.textCtrlSMTPUser.GetValue(),
                            self.textCtrlSMTPPassword.GetValue(),
                            Body=_('This is a test message sent during configuration of ClamWin Free Antivirus on the following computer: %s.\n'\
                                'Please do not be alarmed.\n') % Utils.GetHostName())
            status, msg = msg.Send(True)
            if not status:
                raise Exception(msg)
            wx.MessageBox(_('Test Email has been sent successfully.'),_('Info'),wx.OK|wx.ICON_INFORMATION)
        except Exception, e:
            wx.MessageBox(_('Could not send the email. Please ensure you are connected to the internet. Error: %s') % str(e),_('Error'),wx.OK|wx.ICON_ERROR)
        self.SetCursor(wx.NullCursor)

    def OnEditableListBoxChar(self, event):
        # Bind F2 key to edit label function
        if event.GetKeyCode() == wx.WXK_F2:
            listCtrl = event.GetEventObject()
            selected = listCtrl.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if selected != -1:
                listCtrl.EditLabel(selected)
        else:
            event.Skip()

    def OnButtonTaskActivate(self, event):
        selected = self.listViewScheduledTasks.GetFirstSelected()
        if selected != -1:
            self._scheduledScans[selected].Active = True
        item = self.listViewScheduledTasks.GetItem(selected)
        item.SetTextColour(wx.BLACK)
        self.listViewScheduledTasks.SetItem(item)
        self.UpdateScheduledTasksButtons()

    def OnButtonTaskDeactivate(self, event):
        selected = self.listViewScheduledTasks.GetFirstSelected()
        if selected != -1:
            self._scheduledScans[selected].Active = False
        item = self.listViewScheduledTasks.GetItem(selected)
        item.SetTextColour(wx.LIGHT_GREY)
        self.listViewScheduledTasks.SetItem(item)
        self.UpdateScheduledTasksButtons()

    def OnCheckBoxCheckVersionCheckbox(self, event):
        event.Skip()

    def OnCheckBoxOutlookAddinEnabledCheckbox(self, event):
        event.Skip()

    def OnCheckBoxOutlookScanOutgoingCheckbox(self, event):
        event.Skip()

    def OnCheckBoxWarnDBOld(self, event):
        event.Skip()

class MyBaseValidator(wx.PyValidator):
     def __init__(self, config, section, value, canEmpty=True):
         wx.PyValidator.__init__(self)
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

##class MyLanguageValidator(MyBaseValidator):
##    def TransferToWindow(self):
##        key = I18N.getLocale()
##        if not len(key):
##            value = WINDOWSUILANGUAGESTRING
##        else:
##            value = AVAILABLE_LANGUAGES[key]
##        ctrl = self.GetWindow()
##        ctrl.SetSelection(value)
##
##    def TransferFromWindow(self):
##        ctrl = self.GetWindow()
##        value = ctrl.GetSelection()
##        for key in AVAILABLE_LANGUAGES.iterkeys():
##            if AVAILABLE_LANGUAGES[i] == value:
##                I18N.forceLocale(key)
##                return
##        # if no key was found, revert to Windows UI Locale
##        I18N.forceLocale('')
        
class MyValidator(MyBaseValidator):
    
    def _getFrequencies(self):
        # get the frequencies in the current language
        choiceFrequencies=[_('Hourly'), _('Daily'), _('Workdays'), _('Weekly')]
        return choiceFrequencies
    
    def _getEnglishFrequency(self, transFrequency):
        # take a translated frequency and return the English frequency selected
        englishFrequencies=['Hourly', 'Daily', 'Workdays', 'Weekly']
        choiceFrequences=self._getFrequencies()
        freqIndex = choiceFrequences.index(transFrequency)
        if freqIndex >= 0:
            return englishFrequencies[freqIndex]
        raise "Could not find English frequency %s" % transFrequency
    
    def _getLocalFrequency(self, englishFrequency):
        # take an english frequency and return the corresponding local language frequency
        choiceFrequencies=self._getFrequencies()
        englishFrequencies=['Hourly', 'Daily', 'Workdays', 'Weekly']
        freqIndex = englishFrequencies.index(englishFrequency)
        if freqIndex >= 0:
            return choiceFrequencies[freqIndex]
        raise "Could not find local frequency %s" % englishFrequency

    def _getLanguages(self):
        # get the languages in the current language
        choiceLanguages=[WINDOWSUILANGUAGESTRING]
        for key in AVAILABLE_LANGUAGES.iterkeys():
            choiceLanguages=choiceLanguages + [AVAILABLE_LANGUAGES[key]]
        return choiceLanguages

    def _getEnglishLanguages(self, transLanguage):
        # take a translated language and return the English language selected
        if transLanguage == WINDOWSUILANGUAGESTRING:
            return 'Windows UI Language'
        return transLanguage

    def _getLocalLanguage(self, englishLanguage):
        # take an english language and return the corresponding local language name
        if englishLanguage == 'Windows UI Language':
            return WINDOWSUILANGUAGESTRING
        return englishLanguage
                
    def _getEnglishPriority(self, transPriority):
        if transPriority == _('Low'):
            return 'Low'
        elif transPriority == _('Normal'):
            return 'Normal'
        raise "Could not find English priority %s" % transPriority
    
    def _getLocalPriority(self, englishPriority):
        if englishPriority == 'Low':
            return _('Low')
        elif englishPriority == 'Normal':
            return _('Normal')
        raise "Could not find local priority %s" % englishPriority
    

    def Validate(self, win):         
        ctrl = self.GetWindow()
        if not ctrl.IsEnabled():
            return True
        if isinstance(ctrl, (wx.Choice, wx.CheckBox, wx.RadioButton)) or self._canEmpty:
            return True
        if isinstance(ctrl, (ICtrl.IntCtrl, wx.SpinCtrl)):
            text = str(ctrl.GetValue())
        else:
            text = ctrl.GetValue()
        if len(text) == 0:
            page = self.GetWindow().GetParent()
            wx.MessageBox(_("Value cannot be empty"), _("ClamWin Free Antivirus"), style=wx.ICON_EXCLAMATION|wx.OK)
            ctrl.SetBackgroundColour("yellow")
            ctrl.SetFocus()
            ctrl.Refresh()
            return False
        else:
            ctrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            ctrl.Refresh()
            return True

    def TransferToWindow(self):
        ctrl = self.GetWindow()
        # Language setting does not use _config, so check this first
        if self._value == 'Language':
            key = I18N.getLocale()
            if key == '':
                value = WINDOWSUILANGUAGESTRING
            else:
                value = AVAILABLE_LANGUAGES[key]
            ctrl.SetStringSelection(value)
            return
            
        value = self._config.Get(self._section, self._value)
        #if isinstance(ctrl, (ICtrl.IntCtrl, wx.CheckBox, wx.RadioButton, wx.SpinCtrl)):
        if isinstance(ctrl, (ICtrl.IntCtrl, wx.SpinCtrl)):
            value = int(value)
        elif isinstance(ctrl, (wx.CheckBox, wx.RadioButton)):
            value = bool(value)
        else:
            if not len(value):
               value = ''

        if(isinstance(ctrl, wx.Choice)):
            if self._value == 'Frequency':
                value = self._getLocalFrequency(value)
            elif self._value == 'Priority':
                value = self._getLocalPriority(value)
                
            ctrl.SetStringSelection(value)
        else:
            ctrl.SetValue(value)


    def TransferFromWindow(self):
        ctrl = self.GetWindow()
        if(isinstance(ctrl, wx.Choice)):
            if self._value == 'Frequency':
                value = self._getEnglishFrequency(ctrl.GetStringSelection())
            elif self._value == 'Priority':
                value = self._getEnglishPriority(ctrl.GetStringSelection())
            elif self._value == 'Language':
                value = ctrl.GetStringSelection()
                for key in AVAILABLE_LANGUAGES.iterkeys():
                    if AVAILABLE_LANGUAGES[key] == value:
                        I18N.forceLocale(key)
                        return
                I18N.forceLocale('')
            else:
                value = ctrl.GetStringSelection()         
        elif isinstance(ctrl, (wx.CheckBox, wx.RadioButton, ICtrl.IntCtrl, wx.SpinCtrl)):
            value = str(ctrl.GetValue())
        elif isinstance(ctrl, masked.TimeCtrl):
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
            choice = wx.MessageBox(_('The folder you selected does not exist. Would you like to create %s now?') % path,
                                   _('ClamWin Free Antivirus'),
                                   wx.YES_NO  | wx.ICON_QUESTION)
            if choice == wx.ID_YES:
                try:
                    os.mkdir(path)
                except Exception, e:
                    wx.MessageBox(_('Unable to create folder %s. Error: %s') % (path, str(e)),_('Error'),wx.OK|wx.ICON_ERROR)                  
        return True

class MyPatternValidator(MyBaseValidator):
    def Validate(self, win):
        ctrl = self.GetWindow()
        if not ctrl.IsEnabled() or self._canEmpty:
            return True
        strings = ctrl.GetStrings()
        if len(strings) == 0:
            page = self.GetWindow().GetParent()
            wx.MessageBox(_("Value cannot be empty"), _("ClamWin Free Antivirus"), wx.ICON_EXCLAMATION|wx.OK)            
            ctrl.GetListCtrl().SetBackgroundColour("yellow")
            ctrl.SetFocus()
            ctrl.Refresh()
            return False
        else:
            ctrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
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
