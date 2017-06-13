import json
import math
import operator
import time
from shutil import copyfile

import numpy
import paho.mqtt.client as mqtt
from pymongo import MongoClient

from sshtunnel import SSHTunnelForwarder

import argparse

from d7a.alp.command import Command
from d7a.alp.interface import InterfaceType
from d7a.d7anp.addressee import Addressee, IdType
from d7a.sp.configuration import Configuration
from d7a.sp.qos import QoS, ResponseMode
from d7a.system_files.uid import UidFile
from modem.modem import Modem

prompt = '> '

# Variables
mag_valueX = []
mag_valueY = []
mag_valueZ = []
pitchs = []
rolls = []
yaws = []
bars = []

# Static variables
maxMapMessages = 1
k = 5

# Connections
clientid = "Fredsons"
MONGO_HOST = "143.129.37.80"
MONGO_DB = "Team-MetVier"
MONGO_USER = "pi"
MONGO_PASS = "raspberry"
MONGO_COLLECTION_NAME = "V-Blok_mag_0"
MQTT_RPi = "localhost"
MQTT_topic_RPi = "/rpi/localization_mag"


def received_command_callback(cmd):
    dataLocal = cmd.actions[0].operand.data
    dataHeader = int(format(dataLocal[0], '#010b'), 0)
    # print dataHeader
    # Only process data if first byte equals '42' (= data header for mobile
    # node). This prevents conflicts with the NFC node.
    if (dataHeader == 42):
        # print dataLocal
        mag_valueX.append(
            int(format(dataLocal[1], '#010b') + format(dataLocal[2], '08b'), 2))
        mag_valueY.append(
            int(format(dataLocal[3], '#010b') + format(dataLocal[4], '08b'), 2))
        mag_valueZ.append(
            int(format(dataLocal[5], '#010b') + format(dataLocal[6], '08b'), 2))
        pitchs.append(
            int(format(dataLocal[7], '#010b') + format(dataLocal[8], '08b'), 2))
        rolls.append(
            int(format(dataLocal[9], '#010b') + format(dataLocal[10], '08b'), 2))
        yaws.append(
            int(format(dataLocal[11], '#010b') + format(dataLocal[12], '08b'), 2))
        bars.append(
            int(format(dataLocal[13], '#010b') + format(dataLocal[14], '08b'), 2))

        # Counter for max messages
        global count
        count = count + 1

        if (count >= maxMapMessages):
            fingerprinting()
            count = 0
            clearVariables()


# Clear gateway data
def clearVariables():
    del mag_valueX[:]
    del mag_valueY[:]
    del mag_valueZ[:]
    del pitchs[:]
    del rolls[:]
    del yaws[:]
    del bars[:]


# kNN algorithm - euclidian
def euclideanDistance(instance1, instance2, length):
    distance = 0
    for x in range(length):
        distance += pow((instance1[x] - instance2[x]), 2)
    return math.sqrt(distance)


# kNN algorithm - manhatten
def manhattenDistance(instance1, instance2, length):
    distance = 0
    for x in range(length):
        distance += abs(instance1[x] - instance2[x])
    return distance


# kNN algorithm - get neighbors of mobile node
def getNeighbors(trainingSet, testInstance, k):
    distances = []
    length = len(testInstance) - 1
    for x in range(len(trainingSet)):
        dist = euclideanDistance(testInstance, trainingSet[x], length)
        distances.append((trainingSet[x], dist))
    distances.sort(key=operator.itemgetter(1))
    neighbors = []
    for x in range(k):
        print "Neighbour" + str(x) + ": " + distances[x][0][-1]
        neighbors.append(distances[x][0])
    return neighbors


# kNN algorithm - fingerprinting
previous_room = ""


def getResponse(neighbors):
    votes = {}
    for x in range(len(neighbors)):
        response = neighbors[x][-1].encode('ascii', 'ignore')
        if response in votes:
            votes[response][0] += 1
            votes[response][1].append(neighbors[x])
        else:
            votes[response] = [1, []]
            votes[response][1].append(neighbors[x])

    sortedVotes = sorted(votes.iteritems(), key=operator.itemgetter(1), reverse=True)
    return sortedVotes[0][0]


def fingerprinting():
    # Get TestData
    testInstance = []
    if len(mag_valueX) > 0:
        a = numpy.array(mag_valueX)
        testInstance.append(int(numpy.median(a)))
    else:
        testInstance.append(0)
    if len(mag_valueY) > 0:
        a = numpy.array(mag_valueY)
        testInstance.append(int(numpy.median(a)))
    else:
        testInstance.append(0)
    if len(mag_valueZ) > 0:
        a = numpy.array(mag_valueZ)
        testInstance.append(int(numpy.median(a)))
    else:
        testInstance.append(0)
    # if len(pitchs) > 0:
    #     a = numpy.array(pitchs)
    #     testInstance.append(int(numpy.median(a)))
    # else:
    #     testInstance.append(0)
    # if len(rolls) > 0:
    #     a = numpy.array(rolls)
    #     testInstance.append(int(numpy.median(a)))
    # else:
    #     testInstance.append(0)
    # if len(yaws) > 0:
    #     a = numpy.array(yaws)
    #     testInstance.append(int(numpy.median(a)))
    # else:
    #     testInstance.append(0)
    # if len(bars) > 0:
    #     a = numpy.array(bars)
    #     testInstance.append(int(numpy.median(a)))
    # else:
    #     testInstance.append(0)

    print "Testinstance: " + str(testInstance)
    neighbors = getNeighbors(trainSet, testInstance, k)
    current_room = getResponse(neighbors)

    global previous_room

    if (previous_room != current_room):
        print "Room: " + current_room
        print

        copyfile('/home/pi/Localization/Magnetometer/magneto_loc/samplepics/' + current_room + '.png', '/etc/openhab2/html/localization/current_mag.png')
        # bashCommand="sudo convert /etc/openhab2/html/localization/current.png -pointsize 18 -fill #00CCFF -annotate +600+50 " +  'Current Room: ' +current_room+ " /etc/openhab2/html/localization/current.png"
        # process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        # output, error = process.communicate()
        # previous_room = current_room

        # json_loc = {"node_id": nodeid, "room_name": current_room}
        # mqttc2.connect(MQTT_RPi, 1883, 60)
        # mqttc2.publish(MQTT_topic_RPi, current_room)
        # mqttc2.disconnect()
        # copyfile('/home/pi/Localization/Magnetometer/magneto_loc/samplepics/' + current_room + '.png', '/etc/openhab2/html/localization/current.png')
        # bashCommand="sudo convert /etc/openhab2/html/localization/current.png -pointsize 18 -fill #00CCFF -annotate +600+50 " +  'Current Room: ' +current_room+ " /etc/openhab2/html/localization/current.png"
        # process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        # output, error = process.communicate()
        # previous_room = current_room
        # dir = os.path.dirname(__file__)
        # cFile = os.path.join(dir, 'samplepics/' + current_room + '.png')
        # copyfile(cFile, '/etc/openhab2/html/pic_mag.png')


# MongoDB - CONNECT
server = SSHTunnelForwarder(
    MONGO_HOST,
    ssh_username=MONGO_USER,
    ssh_password=MONGO_PASS,
    remote_bind_address=('127.0.0.1', 27017)
)
server.start()
client = MongoClient('127.0.0.1', server.local_bind_port) # server.local_bind_port is assigned local port
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION_NAME]

# MQTT - SERVER INFO
mqttc2 = mqtt.Client(client_id=clientid, protocol=3)

# MQTT - RPI INFO
print("Client: " + clientid)
print("Server: " + MQTT_RPi)
print("Topic: " + MQTT_topic_RPi)
print

# Get TrainingData
d = []
cursor = collection.find({})
for document in cursor:
    d.append(document)
trainSet = []
for fi in d:
    finger = []
    local = fi["room_name"] + "_" + str(fi["boxid"]) + "_" + str(fi["fingerid"])
    RSSI_array = fi["RSSI"]
    for RSSI in RSSI_array[:-2]:
        finger.append(int(RSSI["RSSI-Value"]))
    finger.append(local)
    trainSet.append(finger)

count = 0

argparser = argparse.ArgumentParser()
argparser.add_argument("-d", "--device", help="serial device /dev file modem",
                       default="/dev/ttyUSB0")
argparser.add_argument("-r", "--rate", help="baudrate for serial device", type=int, default=115200)
argparser.add_argument("-v", "--verbose", help="verbose", default=False, action="store_true")
config = argparser.parse_args()

modem = Modem(config.device, config.rate, receive_callback=received_command_callback, show_logging=config.verbose)

modem.start_reading()

# Program loop
while True:
    pass
