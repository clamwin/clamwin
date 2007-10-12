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

        self._panelOptions = wx.Panel(self.notebook,style=wx.TAB_TRAVERSAL)

        self._panelFilters = wx.Panel(self.notebook, style=wx.TAB_TRAVERSAL)

        self._panelInternetUpdate = wx.Panel(self.notebook, style=wx.TAB_TRAVERSAL)

        self._panelProxy = wx.Panel(self.notebook, style=wx.TAB_TRAVERSAL)

        self._panelScheduler = wx.Panel(self.notebook, style=wx.TAB_TRAVERSAL)

        self._panelEmailAlerts = wx.Panel(self.notebook,style=wx.TAB_TRAVERSAL)

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


        

        #-----Panel Options (General)

        self.staticBoxScanOptions = wx.StaticBox(self._panelOptions,wx.ID_ANY,_('Scanning Options'))
        SBsizerSO = wx.StaticBoxSizer(self.staticBoxScanOptions,wx.VERTICAL)

        self.checkBoxScanRecursive = wx.CheckBox(self._panelOptions,wx.ID_ANY,_('&Scan In Subdirectories'))
        self.checkBoxScanRecursive.SetToolTipString(_('Select if you wish to scan in subdirectories recursively'))
        SBsizerSO.Add(self.checkBoxScanRecursive,0,wx.LEFT,10)

        self.checkBoxInfectedOnly = wx.CheckBox(self._panelOptions,wx.ID_ANY,_('&Display Infected Files Only'))
        self.checkBoxInfectedOnly.SetToolTipString(_('Select if you wish to display infected files only in the scan progress window'))
        SBsizerSO.Add(self.checkBoxInfectedOnly,0,wx.LEFT,10)

        self.checkBoxShowProgress = wx.CheckBox(self._panelOptions,wx.ID_ANY,_('Display &File Scanned % Progress Indicator'))
        self.checkBoxShowProgress.SetToolTipString(_('Select if you wish to display infected files only in the scan progress window'))
        SBsizerSO.Add(self.checkBoxShowProgress,0,wx.LEFT,10)

        self.staticBoxInfected = wx.StaticBox(self._panelOptions,wx.ID_ANY,_('Infected Files'))
        SBsizerIF = wx.StaticBoxSizer(self.staticBoxInfected,wx.VERTICAL)
        
        self.radioButtonReport = wx.RadioButton(self._panelOptions,wx.ID_ANY,_('&Report Only'))
        self.Bind(wx.EVT_RADIOBUTTON,self.OnRadioInfected,self.radioButtonReport)
        SBsizerIF.Add(self.radioButtonReport,0,wx.LEFT,10)

        self.radioButtonRemoveInfected = wx.RadioButton(self._panelOptions,wx.ID_ANY,_('&Remove (Use Carefully)'))
        self.Bind(wx.EVT_RADIOBUTTON,self.OnRadioInfected,self.radioButtonRemoveInfected)
        SBsizerIF.Add(self.radioButtonRemoveInfected,0,wx.LEFT,10)

        self.radioButtonQuarantine = wx.RadioButton(self._panelOptions,wx.ID_ANY,_('&Move To Quarantine Folder:'))
        self.Bind(wx.EVT_RADIOBUTTON,self.OnRadioInfected,self.radioButtonQuarantine)
        SBsizerIF.Add(self.radioButtonQuarantine,0,wx.LEFT,10)

        self.textCtrlQuarantine = wx.TextCtrl(self._panelOptions,wx.ID_ANY)
        self.textCtrlQuarantine.SetToolTipString(_('Specify location for a quarantine folder'))

        self.buttonBrowseQuarantine = wx.Button(self._panelOptions,wx.ID_ANY,'...')
        self.buttonBrowseQuarantine.SetToolTipString(_('Click to browse for a quarantine folder'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonBrowseQuarantine,self.buttonBrowseQuarantine)
        
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(self.textCtrlQuarantine,1)
        bsizer.Add(self.buttonBrowseQuarantine)
        SBsizerIF.Add(bsizer,0,wx.EXPAND|wx.LEFT,10)

        self.checkBoxUnload = wx.CheckBox(self._panelOptions,wx.ID_ANY,_('&Unload Infected Programs from Computer Memory'))
        self.checkBoxUnload.SetToolTipString( _('Select if you wish to unload infected programs from computer memory so they can be quarantined or removed'))
        SBsizerIF.Add(self.checkBoxUnload,0,wx.LEFT,10)
        
        self.staticBoxLanguage = wx.StaticBox(self._panelOptions,wx.ID_ANY,_('Language Settings'))
        SBsizerL = wx.StaticBoxSizer(self.staticBoxLanguage,wx.VERTICAL)

        self.staticTextLanguage = wx.StaticText(self._panelOptions,wx.ID_ANY,_('&Language:'))

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

        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(self.staticTextLanguage)
        bsizer.Add(self.choiceLanguage)
        SBsizerL.Add(bsizer,0,wx.LEFT,10)
        
        self.staticTextLanguageRemark = wx.StaticText(self._panelOptions,wx.ID_ANY,_('The language will change next time ClamWin is started'))
        SBsizerL.Add(self.staticTextLanguageRemark,0,wx.LEFT,10)

        BSOptions = wx.BoxSizer(wx.VERTICAL)
        BSOptions.Add(SBsizerSO,1,wx.EXPAND|wx.ALL,5)
        BSOptions.Add(SBsizerIF,1,wx.EXPAND|wx.ALL,5)
        BSOptions.Add(SBsizerL,0,wx.EXPAND|wx.ALL,5)

        self._panelOptions.SetSizer(BSOptions)      

        
        #-----
        
        #-----Panel Filters

        bsizer = wx.BoxSizer(wx.VERTICAL)

        self.staticTextFiltreDesc1 = wx.StaticText(self._panelFilters,wx.ID_ANY,_('Specify Filename Patterns to include and/or exclude in scanning'))
        bsizer.Add(self.staticTextFiltreDesc1,0,wx.ALL,5)

        self.staticText2 = wx.StaticText(self._panelFilters,wx.ID_ANY,_('(To specify a regular expression include your pattern within <...>)'))
        bsizer.Add(self.staticText2,0,wx.ALL,5)

        gsizer = wx.FlexGridSizer(2,2)
        
        self.staticTextFiltersExclude = wx.StaticText(self._panelFilters,wx.ID_ANY,_('&Exclude Matching Filenames:'))
        gsizer.Add(self.staticTextFiltersExclude,1,wx.EXPAND)

        self.staticTextFiltersInclude = wx.StaticText(self._panelFilters,wx.ID_ANY,_('&Scan Only Matching Filenames:'))
        gsizer.Add(self.staticTextFiltersInclude,1,wx.EXPAND)

        self.editableListBoxFiltersExclude = wx.gizmos.EditableListBox(self._panelFilters,wx.ID_ANY,_('Patterns'))
        gsizer.Add(self.editableListBoxFiltersExclude,1,wx.EXPAND)

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


        self.editableListBoxFiltersInclude = wx.gizmos.EditableListBox(self._panelFilters,wx.ID_ANY,_('Patterns'))
        gsizer.Add(self.editableListBoxFiltersInclude,1,wx.EXPAND)
        
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

        gsizer.AddGrowableCol(0,1)
        gsizer.AddGrowableCol(1,1)
        gsizer.AddGrowableRow(1,1)
    
        bsizer.Add(gsizer,1,wx.EXPAND|wx.ALL,5)
        
        self._panelFilters.SetSizer(bsizer)

        #-----------------

        #-----Panel Internet Update

        bsizer = wx.BoxSizer(wx.VERTICAL)

        self.checkBoxEnableAutoUpdate = wx.CheckBox(self._panelInternetUpdate,wx.ID_ANY,_('&Enable Automatic Virus Database Updates'))
        self.checkBoxEnableAutoUpdate.SetToolTipString(_('Enable automatic virus database downloads '))
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckBoxEnableAutoUpdate,self.checkBoxEnableAutoUpdate)
        bsizer.Add(self.checkBoxEnableAutoUpdate,0,wx.ALL,5)
    

        gsizer = wx.FlexGridSizer(4,2)
        self.staticText1 = wx.StaticText(self._panelInternetUpdate,wx.ID_ANY,_('Download &Site :'))
        gsizer.Add(self.staticText1)   

        self.textCtrlDBMirror = wx.TextCtrl(self._panelInternetUpdate)
        self.textCtrlDBMirror.SetToolTipString(_('Specify Database Mirror Site here. Usually this is database.clamav.net'))
        gsizer.Add(self.textCtrlDBMirror,0,wx.EXPAND)

        self.staticTextUpdateFrequency = wx.StaticText(self._panelInternetUpdate,wx.ID_ANY,_('&Update Frequency:'))
        gsizer.Add(self.staticTextUpdateFrequency)

        self.choiceUpdateFrequency = wx.Choice(self._panelInternetUpdate,wx.ID_ANY,choices=[_('Hourly'), _('Daily'),_('Workdays'), _('Weekly')])
        self.choiceUpdateFrequency.SetSelection(1)
        self.choiceUpdateFrequency.SetToolTipString(_('How often virus database is downloaded'))
        self.choiceUpdateFrequency.SetStringSelection(_('Daily'))
        self.Bind(wx.EVT_CHOICE,self.OnChoiceUpdateFrequency,self.choiceUpdateFrequency)
        gsizer.Add(self.choiceUpdateFrequency)

        self.staticTextUpdateTime = wx.StaticText(self._panelInternetUpdate,wx.ID_ANY,_('&Time:'))
        gsizer.Add(self.staticTextUpdateTime)
        
        
        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.timeUpdate = masked.TimeCtrl(self._panelInternetUpdate,wx.ID_ANY,fmt24hr=Utils.IsTime24(), useFixedWidthFont=False, display_seconds=True)
        self.timeUpdate.SetToolTipString(_('When the download should be started'))
        h = self.timeUpdate.GetSize().height
        hbsizer.Add(self.timeUpdate)

        self.spinButtonUpdateTime = wx.SpinButton(self._panelInternetUpdate,wx.ID_ANY,size=(-1,h),style=wx.SP_ARROW_KEYS | wx.SP_VERTICAL)
        self.timeUpdate.BindSpinButton(self.spinButtonUpdateTime)
        hbsizer.Add(self.spinButtonUpdateTime)
        gsizer.Add(hbsizer)
        

        self.staticTextUpdateDay = wx.StaticText(self._panelInternetUpdate,wx.ID_ANY,_('&Day Of The Week:'))
        gsizer.Add(self.staticTextUpdateDay)
        
        self.choiceUpdateDay = wx.Choice(self._panelInternetUpdate,wx.ID_ANY,choices=[_('Monday'), _('Tuesday'),_('Wednesday'), _('Thursday'), _('Friday'), _('Saturday'), _('Sunday')])
        self.choiceUpdateDay.SetSelection(1)
        self.choiceUpdateDay.SetToolTipString(_('When update frequency is weekly select day of the week for an update'))
        self.choiceUpdateDay.SetStringSelection(_('Tuesday'))
        gsizer.Add(self.choiceUpdateDay)

        gsizer.AddGrowableCol(1,1)

        bsizer.Add(gsizer,0,wx.EXPAND|wx.ALL,5)

        self.checkBoxWarnDBOld = wx.CheckBox(self._panelInternetUpdate,wx.ID_ANY,_('&Warn if Virus database is Out of Date'))
        self.checkBoxWarnDBOld.SetToolTipString(_('Will display a reminder if the virus database is older than 3 days'))
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckBoxWarnDBOld,self.checkBoxWarnDBOld)
        bsizer.Add(self.checkBoxWarnDBOld,0,wx.ALL,5)

        self.checkBoxUpdateLogon = wx.CheckBox(self._panelInternetUpdate,wx.ID_ANY,_('&Update Virus Database On Logon'))
        self.checkBoxUpdateLogon.SetToolTipString(_('Select if you wish to update the virus databases just after you logged on'))
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckBoxEnableAutoUpdate,self.checkBoxUpdateLogon)
        bsizer.Add(self.checkBoxUpdateLogon,0,wx.ALL,5)

        self.checkBoxCheckVersion = wx.CheckBox(self._panelInternetUpdate,wx.ID_ANY,_('&Notify About New ClamWin Releases'))
        self.checkBoxCheckVersion.SetToolTipString(_('Select if you wish to get a notification message when ClamWin Free Antivirus program has been updated'))
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckBoxCheckVersionCheckbox,self.checkBoxCheckVersion)
        bsizer.Add(self.checkBoxCheckVersion,0,wx.ALL,5)

        self.staticTextNoPersonal = wx.StaticText(self._panelInternetUpdate,wx.ID_ANY,_('(No personal information is transmitted during this check)'))
        bsizer.Add(self.staticTextNoPersonal,0,wx.ALL,5)

        self._panelInternetUpdate.SetSizer(bsizer)

        #-----

        #-----panel Proxy

        bsizer = wx.BoxSizer(wx.VERTICAL)

        t = wx.StaticText(self._panelProxy,wx.ID_ANY,_('Leave these fields blank if you do not connect via Proxy Server'))
        bsizer.Add(t,0,wx.ALL,5)

        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        
        t = wx.StaticText(self._panelProxy,wx.ID_ANY,_('Proxy &Server:'))
        hbsizer.Add(t)
        
        self.textCtrlProxyHost = wx.TextCtrl(self._panelProxy,wx.ID_ANY, size=wx.Size(199, -1))
        self.textCtrlProxyHost.SetToolTipString(_('Proxy Server domain name or IP address'))
        hbsizer.Add(self.textCtrlProxyHost)

        hbsizer.Add((5,-1))

        t = wx.StaticText(self._panelProxy,wx.ID_ANY, _('P&ort:'))
        hbsizer.Add(t)

        self.intCtrlProxyPort = ICtrl.IntCtrl(self._panelProxy,wx.ID_ANY,allow_long=False, allow_none=False,
              default_color=wx.BLACK,limited=False, max=65535, min=0, oob_color=wx.RED,value=3128)
        self.intCtrlProxyPort.SetBounds((0, 65535))
        self.intCtrlProxyPort.SetToolTipString(_('Proxy Server port number (0-65535)'))
        hbsizer.Add(self.intCtrlProxyPort,1)

        bsizer.Add(hbsizer,0,wx.EXPAND|wx.ALL,5)

        hbsizer = wx.BoxSizer(wx.HORIZONTAL)

        t = wx.StaticText(self._panelProxy,wx.ID_ANY,_('&User Name:'))
        hbsizer.Add(t)

        self.textCtrlProxyUser = wx.TextCtrl(self._panelProxy)
        self.textCtrlProxyUser.SetToolTipString(_('Proxy Server Account Name (optional)'))
        hbsizer.Add(self.textCtrlProxyUser,1)

        bsizer.Add(hbsizer,0,wx.EXPAND|wx.ALL,5)

        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        t = wx.StaticText(self._panelProxy,wx.ID_ANY,_('&Password:'))
        hbsizer.Add(t)

        self.textCtrlProxyPassword = wx.TextCtrl(self._panelProxy,wx.ID_ANY,style=wx.TE_PASSWORD)
        self.textCtrlProxyPassword.SetToolTipString(_('Proxy Server account password (optional)'))
        hbsizer.Add(self.textCtrlProxyPassword,1)

        bsizer.Add(hbsizer,0,wx.EXPAND|wx.ALL,5)

        self._panelProxy.SetSizer(bsizer)
       

        #-----

        #------- Panel Scheduler
        
        gsizer = wx.FlexGridSizer(2,2)

        t = wx.StaticText(self._panelScheduler,wx.ID_ANY,_('Scheduled Scans:'))
        gsizer.Add(t,0,wx.ALL,5)

        gsizer.Add((0,0)) #add empty space

        
        self.listViewScheduledTasks = wx.ListView(self._panelScheduler,wx.ID_ANY,style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.listViewScheduledTasks.SetToolTipString(_('List of Scheduled Scans'))
        self.listViewScheduledTasks.SetImageList(self.imageListScheduler, wx.IMAGE_LIST_NORMAL)
        self.listViewScheduledTasks.SetImageList(self.imageListScheduler, wx.IMAGE_LIST_SMALL)
        self._init_coll_listViewScheduledTasks_Columns(self.listViewScheduledTasks)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnScheduledTasksUpdate,self.listViewScheduledTasks)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED,self.OnScheduledTasksUpdate,self.listViewScheduledTasks)
        self.Bind(wx.EVT_LEFT_DCLICK,self.OnButtonEditScheduledScan,self.listViewScheduledTasks)
        gsizer.Add(self.listViewScheduledTasks,0,wx.EXPAND|wx.ALL,5)

        bsizer = wx.BoxSizer(wx.VERTICAL)

        self.buttonTaskAdd = wx.Button(self._panelScheduler,wx.ID_ANY,_('&Add'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonAddScheduledScan,self.buttonTaskAdd)
        bsizer.Add(self.buttonTaskAdd)

        self.buttonTaskRemove = wx.Button(self._panelScheduler,wx.ID_ANY,_('&Remove'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonRemoveScheduledScan,self.buttonTaskRemove)
        bsizer.Add(self.buttonTaskRemove)

        self.buttonTaskEdit = wx.Button(self._panelScheduler,wx.ID_ANY,_('&Edit'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonEditScheduledScan,self.buttonTaskEdit)
        bsizer.Add(self.buttonTaskEdit)

        self.buttonTaskActivate = wx.Button(self._panelScheduler,wx.ID_ANY,_('A&ctivate'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonTaskActivate,self.buttonTaskActivate)
        bsizer.Add(self.buttonTaskActivate)

        self.buttonTaskDeactivate = wx.Button(self._panelScheduler,wx.ID_ANY,_('&Deactivate'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonTaskDeactivate,self.buttonTaskDeactivate)
        bsizer.Add(self.buttonTaskDeactivate)

        gsizer.Add(bsizer,0,wx.ALL,5)

        gsizer.AddGrowableCol(0,1)
        gsizer.AddGrowableRow(1,1)

        self._panelScheduler.SetSizer(gsizer)


        #-------------

        #-------Panel Email Alerts


        bsizer = wx.BoxSizer(wx.VERTICAL)

        self.checkBoxSMTPEnable = wx.CheckBox(self._panelEmailAlerts,wx.ID_ANY,_('&Send Email Alert On Virus Detection'))
        self.checkBoxSMTPEnable.SetToolTipString(_('Select if you wish to receive email alerts when ClamWin detects a virus'))
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckBoxSMTPEnable,self.checkBoxSMTPEnable)
        bsizer.Add(self.checkBoxSMTPEnable,0,wx.ALL,5)
        
        self.staticBoxSMTPConnection = wx.StaticBox(self._panelEmailAlerts,wx.ID_ANY,_('SMTP Connection Details'))
        sbsizer = wx.StaticBoxSizer(self.staticBoxSMTPConnection,wx.VERTICAL)

        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        t = wx.StaticText(self._panelEmailAlerts,wx.ID_ANY,_('&Mail Server:'))
        hbsizer.Add(t)

        self.textCtrlSMTPHost = wx.TextCtrl(self._panelEmailAlerts)
        self.textCtrlSMTPHost.SetToolTipString(_('SMTP Server domain name or IP address'))
        hbsizer.Add(self.textCtrlSMTPHost,1)

        hbsizer.Add((5,-1)) #add spacer

        t = wx.StaticText(self._panelEmailAlerts,wx.ID_ANY,_('P&ort:'))
        hbsizer.Add(t)

        self.intCtrlSMTPPort = ICtrl.IntCtrl(self._panelEmailAlerts,wx.ID_ANY,allow_long=False, allow_none=False,
                                             default_color=wx.BLACK, limited=False, max=65535, min=0,
                                             oob_color=wx.RED, value=25)
        self.intCtrlSMTPPort.SetBounds((0, 65535))
        self.intCtrlSMTPPort.SetToolTipString(_('Mail Server port number (0-65535)'))
        hbsizer.Add(self.intCtrlSMTPPort)

        sbsizer.Add(hbsizer,0,wx.EXPAND)

        hbsizer = wx.BoxSizer(wx.HORIZONTAL)

        t = wx.StaticText(self._panelEmailAlerts,wx.ID_ANY,_('&User Name:'))
        hbsizer.Add(t)

        self.textCtrlSMTPUser = wx.TextCtrl(self._panelEmailAlerts,wx.ID_ANY)
        self.textCtrlSMTPUser.SetToolTipString(_('Mail Server Account Name (optional)'))
        hbsizer.Add(self.textCtrlSMTPUser,1)
        sbsizer.Add(hbsizer,0,wx.EXPAND)


        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        t = wx.StaticText(self._panelEmailAlerts,wx.ID_ANY,_('&Password:'))
        hbsizer.Add(t)

        self.textCtrlSMTPPassword = wx.TextCtrl(self._panelEmailAlerts, style=wx.TE_PASSWORD)
        self.textCtrlSMTPPassword.SetToolTipString(_('Mail Server account password (optional)'))
        hbsizer.Add(self.textCtrlSMTPPassword,1)

        sbsizer.Add(hbsizer,0,wx.EXPAND)
        bsizer.Add(sbsizer,0,wx.EXPAND | wx.ALL,5)


        self.staticBoxEmailDetails = wx.StaticBox(self._panelEmailAlerts,wx.ID_ANY,_('Email Message Details'))
        sbsizer = wx.StaticBoxSizer(self.staticBoxEmailDetails,wx.VERTICAL)

        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        t = wx.StaticText(self._panelEmailAlerts,wx.ID_ANY,_('&From:'))
        hbsizer.Add(t)

        self.textCtrlSMTPFrom = wx.TextCtrl(self._panelEmailAlerts)
        self.textCtrlSMTPFrom.SetToolTipString(_('Specify an email address from which the notification will be sent.'))
        hbsizer.Add(self.textCtrlSMTPFrom,1)
        sbsizer.Add(hbsizer,0,wx.EXPAND)

        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        t = wx.StaticText(self._panelEmailAlerts,wx.ID_ANY,_('&To:'))
        hbsizer.Add(t)

        self.textCtrlSMTPTo = wx.TextCtrl(self._panelEmailAlerts)
        self.textCtrlSMTPTo.SetToolTipString(_('Specify an email address where the email alert will be delivered.  Separate multiple addresses with commas.'))
        hbsizer.Add(self.textCtrlSMTPTo,1)
        sbsizer.Add(hbsizer,0,wx.EXPAND)

        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        t = wx.StaticText(self._panelEmailAlerts,wx.ID_ANY,_('Su&bject:'))
        hbsizer.Add(t)

        self.textCtrlSMTPSubject = wx.TextCtrl(self._panelEmailAlerts)
        self.textCtrlSMTPSubject.SetToolTipString(_("Specify Recipient's email address where the email alert will be delivered"))
        hbsizer.Add(self.textCtrlSMTPSubject,1)
        sbsizer.Add(hbsizer,0,wx.EXPAND)

        bsizer.Add(sbsizer,0,wx.EXPAND|wx.ALL,5)

        self.buttonSendTestEmail = wx.Button(self._panelEmailAlerts,wx.ID_ANY,_('Send &Test Email'))
        self.buttonSendTestEmail.SetToolTipString(_('Click to send a test email message'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonSendTestEmail,self.buttonSendTestEmail)

        bsizer.Add(self.buttonSendTestEmail,0,wx.ALL,5)

        self._panelEmailAlerts.SetSizer(bsizer)

        #--------------



        #----------Panel Archives

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.checkBoxScanArchives = wx.CheckBox(self._panelArchives,wx.ID_ANY,_('&Scan In Archives'))
        self.checkBoxScanArchives.SetValue(False)
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckBoxScanArchives,self.checkBoxScanArchives)
        sizer.Add(self.checkBoxScanArchives,0,wx.ALL,5)

        fgsizer = wx.FlexGridSizer(3,3,5,5)
        self.staticTextMaxSize = wx.StaticText(self._panelArchives,wx.ID_ANY,_('Do Not Scan Archives Larger Than'))
        fgsizer.Add(self.staticTextMaxSize)
        self.spinCtrlArchiveSize = wx.SpinCtrl(self._panelArchives, initial=0, max=4096, min=1,style=wx.SP_ARROW_KEYS)
        fgsizer.Add(self.spinCtrlArchiveSize)
        self.staticTextMB1 = wx.StaticText(self._panelArchives,wx.ID_ANY,_('MegaBytes'))
        fgsizer.Add(self.staticTextMB1)
        self.staticTextLimitFiles = wx.StaticText(self._panelArchives,wx.ID_ANY,_('Do Not Extract More Than '))
        fgsizer.Add(self.staticTextLimitFiles)
        self.spinCtrlArchiveFiles = wx.SpinCtrl(self._panelArchives,wx.ID_ANY,initial=0, max=1073741824, min=1,style=wx.SP_ARROW_KEYS)
        fgsizer.Add(self.spinCtrlArchiveFiles)
        self.staticTextFiles = wx.StaticText(self._panelArchives,wx.ID_ANY,_('Files'))
        fgsizer.Add(self.staticTextFiles)
        self.staticTextRecursion = wx.StaticText(self._panelArchives,wx.ID_ANY,_('Do Not Extract More Than '))
        fgsizer.Add(self.staticTextRecursion)
        self.spinCtrlRecursion = wx.SpinCtrl(self._panelArchives,wx.ID_ANY,initial=0, max=999, min=1,style=wx.SP_ARROW_KEYS)
        fgsizer.Add(self.spinCtrlRecursion)
        self.staticTextSubArchives = wx.StaticText(self._panelArchives,wx.ID_ANY,_('Sub-Archives'))
        fgsizer.Add(self.staticTextSubArchives)

        fgsizer.AddGrowableCol(0)
        sizer.Add(fgsizer,1,wx.EXPAND|wx.ALL,5)
        self._panelArchives.SetSizer(sizer)
        
        #-------------

        #-----Panel Files    


        fgsizer = wx.FlexGridSizer(6,2)
      
        self.staticTextClamScan = wx.StaticText(self._panelFiles,wx.ID_ANY,_('&ClamScan Location:'))
        fgsizer.Add(self.staticTextClamScan,0,wx.ALL,5)
        fgsizer.Add((-1,-1)) #empty space
        self.textCtrlClamScan = wx.TextCtrl(self._panelFiles,wx.ID_ANY)
        self.textCtrlClamScan.SetToolTipString(_('Specify location of clamscan'))
        fgsizer.Add(self.textCtrlClamScan,0,wx.EXPAND|wx.ALL,5)
        self.buttonBrowseClamScan = wx.Button(self._panelFiles,wx.ID_ANY,'...', size=wx.Size(20, 20))
        self.buttonBrowseClamScan.SetToolTipString(_('Click to browse for clamscan'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonBrowseClamScan,self.buttonBrowseClamScan)
        fgsizer.Add(self.buttonBrowseClamScan,0,wx.ALL,5)

        self.staticTextFreshClam = wx.StaticText(self._panelFiles,wx.ID_ANY,_('&FreshClam Location:'))
        fgsizer.Add(self.staticTextFreshClam,0,wx.ALL,5)
        fgsizer.Add((-1,-1)) #empty space
        self.textCtrlFreshClam = wx.TextCtrl(self._panelFiles,wx.ID_ANY)
        self.textCtrlFreshClam.SetToolTipString(_('Specify location of freshclam'))
        fgsizer.Add(self.textCtrlFreshClam,0,wx.EXPAND|wx.ALL,5)
        self.buttonBrowseFreshClam = wx.Button(self._panelFiles,wx.ID_ANY,'...', size=wx.Size(20,20))
        self.buttonBrowseFreshClam.SetToolTipString(_('Click to browse for freshclam'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonBrowseFreshClam,self.buttonBrowseFreshClam)
        fgsizer.Add(self.buttonBrowseFreshClam,0,wx.ALL,5)

        self.staticTextVirDB = wx.StaticText(self._panelFiles,wx.ID_ANY,_('&Virus Database Folder:'))
        fgsizer.Add(self.staticTextVirDB,0,wx.ALL,5)
        fgsizer.Add((-1,-1)) #empty space
        self.textCtrlVirDB = wx.TextCtrl(self._panelFiles,wx.ID_ANY)
        self.textCtrlVirDB.SetToolTipString(_('Specify location of virus database files'))
        fgsizer.Add(self.textCtrlVirDB,0,wx.EXPAND|wx.ALL,5)
        self.buttonVirDB = wx.Button(self._panelFiles,wx.ID_ANY,'...', size=wx.Size(20, 20))
        self.buttonVirDB.SetToolTipString(_('Click to browse for a virus database folder'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonBrowseVirDB,self.buttonVirDB)
        fgsizer.Add(self.buttonVirDB,0,wx.ALL,5)

        fgsizer.AddGrowableCol(0)

        self._panelFiles.SetSizer(fgsizer)
        
        #----------

  

        #------------Panel Reports

        fgsizer = wx.FlexGridSizer(5,2)

        self.staticTextLogFIle = wx.StaticText(self._panelReports,wx.ID_ANY,_('&Scan Report File:'))
        fgsizer.Add(self.staticTextLogFIle,0,wx.ALL,5)
        fgsizer.Add((-1,-1)) #empty space
        self.textCtrlScanLogFile = wx.TextCtrl(self._panelReports,wx.ID_ANY)
        self.textCtrlScanLogFile.SetToolTipString(_('Specify location for a scan reports log file'))
        fgsizer.Add(self.textCtrlScanLogFile,0,wx.EXPAND|wx.ALL,5)
        self.buttonBrowseScanLog = wx.Button(self._panelReports,wx.ID_ANY,'...',size=wx.Size(20,20))
        self.buttonBrowseScanLog.SetToolTipString(_('Click to browse for a log file'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonBrowseScanLog,self.buttonBrowseScanLog)
        fgsizer.Add(self.buttonBrowseScanLog,0,wx.ALL,5)

        self.staticTextDBUpdateLogFile = wx.StaticText(self._panelReports,wx.ID_ANY,_('&Virus Database Update Report File:'))
        fgsizer.Add(self.staticTextDBUpdateLogFile,0,wx.ALL,5)
        fgsizer.Add((-1,-1)) #empty space
        self.textCtrlUpdateLogFile = wx.TextCtrl(self._panelReports,wx.ID_ANY)
        self.textCtrlUpdateLogFile.SetToolTipString(_('Specify location for a database updates log file'))
        fgsizer.Add(self.textCtrlUpdateLogFile,0,wx.EXPAND|wx.ALL,5)
        self.buttonBrowseUpdateLog = wx.Button(self._panelReports,wx.ID_ANY,'...', size=wx.Size(20, 20))
        self.buttonBrowseUpdateLog.SetToolTipString(_('Click to browse for a log file'))
        self.Bind(wx.EVT_BUTTON,self.OnButtonBrowseUpdateLog,self.buttonBrowseUpdateLog)
        fgsizer.Add(self.buttonBrowseUpdateLog,0,wx.ALL,5)

        self.checkBoxTrayNotify = wx.CheckBox(self._panelReports,wx.ID_ANY,_('&Display Pop-up Notification Messages In Taskbar '))
        self.checkBoxTrayNotify.SetToolTipString(_('Select if you wish to receive Tray notification pop-up messages'))
        fgsizer.Add(self.checkBoxTrayNotify,0,wx.ALL,5)

        fgsizer.AddGrowableCol(0)

        self._panelReports.SetSizer(fgsizer)


        #------------


        #Panel EmailScanning

        sizer = wx.BoxSizer()
        
        self.staticBoxOutlookAddin = wx.StaticBox(self._panelEmailScanning,wx.ID_ANY,_('Microsoft Outlook'))
        sbsizer = wx.StaticBoxSizer(self.staticBoxOutlookAddin,wx.VERTICAL)
        
        self.checkBoxOutlookScanIncoming = wx.CheckBox(self._panelEmailScanning,wx.ID_ANY,_('Scan &Incoming Email Messages'))
        self.checkBoxOutlookScanIncoming.SetToolTipString(_('Select if you wish to enable scanning of incoming email messages in MS Outlook'))
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckBoxOutlookAddinEnabledCheckbox,self.checkBoxOutlookScanIncoming)
        sbsizer.Add(self.checkBoxOutlookScanIncoming,0,wx.ALL,5)

        self.checkBoxOutlookScanOutgoing = wx.CheckBox(self._panelEmailScanning,wx.ID_ANY,_('Scan &Outgoing Email Messages'))
        self.checkBoxOutlookScanOutgoing.SetToolTipString(_('Select if you wish to enable scanning of outgoing email messages in MS Outlook'))
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckBoxOutlookScanOutgoingCheckbox,self.checkBoxOutlookScanOutgoing)
        sbsizer.Add(self.checkBoxOutlookScanOutgoing,0,wx.ALL,5)

        sizer.Add(sbsizer,1,wx.ALL,5)
    
        self._panelEmailScanning.SetSizer(sizer)

        #-------
 
      #--------Panel Advanced

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.checkBoxEnableMbox = wx.CheckBox(self._panelAdvanced,wx.ID_ANY,_('&Treat Files As Mailboxes'))
        self.checkBoxEnableMbox.SetToolTipString(_('Select if you wish to scan mailboxes'))
        sizer.Add(self.checkBoxEnableMbox,0,wx.ALL,5)
        self.checkBoxEnableOLE2 = wx.CheckBox(self._panelAdvanced,wx.ID_ANY,_('&Extract Attachments and Macros from MS Office Documents'))
        self.checkBoxEnableOLE2.SetToolTipString(_('Select if you wish to scan OLE attachments and macros in MS Office Documents'))
        sizer.Add(self.checkBoxEnableOLE2,0,wx.ALL,5)
        self.checkBoxScanExeOnly = wx.CheckBox(self._panelAdvanced,wx.ID_ANY,_('Try to &Scan Executable Files Only'))
        self.checkBoxScanExeOnly.SetToolTipString(_('Select if you only wish to scan files that can run on MS Windows platform'))
        sizer.Add(self.checkBoxScanExeOnly,0,wx.ALL,5)
        self.staticTextAdditionalParams = wx.StaticText(self._panelAdvanced,wx.ID_ANY,_('&Additional Clamscan Command Line Parameters:'))
        sizer.Add(self.staticTextAdditionalParams,0,wx.ALL,5)
        self.textCtrlAdditionalParams = wx.TextCtrl(self._panelAdvanced,wx.ID_ANY)
        self.textCtrlAdditionalParams.SetToolTipString(_('Specify any additional parameters for clamscan.exe'))
        sizer.Add(self.textCtrlAdditionalParams,0,wx.EXPAND|wx.ALL,5)

        gsizer = wx.GridSizer(2,3)
        self.staticTextMaxLogSize = wx.StaticText(self._panelAdvanced,wx.ID_ANY,_('Limit Log File Size To:'))
        gsizer.Add(self.staticTextMaxLogSize)
        gsizer.Add((-1,-1))
        self.staticTextPriority = wx.StaticText(self._panelAdvanced,wx.ID_ANY,_('Scanner &Priority:'))
        gsizer.Add(self.staticTextPriority)
        self.spinCtrlMaxLogSize = wx.SpinCtrl(self._panelAdvanced,wx.ID_ANY,initial=0, max=4096, min=1,style=wx.SP_ARROW_KEYS)
        self.spinCtrlMaxLogSize.SetToolTipString(_('Select maximum size for the logfile'))
        self.spinCtrlMaxLogSize.SetValue(1)
        gsizer.Add(self.spinCtrlMaxLogSize)
        self.staticTextMB2 = wx.StaticText(self._panelAdvanced,wx.ID_ANY,_('MegaBytes'))
        gsizer.Add(self.staticTextMB2)
        self.choicePriority = wx.Choice(self._panelAdvanced,wx.ID_ANY,choices=[_('Low'), _('Normal')])
        self.choicePriority.SetToolTipString(_('Specify the process priority for the virus scanner.'))
        self.choicePriority.SetStringSelection(_('Normal'))
        gsizer.Add(self.choicePriority)

        sizer.Add(gsizer,0,wx.ALL,5)

        self._panelAdvanced.SetSizer(sizer)

        #----------------





 


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
