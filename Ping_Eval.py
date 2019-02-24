import datetime
from mqtt_subscriber_general import deliverAll

pingDict = dict()
pingDict.clear()
global ptr
ping = []
ptr=0
deviceDict = dict()
deviceDict.clear()


def getData():
    global ptr
    traffic = deliverAll()
    if traffic[1] == "b'PING'":
        currentTime = datetime.datetime.now()
        try:    #see if it is already in the dictionary
            exists = pingDict[traffic[0]]
            ping[exists][1]=currentTime
        except:  #if not, add it
            pingDict[traffic[0]]= ptr
            ping.append([traffic[0],currentTime])
            ptr += 1
            #print(ping)           
    return

def buildDict():
    # Lookup dictionary to convert ID to name
    # based on the current data in devices.cfg
    f = open('/home/pi/cowstacker/devices.cfg', 'r')
    config = f.read()  
    f.close()
    parsedStr=config.split('\n')
    deviceDict.clear()
    # First look for Power modules by finding the parsedStr = @PM
    x = 0
    while parsedStr[x] != "@PM":
        x+=1
    x+=1   #X now points to first Power Module
    while parsedStr[x] != "@endPM":
        parsedEntry = parsedStr[x].split('/')
        deviceDict[parsedEntry[1].upper()] = "Power@"+parsedEntry[0].upper()
        x+=1
    # Now the Power Modules are added, look for @TM:
    while parsedStr[x] != "@TM":
        x+=1
    x+=1   #X now points to first Temp Module
    while parsedStr[x] != "@endTM":
        parsedEntry = parsedStr[x].split('/')
        deviceDict[parsedEntry[1].upper()] = "Temp@"+parsedEntry[0].upper()
        x+=1
    # Now the Temp Modules are added, look for @ML.
    while parsedStr[x] != "@ML":
        x+=1
    x+=1   #X now points to first Temp Module
    while parsedStr[x] != "@endML":
        parsedEntry = parsedStr[x].split('/')
        deviceDict[parsedEntry[1].upper()] = "Motion@"+parsedEntry[0].upper()
        x+=1
    # Now the Motion Modules are added, look for @BZ.
    while parsedStr[x] != "@BZ":
        x+=1
    x+=1  #x now points to first Buzzer Module
    while parsedStr[x] != "@endBZ":
        parsedEntry = parsedStr[x].split('/')
        deviceDict[parsedEntry[1].upper()] = "Buzzer@"+parsedEntry[0].upper()
        x+=1
    # Now the Buzzer Modules are added.
    #print("Device Dictionary:", deviceDict)

def reportPings():
    buildDict()
    #print("Length of deviceDict:",len(deviceDict))
    #print("Ping Array:", ping)
    currentTime = datetime.datetime.now()
    x = 0
    returnStr= "\n"
    while x < len(ping):
        interval = currentTime - ping[x][1]
        name = deviceDict[ping[x][0]]
        returnStr += name +":"+ str(interval.seconds) + " Seconds  |"
        print(name, interval.seconds, "seconds")
        x+=1
    returnStr += "\n"
    return returnStr
        
    





    
