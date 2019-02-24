from tkinter import *
from Temp_Monitor import tempMainLoop, updateDict
from Module_Util import logHandler, UpdateTimeData, FormatTime
from Web_Command_Processing import checkWebCommand
from Macro_Processing import macroEval, editMacros, moduleCommand
from Ping_Eval import getData, reportPings

global PulseCounter
PulseCounter = 0

global failureNotification
failureNotification = False

global buttonPressed
buttonPressed = False

master = Tk()
master.title("                          Trpster's Cowstacker 2.0")
defaultbg = master.cget('bg')
    
yscrollbar = Scrollbar(master)
yscrollbar.grid(row=4, column=55, sticky=W+N+S)

textbox = Text(master, wrap=NONE, bd=0, yscrollcommand=yscrollbar.set)
textbox.config(height=30, width=100)
textbox.grid(row=4, column=0, columnspan=54, sticky=E)
yscrollbar.config(command=textbox.yview)
    

def Button3PressCommand(event):
    pingData = reportPings()
    parsedPings = pingData.split("|")
    x= 0
    perline = 0
    outStr = "\n"
    while x <len(parsedPings):
        outStr += parsedPings[x]
        perline +=1
        if (perline ==3) or (x==len(parsedPings)-1):
            textbox.insert("end", outStr)
            textbox.see("end")
            outStr = "\n"
            perline = 0
        x += 1
        
    
    

def sendCmd(event):
    config = entrybox.get(1.0, END)
    if len(config) != 0:
        print("Sending Command:"+config)
        at=config.find("@")
        slash=config.find("/")
        command = config[0:at]
        location = config[at+1:slash]
        state = config[slash+1:len(config)]
        print(command+"@"+location+"/"+state)
        moduleCommand(command, location, state)
                                        

b1 = Button(master, text="Edit Macros", command=editMacros)
b1.grid(row=0, column=0)

b2 = Button(master, text="Send Cmd")
b2.bind("<Button-1>", sendCmd)
b2.grid(row=0, column=6)

b3 = Button(master, text="Ping Times")
b3.bind("<Button-1>", Button3PressCommand)
b3.grid(row=0, column=3)

entrybox = Text(master)
entrybox.config(height=2, width=40, bg=defaultbg)               
entrybox.grid(row=0, column=14)

global DailyReset
DailyReset = False

timebox = Text(master)
timebox.config(height=4, width=20, bg=defaultbg)               
timebox.grid(row=0, column=60, rowspan=4)

def SetTm():
    first = 'Time: ' + FormatTime(0,0,0,0)
    second = 'Dawn: ' + FormatTime(1,0,0,0)
    third = 'Dusk: ' + FormatTime(2,0,0,0)
    return first, second, third;

def displayActivity(action):
    timeTag = FormatTime(0,0,0,0)
    textbox.insert(INSERT, timeTag +": "+ action + '\n')
    
def DisplayMacros():
    # Display macro[x][1] which is the macro; omit the other junk
    x = 0
    textbox.insert(INSERT, '-------------------------------' + '\n')
    textbox.insert(INSERT, 'Macros:' + '\n')
    while x < len(macro):
        text = str(macro[x][1]) + '\n'
        textbox.insert(INSERT, text)
        x += 1
 
def DisplayDevices():
    x = 0
    textbox.insert(INSERT, '-------------------------------' + '\n')
    textbox.insert(INSERT, 'Devices:' + '\n')
    while x < len(devices):
        text = str(devices[x][0]) + '\n'
        textbox.insert(INSERT, text)
        x += 1
        
def CheckDailyReset():
    # Clear textbox every day at 11AM
    global DailyReset
    currentHour = UpdateTimeData()[0].hour
    if DailyReset == False and currentHour == 0:
        print('Execute text box reset...')
        textbox.delete(1.0, END)
        logHandler(True, "Daily Reset")
        DailyReset = True
        
    if DailyReset == True and currentHour != 0:
        DailyReset = False

logHandler(True, "Nothing")
updateDict()   #Build dictionaries for Temp_Monitor

def MainLoop():
    #print('Beginning of Loop*************')
    global status
    global PulseCounter
    global buttonPressed
    global ser
    getData()
    CheckDailyReset()
    #print('Finished checking daily reset.....')
    #checkWebCommand()
    timestuff = SetTm()[0] + '\n' + SetTm()[1] + '\n' + SetTm()[2] + '\n' + 'Pulse: ' + str(PulseCounter)
    #timestuff = 'Testing...'
    timebox.delete(1.0, END)
    timebox.insert(INSERT, timestuff)
    #print('Loaded time info.........')
    
    status = ""                        #For testing new motion detector
    if len(status) > 0:
        PulseCounter = 0
        status += ' at ' + FormatTime(0,0,0,0) + '\n'
        textbox.insert(INSERT, status)
        status = ''

    #print('Ready to check macros........')
    status = macroEval()
    if status != '':
        #textbox.insert(INSERT, status)
        textbox.insert("end", status)
        textbox.see("end")
    
    status = tempMainLoop()
    status = ""   # No need to display this here, temp has its own display
    if len(status) > 0:
        activity = FormatTime(0,0,0,0) +": " + status + '\n'
        #textbox.insert(INSERT, activity)
        textbox.insert("end", activity)
        textbox.see("end")
        status = ''
    
    if buttonPressed == True:
        editStatus = editTriggers(master)
        if editStatus == True:
            buttonPressed = False 
                         
    master.after(1000, MainLoop)


master.after(1000, MainLoop)

mainloop()
