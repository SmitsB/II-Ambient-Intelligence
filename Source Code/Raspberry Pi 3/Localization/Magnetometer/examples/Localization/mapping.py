import datetime
import json
import os
import sys
from sys import argv

import numpy
import paho.mqtt.client as mqtt
from pymongo import MongoClient
prompt = '> '

# MOBILE NODES
# Willem --> "node": "b57000009128e"
# Frederik --> "node": "b57000009127b"
# Michiel --> "node": "b5700000913b8"
nodeid = "b57000009128e"

# GATEWAYS
# b5700000912bf
gateway1 = []
# b5700000912fd
gateway2 = []
# b5700000912d9
gateway3 = []
# b570000091ac9
gateway4 = []
# b5700000912d5
gateway5 = []
# b570000091291
gateway6 = []

#Accuracy
maxMapMessages = 10
MaxAccuracy = 6

#Connections
clientid = "Willem-develop"
group_name = "Team-Cool"
collection_name = "V-BlokV3"
MQTT_server = "backend.idlab.uantwerpen.be" #Dont't change this
MQTT_topic = "/localisation/DASH7" #Dont't change this

def on_message(mqttc, obj, msg):
    # MESSAGE TO JSON
    payload = msg.payload
    payload_JSON = json.loads(payload)

    
    if(payload_JSON["node"] == nodeid): #Filter on node
        print payload_JSON
        RSSI_value = payload_JSON["link_budget"]
        gatewayID = str(payload_JSON["gateway"])

        #Filter on gateway
        if gatewayID == 'b5700000912bf':
            gateway1.append(RSSI_value)
        if gatewayID == 'b5700000912fd':
            gateway2.append(RSSI_value)  
        if gatewayID == 'b5700000912d9':
            gateway3.append(RSSI_value)
        if gatewayID == 'b570000091ac9':
            gateway4.append(RSSI_value)          
        if gatewayID == 'b5700000912d5':
            gateway5.append(RSSI_value)
        if gatewayID == 'b570000091291':
            gateway6.append(RSSI_value)

        #Counter for max messages
        global count
        count = count + 1

def mapData(mqttc,room_name,boxid,fingerid):
    #Enter before mapping
    json_data = []

    # Create connection
    mqttc.connect(MQTT_server, 1883, 60)
    mqttc.subscribe(MQTT_topic)

    #Read MQTT messages
    while count < maxMapMessages:
        mqttc.loop()

    #Take the median of each gateway    
    if len(gateway1) > 0:
        a = numpy.array(gateway1)
        RSSI_gateway1 = numpy.median(a)
    if len(gateway2) > 0:
        a = numpy.array(gateway2)
        RSSI_gateway2 = numpy.median(a)
    if len(gateway3) > 0:
        a = numpy.array(gateway3)
        RSSI_gateway3 = numpy.median(a)
    if len(gateway4) > 0:
        a = numpy.array(gateway4)
        RSSI_gateway4 = numpy.median(a)
    if len(gateway5) > 0:
        a = numpy.array(gateway5)
        RSSI_gateway5 = numpy.median(a)
    if len(gateway6) > 0:
        a = numpy.array(gateway6)
        RSSI_gateway6 = numpy.median(a)

    #Create the mapping JSON
    data = {}
    data['room_name'] = room_name
    data['boxid'] = int(boxid)
    data['fingerid'] = fingerid
    data['data_type'] = "raw_mean"
    timestamp = datetime.datetime.now()
    data['timestamp'] = timestamp
    data['nodeid'] = nodeid
    RSSI = []
    if len(gateway1) > 0:
        RSSI.append({"Gateway": "b5700000912bf", "RSSI-Value": int(RSSI_gateway1)})
    else:
        RSSI.append({"Gateway": "b5700000912bf", "RSSI-Value": 0})
    if len(gateway2) > 0:
        RSSI.append({"Gateway": "b5700000912fd", "RSSI-Value": int(RSSI_gateway2)})
    else:
        RSSI.append({"Gateway": "b5700000912fd", "RSSI-Value": 0})
    if len(gateway3) > 0:
        RSSI.append({"Gateway": "b5700000912d9", "RSSI-Value": int(RSSI_gateway3)})
    else:
        RSSI.append({"Gateway": "b5700000912d9", "RSSI-Value": 0})
    if len(gateway4) > 0:
        RSSI.append({"Gateway": "b570000091ac9", "RSSI-Value": int(RSSI_gateway4)})
    else:
        RSSI.append({"Gateway": "b570000091ac9", "RSSI-Value": 0})
    if len(gateway5) > 0:
        RSSI.append({"Gateway": "b5700000912d5", "RSSI-Value": int(RSSI_gateway5)})
    else:
        RSSI.append({"Gateway": "b5700000912d5", "RSSI-Value": 0})
    if len(gateway6) > 0:
        RSSI.append({"Gateway": "b570000091291", "RSSI-Value": int(RSSI_gateway6)})
    else:
        RSSI.append({"Gateway": "b570000091291", "RSSI-Value": 0})
    data['RSSI'] = RSSI
    collection.insert(data)


# SETUP METHODS
mqttc = mqtt.Client(client_id=clientid, protocol=3)
mqttc.on_message = on_message

#Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client[group_name]
collection = db[collection_name]

# CREATE ROOM
print "Give room name:"
room_name = raw_input(prompt)
print "Give box id:"
boxid = raw_input(prompt)
fingerid = 0
count = 0

while True:
    raw_input(prompt)
    for x in range(MaxAccuracy):
        mapData(mqttc, room_name, boxid, fingerid)
        count = 0
    print "Room: " + room_name
    print "Box: " + str(boxid) + "_" + str(fingerid)
    fingerid+=1
