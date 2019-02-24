--[[This contains the code to decode the temp reported by the 
    Dallas 18B20 sensor, and to publish it to the 
    topic "temperature" with the subtopic the chip ID.
    It will also display it on the OLED 128x64 display.
    The reported temp will be Farenheit.
    The duty cycle will be 2 minutes.]]

    --The pins are defined for #5, chip ID 4557553
--Revision 11/10/18 Changed ow pin to #5 
    --for the PC Board design.
--Revision 12/12/18 changed to include ping to broker
--Revision 12/13/18  Added ping results to display
--12/28/18 Modifed display to show pings,
--   and added wifi_status to get temp
    
print(wifi.sta.getip())
ID = node.chipid()
topic = "temperature/"..ID
local module = {}
m = nil
font1=u8g2.font_unifont_t_symbols
font2=u8g2.font_inr30_mn
newTemp="..."

pin =5   
ow.setup(pin)
ow.reset_search(pin)
addr = nil
count = 0
repeat
  count = count + 1
  addr = ow.search(pin)
  tmr.wdclr()
until((addr ~= nil) or (count > 100))
print(count)
print(addr)
print(addr:byte(1,8))
pingFlag = 0

local function send_ping()
    if pingFlag == 0 then
        m:publish("temperature/" ..ID, "PING",0,0)
        disp:clearBuffer()
        disp:setFont(font1)
        disp:drawStr(1,60, "ping")
        disp:sendBuffer()
        pingFlag=1
    else
        print("Broker didn't respond to ping")
        disp:setFont(font1)
        disp:drawStr(1,60, "No ping from broker")
        disp:sendBuffer()
        node.restart()
    end
        
end

function init_display()
    sda = 1  
    scl = 2   
    id = 0
    sla = 0x3C
    i2c.setup(0, sda, scl, i2c.SLOW)
    disp = u8g2.ssd1306_i2c_128x64_noname(id, sla)
    disp:setFont(u8g2.font_inr30_mn)
    disp:clearBuffer()
    disp:drawStr(0,15,"---")
    disp:sendBuffer()
end

function print_OLED(x,y,str)
    disp:clearBuffer()
    disp:setFont(font1)
    disp:drawStr(1,12,str)
    disp:setFont(font2)
    disp:drawStr(35, 45, newTemp)
    disp:sendBuffer()
   

end
init_display()

local function getTemp()
    if wifi.sta.status()~=5 then
        node.restart()    
    end
    disp:clearBuffer()
    ow.reset(pin)
    ow.select(pin, addr)
    ow.write(pin, 0x44, 1)
    tmr.delay(10000)
    present = ow.reset(pin)
          ow.select(pin, addr)
          ow.write(pin,0xBE,1)
          print("P="..present)  
          data = nil
          data = string.char(ow.read(pin))
          for i = 1, 8 do
            data = data .. string.char(ow.read(pin))
          end
         
          print(data:byte(1,9))
          crc = ow.crc8(string.sub(data,1,8))
          print("CRC="..crc)
          if crc == data:byte(9) then
             t = (data:byte(1) + data:byte(2) * 256) * 625
             tf = t*9/50000 +32
             tempstr = tostring(tf)
             print("ready to publish:"..tempstr.." to "..topic)
             m:publish(topic, tempstr,0,0)
             newTemp = tostring(tf)
             print_OLED(35,45,"ping")
             print("Temp "..tostring(tf).."F")
             t1 = t / 10000
             t2 = t % 10000
             print("Temperature="..t1.."."..t2.."Centigrade")
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
        print(topic .. ": " .. data)
        i,j = string.find(topic, "/")
        if i ~= nil then 
            topicA = string.sub(topic, 1,i-1)
            topicB = string.sub(topic, j+1, -1)
            print("parsed: "..topicA .. "|"..topicB)
        end
        if topicA=="temperature" then  --all topics
            print(ID.."/"..topicB)
            if tonumber(topicB)==node.chipid() then
                print("ID Match")
                if string.find(data,"PING")~=nil then
                    print_OLED(1,60,"ping")
                    print("Received Ping")
                    pingFlag=0
                end 
            end
        end
    end
  end)
        -- And then pings each 1000 milliseconds
        tmr.stop(6)
        tmr.alarm(6, 120000, 1, getTemp) --120 seconds
        tmr.stop(5)
        tmr.alarm(5, 5000, 1, send_ping) --5 seconds
        
    end) 

end
if wifi.sta.getip ~= nil then
    print_OLED(10,45,"+++",true)
end

mqtt_start()
