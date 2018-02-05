import paho.mqtt.client as mqtt
import time
import csv
import json
global oldmsg
oldmsg=0

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("esys/time")
    client.subscribe("/esys/mdeded/")
    client.subscribe("/esys/mdeded/data/")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global oldmsg
    print(msg.topic+" "+str(msg.payload))

    if msg.topic == "/esys/mdeded/data/" :
        data = json.loads(str(msg.payload))
        with open('data.csv', 'wb') as csvfile:
            datafile = csv.writer(csvfile, delimiter='', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            datafile.writerow([data["time"]] + [data["temp"]])

    try:
        value = int(msg.payload.split(":")[0])
        if value > oldmsg :
            reply = "Received: "+str(msg.payload)
            client.publish("/esys/mdeded/", payload=reply, qos=0, retain=False)
            oldmsg=value+1
    except ValueError:
        pass



client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.0.10", 1883, 60)


# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
