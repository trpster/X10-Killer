# X10-Killer
A Python program to control and monitor ESP8266 power control modules, motion detectors, temperature monitors, and alarm buzzers.
This is version 2 (cowstacker 2.0); version 1 (cowstacker 1.0 circa 2008) was X-10 based, but power line noise has rendered it unreliable.
Version 1.0 used X-10 protocol and X10 modules; version 2.0 uses MQTT to monitor and control ESP8266 modules.

The R-Pi based python program has a tkinter control panel that provides status and a link to the macro editor.  Actions are defined by a simple free-form macro language, e.g., "If time = dusk then power@bedroom/on."  A sample macro.cfg file shows a typical macro file. Device names are associated with unique ESP8266 id's using the device setup function accessed with the macro editor.  

The MQTT broker is separate from the control program.  Each ESP8266 module pings the broker every 5 seconds, and if it doesn't receive a response to its own ping within 5 seconds, executes a reset to recover from power and/or wifi dropouts.  Also for recovery purposes each module stores its status (on/off, enabled/disabled) and reverts to that status upon recovery.

ESP8266 module code is lua, and each module uses three files; 
init.lua is executed at restart and calls wifi.lua.
wifi connects to local wifi and calls the appropriate control program...power control, temperature, buzzer, motion.
Yes, wifi could be included in the init.lua file, but I've found it simpler to keep them separate; delete init.lua and it won't continue trying to restart while you're troubleshooting.

The Alexa interface is accomplished using habridge that can reside anywhere like the MQTT broker.  habridge provides direct MQTT support, obviating the need for a separate python module as was the case with version 1.0.  


FYI; I am neither a python nor lua programmer, but I can write python and lua code, so don't expect production quality code.
