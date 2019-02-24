'''
Created on 11/12/18

@author: Tom
'''

import time 
import datetime
from astral import Astral #@UnresolvedImport
from pytz import timezone #@UnresolvedImport
import math
from math import fabs
from tkinter import *


CurrentTime    = datetime.datetime.now()

global a
a = Astral()  #This will load it just once at launch, rather than
                #every time the time stuff gets called.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
def FormatTime(type, hour, minute, second):       # Type 0 = current time, 1 = Dawn, 2 = Dusk
    if type < 3:                                 # If Type 3, format time sent from caller
        hour = str(UpdateTimeData()[type].hour)
        minute = str(UpdateTimeData()[type].minute)
        second = str(UpdateTimeData()[type].second)
    ampm = 'AM'
    if int(hour) >= 12:
        ampm = 'PM'
    if int(hour) > 12:
        hour = str(int(hour) - 12)
    time_str = str(hour).zfill(2) + ':' + str(minute).zfill(2) + ':' + str(second).zfill(2) + ' ' + ampm
    return time_str;

def logHandler(clear, logEntry):
    #Create an HTML file containing log info so the Bottle_Server
    #Can display it on a webpage.
    timeTag = FormatTime(0,0,0,0)
    if clear:
        f = open('log.html', 'w')
        startInfo = "Starting log at " + timeTag
        f.write(startInfo)
        f.write('<BR>')
    else:
        f = open('log.html', 'a')
        logInfo = timeTag + ": " + logEntry
        f.write(logInfo)
        f.write('<BR>')
    f.close()


def UpdateTimeData():
    global a
    #a = Astral()  Loaded at program launch rather than every time this is called.
    CurrentTime = datetime.datetime.now()
    Dawn = a.dawn_utc(date=CurrentTime, latitude=45.29, longitude=-109.26)
    Dusk = a.dusk_utc(date=CurrentTime, latitude=45.29, longitude=-109.26)
    Dawn = Dawn.astimezone(timezone('US/Mountain'))   #TBD Does it automatically handle DST?
    Dusk = Dusk.astimezone(timezone('US/Mountain'))
    return CurrentTime, Dawn, Dusk;



