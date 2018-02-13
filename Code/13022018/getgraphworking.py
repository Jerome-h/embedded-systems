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

    l1, = ax1.plot(times, temps,'r',label='^C',marker='o')
    plt.gcf().autofmt_xdate()
    ax1.set_ylabel("Temperature/^C")
    ax1.tick_params('y', colors='r')
    ax1.set_ylim([min_temp,max_temp])
    #plt.legend(bbox_to_anchor=(0., 1.02,1.,.102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

    ax2 = ax1.twinx()
    l2, = ax2.plot(humids,'b', label='%', marker='x')
    ax2.set_ylabel("Humidity /%")
    ax2.tick_params('y', colors='b')
    ax2.set_ylim([min_humid, max_humid])

    plt.legend([l1, l2],["^C", "%"])

    plt.draw()
    plt.pause(refresh)







# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
