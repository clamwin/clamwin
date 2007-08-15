
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

import sys, os, time
import wx
import Utils
import DialogUtils
import version
import I18N
#_ = I18N.getClamString


##
##def create(parent, config):
##    return MainFrame(parent, config)

ID_SCAN = wx.NewId()
ID_SCANMEM = wx.NewId()
ID_REPORTSDATABASE = wx.NewId()
ID_REPORTSSCAN = wx.NewId()
ID_DBUPDATE = wx.NewId()
ID_PREFERENCES = wx.NewId()
ID_REPORTS = wx.NewId()
ID_EXIT = wx.NewId()

ID_ABOUT = wx.NewId()
ID_FAQ = wx.NewId()
ID_UPDATE = wx.NewId()
ID_WEBSITE = wx.NewId()
ID_HELP = wx.NewId()
ID_SUPPORT = wx.NewId()




class MainFrame(wx.Frame):


    def _init_toolbar(self):
        # create toolbar

        self.toolBar = wx.ToolBar(self,style=wx.TB_FLAT | wx.TB_HORIZONTAL | wx.NO_BORDER)
        self.toolBar.SetToolBitmapSize(wx.Size(32, 32))
        self.SetToolBar(self.toolBar)
        
        self.toolBar.AddLabelTool(ID_PREFERENCES,
                                  _('Preferences'),
                                  wx.Bitmap('img/Control.png', wx.BITMAP_TYPE_PNG),
                                  wx.NullBitmap,
                                  wx.ITEM_NORMAL,
                                  _('Displays Preferences Window'),
                                  _('Displays Preferences Window'))
        
        self.toolBar.AddLabelTool(ID_DBUPDATE,
                                  _('Update'),
                                  wx.Bitmap('img/World.png', wx.BITMAP_TYPE_PNG),
                                  wx.NullBitmap,
                                  wx.ITEM_NORMAL,
                                  _('Starts Internet Update'),
                                  _('Updates virus databases over the Internet'))
        
        self.toolBar.AddSeparator()
        
        self.toolBar.AddLabelTool(ID_SCANMEM,
                                  _('Scan Computer Memory'),
                                  wx.Bitmap('img/ScanMem.png', wx.BITMAP_TYPE_PNG),
                                  wx.NullBitmap,
                                  wx.ITEM_NORMAL,
                                  _('Scans Computer Memory for Viruses'),
                                  _('Scans Programs Loaded in Computer Memory for Computer Viruses'))
        
        self.toolBar.AddLabelTool(ID_SCAN,
                                  _('Scan'),
                                  wx.Bitmap('img/Scan.png', wx.BITMAP_TYPE_PNG),
                                  wx.NullBitmap,
                                  wx.ITEM_NORMAL,
                                  _('Scans For Viruses'),
                                  _('Scans Selected File or Folder for Computer Viruses'))
        
        self.Bind(wx.EVT_TOOL, self.OnToolsUpdate, id=ID_DBUPDATE)
        self.Bind(wx.EVT_TOOL, self.OnToolsPreferences, id=ID_PREFERENCES)
        self.Bind(wx.EVT_TOOL, self.OnScanButton, id=ID_SCAN)
        self.Bind(wx.EVT_TOOL, self.OnScanMemButton, id=ID_SCANMEM)

        self.toolBar.Realize()

    def _init_sizers(self):
        # generated method, don't edit
##        self.gridSizerFrame = wx.GridSizer(cols=1, hgap=0, rows=1, vgap=0)

        self.flexGridSizerPanel = wx.FlexGridSizer(cols=1, hgap=0, rows=4,vgap=0)

        self.gridSizerButtons = wx.GridSizer(cols=2, hgap=0, rows=1, vgap=0)

        self.flexGridSizerPanel.AddSpacer(8, 8, border=0, flag=0)
        self.flexGridSizerPanel.AddWindow(self.static1, 0, border=5,
              flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_LEFT)
        self.flexGridSizerPanel.AddWindow(self.dirCtrlScan, 0, border=10,
              flag=wx.LEFT | wx.RIGHT | wx.GROW)

        self.flexGridSizerPanel.AddGrowableRow(2)
        self.flexGridSizerPanel.AddGrowableCol(0)

        self.gridSizerButtons.AddWindow(self.buttonScan, 0, border=10,
              flag=wx.ALIGN_RIGHT | wx.ALL)
        self.gridSizerButtons.AddWindow(self.buttonClose, 0, border=10,
              flag=wx.ALIGN_LEFT | wx.ALL)

    
        self.flexGridSizerPanel.AddSizer(self.gridSizerButtons, flag = wx.GROW)
        self.panelFrame.SetSizer(self.flexGridSizerPanel)


    def _init_menubar(self):
        #Create Menubar
        self.menuBar = wx.MenuBar()

        self.File = wx.Menu()
        self.File.Append(ID_SCAN,_('&Scan'),_('Scans Files or Folders for Computer Viruses'))
        self.File.Append(ID_SCANMEM,_('Scan &Memory'),_('Scans Programs in Computer Memory for Viruses'))
        self.File.AppendSeparator()
        self.File.Append(ID_EXIT,_('E&xit'),_('Exits the application'))
        
        self.Bind(wx.EVT_MENU, self.OnScanButton, id=ID_SCAN)
        self.Bind(wx.EVT_MENU, self.OnScanMemButton, id=ID_SCANMEM)
        self.Bind(wx.EVT_MENU, self.OnFileExit, id=ID_EXIT)

        self.Reports = wx.Menu(title='')
        self.Reports.Append(ID_REPORTSDATABASE,_('&Virus Database Update Report'),_('Displays Virus Database Update Log FIle'))
        self.Reports.Append(ID_REPORTSSCAN,_('&Scan Report'),_('Displays Virus Scan Log File'))
        
        self.Bind(wx.EVT_MENU, self.OnViewUpdateLog, id=ID_REPORTSDATABASE)
        self.Bind(wx.EVT_MENU, self.OnViewScanLog, id=ID_REPORTSSCAN)

        self.Tools = wx.Menu()
        self.Tools.Append(ID_PREFERENCES,_('&Preferences'), _('Displays the configuration window'))
        self.Tools.Append(ID_DBUPDATE, _('Download &Virus Database Update'),_('Downloads latest virus database from the Internet'))
        self.Tools.AppendMenu(ID_REPORTS,_('&Display Reports'),self.Reports,_('Displays ClamWin Log Files'))
        
        self.Bind(wx.EVT_MENU, self.OnToolsPreferences, id=ID_PREFERENCES)
        self.Bind(wx.EVT_MENU, self.OnToolsUpdate, id=ID_DBUPDATE)

        self.Help = wx.Menu()
        self.Help.Append(ID_HELP,_('&Help'),_('Displays ClamWin Free Antivirus Manual'))
        self.Help.Append(ID_SUPPORT,_('&Technical Support'),_('Opens Support Forum in the Web Browser'))
        self.Help.Append(ID_UPDATE,_('&Check Latest Version'),_('Checks for the Latest Version'))
        self.Help.Append(ID_WEBSITE,_('ClamWin &Website'),_('Opens ClamWin Free Antivirus Website'))
        self.Help.Append(ID_FAQ,_('&FAQ'),_('Opens Frequently Asked Questions Page in the Web Browser'))
        self.Help.AppendSeparator()
        self.Help.Append(ID_ABOUT,_('&About'),_('Displays the  About Box'))
        
        self.Bind(wx.EVT_MENU, self.OnHelpAbout, id=ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnHelpHelp, id=ID_HELP)
        self.Bind(wx.EVT_MENU, self.OnHelpSupport, id=ID_SUPPORT)
        self.Bind(wx.EVT_MENU, self.OnHelpUpdate, id=ID_UPDATE)
        self.Bind(wx.EVT_MENU, self.OnHelpWebsite, id=ID_WEBSITE)
        self.Bind(wx.EVT_MENU, self.OnHelpFAQ, id=ID_FAQ)


        self.menuBar.Append(self.File, _('&File'))
        self.menuBar.Append(self.Tools, _('&Tools'))
        self.menuBar.Append(self.Help, _('&Help'))

        self.SetMenuBar(self.menuBar)

    def _init_ctrls(self, prnt):

        wx.Frame.__init__(self, prnt, wx.ID_ANY, _('ClamWin Free Antivirus'), style=wx.DEFAULT_FRAME_STYLE)
        
        self._init_menubar()
        
        self.SetClientSize(wx.Size(560, 403))
        self.SetHelpText(_('ClamWin Free Antivirus'))
        self.Center(wx.BOTH)

        self._init_toolbar()
        
        self.statusBar = wx.StatusBar(self)
        self.statusBar.SetToolTipString(_('Status Bar'))
        self.SetStatusBar(self.statusBar)

        self.panelFrame = wx.Panel(self,style=wx.TAB_TRAVERSAL)

        self.static1 = wx.StaticText(self.panelFrame,wx.ID_ANY,_('Select a folder or a file to scan\n(Hold Shift key to select multiple files or folders)'))
   
        self.dirCtrlScan = GenericDirCtrlEx(self.panelFrame,wx.ID_ANY,defaultFilter=0, dir='.', filter='',
                                            style=wx.DIRCTRL_SELECT_FIRST | wx.SUNKEN_BORDER | wx.DIRCTRL_3D_INTERNAL)

        self.buttonScan = wx.Button(self.panelFrame,wx.ID_ANY,_('&Scan'))
        self.buttonScan.SetDefault()
        self.Bind(wx.EVT_BUTTON, self.OnScanButton, self.buttonScan)

        self.buttonClose = wx.Button(self.panelFrame,wx.ID_ANY,_('&Close'))
        self.Bind(wx.EVT_BUTTON, self.OnButtonClose, self.buttonClose)

        

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
        #self.dirCtrlScan.SetSize((-1, 0))
        #self.panelFrame.SetSize((-1, 0))
        self._init_sizers()
        

        # set window icons
        icons = wx.IconBundle()
        icons.AddIconFromFile('img/FrameIcon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcons(icons)

        if not sys.platform.startswith('win'):
            self.Help.Remove(ID_HELPHELP)

        self._UpdateState()


    def OnFileExit(self, event):
        self.Close()

    def OnToolsPreferences(self, event):
        DialogUtils.Configure(self, self._config)
        self._UpdateState()

    def OnHelpAbout(self, event):
        DialogUtils.About(self, self._config)

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
                if wx.ID_YES == wx.MessageBox(_('ClamWin Free Antivirus is not configured. Would you like to configure it now?'),_('ClamWin Free Antivirus'), wx.YES_NO | wx.ICON_QUESTION):
                    DialogUtils.Configure(None, self._config)
                    configured = self._IsConfigured()

            hasdb = Utils.CheckDatabase(self._config)
            if configured and not hasdb:
                if wx.ID_YES == wx.MessageBox( _('You have not yet downloaded Virus Definitions Database. Would you like to download it now?'),_('ClamWin Free Antivirus'), wx.YES_NO | wx.ICON_QUESTION):
                    DialogUtils.UpdateVirDB(self, self._config)
                    hasdb = Utils.CheckDatabase(self._config)                    
            
            self.buttonScan.Enable(configured and hasdb)
            self.toolBar.EnableTool(ID_DBUPDATE, configured)
            self.toolBar.EnableTool(ID_SCAN, configured and hasdb)
            self.toolBar.EnableTool(ID_SCANMEM, configured and hasdb)
            
            # check if the db is current (not older than 3 days)                    
            if hasdb:
                dbpath =  self._config.Get('ClamAV', 'Database')                
                daily = os.path.join(dbpath, 'daily.cvd')
                if not os.path.isfile(daily):
                    daily = os.path.join(os.path.join(dbpath, 'daily.inc'), 'daily.info')                   
                ver, numv, updated = Utils.GetDBInfo(daily)
    
                
            #print updated, time.mktime(time.localtime()), time.mktime(time.localtime()) - updated
            if hasdb and self._config.Get('Updates', 'WarnOutOfDate') == '1' and (time.time() - updated > 86400*3):
                if wx.ID_YES == wx.MessageBox(_('Virus signature database is older than 3 days and may not offer the latest protection. Would you like to update it now?'),_('ClamWin Free Antivirus'),  wx.YES_NO | wx.ICON_QUESTION):
                    DialogUtils.UpdateVirDB(self, self._config)
                    hasdb = Utils.CheckDatabase(self._config)                    
                       
        except Exception, e:
            print _('An Error occurred while updating UI selection. %s') % str(e)

    def OnScanButton(self, event):
        scanPath = ''
        for path in self.dirCtrlScan.GetMultiplePath():
            scanPath += "\"%s\" " % path
        DialogUtils.Scan(self, self._config, scanPath)

    def OnScanMemButton(self, event):
        DialogUtils.Scan(self, self._config, None)

    def OnToolsUpdate(self, event):
        DialogUtils.UpdateVirDB(self, self._config)
        self._UpdateState()

    def OnButtonClose(self, event):
        self.Close()

    def OnViewUpdateLog(self, event):
        DialogUtils.ShowLog(self, self._config.Get('Updates', 'DBUpdateLogFile'))

    def OnViewScanLog(self, event):
        DialogUtils.ShowLog(self, self._config.Get('ClamAV', 'LogFile'))

    def OnHelpHelp(self, event):
        if sys.platform.startswith('win'):
            #import win32api, win32con
            helpfile = I18N.getHelpFilePath()
            helppath = helpfile[:helpfile.rfind("\\")]
            if not os.path.isfile(helpfile):
                wx.MessageBox(_('Could not open help file - %s not found.') % helpfile,_('Error'),wx.OK | wx.ICON_ERROR)
            else:
                os.startfile(helpfile)
##                try:
##                    win32api.ShellExecute(self.GetHandle(), 'open',
##                        helpfile,
##                        None, helppath, win32con.SW_SHOWNORMAL)
##                except Exception, e:
##                    wx.MessageBox(_('Could not open help file. Please ensure that you have Adobe Acrobat Reader installed.'),_('Error'),wx.OK | wx.ICON_ERROR)

    def OnHelpFAQ(self, event):
        DialogUtils.GoToInternetUrl(_('http://www.clamwin.com/content/category/3/7/27/'))
        
    def OnHelpSupport(self, event):
        DialogUtils.GoToInternetUrl('http://forums.clamwin.com/')


    def OnHelpUpdate(self, event):
        DialogUtils.GoToInternetUrl(_('http://www.clamwin.com/index.php?option=content&task=view&id=40&Itemid=60&version=')+version.clamwin_version)


    def OnHelpWebsite(self, event):
        DialogUtils.GoToInternetUrl(_('http://www.clamwin.com'))

class GenericDirCtrlEx(wx.GenericDirCtrl):
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

        wx.GenericDirCtrl.__init__(self, *_args, **_kwargs)
        self.ShowHidden(showhidden)
        if multiselect:
            tree = self.GetTreeCtrl()
            tree.SetWindowStyleFlag(tree.GetWindowStyleFlag() | wx.TR_MULTIPLE)

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



