import json
import math
import operator
from sys import argv

import paho.mqtt.client as mqtt
from pymongo import MongoClient

prompt = '> '

# MOBILE NODES
# Willem --> "node": "b57000009128e"
# Frederik --> "node": "b57000009127b"
# Michiel --> "node": "b5700000913b8"

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

# MQTT on_connect
def on_connect(mqttc1, obj, flags, rc):
    print("rc: " + str(rc))

# MQTT on_message
def on_message(mqttc1, obj, msg):
   
    # MESSAGE TO JSON
    payload = msg.payload
    payload_JSON = json.loads(payload)

    # Filter on node
    if (payload_JSON["node"] == nodeid):
        RSSI_value = payload_JSON["link_budget"]
        gatewayID = str(payload_JSON["gateway"])
        
        # Filter on gateway
        if gatewayID == 'b5700000912bf':
           
            # Check if gateway data was already received
            if (len(gateway1) > 0):
                fingerprinting()
                del gateway1[:]
                del gateway2[:]
                del gateway3[:]
                del gateway4[:]
                del gateway5[:]
                del gateway6[:]
                gateway1.append(RSSI_value)
            else:
                gateway1.append(RSSI_value)
        if gatewayID == 'b5700000912fd':
            if (len(gateway2) > 0):
                fingerprinting()
                del gateway1[:]
                del gateway2[:]
                del gateway3[:]
                del gateway4[:]
                del gateway5[:]
                del gateway6[:]
                gateway2.append(RSSI_value)
            else:
                gateway2.append(RSSI_value)
        if gatewayID == 'b5700000912d9':
            if (len(gateway3) > 0):
                fingerprinting()
                del gateway1[:]
                del gateway2[:]
                del gateway3[:]
                del gateway4[:]
                del gateway5[:]
                del gateway6[:]
                gateway3.append(RSSI_value)
            else:
                gateway3.append(RSSI_value)
        if gatewayID == 'b570000091ac9':
            if (len(gateway4) > 0):
                fingerprinting()
                del gateway1[:]
                del gateway2[:]
                del gateway3[:]
                del gateway4[:]
                del gateway5[:]
                del gateway6[:]
                gateway4.append(RSSI_value)
            else:
                gateway4.append(RSSI_value)
        if gatewayID == 'b5700000912d5':
            if (len(gateway5) > 0):
                fingerprinting()
                del gateway1[:]
                del gateway2[:]
                del gateway3[:]
                del gateway4[:]
                del gateway5[:]
                del gateway6[:]
                gateway5.append(RSSI_value)
            else:
                gateway5.append(RSSI_value)
        if gatewayID == 'b570000091291':
            if (len(gateway6) > 0):
                fingerprinting()
                del gateway1[:]
                del gateway2[:]
                del gateway3[:]
                del gateway4[:]
                del gateway5[:]
                del gateway6[:]
                gateway6.append(RSSI_value)
            else:
                gateway6.append(RSSI_value)

# MQTT on_publish
def on_publish(mqttc1, obj, mid):
    print("mid: " + str(mid))

# MQTT on_subscribe
def on_subscribe(mqttc1, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# MQTT on_log
def on_log(mqttc1, obj, level, string):
    print(string)

# kNN algorithm - euclidian
def euclideanDistance(instance1, instance2, length):
    distance = 0
    for x in range(length):
        distance += pow((instance1[x] - instance2[x]), 2)
    return math.sqrt(distance)

# kNN algorithm - get neighbors of mobile node
def getNeighbors(trainingSet, testInstance, k):
    distances = []
    length = len(testInstance)-1
    for x in range(len(trainingSet)):
        dist = euclideanDistance(testInstance, trainingSet[x], length)
        distances.append((trainingSet[x], dist))
    distances.sort(key=operator.itemgetter(1))
    neighbors = []
    for x in range(k):
        neighbors.append(distances[x][0])
    return neighbors

# kNN algorithm - fingerprinting
def fingerprinting():

    # Get TrainingData
    d = []
    cursor = collection.find({})
    for document in cursor:
        d.append(document)
    trainSet = []
    for fi in d:
        finger = []
        room_name = fi["room_name"]
        room_id = fi["room_id"]
        RSSI_array = fi["RSSI"]
        for RSSI in RSSI_array:
            finger.append(RSSI["RSSI-Value"])
        finger.append(room_name)
        finger.append(room_id)
        trainSet.append(finger)

    # Get TestData
    testInstance = []
    if len(gateway1) > 0:
        testInstance.append(int(gateway1[0]))
    else:
        testInstance.append(0)
    if len(gateway2) > 0:
        testInstance.append(int(gateway2[0]))
    else:
        testInstance.append(0)
    if len(gateway3) > 0:
        testInstance.append(int(gateway3[0]))
    else:
        testInstance.append(0)
    if len(gateway4) > 0:
        testInstance.append(int(gateway4[0]))
    else:
        testInstance.append(0)
    if len(gateway5) > 0:
        testInstance.append(int(gateway5[0]))
    else:
        testInstance.append(0)
    if len(gateway6) > 0:
        testInstance.append(int(gateway6[0]))
    else:
        testInstance.append(0)
    k = 3
    neighbors = getNeighbors(trainSet, testInstance, k)
    print "You are in"
    print "Room: " + str(neighbors[0][6])
    print
    mqttc2.publish(MQTT_topic_RPi,str(neighbors[0][6]))

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['Ambient']
collection = db['V-blok']

# MQTT - SERVER INFO
clientid = "Willem-develop"
clientprotocol = 3  # MQTTv3.1
mqttc1 = mqtt.Client(client_id=clientid, protocol=clientprotocol)
mqttc2 = mqtt.Client(client_id=clientid, protocol=clientprotocol)
nodeid = "b57000009128e"

# MQTT - SETUP METHODS
mqttc1.on_message = on_message
mqttc1.on_connect = on_connect
mqttc1.on_publish = on_publish
mqttc1.on_subscribe = on_subscribe

# MQTT - SERVER INFO
MQTT_server = "backend.idlab.uantwerpen.be"
MQTT_topic = "/localisation/DASH7"
print("Client: " + clientid)
print("Server: " + MQTT_server)
print("Topic: " + MQTT_topic)
print

# MQTT - RPI INFO
MQTT_RPi = "localhost"
MQTT_topic_RPi = "/rpi/localization"
print("Client: " + clientid)
print("Server: " + MQTT_RPi)
print("Topic: " + MQTT_topic_RPi)
print

# MQTT - Create connection with server and subscribe/RPI publisch connect
print("Create connections....")
mqttc1.connect(MQTT_server, 1883, 60)
mqttc1.subscribe(MQTT_topic)
mqttc2.connect(MQTT_RPi, 1883, 60)
print("Connection created....\n")

# Program loop
while True:
    mqttc1.loop()
