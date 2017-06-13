from sys import argv
import paho.mqtt.client as mqtt
import json
prompt = '> '


run = True
ROOM315_1 = False
ROOM315_2 = False
gang_1 = False
gang_2 = False
lift_1 = False
lift_2 = False

def on_connect(mqttc, obj, flags, rc):
    print("rc: "+str(rc))

def on_message(mqttc, obj, msg):
    global ROOM315_1
    global ROOM315_2
    global gang_1
    global gang_2
    global lift_1
    global lift_2
    global run

    #MESSAGE TO JSON
    payload = msg.payload
    payload_JSON = json.loads(payload)
    if(payload_JSON["node"]==nodeid):
        treshold = 15
        if(payload_JSON["gateway"] == "b570000091ac9"):
            if(payload_JSON["link_budget"] > 36 - treshold and payload_JSON["link_budget"] < 36 + treshold):
                ROOM315_1 = True
            if (payload_JSON["link_budget"] > 79 - treshold and payload_JSON["link_budget"] < 79 + treshold):
                gang_1 = True
            if (payload_JSON["link_budget"] > 97 - treshold and payload_JSON["link_budget"] < 97 + treshold):
                lift_1 = True

        if (payload_JSON["gateway"] == "b5700000912fd"):
            if (payload_JSON["link_budget"] > 75 - treshold and payload_JSON["link_budget"] < 75 + treshold):
                ROOM315_2 = True
            if (payload_JSON["link_budget"] > 75 - treshold and payload_JSON["link_budget"] < 75 + treshold):
                gang_2 = True
            if (payload_JSON["link_budget"] > 69 - treshold and payload_JSON["link_budget"] < 69 + treshold):
                lift_2 = True


        if(ROOM315_1==True and ROOM315_2==True):
            print "Welcome in ROOM315"
            ROOM315_1 = False
            ROOM315_2 = False
        if(gang_1==True and gang_2==True):
            print "Welcome in GANG"
            gang_1 = False
            gang_2 = False
        if(lift_1==True and lift_2==True):
            print "Welcome in LIFT"
            lift_1 = False
            lift_2 = False

def on_publish(mqttc, obj, mid):
    print("mid: "+str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_log(mqttc, obj, level, string):
    print(string)

#CLIENT INFO
clientid = "Willem-develop"
clientprotocol = 3 #MQTTv3.1
mqttc = mqtt.Client(client_id=clientid, protocol=clientprotocol)
nodeid = "b57000009128e"

#SETUP METHODS
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
#mqttc.on_log = on_log

#MQTT SERVER INFO
MQTT_server = "backend.idlab.uantwerpen.be"
MQTT_topic = "/localisation/DASH7"

print("Client: " + clientid)
print("Server: " + MQTT_server)
print("Topic: " + MQTT_topic)
print

#Create connection
print("Create connection....")
mqttc.connect(MQTT_server, 1883, 60)
mqttc.subscribe(MQTT_topic)
print("Connection created....\n")

while run:
    mqttc.loop()