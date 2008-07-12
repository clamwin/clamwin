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
from copy import deepcopy
from types import StringType, IntType, BooleanType  

mapping = { 'get': StringType, 'getint': IntType, 'getboolean': BooleanType }

REGEX_SEPARATOR="|CLAMWIN_SEP|"

class Settings:
    def __init__(self, filename):
        self._filename = filename
        self._options = {
            'clamav':
            {
                'clamscan'          : [ 'get', '' ],
                'freshclam'         : [ 'get', '' ],
                'database'          : [ 'get', '' ],
                'removeinfected'    : [ 'getboolean', False ],
                'scanrecursive'     : [ 'getboolean', True ],
                'infectedonly'      : [ 'getboolean', False ],
                'showprogress'      : [ 'getboolean', True ],
                'priority'          : [ 'get', 'Low' ],
                'enablembox'        : [ 'getboolean', False ],
                'scanole2'          : [ 'getboolean',  True ],
                'scanarchives'      : [ 'getboolean', True ],
                'maxscansize'       : [ 'getint', 150 ],
                'maxfiles'          : [ 'getint', 500 ],
                'maxfilesize'       : [ 'getint', 100 ],
                'maxrecursion'      : [ 'getint', 5 ],
                'logfile'           : [ 'get', '' ],
                'maxlogsize'        : [ 'getint', 1 ],
                'moveinfected'      : [ 'getboolean', False ],
                'quarantinedir'     : [ 'get', '' ],
                'debug'             : [ 'getboolean', False ],
                'clamscanparams'    : [ 'get', '' ],
                'kill'              : [ 'getboolean', True ],
                'includepatterns'   : [ 'get', '' ],
                'excludepatterns'   : [ 'get', REGEX_SEPARATOR.join(('*.dbx','*.tbb','*.pst', '*.dat', '*.log', '*.evt', '*.nsf', '*.ntf', '*.chm')) ]
            },
            'proxy':
            {
                'host'              : [ 'get', '' ],
                'port'              : [ 'getint', 3128 ],
                'user'              : [ 'get', '' ],
                'password'          : [ 'get', '' ]
            },
            'updates':
            {
                'enable'            : [ 'getboolean', True ],
                'frequency'         : [ 'get', 'Daily' ],
                'time'              : [ 'get', '10:00:00' ],
                'weekday'           : [ 'getint', 2 ],
                'dbmirror'          : [ 'get', 'database.clamav.net' ],
                'dbupdatelogfile'   : [ 'get', '' ],
                'updateonlogon'     : [ 'getboolean', False ],
                'warnoutofdate'     : [ 'getboolean', True ],
                'checkversion'      : [ 'getboolean', True ],
                'checkversionurl'   : [ 'get', 'http://clamwin.sourceforge.net/clamwinver.php' ]
            },
            'emailalerts':
            {    
                'enable'            : [ 'getboolean', False ],
                'smtphost'          : [ 'get', '' ],
                'smtpport'          : [ 'getint', 25 ],
                'smtpuser'          : [ 'get', '' ],
                'smtppassword'      : [ 'get', '' ],
                'from'              : [ 'get', 'clamwin@yourdomain' ],
                'to'                : [ 'get', 'admin@yourdomain' ],
                'subject'           : [ 'get', 'ClamWin Virus Alert' ]
            },
            'ui':
            {
                'traynotify'        : [ 'getboolean', True ],
                'reportinfected'    : [ 'getboolean', True ],
                'standalone'        : [ 'getboolean', False ],
                'version'           : [ 'get', '']
            },
            'schedule':
            {
                'path'              : [ 'get', '' ]
            },
            'emailscan':
            {
                'scanincoming'      : [ 'getboolean', True ],
                'scanoutgoing'      : [ 'getboolean', True ],
                'showsplash'        : [ 'getboolean', False ],
            }
        }
        self._settings = deepcopy(self._options)

    def Get(self, section, option, expand=True):
        value = self._settings[section.lower()][option.lower()][1]
        if expand and self._settings[section.lower()][option.lower()][0] == 'get':
            return Utils.SafeExpandEnvironmentStrings(value)
        return value

    def Set(self, section, option, value):
        if type(value) != mapping[self._options[section.lower()][option.lower()][0]]:
            raise Exception, 'Invalid ' + str(type(value)) + ' for option [' + section + '] ' + option
        self._settings[section.lower()][option.lower()][1] = value

    def Read(self, template = False):
        try:
            conf = ConfigParser.ConfigParser()
            conf.read(self._filename)
        except ConfigParser.Error:
            return False
        for section in conf.sections():
            if section.lower() not in self._options.keys():
                print 'Invalid config section', section
                continue
            for option in conf.options(section):
                if option.lower() not in self._options[section.lower()].keys():
                    print 'Invalid config option', option, 'in section', section
                    continue
                s, o = section.lower(), option.lower()
                getter = getattr(conf, self._settings[s][o][0])
                try:
                    value = getter(section, o)
                except:
                    print 'Invalid value type for', o, 'in section', s
                    value = self._settings[s][o][1]
                self.Set(s, o, value)
        return True

    def Write(self):
        conf = ConfigParser.ConfigParser()
        for section in self._options.keys():
            for option in self._options[section].keys():
                value = self.Get(section, option, expand=False)
                if value != self._options[section][option][1]:
                    if not conf.has_section(section):
                        conf.add_section(section)
                    conf.set(section, option, value)
        conf.write(file(self._filename, 'w'))
        return True

    def GetFilename(self):
        return self._filename
