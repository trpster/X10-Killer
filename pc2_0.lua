-- 1/17/19 forked pc_with_ping.lua to add
-- status save

ID=node.chipid()
ledpin=0    --0 for blinking use, 5 to disable
relaypin=2
swpin=1
blinkpin=4  --4 for blinking use, 5 to disable
gpio.mode(swpin,gpio.INPUT)
gpio.mode(blinkpin, gpio.OUTPUT)
gpio.mode(relaypin,gpio.OUTPUT, gpio.PULLUP)
gpio.mode(ledpin,gpio.OUTPUT)
gpio.write(ledpin,gpio.HIGH)   --led off
--gpio.write(relaypin,gpio.HIGH)--relay off
state=0
relay=0
pingFlag = 0

function setSave(currentStatus)
    file.open("status.txt", "w+")
    file.write(currentStatus)
    print("set status to "..currentStatus)
    file.close()
end

function checkSave()
    fd = file.open("status.txt", "r")
    if fd then
        status = fd:read(1)
        print("Saved status "..status)
        fd:close(); fd = nil
        if status == "0" then
            enable = false
            relay=0
            setSave("0")
            gpio.write(ledpin,gpio.HIGH)
            gpio.write(relaypin,gpio.HIGH)--relay off
        else
            enable = true
            relay=1
            setSave("1")
            gpio.write(ledpin,gpio.LOW)
            gpio.write(relaypin,gpio.LOW)--relay on
        end
    end
end



local function send_ping()
    if pingFlag == 0 then
        print("Heap:"..node.heap())
        m:publish("power/" ..ID, "PING",0,0)
        gpio.write(blinkpin, gpio.LOW)
        pingFlag=1
    else
        print("Broker didn't respond to ping")
        node.restart()
    end
        
end

function check_sw()
    sw_now = gpio.read(swpin)
    if sw_now == 0 then
        if state==1 then  --indicates button transition to on
            state=0
            if relay==0 then
                relay=1
                setSave("1")
                gpio.write(relaypin,gpio.LOW)
                gpio.write(ledpin,gpio.LOW)
            else
                relay=0
                setSave("0")
                gpio.write(relaypin,gpio.HIGH)
                gpio.write(ledpin,gpio.HIGH)
            end
        end
    else
        state=1
    end
    --send_ping()
end

m = mqtt.Client(ID)
m:connect("192.168.1.141",1883, 0, 0)
m:on("connect",function(con) print("connected") 
m:subscribe("power/"..ID, 0, function(conn)
m:publish("power/start", "Pwr Module Alive", 0, 0, function(conn)
    print("sent to broker") end)
    end)
    end)

local function mqtt_start()
    tmr.alarm(6, 100, tmr.ALARM_AUTO, check_sw) --0.1 second     
    tmr.alarm(5, 5000, tmr.ALARM_AUTO, send_ping)
    -- register message callback beforehand
    m:on("message", function(conn, topic, data)
      
      if (data ~= nil) then
        print(topic .. ": " .. data)
        i,j = string.find(topic, "/")
        if i ~= nil then 
            topicA = string.sub(topic, 1,i-1)
            topicB = string.sub(topic, j+1, -1)
            print("parsed: "..topicA .. "|"..topicB)
        end
        if topicA=="power" then  --all topics
            print(ID.."/"..topicB)
            if tonumber(topicB)==node.chipid() then
                print("ID Match")
                if string.find(data,"OFF")~=nil then
                    relay=0 
                    setSave("0")
                    gpio.write(relaypin,gpio.HIGH)
                    gpio.write(ledpin,gpio.HIGH)
                elseif string.find(data,"ON")~=nil then
                    relay=1
                    setSave("1")
                    gpio.write(relaypin,gpio.LOW)
                    gpio.write(ledpin,gpio.LOW)
                elseif string.find(data,"LED_DISABLE")~=nil then
                    gpio.write(blinkpin,gpio.HIGH)
                    gpio.write(ledpin,gpio.HIGH)
                    ledpin=5    --0 for blinkinh use
                    blinkpin=5  --4 for blinking use
                elseif string.find(data,"LED_ENABLE")~=nil then
                    ledpin=0    --0 for blinkinh use
                    blinkpin=4 
                    gpio.mode(blinkpin, gpio.OUTPUT)
                    gpio.mode(ledpin,gpio.OUTPUT)--4 for blinking use
                elseif string.find(data,"PING")~=nil then
                    print("Received Ping")
                    gpio.write(blinkpin,gpio.HIGH)
                    pingFlag=0
                end 
            end
        end
    end
  end)
end

checkSave()
mqtt_start()
