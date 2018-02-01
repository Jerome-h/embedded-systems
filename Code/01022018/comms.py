from umqtt.simple import MQTTClient
import network
import ujson
import json
import time
import test1
import machine
from ntptime import settime


ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.scan()
sta_if.connect('EEERover', 'exhibition')
time.sleep(0.5)
print(sta_if.isconnected())

#settime()
rtc = machine.RTC()
rtc.datetime((2014, 5, 1, 0, 4, 13, 0, 0))
print(rtc.datetime())
#print(rtc.now())

def run():
    message = {'11:00': test1.readtemp(), '11:30': 24.7}

    payload = json.dumps({'name':'mdeded', 'temprecord':message})
    print(payload)


    #CLIENT_ID = machine.unique_id()
    client = MQTTClient('50688','192.168.0.10')
    client.connect()
    time.sleep(0.5)
    client.publish('/esys/mdeded/',bytes(payload,'utf-8'))
