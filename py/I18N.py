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

import gettext
import locale
import os
import sys
import traceback
import _winreg
#import Utils



gLocalePath = ""
gLocale = ""

""" Get a translated version of the specified English
    string, based on the current locale.
"""

def RegKeyExists(key, subkey):
    # try to open the regkey
    try:
        hKey = _winreg.OpenKey(key, subkey);
        _winreg.CloseKey(hKey);
        return True;
    except:
        return False;


def install():
    #install the "_" function
    if gLocalePath == "":
        setLocalePath()
    if gLocale == "":
        setLocale()

    os.environ['LANGUAGE'] = gLocale
    gettext.install(gLocale,gLocalePath,True)

def getClamString(englishString):
    global gLocalePath
    global gLocale
    locale.setlocale(locale.LC_ALL, '')
    if gLocalePath == "":
        setLocalePath()
    if gLocale == "":
        setLocale()

    os.environ['LANGUAGE'] = gLocale
    #gettext.bindtextdomain("clamwin", gLocalePath)
    #gettext.textdomain("clamwin")
    #output = gettext.gettext(englishString).decode("utf-8")
    #locale.setlocale(locale.LC_ALL, 'C')
    gettext.install(gLocale,gLocalePath,True)
    output = _(englishString)
    return output


""" Get the path to the ClamWin bin directory,
    using the Path value in the registr
"""
def getClamBinPath():
    clamBinPath = ""
    try:
        regHandle = _winreg.ConnectRegistry(None, _winreg.HKEY_CURRENT_USER)
        keyHandle = _winreg.OpenKey(regHandle, "SOFTWARE\\ClamWin")
        (clamBinPath, _) = _winreg.QueryValueEx(keyHandle, "Path")
        _winreg.CloseKey(keyHandle)
        _winreg.CloseKey(regHandle)
    except Exception, e:
        pass
    if clamBinPath == "":
        try:
            regHandle = _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE)
            keyHandle = _winreg.OpenKey(regHandle, "SOFTWARE\\ClamWin")
            clamBinPath = _winreg.QueryValueEx(keyHandle, "Path")[0]
            _winreg.CloseKey(keyHandle)
            _winreg.CloseKey(regHandle)
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
    key = _winreg.HKEY_CURRENT_USER
    subKey = 'SOFTWARE\\ClamWin'
    if RegKeyExists(key, subKey) == False:
        key = _winreg.HKEY_LOCAL_MACHINE
    hKey = _winreg.OpenKey(key, subKey, 0,_winreg.KEY_WRITE)
    _winreg.SetValueEx(hKey, 'Locale', 0, _winreg.REG_SZ, loc)
    _winreg.CloseKey(hKey)


""" see which locale should be used
"""
def getLocale():
    loc = ''
    key = _winreg.HKEY_CURRENT_USER
    subKey = 'SOFTWARE\\ClamWin'
    if RegKeyExists(key, subKey):
        try:
            regHandle = _winreg.ConnectRegistry(None, _winreg.HKEY_CURRENT_USER)
            keyHandle = _winreg.OpenKey(regHandle, "SOFTWARE\\ClamWin")
            loc = _winreg.QueryValueEx(keyHandle, "Locale")[0]
            _winreg.CloseKey(keyHandle)
            _winreg.CloseKey(regHandle)
            print "HKCU Locale = '[%s]'" % loc
            return loc
        except Exception, e:
            pass
    key = _winreg.HKEY_LOCAL_MACHINE
    if RegKeyExists(key, subKey):
        try:
            regHandle = _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE)
            keyHandle = _winreg.OpenKey(regHandle, "SOFTWARE\\ClamWin")
            loc = _winreg.QueryValueEx(keyHandle, "Locale")[0]
            _winreg.CloseKey(keyHandle)
            _winreg.CloseKey(regHandle)
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
    countryCode = gLocale[:gLocale.find('_')]
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
    forceLocale("fr_FR")
    setLocalePath()
    print "LocalePath = [%s]" % gLocalePath
    setLocale()

