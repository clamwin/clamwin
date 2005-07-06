import shelve
import win32file
filename=u"c:\\τττ\\aaa"
import os
dir = os.path.split(filename)[0]
print os.path.isdir(dir)
print os.path.supports_unicode_filenames
cwd = os.getcwdu()
shelve = shelve.open(os.path.split(filename)[1])
win32api.SetCurrentDirectory(cwd)

print shelve