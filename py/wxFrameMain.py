#-----------------------------------------------------------------------------
#Boa:Frame:wxMainFrame

#-----------------------------------------------------------------------------
# Name:        wxFrameMain.py
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

import sys, os
from wxPython.wx import *
import MsgBox, Utils, wxDialogUtils, version
from I18N import getClamString as _
def create(parent, config):
    return wxMainFrame(parent, config)

[wxID_WXMAINFRAME, wxID_WXMAINFRAMEBUTTONCLOSE, wxID_WXMAINFRAMEBUTTONSCAN, 
 wxID_WXMAINFRAMEDIRCTRLSCAN, wxID_WXMAINFRAMEPANELFRAME, 
 wxID_WXMAINFRAMESTATIC1, wxID_WXMAINFRAMESTATUSBAR, wxID_WXMAINFRAMETOOLBAR, 
] = map(lambda _init_ctrls: wxNewId(), range(8))


[wxID_WXMAINFRAMETOOLBARTOOLS_INETUPDATE, wxID_WXMAINFRAMETOOLBARTOOLS_PREFS, 
 wxID_WXMAINFRAMETOOLBARTOOLS_SCAN, 
] = map(lambda _init_coll_toolBar_Tools: wxNewId(), range(3))

[wxID_WXMAINFRAMEREPORTSDATABASE, wxID_WXMAINFRAMEREPORTSSCAN, 
] = map(lambda _init_coll_Reports_Items: wxNewId(), range(2))

[wxID_WXMAINFRAMETOOLSDBUPDATE, wxID_WXMAINFRAMETOOLSPREFERENCES, 
 wxID_WXMAINFRAMETOOLSREPORTS, 
] = map(lambda _init_coll_Tools_Items: wxNewId(), range(3))

[wxID_WXMAINFRAMEHELPABOUT, wxID_WXMAINFRAMEHELPFAQ, wxID_WXMAINFRAMEHELPUPDATE, wxID_WXMAINFRAMEHELPWEBSITE, wxID_WXMAINFRAMEHELPHELP, 
] = map(lambda _init_coll_Help_Items: wxNewId(), range(5))

[wxID_WXMAINFRAMEFILEITEMS0, wxID_WXMAINFRAMEFILESCAN, 
] = map(lambda _init_coll_File_Items: wxNewId(), range(2))

class wxMainFrame(wxFrame):    
    def _init_coll_flexGridSizerPanel_Items(self, parent):
        # generated method, don't edit

        parent.AddSpacer(8, 8, border=0, flag=0)
        parent.AddWindow(self.static1, 0, border=5,
              flag=wxLEFT | wxRIGHT | wxBOTTOM | wxALIGN_LEFT)
        parent.AddWindow(self.dirCtrlScan, 0, border=10,
              flag=wxLEFT | wxRIGHT | wxGROW)

    def _init_coll_flexGridSizerPanel_Growables(self, parent):
        # generated method, don't edit

        parent.AddGrowableRow(2)
        parent.AddGrowableCol(0)

    def _init_coll_gridSizerFrame_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.panelFrame, 0, border=0, flag=wxGROW)

    def _init_coll_gridSizerButtons_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.buttonScan, 0, border=10,
              flag=wxALIGN_RIGHT | wxALL)
        parent.AddWindow(self.buttonClose, 0, border=10,
              flag=wxALIGN_LEFT | wxALL)

    def _init_coll_Tools_Items(self, parent):
        # generated method, don't edit

        parent.Append(helpString=_('Displays the configuration window'),
              id=wxID_WXMAINFRAMETOOLSPREFERENCES, item=_('&Preferences'),
              kind=wxITEM_NORMAL)
        parent.Append(helpString=_('Downloads latest virus database from the Internet'),
              id=wxID_WXMAINFRAMETOOLSDBUPDATE,
              item=_('Download &Virus Database Update'), kind=wxITEM_NORMAL)
        parent.AppendMenu(helpString=_('Displays ClamWin Log Files'),
              id=wxID_WXMAINFRAMETOOLSREPORTS, item=_('&Display Reports'),
              subMenu=self.Reports)
        EVT_MENU(self, wxID_WXMAINFRAMETOOLSPREFERENCES,
              self.OnToolsPreferences)
        EVT_MENU(self, wxID_WXMAINFRAMETOOLSDBUPDATE, self.OnToolsUpdate)

    def _init_coll_menuBar_Menus(self, parent):
        # generated method, don't edit

        parent.Append(menu=self.File, title=_('&File'))
        parent.Append(menu=self.Tools, title=_('&Tools'))
        parent.Append(menu=self.Help, title=_('&Help'))

    def _init_coll_Help_Items(self, parent):
        # generated method, don't edit

        parent.Append(helpString=_('Displays ClamWin Free Antivirus Manual'),
              id=wxID_WXMAINFRAMEHELPHELP, item=_('&Help'), kind=wxITEM_NORMAL)
        parent.Append(helpString=_('Checks for the Latest Version'),
              id=wxID_WXMAINFRAMEHELPUPDATE, item=_('&Check Latest Version'), kind=wxITEM_NORMAL)
        parent.Append(helpString=_('Opens ClamWin Free Antivirus Website'),
              id=wxID_WXMAINFRAMEHELPWEBSITE, item=_('ClamWin &Website'), kind=wxITEM_NORMAL)

        parent.Append(helpString=_('Opens Frequently Asked Questions Page in the Web Browser'),
              id=wxID_WXMAINFRAMEHELPFAQ, item=_('&FAQ'), kind=wxITEM_NORMAL)
        parent.AppendSeparator()
        parent.Append(helpString=_('Displays the  About Box'),
              id=wxID_WXMAINFRAMEHELPABOUT, item=_('&About'), kind=wxITEM_NORMAL)
        EVT_MENU(self, wxID_WXMAINFRAMEHELPABOUT, self.OnHelpAbout)
        EVT_MENU(self, wxID_WXMAINFRAMEHELPHELP, self.OnHelpHelp)
        EVT_MENU(self, wxID_WXMAINFRAMEHELPUPDATE, self.OnHelpUpdate)
        EVT_MENU(self, wxID_WXMAINFRAMEHELPWEBSITE, self.OnHelpWebsite)
        EVT_MENU(self, wxID_WXMAINFRAMEHELPFAQ, self.OnHelpFAQ)

    def _init_coll_Reports_Items(self, parent):
        # generated method, don't edit

        parent.Append(helpString=_('Displays Virus Database Update Log FIle'),
              id=wxID_WXMAINFRAMEREPORTSDATABASE,
              item=_('&Virus Database Update Report'), kind=wxITEM_NORMAL)
        parent.Append(helpString=_('Displays Virus Scan Log File'),
              id=wxID_WXMAINFRAMEREPORTSSCAN, item=_('&Scan Report'),
              kind=wxITEM_NORMAL)
        EVT_MENU(self, wxID_WXMAINFRAMEREPORTSDATABASE, self.OnViewUpdateLog)
        EVT_MENU(self, wxID_WXMAINFRAMEREPORTSSCAN, self.OnViewScanLog)

    def _init_coll_File_Items(self, parent):
        # generated method, don't edit
        
        parent.Append(helpString=_('Scans Files or Folders for Computer Viruses'),
              id=wxID_WXMAINFRAMEFILESCAN, item=_('&Scan'), kind=wxITEM_NORMAL)
        parent.AppendSeparator()
        parent.Append(helpString=_('Exits the application'),
              id=wxID_WXMAINFRAMEFILEITEMS0, item=_('E&xit'), kind=wxITEM_NORMAL)
        EVT_MENU(self, wxID_WXMAINFRAMEFILESCAN, self.OnScanButton)
        EVT_MENU(self, wxID_WXMAINFRAMEFILEITEMS0, self.OnFileExit)        

    def _init_coll_toolBar_Tools(self, parent):
        # generated method, don't edit

        parent.DoAddTool(bitmap=wxBitmap('img/Control.png', wxBITMAP_TYPE_PNG),
              bmpDisabled=wxNullBitmap, id=wxID_WXMAINFRAMETOOLBARTOOLS_PREFS,
              kind=wxITEM_NORMAL, label=_('Preferences'),
              longHelp=_('Displays Preferences Window'),
              shortHelp=_('Displays Preferences Window'))
        parent.DoAddTool(bitmap=wxBitmap('img/World.png', wxBITMAP_TYPE_PNG),
              bmpDisabled=wxNullBitmap,
              id=wxID_WXMAINFRAMETOOLBARTOOLS_INETUPDATE, kind=wxITEM_NORMAL,
              label=_('Update'),
              longHelp=_('Updates virus databases over the Internet'),
              shortHelp=_('Starts Internet Update'))
        parent.AddSeparator()
        parent.DoAddTool(bitmap=wxBitmap('img/Scan.png', wxBITMAP_TYPE_PNG),
              bmpDisabled=wxNullBitmap, id=wxID_WXMAINFRAMETOOLBARTOOLS_SCAN,
              kind=wxITEM_NORMAL, label=_('Scan'),
              longHelp=_('Scans Selected File or Folder for Computer Viruses'),
              shortHelp=_('Scans For Viruses'))
        EVT_TOOL(self, wxID_WXMAINFRAMETOOLBARTOOLS_INETUPDATE,
              self.OnToolsUpdate)
        EVT_TOOL(self, wxID_WXMAINFRAMETOOLBARTOOLS_PREFS,
              self.OnToolsPreferences)
        EVT_TOOL(self, wxID_WXMAINFRAMETOOLBARTOOLS_SCAN, self.OnScanButton)

        parent.Realize()

    def _init_sizers(self):
        # generated method, don't edit
        self.gridSizerFrame = wxGridSizer(cols=1, hgap=0, rows=1, vgap=0)

        self.flexGridSizerPanel = wxFlexGridSizer(cols=1, hgap=0, rows=4,
              vgap=0)

        self.gridSizerButtons = wxGridSizer(cols=2, hgap=0, rows=1, vgap=0)

        self._init_coll_gridSizerFrame_Items(self.gridSizerFrame)
        self._init_coll_flexGridSizerPanel_Items(self.flexGridSizerPanel)
        self._init_coll_flexGridSizerPanel_Growables(self.flexGridSizerPanel)
        self._init_coll_gridSizerButtons_Items(self.gridSizerButtons)

        self.SetSizer(self.gridSizerFrame)
        self.panelFrame.SetSizer(self.flexGridSizerPanel)

    def _init_utils(self):
        # generated method, don't edit
        self.menuBar = wxMenuBar()

        self.File = wxMenu(title='')

        self.Tools = wxMenu(title='')

        self.Help = wxMenu(title='')

        self.Reports = wxMenu(title='')

        self._init_coll_menuBar_Menus(self.menuBar)
        self._init_coll_File_Items(self.File)
        self._init_coll_Tools_Items(self.Tools)
        self._init_coll_Help_Items(self.Help)
        self._init_coll_Reports_Items(self.Reports)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wxFrame.__init__(self, id=wxID_WXMAINFRAME, name='wxMainFrame',
              parent=prnt, pos=wxPoint(250, 143), size=wxSize(568, 430),
              style=wxDEFAULT_FRAME_STYLE, title=_('ClamWin Free Antivirus'))
        self._init_utils()
        self.SetClientSize(wxSize(560, 403))
        self.SetMenuBar(self.menuBar)
        self.SetHelpText(_('ClamWin Free Antivirus'))
        self.Center(wxBOTH)

        self.toolBar = wxToolBar(id=wxID_WXMAINFRAMETOOLBAR, name='toolBar',
              parent=self, pos=wxPoint(0, 0), size=wxSize(560, 41),
              style=wxTB_FLAT | wxTB_HORIZONTAL | wxNO_BORDER)
        self.toolBar.SetToolTipString('')
        self.toolBar.SetToolBitmapSize(wxSize(32, 32))
        self.SetToolBar(self.toolBar)

        self.statusBar = wxStatusBar(id=wxID_WXMAINFRAMESTATUSBAR,
              name='statusBar', parent=self, style=0)
        self.statusBar.SetSize(wxSize(537, 20))
        self.statusBar.SetPosition(wxPoint(0, 218))
        self.statusBar.SetToolTipString(_('Status Bar'))
        self.SetStatusBar(self.statusBar)

        self.panelFrame = wxPanel(id=wxID_WXMAINFRAMEPANELFRAME,
              name='panelFrame', parent=self, pos=wxPoint(0, 0),
              size=wxSize(560, 403), style=wxTAB_TRAVERSAL)

        self.static1 = wxStaticText(id=wxID_WXMAINFRAMESTATIC1,
              label=_('Select a folder or a file to scan\n(Hold Shift key to select multiple files or folders)'), name='static1',
              parent=self.panelFrame, pos=wxPoint(5, 8), size=wxSize(435, 32),
              style=0)
        
        self.dirCtrlScan = wxGenericDirCtrlEx(defaultFilter=0, dir='.', filter='',
              id=wxID_WXMAINFRAMEDIRCTRLSCAN, name='dirCtrlScan',
             parent=self.panelFrame, pos=wxPoint(10, 27), size=wxSize(540,
             376),
             style=wxDIRCTRL_SELECT_FIRST | wxSUNKEN_BORDER | wxDIRCTRL_3D_INTERNAL)

        self.buttonScan = wxButton(id=wxID_WXMAINFRAMEBUTTONSCAN, label=_('&Scan'),
              name='buttonScan', parent=self.panelFrame, pos=wxPoint(-85, 10),
              size=wxSize(75, 23), style=0)
        self.buttonScan.SetDefault()
        EVT_BUTTON(self.buttonScan, wxID_WXMAINFRAMEBUTTONSCAN,
              self.OnScanButton)

        self.buttonClose = wxButton(id=wxID_WXMAINFRAMEBUTTONCLOSE,
              label=_('&Close'), name='buttonClose', parent=self.panelFrame,
              pos=wxPoint(10, 10), size=wxSize(75, 23), style=0)
        EVT_BUTTON(self.buttonClose, wxID_WXMAINFRAMEBUTTONCLOSE,
              self.OnButtonClose)

        self._init_coll_toolBar_Tools(self.toolBar)

        ##self._init_sizers()

    def __init__(self, parent, config):
        self._config = None
        self._config = config

        self._init_ctrls(parent)                     
        
        # select second in the directory tree (usually c:)
        try:
            # navigate to the second item
            treeCtrl = self.dirCtrlScan.GetTreeCtrl()            
            cookie = 0
            itemid, cookie = treeCtrl.GetFirstChild(treeCtrl.GetRootItem(), cookie)            
            itemid, cookie = treeCtrl.GetNextChild(treeCtrl.GetRootItem(), cookie)
            # select it
            treeCtrl.SetFocus()                         
            treeCtrl.UnselectAll()                        
            treeCtrl.SelectItem(itemid)                                    
        except:                        
            pass
        
        # we need to set controls heights to 0 and reinit sizers
        # to overcome boa sizers bug
        self.dirCtrlScan.SetSize((-1, 0))
        self.panelFrame.SetSize((-1, 0))        
        self._init_sizers()
        self.flexGridSizerPanel.AddSizer(self.gridSizerButtons, flag = wxGROW)

        # set window icons
        icons = wxIconBundle()
        icons.AddIconFromFile('img/FrameIcon.ico', wxBITMAP_TYPE_ICO)
        self.SetIcons(icons)
        
        if not sys.platform.startswith('win'):
            self.Help.Remove(wxID_WXMAINFRAMEHELPHELP)

        self._UpdateState()
                

    def OnFileExit(self, event):
        self.Close()

    def OnToolsPreferences(self, event):
        wxDialogUtils.wxConfigure(self, self._config)        
        self._UpdateState()

    def OnHelpAbout(self, event):
        wxDialogUtils.wxAbout(self, self._config)    

    def _IsConfigured(self):        
        if self._config.Get('ClamAV', 'ClamScan') == '' or \
            self._config.Get('ClamAV', 'FreshClam') == '' or \
            self._config.Get('ClamAV', 'Database') == '' :
            return False
        else:
            return True


    def _UpdateState(self):
        try:
            # disable Run Command button if the configuration is invalid
            # or no item is selected in the tree
            configured = self._IsConfigured()       
            if not configured:
                if wxID_YES == MsgBox.MessageBox(None, _('ClamWin Free Antivirus'), _('ClamWin Free Antivirus is not configured. Would you like to configure it now?'), wxYES_NO | wxICON_QUESTION):
                    wxDialogUtils.wxConfigure(None, self._config)
                    configured = self._IsConfigured()

            hasdb = Utils.CheckDatabase(self._config)      
            if configured and not hasdb:
                if wxID_YES == MsgBox.MessageBox(None, _('ClamWin Free Antivirus'), _('You have not yet downloaded Virus Definitions Database. Would you like to download it now?'), wxYES_NO | wxICON_QUESTION):
                    wxDialogUtils.wxUpdateVirDB(self, self._config)
                    hasdb = Utils.CheckDatabase(self._config)

            self.buttonScan.Enable(configured and hasdb)
            self.toolBar.EnableTool(wxID_WXMAINFRAMETOOLBARTOOLS_INETUPDATE, configured)    
            self.toolBar.EnableTool(wxID_WXMAINFRAMETOOLBARTOOLS_SCAN, configured and hasdb)    
            
            
            
        except Exception, e:
            print _('An Error occurred while updating UI selection. %s') % str(e)

    def OnScanButton(self, event):
        scanPath = ''
        for path in self.dirCtrlScan.GetMultiplePath():
            #if sys.platform.startswith("win"):                           
            #    path = path.replace('\\', '/')                                    
            scanPath += "\"%s\" " % path                             
        wxDialogUtils.wxScan(self, self._config, scanPath)        

    def OnToolsUpdate(self, event):
        wxDialogUtils.wxUpdateVirDB(self, self._config)
        self._UpdateState()

    def OnButtonClose(self, event):
        self.Close()        

    def OnViewUpdateLog(self, event):                
        wxDialogUtils.wxShowLog(self, self._config.Get('Updates', 'DBUpdateLogFile'))

    def OnViewScanLog(self, event):
        wxDialogUtils.wxShowLog(self, self._config.Get('ClamAV', 'LogFile'))
                                
    def OnHelpHelp(self, event):        
        if sys.platform.startswith('win'):            
            import win32api, win32con
            curDir = Utils.GetCurrentDir(True)
            helpfile = os.path.join(curDir, 'manual.chm')
            if not os.path.isfile(helpfile):
                MsgBox.ErrorBox(self, _('Could not open help file - %s not found.') % helpfile)
            else:    
                try:                
                    win32api.ShellExecute(self.GetHandle(), 'open', 
                        helpfile,
                        None, curDir, win32con.SW_SHOWNORMAL)
                except Exception, e:
                    MsgBox.ErrorBox(self, _('Could not open help file. Please ensure that you have Adobe Acrobat Reader installed.'))

    def OnHelpFAQ(self, event):
        wxDialogUtils.wxGoToInternetUrl('http://sourceforge.net/docman/display_doc.php?docid=22588&group_id=105508')
        
        
    def OnHelpUpdate(self, event):
        wxDialogUtils.wxGoToInternetUrl('http://www.clamwin.com/index.php?option=content&task=view&id=40&Itemid=60&version='+version.clamwin_version)
        
                
    def OnHelpWebsite(self, event):
        wxDialogUtils.wxGoToInternetUrl(_('http://www.clamwin.com'))
                
class wxGenericDirCtrlEx(wxGenericDirCtrl):    
    def __init__(self,*_args,**_kwargs):
        try:
            if _kwargs['multiselect'] == True:
                multiselect = True
                del _kwargs['multiselect']
            else:
                multiselect = False        
        except KeyError:
            multiselect = True
            
        try:    
            if _kwargs['showhidden'] == True:
                showhidden = True
                del _kwargs['showhidden']
            else:
                showhidden = False
        except KeyError:
            showhidden = True
            
        wxGenericDirCtrl.__init__(self, *_args, **_kwargs)        
        self.ShowHidden(showhidden)
        if multiselect:  
            tree = self.GetTreeCtrl()                      
            tree.SetWindowStyleFlag(tree.GetWindowStyleFlag() | wxTR_MULTIPLE)
        
    def GetMultiplePath(self):
        multiPath = []
        tree = self.GetTreeCtrl()
        sels = tree.GetSelections()
        for sel in sels:
            item = sel
            path = ''
            itemtext = tree.GetItemText(item)
            while True:
                try:                                              
                    if not sys.platform.startswith("win"):                           
                        # unix - terminate when path=='/'
                        if itemtext == '/':
                            path = itemtext + path                            
                            break
                        else:
                            path = itemtext + '/' + path                            
                    else:
                        # windows, root drive is enclosed in ()
                        if itemtext.startswith('(') and itemtext.endswith(':)'):
                            # remove '(' and ')'
                            itemtext = itemtext.strip('()')
                            path = itemtext + '\\' + path
                            break
                        else:                            
                            path = itemtext + '\\' + path                                                
                    item = tree.GetItemParent(item)
                    itemtext = tree.GetItemText(item)                                        
                except:
                    break               
            if len(path) > 1:
                path = path.rstrip('\\/')                             
            multiPath.append(path)
        return multiPath
        
    
        
