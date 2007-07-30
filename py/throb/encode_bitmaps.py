#!/usr/bin/env python
#----------------------------------------------------------------------

"""
This is a way to save the startup time when running img2py on lots of
files...
"""

import sys
from wxPython.tools import img2py


command_lines = [

    "   -u -c bmp/scanprogress00.png throbImages.py",
    "-a -u -c bmp/scanprogress01.png throbImages.py",
    "-a -u -c bmp/scanprogress02.png throbImages.py",
    "-a -u -c bmp/scanprogress03.png throbImages.py",
    "-a -u -c bmp/scanprogress04.png throbImages.py",
    "-a -u -c bmp/scanprogress05.png throbImages.py",
    "-a -u -c bmp/scanprogress06.png throbImages.py",
    "-a -u -c bmp/scanprogress07.png throbImages.py",
    "-a -u -c bmp/scanprogress08.png throbImages.py",
    "-a -u -c bmp/scanprogress09.png throbImages.py",
    "-a -u -c bmp/scanprogress10.png throbImages.py",
    "-a -u -c bmp/scanprogress11.png throbImages.py",
    "-a -u -c bmp/scanprogress12.png throbImages.py",

    "-a -u -c bmp/update00.png throbImages.py",
    "-a -u -c bmp/update01.png throbImages.py",
    "-a -u -c bmp/update02.png throbImages.py",
    "-a -u -c bmp/update03.png throbImages.py",
    "-a -u -c bmp/update04.png throbImages.py",
    "-a -u -c bmp/update05.png throbImages.py",
    "-a -u -c bmp/update06.png throbImages.py",
    "-a -u -c bmp/update07.png throbImages.py",
    "-a -u -c bmp/update08.png throbImages.py",
    "-a -u -c bmp/update09.png throbImages.py",
    "-a -u -c bmp/update10.png throbImages.py",
    "-a -u -c bmp/update11.png throbImages.py",
    "-a -u -c bmp/update12.png throbImages.py",
    "-a -u -c bmp/update13.png throbImages.py",
    "-a -u -c bmp/update14.png throbImages.py",
    "-a -u -c bmp/update15.png throbImages.py",
    "-a -u -c bmp/update16.png throbImages.py",
    "-a -u -c bmp/update17.png throbImages.py",
    "-a -u -c bmp/update18.png throbImages.py",
    "-a -u -c bmp/update19.png throbImages.py",

    ]


for line in command_lines:
    args = line.split()
    img2py.main(args)

