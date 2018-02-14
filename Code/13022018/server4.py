### This code is to be run on the server and takes as user inputs the thresholds and
### transmits these values to the IoT devices. It then logs and saves all data 
### received from the devices in unique comma-separated values text files. It also
### creates a graph of the temperature and humidity data and updates this live.

import paho.mqtt.client as mqtt
import time
import datetime
import csv
import json
import matplotlib.pyplot as plt
import matplotlib
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

#initialise the graph here and when the graph() function is called it only updates it
plt.ion()
fig, ax1 = plt.subplots()
fig.canvas.set_window_title('Data Plot')
plt.title("mdeded-01 Sensor Data", fontsize=28)

#------------------------------------------------------------------------------------
#Function to update the graph
def graph(times, temps, humids, refresh):
    global min_temp, max_temp, min_humid, max_humid

    #create the left hand y-axis as the temperature values
    l1, = ax1.plot(times, temps, 'r', label='^C', marker='o')
    ax1.set_ylabel("Temperature/^C", fontsize=18)
    ax1.set_xlabel("Time Elapsed /s", fontsize=18)
    ax1.tick_params('y', colors='r', labelsize=16)
    ax1.tick_params('x', labelsize=16)
    ax1.set_ylim([min_temp,max_temp])
    handles1, labels1 = ax1.get_legend_handles_labels()

    #create the right hand y-axis as the humidity values
    ax2 = ax1.twinx()
    l2, = ax2.plot(times, humids,'b', label='%', marker='x')
    ax2.set_ylabel("Humidity /%", fontsize=18)
    ax2.tick_params('y', colors='b', labelsize=16)
    ax2.set_ylim([min_humid, max_humid])
    handles2, labels2 = ax2.get_legend_handles_labels()
    #ax2.legend(handles2, labels2)

    plt.legend([l1, l2],["Temperature","Humidity"])
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

    if msg.topic == "/esys/mdeded/data/" :
        #data = json.loads(str(msg.payload))
        data = json.loads(msg.payload)
        alert(data["temp"], data["humid"], data["knock"], data["time"])
        temps.append(data["temp"])
        humids.append(data["humid"])
        times.append(data["secs"])
        graph(times, temps, humids, 0.1)

        with open(data['name'] + '.csv', 'a') as csvfile:
            datafile = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            datafile.writerow([data["name"]] + [data["time"]] + [data["temp"]] + [data["humid"]])



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
