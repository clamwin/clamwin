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

localePath = "..\\locale"

def getCallingModule():
    stackList = traceback.extract_stack()
    stackList.reverse()
    
    for stackItem in stackList:
        modName = stackItem[0]
        indexNum = modName.rfind("\\")
        if indexNum >= 0:
            modName = modName[indexNum+1:]
        if modName.find("I18N.py") < 0:
            callingModName = modName
            return callingModName
    
    raise "Could not find name of calling module"


""" Get a translated version of the specified English
    string, based on the current locale.
"""
def getClamString(englishString):
    global localePath
    os.environ['LANGUAGE'] = locale.getdefaultlocale()[0]
    modName = getCallingModule().replace(".pyo", "")
    modName = modName.replace(".py", "")
    #print "modName = [%s]" % modName
#    gettext.bindtextdomain(modName, localePath)
#    gettext.textdomain(modName)
    gettext.bindtextdomain("clamwin", localePath)
    gettext.textdomain("clamwin")
    #return gettext.gettext(englishString)
    return gettext.gettext(englishString).decode("utf-8")


""" Get the path to the ClamWin bin directory,
    using the Path value in the registr
"""
def getClamBinPath():
    regHandle = wreg.ConnectRegistry(None, wreg.HKEY_LOCAL_MACHINE)
    keyHandle = wreg.OpenKey(regHandle, "SOFTWARE\\ClamWin")
    (clamBinPath, _) = wreg.QueryValueEx(keyHandle, "Path")
    wreg.CloseKey(keyHandle)
    wreg.CloseKey(regHandle)
    return clamBinPath


""" Set the path to the translated strings, based
    on the Path value in the registry
"""
def setLocalePath():
    global localePath
    regHandle = wreg.ConnectRegistry(None, wreg.HKEY_LOCAL_MACHINE)
    keyHandle = wreg.OpenKey(regHandle, "SOFTWARE\\ClamWin")
    (clamBinPath, _) = wreg.QueryValueEx(keyHandle, "Path")
    wreg.CloseKey(keyHandle)
    wreg.CloseKey(regHandle)
    localePath = clamBinPath[:clamBinPath.rfind("\\")] + "\\locale"    


""" Get the full path including file name, to the
    HTML help file, based on the current locale.
"""
def getHelpFilePath():
    clamBinPath = getClamBinPath()
    localeCode = locale.getdefaultlocale()[0]
    countryCode = localeCode[:localeCode.find('_')]
    helpPath = clamBinPath + "\\manual_" + countryCode + ".chm"
    if not os.path.exists(helpPath):
        helpPath = clamBinPath + "\\manual_" + countryCode + ".pdf"
        
    return helpPath


""" Same as getClamString, except first find the absolute
    path to the locale directory. Used by the outlook
    add-in which is run from another directory.
"""
def findAndGetClamString(englishString):

    regHandle = wreg.ConnectRegistry(None, wreg.HKEY_LOCAL_MACHINE)
    keyHandle = wreg.OpenKey(regHandle, "SOFTWARE\\ClamWin")
    (clamBinPath, _) = wreg.QueryValueEx(keyHandle, "Path")
    wreg.CloseKey(keyHandle)
    wreg.CloseKey(regHandle)
    localePath = clamBinPath[:clamBinPath.rfind("\\")] + "\\locale"
    #print "localePath = [%s]" % localePath
    os.environ['LANGUAGE'] = locale.getdefaultlocale()[0]
    modName = getCallingModule().replace(".pyo", "")
    modName = modName.replace(".py", "")
    #print "modName = [%s]" % modName
#    gettext.bindtextdomain(modName, localePath)
#    gettext.textdomain(modName)
    gettext.bindtextdomain("clamwin", localePath)
    gettext.textdomain("clamwin")
    return gettext.gettext(englishString).decode("utf-8")




