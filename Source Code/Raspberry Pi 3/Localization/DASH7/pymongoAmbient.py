
from pymongo import MongoClient
from sshtunnel import SSHTunnelForwarder

# Connections
clientid = "Fredsons"
MONGO_HOST = "143.129.37.80"
MONGO_DB = "Ambient"
MONGO_USER = "pi"
MONGO_PASS = "raspberry"
MONGO_COLLECTION_NAME = "V-Blok"

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


#JSON to insert
toInsert = {
    "room_name":"V315",
    "room_id":"10",
    "message": "Hi this is a test for ambient!"
}

#Add our JSON to our database
collection.insert(toInsert)

#Fill in room ID and name to find your JSON
toFind = {
    "room_name":"V315",
    "room_id":"10"
}

#Get toFind
print "Get: " + str(toFind)
cursor = collection.find(toFind)
for document in cursor:
    print(document)

#Delete our record to keep database clean
collection.find_one_and_delete(toFind)