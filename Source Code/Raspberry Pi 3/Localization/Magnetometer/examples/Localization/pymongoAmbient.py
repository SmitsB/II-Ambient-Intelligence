
from pymongo import MongoClient

#Connect to MongoDB
# client = MongoClient('localhost', 27017)
client = MongoClient('127.0.0.1', 27017)
db = client['Ambient']
collection = db['V-blok']

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
