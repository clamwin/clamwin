from wxPython.wx import *
def MessageBox(parent, caption, message, flags = wxOK | wxICON_INFORMATION):
        dlg = wxMessageDialog(parent, message, caption, flags)
        try:
            ret = dlg.ShowModal()
        finally:
            dlg.Destroy()    
        return ret
    
def ErrorBox(parent, message):
    return MessageBox(parent, 'Error', message, wxOK | wxICON_ERROR)

def InfoBox(parent, message):
    return MessageBox(parent, 'Information', message)
                 