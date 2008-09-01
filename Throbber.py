import wx
from wx.lib.throbber import Throbber as wxThrobber

class Throbber(wxThrobber):
    def Draw(self, dc):
        bmp = wx.EmptyBitmap(self.width, self.height)
        memDC = wx.MemoryDC()
        memDC.SelectObject(bmp)
        memDC.SetPen(wx.Pen(self.GetParent().GetBackgroundColour(), 1))
        memDC.SetBrush(wx.Brush(self.GetParent().GetBackgroundColour()))
        memDC.DrawRectangle(0, 0, bmp.GetWidth(), bmp.GetHeight());
        memDC.DrawBitmap(self.submaps[self.sequence[self.current]], 0, 0, True)
        memDC.SelectObject(wx.NullBitmap)

        dc.DrawBitmap(bmp, 0, 0, False)
        if self.overlay and self.showOverlay:
            dc.DrawBitmap(self.overlay, self.overlayX, self.overlayY, True)
        if self.label and self.showLabel:
            dc.DrawText(self.label, self.labelX, self.labelY)
            dc.SetTextForeground(wx.WHITE)
            dc.DrawText(self.label, self.labelX-1, self.labelY-1)
