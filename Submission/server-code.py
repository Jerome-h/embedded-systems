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
import os.path


global oldmsg
global min_temp, max_temp, min_humid, max_humid

valCorrect = False
min_temp, max_temp, min_humid, max_humid = float(0), float(0), float(0), float(0)
#initialise arrays which will hold data to be passed and plotted on graph
temps = []
humids = []
times = []

# Initialise the graph here and when the graph() function is called it only updates it
plt.ion()
fig, ax1 = plt.subplots()
fig.canvas.set_window_title('Data Plot')
plt.title("mdeded-01 Sensor Data", fontsize=28)


#----------------------------------------------------------------------------------------
#----------------------------- Function to update the graph -----------------------------
#----------------------------------------------------------------------------------------
def graph(times, temps, humids, refresh):
    global min_temp, max_temp, min_humid, max_humid

    #create the left hand y-axis as the temperature values:
    l1, = ax1.plot(times, temps, 'r', label='^C', marker='o')
    ax1.set_ylabel("Temperature/^C", fontsize=18)
    ax1.set_xlabel("Time Elapsed /s", fontsize=18)
    ax1.tick_params('y', colors='r', labelsize=16)
    ax1.tick_params('x', labelsize=16)
    ax1.set_ylim([min_temp,max_temp])

    #create the right hand y-axis as the humidity values:
    ax2 = ax1.twinx()
    l2, = ax2.plot(times, humids,'b', label='%', marker='x')
    ax2.set_ylabel("Humidity /%", fontsize=18)
    ax2.tick_params('y', colors='b', labelsize=16)

    ax2.set_ylim([min_humid, max_humid])

    plt.legend([l1, l2],["Temperature","Humidity"])     # create the legend
    plt.draw()                                          # draw the update graph
    plt.pause(refresh)
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------
#------------- Function to check and send alerts if thresholds are exceeded -------------
#----------------------------------------------------------------------------------------
def alert(temp, humid, knock, clocktime):
    global min_temp, max_temp, min_humid, max_humid

    # If temperature outside of threshold range, send alert
    if temp > max_temp or temp < min_temp:
        payload = json.dumps({'time': clocktime, 'alert': "ALERT: TEMPERATURE"})
        client.publish('/esys/mdeded/ALERT/', bytes(payload, 'utf-8'))

    # If humidity outside of threshold range, send alert
    if humid > max_humid or humid < min_humid:
        payload = json.dumps({'time': clocktime, 'alert': "ALERT: HUMIDITY"})
        client.publish('/esys/mdeded/ALERT/', bytes(payload, 'utf-8'))

    # If Knock=true send alert
    if knock:
        payload = json.dumps({'time': clocktime, 'alert': "ALERT: KNOCK"})
        client.publish('/esys/mdeded/ALERT/', bytes(payload, 'utf-8'))
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------
#---- Callback function, run when client receives a CONNACK response from the server ----
#----------------------------------------------------------------------------------------
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/esys/mdeded/")           # main topic
    client.subscribe("/esys/mdeded/data/")      # topic to listen for sensor data
    client.subscribe("/esys/mdeded/ALERT/")     # topic to send alerts on
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------
#------- Callback function run when a PUBLISH message is received from the server -------
#----------------------------------------------------------------------------------------
def on_message(client, userdata, msg):
    # ensure message is from data topic
    if msg.topic == "/esys/mdeded/data/" :
        data = json.loads(msg.payload)          # load message into json object
        alert(data["temp"], data["humid"], data["knock"], data["time"]) # pass data to check for alerts
        temps.append(data["temp"])          # append temperature to array for grph plotting
        humids.append(data["humid"])        # append humidity to array for grph plotting
        times.append(data["secs"])          # append time to array for grph plotting
        graph(times, temps, humids, 0.1)    # plot these updated arrays

        # append new received data to device's unique csv file
        with open(data['name'] + '.csv', 'a') as csvfile:
            datafile = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            datafile.writerow([data["name"]] + [data["time"]] + [data["temp"]] + [data["humid"]])
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------



client = mqtt.Client()
client.on_connect = on_connect              # set callback function, run when connects
client.on_message = on_message              # set callback function, when receives messages
client.connect("192.168.0.10", 1883, 60)    # connect to broker address

# While user inputs have not been set, ask for user inputs:
while valCorrect != True:
    # Set user inputs as the global variables needed in other functions
    accel = float(input("Enter accelerometer resolution: "))
    temp = float(input("Enter temperature resolution: "))
    humid = float(input("Enter humidity resolution: "))
    min_temp = float(input("Enter minimum temperature: "))
    max_temp = float(input("Enter maximum temperature: "))
    min_humid = float(input("Enter minimum humidity: "))
    max_humid = float(input("Enter maximum humidity: "))

    #print input to ask user if correct
    print("Threshold values are: Accelerometer = "+ str(accel) + ", temperature = "
        + str(temp)+", humidity = "+ str(humid))

    print("Min/max values are: Min temp = "+ str(min_temp) + ", max temp = "
        + str(max_temp)+", min humidity = "+ str(min_humid)+", max humidity = "+ str(max_humid))

    # if inputs are correct, set boolean as true to exit while loop
    valCorrectStr = input("Are these values correct? Enter TRUE or FALSE: ")
    if (valCorrectStr.upper() == "TRUE"):
        valCorrect = True

# send resultions to IoT device:
inputs = json.dumps({'accel': accel, 'temp': temp, 'humid': humid})
client.publish('/esys/mdeded/inputs/', bytes(inputs, 'utf-8'))

#function to indefinitely listen for messages, also handles reconnects automatically:
client.loop_forever()
