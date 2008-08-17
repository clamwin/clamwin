import win32api, win32gui
from win32file import FindFilesW
from os.path import sep
from socket import socket, AF_INET, SOCK_STREAM

import wx
from wx.lib.throbber import Throbber
from wx.lib.masked import TimeCtrl
from wx.tools.XRCed.plugins.xh_gizmos import EditableListBoxXmlHandler

from xrcs import *
from throb import throbImages

from Utils import IsTime24

import ThreadFuture

## Common methods
class wxDlgCommon:
    def SafeClose(self):
        if self.IsModal():
            return self.EndModal(wx.ID_CANCEL)
        else:
            return self.Close()
    def OnChar_hook(self, evt):
        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            self.SafeClose()
        else:
            evt.Skip()
    def OnButton_buttonOK(self, evt):
        self.SafeClose()

class wxAboutDlg(wxDlgCommon, xrcwxAboutDlg):
    def __init__(self, parent):
        xrcwxAboutDlg.__init__(self, parent)
        self.SetClientSize(wx.Size(420, 316))
        self.SetAutoLayout(False)

class wxDialogLogView(wxDlgCommon, xrcwxDialogLogView):
    pass

class wxDialogStatus(xrcwxDialogStatus):
    def __init__(self, parent):
        xrcwxDialogStatus.__init__(self, parent)
        self.parent = parent
        imgs_update = []
        imgs_scan = []
        for i in throbImages.index:
            if i.find('update') != -1:
                imgs_update.append(throbImages.catalog[i].getBitmap())
            else:
                imgs_scan.append(throbImages.catalog[i].getBitmap())
        self.throbberUpdate = Throbber(self, -1, imgs_update, frameDelay=0.1,
                  pos=wx.Point(16, 8), size=wx.Size(56, 300),
                  style=0)
        self.throbberUpdate.Show(False)
        self.throbberScan = Throbber(self, -1, imgs_scan, frameDelay=0.1,
                  pos=wx.Point(16, 8), size=wx.Size(56, 300),
                  style=0)
        self.throbberScan.Show(False)
        self.throbber = self.throbberScan
        self.mode = 'scan'
    def OnInit_dialog(self, evt):
        winstyle = wx.TAB_TRAVERSAL
        if win32api.GetVersionEx()[0] >= 5:
            winstyle = winstyle | wx.TE_AUTO_URL
        self.SetWindowStyleFlag(self.GetWindowStyleFlag() | winstyle)
        win32gui.SetForegroundWindow(self.GetHandle())
        self.textCtrlStatus.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNFACE))
        self.throbber.Show(True)
        self.throbber.Start()
        if self.mode == 'scan':
            ThreadFuture.Future(self.parent.ScanFiles)
    def SetThrobber(self, t):
        if t == 'update':
            self.throbber = self.throbberUpdate
            self.throbberScan.Show(False)
        else:
            self.throbber = self.throbberScan
            self.throbberUpdate.Show(False)
    def OnClose(self, evt):
        evt.Skip()
    def OnButton_buttonStop(self, evt):
        self.throbber.Stop()
        self.throbber.Show(False)
    def OnButton_buttonSave(self, evt):
        self.throbber.Show(True)
        self.throbber.Start()

class wxDialogScheduledScan(wxDlgCommon, xrcwxDialogScheduledScan):
    def __init__(self, parent):
        xrcwxDialogScheduledScan.__init__(self, parent)
        self.SetClientSize(wx.Size(304, 292))
        self.SetAutoLayout(False)
    def OnInit_dialog(self, evt):
        self.timeCtrl = TimeCtrl(parent=self,
                                 pos=wx.Point(172, 54), size=wx.Size(90, 22),
                                 fmt24hr=IsTime24(),
                                 spinButton=self.spinButtonTime,
                                 useFixedWidthFont=False, display_seconds=True)
        self.timeCtrl.SetToolTipString('When the schedule should be started')

class wxPreferencesDlg(wxDlgCommon, xrcwxPreferencesDlg):
    def __init__(self, parent):
        get_resources().AddHandler(EditableListBoxXmlHandler())
        xrcwxPreferencesDlg.__init__(self, parent)
        self.SetClientSize(wx.Size(412, 368))
        self.SetAutoLayout(False)
        self.dialogscheduledscan = wxDialogScheduledScan(self)
    def OnInit_dialog(self, evt):
        # Time Control
        self.timeUpdate = TimeCtrl(parent=self.panelInternetUpdates,
                                   pos=wx.Point(278, 66), size=wx.Size(74, 22),
                                   fmt24hr=IsTime24(), spinButton=self.spinButtonUpdateTime,
                                   useFixedWidthFont=False, display_seconds=True)
        self.timeUpdate.SetToolTipString('When the download should be started')

        # Notebook
        # wxWidgets notebook bug workaround
        # http://sourceforge.net/tracker/index.php?func=detail&aid=645323&group_id=9863&atid=109863
        self.notebook.SetWindowStyleFlag(self.notebook.GetWindowStyleFlag() | wx.NB_MULTILINE)
        self.notebook.SetSize(self.notebook.GetSize() + wx.Size(1, 1))

        # List View Control
        self.imListScheduler = wx.ImageList(height=16, width=16)
        self.imListScheduler.Add(bitmap=wx.Bitmap('img/ListScan.png', wx.BITMAP_TYPE_PNG),
                                 mask=wx.NullBitmap)
        self.lvScheduledTasks = wx.ListView(parent=self.panelScheduledScans,
                                            pos=wx.Point(6, 42), size=wx.Size(298, 188),
                                            style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.lvScheduledTasks.SetToolTipString('List of Scheduled Scans')
        self.lvScheduledTasks.SetImageList(self.imListScheduler, wx.IMAGE_LIST_NORMAL)
        self.lvScheduledTasks.SetImageList(self.imListScheduler, wx.IMAGE_LIST_SMALL)

        self.lvScheduledTasks.InsertColumn(col=0, format=wx.LIST_FORMAT_LEFT, heading='Description', width=-1)
        self.lvScheduledTasks.InsertColumn(col=1, format=wx.LIST_FORMAT_LEFT, heading='Path', width=-1)
        self.lvScheduledTasks.InsertColumn(col=2, format=wx.LIST_FORMAT_LEFT, heading='Frequency', width=-1)

        col_count = self.lvScheduledTasks.GetColumnCount()
        col_size = (self.lvScheduledTasks.GetSize()[0] / col_count) - 1
        self.lvScheduledTasks.SetColumnWidth(0, col_size + 30)
        self.lvScheduledTasks.SetColumnWidth(1, col_size + 5)
        self.lvScheduledTasks.SetColumnWidth(2, col_size - 35)

        self.lvScheduledTasks.Bind(wx.EVT_LIST_ITEM_SELECTED, None)
        self.lvScheduledTasks.Bind(wx.EVT_LIST_ITEM_DESELECTED, None)
        self.lvScheduledTasks.Bind(wx.EVT_LEFT_DCLICK, None)
    def OnButton_buttonOK(self, evt): # Placeholder override for wxDlgCommon method
        self.EndModal(wx.ID_OK)
    def OnButton_buttonCancel(self, evt):
        self.EndModal(wx.ID_CANCEL)
    def OnButton_buttonTaskAdd(self, evt):
        self.dialogscheduledscan.ShowModal()

class wxMainFrame(xrcwxMainFrame):
    def __init__(self):
        # Events mapping
        self.OnButton_ScanFiles = self.OnTool_ScanFiles
        self.OnButton_Close = self.OnMenu_Exit

        # Last one or it will override our method redirections
        xrcwxMainFrame.__init__(self, None)

        # Icon
        icons = wx.IconBundle()
        icons.AddIconFromFile('img/FrameIcon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcons(icons)

        # options for dir tree
        self.dirCtrlScan.ShowHidden(True)
        tree = self.dirCtrlScan.GetTreeCtrl()
        tree.SetWindowStyleFlag(tree.GetWindowStyleFlag() | wx.TR_MULTIPLE)

        # Child dialogs
        self.about = wxAboutDlg(self)
        self.logviewver = wxDialogLogView(self)
        self.dialogstatus = wxDialogStatus(self)
        self.preferencesdlg = wxPreferencesDlg(self)

    def GetSelections(self):
        tree = self.dirCtrlScan.GetTreeCtrl()
        root = tree.GetRootItem()
        paths = []

        sels = tree.GetSelections()
        for sel in sels:
            path = []
            while sel != root:
                path.append(tree.GetItemText(sel))
                sel = tree.GetItemParent(sel)
            path.reverse()
            paths.append(sep.join(path))

        return paths

    def CanonicalizePath(self, path):
        ifansi = path.encode('mbcs')
        if ifansi.find('?') == -1: return ifansi

        plist = path.split(sep)
        p = [ plist[0] ] # drive letter or unc prefix

        for i in range(1, len(plist)):
            f = FindFilesW(sep.join(plist[:i+1]))[-1]
            name = f[-2]
            altname = f[-1]
            if len(altname):
                p.append(altname)
            else:
                p.append(name)

        return sep.join(p).encode('mbcs')

    def OnTool_ScanFiles(self, evt):
        self.dialogstatus.Show()

    def ServerConnection(self):
        s = socket(AF_INET, SOCK_STREAM)
        s.connect(('localhost', 3310))
        f = s.makefile('rw', 0)
        s.close()
        return f

    def ScanFiles(self):
        ctrl = self.dialogstatus.textCtrlStatus
        ctrl.AppendText('Scanner started\n\n') # Without a message it hangs :(
        f = self.ServerConnection()
        for p in self.GetSelections():
            filename = self.CanonicalizePath(p)
            ctrl.SetDefaultStyle(wx.TextAttr(colText=wx.Colour(0,0,0xff)))
            ctrl.AppendText('Scanning ' + filename + '\n\n')
            ctrl.SetDefaultStyle(wx.TextAttr(wx.NullColour))
            f.write('CONTSCAN ' + filename + '\n')
            f.flush()
            while True:
                res = f.readline()
                if len(res) == 0: break
                if res.find('FOUND') != -1:
                    ctrl.SetDefaultStyle(wx.TextAttr(colText=wx.Colour(128,0,0)))                    
                ctrl.AppendText(res)
                ctrl.SetDefaultStyle(wx.TextAttr(wx.NullColour))
        f.close()
        self.dialogstatus.throbber.Stop()
        ctrl.AppendText('\n--Done--\n')

    def OnTool_ScanMemory(self, evt):
        print 'ClamWin ScanMemory'

    def OnMenu_About(self, evt):
        self.about.Show()

    def OnMenu_Exit(self, evt):
        self.Close()

    def OnTool_Update(self, evt):
        self.dialogstatus.SetThrobber('scan')
        self.dialogstatus.ShowModal()

    def OnTool_Preferences(self, evt):
        self.preferencesdlg.ShowModal()

if __name__ == '__main__':
    app = wx.App(redirect=False)
    m = wxMainFrame()
    m.Show()
    app.MainLoop()
