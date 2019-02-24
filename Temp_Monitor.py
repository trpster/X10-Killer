from tkinter import *
from Module_Util import a
from mqtt_subscriber_general import deliverIncomingTemp
import datetime
import time


global maxTemp
global minTemp
maxTemp = 0
minTemp = 200

tempMaster = Tk()
tempMaster.title("Temperature Monitor")

currentTime = datetime.datetime.now()
global DailyReset
DailyReset = False

global lastMinute
lastMinute = 0

global lastSave
lastSave = 0

global tempBoxOpen
tempBoxOpen = False
global dislplaybox

#Define Array: ID(0), Name(1), mintemp(2), mintemp time(3), maxtemp(4), maxtemp time(5), current temp(6), current temp time(7)
# Initial values inserted as place holders; actual values will be set by program.
tArray = []
tArray.append(['231176', 'APARTMENT', 200, currentTime, 0, currentTime, 0, currentTime])
tArray.append(['4557553', 'GARDEN_ROOM', 200, currentTime, 0, currentTime, 0, currentTime])
tArray.append(['ID', 'Location', 200, currentTime, 0, currentTime, 0, currentTime])
tArray.append(['ID', 'Location', 200, currentTime, 0, currentTime, 0, currentTime])
tArray.append(['ID', 'Location', 200, currentTime, 0, currentTime, 0, currentTime])
tArray.append(['ID', 'Location', 200, currentTime, 0, currentTime, 0, currentTime])
tArray.append(['ID', 'Location', 200, currentTime, 0, currentTime, 0, currentTime])
tArray.append(['ID', 'Location', 200, currentTime, 0, currentTime, 0, currentTime])
tArray.append(['ID', 'Location', 200, currentTime, 0, currentTime, 0, currentTime])
tArray.append(['ID', 'Location', 200, currentTime, 0, currentTime, 0, currentTime])

# Need two dictionaries. the first is when the module reports its data
#ID = {'231176':0, '4557553':1}
# The 2nd for when the macro processor needs temp data from array
#nameDic = {'APARTMENT':0, 'GARDEN_ROOM':1}
ID = dict()
nameDic = dict()

def UpdateTimeData():
    global a
    CurrentTime = datetime.datetime.now()
    Dawn = a.dawn_utc(date=CurrentTime, latitude=45.29, longitude=-109.26)
    Dusk = a.dusk_utc(date=CurrentTime, latitude=45.29, longitude=-109.26)
    Dawn = Dawn.astimezone(timezone('US/Mountain')) 
    Dusk = Dusk.astimezone(timezone('US/Mountain'))
    return CurrentTime, Dawn, Dusk;

def getTemp(location):
    #This is used by Macro_Processor when it needs a temp.  It sends the 'location', needs a temp value.
    try:
        pointer = nameDic[location]
    except:
        # if a location hasn't yet been defined
        pointer = 9  #point to data that doesn't exist yet
    
    temp = (tArray[pointer][6])
    if temp == 0:
        #This happens at startup before data has been collected. Rather than
        #return 0 which will trip macros looking for cold temps, return phony 60
        #which won't.
        temp = 60
    return int(temp)

def openDisplayBox():
    global tempBoxOpen
    global displaybox
    if tempBoxOpen == False:
        displaybox = Text(tempMaster)
        size = len(ID)*5
        displaybox.config(height=size, width=40)
        displaybox.grid(row=0, column=60, rowspan=4)
        tempBoxOpen = True
    
def FormatTime(pointer, type):      
    hour = str(tArray[pointer][type].hour)
    minute = str(tArray[pointer][type].minute)
    second = str(tArray[pointer][type].second)
    ampm = 'AM'
    if int(hour) >= 12:
        ampm = 'PM'
    if int(hour) > 12:
        hour = str(int(hour) - 12)
    time_str = str(hour).zfill(2) + ':' + str(minute).zfill(2) + ':' + str(second).zfill(2) + ' ' + ampm
    return time_str;  

def updateArchive(date):
    # Load data in the following order: current date, and then a list
    # from tArray in the following order: name, min temp, max temp
    print('Update archive')
    f = open('temp_archive.txt', 'a')
    f.write(date + ':')
    x =  0
    while x < len(tArray):
        temp = tArray[x][1] + ',' + str(round(tArray[x][2],2)) + ',' + str(round(tArray[x][4],2)) + ':'
        f.write(temp)
        x += 1
    f.write('\n')
    f.close()  

def CheckDailyReset():
    # Clear textbox every day at 12AM
    global DailyReset
    currentTime = datetime.datetime.now()
    if DailyReset == False and currentTime.hour == 0:
        currentTime = datetime.datetime.now()
        date = str(currentTime)[0:10]
        updateArchive(date)
        x = 0
        while x < len(tArray):
            tArray[x][2] = 200
            tArray[x][4] = 0
            x += 1
        DailyReset = True
    if DailyReset == True and currentTime.hour != 0:
        DailyReset = False
    
def updateDisplay(save):
    displaybox.delete(1.0, END)
    if save == True:
        try:
            f = open('index.html', 'w')
            f.write("<meta http-equiv='refresh' content=120 />")
        except:
            print('Could not open index file')
            save = False
    x = 0
    while x < len(nameDic):
        displaybox.insert(INSERT, tArray[x][1])
        displaybox.insert(INSERT, '\n')
        if save == True:
            f.write(tArray[x][1])
            f.write('<BR>')
        tempStuff = 'Current Temp = ' +str(round(tArray[x][6],2)) + ' at ' +FormatTime(x, 7) + '\n'
        displaybox.insert(INSERT, tempStuff)
        if save == True:
            f.write(tempStuff)
            f.write('<BR>')
        tempStuff = 'Minimum Temp = ' +str(round(tArray[x][2],2)) + ' at ' +FormatTime(x, 3) + '\n'
        displaybox.insert(INSERT, tempStuff)
        if save == True:
            f.write(tempStuff)
            f.write('<BR>')
        tempStuff = 'Maximum Temp = ' +str(round(tArray[x][4],2)) + ' at ' +FormatTime(x, 5) + '\n'
        displaybox.insert(INSERT, tempStuff)
        displaybox.insert(INSERT, '\n')
        if save == True:
            f.write(tempStuff)
            f.write('<BR>')
            f.write('<BR>')
            
        x += 1
    if save == True:
        f.close()
            
# tArray: ID(0), Name(1), mintemp(2), mintemp time(3), maxtemp(4), maxtemp time(5), current temp(6), current temp time(7)
def checkTemp():
    temp = deliverIncomingTemp(True)
    status = ""
    if temp[0]=="temperature":
        #print("Temp from :"+temp[1]+":"+temp[2])
        try:
            p=ID[temp[1]]
            newTemp = temp[2][2:4]
            #print("newtemp:",newTemp)
            status = "Temp from: " +temp[1]+": " +temp[2]
            #print("Temp="+str(newTemp))
            currentTime = datetime.datetime.now()
            tArray[p][6] = int(newTemp)   # Current Temp
            tArray[p][7] = currentTime      
            if tArray[p][6] > tArray[p][4]:   # Is Current Temp > Max Temp?
                tArray[p][4] = tArray[p][6]
                tArray[p][5] = currentTime
            if tArray[p][6] < tArray[p][2]:   # Is Current Temp < Min temp?
                tArray[p][2] = tArray[p][6]
                tArray[p][3] = currentTime
        except:
            print("Undefined ID:",temp[1])
            print("ID:",ID)
    return status

def updateDict():
    #Rebuild dicts from scratch at start and anytime device.cfg changes
    #nameDic is in the form "location:array position"
    #ID is in the form "device ID: array position"
    nameDic.clear()  
    ID.clear()   #Builds dictionary in the form "location:module ID" 
    f = open('/home/pi/cowstacker/devices.cfg', 'r')
    config = f.read()
    #print("Devices:", config)
    f.close()
    parsedStr=config.split('\n')
    
    # Look for Temp modules by finding the parsedStr = @TM
    x = 0
    while parsedStr[x] != "@TM":
        x+=1
    x+=1   #X now points to first Temp Module
    ptr = 0
    while parsedStr[x] != "@endTM":
        parsedEntry = parsedStr[x].split('/')
        tArray[ptr][0]= parsedEntry[1]
        tArray[ptr][1]= parsedEntry[0]
        nameDic[parsedEntry[0].upper()] = ptr
        print("New ID:",parsedEntry[0].upper())
        ID[parsedEntry[1].upper()] = ptr
        print("New Name:",parsedEntry[1].upper())
        x+=1
        ptr+=1
    print("ID:", ID)
    print("ID Length:",len(ID))
    print("nameDic:", nameDic)
    #print("tArray:", tArray)

updateDict()
        
def checkReload():
    f=open('/home/pi/cowstacker/reload.txt', 'r')
    reload = f.read()
    f.close()
    if reload == "1":
        updateDict()
        f=open('/home/pi/cowstacker/reload.txt', 'w')
        f.write("0")
        f.close()
    
        
def tempMainLoop():
    global lastMinute
    global lastSave
    checkReload()
    openDisplayBox()
    currentTime = datetime.datetime.now()
    status = ""
    status = checkTemp()
    if currentTime.minute != lastMinute:    # Update the display once each minute
        save = False
        if abs(lastSave - currentTime.minute) > 2:  # Update index.html every 2 minutes
            save = True
            lastSave = currentTime.minute
        updateDisplay(save)
        lastMinute = currentTime.minute
    CheckDailyReset()
    return status


