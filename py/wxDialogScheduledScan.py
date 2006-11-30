#Boa:Dialog:wxDialogScheduledScan

#-----------------------------------------------------------------------------
# Name:        wxDialogScheduledScan.py
# Product:     ClamWin Free Antivirus
#
# Author:      alch [alch at users dot sourceforge dot net]
#
# Created:     2004/18/04
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
from wxPython.lib.timectrl import *
import os, sys, time, locale
import Utils
import shelve
from I18N import getClamString as _
# scheduled scan information holder
# it is used for persistent storage
class ScheduledScanInfo(list):
    def __init__(self, frequency=_('Daily'), time='18:30:00', weekDay=3, path='', description='', active=True, scanmem=True):
        list.__init__(self, [frequency, time, weekDay, path, description, active, scanmem])

    def __getFrequency(self): return self[0]
    def __setFrequency(self, value): self[0] = value
    Frequency = property(__getFrequency, __setFrequency)

    def __getTime(self): return self[1]
    def __setTime(self, value): self[1] = value
    Time = property(__getTime, __setTime)

    def __getWeekDay(self): return self[2]
    def __setWeekDay(self, value): self[2] = value
    WeekDay = property(__getWeekDay, __setWeekDay)

    def __getPath(self): return self[3]
    def __setPath(self, value): self[3] = value
    Path = property(__getPath, __setPath)

    def __getDescription(self): return self[4]
    def __setDescription(self, value): self[4] = value
    Description = property(__getDescription, __setDescription)

    def __getActive(self): return self[5]
    def __setActive(self, value): self[5] = value
    Active = property(__getActive, __setActive)
    
    def __getScanMemory(self): return self[6]
    def __setScanMemory(self, value): self[6] = value
    ScanMemory = property(__getScanMemory, __setScanMemory)

def _getFrequencies():
    # get the frequencies in the current language
    choiceFrequencies=[_('Hourly'), _('Daily'), _('Workdays'), _('Weekly')]
    return choiceFrequencies

def _getEnglishFrequency(transFrequency):
    # take a translated frequency and return the English frequency selected
    englishFrequencies=['Hourly', 'Daily', 'Workdays', 'Weekly']
    choiceFrequences=_getFrequencies()
    freqIndex = choiceFrequences.index(transFrequency)
    if freqIndex >= 0:
        return englishFrequencies[freqIndex]
    raise "Could not find translated frequency %s" % transFrequency

def _getLocalFrequency(englishFrequency):
    choiceFrequencies=_getFrequencies()
    englishFrequencies=['Hourly', 'Daily', 'Workdays', 'Weekly']
    freqIndex = englishFrequencies.index(englishFrequency)
    if freqIndex >= 0:
        return choiceFrequencies[freqIndex]
    raise "Could not find local frequency %s" % englishFrequency

def _convertDataToEnglish(scheduledScans):
    for schedScan in scheduledScans:
        schedScan.Frequency = _getEnglishFrequency(schedScan.Frequency)

def _convertDataFromEnglish(scheduledScans):
    for schedScan in scheduledScans:
        schedScan.Frequency = _getLocalFrequency(schedScan.Frequency)

def LoadPersistentScheduledScans(filename):
    try:
        _shelve = shelve.open(filename)
        # set version of the persistent storage data
        # we may need it in future when upgrading to newer data set
        try:
            version = _shelve['version']
        except KeyError:
            version = 1
        # read our scheduled scans info
        # or create a new empty list
        try:
            scheduledScans = _shelve['ScheduledScans']
        except KeyError:
            scheduledScans = []
        if version < 3:
            for i in range(len(scheduledScans)):
                if version < 2:
                    active = True
                    description = 'Scan ' + scheduledScans[i][3]
                else:
                    active = scheduledScans[i][5]
                    description = scheduledScans[i][4]
                scheduledScans[i] = ScheduledScanInfo(scheduledScans[i][0],
                                         scheduledScans[i][1], scheduledScans[i][2],
                                         scheduledScans[i][3],
                                         description, active, True)

            _shelve['version'] = 3
            _shelve['ScheduledScans'] = scheduledScans
    except Exception, e:
        scheduledScans = []
        print _('Could not open persistent storage for scheduled scans. Error: %s') % str(e)            

    return scheduledScans

def SavePersistentScheduledScans(filename, scheduledScans):
    _convertDataToEnglish(scheduledScans)
    try:
        _shelve = shelve.open(filename)
        _shelve['ScheduledScans'] = scheduledScans
        _shelve['version'] = 3
    except Exception, e:
        print _('Could not save scheduled scans to persistent storage. Error: %s') % str(e)                

def create(parent, scanInfo):
    return wxDialogScheduledScan(parent, scanInfo)

[wxID_WXDIALOGSCHEDULEDSCAN, wxID_WXDIALOGSCHEDULEDSCANBUTTONBROWSEFOLDER,
 wxID_WXDIALOGSCHEDULEDSCANBUTTONCANCEL, wxID_WXDIALOGSCHEDULEDSCANBUTTONOK,
 wxID_WXDIALOGSCHEDULEDSCANCHECKBOXENABLED,
 wxID_WXDIALOGSCHEDULEDSCANCHECKBOXSCANMEMORY,
 wxID_WXDIALOGSCHEDULEDSCANCHOICEDAY,
 wxID_WXDIALOGSCHEDULEDSCANCHOICEFREQUENCY,
 wxID_WXDIALOGSCHEDULEDSCANSPINBUTTONTIME,
 wxID_WXDIALOGSCHEDULEDSCANSTATICBOX1,
 wxID_WXDIALOGSCHEDULEDSCANSTATICLINETIMECTRL,
 wxID_WXDIALOGSCHEDULEDSCANSTATICTEXTDAY,
 wxID_WXDIALOGSCHEDULEDSCANSTATICTEXTDESCRIPTION,
 wxID_WXDIALOGSCHEDULEDSCANSTATICTEXTFOLDER,
 wxID_WXDIALOGSCHEDULEDSCANSTATICTEXTFREQUENCY,
 wxID_WXDIALOGSCHEDULEDSCANSTATICTEXTTIME,
 wxID_WXDIALOGSCHEDULEDSCANTEXTCTRLDESCRIPTION,
 wxID_WXDIALOGSCHEDULEDSCANTEXTCTRLFOLDER,
] = map(lambda _init_ctrls: wxNewId(), range(18))

class wxDialogScheduledScan(wxDialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit

        STRETCH_LEN = 30
        wxDialog.__init__(self, id=wxID_WXDIALOGSCHEDULEDSCAN,
              name='wxDialogScheduledScan', parent=prnt, pos=wxPoint(427, 201),
              size=wxSize(311 + STRETCH_LEN*2, 318), style=wxDEFAULT_DIALOG_STYLE,
              title=_('Scheduled Scan'))
        self.SetClientSize(wxSize(303 + STRETCH_LEN*2, 291))
        self.SetToolTipString('')
        self.Center(wxBOTH)
        EVT_CHAR_HOOK(self, self.OnCharHook)

        self.staticBox1 = wxStaticBox(id=wxID_WXDIALOGSCHEDULEDSCANSTATICBOX1,
              label=_('Schedule'), name='staticBox1', parent=self, pos=wxPoint(11,
              8), size=wxSize(282 + STRETCH_LEN*2, 104), style=0)

        self.staticTextFrequency = wxStaticText(id=wxID_WXDIALOGSCHEDULEDSCANSTATICTEXTFREQUENCY,
              label=_('Scanning &Frequency:'), name='staticTextFrequency',
              parent=self, pos=wxPoint(25, 30), size=wxSize(131 + STRETCH_LEN, 13), style=0)
        self.staticTextFrequency.SetToolTipString('')

        self.choiceFrequency = wxChoice(choices=[_('Hourly'), _('Daily'), _('Workdays'),
                _('Weekly')], id=wxID_WXDIALOGSCHEDULEDSCANCHOICEFREQUENCY,
              name='choiceFrequency', parent=self, pos=wxPoint(171 + STRETCH_LEN, 27),
              size=wxSize(107 + STRETCH_LEN, 21), style=0)
        self.choiceFrequency.SetColumns(2)
        self.choiceFrequency.SetToolTipString(_('How often the schedule is executed'))
        self.choiceFrequency.SetStringSelection(_('Daily'))
        EVT_CHOICE(self.choiceFrequency,
              wxID_WXDIALOGSCHEDULEDSCANCHOICEFREQUENCY,
              self.OnChoiceFrequency)

        self.staticTextTime = wxStaticText(id=wxID_WXDIALOGSCHEDULEDSCANSTATICTEXTTIME,
              label=_('&Time:'), name='staticTextTime', parent=self,
              pos=wxPoint(25, 56), size=wxSize(121 + STRETCH_LEN, 18), style=0)

        self.staticLineTimeCtrl = wxStaticLine(id=wxID_WXDIALOGSCHEDULEDSCANSTATICLINETIMECTRL,
              name='staticLineTimeCtrl', parent=self, pos=wxPoint(171 + STRETCH_LEN, 54),
              size=wxSize(90 + STRETCH_LEN, 22), style=0)
        self.staticLineTimeCtrl.Show(False)
        self.staticLineTimeCtrl.SetToolTipString(_('When the schedule should be started'))

        self.spinButtonTime = wxSpinButton(id=wxID_WXDIALOGSCHEDULEDSCANSPINBUTTONTIME,
              name='spinButtonTime', parent=self, pos=wxPoint(261 + STRETCH_LEN*2, 53),
              size=wxSize(16, 22), style=wxSP_ARROW_KEYS | wxSP_VERTICAL)
        self.spinButtonTime.SetToolTipString('')

        self.staticTextDay = wxStaticText(id=wxID_WXDIALOGSCHEDULEDSCANSTATICTEXTDAY,
              label=_('&Day Of The Week:'), name='staticTextDay', parent=self,
              pos=wxPoint(25, 85), size=wxSize(123 + STRETCH_LEN, 18), style=0)
        self.staticTextDay.SetToolTipString('')

        self.choiceDay = wxChoice(choices=[_('Monday'), _('Tuesday'), _('Wednesday'),
              _('Thursday'), _('Friday'), _('Saturday'), _('Sunday')],
              id=wxID_WXDIALOGSCHEDULEDSCANCHOICEDAY, name='choiceDay',
              parent=self, pos=wxPoint(171 + STRETCH_LEN, 82), size=wxSize(107 + STRETCH_LEN, 21), style=0)
        self.choiceDay.SetColumns(2)
        self.choiceDay.SetToolTipString(_('When schedule frequency is weekly select day of the week'))
        self.choiceDay.SetStringSelection(_('Tuesday'))

        self.staticTextFolder = wxStaticText(id=wxID_WXDIALOGSCHEDULEDSCANSTATICTEXTFOLDER,
              label=_('&Scan Folder:'), name='staticTextFolder', parent=self,
              pos=wxPoint(12, 165), size=wxSize(78, 15), style=0)
        self.staticTextFolder.SetToolTipString('')

        self.textCtrlFolder = wxTextCtrl(id=wxID_WXDIALOGSCHEDULEDSCANTEXTCTRLFOLDER,
              name='textCtrlFolder', parent=self, pos=wxPoint(12, 183),
              size=wxSize(260 + STRETCH_LEN*2, 20), style=0, value='')
        self.textCtrlFolder.SetToolTipString(_('Specify a folder to be scanned'))

        self.buttonBrowseFolder = wxButton(id=wxID_WXDIALOGSCHEDULEDSCANBUTTONBROWSEFOLDER,
              label='...', name='buttonBrowseFolder', parent=self,
              pos=wxPoint(273 + STRETCH_LEN*2, 183), size=wxSize(20, 20), style=0)
        self.buttonBrowseFolder.SetToolTipString(_('Click to browse for a folder'))
        EVT_BUTTON(self.buttonBrowseFolder,
              wxID_WXDIALOGSCHEDULEDSCANBUTTONBROWSEFOLDER,
              self.OnButtonBrowseFolder)

        self.staticTextDescription = wxStaticText(id=wxID_WXDIALOGSCHEDULEDSCANSTATICTEXTDESCRIPTION,
              label=_('D&escription:'), name='staticTextDescription', parent=self,
              pos=wxPoint(12, 208), size=wxSize(68, 16), style=0)
        self.staticTextDescription.SetToolTipString('')

        self.textCtrlDescription = wxTextCtrl(id=wxID_WXDIALOGSCHEDULEDSCANTEXTCTRLDESCRIPTION,
              name='textCtrlDescription', parent=self, pos=wxPoint(12, 226),
              size=wxSize(282 + STRETCH_LEN*2, 20), style=0, value='')
        self.textCtrlDescription.SetToolTipString(_('Specify a friendly description for the scheduled scan'))

        self.checkBoxEnabled = wxCheckBox(id=wxID_WXDIALOGSCHEDULEDSCANCHECKBOXENABLED,
              label=_('&Activate This Schedule'), name='checkBoxEnabled',
              parent=self, pos=wxPoint(11, 121), size=wxSize(278, 15), style=0)
        self.checkBoxEnabled.SetValue(False)
        self.checkBoxEnabled.SetToolTipString(_('Select if you wish to enable this schedule'))

        self.buttonOK = wxButton(id=wxID_WXDIALOGSCHEDULEDSCANBUTTONOK,
              label=_('OK'), name='buttonOK', parent=self, pos=wxPoint(73 + STRETCH_LEN, 258),
              size=wxSize(75, 23), style=0)
        self.buttonOK.SetDefault()
        self.buttonOK.SetToolTipString(_('Closes the dialog and applies the settings'))
        EVT_BUTTON(self.buttonOK, wxID_WXDIALOGSCHEDULEDSCANBUTTONOK, self.OnOK)

        self.buttonCancel = wxButton(id=wxID_WXDIALOGSCHEDULEDSCANBUTTONCANCEL,
              label=_('Cancel'), name='buttonCancel', parent=self, pos=wxPoint(160 + STRETCH_LEN,
              258), size=wxSize(75, 23), style=0)
        self.buttonCancel.SetToolTipString(_('Closes the dialog and discards the changes'))
        EVT_BUTTON(self.buttonCancel, wxID_WXDIALOGSCHEDULEDSCANBUTTONCANCEL,
              self.OnCancel)

        self.checkBoxScanMemory = wxCheckBox(id=wxID_WXDIALOGSCHEDULEDSCANCHECKBOXSCANMEMORY,
              label=_('Scan &Programs Loaded in Computer Memory'),
              name='checkBoxScanMemory', parent=self, pos=wxPoint(11, 141),
              size=wxSize(282 + STRETCH_LEN*2, 18), style=0)
        self.checkBoxScanMemory.SetValue(False)
        self.checkBoxScanMemory.SetToolTipString(_('Select if you wish to include programs computer memory during every scan'))

    def __init__(self, parent, scanInfo):
        self._scanInfo = None
        self._scanInfo = scanInfo
        self._init_ctrls(parent)
        locale.setlocale(locale.LC_ALL, 'C')
        self.timeCtrl = wxTimeCtrl(parent=self,
                        pos=self.staticLineTimeCtrl.GetPosition(),
                        size=self.staticLineTimeCtrl.GetSize(),
                        fmt24hr=Utils.IsTime24(),
                        spinButton=self.spinButtonTime,
                        useFixedWidthFont=False, display_seconds=True)
        self.timeCtrl.SetToolTipString(self.staticLineTimeCtrl.GetToolTip().GetTip())

        self.choiceFrequency.SetValidator(MyValidator(self._scanInfo, 'Frequency'))
        self.timeCtrl.SetValidator(MyValidator(self._scanInfo, 'Time'))
        self.choiceDay.SetValidator(MyValidator(self._scanInfo, 'WeekDay'))
        self.textCtrlDescription.SetValidator(MyValidator(self._scanInfo, 'Description', False))
        self.textCtrlFolder.SetValidator(MyValidator(self._scanInfo, 'Path', False))
        self.checkBoxEnabled.SetValidator(MyValidator(self._scanInfo, 'Active'))
        self.checkBoxScanMemory.SetValidator(MyValidator(self._scanInfo, 'ScanMemory'))
        self.TransferDataToWindow()

        self.choiceDay.Enable(self.choiceFrequency.GetStringSelection() == _('Weekly'))        

    def _Apply(self):
        if not self.Validate():
            return False
        self.TransferDataFromWindow()
        return True

    def OnChoiceFrequency(self, event):
        self.choiceDay.Enable(self.choiceFrequency.GetStringSelection() == _('Weekly'))
        event.Skip()

    def OnOK(self, event):
        if self._Apply():
            self.EndModal(wxID_OK)

    def OnCancel(self, event):
        self.EndModal(wxID_CANCEL)

    def OnCharHook(self, event):
        if event.GetKeyCode() == WXK_ESCAPE:
            self.EndModal(wxID_CANCEL)
        else:
            event.Skip()

    def OnButtonBrowseFolder(self, event):
        dlg = wxDirDialog(self, _('Select a directory'))
        try:
            if dlg.ShowModal() == wxID_OK:
                dir = dlg.GetPath()
                self.textCtrlFolder.Clear()
                self.textCtrlFolder.WriteText(dir)
        finally:
            dlg.Destroy()

class MyValidator(wxPyValidator):
    def __init__(self, scanInfo, propName, canEmpty=True):
        wxPyValidator.__init__(self)
        self._scanInfo = scanInfo
        self._propName = propName
        self._canEmpty = canEmpty

    def Clone(self):
        return MyValidator(self._scanInfo, self._propName, self._canEmpty)

    def Validate(self, win):
        ctrl = self.GetWindow()
        if isinstance(ctrl, (wxChoice, wxCheckBox)) or self._canEmpty:
            return True
        if isinstance(ctrl, wxSpinCtrl):
            text = str(ctrl.GetValue())
        else:
            text = ctrl.GetValue()
        invalid = False
        if len(text) == 0:
            wxMessageBox(_("Value cannot be empty"), "ClamWin", style=wxICON_EXCLAMATION|wxOK)
            invalid = True
        elif ctrl.GetName() == 'textCtrlFolder' and not os.path.exists(text):
            wxMessageBox(_("Specified path is invalid. Plese verify your selection."), "ClamWin", style=wxICON_EXCLAMATION|wxOK)
            invalid = True
        else:
            ctrl.SetBackgroundColour(wxSystemSettings_GetColour(wxSYS_COLOUR_WINDOW))
            ctrl.Refresh()
        if invalid:
            ctrl.SetBackgroundColour("yellow")
            ctrl.SetFocus()
            ctrl.Refresh()
        return not invalid

    def TransferToWindow(self):
        value = getattr(self._scanInfo, self._propName)
        ctrl = self.GetWindow()
        if(isinstance(ctrl, wxChoice)):
            if ctrl.GetName() == 'choiceDay':
                ctrl.SetSelection(value)
            else:
                ctrl.SetStringSelection(value)
        else:
            ctrl.SetValue(value)
        return True


    def TransferFromWindow(self):
        ctrl = self.GetWindow()
        if(isinstance(ctrl, wxChoice)):
            if ctrl.GetName() == 'choiceDay':
                value = ctrl.GetSelection()
            else:
                value = ctrl.GetStringSelection()
        elif isinstance(ctrl, wxCheckBox):
            value = ctrl.GetValue()
        elif isinstance(ctrl, wxTimeCtrl):
            # set C locale, otherwise python and wxpython complain
            locale.setlocale(locale.LC_ALL, 'C')
            value = ctrl.GetWxDateTime().Format('%H:%M:%S')
        else:
            value = ctrl.GetValue()
        setattr(self._scanInfo, self._propName, value)
        return True


