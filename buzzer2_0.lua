--Buzzer Module
--Modified 12/12/18 to add broker ping
--Modified 12/19/18 to add heartbeat 
--1/11/18  Added status save

ledpin=0
blinkpin=4
ID=node.chipid()
enable = false

swpin=1
gpio.mode(blinkpin, gpio.OUTPUT)
gpio.mode(swpin,gpio.INPUT)
gpio.mode(ledpin,gpio.OUTPUT)
gpio.write(ledpin,gpio.HIGH) --start disabled
state=0
blink=0
pingFlag = 0

function checkSave()
    fd = file.open("status.txt", "r")
    if fd then
        status = fd:read(1)
        print("Saved status "..status)
        fd:close(); fd = nil
        if status == "0" then
            enable = false
            gpio.write(ledpin,gpio.HIGH)
        else
            enable = true
            gpio.write(ledpin,gpio.LOW)
        end
    end
end

function setSave(currentStatus)
    file.open("status.txt", "w+")
    file.write(currentStatus)
    print("set status to "..currentStatus)
    file.close()
end

speakerPin = 2;  
 gpio.mode(speakerPin,gpio.OUTPUT)  
 --speaker cprint(type(topicB))onnected port  
 --Tone table  
 t={}  
 t["c"]=261  
 t["d"]= 294  
 t["e"]= 329  
 t["f"]= 349  
 t["g"]= 391  
 t["gS"]= 415  
 t["a"]= 440  
 t["aS"]= 455  
 t["b"]= 466  
 t["cH"]= 523  
 t["cSH"]= 554  
 t["dH"]= 587  
 t["dSH"]= 622  
 t["eH"]= 659  
 t["fH"]= 698  
 t["fSH"]= 740  
 t["gH"]= 784  
 t["gSH"]= 830  
 t["aH"]= 880 

function beep(pin, tone, duration)
 print("tone "..tone)  
 freq = t[tone]  
 print ("Frequency:" .. freq)  
 pwm.setup(pin, freq, 512)  
 pwm.start(pin)  
 -- delay in uSeconds  
 tmr.delay(duration * 1000)  
 pwm.stop(pin)  
 --20ms pause  
 tmr.wdclr()  
 tmr.delay(20000)  
 end  

function tempTone()
    if enable==true then
       beep(speakerPin, "c", 200)  
       beep(speakerPin, "cH", 150)  
       beep(speakerPin, "cH", 150)  
       beep(speakerPin, "b", 300)  
       beep(speakerPin, "a", 400)  
       beep(speakerPin, "g", 400)  
       beep(speakerPin, "f", 400)  
       beep(speakerPin, "c", 1500)
    end    
end

function backTone()
    if enable==true then
       beep(speakerPin, "cH", 400)  
       beep(speakerPin, "c", 400)  
       beep(speakerPin, "cH", 400)  
       beep(speakerPin, "c", 400)  
       beep(speakerPin, "cH", 400)  
       beep(speakerPin, "c", 400)  
       beep(speakerPin, "cH", 1000)
    end
end

function helloTone()
    if enable==true then
       beep(speakerPin, "cH", 200)  
       beep(speakerPin, "a", 400)  
    end
end

function check_sw()
    sw_now = gpio.read(swpin)
    
    if sw_now == 0 then
        if state==1 then  --indicates button transition to on
            state=0
            if enable==true then
                enable = false
                setSave("0")
                gpio.write(ledpin,gpio.HIGH)
            else
                enable = true
                setSave("1")
                gpio.write(ledpin,gpio.LOW)
            end
        end
    else
        state=1
    end
end

local function send_ping()
    if pingFlag == 0 then
        m:publish("buzzer/" ..ID, "PING",0,0)
        gpio.write(blinkpin,gpio.LOW)
        pingFlag=1
    else
        print("Broker didn't respond to ping")
        node.restart()
    end
        
end

m = mqtt.Client(ID)
m:connect("192.168.1.141",1883, 0, 0)
m:on("connect",function(con) print("connected")
m:subscribe("buzzer/#", 0, function(conn)
m:publish("buzzer/start", "Buzzer Alive", 0, 0, function(conn)
    print("sent to broker") end)
    end)
    end)

local function mqtt_start()
    tmr.alarm(6, 100, tmr.ALARM_AUTO, check_sw) --.1 second
    tmr.alarm(5, 5000, tmr.ALARM_AUTO, send_ping)     
    -- register message callback beforehand
    m:on("message", function(conn, topic, data)
      if (data ~= nil) then
        --print(topic .. ": " .. data)
        i,j = string.find(topic, "/")
        if i ~= nil then
            --print("Location of /: "..tostring(i).." to "..tostring(j)) 
            topicA = string.sub(topic, 1,i-1)
            topicB = string.sub(topic, j+1, -1)
            --print("parsed: "..topicA .. "|"..topicB.."data="..data)
        end
        if topicA=="buzzer" then  --all topics
            --print(ID.."/"..topicB)
            if tonumber(topicB) == node.chipid() then
                print("ID Match")
                if string.find(data,"BACK")~=nil then
                    backTone()
                elseif string.find(data,"TEMP")~=nil then
                    tempTone()
                elseif string.find(data,"HELLO")~=nil then
                    helloTone()
                elseif string.find(data,"ENABLE")~=nil then
                    gpio.write(ledpin,gpio.LOW)
                    enable = true
                    setSave("1") 
                elseif string.find(data,"DISABLE")~=nil then
                    gpio.write(ledpin,gpio.HIGH)
                    enable = false
                    setSave("0")
                elseif string.find(data,"PING")~=nil then
                    print("Received Ping")
                    gpio.write(blinkpin, gpio.HIGH)
                    pingFlag=0
                else
                    print("Matched with nothing")
                end 
            end
        end
    end
  end)
end

checkSave()
mqtt_start()
