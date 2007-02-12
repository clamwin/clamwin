#-----------------------------------------------------------------------------
# Name:        I18N.py
# Product:     ClamWin Free Antivirus
#
# Author:      kleankoder [kleankoder at users dot sourceforge dot net]
#
# Created:     2005/12/11
# Copyright:   Copyright alch (c) 2005
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

import gettext, locale, os, sys, traceback
import _winreg as wreg

gLocalePath = ""
gLocale = ""

""" Get a translated version of the specified English
    string, based on the current locale.
"""
def getClamString(englishString):
    global gLocalePath
    global gLocale
    if gLocalePath == "":
        setLocalePath()
    if gLocale == "":
        setLocale()

    os.environ['LANGUAGE'] = gLocale
    gettext.bindtextdomain("clamwin", gLocalePath)
    gettext.textdomain("clamwin")
    return gettext.gettext(englishString).decode("utf-8")


""" Get the path to the ClamWin bin directory,
    using the Path value in the registr
"""
def getClamBinPath():
    clamBinPath = ""
    try:
        regHandle = wreg.ConnectRegistry(None, wreg.HKEY_CURRENT_USER)
        keyHandle = wreg.OpenKey(regHandle, "SOFTWARE\\ClamWin")
        (clamBinPath, _) = wreg.QueryValueEx(keyHandle, "Path")
        wreg.CloseKey(keyHandle)
        wreg.CloseKey(regHandle)
    except Exception, e:
        pass
    if clamBinPath == "":
        try:
            regHandle = wreg.ConnectRegistry(None, wreg.HKEY_LOCAL_MACHINE)
            keyHandle = wreg.OpenKey(regHandle, "SOFTWARE\\ClamWin")
            (clamBinPath, _) = wreg.QueryValueEx(keyHandle, "Path")
            wreg.CloseKey(keyHandle)
            wreg.CloseKey(regHandle)
        except Exception, e:
            pass
    print "clambinPath = [%s]" % clamBinPath
    return clamBinPath


""" Set the path to the translated strings, based
    on the Path value in the registry
"""
def setLocalePath():
    global gLocalePath
    clamBinPath = getClamBinPath()
    gLocalePath = clamBinPath[:clamBinPath.rfind("\\")] + "\\locale"    

""" Set the locale.
    First check the registry (both HKCU and HKLM) for the Language setting.
    Then use the system locale.
"""
def setLocale():
    global gLocale
    try:
        regHandle = wreg.ConnectRegistry(None, wreg.HKEY_CURRENT_USER)
        keyHandle = wreg.OpenKey(regHandle, "SOFTWARE\\ClamWin")
        (gLocale, _) = wreg.QueryValueEx(keyHandle, "Locale")
        wreg.CloseKey(keyHandle)
        wreg.CloseKey(regHandle)
        print "HKCU Locale = '[%s]'" % gLocale
    except Exception, e:
        gLocale = ""
        pass
    if gLocale == "":
        try:
            regHandle = wreg.ConnectRegistry(None, wreg.HKEY_LOCAL_MACHINE)
            keyHandle = wreg.OpenKey(regHandle, "SOFTWARE\\ClamWin")
            (gLocale, _) = wreg.QueryValueEx(keyHandle, "Locale")
            wreg.CloseKey(keyHandle)
            wreg.CloseKey(regHandle)
            print "HKLM Locale = '[%s]'" % gLocale
        except Exception, e:
            gLocale = ""
            pass
    if gLocale == "":
        gLocale = locale.getdefaultlocale()[0]
        print "Default Locale = '[%s]'" % gLocale


""" Get the full path including file name, to the
    HTML help file, based on the current locale.
"""
def getHelpFilePath():
    global gLocale
    if gLocale == "":
        setLocale()
    clamBinPath = getClamBinPath()
    localeCode = gLocale
    countryCode = gLocaled[:gLocale.find('_')]
    helpPath = clamBinPath + "\\..\\doc\\manual_" + countryCode + ".chm"
    if not os.path.exists(helpPath):
        helpPath = clamBinPath + "\\..\\doc\\manual_" + countryCode + ".pdf"
        if not os.path.exists(helpPath):
            helpPath = clamBinPath + "\\..\\doc\\manual_EN.chm"
            if not os.path.exists(helpPath):
                helpPath = clamBinPath + "\\..\\doc\\manual_EN.pdf"
        
    return helpPath


""" Same as getClamString, except first find the absolute
    path to the locale directory. Used by the outlook
    add-in which is run from another directory.
"""
def findAndGetClamString(englishString):
    global gLocalePath
    global gLocale
    if gLocalePath == "":
        setLocalePath()
    if gLocale == "":
        setLocale()
    os.environ['LANGUAGE'] = gLocale
    gettext.bindtextdomain("clamwin", gLocalePath)
    gettext.textdomain("clamwin")
    return gettext.gettext(englishString).decode("utf-8")

# module test function
if __name__ == '__main__':
    setLocalePath()
    print "LocalePath = [%s]" % gLocalePath
    setLocale()

