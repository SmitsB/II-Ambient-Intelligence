from sys import argv
import json
import math
import operator
import paho.mqtt.client as mqtt
from pymongo import MongoClient

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

def on_message(mqttc, obj, msg):
    # Default incoming message
    #print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))

    # MESSAGE TO JSON
    payload = msg.payload
    payload_JSON = json.loads(payload)

    if(payload_JSON["node"] == nodeid):
        #print payload_JSON
        RSSI_value = payload_JSON["link_budget"]
        gatewayID = str(payload_JSON["gateway"])

        if gatewayID == 'b5700000912bf':
            gateway1.append(RSSI_value)
        else:
            gateway1.append(0)
        if gatewayID == 'b5700000912fd':
            gateway2.append(RSSI_value)
        else:
            gateway2.append(0)    
        if gatewayID == 'b5700000912d9':
            gateway3.append(RSSI_value)
        else:
            gateway3.append(0) 
        if gatewayID == 'b570000091ac9':
            gateway4.append(RSSI_value)
        else:
            gateway4.append(0)           
        if gatewayID == 'b5700000912d5':
            gateway5.append(RSSI_value)
        else:
            gateway5.append(0) 
        if gatewayID == 'b570000091291':
            gateway6.append(RSSI_value)
        else:
            gateway6.append(0) 

        global count
        count = count + 1

def euclideanDistance(instance1, instance2, length):
	distance = 0
	for x in range(length):
		distance += pow((instance1[x] - instance2[x]), 2)
	return math.sqrt(distance)

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

# CLIENT INFO
clientid = "Willem-develop"
clientprotocol = 3  # MQTTv3.1
mqttc = mqtt.Client(client_id=clientid, protocol=clientprotocol)
nodeid = "b57000009128e"

# SETUP METHODS
mqttc.on_message = on_message
#mqttc.on_log = on_log


#Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['Ambient']
collection = db['V-blok']

# MQTT SERVER INFO
MQTT_server = "backend.idlab.uantwerpen.be"
MQTT_topic = "/localisation/DASH7"

print("Client: " + clientid)
print("Server: " + MQTT_server)
print("Topic: " + MQTT_topic)
print

# Create connection
print("Create connection....")
mqttc.connect(MQTT_server, 1883, 60)
mqttc.subscribe(MQTT_topic)
print("Connection created....\n")

while True:
    #Get TrainingData
    d = []
    cursor = collection.find({})
    for document in cursor:
        d.append(document)

    #Create Trainset
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

    #Get node RSSI
    nodeRSSI = []



    count = 0
    while count < 8:
        mqttc.loop()

    nodeRSSI.append(round(sum(gateway1) / float(len(gateway1))))
    nodeRSSI.append(round(sum(gateway2) / float(len(gateway2))))
    nodeRSSI.append(round(sum(gateway3) / float(len(gateway3))))
    nodeRSSI.append(round(sum(gateway4) / float(len(gateway4))))
    nodeRSSI.append(round(sum(gateway5) / float(len(gateway5))))
    nodeRSSI.append(round(sum(gateway6) / float(len(gateway6))))

    #Print Location
    k = 3
    neighbors = getNeighbors(trainSet, nodeRSSI, 3)
    print "You are in"
    print "Room: " + neighbors[0][6]