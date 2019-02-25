
import paho.mqtt.client as mqtt
import datetime
 
MQTT_SERVER = "192.168.1.141"  # The HA Bridge R-pi that also has MQTT broker
MQTT_PATH = "#"      # Or whatever topic you want, "#" = wildcard
global incomingTemp, incomingMotion, tempSubpath, tempTopic, motionTopic, motionSubpath
global incomingPower, powerSubpath, powerTopic, incomingSubpath, incomingData
incomingTemp = ""
incomingMotion = ""
motionTopic=""
motionSubpath=""
tempTopic=""
tempSubpath=""
incomingPower = ""
powerSubpath = ""
powerTopic = ""
incomingSubpath = ""
incomingData = ""

    
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_PATH)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global incomingTemp, incomingMotion, tempSubpath, tempTopic, motionSubpath, motionTopic
    global incomingPower, powerSubpath, powerTopic, incomingSubpath, incomingData
    #print("Got to on_message")
    path = msg.topic
    #print("Path:", path)
    index = path.find("/")
    topic = path[0:index]
    #print("Topic:"+topic)
    subpath = path[(index+1):len(path)]
    incomingSubpath = subpath
    incomingData = str(msg.payload)
    #print(msg.topic+" "+str(msg.payload))
    if topic == "temperature":
        if str(msg.payload) != "b'PING'":
            incomingTemp = str(msg.payload)
            tempSubpath = subpath
            tempTopic = topic
    if topic == "motion":
        if str(msg.payload) != "b'PING'":
            incomingMotion = "motion"
            motionSubpath = subpath
            motionTopic = topic
            #print("Got through motion if: ", incomingMotion)
    if (topic == "power") or (topic == "buzzer"):
        if str(msg.payload) != "b'PING'":
            incomingPower = str(msg.payload)
            powerSubpath = subpath
            powerTopic = topic
    #print("incoming from on_message:",str(msg.payload))
    # more callbacks, etc

def deliverAll():
    global incomingSubpath, incomingData
    path = incomingSubpath
    data = incomingData
    incomingSubpath = ""
    incomingData = ""
    return path, data

def deliverIncomingTemp(clear):
    client.on_message = on_message
    global incomingTemp, tempSubpath, topic, tempTopic
    sendData = incomingTemp
    sendTopic = tempTopic
    sendSubpath = tempSubpath
    if (tempTopic != "temperature") or (sendData=="b'PING'"):
        sendData = ""
        sendTopic = ""
        sendSubpath = ""
    if clear:
        incomingTemp = ""
        tempSubpath = ""
        tempTopic = ""
    
    return sendTopic, sendSubpath, sendData

def deliverIncomingMotion(clear):
    client.on_message = on_message
    global incomingMotion, motionSubpath, motionTopic
    sendData = incomingMotion
    sendTopic = motionTopic
    sendSubpath = motionSubpath
    if motionTopic != "motion":
        sendData = ""
        sendTopic = ""
        sendSubpath = ""
    if clear:
        incomingMotion = ""
        motionSubpath = ""
        motionTopic = ""
    return sendTopic, sendSubpath, sendData

def deliverIncomingPower(clear):
    client.on_message = on_message
    global incomingPower, powerSubpath, powerTopic
    #print("Incoming power:" + incomingPower+" : "+powerSubpath+ " : "+ powerTopic)
    sendData = incomingPower
    sendTopic = powerTopic
    sendSubpath = powerSubpath
    if (powerTopic != "power") and (powerTopic != "buzzer"):
        sendData = ""
        sendTopic = ""
        sendSubpath = ""
    if clear:
        incomingPower = ""
        powerSubpath = ""
        powerTopic = ""
    return sendTopic, sendSubpath, sendData

client = mqtt.Client()
client.on_connect = on_connect


client.connect(MQTT_SERVER, 1883, 60)
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_start()
