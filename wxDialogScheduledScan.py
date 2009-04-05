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

import os, sys, time, locale
import Utils
import shelve
import wx
import wx.lib.masked

# scheduled scan information holder
# it is used for persistent storage
class ScheduledScanInfo(list):
    def __init__(self, frequency='Daily', time='18:30:00', weekDay=3, path='', description='', active=True, scanmem=True):
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
        print 'Could not open persistent storage for scheduled scans. Error: %s' % str(e)

    return scheduledScans

def SavePersistentScheduledScans(filename, scheduledScans):
    try:
        _shelve = shelve.open(filename)
        _shelve['ScheduledScans'] = scheduledScans
        _shelve['version'] = 3
    except Exception, e:
        print 'Could not save scheduled scans to persistent storage. Error: %s' % str(e)

def create(parent, scanInfo):
    return wxDialogScheduledScan(parent, scanInfo)

class wxDialogScheduledScan(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self,
              name='wxDialogScheduledScan', parent=prnt, pos=wx.Point(1065, 481),
              size=wx.Size(311, 318), style=wx.DEFAULT_DIALOG_STYLE,
              title='Scheduled Scan')
        self.SetClientSize(wx.Size(303, 291))
        self.SetToolTipString('')
        self.Center(wx.BOTH)
        self.Bind(wx.EVT_CHAR_HOOK, self.OnCharHook)

        self.staticBox1 = wx.StaticBox(
              label='Schedule', name='staticBox1', parent=self, pos=wx.Point(11,
              8), size=wx.Size(282, 104), style=0)

        self.staticTextFrequency = wx.StaticText(
              label='Scanning &Frequency:', name='staticTextFrequency',
              parent=self, pos=wx.Point(25, 30), size=wx.Size(131, 13), style=0)
        self.staticTextFrequency.SetToolTipString('')

        self.choiceFrequency = wx.Choice(choices=['Hourly', 'Daily', 'Workdays', 'Weekly'],
              name='choiceFrequency', parent=self, pos=wx.Point(171, 27),
              size=wx.Size(107, 21), style=0)
        self.choiceFrequency.SetToolTipString('How often the schedule is executed')
        self.choiceFrequency.SetStringSelection('Daily')
        self.choiceFrequency.Bind(wx.EVT_CHOICE, self.OnChoiceFrequency)

        self.staticTextTime = wx.StaticText(
              label='&Time:', name='staticTextTime', parent=self,
              pos=wx.Point(25, 56), size=wx.Size(121, 18), style=0)

        self.staticLineTimeCtrl = wx.StaticLine(
              name='staticLineTimeCtrl', parent=self, pos=wx.Point(171, 54),
              size=wx.Size(90, 22), style=0)
        self.staticLineTimeCtrl.Show(False)
        self.staticLineTimeCtrl.SetToolTipString('When the schedule should be started')

        self.spinButtonTime = wx.SpinButton(
              name='spinButtonTime', parent=self, pos=wx.Point(261, 53),
              size=wx.Size(16, 22), style=wx.SP_ARROW_KEYS | wx.SP_VERTICAL)
        self.spinButtonTime.SetToolTipString('')

        self.staticTextDay = wx.StaticText(
              label='&Day Of The Week:', name='staticTextDay', parent=self,
              pos=wx.Point(25, 85), size=wx.Size(123, 18), style=0)
        self.staticTextDay.SetToolTipString('')

        self.choiceDay = wx.Choice(choices=['Monday', 'Tuesday', 'Wednesday',
              'Thursday', 'Friday', 'Saturday', 'Sunday'],
              name='choiceDay',
              parent=self, pos=wx.Point(171, 82), size=wx.Size(107, 21), style=0)
        self.choiceDay.SetToolTipString('When schedule frequency is weekly select day of the week')
        self.choiceDay.SetStringSelection('Tuesday')

        self.staticTextFolder = wx.StaticText(
              label='&Scan Folder:', name='staticTextFolder', parent=self,
              pos=wx.Point(12, 165), size=wx.Size(78, 15), style=0)
        self.staticTextFolder.SetToolTipString('')

        self.textCtrlFolder = wx.TextCtrl(
              name='textCtrlFolder', parent=self, pos=wx.Point(12, 183),
              size=wx.Size(260, 20), style=0, value='')
        self.textCtrlFolder.SetToolTipString('Specify a folder to be scanned')

        self.buttonBrowseFolder = wx.Button(
              label='...', name='buttonBrowseFolder', parent=self,
              pos=wx.Point(274, 183), size=wx.Size(20, 20), style=0)
        self.buttonBrowseFolder.SetToolTipString('Click to browse for a folder')
        self.buttonBrowseFolder.Bind(wx.EVT_BUTTON, self.OnButtonBrowseFolder)

        self.staticTextDescription = wx.StaticText(
              label='D&escription:', name='staticTextDescription', parent=self,
              pos=wx.Point(12, 208), size=wx.Size(68, 16), style=0)
        self.staticTextDescription.SetToolTipString('')

        self.textCtrlDescription = wx.TextCtrl(
              name='textCtrlDescription', parent=self, pos=wx.Point(12, 226),
              size=wx.Size(282, 20), style=0, value='')
        self.textCtrlDescription.SetToolTipString('Specify a friendly description for the scheduled scan')

        self.checkBoxEnabled = wx.CheckBox(
              label='&Activate This Schedule', name='checkBoxEnabled',
              parent=self, pos=wx.Point(11, 121), size=wx.Size(278, 15), style=0)
        self.checkBoxEnabled.SetValue(False)
        self.checkBoxEnabled.SetToolTipString('Select if you wish to enable this schedule')

        self.buttonOK = wx.Button(
              label='OK', name='buttonOK', parent=self, pos=wx.Point(76, 258),
              size=wx.Size(75, 23), style=0)
        self.buttonOK.SetDefault()
        self.buttonOK.SetToolTipString('Closes the dialog and applies the settings')
        self.buttonOK.Bind(wx.EVT_BUTTON, self.OnOK)

        self.buttonCancel = wx.Button(
              label='Cancel', name='buttonCancel', parent=self, pos=wx.Point(163,
              258), size=wx.Size(75, 23), style=0)
        self.buttonCancel.SetToolTipString('Closes the dialog and discards the changes')
        self.buttonCancel.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.checkBoxScanMemory = wx.CheckBox(
              label='Scan &Programs Loaded in Computer Memory',
              name='checkBoxScanMemory', parent=self, pos=wx.Point(11, 141),
              size=wx.Size(277, 18), style=0)
        self.checkBoxScanMemory.SetValue(False)
        self.checkBoxScanMemory.SetToolTipString('Select if you wish to include programs computer memory during every scan')

    def __init__(self, parent, scanInfo):
        self._scanInfo = None
        self._scanInfo = scanInfo
        self._init_ctrls(parent)
        locale.setlocale(locale.LC_ALL, 'C')
        self.timeCtrl = wx.lib.masked.TimeCtrl(parent=self,
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

        self.choiceDay.Enable(self.choiceFrequency.GetStringSelection() == 'Weekly')

    def _Apply(self):
        if not self.Validate():
            return False
        self.TransferDataFromWindow()
        return True

    def OnChoiceFrequency(self, event):
        self.choiceDay.Enable(self.choiceFrequency.GetStringSelection() == 'Weekly')
        event.Skip()

    def OnOK(self, event):
        if self._Apply():
            self.EndModal(wx.ID_OK)

    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnCharHook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

    def OnButtonBrowseFolder(self, event):
        dlg = wx.DirDialog(self)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                dir = dlg.GetPath()
                self.textCtrlFolder.Clear()
                self.textCtrlFolder.WriteText(dir)
        finally:
            dlg.Destroy()

class MyValidator(wx.PyValidator):
    def __init__(self, scanInfo, propName, canEmpty=True):
        wx.PyValidator.__init__(self)
        self._scanInfo = scanInfo
        self._propName = propName
        self._canEmpty = canEmpty

    def Clone(self):
        return MyValidator(self._scanInfo, self._propName, self._canEmpty)

    def Validate(self, win):
        ctrl = self.GetWindow()
        if isinstance(ctrl, (wx.Choice, wx.CheckBox)) or self._canEmpty:
            return True
        text = ctrl.GetValue()
        invalid = False
        if not bool(text):
            wx.MessageBox("Value cannot be empty", "ClamWin", style=wx.ICON_EXCLAMATION|wx.OK)
            invalid = True
        elif ctrl.GetName() == 'textCtrlFolder' and not os.path.exists(text):
            wx.MessageBox("Specified path is invalid. Plese verify your selection.", "ClamWin", style=wx.ICON_EXCLAMATION|wx.OK)
            invalid = True
        else:
            ctrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            ctrl.Refresh()
        if invalid:
            ctrl.SetBackgroundColour("yellow")
            ctrl.SetFocus()
            ctrl.Refresh()
        return not invalid

    def TransferToWindow(self):
        value = getattr(self._scanInfo, self._propName)
        ctrl = self.GetWindow()
        if(isinstance(ctrl, wx.Choice)):
            if ctrl.GetName() == 'choiceDay':
                ctrl.SetSelection(value)
            else:
                ctrl.SetStringSelection(value)
        else:
            ctrl.SetValue(value)
        return True


    def TransferFromWindow(self):
        ctrl = self.GetWindow()
        if(isinstance(ctrl, wx.Choice)):
            if ctrl.GetName() == 'choiceDay':
                value = ctrl.GetSelection()
            else:
                value = ctrl.GetStringSelection()
        elif isinstance(ctrl, wx.CheckBox):
            value = ctrl.GetValue()
        elif isinstance(ctrl, wx.lib.masked.TimeCtrl):
            # set C locale, otherwise python and wxpython complain
            locale.setlocale(locale.LC_ALL, 'C')
            value = ctrl.GetWxDateTime().Format('%H:%M:%S')
        else:
            value = ctrl.GetValue()
        setattr(self._scanInfo, self._propName, value)
        return True


