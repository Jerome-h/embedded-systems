import paho.mqtt.client as mqtt
import time
import csv
import json
#import matplotlib
#import pyplot as plt
#from matplotlib import pyplot as plt
#matplotlib.use('Agg')
import matplotlib.pyplot as plt

global oldmsg
global valCorrect
valCorrect = False
#oldmsg=0
temps = []
#times = []


def graph(temps,refresh):
    #dates = matplotlib.dates.date2num(times)
    #plt.plot_date(dates, temps,'r',label='^C',marker='o')
    plt.plot(temps,'r',label='^C',marker='o')
    plt.legend()
    axes = plt.gca()
    plt.draw()
    plt.pause(refresh)
    plt.clf()
#dates = matplotlib.dates.date2num(times)
#matplotlib.pyplot.plot_date(dates, temps)

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
    #global oldmsg
    #print(msg.topic+" "+str(msg.payload))
    #print(msg.topic+" "+msg.payload.decode('utf-8'))

    if msg.topic == "/esys/mdeded/data/" :
        #data = json.loads(str(msg.payload))
        data = json.loads(msg.payload)
        temps.append(data["temp"])
        #datetime.strptime("02/05/2017","%m/%d/%Y")
        #times.append(data["time"])
        graph(temps,1)
        #print("time: " + [data["time"]])
        #print("temp: " + [data["time"]])
        #print("humid: " + [data["humid"]])
        with open('data.csv', 'a') as csvfile:
            datafile = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            datafile.writerow([data["time"]] + [data["temp"]] + [data["humid"]])

    #try:
    #    value = int(msg.payload.split(":")[0])
    #    if value > oldmsg :
    #        reply = "Received: "+str(msg.payload)
    #        client.publish("/esys/mdeded/", payload=reply, qos=0, retain=False)
    #        oldmsg=value+1
    #except ValueError:
    #    pass




client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.0.10", 1883, 60)

while valCorrect == False:
    accel=float(input("Enter accelerometer threshold: "))
    temp=float(input("Enter temperature threshold: "))
    humid=float(input("Enter humidity threshold: "))
    print("Threshold values are: Accelerometer = "+ str(accel) + ", temperature = "+ str(temp)+", humidity = "+ str(humid))
    valCorrectStr=input("Are these values correct? Enter TRUE or FALSE: ")
    if (valCorrectStr.upper() == "TRUE"):
        valCorrect = True
thresholds = json.dumps({'accel':accel, 'temp':temp, "humid":humid})
client.publish('/esys/mdeded/thresholds/',bytes(thresholds,'utf-8'))



# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
