#-----------------------------------------------------------------------------
# Name:        RedirectStd.py
# Product:     ClamWin Free Antivirus
#
# Author:      alch [alch at users dot sourceforge dot net]
#
# Created:     2004/22/03
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
import sys, os
import win32api

if hasattr(sys, 'frozen'):
    sys.path.insert(0, sys.prefix)

# If we are not running in a console, redirect all print statements to the
# win32traceutil collector.
# You can view output either from Pythonwin's "Tools->Trace Collector Debugging Tool",
# or simply run "win32traceutil.py" from a command prompt.

try:
    win32api.GetConsoleTitle()
except win32api.error:
    # No console - if we are running from Python sources,
    # redirect to win32traceutil, but if running from a binary
    # install, redirect to a log file.
    if hasattr(sys, 'frozen'):
        temp_dir = win32api.GetTempPath()
        for i in range(3, 0, -1):
            try: os.unlink(os.path.join(temp_dir, 'ClamWin%d.log' % (i + 1)))
            except os.error: pass
            try:
                os.rename(
                    os.path.join(temp_dir, 'ClamWin%d.log' % i),
                    os.path.join(temp_dir, 'ClamWin%d.log' % (i + 1))
                    )
            except os.error: pass
        # Open this log, as unbuffered so crashes still get written.
        sys.stdout = file(os.path.join(temp_dir, 'ClamWin1.log'), 'wt', 0)
        sys.stderr = sys.stdout
    else:
        import win32traceutil
