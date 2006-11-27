#-----------------------------------------------------------------------------
# Name:        Scheduler.py
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
#!/usr/bin/env python


import os, tempfile
import sched, time, locale
import types
import threading


class Scheduler(threading.Thread):
    # empty tuple for status_filenames parameter will reuslt in no checking
    # for missed schedules
    def __init__(self, frequency, startTime, weekDay, action, argument=(),
            status_filenames=(), loopDelay = 0.5):
        threading.Thread.__init__(self)
        self._filenames = status_filenames
        self._delay = 0.5
        self._loopDelay = loopDelay
        self._cancelling = False
        self._frequency = frequency
        self._weekDay = weekDay
        self._startTime = startTime

        self._action = action
        self._argument = argument
        self._lastRun = self._ReadLastRun()

        self._sched = sched.scheduler(time.time, self._DelayFunc)
        self._missedSchedule = False
        self._id = self._sched.enterabs(self._CalcNextRun(), 0, self._RunTask, ())

    def reset(self, frequency, startTime, weekDay, action, argument=(), loopDelay = 0.2):
        self._delay = 1.0
        self._loopDelay = loopDelay
        self._cancelling = False
        self._frequency = frequency
        self._weekDay = weekDay
        self._startTime = startTime

        self._action = action
        self._argument = argument
        self._lastRun = self._ReadLastRun()
        self._missedSchedule = False

        # stop current thread
        self.stop()
        threading.Thread.__init__(self)


        # ensure it stopped
        i = 0
        while self.isAlive() and i < 50:
            time.sleep(0.1)
            i+=1

        # recreate scheduled event
        self._id = self._sched.enterabs(self._CalcNextRun(), 0, self._RunTask, ())


    def _ReadLastRun(self):
        # 0 signifies an error
        t = 0

        # read when the task was run last
        for filename in self._filenames:
            try:
                f = file(os.path.join(tempfile.gettempdir(), filename), 'r')
                t = f.read()
                f.close()
            except:
                t = 0
                continue
            # check that we have a float
            if not isinstance(t, types.FloatType):
                t = 0
                continue
            if time.time() < float(t):
                # got time in future, ignore it
                t = 0
                continue
            else:
                break

        return float(t)

    def _WriteLastRun(self):
        # save time when the task was run for future
        for filename in self._filenames:
            try:
                f = file(os.path.join(tempfile.gettempdir(), filename), 'w')
                f.write(str(self._lastRun))
                f.close()
            except IOError:
                pass

    def _AdjustDST(self, t):
        # deal with daylight savings, if we're on the edge
        dstDiff = time.localtime().tm_isdst - time.localtime(t).tm_isdst
        t += dstDiff * 3600.00
        return t

    # returns time in seconds (as in time.time())
    # when next scheduled run occurs
    def _CalcNextRun(self):
        # calculate when the next task should run
        # depending on last run time, update frequency,
        # task start time and day of the week

        # set C locale, otherwise python and wxpython complain
        locale.setlocale(locale.LC_ALL, 'C')
        # get current time, skip milliseconds
        t = time.time()
        if self._frequency == 'Hourly':
            try:
                # use only MM:SS part of starttime
                schedTime = time.mktime(time.strptime(time.strftime('%d-%m-%Y %H:') + self._startTime.split(':', 1)[1],'%d-%m-%Y %H:%M:%S'))
            except ValueError, e:
                print "couldn't parse time, self._startTime = %s.\n Error: %s" % (self._startTime, str(e))
                self._missedSchedule = True
                schedTime = t + 120
            addTime = 3600.0
        elif self._frequency in ('Weekly', 'Once'):
            try:
                lt = time.localtime(t)
                # use  weekday and HH:MM:SS part of starttime
                schedTime = time.mktime(time.strptime(str(lt.tm_yday - lt.tm_wday + self._weekDay) + \
                            time.strftime(' %Y ', lt) + self._startTime, '%j %Y %H:%M:%S'))
            except ValueError, e:
                print "couldn't parse time, self._startTime = %s. self._weekDay = %i\n Error: %s" % (self._startTime, self._weekDay, str(e))
                self._missedSchedule = True
                schedTime = t + 120
            addTime = 3600.0*24*7
        else: #'Daily' or 'Workdays' is default
            try:
                # use HH:MM:SS part of starttime
                schedTime = time.mktime(time.strptime(time.strftime('%d-%m-%Y ') + self._startTime,'%d-%m-%Y %H:%M:%S'))
            except ValueError, e:
                self._missedSchedule = True
                schedTime = t + 120
                print "couldn't parse time, self._startTime = %s.\n Error: %s" % (self._startTime, str(e))
            addTime = 3600.0*24


        # go to next time interval if it is out
        tmp = schedTime
        while self._AdjustDST(schedTime) < t:
            schedTime += addTime

        # move out of the weekend for workdays
        if self._frequency == 'Workdays':
            while time.localtime(self._AdjustDST(schedTime)).tm_wday in (5,6):
                schedTime += addTime
            if tmp < schedTime:
                addTime = schedTime - tmp

        #don't return for missed schedule if frequency is workdays and it is weekend now
        if self._frequency != 'Workdays' or time.localtime(t).tm_wday not in (5,6):
            # check if we missed the scheduled run
            # and return now (+ 2 minutes) instead
            if  self._lastRun != 0 and self._AdjustDST(schedTime) - addTime > self._lastRun:
                t = t + 120
                print 'Schedule missed, returning: %s' % time.asctime(time.localtime(t))
                try:
                      print 'LastRun: %s' % time.asctime(time.localtime(self._lastRun))
                except:
                      pass
                self._missedSchedule = True
                return t

        schedTime = self._AdjustDST(schedTime)
        print 'Scheduling task for: %s' % time.asctime(time.localtime(schedTime))
        return schedTime + self._delay


    def _RunTask(self):
        # get current time
        if self._cancelling:
            return
        # set C locale, otherwise python and wxpython complain
        locale.setlocale(locale.LC_ALL, 'C')

        t = time.time()

        # execute the action
        print 'running task on: %s. Frequency is: %s\n' % (time.strftime('%d-%m-%y %H:%M:%S', time.localtime(t)), self._frequency)
        void = self._action(*self._argument)
        self._lastRun = t
        self._WriteLastRun()

        # schedule next action
        if self._frequency != 'Once' and not self._missedSchedule:
            self._id = self._sched.enterabs(self._CalcNextRun(), 0, self._RunTask, ())

    def _DelayFunc(self, delay):
        start = time.time()
        while not self._cancelling and int(time.time() - start) < int(delay):
            time.sleep(self._loopDelay)

    def run(self):
        self._sched.run()
        print 'Scheduler terminated'

    def stop(self):
        try:
           self._sched.cancel(self._id)
        except:
           pass
        self._cancelling = True

if __name__ == '__main__':
    import sys
    def action():
        print 'execute'

    s = Scheduler('Workdays', '20:20:00', 5, action)
    s.start()
    while sys.stdin.read(1) != 'c':
        time.sleep(0)
    s.stop()
    s.join(1)
    print 'completed'


