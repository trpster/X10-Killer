'''
Created on Aug 31, 2015
Modified for 2.0 November 2018
@author: TP
'''
from Temp_Monitor import getTemp
from mqtt_subscriber_general import deliverIncomingMotion, deliverIncomingPower
from Module_Util import UpdateTimeData, logHandler
from math import fabs
from tkinter import *
import paho.mqtt.publish as publish

MQTT_HOST = "192.168.1.141"
MQTT_PORT = 1883
'''
client = mqtt.Client()
client.connect(MQTT_HOST, MQTT_PORT)
'''
global motionInfo, reload
global macrobox, devicebox, textbox
global t # Used by everyone who needs time info

# A free form macro processor of the form:
# if (condition) then (send MQTT command)
# The 'if' statement can contain any number of conditions and parentheses; for example:
# if (time > 10PM) and (specific motion detector turns on).
# operators can be =,>=,<=,>,<,+,-,and,or,not
# operands can be time, dawn, dusk, motion detector status,
#
# complex conditions can use parens, equations resolved right to left
# Delimiters: space, parens, semicolon (to separate multiple actions)
# Sub-delimiters: "/" to divide operand into Location and Action; 
#     ":" to define hour:minute
    
# macro elements: Flag, macro, time set, delay
#    'Flag' is set when the macro is true and executed;
#    'macro' is the user entered macro;
#    'time set' records the time in minutes that the macro was true and executed;
#    'delay' is user entered, identifies how many minutes the macro should be ignored
#             even if it is true.

# The following are just for initial run; user entered macros will define the macros ultimately used

macro = []; timeSet = 2; delay = 3
macro.append([False, "If 'motion/Back Deck' then Bell/On setDelay=1", 0, 0 ])
#macro.append([False, "If time = 12:05 then G1/Off",0,0])
#macro.append([False, "If A13/Off then G15/Off",0,0])
#macro.append([False, "If Not(A13) And time > 21:30 then H1/Off",0,0])
global PMdata, BZdata, MLdata, MLname

def moduleCommand(command, location, state): #state = ON or OFF
    global PMdata, BZdata
    ID = ""
    topic = ""
    print("moduleCommand:"+ command +" : "+ location + " : " + state)
    if command.upper()=="POWER":
        try:
            ID = PMdata[location.upper()]
            topic = "power/"+ID
        except:
            print("Error; no dictionary entry for location:",location)
    if command.upper()=="BUZZER":
        try:
            ID = BZdata[location.upper()]
            topic = "buzzer/"+ID
        except:
            print("Error; no dictionary entry for location:",location)
    print("Topic:" + topic)
    state = state.upper()
    print("Got to moduleCommand:" + command +"@"+location + "  " + state +" ID:"+ID)
    #client.publish(topic, payload=state, qos=0, retain=False)
    if ID!="":
        publish.single(topic, payload=state, hostname=MQTT_HOST)
    else:
        print("Couldn't send anything since ID is undefined.")

def makeMacroHTML():
    #Create an HTML file containing the macros and devices so the Bottle_Server
    #Can display it on a webpage.
    f = open('macros.html', 'w')
    x = 0
    while x < len(macro):
        f.write(str(macro[x][1]))
        f.write('<BR>')
        x+=1
    f.write('<BR>' + '<BR>')
    f.close()
     
def updateMacroArray(data):
    #print(data)
    parsedStr=data.split('\n')
    while len(macro) > 0:
        del macro[0]
    x = 0
    while x < len(parsedStr):
        element = parsedStr[x]
        #print("Element =", element)
        if len(element)>=2:
            macro.append([False, element, 0, 0])
        x += 1
    makeMacroHTML()

        
def updateDeviceDictionaries(data):
    global PMdata, BZdata, MLdata, MLname
    '''Four dictionaries will be created from the device data,
    and are used to relate ID's to locations.
    Power Modules will be between @PM and @endPM.
    Temp Modules will be between @TM and @endTM.
    Motion Modules will be between @ML and @endML
    Buzzer Modules will be between @BZ and @endBZ.
    Motion detectors are a hodge podge, since some are from
    webcams until all are replaced by actual motion detectors.
    '''
    parsedStr=data.split('\n')
    PMdata = dict()   #rebuild from scratch for any modification
    TMdata = dict()
    BZdata = dict()
    MLdata = dict()
    MLname = dict()
    # First look for Power modules by finding the parsedStr = @PM
    x = 0
    while parsedStr[x] != "@PM":
        x+=1
    x+=1   #X now points to first Power Module
    while parsedStr[x] != "@endPM":
        parsedEntry = parsedStr[x].split('/')
        PMdata[parsedEntry[0].upper()] = parsedEntry[1].upper()
        x+=1
    # Now the Power Module dictionary is built, look for @TM:
    while parsedStr[x] != "@TM":
        x+=1
    x+=1   #X now points to first Temp Module
    while parsedStr[x] != "@endTM":
        parsedEntry = parsedStr[x].split('/')
        TMdata[parsedEntry[0].upper()] = parsedEntry[1].upper()
        x+=1
    # Now the Temp Module dictionary is built, look for @ML.
    while parsedStr[x] != "@ML":
        x+=1
    x+=1   #X now points to first Motion Module
    while parsedStr[x] != "@endML":
        parsedEntry = parsedStr[x].split('/')
        #print("ML parsed:",parsedEntry)
        MLdata[parsedEntry[0].upper()] = parsedEntry[1].upper()
        MLname[parsedEntry[1].upper()] = parsedEntry[0].upper()
        x+=1
    # Now the Motion Module dictionary is built, look for @BZ.
    while parsedStr[x] != "@BZ":
        x+=1
    x+=1  #x now points to first Buzzer Module
    while parsedStr[x] != "@endBZ":
        parsedEntry = parsedStr[x].split('/')
        BZdata[parsedEntry[0].upper()] = parsedEntry[1].upper()
        x+=1
    # Now the Buzzer Module dictionary is built.
    
    print("Power Module Dictionary:", PMdata)
    print("Temp Module Dictionary:", TMdata)
    print("Buzzer Module Dictionary", BZdata)
    print("Motion Module Dictionary:", MLdata)
    print("Motion locations:", MLname)
    makeMacroHTML()
       
def loadMacros():   
    f = open('/home/pi/cowstacker/macros.cfg', 'r')
    config = f.read()
    f.close()
    #print(config)
    updateMacroArray(config)
    
    
def loadDevices():  
    f = open('/home/pi/cowstacker/devices.cfg', 'r')
    config = f.read()  
    f.close()
    updateDeviceDictionaries(config)
    

def saveMacros(event):
    global macrobox
    config = macrobox.get(1.0, END)
    if len(config) != 0:
        f = open('/home/pi/cowstacker/macros.cfg', 'w')
        f.write(config)
        f.close()
        
        
def saveDevices(event):
    global devicebox
    config = devicebox.get(1.0, END)
    #if 1==2:  #temporary...inhibit saving until things are working
    if len(config) != 0:
        updateDeviceDictionaries(config)
        f = open('/home/pi/cowstacker/devices.cfg', 'w')
        f.write(config)
        f.close()
        f= open('/home/pi/cowstacker/reload.txt', 'w')
        f.write("1") #Indicates Temp Monitor needs to update dictionaries
        f.close()


def displayDevices(event):
    global devicebox
    devicebox.delete(1.0, END)
    f = open('/home/pi/cowstacker/devices.cfg', 'r')
    config=f.read()
    f.close()
    devicebox.insert(INSERT, config)

def updateMacros(event):
    global macrobox
    data = macrobox.get(1.0, END)
    if len(data) != 0:
        updateMacroArray(data)
        #macrobox.insert(INSERT, data)
        saveMacros(event)
        #print(macro)

def displayMacros(event):
    print("got to displayMacros")
    global macrobox
    macrobox.delete(1.0, END)
    x = 0
    while x < len(macro):
        if x != len(macro)-1:
            status = macro[x][1]  + '\n'
        else:
            status = macro[x][1]
        macrobox.insert(INSERT, status)
        x += 1
    #print('Finished with displayMacros')
            
loadMacros()
loadDevices()
makeMacroHTML()

def editMacros():
    global macrobox, devicebox, textbox
    editMaster = Tk()
    editMaster.title("                                              Macro Editor    ")
    defaultbg = editMaster.cget('bg')

    y1scrollbar = Scrollbar(editMaster)
    y1scrollbar.grid(row=15, column=99, sticky=N+S)

    macrobox = Text(editMaster, wrap=NONE, bd=2, bg="light yellow", yscrollcommand=y1scrollbar.set)
    macrobox.config(height=32, width=99)
    macrobox.grid(row=3, column=0, columnspan=50, sticky=S+E+W)
    y1scrollbar.config(command=macrobox.yview)

    y2scrollbar = Scrollbar(editMaster)
    y2scrollbar.grid(row=3, column=140, sticky=W+N+S)

    devicebox = Text(editMaster, wrap=NONE, bd=2, yscrollcommand=y2scrollbar.set)
    devicebox.config(height=35, width=40)
    devicebox.grid(row=3, column=101, columnspan=1, rowspan=20, sticky=N)
    y2scrollbar.config(command=devicebox.yview)
    
    b1 = Button(editMaster, text="Display Macros ")
    b1.bind("<Button-1>", lambda event:displayMacros(macrobox))
    b1.grid(row=0, column=0)

    b2 = Button(editMaster, text="Update Macros ")
    b2.bind("<Button-1>", lambda event:updateMacros(macrobox))
    b2.grid(row=1, column=0)

    b3 = Button(editMaster, text="Display Devices")
    b3.bind("<Button-1>", lambda event:displayDevices(devicebox))
    b3.grid(row=0, column=2)

    b4 = Button(editMaster, text="Update Devices")
    b4.bind("<Button-1>", lambda event:saveDevices(devicebox))
    b4.grid(row=1, column=2)

    editMaster.mainloop()
    print('Leaving editMacros')
   
def convertToMinutes(time):
    result = (60 * time.hour) + time.minute
    return result

def whatIsIt(operand):
    # Return times as minutes; 60*hours+minute
    global t, MLname
    result = operand
    #print("Mac-------------operand=", result)
    if type(operand) == str:
        if operand.upper() == 'TIME':
            result = convertToMinutes(t[0])
            #print('Time result = ', result)
        elif operand.upper() == 'DAWN':
            result = convertToMinutes(t[1])
        elif operand.upper() == 'DUSK':
            result = convertToMinutes(t[2])
        elif operand.find(':') != -1:  #which identifies a time format; hh:mm
            colon = operand.find(':')
            hours = int(operand[0:colon])
            minutes = int(operand[colon+1:len(operand)])
            #print('Time operand = '+ str(hours) + ':' + str(minutes))
            result = (60 * hours) + minutes
            #print('Time limit =',result)
        elif operand[0:4].upper() == 'TEMP':
            length = len(operand)
            ID = operand[5:length]
            #print("Temp ID from whatisit:" + ID)
            #print('Detected a temp value request:',ID)
            result = getTemp(ID)
            #print('current temp = ',result)
        elif operand.upper().find('MOTION') != -1:
            #print("whatIsIt:" + operand)
            # This is looking for a motion command
            motion =""
            motion = deliverIncomingMotion(False)  #check for new motion
            result = False
            #print("motion:",motion)
            if motion[0]== "motion":
                print("motion:",motion)
                #print("Got to whatisit motion test")
                #if payload = 'motion,' then motion[1] defines whose motion.
                deviceID = motion[1].upper()
                try:
                    location = MLname[deviceID]
                except:
                    location = "unknown"
                print("Operands:" +operand.upper() +":MOTION@"+location.upper())
                if operand.upper() == "MOTION@"+location.upper():
                    #print("Operand equals motion detector")
                    result = True
                else:
                    #print("Not equal")
                    result = False
        else:
            #print("Operand:", operand)
            result = int(operand)
                
    return result
    

def resolve(A,op,B):
    #ops are:=,>=,<=,>,<,+,-,And,Or,Not
    #Single operand operations use just A, place holder for B...like True
    #print('Resolve A, op, B:', A, op, B, 'Length of op:',len(op))
    #print("Resolve: A:" + A + " op: " + op + " B: " + B)
    aOp = whatIsIt(A)
    bOp = whatIsIt(B)
    #print('after whatIsIt: aOp =',aOp,'  And bOp = ',bOp)
    
    result = False
    if op =='':
        if aOp:result = True
        else: result = False
    if op == "=":
        if aOp == bOp:result = True
    elif op == ">=":
        if aOp >= bOp:result = True
    elif op == "<=":
        if aOp <= bOp:result = True
    elif op == ">":
        if aOp > bOp:result = True
    elif op == "<":
        #print('Got to less than', aOp,bOp)
        if aOp < bOp:result = True
    elif op.upper() == "AND":
        if ((aOp) or not(aOp)) and ((bOp) or not(bOp)):
            if aOp and bOp:result = True
            else: result = False
        else:
            print('Macro-----------something wrong:',aOp,op,bOp)
    elif op.upper() == "OR":
        if ((aOp) or not(aOp)) and ((bOp) or not(bOp)):
            if aOp or bOp:result = True
            else: result = False
        else:
            print('Macro-----------something wrong:',aOp,op,bOp)
    elif op.upper() == "NOT":
        if aOp:result = False
        else:result = True
    elif op == "+":
        result = aOp+bOp
    elif op == "-":
        result = fabs(aOp-bOp)
    #print('Resolve result = ', result)
    return result

def updateCondition(parsed, amount, where):
    # Parens now resolved to a single value, now remove them and the elements.
    x = amount
    #print('    updateCondition parsed, amount, where = ',parsed,amount,where )
    while x > 0:
        #print('Preremoval= ',parsed)
        del parsed[where]
        #print("Postremoval=", parsed)
        x -= 1
    return parsed
        

def resolveParens(parsed):
    #Find first (if any) right paren
    #This just resolves the first set of parens
    x = 0; rightParen = 0; leftParen=0
    #print('length of condition=', len(parsed))
    while x < len(parsed):
        #print('x=',x, ' Condition[x]=',parsed[x])
        if parsed[x] == ")":rightParen = x; break
        x += 1
    #if parsed[x-1] != ")": return  # Here if no right paren found
    #if parsed[x] != ")": return  # Here if no right paren found
    # Got here if a right paren exists, and it's at x
    # Now find the nearest left paren before the right one
    x = rightParen - 1
    while x >= 0:
        if parsed[x] == '(': leftParen = x; break
        x -= 1
    # leftParen and rightParen define innermost parens
    size = rightParen - leftParen - 1
    #print('left Paren = ',leftParen, '  Right Paren = ',rightParen,'Size of parens=',size)
    if size == 1 and parsed[leftParen - 1] == 'Not':
        parenValue = resolve(parsed[leftParen+1],'Not', True)
        # Now parnValue can be put where 'Not' was, and the 
        # parens and the operand can be removed by sliding the elements up
        parsed[leftParen-1]= parenValue
        parsed = updateCondition(parsed, 3, leftParen)
        
    if size == 3:
        parenValue = resolve(parsed[leftParen+1],parsed[leftParen+2],parsed[leftParen+3])
        parsed[leftParen]= parenValue
        parsed = updateCondition(parsed, 4, leftParen+1)
        
def resolveCondition(condition):
    # Condition is now parsed into tuple, condition[0] through condition[n]
    # If there are no parens, start at right (condition[n]) and move to the left
    # if parens, first resolve them and create new condition
    # Condition is alternating operands and operators, starting with an operand
    
    #Condition should now contain either 1 element, or 3 or more.
    #print("Condition = ", condition)
    if len(condition) == 1:  #Here if just a single term, like a motion detection
        answer = resolve(condition[0],"",True)
        #print("Single term:",answer)
        if answer == True:
            condition[0] = True
        else:
            condition[0] = False
    else:
        while len(condition) >= 3:
            x = len(condition)-1
            answer = resolve(condition[x-2], condition[x-1], condition[x])
            condition[x-2] = answer
            del condition[len(condition)-1]
            del condition[len(condition)-1]
    #print("Macro -------------", macro)
    #print('Resolve Condition =',condition[0])
    return condition[0]

def parseThen(macro):
    # From thenPosition+4 to len(macro), commands are 
    # divided by spaces.
    thenPosition = macro.find('then')
    parsed = []
    parseCtr = thenPosition+5; element = ""
    while parseCtr < len(macro):
        if macro[parseCtr] != " ":
            #print("Should add to element here")
            #print("Condition at parseCtr=",condition[parseCtr] )
            element = element + macro[parseCtr]
        else:
            parsed.append(element)
            element = ""
        parseCtr += 1
    if element != ' ':parsed.append(element)
    #print('Parsed then =', parsed)
    return parsed
    
    
        
def parseMacro(macro):
    # First determine if syntax of macro is correct.
    # Macro must start with 'If' and contain 'then'
    # Between 'If' and 'then' is the condition; resulting action follows 'then'
    # The condition must contain at least 1 operand
    # Multiple operands must be separated by operators.
    parsed = []
    macro = macro.upper()
    if macro.find('IF') ==-1 or macro.find('THEN') == -1:
        print('Missing If or then ***********************************************' )
        return parsed
    thenPosition = macro.find('THEN')
    condition = macro[3:thenPosition-1]
    #print("Condition =", condition)
    #print("Length of Condition =", len(condition))
    parseCtr = 0; element = ""
    while parseCtr < len(condition):
        if condition[parseCtr] != " " and condition[parseCtr] != "(" and condition[parseCtr] != ")":
            #print("Should add to element here")
            #print("Condition at parseCtr=",condition[parseCtr] )
            element = element + condition[parseCtr]
                #print("Element now=",element)
        else: 
            #print("Delimiter =",condition[parseCtr])
            if element != ' ' and element != '':
                parsed.append(element)
            if condition[parseCtr] == "(" or condition[parseCtr] == ")":
                parsed.append(condition[parseCtr])
                #print("Element =",element)
            element = ""
        parseCtr += 1
    if element != '':
        parsed.append(element) # Because the end of the condition is an implied delimiter
    return parsed

def executeThen(macro):
    parsed = parseThen(macro[1])
    # Now figure out what to do with the commands
    x = 0
    global t
    result = convertToMinutes(t[0])
    macro[timeSet] = result;macro[0]= True
    while x < len(parsed):
        # Check first for condition identified by "/"
        # Could be power@location/condition (On or OFF) or
        # buzzer@location/condition (requested tone)
        if parsed[x].find('/') != -1:
            slash = parsed[x].find('/')
            at = parsed[x].find('@')
            command = parsed[x][0:at]
            location = parsed[x][at+1:slash]
            state = parsed[x][slash+1:len(parsed[x])]
            print("From executeThen: "+ command +"@"+ location +"/"+ state)
            currentTime = str(t[0].hour) + ":" + str(t[0].minute)
            status = currentTime +"--" + location + '/' + state + '\n'
            logStatus = "Macro----"+location + '/' + state
            logHandler(False, logStatus)
            print("-----------------")
            print(macro)
            print("-----------------")
            moduleCommand(command, location, state)
        elif parsed[x].find('SETDELAY') != -1:
            setDelay = parsed[x].find('setDelay')
            macro[delay] = float(parsed[x][setDelay+10])
            logStatus = "Macro---- set delay "+ str(macro[delay])
            logHandler(False, logStatus)                                                    
            print("Macro----------- set delay=", macro[delay])
            #print('Set Delay=', parsed[x][setDelay+9])
        x += 1
        
def testStatus(macro):
    # Got here if the condition is true;
    # If macro flag is already set, no need to execute "then" again, unless
    # a delay is set and has timed out; if so, reset the flag so 
    # it gets executed again.
    global t
    if macro[delay] != 0:
        result = convertToMinutes(t[0])
        #print('result, macro[timeSet] =',result, '  ',macro[timeSet], " Delay=", macro[delay])
        if fabs((result) - (macro[timeSet])) > macro[delay]:
            #print("-----------------reset macro flag here")
            macro[0] = False
    return macro
            
def macroEval():
    global motionInfo
    global t
    loginfo = ''
    t = UpdateTimeData()
    #
    # Maybe this doesn't belong here, but it belongs somewhere, and since
    # this happens once each main loop, and this module knows how to turn
    # module names into ID's, it seems logical.
    # This should process shit from Alexa via the HA Bridge that's also the
    # Mosquitto broker.
    # To distinguish the transmission between alexa and all others,
    # alexa data must be of the form "alexa-state" or it will be ignored.
    alexaCheck = deliverIncomingPower(True)
    if alexaCheck[0] != "": # something related to power or a buzzer
        if alexaCheck[2].find("alexa") != -1: # then it's from alexa
            dash = alexaCheck[2].find("-")
            state = alexaCheck[2][dash+1:len(alexaCheck[2])-1]
            print("alexaCheck:", alexaCheck)
            print("State: ",state)
            loginfo = "From Alexa:" + alexaCheck[0] +":"+alexaCheck[1]+":"+alexaCheck[2] + "\n"
            moduleCommand(alexaCheck[0], alexaCheck[1], state)
    
    socketInfo = ''
    #motionInfo = deliverMotionInfo()
    #if len(motionInfo) > 1:print("Motion Info = ",motionInfo)   # Go get it from CM11A_Interface
    x = 0; parsed  = []
    #print("Macro =", macro)
    while x < len(macro):
        #print('----------------Next Macro ----------------')
        parsed = parseMacro(macro[x][1])
        #print("Parsed condition =",parsed)
        numberOfElements = len(parsed)
        newNumber = 0
        while numberOfElements > newNumber:
        #Keep calling resolveParens until the size of parsed doesn't change,
        #  which means that all parens have been resolved.
            resolveParens(parsed)
            newNumber = len(parsed)
            if newNumber != numberOfElements:
                numberOfElements = newNumber;newNumber = 0
        #print("    Parsed condition after resolveParens =",parsed)
        finalResult = resolveCondition(parsed)
        #print('Final Result = ',finalResult)
        if finalResult == True:
            #Check to see if it should be executed
            #print('Macro =',macro[x])
            macro[x] = testStatus(macro[x])
            #print('Macro =',macro[x])
            if macro[x][0] == False:
                print('True Macro =', macro[x])
                executeThen(macro[x])
                tstr = str(t[0].hour) + ':' + str(t[0].minute)
                loginfo += '------------Macro ' + tstr + '-' + '\n' + '   ' + macro[x][1] + '\n'
                socketInfo = tstr + "-" + str(macro[x][1])
                macro[x][0] = True
                #print('Macro =',macro[x])
        elif macro[x][delay] == 0:
            macro[x][0] = False   # Reset macro flag if condition is false
               
        x += 1
    deliverIncomingMotion(True)
    #print("Motion String at end of macroEval")
    #resetMotionStuff()
    if socketInfo !='':
        q=1 #dummy command 
        #sendToSocket(socketInfo)
    return loginfo
        

        
