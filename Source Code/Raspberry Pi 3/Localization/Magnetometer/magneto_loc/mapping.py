import datetime
import json
import os
import sys
from sys import argv

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
import time

prompt = '> '

# Variables
mag_valueX = []
mag_valueY = []
mag_valueZ = []
pitchs = []
rolls = []
yaws = []
bars = []

#Accuracy
maxMapMessages = 2
MaxAccuracy = 1

def received_command_callback(cmd):
    if(check):
        dataLocal = cmd.actions[0].operand.data
        print dataLocal
        mag_valueX.append(int(format(dataLocal[1], '#010b') + format(dataLocal[2], '08b'),2))
        mag_valueY.append(int(format(dataLocal[3], '#010b') + format(dataLocal[4], '08b'),2))
        mag_valueZ.append(int(format(dataLocal[5], '#010b') + format(dataLocal[6], '08b'),2))
        pitchs.append(int(format(dataLocal[7], '#010b') + format(dataLocal[8], '08b'), 2))
        rolls.append(int(format(dataLocal[9], '#010b') + format(dataLocal[10], '08b'), 2))
        yaws.append(int(format(dataLocal[11], '#010b') + format(dataLocal[12], '08b'), 2))
        bars.append(int(format(dataLocal[13], '#010b') + format(dataLocal[14], '08b'), 2))

        # Counter for max messages
        global count
        count = count + 1

check = False
def mapData(room_name,boxid,fingerid):
    #Enter before mapping
    json_data = []

    #Read MQTT messages
    while count < maxMapMessages:
        global check
        check = True

    check = False

    #Take the median of each gateway
    if len(mag_valueX) > 0:
        a = numpy.array(mag_valueX)
        RSSI_mag_valueX = numpy.median(a)
    if len(mag_valueY) > 0:
        a = numpy.array(mag_valueY)
        RSSI_mag_valueY = numpy.median(a)
    if len(mag_valueZ) > 0:
        a = numpy.array(mag_valueZ)
        RSSI_mag_valueZ = numpy.median(a)
    if len(pitchs) > 0:
        a = numpy.array(pitchs)
        RSSI_pitch = numpy.median(a)
    if len(rolls) > 0:
        a = numpy.array(rolls)
        RSSI_roll = numpy.median(a)
    if len(yaws) > 0:
        a = numpy.array(yaws)
        RSSI_yaw = numpy.median(a)
    if len(bars) > 0:
        a = numpy.array(bars)
        RSSI_bar = numpy.median(a)

    #Create the mapping JSON
    data = {}
    data['room_name'] = room_name
    data['boxid'] = int(boxid)
    data['fingerid'] = fingerid
    data['data_type'] = "raw_mean"
    timestamp = datetime.datetime.now()
    data['timestamp'] = timestamp
    RSSI = []
    if len(mag_valueX) > 0:
        RSSI.append({"Variable": "mag_valueX", "RSSI-Value": int(RSSI_mag_valueX)})
    else:
        RSSI.append({"Variable": "mag_valueX", "RSSI-Value": 0})
    if len(mag_valueY) > 0:
        RSSI.append({"Variable": "mag_valueY", "RSSI-Value": int(RSSI_mag_valueY)})
    else:
        RSSI.append({"Variable": "mag_valueY", "RSSI-Value": 0})
    if len(mag_valueZ) > 0:
        RSSI.append({"Variable": "mag_valueZ", "RSSI-Value": int(RSSI_mag_valueZ)})
    else:
        RSSI.append({"Variable": "mag_valueZ", "RSSI-Value": 0})
    if len(pitchs) > 0:
        RSSI.append({"Variable": "pitch", "RSSI-Value": int(RSSI_pitch)})
    else:
        RSSI.append({"Variable": "pitch", "RSSI-Value": 0})
    if len(rolls) > 0:
        RSSI.append({"Variable": "roll", "RSSI-Value": int(RSSI_roll)})
    else:
        RSSI.append({"Variable": "roll", "RSSI-Value": 0})
    if len(yaws) > 0:
        RSSI.append({"Variable": "yaw", "RSSI-Value": int(RSSI_yaw)})
    else:
        RSSI.append({"Gateway": "yaw", "RSSI-Value": 0})
    if len(bars) > 0:
        RSSI.append({"Gateway": "bar", "RSSI-Value": int(RSSI_bar)})
    else:
        RSSI.append({"Gateway": "bar", "RSSI-Value": 0})

    data['RSSI'] = RSSI
    collection.insert(data)


clientid = "Fredsons"
MONGO_HOST = "143.129.37.80"
MONGO_DB = "Team-MetVier"
MONGO_USER = "pi"
MONGO_PASS = "raspberry"
MONGO_COLLECTION_NAME = "V-Blok_mag"
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

# CREATE ROOM
print "Give room name:"
room_name = raw_input(prompt)
print "Give box id:"
boxid = raw_input(prompt)
fingerid = 0
count = 0

argparser = argparse.ArgumentParser()
argparser.add_argument("-d", "--device", help="serial device /dev file modem",
                            default="/dev/ttyUSB0")
argparser.add_argument("-r", "--rate", help="baudrate for serial device", type=int, default=115200)
argparser.add_argument("-v", "--verbose", help="verbose", default=False, action="store_true")
config = argparser.parse_args()

modem = Modem(config.device, config.rate, receive_callback=received_command_callback, show_logging=config.verbose)

modem.start_reading()

while True:
    raw_input(prompt)
    for x in range(MaxAccuracy):
        mapData(room_name, boxid, fingerid)
        count = 0
    print "Room: " + room_name
    print "Box: " + str(boxid) + "_" + str(fingerid)
    fingerid+=1
