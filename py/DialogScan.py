# -*- coding: cp1252 -*-

#-----------------------------------------------------------------------------
# Name:        DialogScan.py
# Product:     ClamWin Free Antivirus
#
# Author:      sramage
#
# Created:     08/09/2007
# Copyright:   Copyright sramage (c) 2007
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
import wx.lib.hyperlink as hl
import time

class DialogScan(wx.Dialog):
    def __init__(self,parent):
        wx.Dialog.__init__(self,parent,wx.ID_ANY,_('ClamWin Scanner'),size=(400,300))
        self.Center(wx.BOTH)
        #self.SetBackgroundColour(wx.WHITE)

        sizer = wx.BoxSizer(wx.VERTICAL)

        img = wx.Image('img/Title.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        imgctrl = wx.StaticBitmap(self,wx.ID_ANY,img)
        sizer.Add(imgctrl,0,wx.ALIGN_CENTER_HORIZONTAL)
    
        self.NB = wx.Notebook(self)
        
        sizer.Add(self.NB,1,wx.EXPAND)
        self.SetSizer(sizer)

        self._panelStatus = wx.Panel(self.NB)
        self._panelInfections = wx.Panel(self.NB)
        self._panelErrors = wx.Panel(self.NB)

        self.NB.AddPage(self._panelStatus,_('Status'),True)
        self.NB.AddPage(self._panelInfections,_('Infections'))
        self.NB.AddPage(self._panelErrors,_('Errors/Warnings'))

        #Panel status
        status_sizer = wx.BoxSizer(wx.VERTICAL)

        self.StatusTotal = wx.StaticText(self._panelStatus)
        status_sizer.Add(self.StatusTotal, 0, wx.TOP|wx.RIGHT|wx.LEFT,10)
        self.StatusInfected = hl.HyperLinkCtrl(self._panelStatus, wx.ID_ANY, _("Infected :"))
        #self.StatusInfected = wx.StaticText(self._panelStatus)
        status_sizer.Add(self.StatusInfected, 0,wx.RIGHT|wx.LEFT,10)
        self.StatusInfected.AutoBrowse(False)
        self.StatusInfected.EnableRollover(True)
        self.StatusInfected.SetUnderlines(False, False, True)
        self.StatusInfected.SetColours("BLUE", "BLUE", "BLUE")
        self.StatusInfected.SetToolTip(wx.ToolTip(_("Click here to see infected files")))
        self.StatusInfected.UpdateLink()
        self.StatusErrors = hl.HyperLinkCtrl(self._panelStatus, wx.ID_ANY, _("Errors/Warnings :"))
        #self.StatusErrors = wx.StaticText(self._panelStatus)
        status_sizer.Add(self.StatusErrors, 0, wx.RIGHT|wx.LEFT,10)
        self.StatusErrors.AutoBrowse(False)
        self.StatusErrors.EnableRollover(True)
        self.StatusErrors.SetUnderlines(False, False, True)
        self.StatusErrors.SetColours("BLUE", "BLUE", "BLUE")
        self.StatusErrors.SetToolTip(wx.ToolTip(_("Click here to see Errors and Warnings")))
        self.StatusErrors.UpdateLink()
        self.StatusLast = wx.StaticText(self._panelStatus)
        status_sizer.Add(self.StatusLast,0,wx.RIGHT|wx.LEFT|wx.BOTTOM,10)
        self.Gauge = wx.Gauge(self._panelStatus,wx.ID_ANY,100) #100%
        status_sizer.Add(self.Gauge,0,wx.EXPAND|wx.RIGHT|wx.LEFT,10)
        self.StatusTime = wx.StaticText(self._panelStatus)
        status_sizer.Add(self.StatusTime,0,wx.RIGHT|wx.LEFT,10)
        self.StatusRestTime = wx.StaticText(self._panelStatus)
        status_sizer.Add(self.StatusRestTime,0,wx.RIGHT|wx.LEFT,10)

        self.StatusInfected.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLinkInfected)
        self.StatusErrors.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLinkErrors)

        self._panelStatus.SetSizer(status_sizer)

        #Panel Infections

        infections_sizer = wx.BoxSizer(wx.VERTICAL)


        self._panelInfections.SetSizer(infections_sizer)

        #Panel Errors/Warnings

        errors_sizer = wx.BoxSizer(wx.VERTICAL)

        self._panelErrors.SetSizer(errors_sizer)
        
        #Data
        self.Percent = 0
        self.CurrentScan = '' #current file
        self.Infected = [] #list of infected files
        self.Errors = [] #list of errors
    
        self.UpdateTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnUpdate, self.UpdateTimer)
        self.UpdateTimer.Start(500) #update dialog every 200ms
        self._start_time = time.time()

    def OnLinkInfected(self, event):
        self.NB.SetSelection(1)

    def OnLinkErrors(self, event):
        self.NB.SetSelection(2)

    def OnUpdate(self, event):
        self.Gauge.SetValue(self.Percent)
        self.StatusTotal.SetLabel(_("Total scanned : %d")%(self.Percent))
        self.StatusInfected.SetLabel(_("Infected : %d")%(len(self.Infected)))
        self.StatusErrors.SetLabel(_("Errors/Warnings : %d")%(len(self.Errors)))
        self.StatusLast.SetLabel(_("Last scanned file : %s")%(self.CurrentScan))
        self.StatusTime.SetLabel(_("Elapsed time : %s")%(time.strftime("%H:%M:%S",time.gmtime(time.time()-self._start_time))))
        self.StatusRestTime.SetLabel(_("Estimated rest time : %s")%(time.strftime("%H:%M:%S",time.gmtime((100-self.Percent)*(time.time()-self._start_time)/self.Percent))))
        
    def SetState(self,percent,current):

        self.Percent = percent
        self.CurrentScan = current


    def Demo(self):
        #Enable Demo mode
        
        
        self.count = 0
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.TimerHandler, self.timer)
        
        self.timer.Start(100)

    def TimerHandler(self, event):
        self.count = self.count + 1

        if self.count >= 100:
            #self.count = 0
            self.timer.Stop()

        filename = self._Demo_RandFile()
        self.SetState(self.count,filename)


        test = random.randint(1,100)
        if test > 95:
            self.Errors.append(filename)
        elif test > 90:
            self.Infected.append(filename)
            


    def _Demo_RandFile(self):
        #generate random filename for demo
        filename = ''
        for i in range(random.randint(8,16)):
            filename += random.choice(string.ascii_lowercase+string.digits)
        filename += '.'
        for i in range(3):
            filename += random.choice(string.ascii_lowercase)
        return filename


        

if __name__ == '__main__':
    import I18N
    I18N.install()

    import string
    import random
    
    a = wx.App()
    dlg = DialogScan(None)
    dlg.Demo()
    dlg.ShowModal()
    a.SetTopWindow(dlg)
    
    a.MainLoop()
    dlg.Destroy()
    a.Exit()
    
    
