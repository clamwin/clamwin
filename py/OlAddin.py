#-----------------------------------------------------------------------------
# Name:        OlAddin.py
# Product:     ClamWin Free Antivirus
#
# Author:      alch [alch at users dot sourceforge dot net]
#
# Created:     2004/31/03
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
# ClamWin Outlook Addin
# Parts of the code based on SpamBayes Source Code (Outlook2000/addin.py)
# Thanks to Sean True and Mark Hammond

# Copyright (C) 2002-2003 Python Software Foundation; All Rights Reserved
# 
# The Python Software Foundation (PSF) holds copyright on all material
# in this project.  You may use it under the terms of the PSF license:
# 
# PSF LICENSE AGREEMENT FOR THE SPAMBAYES PROJECT
# -----------------------------------------------
# 
# 1. This LICENSE AGREEMENT is between the Python Software Foundation
# ("PSF"), and the Individual or Organization ("Licensee") accessing and
# otherwise using the spambayes software ("Software") in source or binary
# form and its associated documentation.
# 
# 2. Subject to the terms and conditions of this License Agreement, PSF
# hereby grants Licensee a nonexclusive, royalty-free, world-wide
# license to reproduce, analyze, test, perform and/or display publicly,
# prepare derivative works, distribute, and otherwise use the Software
# alone or in any derivative version, provided, however, that PSF's
# License Agreement and PSF's notice of copyright, i.e., "Copyright (c)
# 2002-2003 Python Software Foundation; All Rights Reserved" are retained
# the Software alone or in any derivative version prepared by Licensee.
# 
# 3. In the event Licensee prepares a derivative work that is based on
# or incorporates the Software or any part thereof, and wants to make
# the derivative work available to others as provided herein, then
# Licensee hereby agrees to include in any such work a brief summary of
# the changes made to the Software.
# 
# 4. PSF is making the Software available to Licensee on an "AS IS"
# basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
# IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND
# DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
# FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF THE SOFTWARE WILL NOT
# INFRINGE ANY THIRD PARTY RIGHTS.
# 
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF THE
# SOFTWARE FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS
# A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING THE SOFTWARE,
# OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.
# 
# 6. This License Agreement will automatically terminate upon a material
# breach of its terms and conditions.
# 
# 7. Nothing in this License Agreement shall be deemed to create any
# relationship of agency, partnership, or joint venture between PSF and
# Licensee.  This License Agreement does not grant permission to use PSF
# trademarks or trade name in a trademark sense to endorse or promote
# products or services of Licensee, or any third party.
# 
# 8. By copying, installing or otherwise using the Software, Licensee
# agrees to be bound by the terms and conditions of this License
# Agreement.

import SetUnicode
import sys
import os
import re
import tempfile
import warnings
import traceback
import _winreg
import Utils
import Config
import Process
import SplashScreen

# *sigh* - this is for the binary installer, and for the sake of one line
# that is implicit anyway, I gave up
import encodings

try:
    True, False
except NameError:
    # Maintain compatibility with Python 2.2
    True, False = 1, 0

# We have lots of locale woes.  The short story:
# * Outlook/MAPI will change the locale on us as some predictable
#   times - but also at unpredictable times.
# * Python currently insists on "C" locale - if it isn't, subtle things break,
#   such as floating point constants loaded from .pyc files.
# * Our config files also want a consistent locale, so periods and commas
#   are the same when they are read as when they are written.
# So, at a few opportune times, we simply set it back.
# We do it here as early as possible, before any imports that may see this
#
# See also [725466] Include a proper locale fix in Options.py,
# assorted errors relating to strange math errors, and spambayes-dev archives,
# starting July 23 2003.
import locale
locale.setlocale(locale.LC_NUMERIC, "C")

from win32com import universal
from win32com.server.exception import COMException
from win32com.client import gencache, DispatchWithEvents, Dispatch
import win32api
import pythoncom
from win32com.client import constants, getevents

import win32gui, win32con, win32clipboard # for button images!
from win32com.mapi import mapi, mapiutil, mapitags
import RedirectStd

_DEBUG=False

def dbg_print(*args):    
    if not _DEBUG:
        return
    else:
        print args
    
# As MarkH assumed, and later found to back him up in:
# http://www.slipstick.com/dev/comaddins.htm:
# On building add-ins for multiple Outlook versions, Randy Byrne writes in
# the microsoft.public.office.developer.com.add_ins newsgroup, "The best
# practice is to compile your Add-in with OL2000 and MSO9.dll. Then your
# add-in will work with both OL2000 and OL2002, and CommandBar events will
# work with both versions. If you need to use any specific OL2002 or
# Office 10.0 Object Library calls, you can use late binding to address
# those issues. The CommandBar Events are the same in both Office
# 2000 and Office XP."
# So that is what we do: specify the minimum versions of the typelibs we
# can work with - ie, Outlook 2000.

# win32com generally checks the gencache is up to date (typelib hasn't
# changed, makepy hasn't changed, etc), but when frozen we dont want to
# do this - not just for perf, but because they don't always exist!
bValidateGencache = not hasattr(sys, "frozen")
# Generate support so we get complete support including events
gencache.EnsureModule('{00062FFF-0000-0000-C000-000000000046}', 0, 9, 0,
                        bForDemand=True, bValidateFile=bValidateGencache) # Outlook 9
gencache.EnsureModule('{2DF8D04C-5BFA-101B-BDE5-00AA0044DE52}', 0, 2, 1,
                        bForDemand=True, bValidateFile=bValidateGencache) # Office 9
# We the "Addin Designer" typelib for its constants
gencache.EnsureModule('{AC0714F2-3D04-11D1-AE7D-00A0C90F26F4}', 0, 1, 0,
                        bForDemand=True, bValidateFile=bValidateGencache)
# ... and also for its _IDTExtensibility2 vtable interface.
universal.RegisterInterfaces('{AC0714F2-3D04-11D1-AE7D-00A0C90F26F4}', 0, 1, 0,
                             ["_IDTExtensibility2"])

try:
    from win32com.client import CastTo, WithEvents
except ImportError:
    print "*" * 50
    print "You appear to be running a win32all version pre 151, which is pretty old"
    print "I'm afraid it is time to upgrade"
    raise
# we seem to have all the COM support we need - let's rock!


# Button/Menu and other UI event handler classes
class ButtonEvent:
    def Init(self, handler, *args):
        self.handler = handler
        self.args = args
    def Close(self):
        self.handler = self.args = None
    def OnClick(self, button, cancel):
        # Callback from Outlook - locale may have changed.
        locale.setlocale(locale.LC_NUMERIC, "C") # see locale comments above
        self.handler(*self.args)

# no ui yet, no commands
def HelpAbout():
    try:                           
        curDir = Utils.GetCurrentDir(True)
        Utils.SpawnPyOrExe(os.path.join(curDir, 'ClamWin'), ' --mode=about')        
    except Exception, e:            
        win32gui.MessageBox(GetWindow(), 'An error occured in ClamWin Free Antivirus About Box.\n' + str(e), 'ClamWin Free Antivirus', win32con.MB_OK | win32con.MB_ICONERROR)

# Helpers to work with images on buttons/toolbars.
def SetButtonImage(button, fname):
    # whew - http://support.microsoft.com/default.aspx?scid=KB;EN-US;q288771
    # shows how to make a transparent bmp.
    # Also note that the clipboard takes ownership of the handle -
    # thus, we can not simply perform this load once and reuse the image.
    # Hacks for the binary - we can get the bitmaps from resources.
    
    if not os.path.isabs(fname):
        # images relative to the application path
        fname = os.path.join(Utils.GetCurrentDir(False),"images", fname)
        if not os.path.isfile(fname):
            print "WARNING - Trying to use image '%s', but it doesn't exist" % (fname,)
            return None
        handle = win32gui.LoadImage(0, fname, win32con.IMAGE_BITMAP, 0, 0, win32con.LR_DEFAULTSIZE | win32con.LR_LOADFROMFILE)
    win32clipboard.OpenClipboard()
    win32clipboard.SetClipboardData(win32con.CF_BITMAP, handle)
    win32clipboard.CloseClipboard()
    button.Style = constants.msoButtonIconAndCaption
    button.PasteFace()
    
def GetWindow():
    hwnd = 0
    try:
        hwnd = win32gui.GetActiveWindow()
    except:
        hwnd = win32gui.GetForegroundWindow()   
    return hwnd        
    
class ScanError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)        

def ScanFile(path, config, attname):        
    # initialise environment var TMPDIR
    # for clamav    
    try:
        if os.getenv('TMPDIR') is None:
            os.putenv('TMPDIR', tempfile.gettempdir().replace('\\', '/'))
                       #re.sub('([A-Za-z]):[/\\\\]', r'/cygdrive/\1/', 
                       #tempfile.gettempdir()).replace('\\', '/'))
        #Utils.SetCygwinTemp()
    except Exception, e:
        print str(e)                    
            
        
    logfile = os.path.split(path)[0]+'\\Virus Deleted by ClamWin.txt'
    cmd = '--tempdir "%s"' % tempfile.gettempdir().replace('\\', '/').rstrip('/')

    path = path.replace('\\', '/')
    cmd = '--max-ratio=0 --stdout --database="%s" --log="%s" "%s"' % \
            (config.Get('ClamAV', 'Database'), logfile, path)
         
    cmd = cmd.replace('\\', '/')
    cmd = '"%s" %s' % (config.Get('ClamAV', 'ClamScan'), cmd)
                
    scanstatus = ''        
    retcode = 1
    proc = None
    try:        
        proc = Process.ProcessOpen(cmd)
        retcode = proc.wait()   
        dbg_print('scanning completed with %i' % retcode)  
        # returns 100 if a damaged rar archive was found
        if retcode >= 100 and retcode <= 106: 
            dbg_print('damaged archive - ignoring')  
            retcode = 0            
    except Exception, e:
        if proc is not None:
            proc.close()
        safe_remove(logfile)
        raise ScanError('An Error occured whilst starting clamscan: %s' % str(e))
        
    if proc is not None:
        proc.close()
    if retcode == 0:
        virusFound = False
    # check the retrun Code
    elif retcode == 1:
        virusFound = True
    else:
        # error, raise an exception
        try:
            error = file(logfile, 'rt').read()
            #error = re.sub('/cygdrive/([A-Za-z])/', r'\1:/', error).replace('/', '\\')
            safe_remove(logfile)
        except Exception, e:
            raise ScanError('An Error occured reading clamscan report: %s' % str(e))
        raise ScanError('An Error occured whilst scanning:\n%s' % error)
                    
    # replace \n's with \r\n's   
    # so it can be shown in notepad
    # also replace temp filename with real attachment name
    try:
        text = file(logfile, 'rt').read().replace('\n', '\r\n').replace(path, attname)        
        file(logfile, 'wt').write(text)
    except Exception, e:
        safe_remove(logfile)
        raise ScanError('An Error occured whilst converting clamscan report: %s' % str(e))    
    return (virusFound, logfile)
            
# returns 0 if everything is okay, or number fo infected files                     
def ScanMailItem(item, sending, added_attachments = None):     
    if not item.Attachments.Count:
        return 0
    
    config_file = os.path.join(Utils.GetProfileDir(True),'ClamWin.conf')
    if not os.path.isfile(config_file):
        config_file = 'ClamWin.conf'                    
    config = Config.Settings(config_file)    
    config.Read()
    
    # get the virus database version from daily.cvd
    # we will need it when deciding if the message should be rescanned;
    
    # after message is scanned the current daily.cvd version is saved;
    # then when message is next accessed we compare the saved version
    # with the current version and if they're different then 
    # we rescan the message
    
    # disabled as it is of little use and causes outlook 
    # to switch to RTF winmail.dat format
    # when replying or forwarding a scanned message
        
    # virdb_ver = Utils.GetDBInfo(os.path.join(config.Get('ClamAV', 'Database'), 'daily.cvd'))[0]
    # dbg_print('Daily.cvd Version: %s' % str(virdb_ver))
    
    # check that there are database files and display an error ballon if not
    hasdb = Utils.CheckDatabase(config)      
    if not hasdb:
        if config.Get('UI', 'TrayNotify') == '1':
            import win32gui
            tray_notify_params = (('Virus Definitions Database Not Found! Please download it now.', 
            -1, win32gui.NIIF_ERROR, 30000), None)
            # show balloon
            Utils.ShowBalloon(-1, tray_notify_params)
            return 0

    
    dir = ''; path = ''; statusfile = ''        
    infected = []; attachments = []
    try:
        attachments = item.Attachments            
        
        # see if the message has already been scanned
        # disabled as it is of little use and causes outlook 
		  # to switch to RTF winmail.dat format
        # when replying or forwarding a scanned message

        #userProps = item.UserProperties    
        #prop = userProps.Find('Scanned By ClamWin')
        #if prop is not None:            
        #    if prop.Value == virdb_ver:
        #        dbg_print('ScanMailItem: Already Scanned')
        #        return 0
            
        waitCursor = WaitCursor()              
        for num in range(1, attachments.Count+1):
            att = attachments.Item(num)
            
            # create a temporary folder to save the attachment to
            dir = tempfile.mktemp()
            os.mkdir(dir)
            path = tempfile.mktemp(dir=dir)
            dbg_print('ScanMailItem: saving attachment - ', path)
            try:
                att.SaveAsFile(path)
            except pythoncom.com_error, e:
                # ignore "Object not found" save errors
                # most likely the file won't be saved by outlook anyway
                hr, desc, exc, argErr = e                
                if exc[5] in (-2147221233, -2147024894, -2147467259): #0x8004010F, 0x80070002, 0x80040005
                    dbg_print('error saving attachment to %s. Error: %s' % (path, str(exc)))
                    safe_remove(dir)
                    continue
                else:
                    raise e
        
            try:
                attName = att.DisplayName.encode('ascii', 'replace')
            except:
                attName = 'Attached File'
                
            code, statusfile = ScanFile(path, config, attName)
                            
            # remove saved and scanned attachment  file
            safe_remove(path)                              
            if code == 0:            
                # no viruses found
                # remove the scan status file
                # along with temp dir
                safe_remove(statusfile, True)        
            else:                            
                # virus detected
                if sending:     
                    # for messages being sent display message box once and exit               
                    try:                    
                        msg = file(statusfile, 'rt').read()                                                
                        # remove the scan status file
                        # along with temp dir
                        safe_remove(statusfile, True)
                    except Exception, e:
                        msg = 'ClamWin Free Antivirus could not scan file%s\n.Error: %s' % (statusfile, str(e))                        
                    win32gui.MessageBox(GetWindow(), msg, 'ClamWin Free Antivirus', win32con.MB_ICONERROR | win32con.MB_OK)
                    return 1
                else:
                    # bugfix [930909]
                    # remove str(att.DisplayName) - was causing unicode woes
                    infected.append((att, statusfile))

        # remove infected attachments            
        for info in infected:
            dbg_print('ScanMailItem: removing attachment - ', info[0].DisplayName)
            info[0].Delete()                            
            
        # add status files instead of the infected attachments
        # can't have it in the for loop above because in some cases
        # (like when a message is opened form the .msg file
        # outlook saves the message when you add the attachment
        # and screwes the indices            
        for info in infected:
            dbg_print('ScanMailItem: adding attachment - ', info[1])
            attachments.Add(Source=info[1], Type=constants.olByValue)                                
            # remove the scan status file
            # along with temp dir
            safe_remove(info[1], True)                   

        # add persistent property to the message
        # so we don't have to scan it in future
        # we save the daily.cvd version        
        # so message gets rescanned if database is updated
        
        # disabled as it is of little use and causes outlook 
        # to switch to RTF winmail.dat format
        # when replying or forwarding a scanned message
        #if virdb_ver is not None:
        #    prop = userProps.Add('Scanned By ClamWin', constants.olNumber, False)
        #    prop.Value = virdb_ver
        #    dbg_print('ScanMailItem: Saving MailItem')
        #    try:
	     #      item.Save()           
        #    except pythoncom.com_error, e:
        #       # read only message store (hotmail, etc)
        #        # ignore save errors
        #        hr, desc, exc, argErr = e
        #        if hr != -2147352567:
        #            raise e
        
        if len(infected) > 0:                        
            # for Outlook 2000 we need to display a message box in order to 
            # warn a user becuase it will not change the attachments info in
            # the event handlers
            if int(item.Application.Version.split('.', 1)[0]) < 10:                
                msg = 'ClamWin Free Antivirus has detected a virus in the message attachments!'
                win32gui.MessageBox(GetWindow(), msg, 'Virus Detected!', win32con.MB_ICONERROR | win32con.MB_OK)                            
            elif config.Get('UI', 'TrayNotify') == '1':       
                # show balloon in outlook 2002 +
                tray_notify_params = (('Virus has been detected in an email attachment! The attachment was replaced with the report file.', 1, 
                                win32gui.NIIF_ERROR, 30000),
                ('An error occured whilst scanning email message.', 0, 
                win32gui.NIIF_WARNING, 30000))
                Utils.ShowBalloon(1, tray_notify_params)

            return len(infected)
        else:
            return 0                         
    except Exception, e:
        # cleanup any created files and folders
        safe_remove(path)
        safe_remove(statusfile)                
        for info in infected:
            safe_remove(info[1], True) 
        safe_remove(dir)   
        
        # display error   
        win32gui.MessageBox(GetWindow(), str(e), 'ClamWin Free Antivirus', win32con.MB_OK | win32con.MB_ICONERROR)        
        return True        

    return len(infected)

def safe_remove(path, removeLastDir = False):
    try:
        if os.path.isfile(path):
            os.remove(path)  
        else:
            os.rmdir(path)  
        if removeLastDir:
            dir = os.path.split(path)[0]              
            if os.path.exists(dir):
                os.rmdir(dir)              
    except Exception, e:
        print 'Could not remove file: %s. Error: %s' % (path, str(e))

class WaitCursor:    
    def __init__(self):
        self._hCursor = win32gui.SetCursor(win32gui.LoadCursor(0, win32con.IDC_WAIT))    
    def __del__(self):
        win32gui.SetCursor(self._hCursor)    

# Base Class for Explorer, Inspector and MailItem Outlook Objects           
class ObjectWithEvents:
    def Init(self, collection):    
        self.collection = collection
        
    def OnClose(self):      
        if hasattr(self.collection.host, 'DisconnectEventHandler'):
            self.collection.host.DisconnectEventHandler(self.collection)   
        self.collection._DoDeadObject(self)
        self.collection = None        
        self.close()         
        # disconnect events.

# EventSink Base Class for Explorers, Inspectors and MailItems Outlook Object Collections            
class ObjectsEvent:
    def Init(self, classWithEvents, host):
        self.objects = []        
        self.classWithEvents = classWithEvents        
        # host object that created EventSink
        self.host = host

    def Close(self):        
        while self.objects:
            self._DoDeadObject(self.objects[0])
        self.objects = None
        self.close()

    def _DoNewObject(self, obj):
        obj = DispatchWithEvents(obj, self.classWithEvents)
        obj.Init(self)
        self.objects.append(obj)
        return obj

    def _DoDeadObject(self, obj):        
        self.objects.remove(obj)
        obj = None        
            
        
        
# A class that manages an "Outlook Explorer" - that is, a top-level window
# All UI elements are managed here, and there is one instance per explorer.
class ExplorerWithEvents(ObjectWithEvents):
    def Init(self, explorers_collection):
        dbg_print('ExplorerWithEvents:Init')
        self.have_setup_ui = False        
        self.event_handlers = []                
        ObjectWithEvents.Init(self, explorers_collection)

    def SetupUI(self):               
        # find Help->About Outlook menu
        aboutOutlook = self.CommandBars.FindControl(
                            Type = constants.msoControlButton,
                            Id = 927)
        
        if aboutOutlook is None:
            return
                
        popup = aboutOutlook.Parent
        if popup is None:
            return
        # Add Help->About Clamwin menu item 
        child = self._AddControl(popup,
                       constants.msoControlButton,
                       ButtonEvent, (HelpAbout, ),
                       Caption="&About ClamWin Free Antivirus",
                       TooltipText = "Shows the ClamWin About Box",
                       Enabled = True,
                       Visible=True,
                       Tag = "ClamWin.About")
        self.have_setup_ui = True
                           
    def _AddControl(self,
                    parent, # who the control is added to
                    control_type, # type of control to add.
                    events_class, events_init_args, # class/Init() args
                    **item_attrs): # extra control attributes.
        assert item_attrs.has_key('Tag'), "Need a 'Tag' attribute!"
        image_fname = None
        if 'image' in item_attrs:
            image_fname = item_attrs['image']
            del item_attrs['image']

        tag = item_attrs["Tag"]
        item = self.CommandBars.FindControl(
                        Type = control_type,
                        Tag = tag)
        if item is None:
            # Now add the item itself to the parent.
            try:
                item = parent.Controls.Add(Type=control_type, Temporary=True)
            except pythoncom.com_error, e:               
                print "FAILED to add the toolbar item '%s' - %s" % (tag,e)
                return
            if image_fname:
                # Eeek - only available in derived class.
                assert control_type == constants.msoControlButton
                but = CastTo(item, "_CommandBarButton")
                SetButtonImage(but, image_fname)
            # Set the extra attributes passed in.
            for attr, val in item_attrs.items():
                setattr(item, attr, val)
        # didn't previously set this, and it seems to fix alot of problem - so
        # we set it for every object, even existing ones.
        item.OnAction = "<!" + OutlookAddin._reg_progid_ + ">"

        # Hook events for the item, but only if we haven't already in some
        # other explorer instance.
        if events_class is not None and tag not in self.collection.button_event_map:
            item = DispatchWithEvents(item, events_class)
            item.Init(*events_init_args)
            # We must remember the item itself, else the events get disconnected
            # as the item destructs.
            self.collection.button_event_map[tag] = item
        return item

    # The Outlook event handlers
    def OnActivate(self): 
        dbg_print('ExplorerWithEvents:OnActivate')
        # See comments for OnNewExplorer below.
        # *sigh* - OnActivate seems too early too for Outlook 2000,
        # but Outlook 2003 seems to work here, and *not* the folder switch etc
        # Outlook 2000 crashes when a second window is created and we use this
        # event
        # OnViewSwitch however seems useful, so we ignore this.
        pass

    def OnSelectionChange(self):         
        dbg_print('ExplorerWithEvents:OnSelectionChange')
        # See comments for OnNewExplorer below.
        if not self.have_setup_ui:
            self.SetupUI()
        if self.IsPaneVisible(constants.olPreview) and \
            self.Selection.Count == 1:            
            item = self.Selection.Item(1)
            if item.Class == constants.olMail and item.Sent:                                                  
                ScanMailItem(item, False)                       
        
    def OnClose(self):                                
        dbg_print('ExplorerWithEvents:OnClose')
        for event_handler in self.event_handlers:        
            event_handler.Close()
        self.event_handler = []        
        ObjectWithEvents.OnClose(self)

    def OnBeforeFolderSwitch(self, new_folder, cancel):
        dbg_print('ExplorerWithEvents:OnBeforeFolderSwitch')
        pass

    def OnFolderSwitch(self):        
        # Yet another work-around for our event timing woes.  This may
        # be the first event ever seen for this explorer if, eg,
        # "Outlook Today" is the initial Outlook view.
        dbg_print('ExplorerWithEvents:OnFolderSwitch')
        if not self.have_setup_ui:
            self.SetupUI()

    def OnBeforeViewSwitch(self, new_view, cancel):
        dbg_print('ExplorerWithEvents:OnBeforeViewSwitch')
        pass

    def OnViewSwitch(self):        
        dbg_print('ExplorerWithEvents:OnViewSwitch')
        if not self.have_setup_ui:
            self.SetupUI()
            
    

# Events from our "Explorers" collection (not an Explorer instance)
class ExplorersEvent(ObjectsEvent):
    def Init(self, olAddin):
        dbg_print('ExplorersEvent:Init')
        self.button_event_map = {}
        ObjectsEvent.Init(self, ExplorerWithEvents, olAddin)    

    def _DoDeadObject(self, obj):
        dbg_print('ExplorersEvent:_DoDeadObject')
        ObjectsEvent._DoDeadObject(self, obj)
        if len(self.objects)==0:            
            # No more explorers - disconnect all events.
            # (not doing this causes shutdown problems)
            for tag, button in self.button_event_map.items():
                closer = getattr(button, "Close", None)
                if closer is not None:
                    closer()
            self.button_event_map = {}            

    def OnNewExplorer(self, explorer):
        # NOTE - Outlook has a bug, as confirmed by many on Usenet, in
        # that OnNewExplorer is too early to access the CommandBars
        # etc elements. We hack around this by putting the logic in
        # the first OnActivate call of the explorer itself.
        # Except that doesn't always work either - sometimes
        # OnActivate will cause a crash when selecting "Open in New Window",
        # so we tried OnSelectionChanges, which works OK until there is a
        # view with no items (eg, Outlook Today) - so at the end of the
        # day, we can never assume we have been initialized!        
        dbg_print('ExplorersEvent:OnNewExplorer')
        self._DoNewObject(explorer)

# A class that manages an "Outlook Inspector" - that is, a message or contact window
class InspectorWithEvents(ObjectWithEvents):
    def Init(self, inspectors_collection):               
        dbg_print('InspectorWithEvents:Init')
        self.event_handlers = []        
        item = self.CurrentItem        
        if item.Class == constants.olMail:                                            
            # Create EventHandler for MailItem
            mailitem_events = WithEvents(item, MailItemsEvent)
            mailitem_events.Init(self)        
            mailitem_events._DoNewObject(item)            
            self.event_handlers.append(mailitem_events)            
        ObjectWithEvents.Init(self, inspectors_collection)
    
    # The Outlook event handlers
    def OnActivate(self):
        dbg_print('InspectorWithEvents:OnActivate')
        pass                                                     
        
    def OnClose(self):     
        dbg_print('InspectorWithEvents:OnClose')
        for handler in self.event_handlers:        
            handler.Close()
        self.event_handlers = []
        ObjectWithEvents.OnClose(self)
        
    def DisconnectEventHandler(self, obj):
        dbg_print('InspectorWithEvents:DisconnectEventHandler')
        obj.close()
        self.event_handlers.remove(obj)      
        
# Events from our "Inspectors" collection
class InspectorsEvent(ObjectsEvent):
    def Init(self, host):          
        dbg_print('InspectorsEvent:Init')
        ObjectsEvent.Init(self, InspectorWithEvents, host)  
        
    def OnNewInspector(self, inspector):   
        dbg_print('InspectorsEvent:OnNewInspector')
        self._DoNewObject(inspector)  
        

# A class that manages an "Outlook MailItem" - that is, a message 
class MailItemWithEvents(ObjectWithEvents):
    def Init(self, items_collection):      
        dbg_print('MailItemWithEvents:Init')
        ObjectWithEvents.Init(self, items_collection)
        self._scanned = False
        self._close_inspector = False
        self._num_infected = 0
        
    def OnClose(self, cancel):      
        dbg_print('MailItemWithEvents:OnClose')
        host = self.collection.host
        ObjectWithEvents.OnClose(self)
        if self._close_inspector:
            # need to disconnect Inspectors Collection ebent handler because
            # Outlook 2000 doesn't fire Inspector:Close event
            # for sent messages and remains hanging around after exit
            dbg_print('MailItemWithEvents:OnClose host.OnClose()')                    
            host.OnClose()
        
        

    def OnRead(self):  
        dbg_print('MailItemWithEvents:OnRead')
        # OnOpen event is not always fired
        # only when a user double-clicks the message
        # so we scan here and reinitialize attachmets
        if self.Sent and not self._scanned:             
            dbg_print('MailItemWithEvents:OnRead scanning')
            self._scanned = True
            self._num_infected = ScanMailItem(self, False)  
            
        
    def OnOpen(self, cancel):  
        dbg_print('MailItemWithEvents:OnOpen')
        if not self._scanned and self.Sent :      
            # in case OnRead has not been called
            dbg_print('MailItemWithEvents:OnOpen scanning')
            self._scanned = True
            self._num_infected = ScanMailItem(self, False)  
        elif  self._num_infected:
            # a bit of trickery here - remove and reinsert attachments 
            # so that bloody outlook shows our changes
            dbg_print('MailItemWithEvents:OnOpen Scanned Earlier')
            try:
                saved_attachments = []            
                for i in range(self.Attachments.Count - self._num_infected + 1, self.Attachments.Count + 1):
                    att = self.Attachments.Item(i)
                    # save attachment to a temp file
                    name = att.DisplayName
                    dir = tempfile.mktemp()
                    os.mkdir(dir)
                    filename = os.path.join(dir, name)
                    att.SaveAsFile(filename)
                    saved_attachments.append((att, filename))
            
                for saved in saved_attachments:
                    saved[0].Delete()
                
                for saved in saved_attachments:
                    self.Attachments.Add(Source=saved[1], Type=constants.olByValue)
                for saved in saved_attachments:
                    safe_remove(saved[1], True)                
                saved_attachments = []    
                
                try:
                   self.Save()           
                except pythoncom.com_error, e:
                    # read only message store (hotmail, etc
                    # ignore save errors
                    hr, desc, exc, argErr = e
                    if hr != -2147352567:
                        raise e                    
            except Exception, e:
                for saved in saved_attachments:
                    safe_remove(saved[1], True)
                msg = 'ClamWin Free Antivirus could not replace an attachment. Error: %s' % str(e)
                win32gui.MessageBox(GetWindow(), msg, 'ClamWin Free Antivirus!', win32con.MB_ICONERROR | win32con.MB_OK)                                                                                      
    
    def OnWrite(self, cancel):
        dbg_print('MailItemWithEvents:OnWrite')
        # disabled as it is of little use and causes outlook 
        # to switch to RTF winmail.dat format
        # when replying or forwarding a scanned message

        #if self.Sent and not self._scanned:
        #    prop = self.UserProperties.Find('Scanned By ClamWin')
        #    if prop is not None:
        #        prop.Delete()
                                
    def OnSend(self, cancel):        
        dbg_print('MailItemWithEvents:OnSend')
        virus_found = (ScanMailItem(self, True) > 0)
        cancel = virus_found
        # disconnect Inspectors Collection event handler
        # in OnClose
        self._close_inspector = True
        return not cancel
        

# Events from our "MailItems" collection
class MailItemsEvent(ObjectsEvent):
    def Init(self, host):  
        dbg_print('MailItemsEvent:Init')
        ObjectsEvent.Init(self, MailItemWithEvents, host)  
        
    def OnItemAdd(self, mailitem):               
        dbg_print('MailItemsEvent:OnItemAdd')
        self._DoNewObject(mailitem)  
                    
# The outlook Plugin COM object itself.
class OutlookAddin(ObjectsEvent):
    _com_interfaces_ = ['_IDTExtensibility2']
    _public_methods_ = []
#    _reg_clsctx_ = pythoncom.CLSCTX_INPROC_SERVER
    _reg_clsid_ = "{E77FA584-1433-4af3-800D-AEC49BCCCB11}"
    _reg_progid_ = "ClamWin.OutlookAddin"
    _reg_policy_spec_ = "win32com.server.policy.EventHandlerPolicy"

    def __init__(self):        
        self.application = None       
        # check the debug flag iun the registry
        global _DEBUG
        try:
            subkey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\\ClamWin')            
            _DEBUG = int(_winreg.QueryValueEx(subkey, "Debug")[0])==1            
        except:
            _DEBUG = False                

    def OnConnection(self, application, connectMode, addin, custom):            
        dbg_print('OutlookAddin:OnConnection')
        # Handle failures during initialization so that we are not
        # automatically disabled by Outlook.
        locale.setlocale(locale.LC_NUMERIC, "C") # see locale comments above
        try:
            self.application = application
            self.event_handlers = [] # create at OnStartupComplete            

            if connectMode == constants.ext_cm_AfterStartup:
                # We are being enabled after startup, which means we don't get
                # the 'OnStartupComplete()' event - call it manually so we
                # bootstrap code that can't happen until startup is complete.
                self.OnStartupComplete(None)
        except:
            print "Error connecting to Outlook!"
            traceback.print_exc()
            print "There was an error initializing the ClamWin addin\r\n\r\n"\
                "Please re-start Outlook and try again."

    def OnStartupComplete(self, custom):
        dbg_print('OutlookAddin:OnStartupComplete')
        Utils.CreateProfile()
        # display SplashScreen
        try:            
            splash = os.path.join(Utils.GetCurrentDir(False), "img\\Splash.bmp")
            SplashScreen.ShowSplashScreen(splash, 5)
        except Exception, e:           
            print "An error occured whilst displaying the spashscreen %s. Error: %s." % (splash, str(e))
        # Setup all our filters and hooks.  We used to do this in OnConnection,
        # but a number of 'strange' bugs were reported which I suspect would
        # go away if done during this later event - and this later place
        # does seem more "correct" than the initial OnConnection event.
        # Toolbar and other UI stuff must be setup once startup is complete.
        explorers = self.application.Explorers
        # and Explorers events so we know when new explorers spring into life.
        explorers_events = WithEvents(explorers, ExplorersEvent)
        explorers_events.Init(self)        
        # And hook our UI elements to all existing explorers
        for i in range(explorers.Count):
            explorer = explorers.Item(i+1)
            explorer = explorers_events._DoNewObject(explorer)
            explorer.OnFolderSwitch()
        self.event_handlers.append(explorers_events)
        
        inspectors = self.application.Inspectors
        # and Inspectors events so we know when new inspectors spring into life.
        inspectors_events = WithEvents(inspectors, InspectorsEvent)
        inspectors_events.Init(self)        
        # And elements to all existing inspectors
        for i in range(inspectors.Count):
            inspector = inspectors.Item(i+1)
            inspector = inspectors_events._DoNewObject(inspector)
        self.event_handlers.append(inspectors_events)
        # release application object otherwise Outlook2003 won't
        # shutdown if we are running in out-of-process EXE
        self.application = None    
        
    def OnDisconnection(self, mode, custom):
        dbg_print('ClamWin - Disconnecting from Outlook')
        for handler in self.event_handlers:        
            handler.Close()
        self.event_handlers = []        
        self.application = None

        print "Addin terminating: %d COM client and %d COM servers exist." \
              % (pythoncom._GetInterfaceCount(), pythoncom._GetGatewayCount())
        try:
            # will be available if "python_d addin.py" is used to
            # register the addin.
            total_refs = sys.gettotalrefcount() # debug Python builds only
            print "%d Python references exist" % (total_refs,)
        except AttributeError:
            pass
        
    def OnAddInsUpdate(self, custom):
        pass

    def OnBeginShutdown(self, custom):
        dbg_print('OutlookAddin:OnBeginShutdown')
        pass

def _DoRegister(klass, root):
    key = _winreg.CreateKey(root,
                            "Software\\Microsoft\\Office\\Outlook\\Addins")
    subkey = _winreg.CreateKey(key, klass._reg_progid_)
    _winreg.SetValueEx(subkey, "CommandLineSafe", 0, _winreg.REG_DWORD, 0)
    _winreg.SetValueEx(subkey, "LoadBehavior", 0, _winreg.REG_DWORD, 3)
    _winreg.SetValueEx(subkey, "Description", 0, _winreg.REG_SZ, "ClamWin Free Antivirus")
    _winreg.SetValueEx(subkey, "FriendlyName", 0, _winreg.REG_SZ, "ClamWin Free Antivirus")

# Note that Addins can be registered either in HKEY_CURRENT_USER or
# HKEY_LOCAL_MACHINE.  If the former, then:
# * Only available for the user that installed the addin.
# * Appears in the 'COM Addins' list, and can be removed by the user.
# If HKEY_LOCAL_MACHINE:
# * Available for every user who uses the machine.  This is useful for site
#   admins, so it works with "roaming profiles" as users move around.
# * Does not appear in 'COM Addins', and thus can not be disabled by the user.

# Note that if the addin is registered in both places, it acts as if it is
# only installed in HKLM - ie, does not appear in the addins list.
# For this reason, the addin can be registered in HKEY_LOCAL_MACHINE
# by executing 'regsvr32 /i:hkey_local_machine outlook_addin.dll'
# (or 'python addin.py hkey_local_machine' for source code users.
# Note to Binary Builders: You need py2exe dated 8-Dec-03+ for this to work.

# Called when "regsvr32 /i:whatever" is used.  We support 'hkey_local_machine'
# and hkey_current_user
def DllInstall(bInstall, cmdline):
    klass = OutlookAddin
    if bInstall:
        # Unregister the old installation, if one exists.
        DllUnregisterServer()
        rootkey = None
        if cmdline.lower().find('hkey_local_machine')>=0:                    
            rootkey = _winreg.HKEY_LOCAL_MACHINE
            print "Registering (in HKEY_LOCAL_MACHINE)..."
        elif cmdline.lower().find('hkey_current_user')>=0:                    
            rootkey = _winreg.HKEY_CURRENT_USER
            print "Registering (in HKEY_CURRENT_USER)..."
        if rootkey is not None:
            # Don't catch exceptions here - if it fails, the Dll registration
            # must fail.
            _DoRegister(klass, _winreg.HKEY_LOCAL_MACHINE)
            print "Registration Complete"            

def DllRegisterServer():
    klass = OutlookAddin
    
    # *sigh* - we used to *also* register in HKLM, but as above, this makes
    # things work like we are *only* installed in HKLM.  Thus, we explicitly
    # remove the HKLM registration here (but it can be re-added - see the
    # notes above.)
    try:
        _winreg.DeleteKey(_winreg.HKEY_LOCAL_MACHINE,
                          "Software\\Microsoft\\Office\\Outlook\\Addins\\" \
                          + klass._reg_progid_)
    except WindowsError:
        pass
    _DoRegister(klass, _winreg.HKEY_CURRENT_USER)
    print "Registration complete."

def DllUnregisterServer():
    klass = OutlookAddin
    # Try to remove the HKLM version.
    try:
        _winreg.DeleteKey(_winreg.HKEY_LOCAL_MACHINE,
                          "Software\\Microsoft\\Office\\Outlook\\Addins\\" \
                          + klass._reg_progid_)
    except WindowsError:
        pass
    # and again for current user.
    try:
        _winreg.DeleteKey(_winreg.HKEY_CURRENT_USER,
                          "Software\\Microsoft\\Office\\Outlook\\Addins\\" \
                          + klass._reg_progid_)
    except WindowsError:
        pass

if __name__ == '__main__':
    if '--register' in sys.argv[1:] or \
       '--unregister' in sys.argv[1:] or \
       not hasattr(sys, "frozen"):
        import win32com.server.register
        win32com.server.register.UseCommandLine(OutlookAddin)    
        if "--unregister" in sys.argv[1:]:
            DllUnregisterServer()
        else:
            DllRegisterServer()

        # Support 'hkey_local_machine' on the commandline, to work in
        # the same way as 'regsvr32 /i:hkey_local_machine' does.
        # regsvr32 calls it after DllRegisterServer, (and our registration
        # logic relies on that) so we will too.
        for a in sys.argv[1:]:
            if a.lower()=='hkey_local_machine':
                DllInstall(True, 'hkey_local_machine')
    elif hasattr(sys, "frozen"):
        if sys.frozen == "exe":
            # start the exe server.
            from win32com.server import localserver
            localserver.main()


##        #Some MAPI code, just in case we need it 
##        try:
##            iMsg = self.MAPIOBJECT.QueryInterface(mapi.IID_IMessage)
##            for num in range (0, self.Attachments.Count):                        
##                print "Deleting Attachment - ", num
##                iMsg.DeleteAttach(num, 0, None, 0)
##                deleted = True
##            if deleted:
##                iMsg.SaveChanges(0)
##            iMsg = None
##        except Exception, e:
##            print "MailItem OnRead Exception: ", str(e)

##for i in range(attachments.Count - num_infected+1, attachments.Count+1):
##    try:            
##        iMsg = item.MAPIOBJECT.QueryInterface(mapi.IID_IMessage)                                
##        print 'getting att', i               
##        att = attachments.Item(i)
##        print 'got att'
##        iAtt = att.MAPIOBJECT.QueryInterface(mapi.IID_IMAPIProp)                                
##        print 'got iAtt'
##        iAtt.SetProps([(mapitags.PR_ATTACH_FILENAME, att.DisplayName),])
##        print 'set PR_ATTACH_FILENAME'
##        iAtt.SetProps([(mapitags.PR_ATTACH_LONG_FILENAME, att.DisplayName),])
##        print 'set PR_ATTACH_LONG_FILENAME'
##        iAtt.SaveChanges(mapi.KEEP_OPEN_READWRITE)
##        print 'Saved Changes'
##        iAtt = None; att = None
##    except Exception, e:
##        print "Could not set attachment display name: ", str(e)
##
