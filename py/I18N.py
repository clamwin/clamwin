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

def getClamString(englishString):
    
    os.environ['LANGUAGE'] = locale.getdefaultlocale()[0]
    modName = getCallingModule().replace(".pyo", "")
    modName = modName.replace(".py", "")
    gettext.bindtextdomain(modName, "apptext")
    gettext.textdomain(modName)
    return gettext.gettext(englishString).decode("utf-8")
    
def testIt():
    
    callingModule = getCallingModule()
    print callingModule 


#testIt()



