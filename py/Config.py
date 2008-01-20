#-----------------------------------------------------------------------------
# Name:        Config.py
# Product:     ClamWin Free Antivirus
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
import ConfigParser
import Utils
import version
import binascii
import sys
if sys.platform.startswith("win"):
    import win32api

REGEX_SEPARATOR="|CLAMWIN_SEP|"

class Settings:
    def __init__(self, filename):
        self._filename = filename
        self._settings = {
        'ClamAV':
        [0, {'ClamScan': '', 'FreshClam': '', 'Database': '',
             'RemoveInfected': '0', 'ScanRecursive': '1',
             'InfectedOnly': '0', 'ShowProgress': '1',
             'Priority': 'Low', 'EnableMbox': '0', 'ScanOle2': '1',
             'ScanArchives': '1', 'MaxSize': '10', 'MaxFiles': '500',
             'MaxRecursion': '5', 'LogFile': '', 'MaxLogSize': '1',
             'MoveInfected': '0', 'QuarantineDir': '',  'Debug': '0',
             'ScanExeOnly': '1', 'DetectPUA': 0, 'ClamScanParams':'', 'Kill': '1',
             'IncludePatterns': '',
             'ExcludePatterns': REGEX_SEPARATOR.join(('*.dbx','*.tbb','*.pst', '*.dat', '*.log', '*.evt', '*.nsf', '*.ntf', '*.chm')),}],
        'Proxy':
        [0, {'Host': '', 'Port': '3128', 'User':'',
             'Password': ''}],
        'Updates':
        [0, {'Enable': '1', 'Frequency': 'Daily', 'Time': '10:00:00',
            'WeekDay': '2', 'DBMirror': 'database.clamav.net',
            'DBUpdateLogFile': '', 'UpdateOnLogon': '0', 'WarnOutOfDate': '1',
            'CheckVersion': '1', 'CheckVersionURL': 'http://clamwin.sourceforge.net/clamwinver.php'}],
        'EmailAlerts':
        [0, {'Enable': '0',
             'SMTPHost': '', 'SMTPPort': '25', 'SMTPUser':'',
             'SMTPPassword': '',
             'From': 'clamwin@yourdomain', 'To': 'admin@yourdomain',
             'Subject': 'ClamWin Virus Alert'}],
        'UI':
        [0, {'TrayNotify': '1', 'ReportInfected': '1', 'Standalone': '0', 'Version': ''}],
        'Schedule':
        [0, {'Path': '', }],
        'EmailScan':
        [0, {'ScanIncoming': '1', 'ScanOutgoing': '1', }],
        }

    def Read(self, template = False):
        write = False
        try:
            conf = ConfigParser.ConfigParser()
            conf.read(self._filename)
        except ConfigParser.Error:
            return False
        for sect in self._settings:
            for name in self._settings[sect][1]:
                try:
                    val = conf.get(section = sect, option = name)
                    if self._settings[sect][0]: # is binary?
                        val = binascii.a2b_hex(val)
                    self._settings[sect][1][name] = val
                except ConfigParser.Error:
                    pass
        if template:
            return True
        # for older version set display infected only to 1
        if self._settings['UI'][1]['Version'] == '':
            self._settings['ClamAV'][1]['InfectedOnly'] = '1'
            write = True

        # rewrite CheckVersionURL for earlier versions    
        if self._settings['UI'][1]['Version'] < '0.90.2.1' and \
           self._settings['Updates'][1]['CheckVersionURL'] == 'http://clamwin.sourceforge.net/clamwin.ver':
            self._settings['Updates'][1]['CheckVersionURL'] = 'http://clamwin.sourceforge.net/clamwinver.php'
            write = True

        if self._settings['UI'][1]['Version'] < version.clamwin_version:
            self._settings['UI'][1]['Version'] = version.clamwin_version
            write = True
            
        if write:
            print 'Config updated to version %s. Saving' % version.clamwin_version
            self.Write()
        return True

    def Write(self):
        try:
            conf = ConfigParser.ConfigParser()
            for sect in self._settings:
                if not conf.has_section(sect):
                    conf.add_section(sect)
                    for name in self._settings[sect][1]:
                        val = self._settings[sect][1][name]
                        if self._settings[sect][0]: # is binary?
                            val = binascii.b2a_hex(val)
                        conf.set(sect, option = name, value = val)
            conf.write(file(self._filename, 'w'))
        except (ConfigParser.Error, IOError):
            return False
        return True


    def Get(self, sect, name):
        value = self._settings[sect][1][name]
        if(value is None):
            return ""
        return Utils.SafeExpandEnvironmentStrings(value)


    def Set(self, sect, name, val):
        if val is None:
            val = ''
        if not self._settings.has_key(sect) or \
            not self._settings[sect][1].has_key(name):
            raise AttributeError('Internal Error. No such attribute: '+ sect + ': ' + name)
        else:
            self._settings[sect][1][name] = val

    def GetFilename(self):
        return self._filename