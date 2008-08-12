import wx
from os.path import sep
from xrcs import xrcwxMainFrame, xrcwxAboutDlg

class wxAboutDlg(xrcwxAboutDlg):
    def __init__(self, parent):
        xrcwxAboutDlg.__init__(self, parent)
        self.SetClientSize(wx.Size(420, 316))
        self.SetAutoLayout(False)
    def OnButton_buttonOK(self, evt):
        self.Close()

class wxMainFrame(xrcwxMainFrame):
    def __init__(self):
        # Scan Files
        self.OnMenu_Scan_Files = self.ScanFiles
        self.OnTool_Scan_Selected_Files = self.ScanFiles
        self.OnButton_buttonScan = self.ScanFiles

        # Scan Memory
        self.OnMenu_Scan_Memory = self.ScanMemory
        self.OnTool_Scan_Computer_Memory = self.ScanMemory

        # Close
        self.OnButton_buttonClose = self.OnMenu_Exit

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

        # About Dialog
        self.about = wxAboutDlg(self)

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

    def ScanFiles(self, evt):
        print 'ClamWin ScanFiles'
        for p in self.GetSelections():
            print p.encode('latin1', 'replace')

    def ScanMemory(self, evt):
        print 'ClamWin ScanMemory'

    def OnMenu_About(self, evt):
        self.about.Show()

    def OnMenu_Exit(self, evt):
        self.Close()

if __name__ == '__main__':
    app = wx.App(redirect=False)
    m = wxMainFrame()
    m.Show()
    app.MainLoop()