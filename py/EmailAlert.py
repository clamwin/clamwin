#-----------------------------------------------------------------------------
# Name:        EmailAlert.py
# Product:     ClamWin Free Antivirus
#
# Author:      alch [alch at users dot sourceforge dot net]
#
# Created:     2004/28/04
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

import sys, os, re
import smtplib

# Import the email modules we'll need
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import email
import Utils, ThreadFuture
from I18N import getClamString as _
class EmailMsg(MIMEMultipart):
    def __init__(self, From, To, Subject, Body, Reports=()):
        MIMEMultipart.__init__(self)
        self['Date'] =  email.Utils.formatdate(localtime = True)
        self['From'] = From
        self['To'] = To
        self['Subject'] = Subject        
        self.preamble = 'This is a MIME Message\r\n'
        self.epilogue = '\r\n'
        self.attach(MIMEText(Body))        
        for attachment in Reports:
            report = file(attachment, 'rt').read()
            #if sys.platform.startswith('win'):
                # replace cygwin-like pathes with windows-like
                #report = re.sub('/cygdrive/([A-Za-z])/', r'\1:/', report).replace('/', '\\')  
            part = MIMEText(report)
            reprot = None

            part.add_header('Content-Disposition', 'attachment',
                        filename='report.txt')
            self.attach(part)        
            
    def Send(self, host, port=25, username='', password='', wait=False):
        Func = ThreadFuture.Future(self._Send, self['From'], self['To'], self.as_string(), 
                host, port, username, password)    
        if wait:
            return Func()
                
    def _Send(From, To, Body, Host, Port, Username, Password):
        error = ''
        # try toi send 3 times before giving up
        for i in range(3):
            try:
                # Send the email via our own SMTP server.
                s = smtplib.SMTP()
                ##s.set_debuglevel(9)
                s.connect(Host, Port)        
                if len(Username):
                    s.login(Username, Password)            
                # To Address can be separated by commas or semicolons
                if To.find(',') != -1:
                    To = To.split(',')
                elif To.find(';') != -1:
                    To = To.split(';')            
                s.sendmail(From, To, Body)
                s.quit()
                s.close()
                print _('Email alert to %s has been sent successfully.') % To
                return (True, '')
            except Exception, e:
                error = str(e)
                print _('Could not send an email. Error: %s') % error                                        
        return (False, error)         
    _Send = staticmethod(_Send)    
        
class VirusAlertMsg(EmailMsg):
    def __init__(self, From, To, Subject, Host, Port, 
                User, Password, Reports=(), Body=None):                                    
        if Body is None:
            # get computer name for the message body                          
            Body = _('ClamWin detected a virus on the following computer: %s\n\n' \
                    'Please review the attached log files for more details.\n') % Utils.GetHostName()
        
        self._host = Host
        self._port = Port
        self._user = User
        self._password = Password
        
        EmailMsg.__init__(self, From, To, Subject, Body, Reports)           
                            
    def Send(self,  wait = False):
        return EmailMsg.Send(self, self._host, self._port, self._user, self._password, wait)                        
            
        
class ConfigVirusAlertMsg(VirusAlertMsg):
     def __init__(self, config, Reports=(), Body=None):                    
        VirusAlertMsg.__init__(self, config.Get('EmailAlerts', 'From'),
                            config.Get('EmailAlerts', 'To'), 
                            config.Get('EmailAlerts', 'Subject'),
                            config.Get('EmailAlerts', 'SMTPHost'),
                            int(config.Get('EmailAlerts', 'SMTPPort')),
                            config.Get('EmailAlerts', 'SMTPUser'),
                            config.Get('EmailAlerts', 'SMTPPassword'),
                            Reports, Body)
                        

if __name__ == '__main__':
    import Config     
    config = Config.Settings('ClamWin.conf')    
    config.Read()
    msg = ConfigVirusAlertMsg(config, ('c:\\test.txt',))
    msg.Send(wait=True)
    print 'exiting'
     