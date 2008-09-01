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
import MsgBox, Utils, wxDialogUtils, version
import wx

def create(parent, config):
    return wxMainFrame(parent, config)

[wxID_WXMAINFRAME, wxID_WXMAINFRAMEBUTTONCLOSE, wxID_WXMAINFRAMEBUTTONSCAN,
 wxID_WXMAINFRAMEDIRCTRLSCAN, wxID_WXMAINFRAMEPANELFRAME,
 wxID_WXMAINFRAMESTATIC1, wxID_WXMAINFRAMESTATUSBAR, wxID_WXMAINFRAMETOOLBAR, wxID_WXMAINFRAMETOOLBARTOOLS_SCANMEM
] = map(lambda _init_ctrls: wx.NewId(), range(9))


[wxID_WXMAINFRAMETOOLBARTOOLS_INETUPDATE, wxID_WXMAINFRAMETOOLBARTOOLS_PREFS,
 wxID_WXMAINFRAMETOOLBARTOOLS_SCAN,
] = map(lambda _init_coll_toolBar_Tools: wx.NewId(), range(3))

[wxID_WXMAINFRAMEREPORTSDATABASE, wxID_WXMAINFRAMEREPORTSSCAN,
] = map(lambda _init_coll_Reports_Items: wx.NewId(), range(2))

[wxID_WXMAINFRAMETOOLSDBUPDATE, wxID_WXMAINFRAMETOOLSPREFERENCES,
 wxID_WXMAINFRAMETOOLSREPORTS,
] = map(lambda _init_coll_Tools_Items: wx.NewId(), range(3))

[wxID_WXMAINFRAMEHELPABOUT, wxID_WXMAINFRAMEHELPFAQ, wxID_WXMAINFRAMEHELPUPDATE, wxID_WXMAINFRAMEHELPWEBSITE, wxID_WXMAINFRAMEHELPHELP, wxID_WXMAINFRAMEHELPSUPPORT,
] = map(lambda _init_coll_Help_Items: wx.NewId(), range(6))

[wxID_WXMAINFRAMEFILEITEMS0, wxID_WXMAINFRAMEFILESCAN, wxID_WXMAINFRAMEFILESCANMEM
] = map(lambda _init_coll_File_Items: wx.NewId(), range(3))

class wxMainFrame(wx.Frame):
    def _init_coll_flexGridSizerPanel_Items(self, parent):
        parent.AddSpacer(8, 8, border=0, flag=0)
        parent.AddWindow(self.static1, 0, border=5, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_LEFT)
        parent.AddWindow(self.dirCtrlScan, 0, border=10, flag=wx.LEFT | wx.RIGHT | wx.GROW)

    def _init_coll_flexGridSizerPanel_Growables(self, parent):
        parent.AddGrowableRow(2)
        parent.AddGrowableCol(0)

    def _init_coll_gridSizerFrame_Items(self, parent):
        parent.AddWindow(self.panelFrame, 0, border=0, flag=wx.GROW)

    def _init_coll_gridSizerButtons_Items(self, parent):
        parent.AddWindow(self.buttonScan, 0, border=10, flag=wx.ALIGN_RIGHT | wx.ALL)
        parent.AddWindow(self.buttonClose, 0, border=10, flag=wx.ALIGN_LEFT | wx.ALL)

    def _init_coll_Tools_Items(self, parent):
        parent.Append(wxID_WXMAINFRAMETOOLSPREFERENCES, help='Displays the configuration window',
              text='&Preferences',
              kind=wx.ITEM_NORMAL)
        parent.Append(wxID_WXMAINFRAMETOOLSDBUPDATE, help='Downloads latest virus database from the Internet',
              text='Download &Virus Database Update', kind=wx.ITEM_NORMAL)
        parent.AppendMenu(wxID_WXMAINFRAMETOOLSREPORTS, help='Displays ClamWin Log Files',
              text='&Display Reports',
              submenu=self.Reports)
        wx.EVT_MENU(self, wxID_WXMAINFRAMETOOLSPREFERENCES, self.OnToolsPreferences)
        wx.EVT_MENU(self, wxID_WXMAINFRAMETOOLSDBUPDATE, self.OnToolsUpdate)

    def _init_coll_menuBar_Menus(self, parent):
        parent.Append(menu=self.File, title='&File')
        parent.Append(menu=self.Tools, title='&Tools')
        parent.Append(menu=self.Help, title='&Help')

    def _init_coll_Help_Items(self, parent):
        parent.Append(wxID_WXMAINFRAMEHELPHELP, help='Displays ClamWin Free Antivirus Manual',
              text='&Help', kind=wx.ITEM_NORMAL)
        parent.Append(wxID_WXMAINFRAMEHELPSUPPORT, help='Opens Support Forum in the Web Browser',
              text='&Technical Support', kind=wx.ITEM_NORMAL)
        parent.Append(wxID_WXMAINFRAMEHELPUPDATE, help='Checks for the Latest Version',
              text='&Check Latest Version', kind=wx.ITEM_NORMAL)
        parent.Append(wxID_WXMAINFRAMEHELPWEBSITE, help='Opens ClamWin Free Antivirus Website',
              text='ClamWin &Website', kind=wx.ITEM_NORMAL)

        parent.Append(wxID_WXMAINFRAMEHELPFAQ, help='Opens Frequently Asked Questions Page in the Web Browser',
              text='&FAQ', kind=wx.ITEM_NORMAL)

        parent.AppendSeparator()
        parent.Append(wxID_WXMAINFRAMEHELPABOUT, help='Displays the About Box',
              text='&About', kind=wx.ITEM_NORMAL)
        wx.EVT_MENU(self, wxID_WXMAINFRAMEHELPABOUT, self.OnHelpAbout)
        wx.EVT_MENU(self, wxID_WXMAINFRAMEHELPHELP, self.OnHelpHelp)
        wx.EVT_MENU(self, wxID_WXMAINFRAMEHELPSUPPORT, self.OnHelpSupport)
        wx.EVT_MENU(self, wxID_WXMAINFRAMEHELPUPDATE, self.OnHelpUpdate)
        wx.EVT_MENU(self, wxID_WXMAINFRAMEHELPWEBSITE, self.OnHelpWebsite)
        wx.EVT_MENU(self, wxID_WXMAINFRAMEHELPFAQ, self.OnHelpFAQ)

    def _init_coll_Reports_Items(self, parent):
        parent.Append(wxID_WXMAINFRAMEREPORTSDATABASE, help='Displays Virus Database Update Log FIle',
              text='&Virus Database Update Report', kind=wx.ITEM_NORMAL)
        parent.Append(wxID_WXMAINFRAMEREPORTSSCAN, help='Displays Virus Scan Log File',
              text='&Scan Report',
              kind=wx.ITEM_NORMAL)
        wx.EVT_MENU(self, wxID_WXMAINFRAMEREPORTSDATABASE, self.OnViewUpdateLog)
        wx.EVT_MENU(self, wxID_WXMAINFRAMEREPORTSSCAN, self.OnViewScanLog)

    def _init_coll_File_Items(self, parent):
        parent.Append(wxID_WXMAINFRAMEFILESCAN, help='Scans Selected Files or Folders for Computer Viruses',
              text='&Scan Files', kind=wx.ITEM_NORMAL)
        parent.Append(wxID_WXMAINFRAMEFILESCANMEM, help='Scans Programs in Computer Memory for Viruses',
              text='Scan &Memory', kind=wx.ITEM_NORMAL)

        parent.AppendSeparator()
        parent.Append(wxID_WXMAINFRAMEFILEITEMS0, help='Exits the application',
              text='E&xit', kind=wx.ITEM_NORMAL)
        wx.EVT_MENU(self, wxID_WXMAINFRAMEFILESCAN, self.OnScanButton)
        wx.EVT_MENU(self, wxID_WXMAINFRAMEFILESCANMEM, self.OnScanMemButton)
        wx.EVT_MENU(self, wxID_WXMAINFRAMEFILEITEMS0, self.OnFileExit)

    def _init_coll_toolBar_Tools(self, parent):
        parent.DoAddTool(bitmap=wx.Bitmap('img/Control.png', wx.BITMAP_TYPE_PNG),
              bmpDisabled=wx.NullBitmap, id=wxID_WXMAINFRAMETOOLBARTOOLS_PREFS,
              kind=wx.ITEM_NORMAL, label='Preferences',
              longHelp='Displays Preferences Window',
              shortHelp='Displays Preferences Window')
        parent.DoAddTool(bitmap=wx.Bitmap('img/World.png', wx.BITMAP_TYPE_PNG),
              bmpDisabled=wx.NullBitmap,
              id=wxID_WXMAINFRAMETOOLBARTOOLS_INETUPDATE, kind=wx.ITEM_NORMAL,
              label='Update',
              longHelp='Updates virus databases over the Internet',
              shortHelp='Starts Internet Update')
        parent.AddSeparator()
        parent.DoAddTool(bitmap=wx.Bitmap('img/ScanMem.png', wx.BITMAP_TYPE_PNG),
              bmpDisabled=wx.NullBitmap, id=wxID_WXMAINFRAMETOOLBARTOOLS_SCANMEM,
              kind=wx.ITEM_NORMAL, label='Scan Computer Memory',
              longHelp='Scans Programs Loaded in Computer Memory for Computer Viruses',
              shortHelp='Scans Computer Memory for Viruses')
        parent.DoAddTool(bitmap=wx.Bitmap('img/Scan.png', wx.BITMAP_TYPE_PNG),
              bmpDisabled=wx.NullBitmap, id=wxID_WXMAINFRAMETOOLBARTOOLS_SCAN,
              kind=wx.ITEM_NORMAL, label='Scan Selected Files',
              longHelp='Scans Selected Files or Folders for Computer Viruses',
              shortHelp='Scans Selected Files For Viruses')
        wx.EVT_TOOL(self, wxID_WXMAINFRAMETOOLBARTOOLS_INETUPDATE,
              self.OnToolsUpdate)
        wx.EVT_TOOL(self, wxID_WXMAINFRAMETOOLBARTOOLS_PREFS,
              self.OnToolsPreferences)
        wx.EVT_TOOL(self, wxID_WXMAINFRAMETOOLBARTOOLS_SCAN, self.OnScanButton)
        wx.EVT_TOOL(self, wxID_WXMAINFRAMETOOLBARTOOLS_SCANMEM, self.OnScanMemButton)

        parent.Realize()

    def _init_sizers(self):
        self.gridSizerFrame = wx.GridSizer(cols=1, hgap=0, rows=1, vgap=0)
        self.flexGridSizerPanel = wx.FlexGridSizer(cols=1, hgap=0, rows=4, vgap=0)
        self.gridSizerButtons = wx.GridSizer(cols=2, hgap=0, rows=1, vgap=0)

        self._init_coll_gridSizerFrame_Items(self.gridSizerFrame)
        self._init_coll_flexGridSizerPanel_Items(self.flexGridSizerPanel)
        self._init_coll_flexGridSizerPanel_Growables(self.flexGridSizerPanel)
        self._init_coll_gridSizerButtons_Items(self.gridSizerButtons)

        self.SetSizer(self.gridSizerFrame)
        self.panelFrame.SetSizer(self.flexGridSizerPanel)

    def _init_utils(self):
        self.menuBar = wx.MenuBar()
        self.File = wx.Menu(title='')
        self.Tools = wx.Menu(title='')
        self.Help = wx.Menu(title='')
        self.Reports = wx.Menu(title='')

        self._init_coll_menuBar_Menus(self.menuBar)
        self._init_coll_File_Items(self.File)
        self._init_coll_Tools_Items(self.Tools)
        self._init_coll_Help_Items(self.Help)
        self._init_coll_Reports_Items(self.Reports)

    def _init_ctrls(self, prnt):
        wx.Frame.__init__(self, id=wxID_WXMAINFRAME, name='wxMainFrame',
              parent=prnt, pos=wx.Point(250, 143), size=wx.Size(568, 430),
              style=wx.DEFAULT_FRAME_STYLE, title='ClamWin Free Antivirus')
        self._init_utils()
        self.SetClientSize(wx.Size(560, 403))
        self.SetMenuBar(self.menuBar)
        self.SetHelpText('ClamWin Free Antivirus')
        self.Center(wx.BOTH)

        self.toolBar = wx.ToolBar(id=wxID_WXMAINFRAMETOOLBAR, name='toolBar',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(560, 41),
              style=wx.TB_FLAT | wx.TB_HORIZONTAL | wx.NO_BORDER)
        self.toolBar.SetToolTipString('')
        self.toolBar.SetToolBitmapSize(wx.Size(32, 32))
        self.SetToolBar(self.toolBar)

        self.statusBar = wx.StatusBar(id=wxID_WXMAINFRAMESTATUSBAR, name='statusBar', parent=self, style=0)
        self.statusBar.SetSize(wx.Size(537, 20))
        self.statusBar.SetPosition(wx.Point(0, 218))
        self.statusBar.SetToolTipString('Status Bar')
        self.SetStatusBar(self.statusBar)

        self.panelFrame = wx.Panel(id=wxID_WXMAINFRAMEPANELFRAME,
              name='panelFrame', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(560, 403), style=wx.TAB_TRAVERSAL)

        self.static1 = wx.StaticText(id=wxID_WXMAINFRAMESTATIC1,
              label='Select a folder or a file to scan\n(Hold Shift key to select multiple files or folders)', name='static1',
              parent=self.panelFrame, pos=wx.Point(5, 8), size=wx.Size(435, 32),
              style=0)

        self.dirCtrlScan = wxGenericDirCtrlEx(defaultFilter=0, dir='.', filter='',
              id=wxID_WXMAINFRAMEDIRCTRLSCAN, name='dirCtrlScan',
             parent=self.panelFrame, pos=wx.Point(10, 27), size=wx.Size(540,
             376),
             style=wx.DIRCTRL_SELECT_FIRST | wx.SUNKEN_BORDER | wx.DIRCTRL_3D_INTERNAL)

        self.buttonScan = wx.Button(id=wxID_WXMAINFRAMEBUTTONSCAN, label='&Scan',
              name='buttonScan', parent=self.panelFrame, pos=wx.Point(-85, 10),
              size=wx.Size(75, 23), style=0)
        self.buttonScan.SetDefault()
        wx.EVT_BUTTON(self.buttonScan, wxID_WXMAINFRAMEBUTTONSCAN, self.OnScanButton)

        self.buttonClose = wx.Button(id=wxID_WXMAINFRAMEBUTTONCLOSE,
              label='&Close', name='buttonClose', parent=self.panelFrame,
              pos=wx.Point(10, 10), size=wx.Size(75, 23), style=0)
        wx.EVT_BUTTON(self.buttonClose, wxID_WXMAINFRAMEBUTTONCLOSE, self.OnButtonClose)

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
        self.flexGridSizerPanel.AddSizer(self.gridSizerButtons, flag = wx.GROW)

        # set window icons
        icons = wx.IconBundle()
        icons.AddIconFromFile('img/FrameIcon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcons(icons)
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
                if wx.ID_YES == MsgBox.MessageBox(None, 'ClamWin Free Antivirus', 'ClamWin Free Antivirus is not configured. Would you like to configure it now?', wx.YES_NO | wx.ICON_QUESTION):
                    wxDialogUtils.wxConfigure(None, self._config)
                    configured = self._IsConfigured()

            hasdb = Utils.CheckDatabase(self._config)
            if configured and not hasdb:
                if wx.ID_YES == MsgBox.MessageBox(None, 'ClamWin Free Antivirus', 'You have not yet downloaded Virus Definitions Database. Would you like to download it now?', wx.YES_NO | wx.ICON_QUESTION):
                    wxDialogUtils.wxUpdateVirDB(self, self._config)
                    hasdb = Utils.CheckDatabase(self._config)

            self.buttonScan.Enable(configured and hasdb)
            self.toolBar.EnableTool(wxID_WXMAINFRAMETOOLBARTOOLS_INETUPDATE, configured)
            self.toolBar.EnableTool(wxID_WXMAINFRAMETOOLBARTOOLS_SCAN, configured and hasdb)
            self.toolBar.EnableTool(wxID_WXMAINFRAMETOOLBARTOOLS_SCANMEM, configured and hasdb)

            # check if the db is current (not older than 3 days)
            if hasdb:
                dbpath =  self._config.Get('ClamAV', 'Database')
                daily = os.path.join(dbpath, 'daily.cld')
                if not os.path.isfile(daily):
                    daily = os.path.join(dbpath, 'daily.cvd')
                ver, numv, updated = Utils.GetDBInfo(daily)

            # print updated, time.mktime(time.localtime()), time.mktime(time.localtime()) - updated
            if hasdb and self._config.Get('Updates', 'WarnOutOfDate') and (time.mktime(time.localtime()) - updated > 86400*5):
                if wx.ID_YES == MsgBox.MessageBox(None, 'ClamWin Free Antivirus', 'Virus signature database is older than 5 days and may not offer the latest protection. Would you like to update it now?', wx.YES_NO | wx.ICON_QUESTION):
                    wxDialogUtils.wxUpdateVirDB(self, self._config)
                    hasdb = Utils.CheckDatabase(self._config)

        except Exception, e:
            print 'An Error occured while updating UI selection. %s' % str(e)

    def OnScanButton(self, event):
        scanPath = ''
        for path in self.dirCtrlScan.GetMultiplePath():
            scanPath += "\"%s\" " % path
        wxDialogUtils.wxScan(self, self._config, scanPath)

    def OnScanMemButton(self, event):
        wxDialogUtils.wxScan(self, self._config, None)

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
                MsgBox.ErrorBox(self, 'Could not open help file - %s not found.' % helpfile)
            else:
                try:
                    win32api.ShellExecute(self.GetHandle(), 'open',
                        helpfile,
                        None, curDir, win32con.SW_SHOWNORMAL)
                except Exception, e:
                    MsgBox.ErrorBox(self, 'Could not open help file. Please ensure that you have Adobe Acrobat Reader installed.')

    def OnHelpFAQ(self, event):
        wxDialogUtils.wxGoToInternetUrl('http://www.clamwin.com/content/category/3/7/27/')

    def OnHelpSupport(self, event):
        wxDialogUtils.wxGoToInternetUrl('http://forums.clamwin.com/')

    def OnHelpUpdate(self, event):
        wxDialogUtils.wxGoToInternetUrl('http://www.clamwin.com/index.php?option=content&task=view&id=40&Itemid=60&version='+version.clamwin_version)

    def OnHelpWebsite(self, event):
        wxDialogUtils.wxGoToInternetUrl('http://www.clamwin.com')

class wxGenericDirCtrlEx(wx.GenericDirCtrl):
    def __init__(self, *_args, **_kwargs):
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
