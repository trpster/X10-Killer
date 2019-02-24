--[[This uses the HC-SR501 motion detector
     beginning 12/18/18
     turn on onboard LED when motion detected]]
     
ledpin=0
blinkpin=4
sensorpin=1
gpio.mode(sensorpin,gpio.INPUT)
gpio.mode(ledpin,gpio.OUTPUT)
gpio.mode(blinkpin,gpio.OUTPUT)
gpio.write(blinkpin,gpio.HIGH)
gpio.write(ledpin,gpio.HIGH) --start disabled
state=0
pingFlag = 0
    
print(wifi.sta.getip())
ID = node.chipid()
topic = "motion/"..ID
local module = {}
m = nil


local function send_ping()
    if pingFlag == 0 then
        --print("heap:"..node.heap())
        m:publish(topic, "PING",0,0)
        gpio.write(blinkpin,gpio.LOW)
        state=0
        pingFlag=1
    else
        print("Broker didn't respond to ping")
        node.restart()
    end
        
end

local function checkMotion()
    if gpio.read(sensorpin)==1 and state==0 then  --1 = motion
        gpio.write(ledpin,gpio.LOW)
        m:publish(topic, "motion",0,0)
        state=1
        print("Sensor detects motion")
    else
        gpio.write(ledpin,gpio.HIGH)
        --print("No motion")
    end
end

-- Sends my id to the broker for registration
local function register_myself()
    m:subscribe(topic,0,function(conn)
        print("Successfully subscribed to data endpoint")
    end)
end

local function mqtt_start()
    m = mqtt.Client(ID, 180)
    -- Connect to broker
    m:connect("192.168.1.141", 1883, 0, 0, function(con) 
        register_myself()
        m:on("message", function(conn, topic, data)
      
      if (data ~= nil) then
        --print(topic .. ": " .. data)
        i,j = string.find(topic, "/")
        if i ~= nil then 
            topicA = string.sub(topic, 1,i-1)
            topicB = string.sub(topic, j+1, -1)
            --print("parsed: "..topicA .. "|"..topicB)
        end
        if topicA=="motion" then  --all topics
            --print(ID.."/"..topicB)
            if tonumber(topicB)==node.chipid() then
                --print("ID Match")
                if string.find(data,"PING")~=nil then
                    gpio.write(blinkpin, gpio.HIGH)
                    --print("Received Ping")
                    pingFlag=0
                end 
            end
        end
    end
  end)
        -- And then pings each 1000 milliseconds
        tmr.stop(6)
        tmr.alarm(6, 100, 1, checkMotion) --0.1 seconds
        tmr.stop(5)
        tmr.alarm(5, 5000, 1, send_ping) --5 seconds
        
    end) 

end

mqtt_start()
