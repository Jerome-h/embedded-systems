from umqtt.simple import MQTTClient
import network
import ujson
import json
import time
import test1
import machine

rtc = machine.RTC()

def sub_time(topic, msg):
    print(msg.decode('utf-8'))
    clock = msg.decode('utf-8')
    datedata = clock.split("T")[0]
    clockdata = clock.split("T")[1]
    timedata = clockdata.split("+")[0]
    year = datedata.split("-")[0]
    month = datedata.split("-")[1]
    day = datedata.split("-")[2]
    hours = timedata.split(":")[0]
    minutes = timedata.split(":")[1]
    seconds = timedata.split(":")[2]

    rtc.datetime((int(year), int(month), int(day), 0, int(hours), int(minutes), int(seconds), 0))
    print(rtc.datetime())
    #print(rtc.hours)

ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.scan()
sta_if.connect('EEERover', 'exhibition')
time.sleep(0.5)
print(sta_if.isconnected())


#CLIENT_ID = machine.unique_id()
client = MQTTClient('50688','192.168.0.10')
client.set_callback(sub_time)
client.connect()
time.sleep(0.5)
client.subscribe("esys/time")
client.wait_msg()



def run():
    year, month, day, weekday, hour, minutes, seconds, subseconds = rtc.datetime()
    time = "%d:%d:%d" % (hour, minutes, seconds)
    #message = {time: test1.readtemp()}

    payload = json.dumps({'name':'mdeded', 'time':time, 'temp':test1.readtemp()})
    print(payload)

    client.publish('/esys/mdeded/',bytes(payload,'utf-8'))



def time():
    print(rtc.datetime())
