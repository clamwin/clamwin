#-----------------------------------------------------------------------------
# Name:        setup_all.py
# Product:     ClamWin Antivirus
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

#-----------------------------------------------------------------------------
# setup_all.py
# A distutils setup script for SpamBayes binaries

import sys, os, glob
import version


# ModuleFinder can't handle runtime changes to __path__, but win32com uses them,
# particularly for people who build from sources.  Hook this in.
try:
    import modulefinder
    import win32com
    for p in win32com.__path__[1:]:
        modulefinder.AddPackagePath('win32com', p)
    for extra in [ 'win32com.shell', 'win32com.mapi']:
        __import__(extra)
        m = sys.modules[extra]
        for p in m.__path__[1:]:
            modulefinder.AddPackagePath(extra, p)
except ImportError:
    # no build path setup, no worries.
    pass

from distutils.core import setup
import py2exe

ver = version.clamwin_version
while ver.count('.') < 3:
    ver = ver + '.0'

manifest = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
manifestVersion="1.0">
<assemblyIdentity
    version="%s"
    processorArchitecture="x86"
    name="Controls"
    type="win32"
/>
<description>ClamWin Free Antivirus</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
""" % ver

py2exe_options = dict(
    packages = 'encodings',
    excludes = 'win32ui, pywin, pywin.debugger', # pywin is a package, and still seems to be included.
    includes = 'throb, dbhash', # AVI throb images
    dll_excludes = 'dapi.dll, mapi32.dll, msvcr80.dll',
    optimize = '02',
)

scanner = dict(
    company_name = 'ClamWin Pty Ltd',
    copyright = 'ClamWin Pty Ltd (c) 2008',
    comments = 'ClamWin Antivirus Scanner',
    icon_resources = [(1, 'img/FrameIcon.ico')],
    script = 'ClamWin.py',
    dest_base = 'bin/ClamWin',
    other_resources = [(24, 1, manifest)],
)

tray = dict(
    company_name = 'ClamWin Pty Ltd',
    copyright = 'ClamWin Pty Ltd (c) 2008',
    comments = 'Taskbar Tray Icon Module for ClamWin Antivirus',
    icon_resources = [(1, 'img/FrameIcon.ico')],
    script = 'ClamTray.py',
    dest_base = 'bin/ClamTray',
    other_resources = [(24, 1, manifest)],
)

winclose = dict(
    company_name = 'ClamWin Pty Ltd',
    copyright = 'ClamWin Pty Ltd (c) 2008',
    comments = 'Setup Utility',
    icon_resources = [(1, 'img/FrameIcon.ico')],
    script = 'CloseWindows.py',
    dest_base = 'bin/WClose',
)

image_files = [
    ['bin/img', glob.glob('img/*.*')],
]

# Default and only distutils command is "py2exe" - save adding it to the
# command line every single time.
if len(sys.argv) == 1 or \
   (len(sys.argv) == 2 and sys.argv[1] in ['-q', '-n']):
    sys.argv.append('py2exe')

setup(name='ClamWin Antivirus',
      version=ver,
      description='ClamWin Antivirus',
      windows=[scanner, tray, winclose],
      data_files = image_files,
      options = {'py2exe' : py2exe_options},
      zipfile = 'lib/clamwin.zip',
)
