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
sb_top_dir = os.path.abspath(os.path.dirname(os.path.join(__file__, "../../../..")))
sys.path.append(sb_top_dir)
sys.path.append(os.path.join(sb_top_dir,"py"))
sys.path.append(os.path.join(sb_top_dir,"../addons/pyclamav/build/lib.win32-2.3"))

import version


# ModuleFinder can't handle runtime changes to __path__, but win32com uses them,
# particularly for people who build from sources.  Hook this in.
try:
    import modulefinder
    import win32com
    for p in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", p)
    for extra in ["win32com.shell","win32com.mapi"]:
        __import__(extra)
        m = sys.modules[extra]
        for p in m.__path__[1:]:
            modulefinder.AddPackagePath(extra, p)
except ImportError:
    # no build path setup, no worries.
    pass

from distutils.core import setup
import py2exe


py2exe_options = dict(
    packages = "encodings",
    excludes = "win32ui,pywin,pywin.debugger", # pywin is a package, and still seems to be included.
    includes = "throb,dbhash", # AVI throb images
    dll_excludes = "dapi.dll,mapi32.dll",
    optimize = '02',
    typelibs = [
        ('{00062FFF-0000-0000-C000-000000000046}', 0, 9, 0),
        ('{2DF8D04C-5BFA-101B-BDE5-00AA0044DE52}', 0, 2, 1),
        ('{AC0714F2-3D04-11D1-AE7D-00A0C90F26F4}', 0, 1, 0),
    ]
)

# These are just objects passed to py2exe
outlook_addin = dict(
    icon_resources = [(1, "img/FrameIcon.ico")],
    company_name = "alch",
    copyright = "alch (c)  2004",
    comments = "Outlook Addin for ClamWin Antivirus",
    modules = ["OlAddin"],
    dest_base = "bin/OlAddin",
#    create_exe = False,
)

explorer_shell = dict(
    company_name = "alch",
    copyright = "alch (c)  2004",
    comments = "Windows Explorer Context Menu Handler for ClamWin Antivirus",
    icon_resources = [(1, "img/FrameIcon.ico")],
    modules = ["ExplorerShell"],
    dest_base = "bin/ExplorerShell",
    create_exe = False,
)

scanner = dict(
    company_name = "alch",
    copyright = "alch (c)  2004",
    comments = "ClamWin Antivirus Scanner",
    icon_resources = [(1, "img/FrameIcon.ico")],
    script = os.path.join(sb_top_dir, "py", "ClamWin.py"),
    dest_base = "bin/ClamWin",
)

tray = dict(
    company_name = "alch",
    copyright = "alch (c)  2004",
    comments = "Taskbar Tray Icon Module for ClamWin Antivirus",
    icon_resources = [(1, "img/FrameIcon.ico")],
    script = os.path.join(sb_top_dir, "py", "ClamTray.py"),
    dest_base = "bin/ClamTray",
)

winclose = dict(
    company_name = "alch",
    copyright = "alch (c)  2004",
    comments = "Setup Utility",
    icon_resources = [(1, "img/FrameIcon.ico")],
    script = os.path.join(sb_top_dir, "py", "CloseWindows.py"),
    dest_base = "bin/WClose",
)

image_files = [
    ["bin/img", glob.glob(os.path.join(sb_top_dir, "py/img/*.*"))],
]

# Default and only distutils command is "py2exe" - save adding it to the
# command line every single time.
if len(sys.argv)==1 or \
   (len(sys.argv)==2 and sys.argv[1] in ['-q', '-n']):
    sys.argv.append("py2exe")

setup(name="ClamWin Antivirus",
      version=version.clamwin_version,
      description="ClamWin Antivirus",
      #com_server=[outlook_addin],
      windows=[scanner, tray, winclose],
      # and the misc data files
      data_files = image_files,
      #options = {"py2exe" : py2exe_options},
      zipfile = "lib/clamwin.zip",
)
