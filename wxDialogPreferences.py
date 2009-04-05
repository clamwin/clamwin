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

import MsgBox, Utils, EmailAlert, Config
import os, sys, locale
import wxDialogScheduledScan
import wx.lib.intctrl
import wx.lib.masked
import wx.gizmos

def create(parent, config=None, switchToSchedule=False):
    return wxPreferencesDlg(parent, config, switchToSchedule)

class wxPreferencesDlg(wx.Dialog):
    def _init_coll_imageListScheduler_Images(self, parent):
        parent.Add(bitmap=wx.Bitmap('img/ListScan.png', wx.BITMAP_TYPE_PNG), mask=wx.NullBitmap)

    def _init_coll_notebook_Pages(self, parent):
        parent.AddPage(imageId=-1, page=self._panelOptions, select=True, text='General')
        parent.AddPage(imageId=-1, page=self._panelFilters, select=False, text='Filters')
        parent.AddPage(imageId=-1, page=self._panelInternetUpdate, select=False, text='Internet Updates')
        parent.AddPage(imageId=-1, page=self._panelProxy, select=False, text='Proxy')
        parent.AddPage(imageId=-1, page=self._panelScheduler, select=False, text='Scheduled Scans')
        parent.AddPage(imageId=-1, page=self._panelEmailAlerts, select=False, text='Email Alerts')
        parent.AddPage(imageId=-1, page=self._panelArchives, select=False, text='Limits')
        parent.AddPage(imageId=-1, page=self._panelFiles, select=False, text='File Locations')
        parent.AddPage(imageId=-1, page=self._panelReports, select=False, text='Reports')
        parent.AddPage(imageId=-1, page=self._panelEmailScanning, select=False, text='Email Scanning')
        parent.AddPage(imageId=-1, page=self._panelAdvanced, select=False, text='Advanced')

    def _init_coll_listViewScheduledTasks_Columns(self, parent):
        parent.InsertColumn(col=0, format=wx.LIST_FORMAT_LEFT, heading='Description', width=-1)
        parent.InsertColumn(col=1, format=wx.LIST_FORMAT_LEFT, heading='Path', width=-1)
        parent.InsertColumn(col=2, format=wx.LIST_FORMAT_LEFT, heading='Frequency', width=-1)

    def _init_utils(self):
        self.imageListScheduler = wx.ImageList(height=16, width=16)
        self._init_coll_imageListScheduler_Images(self.imageListScheduler)

    def _init_ctrls(self, prnt):
        wx.Dialog.__init__(self, name='', parent=prnt,
              pos=wx.Point(1011, 447), size=wx.Size(419, 395),
              style=wx.DEFAULT_DIALOG_STYLE, title='ClamWin Preferences')
        self._init_utils()
        self.SetClientSize(wx.Size(411, 368))
        self.SetAutoLayout(False)
        self.Center(wx.BOTH)
        wx.EVT_CHAR_HOOK(self, self.OnCharHook)
        wx.EVT_INIT_DIALOG(self, self.OnInitDialog)

        self.notebook = wx.Notebook(
              name='notebook', parent=self, pos=wx.Point(7, 7), size=wx.Size(398, 321),
              style=wx.NB_MULTILINE)
        self.notebook.SetAutoLayout(False)
        self.notebook.SetToolTipString('')

        self._panelOptions = wx.Panel(
              name='_panelOptions', parent=self.notebook, pos=wx.Point(0, 0),
              size=wx.Size(390, 277), style=wx.TAB_TRAVERSAL)
        self._panelOptions.SetAutoLayout(False)

        self._panelInternetUpdate = wx.Panel(
              name='_panelInternetUpdate', parent=self.notebook, pos=wx.Point(0, 0),
              size=wx.Size(390, 277), style=wx.TAB_TRAVERSAL)
        self._panelInternetUpdate.SetAutoLayout(False)

        self._panelProxy = wx.Panel(
              name='_panelProxy', parent=self.notebook, pos=wx.Point(0, 0),
              size=wx.Size(390, 277), style=wx.TAB_TRAVERSAL)
        self._panelProxy.SetAutoLayout(False)

        self._panelFiles = wx.Panel(
              name='_panelFiles', parent=self.notebook, pos=wx.Point(0, 0),
              size=wx.Size(390, 277), style=wx.TAB_TRAVERSAL)
        self._panelFiles.SetAutoLayout(False)

        self._panelArchives = wx.Panel(
              name='_panelArchives', parent=self.notebook, pos=wx.Point(0, 0),
              size=wx.Size(390, 277), style=wx.TAB_TRAVERSAL)
        self._panelArchives.SetAutoLayout(False)

        self._panelReports = wx.Panel(
              name='_panelReports', parent=self.notebook, pos=wx.Point(0, 0),
              size=wx.Size(390, 277), style=wx.TAB_TRAVERSAL)
        self._panelReports.SetAutoLayout(False)

        self._panelEmailScanning = wx.Panel(
              name='_panelEmailScanning', parent=self.notebook, pos=wx.Point(0, 0),
              size=wx.Size(390, 277), style=wx.TAB_TRAVERSAL)

        self._panelAdvanced = wx.Panel(
              name='_panelAdvanced', parent=self.notebook, pos=wx.Point(0, 0),
              size=wx.Size(390, 277), style=wx.TAB_TRAVERSAL)
        self._panelAdvanced.SetAutoLayout(False)

        self.buttonOK = wx.Button(label='OK',
              name='buttonOK', parent=self, pos=wx.Point(128, 338),
              size=wx.Size(72, 23), style=0)
        self.buttonOK.SetToolTipString('Closes the window and saves the changes')
        self.buttonOK.SetDefault()
        self.buttonOK.Bind(wx.EVT_BUTTON, self.OnOK)

        self.buttonCancel = wx.Button(
              label='Cancel', name='buttonCancel', parent=self, pos=wx.Point(209, 338),
              size=wx.Size(75, 23), style=0)
        self.buttonCancel.SetToolTipString('Closes the window without saving the changes')
        self.buttonCancel.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.staticTextProxyHost = wx.StaticText(
              label='Proxy &Server:', name='staticTextProxyHost',
              parent=self._panelProxy, pos=wx.Point(6, 61), size=wx.Size(80, 15), style=0)

        self.textCtrlProxyHost = wx.TextCtrl(
              name='textCtrlProxyHost', parent=self._panelProxy, pos=wx.Point(91, 57),
              size=wx.Size(199, 21), style=0, value='')
        self.textCtrlProxyHost.SetToolTipString('Proxy Server domain name or IP address')

        self.staticTextProxyPort = wx.StaticText(
              label='P&ort:', name='staticTextProxyPort',
              parent=self._panelProxy, pos=wx.Point(296, 61), size=wx.Size(34, 15), style=0)

        self.intCtrlProxyPort = wx.lib.intctrl.IntCtrl(allow_long=False, allow_none=False,
              default_color=wx.BLACK,
              limited=False, max=65535, min=0, name='intCtrlProxyPort',
              oob_color=wx.RED, parent=self._panelProxy, pos=wx.Point(332, 57),
              size=wx.Size(54, 21), style=0, value=3128)
        self.intCtrlProxyPort.SetBounds((0, 65535))
        self.intCtrlProxyPort.SetToolTipString('Proxy Server port number (0-65535)')

        self.staticTextProxyUser = wx.StaticText(
              label='&User Name:', name='staticTextProxyUser',
              parent=self._panelProxy, pos=wx.Point(6, 97), size=wx.Size(80, 15), style=0)

        self.textCtrlProxyUser = wx.TextCtrl(
              name='textCtrlProxyUser', parent=self._panelProxy, pos=wx.Point(91, 93),
              size=wx.Size(295, 21), style=0, value='')
        self.textCtrlProxyUser.SetToolTipString('Proxy Server Account Name (optional)')

        self.staticTextProxyPassword = wx.StaticText(
              label='&Password:', name='staticTextProxyPassword',
              parent=self._panelProxy, pos=wx.Point(6, 135), size=wx.Size(80, 15), style=0)

        self.textCtrlProxyPassword = wx.TextCtrl(
              name='textCtrlProxyPassword', parent=self._panelProxy,
              pos=wx.Point(91, 131), size=wx.Size(295, 21), style=wx.TE_PASSWORD, value='')
        self.textCtrlProxyPassword.SetToolTipString('Proxy Server account password (optional)')

        self.staticTextExplain = wx.StaticText(
              label='Leave these fields blank if you do not connect via Proxy Server',
              name='staticTextExplain', parent=self._panelProxy, pos=wx.Point(6, 15),
              size=wx.Size(378, 27), style=0)
        self.staticTextExplain.SetToolTipString('')

        self.staticBoxScanOptions = wx.StaticBox(
              label='Scanning Options', name='staticBoxScanOptions',
              parent=self._panelOptions, pos=wx.Point(6, 11), size=wx.Size(376, 90), style=0)

        self.checkBoxEnableAutoUpdate = wx.CheckBox(
              label='&Enable Automatic Virus Database Updates',
              name='checkBoxEnableAutoUpdate', parent=self._panelInternetUpdate,
              pos=wx.Point(6, 11), size=wx.Size(322, 20), style=0)
        self.checkBoxEnableAutoUpdate.SetToolTipString('Enable automatic virus database downloads')
        self.checkBoxEnableAutoUpdate.Bind(wx.EVT_CHECKBOX, self.OnCheckBoxEnableAutoUpdate)

        self.staticText1 = wx.StaticText(
              label='Download &Site :', name='staticText1',
              parent=self._panelInternetUpdate, pos=wx.Point(24, 43),
              size=wx.Size(81, 13), style=0)

        self.textCtrlDBMirror = wx.TextCtrl(
              name='textCtrlDBMirror', parent=self._panelInternetUpdate,
              pos=wx.Point(126, 37), size=wx.Size(243, 21), style=0, value='')
        self.textCtrlDBMirror.SetToolTipString('Specify Database Mirror Site here. Usually this is database.clamav.net')

        self.staticTextUpdateFrequency = wx.StaticText(
              label='&Update Frequency:', name='staticTextUpdateFrequency',
              parent=self._panelInternetUpdate, pos=wx.Point(23, 70),
              size=wx.Size(98, 18), style=0)
        self.staticTextUpdateFrequency.SetToolTipString('')

        self.choiceUpdateFrequency = wx.Choice(choices=['Hourly', 'Daily',
              'Workdays', 'Weekly'],
              name='choiceUpdateFrequency', parent=self._panelInternetUpdate,
              pos=wx.Point(126, 67), size=wx.Size(110, 21), style=0)
        self.choiceUpdateFrequency.SetToolTipString('How often virus database is downloaded')
        self.choiceUpdateFrequency.SetStringSelection('Daily')
        self.choiceUpdateFrequency.Bind(wx.EVT_CHOICE, self.OnChoiceUpdateFrequency)

        self.staticTextClamScan = wx.StaticText(
              label='&ClamScan Location:', name='staticTextClamScan',
              parent=self._panelFiles, pos=wx.Point(6, 15), size=wx.Size(354, 13), style=0)
        self.staticTextClamScan.SetToolTipString('')

        self.textCtrlClamScan = wx.TextCtrl(
              name='textCtrlClamScan', parent=self._panelFiles, pos=wx.Point(6, 33),
              size=wx.Size(356, 20), style=0, value='')
        self.textCtrlClamScan.SetToolTipString('Specify location of clamscan')

        self.buttonBrowseClamScan = wx.Button(
              label='...', name='buttonBrowseClamScan', parent=self._panelFiles,
              pos=wx.Point(363, 34), size=wx.Size(20, 20), style=0)
        self.buttonBrowseClamScan.SetToolTipString('Click to browse for clamscan')
        self.buttonBrowseClamScan.Bind(wx.EVT_BUTTON, self.OnButtonBrowseClamScan)

        self.staticTextFreshClam = wx.StaticText(
              label='&FreshClam Location:', name='staticTextFreshClam',
              parent=self._panelFiles, pos=wx.Point(6, 65), size=wx.Size(354, 13), style=0)
        self.staticTextFreshClam.SetToolTipString('')

        self.textCtrlFreshClam = wx.TextCtrl(
              name='textCtrlFreshClam', parent=self._panelFiles, pos=wx.Point(6, 83),
              size=wx.Size(355, 20), style=0, value='')
        self.textCtrlFreshClam.SetToolTipString('Specify location of freshclam')

        self.buttonBrowseFreshClam = wx.Button(
              label='...', name='buttonBrowseFreshClam',
              parent=self._panelFiles, pos=wx.Point(363, 83), size=wx.Size(20, 20), style=0)
        self.buttonBrowseFreshClam.SetToolTipString('Click to browse for freshclam')
        self.buttonBrowseFreshClam.Bind(wx.EVT_BUTTON, self.OnButtonBrowseFreshClam)

        self.staticTextVirDB = wx.StaticText(
              label='&Virus Database Folder:', name='staticTextVirDB',
              parent=self._panelFiles, pos=wx.Point(6, 115), size=wx.Size(354, 13), style=0)
        self.staticTextVirDB.SetToolTipString('')

        self.textCtrlVirDB = wx.TextCtrl(
              name='textCtrlVirDB', parent=self._panelFiles, pos=wx.Point(6, 133),
              size=wx.Size(355, 20), style=0, value='')
        self.textCtrlVirDB.SetToolTipString('Specify location of virus database files')

        self.buttonVirDB = wx.Button(
              label='...', name='buttonVirDB', parent=self._panelFiles,
              pos=wx.Point(362, 133), size=wx.Size(20, 20), style=0)
        self.buttonVirDB.SetToolTipString('Click to browse for a virus database folder')
        self.buttonVirDB.Bind(wx.EVT_BUTTON, self.OnButtonBrowseVirDB)

        self.checkBoxScanRecursive = wx.CheckBox(
              label='&Scan in Subdirectories', name='checkBoxScanRecursive',
              parent=self._panelOptions, pos=wx.Point(15, 53), size=wx.Size(354, 18), style=0)
        self.checkBoxScanRecursive.SetToolTipString('Select if you wish to scan in subdirectories recursively')
        self.checkBoxScanRecursive.SetValue(False)

        self.staticTextUpdateTime = wx.StaticText(
              label='&Time:', name='staticTextUpdateTime',
              parent=self._panelInternetUpdate, pos=wx.Point(240, 70),
              size=wx.Size(33, 18), style=0)

        self.spinButtonUpdateTime = wx.SpinButton(
              name='spinButtonUpdateTime', parent=self._panelInternetUpdate,
              pos=wx.Point(353, 65), size=wx.Size(16, 23),
              style=wx.SP_ARROW_KEYS | wx.SP_VERTICAL)
        self.spinButtonUpdateTime.SetToolTipString('')

        self.spinCtrlMaxFileSize = wx.SpinCtrl(
              initial=0, max=4096, min=1, name='spinCtrlMaxFileSize',
              parent=self._panelArchives, pos=wx.Point(205, 29), size=wx.Size(72, 21), style=wx.SP_ARROW_KEYS)

        self.staticTextFileSize = wx.StaticText(
              label='Do Not Scan Files Larger Than', name='staticTextFileSize',
              parent=self._panelArchives, pos=wx.Point(24, 32), size=wx.Size(166, 13), style=0)

        self.staticBox1 = wx.StaticBox(
              label='All Files', name='staticBox1', parent=self._panelArchives,
              pos=wx.Point(6, 8), size=wx.Size(377, 56), style=0)

        self.staticTextFileSizeMB = wx.StaticText(
              label='MegaBytes', name='staticTextFileSizeMB',
              parent=self._panelArchives, pos=wx.Point(293, 32), size=wx.Size(80, 16), style=0)

        self.staticBox2 = wx.StaticBox(
              label='Archives', name='staticBox2', parent=self._panelArchives,
              pos=wx.Point(6, 78), size=wx.Size(377, 162), style=0)

        self.checkBoxScanArchives = wx.CheckBox(
              label='&Extract Files From Archives', name='checkBoxScanArchives',
              parent=self._panelArchives, pos=wx.Point(14, 102), size=wx.Size(322, 20), style=0)
        self.checkBoxScanArchives.SetValue(False)
        self.checkBoxScanArchives.SetToolTipString('Select if you wish to scan files conatined in archives (zip, rar, etc)')
        self.checkBoxScanArchives.Bind(wx.EVT_CHECKBOX, self.OnCheckBoxScanArchives)

        self.staticTextMaxSize = wx.StaticText(
              label='Do Not Extract More Than ', name='staticTextMaxSize',
              parent=self._panelArchives, pos=wx.Point(24, 136), size=wx.Size(160, 13), style=0)

        self.spinCtrlArchiveSize = wx.SpinCtrl(
              initial=0, max=4096, min=1, name='spinCtrlArchiveSize',
              parent=self._panelArchives, pos=wx.Point(205, 134), size=wx.Size(72, 21), style=wx.SP_ARROW_KEYS)

        self.staticTextMB1 = wx.StaticText(
              label='MegaBytes', name='staticTextMB1',
              parent=self._panelArchives, pos=wx.Point(293, 136), size=wx.Size(80, 16), style=0)

        self.staticTextLimitFiles = wx.StaticText(
              label='Do Not Extract More Than ', name='staticTextLimitFiles',
              parent=self._panelArchives, pos=wx.Point(24, 169), size=wx.Size(168, 17), style=0)

        self.checkBoxEnableMbox = wx.CheckBox(
              label='&Treat Files As Mailboxes', name='checkBoxEnableMbox',
              parent=self._panelAdvanced, pos=wx.Point(6, 11), size=wx.Size(384, 18), style=0)
        self.checkBoxEnableMbox.SetToolTipString('Select if you wish to scan mailboxes')
        self.checkBoxEnableMbox.SetValue(False)

        self.checkBoxEnableOLE2 = wx.CheckBox(
              label='&Extract Attachments and Macros from MS Office Documents',
              name='checkBoxEnableOLE2', parent=self._panelAdvanced,
              pos=wx.Point(6, 33), size=wx.Size(381, 18), style=0)
        self.checkBoxEnableOLE2.SetToolTipString('Select if you wish to scan OLE attachments and macros in MS Office Documents')
        self.checkBoxEnableOLE2.SetValue(False)

        self.staticTextAdditionalParams = wx.StaticText(
              label='&Additional Clamscan Command Line Parameters:',
              name='staticTextAdditionalParams', parent=self._panelAdvanced,
              pos=wx.Point(6, 108), size=wx.Size(378, 13), style=0)

        self.textCtrlAdditionalParams = wx.TextCtrl(
              name='textCtrlAdditionalParams', parent=self._panelAdvanced,
              pos=wx.Point(6, 126), size=wx.Size(379, 21), style=0, value='')
        self.textCtrlAdditionalParams.SetToolTipString('Specify any additional parameters for clamscan.exe')

        self.staticTextMaxLogSize = wx.StaticText(
              label='Limit Log File Size To:', name='staticTextMaxLogSize',
              parent=self._panelAdvanced, pos=wx.Point(6, 165), size=wx.Size(170, 17), style=0)

        self.staticTextLogFIle = wx.StaticText(
              label='&Scan Report File:', name='staticTextLogFIle',
              parent=self._panelReports, pos=wx.Point(6, 15), size=wx.Size(354, 19), style=0)
        self.staticTextLogFIle.SetToolTipString('')

        self.textCtrlScanLogFile = wx.TextCtrl(
              name='textCtrlScanLogFile', parent=self._panelReports,
              pos=wx.Point(6, 35), size=wx.Size(360, 20), style=0, value='')
        self.textCtrlScanLogFile.SetToolTipString('Specify location for a scan reports log file')

        self.buttonBrowseScanLog = wx.Button(
              label='...', name='buttonBrowseScanLog',
              parent=self._panelReports, pos=wx.Point(366, 35), size=wx.Size(20,
              20), style=0)
        self.buttonBrowseScanLog.SetToolTipString('Click to browse for a log file')
        self.buttonBrowseScanLog.Bind(wx.EVT_BUTTON, self.OnButtonBrowseScanLog)

        self.staticTextDBUpdateLogFile = wx.StaticText(
              label='&Virus Database Update Report File:',
              name='staticTextDBUpdateLogFile', parent=self._panelReports,
              pos=wx.Point(6, 66), size=wx.Size(354, 19), style=0)
        self.staticTextDBUpdateLogFile.SetToolTipString('')

        self.textCtrlUpdateLogFile = wx.TextCtrl(
              name='textCtrlUpdateLogFile', parent=self._panelReports,
              pos=wx.Point(6, 86), size=wx.Size(360, 20), style=0, value='')
        self.textCtrlUpdateLogFile.SetToolTipString('Specify location for a database updates log file')

        self.buttonBrowseUpdateLog = wx.Button(
              label='...', name='buttonBrowseUpdateLog',
              parent=self._panelReports, pos=wx.Point(366, 86), size=wx.Size(20, 20), style=0)
        self.buttonBrowseUpdateLog.SetToolTipString('Click to browse for a log file')
        self.buttonBrowseUpdateLog.Bind(wx.EVT_BUTTON, self.OnButtonBrowseUpdateLog)

        self.staticLineUpdateTimeCtrl = wx.StaticLine(
              name='staticLineUpdateTimeCtrl', parent=self._panelInternetUpdate,
              pos=wx.Point(277, 66), size=wx.Size(74, 22), style=0)
        self.staticLineUpdateTimeCtrl.Show(False)
        self.staticLineUpdateTimeCtrl.SetToolTipString('When the download should be started')

        self.staticTextUpdateDay = wx.StaticText(
              label='&Day Of The Week:', name='staticTextUpdateDay',
              parent=self._panelInternetUpdate, pos=wx.Point(23, 104),
              size=wx.Size(96, 18), style=0)
        self.staticTextUpdateDay.SetToolTipString('')

        self._panelScheduler = wx.Panel(
              name='_panelScheduler', parent=self.notebook, pos=wx.Point(0, 0),
              size=wx.Size(390, 277), style=wx.TAB_TRAVERSAL)
        self._panelScheduler.SetToolTipString('')

        self.listViewScheduledTasks = wx.ListView(
              name='listViewScheduledTasks', parent=self._panelScheduler,
              pos=wx.Point(6, 41), size=wx.Size(298, 187),
              style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.listViewScheduledTasks.SetToolTipString('List of Scheduled Scans')
        self.listViewScheduledTasks.SetImageList(self.imageListScheduler, wx.IMAGE_LIST_NORMAL)
        self.listViewScheduledTasks.SetImageList(self.imageListScheduler, wx.IMAGE_LIST_SMALL)
        self._init_coll_listViewScheduledTasks_Columns(self.listViewScheduledTasks)
        self.listViewScheduledTasks.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnScheduledTasksUpdate)
        self.listViewScheduledTasks.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnScheduledTasksUpdate)
        self.listViewScheduledTasks.Bind(wx.EVT_LEFT_DCLICK, self.OnButtonEditScheduledScan)

        self.staticTextScheduledTasks = wx.StaticText(
              label='Scheduled Scans:', name='staticTextScheduledTasks',
              parent=self._panelScheduler, pos=wx.Point(6, 14), size=wx.Size(154, 16), style=0)
        self.staticTextScheduledTasks.SetToolTipString('')

        self.buttonTaskAdd = wx.Button(
              label='&Add', name='buttonTaskAdd', parent=self._panelScheduler,
              pos=wx.Point(311, 41), size=wx.Size(75, 23), style=0)
        self.buttonTaskAdd.Bind(wx.EVT_BUTTON, self.OnButtonAddScheduledScan)

        self.buttonTaskRemove = wx.Button(
              label='&Remove', name='buttonTaskRemove',
              parent=self._panelScheduler, pos=wx.Point(311, 81), size=wx.Size(75, 23), style=0)
        self.buttonTaskRemove.Bind(wx.EVT_BUTTON, self.OnButtonRemoveScheduledScan)

        self.buttonTaskEdit = wx.Button(
              label='&Edit', name='buttonTaskEdit', parent=self._panelScheduler,
              pos=wx.Point(311, 122), size=wx.Size(75, 23), style=0)
        self.buttonTaskEdit.Bind(wx.EVT_BUTTON, self.OnButtonEditScheduledScan)

        self.checkBoxInfectedOnly = wx.CheckBox(
              label='&Display Infected Files Only', name='checkBoxInfectedOnly',
              parent=self._panelOptions, pos=wx.Point(15, 32), size=wx.Size(354, 18), style=0)
        self.checkBoxInfectedOnly.SetValue(False)
        self.checkBoxInfectedOnly.SetToolTipString('Select if you wish to display infected files only in the scan progress window')

        self.choiceUpdateDay = wx.Choice(choices=['Monday', 'Tuesday',
              'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
              name='choiceUpdateDay',
              parent=self._panelInternetUpdate, pos=wx.Point(126, 101),
              size=wx.Size(110, 21), style=0)

        self.choiceUpdateDay.SetToolTipString('When update frequency is weekly select day of the week for an update')
        self.choiceUpdateDay.SetStringSelection('Tuesday')

        self.checkBoxWarnDBOld = wx.CheckBox(
              label='&Warn if Virus database is Out of Date',
              name='checkBoxWarnDBOld', parent=self._panelInternetUpdate,
              pos=wx.Point(6, 143), size=wx.Size(322, 20), style=0)
        self.checkBoxWarnDBOld.SetToolTipString('Will display a reminder if the virus database is older than 5 days')
        self.checkBoxWarnDBOld.SetValue(False)
        self.checkBoxWarnDBOld.Bind(wx.EVT_CHECKBOX, self.OnCheckBoxWarnDBOld)

        self.staticBoxInfected = wx.StaticBox(
              label='Infected Files', name='staticBoxInfected',
              parent=self._panelOptions, pos=wx.Point(6, 108), size=wx.Size(376, 133), style=0)

        self.radioButtonReport = wx.RadioButton(
              label='&Report Only', name='radioButtonReport',
              parent=self._panelOptions, pos=wx.Point(15, 129), size=wx.Size(354, 18), style=0)
        self.radioButtonReport.SetValue(False)
        self.radioButtonReport.Bind(wx.EVT_RADIOBUTTON, self.OnRadioInfected)

        self.radioButtonRemoveInfected = wx.RadioButton(
              label='R&emove (Use Carefully)', name='radioButtonRemoveInfected',
              parent=self._panelOptions, pos=wx.Point(15, 147), size=wx.Size(354, 18), style=0)
        self.radioButtonRemoveInfected.SetValue(False)
        self.radioButtonRemoveInfected.Bind(wx.EVT_RADIOBUTTON, self.OnRadioInfected)

        self.radioButtonQuarantine = wx.RadioButton(
              label='&Move To Quarantine Folder:', name='radioButtonQuarantine',
              parent=self._panelOptions, pos=wx.Point(15, 166), size=wx.Size(354, 18), style=0)
        self.radioButtonQuarantine.SetValue(False)
        self.radioButtonQuarantine.Bind(wx.EVT_RADIOBUTTON, self.OnRadioInfected)

        self.textCtrlQuarantine = wx.TextCtrl(
              name='textCtrlQuarantine', parent=self._panelOptions,
              pos=wx.Point(31, 186), size=wx.Size(319, 20), style=0, value='')
        self.textCtrlQuarantine.SetToolTipString('Specify location for a quarantine folder')

        self.buttonBrowseQuarantine = wx.Button(
              label='...', name='buttonBrowseQuarantine',
              parent=self._panelOptions, pos=wx.Point(351, 186), size=wx.Size(20, 20), style=0)
        self.buttonBrowseQuarantine.SetToolTipString('Click to browse for a quarantine folder')
        self.buttonBrowseQuarantine.Bind(wx.EVT_BUTTON, self.OnButtonBrowseQuarantine)

        self._panelEmailAlerts = wx.Panel(
              name='_panelEmailAlerts', parent=self.notebook, pos=wx.Point(0, 0),
              size=wx.Size(390, 277), style=wx.TAB_TRAVERSAL)
        self._panelEmailAlerts.SetToolTipString('')

        self.checkBoxSMTPEnable = wx.CheckBox(
              label='&Send Email Alert On Virus Detection',
              name='checkBoxSMTPEnable', parent=self._panelEmailAlerts,
              pos=wx.Point(6, 11), size=wx.Size(362, 15), style=0)
        self.checkBoxSMTPEnable.SetValue(False)
        self.checkBoxSMTPEnable.SetToolTipString('Select if you wish to receive email alerts when ClamWin detects a virus')
        self.checkBoxSMTPEnable.Bind(wx.EVT_CHECKBOX, self.OnCheckBoxSMTPEnable)

        self.staticBoxSMTPConnection = wx.StaticBox(
              label='SMTP Connection Details', name='staticBoxSMTPConnection',
              parent=self._panelEmailAlerts, pos=wx.Point(16, 32),
              size=wx.Size(368, 71), style=0)
        self.staticBoxSMTPConnection.SetToolTipString('')

        self.staticTextSMTPHost = wx.StaticText(
              label='&Mail Server:', name='staticTextSMTPHost',
              parent=self._panelEmailAlerts, pos=wx.Point(24, 54),
              size=wx.Size(71, 16), style=0)
        self.staticTextSMTPHost.SetToolTipString('')

        self.textCtrlSMTPHost = wx.TextCtrl(
              name='textCtrlSMTPHost', parent=self._panelEmailAlerts,
              pos=wx.Point(104, 51), size=wx.Size(192, 21), style=0, value='')
        self.textCtrlSMTPHost.SetToolTipString('SMTP Server domain name or IP address')

        self.staticTextSMTPPort = wx.StaticText(
              label='P&ort:', name='staticTextSMTPPort',
              parent=self._panelEmailAlerts, pos=wx.Point(300, 54),
              size=wx.Size(31, 16), style=0)

        self.intCtrlSMTPPort = wx.lib.intctrl.IntCtrl(allow_long=False, allow_none=False,
              default_color=wx.BLACK,
              limited=False, max=65535, min=0, name='intCtrlSMTPPort',
              oob_color=wx.RED, parent=self._panelEmailAlerts, pos=wx.Point(330,
              51), size=wx.Size(47, 21), style=0, value=25)
        self.intCtrlSMTPPort.SetBounds((0, 65535))
        self.intCtrlSMTPPort.SetToolTipString('Mail Server port number (0-65535)')

        self.staticTextSMTPUserName = wx.StaticText(
              label='&User Name:', name='staticTextSMTPUserName',
              parent=self._panelEmailAlerts, pos=wx.Point(24, 77),
              size=wx.Size(79, 16), style=0)
        self.staticTextSMTPUserName.SetToolTipString('')

        self.textCtrlSMTPUser = wx.TextCtrl(
              name='textCtrlSMTPUser', parent=self._panelEmailAlerts,
              pos=wx.Point(104, 74), size=wx.Size(101, 21), style=0, value='')
        self.textCtrlSMTPUser.SetToolTipString('Mail Server Account Name (optional)')

        self.staticTextSMTPPassword = wx.StaticText(
              label='&Password:', name='staticTextSMTPPassword',
              parent=self._panelEmailAlerts, pos=wx.Point(209, 77),
              size=wx.Size(66, 16), style=0)
        self.staticTextSMTPPassword.SetToolTipString('')

        self.textCtrlSMTPPassword = wx.TextCtrl(
              name='textCtrlSMTPPassword', parent=self._panelEmailAlerts,
              pos=wx.Point(276, 74), size=wx.Size(101, 21), style=wx.TE_PASSWORD, value='')
        self.textCtrlSMTPPassword.SetToolTipString('Mail Server account password (optional)')

        self.staticBoxEmailDetails = wx.StaticBox(
              label='Email Message Details', name='staticBoxEmailDetails',
              parent=self._panelEmailAlerts, pos=wx.Point(16, 113),
              size=wx.Size(368, 96), style=0)
        self.staticBoxEmailDetails.SetToolTipString('')

        self.staticTextSMTPFrom = wx.StaticText(
              label='&From:', name='staticTextSMTPFrom',
              parent=self._panelEmailAlerts, pos=wx.Point(24, 135),
              size=wx.Size(63, 16), style=0)
        self.staticTextSMTPFrom.SetToolTipString('')

        self.textCtrlSMTPFrom = wx.TextCtrl(
              name='textCtrlSMTPFrom', parent=self._panelEmailAlerts,
              pos=wx.Point(104, 129), size=wx.Size(273, 21), style=0, value='')
        self.textCtrlSMTPFrom.SetToolTipString('Specify an email address from which the notification will be sent.')

        self.staticTextSMTPTo = wx.StaticText(
              label='&To:', name='staticTextSMTPTo',
              parent=self._panelEmailAlerts, pos=wx.Point(24, 159),
              size=wx.Size(63, 16), style=0)
        self.staticTextSMTPTo.SetToolTipString('')

        self.textCtrlSMTPTo = wx.TextCtrl(
              name='textCtrlSMTPTo', parent=self._panelEmailAlerts,
              pos=wx.Point(104, 154), size=wx.Size(273, 21), style=0, value='')
        self.textCtrlSMTPTo.SetToolTipString('Specify an email address where the email alert will be delivered.  Separate multiple addresses with commas.')

        self.staticTextSMTPSubject = wx.StaticText(
              label='Su&bject:', name='staticTextSMTPSubject',
              parent=self._panelEmailAlerts, pos=wx.Point(24, 182),
              size=wx.Size(63, 16), style=0)
        self.staticTextSMTPSubject.SetToolTipString('')

        self.textCtrlSMTPSubject = wx.TextCtrl(
              name='textCtrlSMTPSubject', parent=self._panelEmailAlerts,
              pos=wx.Point(104, 178), size=wx.Size(273, 21), style=0, value='')
        self.textCtrlSMTPSubject.SetToolTipString("Specify Recipient's email address where the email alert will be delivered")

        self.buttonSendTestEmail = wx.Button(
              label='Send &Test Email', name='buttonSendTestEmail',
              parent=self._panelEmailAlerts, pos=wx.Point(120, 220),
              size=wx.Size(149, 23), style=0)
        self.buttonSendTestEmail.SetToolTipString('Click to send a test email message')
        self.buttonSendTestEmail.Bind(wx.EVT_BUTTON, self.OnButtonSendTestEmail)

        self.checkBoxTrayNotify = wx.CheckBox(
              label='&Display Pop-up Notification Messages In Taskbar ',
              name='checkBoxTrayNotify', parent=self._panelReports,
              pos=wx.Point(6, 123), size=wx.Size(354, 18), style=0)
        self.checkBoxTrayNotify.SetValue(False)
        self.checkBoxTrayNotify.SetToolTipString('Select if you wish to receive Tray notification pop-up messages')

        self._panelFilters = wx.Panel(
              name='_panelFilters', parent=self.notebook, pos=wx.Point(0, 0),
              size=wx.Size(390, 277), style=wx.TAB_TRAVERSAL)

        self.staticTextFiltreDesc1 = wx.StaticText(
              label='Specify Filename Patterns to include and/or exclude in scanning',
              name='staticTextFiltreDesc1', parent=self._panelFilters,
              pos=wx.Point(6, 11), size=wx.Size(383, 16), style=0)

        self.staticText2 = wx.StaticText(
              label='(To specify a regular expression include your pattern within <...>)',
              name='staticText2', parent=self._panelFilters, pos=wx.Point(6, 28),
              size=wx.Size(382, 16), style=0)

        self.staticTextFiltersExclude = wx.StaticText(
              label='&Exclude Matching Filenames:',
              name='staticTextFiltersExclude', parent=self._panelFilters,
              pos=wx.Point(6, 50), size=wx.Size(184, 16), style=0)

        self.editableListBoxFiltersExclude = wx.gizmos.EditableListBox(
              label='Patterns', name='editableListBoxFiltersExclude',
              parent=self._panelFilters, pos=wx.Point(6, 69), size=wx.Size(182, 171))

        self.staticTextFiltersInclude = wx.StaticText(
              label='&Scan Only Matching Filenames:',
              name='staticTextFiltersInclude', parent=self._panelFilters,
              pos=wx.Point(202, 51), size=wx.Size(187, 16), style=0)

        self.editableListBoxFiltersInclude = wx.gizmos.EditableListBox(
              label='Patterns', name='editableListBoxFiltersInclude',
              parent=self._panelFilters, pos=wx.Point(200, 69), size=wx.Size(184,
              171))

        self.buttonTaskDeactivate = wx.Button(
              label='&Deactivate', name='buttonTaskDeactivate',
              parent=self._panelScheduler, pos=wx.Point(311, 204),
              size=wx.Size(75, 23), style=0)
        self.buttonTaskDeactivate.Bind(wx.EVT_BUTTON, self.OnButtonTaskDeactivate)

        self.buttonTaskActivate = wx.Button(
              label='A&ctivate', name='buttonTaskActivate',
              parent=self._panelScheduler, pos=wx.Point(311, 163),
              size=wx.Size(75, 23), style=0)
        self.buttonTaskActivate.Bind(wx.EVT_BUTTON, self.OnButtonTaskActivate)

        self.checkBoxUpdateLogon = wx.CheckBox(
              label='&Update Virus Database On Logon',
              name='checkBoxUpdateLogon', parent=self._panelInternetUpdate,
              pos=wx.Point(6, 171), size=wx.Size(322, 20), style=0)
        self.checkBoxUpdateLogon.SetToolTipString('Select if you wish to update the virus databases just after you logged on')
        self.checkBoxUpdateLogon.SetValue(False)
        self.checkBoxUpdateLogon.Bind(wx.EVT_CHECKBOX, self.OnCheckBoxEnableAutoUpdate)

        self.checkBoxCheckVersion = wx.CheckBox(
              label='&Notify About New ClamWin Releases',
              name='checkBoxCheckVersion', parent=self._panelInternetUpdate,
              pos=wx.Point(6, 198), size=wx.Size(322, 20), style=0)
        self.checkBoxCheckVersion.SetToolTipString('Select if you wish to get a notification message when ClamWin Free Antivirus program has been updated')
        self.checkBoxCheckVersion.SetValue(False)
        self.checkBoxCheckVersion.Bind(wx.EVT_CHECKBOX, self.OnCheckBoxCheckVersionCheckbox)

        self.spinCtrlMaxLogSize = wx.SpinCtrl(
              initial=0, max=4096, min=1, name='spinCtrlMaxLogSize',
              parent=self._panelAdvanced, pos=wx.Point(6, 184), size=wx.Size(129, 21), style=wx.SP_ARROW_KEYS)
        self.spinCtrlMaxLogSize.SetToolTipString('Select maximum size for the logfile')
        self.spinCtrlMaxLogSize.SetValue(1)

        self.staticTextMB2 = wx.StaticText(
              label='MegaBytes', name='staticTextMB2',
              parent=self._panelAdvanced, pos=wx.Point(144, 185), size=wx.Size(74, 16), style=0)

        self.staticTextPriority = wx.StaticText(
              label='Scanner &Priority:', name='staticTextPriority',
              parent=self._panelAdvanced, pos=wx.Point(252, 165),
              size=wx.Size(103, 17), style=0)

        self.checkBoxShowProgress = wx.CheckBox(
              label='Display &File Scanned % Progress Indicator',
              name='checkBoxShowProgress', parent=self._panelOptions,
              pos=wx.Point(15, 76), size=wx.Size(354, 17), style=0)
        self.checkBoxShowProgress.SetValue(False)
        self.checkBoxShowProgress.SetToolTipString('Select if you wish to display infected files only in the scan progress window')

        self.checkBoxUnload = wx.CheckBox(
              label='&Unload Infected Programs from Computer Memory',
              name='checkBoxUnload', parent=self._panelOptions, pos=wx.Point(15,
              213), size=wx.Size(354, 17), style=0)
        self.checkBoxUnload.SetValue(False)
        self.checkBoxUnload.SetToolTipString('Select if you wish to unload infected programs from computer memory so they can be quarantined or removed')

        self.staticBoxOutlookAddin = wx.StaticBox(
              label='Microsoft Outlook', name='staticBoxOutlookAddin',
              parent=self._panelEmailScanning, pos=wx.Point(6, 11),
              size=wx.Size(376, 101), style=0)

        self.checkBoxOutlookScanIncoming = wx.CheckBox(
              label='Scan &Incoming Email Messages',
              name='checkBoxOutlookScanIncoming',
              parent=self._panelEmailScanning, pos=wx.Point(15, 32),
              size=wx.Size(354, 18), style=0)
        self.checkBoxOutlookScanIncoming.SetValue(False)
        self.checkBoxOutlookScanIncoming.SetToolTipString('Select if you wish to enable scanning of incoming email messages in MS Outlook')
        self.checkBoxOutlookScanIncoming.Bind(wx.EVT_CHECKBOX, self.OnCheckBoxOutlookScanIncomingCheckbox)

        self.checkBoxOutlookScanOutgoing = wx.CheckBox(
              label='Scan &Outgoing Email Messages',
              name='checkBoxOutlookScanOutgoing',
              parent=self._panelEmailScanning, pos=wx.Point(15, 57),
              size=wx.Size(354, 18), style=0)
        self.checkBoxOutlookScanOutgoing.SetValue(False)
        self.checkBoxOutlookScanOutgoing.SetToolTipString('Select if you wish to enable scanning of outgoing email messages in MS Outlook')
        self.checkBoxOutlookScanOutgoing.Bind(wx.EVT_CHECKBOX, self.OnCheckBoxOutlookScanOutgoingCheckbox)

        self.staticTextNoPersonal = wx.StaticText(
              label='(No personal information is transmitted during this check)',
              name='staticTextNoPersonal', parent=self._panelInternetUpdate,
              pos=wx.Point(27, 219), size=wx.Size(349, 21), style=0)

        self.choicePriority = wx.Choice(choices=['Low', 'Normal'],
              name='choicePriority',
              parent=self._panelAdvanced, pos=wx.Point(252, 184),
              size=wx.Size(134, 21), style=0)
        self.choicePriority.SetToolTipString('Specify the process priority for the virus scanner.')
        self.choicePriority.SetStringSelection('Normal')
        self.choicePriority.SetLabel('')

        self.spinCtrlArchiveFiles = wx.SpinCtrl(
              initial=0, max=1073741824, min=1, name='spinCtrlArchiveFiles',
              parent=self._panelArchives, pos=wx.Point(205, 166), size=wx.Size(72, 21), style=wx.SP_ARROW_KEYS)

        self.staticTextFiles = wx.StaticText(
              label='Files', name='staticTextFiles', parent=self._panelArchives,
              pos=wx.Point(293, 169), size=wx.Size(80, 16), style=0)

        self.staticTextRecursion = wx.StaticText(
              label='Do Not Extract More Than ', name='staticTextRecursion',
              parent=self._panelArchives, pos=wx.Point(24, 205), size=wx.Size(168, 19), style=0)

        self.spinCtrlRecursion = wx.SpinCtrl(
              initial=0, max=999, min=1, name='spinCtrlRecursion',
              parent=self._panelArchives, pos=wx.Point(205, 202), size=wx.Size(72, 21), style=wx.SP_ARROW_KEYS)

        self.staticTextSubArchives = wx.StaticText(
              label='Sub-Archives', name='staticTextSubArchives',
              parent=self._panelArchives, pos=wx.Point(293, 205), size=wx.Size(82, 16), style=0)

        self.checkBoxOutlookShowSplash = wx.CheckBox(
              label='&Display Splash Screen on Startup',
              name='checkBoxOutlookShowSplash', parent=self._panelEmailScanning,
              pos=wx.Point(15, 83), size=wx.Size(354, 18), style=0)
        self.checkBoxOutlookShowSplash.SetValue(False)
        self.checkBoxOutlookShowSplash.SetToolTipString('Select if you wish to display ClamWin Splash Screen when MS Outlook starts up')
        self.checkBoxOutlookShowSplash.Bind(wx.EVT_CHECKBOX, self.OnCheckBoxOutlookScanOutgoingCheckbox)

        self._init_coll_notebook_Pages(self.notebook)

    def __init__(self, parent, config, switchToSchedule):
        self._config = None
        self._config = config
        if sys.platform.startswith("win"):
            self._scheduledScans = wxDialogScheduledScan.LoadPersistentScheduledScans(
                os.path.join(Utils.GetScheduleShelvePath(self._config), 'ScheduledScans'))
        self._init_ctrls(parent)

        # set window icons
        icons = wx.IconBundle()
        icons.AddIconFromFile('img/FrameIcon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcons(icons)


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
        if self._config.Get('UI', 'Standalone'):
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

         # wxWidgets notebook bug workaround
        # http://sourceforge.net/tracker/index.php?func=detail&aid=645323&group_id=9863&atid=109863
        s = self.notebook.GetSize()
        self.notebook.SetSize(wx.Size(s.GetWidth() + 1, s.GetHeight() + 1))
        self.notebook.SetSize(s)
        self.notebook.Layout()


    def OnInitDialog(self, event):
        # vista theme workaround
        # otherwise contrls on the
        # first notebook page don't show
        self.notebook.Update()
        self.notebook.Refresh()


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
            enable = self._config.Get('ClamAV', 'MoveInfected') and len(self._config.Get('ClamAV', 'QuarantineDir'))
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
        wx.EVT_CHAR(self.editableListBoxFiltersInclude.GetListCtrl(), self.OnEditableListBoxChar)
        wx.EVT_CHAR(self.editableListBoxFiltersExclude.GetListCtrl(), self.OnEditableListBoxChar)

    def _EnableInternetUpdateControls(self, init):
        if sys.platform.startswith("win"):
            if init:
                enable = self._config.Get('Updates', 'Enable')
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
        self.timeUpdate = wx.lib.masked.TimeCtrl(parent=self._panelInternetUpdate,
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
            enable = self._config.Get('EmailAlerts', 'Enable')
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
            enable = self._config.Get('ClamAV', 'ScanArchives')
        else:
            enable = self.checkBoxScanArchives.IsChecked()
        self.spinCtrlArchiveFiles.Enable(enable)
        self.spinCtrlArchiveSize.Enable(enable)
        self.spinCtrlRecursion.Enable(enable)

    def _ArchivesPageInit(self):
        self.spinCtrlMaxFileSize.SetValidator(MyValidator(self._config, section='ClamAV', value='MaxFileSize', canEmpty=False))
        self.checkBoxScanArchives.SetValidator(MyValidator(config=self._config, section='ClamAV', value='ScanArchives'))
        self.spinCtrlArchiveSize.SetValidator(MyValidator(self._config, section='ClamAV', value='MaxScanSize', canEmpty=False))
        self.spinCtrlArchiveFiles.SetValidator(MyValidator(self._config, section='ClamAV', value='MaxFiles', canEmpty=False))
        self.spinCtrlRecursion.SetValidator(MyValidator(self._config, section='ClamAV', value='MaxRecursion', canEmpty=False))
        self._EnableArchivesControls(True)

    def _ReportsPageInit(self):
        self.textCtrlScanLogFile.SetValidator(MyValidator(config=self._config, section='ClamAV', value='LogFile', canEmpty=False))
        self.textCtrlUpdateLogFile.SetValidator(MyValidator(config=self._config, section='Updates', value='DBUpdateLogFile', canEmpty=False))
        if sys.platform.startswith('win') and not self._config.Get('UI', 'Standalone'):
            self.checkBoxTrayNotify.SetValidator(MyValidator(config=self._config, section='UI', value='TrayNotify'))
        else:
            self.checkBoxTrayNotify.Hide()

    def _EmailScanningPageInit(self):
        self.checkBoxOutlookScanIncoming.SetValidator(MyValidator(config=self._config, section='EmailScan', value='ScanIncoming'));
        self.checkBoxOutlookScanOutgoing.SetValidator(MyValidator(config=self._config, section='EmailScan', value='ScanOutgoing'));
        self.checkBoxOutlookShowSplash.SetValidator(MyValidator(config=self._config, section='EmailScan', value='ShowSplash'));

    def _AdvancedPageInit(self):
        self.choicePriority.SetValidator(MyValidator(config=self._config, section='ClamAV', value='Priority'))
        self.spinCtrlMaxLogSize.SetValidator(MyValidator(self._config, section='ClamAV', value='MaxLogSize', canEmpty=False))
        self.checkBoxEnableMbox.SetValidator(MyValidator(config=self._config, section='ClamAV', value='EnableMbox'))
        self.checkBoxEnableOLE2.SetValidator(MyValidator(config=self._config, section='ClamAV', value='ScanOle2'))
        self.textCtrlAdditionalParams.SetValidator(MyValidator(config=self._config, section='ClamAV', value='ClamScanParams', canEmpty=True))

    def _ListAddScheduledScan(self, sc, pos = -1):
        if pos == -1:
            pos = self.listViewScheduledTasks.GetItemCount()
        self.listViewScheduledTasks.InsertImageStringItem(pos, sc.Description, 0)
        self.listViewScheduledTasks.SetStringItem(pos, 1, sc.Path)
        self.listViewScheduledTasks.SetStringItem(pos, 2, sc.Frequency)
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
            mask = "Executable files (*.exe)|*.exe|All files (*.*)|*.*"
        else:
            filename = 'freshclam'
            mask = "All files (*)|*"
        dlg = wx.FileDialog(self, "Choose a file", ".", filename, mask, wx.OPEN)
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
            mask = "Executable files (*.exe)|*.exe|All files (*.*)|*.*"
        else:
            filename = 'clamscan'
            mask = "All files (*)|*"
        dlg = wx.FileDialog(self, "Choose a file", ".", filename, mask, wx.OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                self.textCtrlClamScan.Clear()
                self.textCtrlClamScan.WriteText(filename)
        finally:
            dlg.Destroy()

    def OnButtonBrowseVirDB(self, event):
        dlg = wx.DirDialog(self)
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
            mask = "Text Files (*.txt)|*.txt|All files (*.*)|*.*"
        else:
            filename = 'ClamScanLog'
            mask = "All files (*)|*"
        dlg = wx.FileDialog(self, "Choose a file", ".", filename, mask, wx.SAVE)
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
            mask = "Text Files (*.txt)|*.txt|All files (*.*)|*.*"
        else:
            filename = 'ClamUpdateLog'
            mask = "All files (*)|*"
        dlg = wx.FileDialog(self, "Choose a file", ".", filename, mask, wx.SAVE)
        try:
            if dlg.ShowModal() == wx.ID_OK:
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
            dlg = wxDialogScheduledScan.wxDialogScheduledScan(self, sc)
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
        dlg = wx.DirDialog(self)
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
        self.SetCursor(wx.NullCursor)

    def OnEditableListBoxChar(self, event):
        # bind F2 key to edit label function
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
        item.SetTextColour(wx.NullColour)
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

    def OnCheckBoxOutlookScanIncomingCheckbox(self, event):
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
         ctrl = self.GetWindow()
         ctrl.SetSelection(int(value))

     def TransferFromWindow(self):
        ctrl = self.GetWindow()
        value = ctrl.GetSelection()
        self._config.Set(self._section, self._value, value)

class MyValidator(MyBaseValidator):
    def Validate(self, win):
        ctrl = self.GetWindow()
        if not ctrl.IsEnabled():
            return True
        if isinstance(ctrl, (wx.Choice, wx.CheckBox, wx.RadioButton)) or self._canEmpty:
            return True
        if not bool(ctrl.GetValue()):
            page = self.GetWindow().GetParent()
            wx.MessageBox("Value cannot be empty", "ClamWin Free Antivirus", style=wx.ICON_EXCLAMATION|wx.OK)
            ctrl.SetBackgroundColour("yellow")
            ctrl.SetFocus()
            ctrl.Refresh()
            return False
        else:
            ctrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            ctrl.Refresh()
            return True

    def TransferToWindow(self):
        value = self._config.Get(self._section, self._value)
        ctrl = self.GetWindow()
        if(isinstance(ctrl, wx.Choice)):
            ctrl.SetStringSelection(value)
        else:
            ctrl.SetValue(value)


    def TransferFromWindow(self):
        ctrl = self.GetWindow()
        if(isinstance(ctrl, wx.Choice)):
            value = ctrl.GetStringSelection()
        elif isinstance(ctrl, (wx.CheckBox, wx.RadioButton, wx.lib.intctrl.IntCtrl, wx.SpinCtrl)):
            value = ctrl.GetValue()
        elif isinstance(ctrl, wx.lib.masked.TimeCtrl):
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
                        wx.YES_NO  | wx.ICON_QUESTION)
            if choice == wx.ID_YES:
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
            wx.MessageBox("Value cannot be empty", "ClamWin Free Antivirus", style=wx.ICON_EXCLAMATION|wx.OK)
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

