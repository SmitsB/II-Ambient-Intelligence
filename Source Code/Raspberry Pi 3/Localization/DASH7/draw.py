# Example of kNN implemented from Scratch in Python

import csv
import random
import math
import operator
from pymongo import MongoClient
from matplotlib import pyplot
#import pylab
from mpl_toolkits.mplot3d import Axes3D
from sshtunnel import SSHTunnelForwarder

# Connections
clientid = "Fredsons"
MONGO_HOST = "143.129.37.80"
MONGO_DB = "Team-Cool"
MONGO_USER = "pi"
MONGO_PASS = "raspberry"
MONGO_COLLECTION_NAME = "V-Blok"


def drawNeighbours(trainSet, testSet):
    drawList = {}
    ax = pyplot.subplot(111, projection='3d')

    for x in range(len(trainSet)):
        response = trainSet[x][-1].encode('ascii', 'ignore')
        if response in drawList:
            drawList[response][0].append(trainSet[x][1])
            drawList[response][1].append(trainSet[x][3])
            drawList[response][2].append(trainSet[x][4])
        else:
            drawList[response] = [[], [], []]
            drawList[response][0].append(trainSet[x][1])
            drawList[response][1].append(trainSet[x][3])
            drawList[response][2].append(trainSet[x][4])

    ax.scatter(testSet[1], testSet[3], testSet[4], label='Sample')
    for key, value in drawList.items():
        ax.scatter(value[0], value[1], value[2], label=key)

    ax.legend()
    pyplot.show()


def euclideanDistance(instance1, instance2, length):
    distance = 0
    for x in range(length):
        distance += pow((instance1[x] - instance2[x]), 2)
    return math.sqrt(distance)


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


def main():
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

    # Get TrainingData
    d = []
    cursor = collection.find({})
    for document in cursor:
        d.append(document)
    trainSet = []
    for fi in d:
        finger = []
        local = fi["room_name"]# + "_" + str(fi["boxid"]) + "_" + str(fi["fingerid"])
        RSSI_array = fi["RSSI"]
        for RSSI in RSSI_array:
            finger.append(int(RSSI["RSSI-Value"]))
        finger.append(local)
        trainSet.append(finger)

    # prepare data
    testSet = [0, 78, 0, 57, 81, 0]

    # generate predictions
    predictions = []
    k = 7

    neighbors = getNeighbors(trainSet, testSet, k)
    result = getResponse(neighbors)
    print('> predicted=' + repr(result))
    drawNeighbours(trainSet, testSet)


main()