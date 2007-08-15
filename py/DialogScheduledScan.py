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


import wx
import wx.lib.masked as masked
import wx.lib.filebrowsebutton as filebrowse

import os, sys, time, locale
import Utils

import Scheduler

#from I18N import getClamString as _

          
def create(parent, scanInfo):
    return DialogScheduledScan(parent, scanInfo)

class DialogScheduledScan(wx.Dialog):
    def __init__(self, parent, scanInfo):
        self._scanInfo = scanInfo

        STRETCH_LEN = 30
        wx.Dialog.__init__(self, parent,wx.ID_ANY,_('Scheduled Scan'))
        self.SetClientSize(wx.Size(303 + STRETCH_LEN*2, 291))
        self.Center(wx.BOTH)
        self.Bind(wx.EVT_CHAR_HOOK, self.OnCharHook)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.staticBox1 = wx.StaticBox(self,wx.ID_ANY,_('Schedule'))
        bsizer = wx.StaticBoxSizer(self.staticBox1, wx.VERTICAL)
        sizer.Add(bsizer,0,wx.EXPAND | wx.ALL, 10)

        grid = wx.GridSizer(3,2,5,5)

        self.staticTextFrequency = wx.StaticText(self,wx.ID_ANY,_('Scanning &Frequency:'))
        grid.Add(self.staticTextFrequency)

        self.choiceFrequency = wx.Choice(self,wx.ID_ANY,choices = Scheduler._getFrequencies())
        self.choiceFrequency.SetSelection(1)
        self.choiceFrequency.SetToolTipString(_('How often the schedule is executed'))
        self.choiceFrequency.SetStringSelection(_('Daily'))
        self.Bind(wx.EVT_CHOICE,self.OnChoiceFrequency,self.choiceFrequency)
        grid.Add(self.choiceFrequency,0,wx.EXPAND)              

        self.staticTextTime = wx.StaticText(self,wx.ID_ANY,_('&Time:'))
        grid.Add(self.staticTextTime)

        self.timeCtrl = masked.TimeCtrl(self,wx.ID_ANY,time.strftime('%H:%M:%S',time.localtime()),
                                        fmt24hr=Utils.IsTime24(),
                                        useFixedWidthFont=False, display_seconds=True)
        self.timeCtrl.SetToolTipString(_('When the schedule should be started'))
        h = self.timeCtrl.GetSize().height
        self.spinButtonTime = wx.SpinButton(self,wx.ID_ANY, size=(-1,h),style=wx.SP_ARROW_KEYS | wx.SP_VERTICAL)
        self.timeCtrl.BindSpinButton( self.spinButtonTime )

        timesizer = wx.BoxSizer(wx.HORIZONTAL)
        timesizer.Add(self.timeCtrl,1)
        timesizer.Add(self.spinButtonTime,0,wx.EXPAND)
        grid.Add(timesizer,0,wx.EXPAND)
                

        self.staticTextDay = wx.StaticText(self,wx.ID_ANY,_('&Day Of The Week:'))
        grid.Add(self.staticTextDay,0,wx.EXPAND)

        self.choiceDay = wx.Choice(self,wx.ID_ANY,choices = [_('Monday'), _('Tuesday'), _('Wednesday'),_('Thursday'), _('Friday'), _('Saturday'), _('Sunday')])
        self.choiceDay.SetSelection(1)
        self.choiceDay.SetToolTipString(_('When schedule frequency is weekly select day of the week'))
        self.choiceDay.SetStringSelection(_('Tuesday'))
        grid.Add(self.choiceDay,0,wx.EXPAND)

        bsizer.Add(grid,0,wx.EXPAND|wx.ALL,5)

        

        self.checkBoxEnabled = wx.CheckBox(self,wx.ID_ANY,_('&Activate This Schedule'))
        self.checkBoxEnabled.SetValue(False)
        self.checkBoxEnabled.SetToolTipString(_('Select if you wish to enable this schedule'))
        sizer.Add(self.checkBoxEnabled,0,wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        self.checkBoxScanMemory = wx.CheckBox(self,wx.ID_ANY,_('Scan &Programs Loaded in Computer Memory'))
        self.checkBoxScanMemory.SetValue(False)
        self.checkBoxScanMemory.SetToolTipString(_('Select if you wish to include programs computer memory during every scan'))
        sizer.Add(self.checkBoxScanMemory,0,wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        sizer.Add((-1,-1),1)

        self.staticTextFolder = wx.StaticText(self,wx.ID_ANY,_('&Scan Folder:'))
        sizer.Add(self.staticTextFolder,0,wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        self.textCtrlFolder = filebrowse.DirBrowseButton(self,labelText='',
                                                         buttonText=_('Browse'),
                                                         toolTip=_('Specify a folder to be scanned'),
                                                         dialogTitle = _('Select a directory'))
        sizer.Add(self.textCtrlFolder,0,wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        self.staticTextDescription = wx.StaticText(self,wx.ID_ANY,_('D&escription:'))
        sizer.Add(self.staticTextDescription,0,wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        self.textCtrlDescription = wx.TextCtrl(self,wx.ID_ANY)
        self.textCtrlDescription.SetToolTipString(_('Specify a friendly description for the scheduled scan'))
        sizer.Add(self.textCtrlDescription,0,wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

##        self.textCtrlFolder = wx.TextCtrl(self,pos=(12, 183),size=(260 + STRETCH_LEN*2, 20))
##        self.textCtrlFolder.SetToolTipString(_('Specify a folder to be scanned'))
##
##        self.buttonBrowseFolder = wx.Button(self,wx.ID_ANY,'...',(273 + STRETCH_LEN*2, 183),(20, 20))
##        self.buttonBrowseFolder.SetToolTipString(_('Click to browse for a folder'))
##        self.Bind(wx.EVT_BUTTON,self.OnButtonBrowseFolder,self.buttonBrowseFolder)

        sizer_bt = wx.BoxSizer(wx.HORIZONTAL)

        self.buttonOK = wx.Button(self,wx.ID_ANY,_('OK'))
        self.buttonOK.SetDefault()
        self.buttonOK.SetToolTipString(_('Closes the dialog and applies the settings'))
        self.Bind(wx.EVT_BUTTON,self.OnOK,self.buttonOK)
        sizer_bt.Add(self.buttonOK)

        sizer_bt.Add((10,-1))

        self.buttonCancel = wx.Button(self,wx.ID_ANY,_('Cancel'))
        self.buttonCancel.SetToolTipString(_('Closes the dialog and discards the changes'))
        self.Bind(wx.EVT_BUTTON,self.OnCancel,self.buttonCancel)
        sizer_bt.Add(self.buttonCancel)

        sizer.Add(sizer_bt,0,wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)
        
        


        self.SetSizer(sizer)
        

        #locale.setlocale(locale.LC_ALL, 'C')


        self.choiceFrequency.SetValidator(MyValidator(self._scanInfo, 'Frequency'))
        self.timeCtrl.SetValidator(MyValidator(self._scanInfo, 'Time'))
        self.choiceDay.SetValidator(MyValidator(self._scanInfo, 'WeekDay'))
        self.textCtrlDescription.SetValidator(MyValidator(self._scanInfo, 'Description', False))
        #self.textCtrlFolder.SetValidator(MyValidator(self._scanInfo, 'Path', False))
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
            self.EndModal(wx.ID_OK)

    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnCharHook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

##    def OnButtonBrowseFolder(self, event):
##        dlg = wx.DirDialog(self, _('Select a directory'))
##        try:
##            if dlg.ShowModal() == wx.ID_OK:
##                dir = dlg.GetPath()
##                self.textCtrlFolder.Clear()
##                self.textCtrlFolder.WriteText(dir)
##        finally:
##            dlg.Destroy()

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
        if isinstance(ctrl, wx.SpinCtrl):
            text = str(ctrl.GetValue())
        else:
            text = ctrl.GetValue()
        invalid = False
        if len(text) == 0:
            wx.MessageBox(_("Value cannot be empty"), "ClamWin", style=wx.ICON_EXCLAMATION|wx.OK)
            invalid = True
        elif isinstance(ctrl,filebrowse.DirBrowseButton) and not os.path.exists(text):
            wx.MessageBox(_("Specified path is invalid. Plese verify your selection."), "ClamWin", style=wx.ICON_EXCLAMATION|wx.OK)
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
        if isinstance(ctrl, wx.Choice):
            ctrl.SetSelection(value)
##            if ctrl.GetName() == 'choiceDay':
##                ctrl.SetSelection(value)
##            else:
##                ctrl.SetStringSelection(value)
        else:
            ctrl.SetValue(value)
        return True


    def TransferFromWindow(self):
        ctrl = self.GetWindow()
        if(isinstance(ctrl, wx.Choice)):
            value = ctrl.GetSelection()
##            if ctrl.GetName() == 'choiceDay':
##                value = ctrl.GetSelection()
##            else:
##                value = ctrl.GetStringSelection()
        elif isinstance(ctrl, wx.CheckBox):
            value = ctrl.GetValue()
        elif isinstance(ctrl, masked.TimeCtrl):
            # set C locale, otherwise python and wxpython complain
            # sramage : what's the problem?
            #locale.setlocale(locale.LC_ALL, 'C')
            value = ctrl.GetWxDateTime().Format('%H:%M:%S')
        else:
            value = ctrl.GetValue()
        setattr(self._scanInfo, self._propName, value)
        return True


if __name__ == '__main__':
    a = wx.App(False)
    dlg = DialogScheduledScan(None,Scheduler.ScheduledScanInfo())
    dlg.ShowModal()
    dlg.Destroy()
    
