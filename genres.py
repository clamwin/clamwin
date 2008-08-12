#!/usr/bin/env python

from glob import glob
from wx.tools.pywxrc import main

main(['-p', '-v', '-o', 'xrcs.py'] + glob('*.xrc'))
