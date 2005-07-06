#-----------------------------------------------------------------------------
#Boa:Dialog:wxDialogStatus

#-----------------------------------------------------------------------------
# Name:        wxDialogStatus.py
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
from wxPython.lib.throbber import Throbber
from threading import *
from throb import throbImages
import string
import time
import tempfile
import Process
import os, sys
import re
import MsgBox
import Utils


_WAIT_TIMEOUT = 5
if sys.platform.startswith("win"):    
    import win32event, win32api, winerror, win32con, win32gui
    _KILL_SIGNAL = None    
    _WAIT_NOWAIT = 0
    _NEWLINE_LEN=2
else:
    import signal, os
    _KILL_SIGNAL = signal.SIGKILL
    _WAIT_NOWAIT = os.WNOHANG
    _NEWLINE_LEN=1


                    
class StatusUpdateBuffer(Process.IOBuffer):            
    def __init__(self,  caller, update, notify):
        Process.IOBuffer.__init__(self)
        self._caller = caller
        self.update = update
        self.notify = notify        
        
    def _doWrite(self, s):
        # sometimes there is more than one line in the buffer
        # so we need to call update method for every new line                                
        lines = s.replace('\r', '\n').splitlines(True)        
        for line in lines:              
            if sys.platform.startswith('win'):        
                # replace cygwin-like pathes with windows-like
                line = re.sub('/cygdrive/([A-Za-z])/', r'\1:/', line).replace('/', '\\')
            self.update(self._caller, line)             
            
        
        
        # do not call original implementation
        # Process.IOBuffer._doWrite(self, s)
        
    def _doClose(self):
        self.notify(self._caller)
        Process.IOBuffer._doClose(self)

# custom command events sent from worker thread when it finishes    
# and when status message needs updating
# the handler updates buttons and status text
THREADFINISHED = wxNewEventType() 
def EVT_THREADFINISHED( window, function ):     
    window.Connect( -1, -1, THREADFINISHED, function ) 
 
class ThreadFinishedEvent(wxPyCommandEvent): 
    eventType = THREADFINISHED 
    def __init__(self, windowID): 
        wxPyCommandEvent.__init__(self, self.eventType, windowID) 
 
    def Clone( self ): 
        self.__class__( self.GetId() )
 
THREADUPDATESTATUS = wxNewEventType() 
def EVT_THREADUPDATESTATUS( window, function ):     
    window.Connect( -1, -1, THREADUPDATESTATUS, function ) 
           
class ThreadUpdateStatusEvent(wxPyCommandEvent): 
    eventType = THREADUPDATESTATUS 
    def __init__(self, windowID, text, append): 
        self.text = text
        self.append = append
        wxPyCommandEvent.__init__(self, self.eventType, windowID) 
 
    def Clone( self ): 
        self.__class__( self.GetId() )
        
def create(parent, cmd, logfile, priority, bitmap_mask, notify_params=None):
    return wxDialogStatus(parent, cmd, logfile, priority, bitmap_mask, notify_params)                 

[wxID_WXDIALOGSTATUS, wxID_WXDIALOGSTATUSBUTTONSAVE, 
 wxID_WXDIALOGSTATUSBUTTONSTOP, wxID_WXDIALOGSTATUSSTATICBITMAP1, 
 wxID_WXDIALOGSTATUSTEXTCTRLSTATUS, 
] = map(lambda _init_ctrls: wxNewId(), range(5))

class wxDialogStatus(wxDialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxDialog.__init__(self, id=wxID_WXDIALOGSTATUS, name='wxDialogStatus',
              parent=prnt, pos=wxPoint(449, 269), size=wxSize(568, 392),
              style=wxDEFAULT_DIALOG_STYLE, title='ClamWin Status')
        self.SetClientSize(wxSize(560, 365))
        self.SetAutoLayout(false)
        self.Center(wxBOTH)
        self.SetToolTipString('')
        EVT_CLOSE(self, self.OnWxDialogStatusClose)
        EVT_INIT_DIALOG(self, self.OnInitDialog)

        self.textCtrlStatus = wxTextCtrl(id=wxID_WXDIALOGSTATUSTEXTCTRLSTATUS,
              name='textCtrlStatus', parent=self, pos=wxPoint(89, 11),
              size=wxSize(455, 300),
              style=wxTAB_TRAVERSAL | wxTE_RICH | wxTE_MULTILINE | wxTE_READONLY, value='')
              
        self.staticBitmap1 = wxStaticBitmap(bitmap=wxNullBitmap,
              id=wxID_WXDIALOGSTATUSSTATICBITMAP1, name='staticBitmap1',
              parent=self, pos=wxPoint(16, 9), size=wxSize(56, 300),
              style=wxTRANSPARENT_WINDOW)

        self.buttonStop = wxButton(id=wxID_WXDIALOGSTATUSBUTTONSTOP,
              label='&Stop', name='buttonStop', parent=self, pos=wxPoint(291,
              328), size=wxSize(85, 24), style=0)
        self.buttonStop.Enable(True)
        self.buttonStop.SetDefault()
        EVT_BUTTON(self.buttonStop, wxID_WXDIALOGSTATUSBUTTONSTOP,
              self.OnButtonStop)

        self.buttonSave = wxButton(id=wxID_WXDIALOGSTATUSBUTTONSAVE,
              label='S&ave Report', name='buttonSave', parent=self,
              pos=wxPoint(192, 328), size=wxSize(86, 24), style=0)
        self.buttonSave.Enable(False)
        EVT_BUTTON(self.buttonSave, wxID_WXDIALOGSTATUSBUTTONSAVE,
              self.OnButtonSave)

    def __init__(self, parent, cmd, logfile, priority='n', bitmapMask="", notify_params=None):
        self._autoClose = False
        self._closeRetCode = None
        self._cancelled = False        
        self._logfile = logfile
        self._returnCode = -1
        self.terminating = False       
        self._out = None
        self._proc = None         
        self._notify_params = notify_params
        
        self._init_ctrls(parent)
        
        # bind thread notification events
        EVT_THREADFINISHED(self, self.OnThreadFinished)        
        EVT_THREADUPDATESTATUS(self, self.OnThreadUpdateStatus)                
        
        # initilaise our throbber (an awkward way to display animated images)
        images = [throbImages.catalog[i].getBitmap()
                  for i in throbImages.index
                  if i.find(bitmapMask) != -1]                        
        self.throbber = Throbber(self, -1, images, frameDelay=0.1,
                  pos=self.staticBitmap1.GetPosition(), size=self.staticBitmap1.GetSize(),
                  style=self.staticBitmap1.GetWindowStyleFlag(), useParentBackground = True, name='staticThrobber')
    
        
        # set window icons
        icons = wxIconBundle()
        icons.AddIconFromFile('img/FrameIcon.ico', wxBITMAP_TYPE_ICO)
        self.SetIcons(icons)        

        # change colour of read-only controls (gray)
        self.textCtrlStatus.SetBackgroundColour(wxSystemSettings_GetColour(wxSYS_COLOUR_BTNFACE))        
        
        # spawn and monitor our process
        try:
            self._SpawnProcess(cmd, priority)            
        except Process.ProcessError, e:
            event = ThreadUpdateStatusEvent(self.GetId(), str(e), False)                         
            self.GetEventHandler().AddPendingEvent(event)                 
            event = ThreadFinishedEvent(self.GetId()) 
            self.GetEventHandler().AddPendingEvent(event)                             
        
    def SetAutoClose(self, autoClose, closeRetCode=None):
        self._autoClose = autoClose
        self._closeRetCode = closeRetCode

    
    def OnWxDialogStatusClose(self, event):          
         self.terminating = True         
         self._StopProcess()                     
         event.Skip()
    
    def _IsProcessRunning(self, wait=False):
        if self._proc is None:
            return False
        
        if wait:
            timeout = _WAIT_TIMEOUT
        else:
            timeout = _WAIT_NOWAIT
        try:        
            self._proc.wait(timeout)                  
        except Exception, e:
            if isinstance(e, Process.ProcessError):
                if e.errno == Process.ProcessProxy.WAIT_TIMEOUT:        
                    return True     
                else:
                    return False
        return False

    def _StopProcess(self):  
        # check if process is still running
        if self._IsProcessRunning():       
            # still running - kill
            # terminate process and use KILL_SIGNAL to terminate gracefully
            # do not wait too long for the process to finish                
            self._proc.kill(sig=_KILL_SIGNAL)
            
            #wait to finish
            if self._IsProcessRunning(True):       
                # still running, huh
                # kill unconditionally
                try:
                    self._proc.kill()
                except Process.ProcessError:
                    pass                               
                
                # last resort if failed to kill the process
                if self._IsProcessRunning():       
                    MsgBox.ErrorBox(self, 'Unable to stop runner thread, terminating')
                    os._exit(0)      
                    
            self._proc.close()
            self._out.close()                                                    
                
    def OnButtonStop(self, event):      
        if self._IsProcessRunning():           
            self._cancelled = True 
            self._StopProcess()            
        else:
            self.Close()                    

    def OnButtonSave(self, event):
        filename = "clamav_report_" + time.strftime("%d%m%y_%H%M%S")
        if sys.platform.startswith("win"):
            filename +=  ".txt"
            mask = "Report files (*.txt)|*.txt|All files (*.*)|*.*"
        else:            
            mask = "All files (*)|*"
        dlg = wxFileDialog(self, "Choose a file", ".", filename, mask, wxSAVE)
        try:
            if dlg.ShowModal() == wxID_OK:
                filename = dlg.GetPath()
                try:
                    file(filename, "w").write(self.textCtrlStatus.GetLabel())
                except:
                    dlg = wxMessageDialog(self, 'Could not save report to the file ' + \
                                            filename + ". Please check that you have write "
                                            "permissions to the folder and there is enough space on the disk.",
                      'ClamWin', wxOK | wxICON_ERROR)
                    try:
                        dlg.ShowModal()
                    finally:
                        dlg.Destroy()
        finally:
            dlg.Destroy()
            
            
    def ThreadFinished(owner):    
        if owner.terminating:            
            return
        event = ThreadFinishedEvent(owner.GetId()) 
        owner.GetEventHandler().AddPendingEvent(event)                 
    ThreadFinished = staticmethod(ThreadFinished)
    
    def ThreadUpdateStatus(owner, text, append=True):
        if owner.terminating:            
            return
        event = ThreadUpdateStatusEvent(owner.GetId(), text, append)             
        owner.GetEventHandler().AddPendingEvent(event)                    
    ThreadUpdateStatus = staticmethod(ThreadUpdateStatus)
    
    def OnThreadFinished(self, event):
        self.buttonSave.Enable(True)
        self.throbber.Rest()
        self.buttonStop.SetFocus()
        self.buttonStop.SetLabel('&Close')                   
                
       
        data = ''
        if self._logfile is not None:
            try:
                data = file(self._logfile, 'rt').read()
            except Exception, e:
                print 'Could not read from log file %s. Error: %s' % (self._logfile, str(e))
        if sys.platform.startswith('win'):
            # replace cygwin-like pathes with windows-like
            data = re.sub('/cygdrive/([A-Za-z])/', r'\1:/', data).replace('/', '\\').replace('I\\O', 'I/O')  
            data = Utils.ReformatLog(data, win32api.GetVersionEx()[0] >= 5)
        else:
            data = Utils.ReformatLog(data, False)
                
        if len(data.splitlines()) > 1:
            self.ThreadUpdateStatus(self, data, False)
        
        if not self._cancelled:    
           self.ThreadUpdateStatus(self, "\n-------------------\nCompleted\n-------------------\n")                  
        else:
            self.ThreadUpdateStatus(self, "\n-------------------\nCommand has been interrupted...\n-------------------\n")        
            
        if sys.platform.startswith('win'):    
            win32api.PostMessage(self.textCtrlStatus.GetHandle(), win32con.EM_SCROLLCARET, 0, 0)
        else:
            self.textCtrlStatus.SetInsertionPointEnd()                        
            self.textCtrlStatus.ShowPosition(self.textCtrl.GetLastPosition())                
        
        try:                
            self._returnCode = self._proc.wait(_WAIT_TIMEOUT)            
        except:            
            self._returnCode = -1
                        
        if (self._notify_params is not None) and (not self._cancelled):                                
            Utils.ShowBalloon(self._returnCode, self._notify_params)
                                
        # close the window automatically if requested
        if self._autoClose and \
           (self._closeRetCode is None or self._closeRetCode == self._returnCode):             
            time.sleep(0)
            e = wxCommandEvent(wxEVT_COMMAND_BUTTON_CLICKED, self.buttonStop.GetId())
            self.buttonStop.AddPendingEvent(e)                                                
                    
    def OnThreadUpdateStatus(self, event):
        ctrl = self.textCtrlStatus
           
        text = event.text           
        if event.append == True:
            
            # Check if we reached 30000 characters
            # and need to purge topmost line           
            if ctrl.GetLastPosition() + len(text) + _NEWLINE_LEN >= 30000:
                ctrl.Clear()
            
            line_number = ctrl.GetNumberOfLines() - 2
            # detect progress message in the new text
            progress_markers = ['[|]', '[/]', '[-]', '[\]', '[*]']
            print_over = False
            # check if the current line contains progress marker
            for marker in progress_markers:
                if text.find(marker) != -1:
                    print_over = True                    
                    break
            if print_over:
                print_over = False
                # check if we need to overwrite last line
                # (it contains progress marker)
                last_line_text = ctrl.GetLineText(line_number)                
                for marker in progress_markers:
                    if last_line_text.find(marker) != -1:
                        print_over = True
                        break            
            if print_over:
                line_end = ctrl.GetLastPosition()
                line_start = ctrl.GetLastPosition() - \
                                ctrl.GetLineLength(line_number) - _NEWLINE_LEN                                                
                ctrl.Remove(line_start, line_end)

            ctrl.AppendText(text)
        else:
            ctrl.SetValue(text)    
        
    def GetExitCode(self):
        return self._returnCode 
   
    def _SpawnProcess(self, cmd, priority):
        # initialise environment var TMPDIR
        try:
            if os.getenv('TMPDIR') is None:
                os.putenv('TMPDIR', 
                           re.sub('([A-Za-z]):[/\\\\]', r'/cygdrive/\1/', 
                           tempfile.gettempdir()).replace('\\', '/'))
            Utils.SetCygwinTemp()
        except Exception, e:
            print str(e)            
            
        # check that we got the command line        
        if cmd is None:   
            raise Process.ProcessError('Could not start process. No Command Line specified')                                                     
        
        # start our process    
        try:                
            # check if the file exists first
            executable = cmd.split('" ' ,1)[0].lstrip('"')
            if not os.path.exists(executable):
                raise Process.ProcessError('Could not start process.\n%s\nFile does not exist.' % executable)                
            # create our stdout implementation that updates status window                
            self._out = StatusUpdateBuffer(self, self.ThreadUpdateStatus, self.ThreadFinished)                                                    
            self._proc = Process.ProcessProxy(cmd, stdout=self._out, priority=priority)                                                                
            self._proc.wait(_WAIT_NOWAIT)
        except Exception, e:             
            if isinstance(e, Process.ProcessError):
                if e.errno != Process.ProcessProxy.WAIT_TIMEOUT:                                       
                    raise Process.ProcessError('Could not start process:\n%s\nError: %s' % (cmd, str(e)))                     
            else:
                raise Process.ProcessError('Could not start process:\n%s\nError: %s' % (cmd, str(e)))

    def OnInitDialog(self, event):
        # start animation
        # we need to have our window drawn before that
        # to display transparent animation properly
        # therefore start it in OnInitDialog   
        self.throbber.Start()
        event.Skip()
                    	                	    
