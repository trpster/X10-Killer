--1/12/19 minimal therm for ESP8266

cfg={}
cfg.ssid="XXXXXXX"
cfg.pwd="XXXXXXXXXX"
cfg.save=true
wifi.nullmodesleep(false)
if wifi.sta.getip()==nil then
    wifi.setmode(wifi.STATION, true)
    wifi.sta.config(cfg)   
end
x=0
function checkwifi()
    x=x+1
    print("Status:" .. wifi.sta.status())
    if wifi.sta.status() == 5 then
        print("Wifi Connected")
        tmr.unregister(6)
        dofile("pc2_0.lua")
    else 
        if wifi.sta.status()~=5 then
        print("Waiting to connect")    
        end
        if x<10 then
            tmr.start(6)
        else
            print("Abort")
            node.restart()
        end
    end
end 
    
tmr.alarm(6, 1000, tmr.ALARM_SEMI, checkwifi) --1 second
