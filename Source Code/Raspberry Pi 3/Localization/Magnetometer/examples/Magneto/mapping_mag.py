import datetime
import json
import os
import sys
from sys import argv

import numpy
import paho.mqtt.client as mqtt
from pymongo import MongoClient
prompt = '> '

# Mangeto ID's

# Values
mag_value = []
pitch = []
roll = []
yaw = []
bar = []

#Max messages for mapping
maxMapMessages = 20

#Connections
clientid = "Willem-develop"
group_name = "Ambient"
collection_name = "mapping_mag"

def mapData(room_name,boxid,fingerid):
    #Enter before mapping
    json_data = []

    #DASH7 data binnekrijgen

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
        RSSI.append({"Gateway": "b5700000912bf", "RSSI-Value": RSSI_gateway1})
    else:
        RSSI.append({"Gateway": "b5700000912bf", "RSSI-Value": 0})
    if len(gateway2) > 0:
        RSSI.append({"Gateway": "b5700000912fd", "RSSI-Value": RSSI_gateway2})
    else:
        RSSI.append({"Gateway": "b5700000912fd", "RSSI-Value": 0})
    if len(gateway3) > 0:
        RSSI.append({"Gateway": "b5700000912d9", "RSSI-Value": RSSI_gateway3})
    else:
        RSSI.append({"Gateway": "b5700000912d9", "RSSI-Value": 0})
    if len(gateway4) > 0:
        RSSI.append({"Gateway": "b570000091ac9", "RSSI-Value": RSSI_gateway4})
    else:
        RSSI.append({"Gateway": "b570000091ac9", "RSSI-Value": 0})
    if len(gateway5) > 0:
        RSSI.append({"Gateway": "b5700000912d5", "RSSI-Value": RSSI_gateway5})
    else:
        RSSI.append({"Gateway": "b5700000912d5", "RSSI-Value": 0})
    if len(gateway6) > 0:
        RSSI.append({"Gateway": "b570000091291", "RSSI-Value": RSSI_gateway6})
    else:
        RSSI.append({"Gateway": "b570000091291", "RSSI-Value": 0})
    data['RSSI'] = RSSI
    collection.insert(data)


# SETUP METHODS
mqttc = mqtt.Client(client_id=clientid, protocol=3)
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
#mqttc.on_log = on_log

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
    for x in range(2):
        mapData(mqttc, room_name, boxid, fingerid)
        print "Room: " + room_name
        print "Box: " + str(boxid) + "_" + str(fingerid)
        fingerid+=1
        count = 0

