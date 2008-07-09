import wx

def MessageBox(parent, caption, message, flags = wx.OK | wx.ICON_INFORMATION):
        dlg = wx.MessageDialog(parent, message, caption, flags)
        try:
            ret = dlg.ShowModal()
        finally:
            dlg.Destroy()
        return ret

def ErrorBox(parent, message):
    return MessageBox(parent, 'Error', message, wx.OK | wx.ICON_ERROR)

def InfoBox(parent, message):
    return MessageBox(parent, 'Information', message)
