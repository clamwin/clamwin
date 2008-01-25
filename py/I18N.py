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
import locale
import Utils
import time

gLocalePath = ""
gLocale = ""

""" Get a translated version of the specified English
    string, based on the current locale.
"""
def getClamString(englishString):
    global gLocalePath
    global gLocale
    locale.setlocale(locale.LC_ALL, '')
    if gLocalePath == "":
        setLocalePath()
    if gLocale == "":
        setLocale()

    os.environ['LANGUAGE'] = gLocale
    gettext.bindtextdomain("clamwin", gLocalePath)
    gettext.textdomain("clamwin")
    output = gettext.gettext(englishString).decode("utf-8")
    locale.setlocale(locale.LC_ALL, 'C')
    return output


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

""" Force the Locale in the registry to override Windows UI locale
"""
def forceLocale(loc):
    print "Forcing Locale to [%s]" % loc
    key = wreg.HKEY_CURRENT_USER
    subKey = 'SOFTWARE\\ClamWin'
    if Utils.RegKeyExists(key, subKey) == False:
        key = wreg.HKEY_LOCAL_MACHINE
    hKey = wreg.OpenKey(key, subKey, 0,wreg.KEY_WRITE)
    wreg.SetValueEx(hKey, 'Locale', 0, wreg.REG_SZ, loc)
    wreg.CloseKey(hKey)


""" see which locale should be used
"""
def getLocale():
    loc = ''
    key = wreg.HKEY_CURRENT_USER
    subKey = 'SOFTWARE\\ClamWin'
    if (Utils.RegKeyExists(key, subKey)):
        try:
            regHandle = wreg.ConnectRegistry(None, wreg.HKEY_CURRENT_USER)
            keyHandle = wreg.OpenKey(regHandle, "SOFTWARE\\ClamWin")
            (loc, _) = wreg.QueryValueEx(keyHandle, "Locale")
            wreg.CloseKey(keyHandle)
            wreg.CloseKey(regHandle)
            print "HKCU Locale = '[%s]'" % loc
            return loc
        except Exception, e:
            pass
    key = wreg.HKEY_LOCAL_MACHINE
    if (Utils.RegKeyExists(key, subKey)):
        try:
            regHandle = wreg.ConnectRegistry(None, wreg.HKEY_LOCAL_MACHINE)
            keyHandle = wreg.OpenKey(regHandle, "SOFTWARE\\ClamWin")
            (loc, _) = wreg.QueryValueEx(keyHandle, "Locale")
            wreg.CloseKey(keyHandle)
            wreg.CloseKey(regHandle)
            print "HKLM Locale = '[%s]'" % loc
            return loc
        except Exception, e:
            pass
    return ''

""" Set the locale.
    First check the registry (both HKCU and HKLM) for the Language setting.
    Then use the system locale.
"""
def setLocale():
    global gLocale
    gLocale = getLocale()
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
    languageCode = gLocale.split('_')[0];
    print "languageCode = " + languageCode
    helpPath = os.path.join(clamBinPath, "..", "doc", "manual_" + languageCode + ".chm")
    if not os.path.exists(helpPath):
        helpPath = os.path.join(clamBinPath, "..", "doc", "manual_" + languageCode + ".pdf")
        if not os.path.exists(helpPath):
            helpPath = os.path.join(clamBinPath, "..", "doc", "manual_EN.chm")
            if not os.path.exists(helpPath):
                helpPath = os.path.join(clamBinPath, "..", "doc", "manual_EN.pdf")
    print 'helpPath = ' + helpPath
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

def getDateTimeString():
    tm = time.localtime()
    fmt = getClamString('%a %d %b %Y %H:%M:%S')
    global gLocalePath
    global gLocale
    locale.setlocale(locale.LC_ALL, '')
    if gLocalePath == "":
        setLocalePath()
    if gLocale == "":
        setLocale()

    os.environ['LANGUAGE'] = gLocale
    output = time.strftime(fmt, tm);
    locale.setlocale(locale.LC_ALL, 'C')
    print "DATETIME = '%s'" % output
    return output

# module test function
if __name__ == '__main__':
    forceLocale("nl_BE")
    setLocalePath()
    print "LocalePath = [%s]" % gLocalePath
    print "DateTime = [%s]" % getDateTimeString()
    setLocale()

