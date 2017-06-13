from sys import argv
import paho.mqtt.client as mqtt
import json
import os
prompt = '> '
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

def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))
def on_message(mqttc, obj, msg):
    # Default incoming message
    # print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    # MESSAGE TO JSON
    payload = msg.payload
    payload_JSON = json.loads(payload)
    if (payload_JSON["node"] == nodeid):
        print payload_JSON
        RSSI_value = payload_JSON["link_budget"]
        gatewayID = str(payload_JSON["gateway"])
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
        global count
        count += 1

def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mqttc, obj, level, string):
    print(string)

# CLIENT INFO
clientid = "Willem-develop"
clientprotocol = 3  # MQTTv3.1
mqttc = mqtt.Client(client_id=clientid, protocol=clientprotocol)
nodeid = "b57000009128e"

# SETUP METHODS
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
# mqttc.on_log = on_log

# MQTT SERVER INFO
MQTT_server = "backend.idlab.uantwerpen.be"
MQTT_topic = "/localisation/DASH7"
print("Client: " + clientid)
print("Server: " + MQTT_server)
print("Topic: " + MQTT_topic)
print

# CREATE JSON FILE
print "Writing JSON file..."
print "Give file name:"
file_name = raw_input(prompt)
file_path = "../Mapping/"
file_path = file_path + file_name + ".JSON"
f = open(file_path, 'a')
if os.stat(file_path).st_size != 0:
    f.seek(-1, os.SEEK_END)
    f.truncate()
    f.write(",")
else:
    f.write("[")

room_name = "1"
while True:
    json_data = []
    # CREATE ROOM
    print "Give room name:"
    room_name = raw_input(prompt)
    if room_name == "0":
        break
    print "Give room id:"
    room_id = raw_input(prompt)
    # Create connection
    print("Create connection....")
    mqttc.connect(MQTT_server, 1883, 60)
    mqttc.subscribe(MQTT_topic)
    print("Connection created....\n")
    count = 0
    while count < 60:
        mqttc.loop()
    if len(gateway1) > 0:
        RSSI_gateway1 = round(sum(gateway1) / float(len(gateway1)))
    if len(gateway2) > 0:
        RSSI_gateway2 = round(sum(gateway2) / float(len(gateway2)))
    if len(gateway3) > 0:
        RSSI_gateway3 = round(sum(gateway3) / float(len(gateway3)))
    if len(gateway4) > 0:
        RSSI_gateway4 = round(sum(gateway4) / float(len(gateway4)))
    if len(gateway5) > 0:
        RSSI_gateway5 = round(sum(gateway5) / float(len(gateway5)))
    if len(gateway6) > 0:
        RSSI_gateway6 = round(sum(gateway6) / float(len(gateway6)))
    data = {}
    data['room_id'] = room_id
    data['room_name'] = room_name
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
    json_data = json.dumps(data)
    f.write(json_data)
    f.write(",")
f.seek(-1, os.SEEK_END)
f.truncate()
f.write("]")
f.close()