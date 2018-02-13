import paho.mqtt.client as mqtt
import time
import datetime
import csv
import json
#import matplotlib
#import pyplot as plt
#from matplotlib import pyplot as plt
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


global oldmsg
global valCorrect
global min_temp, max_temp, min_humid, max_humid

valCorrect = False
min_temp, max_temp, min_humid, max_humid = float(0), float(0), float(0), float(0)
#oldmsg=0
temps = []
humids = []
times = []

plt.ion()
fig, ax1 = plt.subplots()
fig.canvas.set_window_title('Data')



def graph(times, temps, humids, refresh):
    global min_temp, max_temp, min_humid, max_humid

    ax1.plot(times, temps,'r',label='^C',marker='o')
    plt.gcf().autofmt_xdate()
    ax1.set_ylabel("Temperature/^C")
    ax1.tick_params('y', colors='r')
    ax1.set_ylim([min_temp,max_temp])
    #plt.legend(bbox_to_anchor=(0., 1.02,1.,.102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

    ax2 = ax1.twinx()
    ax2.plot(humids,'b', label='%', marker='x')
    ax2.set_ylabel("Humidity /%")
    ax2.tick_params('y', colors='b')
    ax2.set_ylim([min_humid, max_humid])


    plt.draw()
    plt.pause(refresh)


def alert(temp, humid, knock, clocktime):
    global min_temp, max_temp, min_humid, max_humid
    # year, month, day, weekday, hour, minutes, seconds, subseconds = datetime.strptime()
    # clocktime = "%d:%d:%d" % (hour, minutes, seconds)
    # year, month, day, weekday, hour, minutes, seconds, subseconds = rtc.datetime()
    # clocktime = "%d:%d:%d" % (hour, minutes, seconds)
    # Temperature Alert
    if temp > max_temp or temp < min_temp:
        payload = json.dumps({'time': clocktime, 'alert': "ALERT: TEMPERATURE"})
        client.publish('/esys/mdeded/ALERT/', bytes(payload, 'utf-8'))
    # Humidity Alert
    if humid > max_humid or humid < min_humid:
        payload = json.dumps({'time': clocktime, 'alert': "ALERT: HUMIDITY"})
        client.publish('/esys/mdeded/ALERT/', bytes(payload, 'utf-8'))
    # Knock Alert
    if knock:
        payload = json.dumps({'time': clocktime, 'alert': "ALERT: KNOCK"})
        client.publish('/esys/mdeded/ALERT/', bytes(payload, 'utf-8'))


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("esys/time")
    client.subscribe("/esys/mdeded/")
    client.subscribe("/esys/mdeded/data/")
    client.subscribe("/esys/mdeded/ALERT/")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    #global oldmsg
    #print(msg.topic+" "+str(msg.payload))
    #print(msg.topic+" "+msg.payload.decode('utf-8'))

    if msg.topic == "/esys/mdeded/data/" :
        #data = json.loads(str(msg.payload))
        data = json.loads(msg.payload)
        print(data["time"])
        year, month, day, weekday, hour, minutes, seconds, subseconds = data["time"]
        clocktime = "%d:%d:%d" % (hour, minutes, seconds)
        alert(data["temp"], data["humid"], data["knock"], clocktime)
        temps.append(data["temp"])
        humids.append(data["humid"])
        times.append(data["time"])
        graph(times, temps, humids, 0.1)
        #print("time: " + [data["time"]])
        #print("temp: " + [data["time"]])
        #print("humid: " + [data["humid"]])
        with open(data['name'] + '.csv', 'a') as csvfile:
            datafile = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            datafile.writerow([data["name"]] + [data["time"]] + [data["temp"]] + [data["humid"]])

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

while valCorrect != True:
    accel = float(input("Enter accelerometer resolution: "))
    temp = float(input("Enter temperature resolution: "))
    humid = float(input("Enter humidity resolution: "))
    min_temp = float(input("Enter minimum temperature: "))
    max_temp = float(input("Enter maximum temperature: "))
    min_humid = float(input("Enter minimum humidity: "))
    max_humid = float(input("Enter maximum humidity: "))
    print("Threshold values are: Accelerometer = "+ str(accel) + ", temperature = "+ str(temp)+", humidity = "+ str(humid))
    print("Min/max values are: Min temp = "+ str(min_temp) + ", max temp = "+ str(max_temp)+", min humidity = "+ str(min_humid)+", max humidity = "+ str(max_humid))
    valCorrectStr = input("Are these values correct? Enter TRUE or FALSE: ")
    if (valCorrectStr.upper() == "TRUE"):
        valCorrect = True
inputs = json.dumps({'accel': accel, 'temp': temp, 'humid': humid})
client.publish('/esys/mdeded/inputs/', bytes(inputs, 'utf-8'))





# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
