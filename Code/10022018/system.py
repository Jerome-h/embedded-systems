from umqtt.simple import MQTTClient
import network
import ujson
import json
import time
import machine
from machine import Pin,I2C

i2cport = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
button = Pin(16, Pin.IN)
LED = Pin(14, Pin.OUT)

rtc = machine.RTC()

global t_accel, t_temp, t_humid

t_accel, t_temp, t_humid = 0, 0, 0

def readtemp():
    #send the read temperature command
    i2cport.writeto(0x44,bytearray([0xf3]))

    #read two bytes of data
    #data=i2cport.readfrom(0x40,2)  This didnt work
    data=i2cport.readfrom_mem(0x44,0x01,2)

    #convert the two bytes to an int
    rawtemp = int.from_bytes(data,'big')
    temp = float(rawtemp)/100	#convert into Celsius

    #print(temp)     #print temperature
    return temp


def readhum():
    # send the read temperature command
    i2cport.writeto(0x40, bytearray([0xe5]))

    # read two bytes of data
    data1 = i2cport.readfrom(0x40, 2)
    finaldata1 = int.from_bytes(data1, 'big')
    humfinal = ((125 * finaldata1) / 65536) - 6

    #print(humfinal)     #print humidity
    return humfinal

def sub_msg(topic, msg):
    global t_accel, t_temp, t_humid
    if topic == "esys/time":
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
    elif topic == "/esys/mdeded/thresholds/":
        thresholds = json.loads(msg.payload)
        t_accel = thresholds["accel"]
        t_temp = thresholds["temp"]
        t_humid = thresholds["humid"]

def log():
    global t_accel, t_temp, t_humid
    oldtemp = 0
    oldhum = 0
    oldx=0
    oldy=0
    oldz=0
    while True:
        xknock=False
        yknock=False
        zknock=False
        knock=False
        i2cport.writeto(0x18,bytearray([0x20,0x97]))
        xsmall=i2cport.readfrom_mem(0x18,0x28,1)
        xbig=i2cport.readfrom_mem(0x18,0x29,1)
        x = xbig + xsmall
        ysmall=i2cport.readfrom_mem(0x18,0x2a,1)
        ybig=i2cport.readfrom_mem(0x18,0x2b,1)
        y = ybig + ysmall
        zsmall=i2cport.readfrom_mem(0x18,0x2c,1)
        zbig=i2cport.readfrom_mem(0x18,0x2d,1)
        z = zbig + zsmall

        #convert the two bytes to an int
        xaccel = int.from_bytes(x,'big')
        if xaccel>0x7fff:
            xaccel = xaccel - 0x10000
        yaccel = int.from_bytes(y,'big')
        if yaccel>0x7fff:
            yaccel = yaccel - 0x10000
        zaccel = int.from_bytes(z,'big')
        if zaccel>0x7fff:
            zaccel = zaccel - 0x10000

        if xaccel>oldx+t_accel or xaccel<oldx-t_accel:
            knock="ALERT: x axis"
            xknock=True
            oldx = xaccel
        if yaccel>oldy+t_accel or yaccel<oldy-t_accel:
            knock="ALERT: y axis"
            yknock=True
            oldy = yaccel
        if zaccel>oldz+t_accel or zaccel<oldz-t_accel:
            knock="ALERT: z axis"
            zknock=True
            oldz = zaccel

        if xknock or yknock or zknock:
            knock = True

        temp = readtemp()-10
        humidity = readhum()

        year, month, day, weekday, hour, minutes, seconds, subseconds = rtc.datetime()
        clocktime = "%d:%d:%d" % (hour, minutes, seconds)
        if temp > oldtemp+t_temp or temp < oldtemp-t_temp:
            payload = json.dumps({'time':clocktime, 'alert':"ALERT: TEMPERATURE"})
            client.publish('/esys/mdeded/ALERT/',bytes(payload,'utf-8'))
        if knock != "0":
            payload = json.dumps({'time':clocktime, 'alert':"ALERT: TEMPERATURE"})
            client.publish('/esys/mdeded/ALERT/',bytes(payload,'utf-8'))

        if temp > oldtemp+t_temp or temp < oldtemp-t_temp or knock:
            payload = json.dumps({'name':'mdeded', 'time':clocktime, 'temp':temp, 'accel':"KNOCKED"})
            print(payload)
            client.publish('/esys/mdeded/',bytes(payload,'utf-8'))
            oldtemp = temp


#Waits until button is pressed before opening communications
while button == 0:
    pass

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
client.set_callback(sub_msg)
client.connect()
time.sleep(0.5)
client.subscribe("esys/time")
client.wait_msg()

#Subscribes to topic which user passes threshold values to
client.subscribe("/esys/mdeded/thresholds/")
while t_temp == 0:
    client.wait_msg()

#turn on LED to represent thresholds ave been received
LED.on()
#Waits until button is pressed before starting log
while button == 0:
    pass
# Turn off LED to save power
LED.off()
#Start Logging data
log()




