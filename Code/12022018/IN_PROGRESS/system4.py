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

global d_accel, d_temp, d_humid
d_accel, d_temp, d_humid = float(0), float(0), float(0)

def readtemp():
    #send the read temperature command
    #old code which works
#    i2cport.writeto(0x44,bytearray([0xf3]))
#    data=i2cport.readfrom_mem(0x44, 0x01,2)
#    rawtemp=int.from_bytes(data, 'big')
#    temp = float(rawtemp)/100
#    return temp


    i2cport.writeto(0x44,bytearray([0xf3]))
    data=i2cport.readfrom_mem(0x44, 0x03,2)
    rawtemp=(data[0]*32 + data[1])*0.03125
    return rawtemp


    #read two bytes of data
    #data=i2cport.readfrom(0x40,2)  This didnt work
    #data=i2cport.readfrom_mem(0x44,0x01,2)

    #tests of calibration
    #data=i2cport.readfrom_mem(0x44,0x03,2)
        #rawtemp=(data[0]*32 + data[1])*0.03125
    #temp = int.from_bytes(rawtemp,'big')


    #convert the two bytes to an int
    #temp = int.from_bytes(rawtemp,'big')
    #temp = float(rawtemp)/100	#convert into Celsius

    #print(temp)     #print temperature
    #return temp

def readhumid():
    # send the read temperature command
    i2cport.writeto(0x40, bytearray([0xe5]))
    time.sleep(0.3)
    # read two bytes of data
    data1 = i2cport.readfrom(0x40, 2)
    finaldata1 = int.from_bytes(data1, 'big')
    humidfinal = ((125 * finaldata1) / 65536) - 6

    #print(humidfinal)     #print humidity
    return humidfinal

def readknock():
    i2cport.writeto(0x18, bytearray([0x20, 0x97]))
    xsmall = i2cport.readfrom_mem(0x18, 0x28, 1)
    xbig = i2cport.readfrom_mem(0x18, 0x29, 1)
    x = xbig + xsmall
    ysmall = i2cport.readfrom_mem(0x18, 0x2a, 1)
    ybig = i2cport.readfrom_mem(0x18, 0x2b, 1)
    y = ybig + ysmall
    zsmall = i2cport.readfrom_mem(0x18, 0x2c, 1)
    zbig = i2cport.readfrom_mem(0x18, 0x2d, 1)
    z = zbig + zsmall

    # convert the two bytes to an int
    xaccel = int.from_bytes(x, 'big')
    if xaccel > 0x7fff:
        xaccel = xaccel - 0x10000
    yaccel = int.from_bytes(y, 'big')
    if yaccel > 0x7fff:
        yaccel = yaccel - 0x10000
    zaccel = int.from_bytes(z, 'big')
    if zaccel > 0x7fff:
        zaccel = zaccel - 0x10000

    accel = [xaccel, yaccel, zaccel]
    return accel

def sub_msg(topic, msg):
    global d_accel, d_temp, d_humid
    if topic.decode('utf-8') == "esys/time":
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
    elif topic.decode('utf-8') == "/esys/mdeded/inputs/":
        print(msg.decode('utf-8'))
        inputs = json.loads(msg.decode('utf-8'))
        d_accel = inputs["accel"]
        d_temp = inputs["temp"]
        d_humid = inputs["humid"]


def log():
    global d_temp, d_humid, d_accel
    oldtemp = 0
    oldhumid = 0
    oldx, oldy, oldz = 0, 0, 0
    while True:
        xknock, yknock, zknock, knock = False, False, False, False
        tempchange = False
        humidchange = False

        temp = readtemp()
        humid = readhumid()
        accel = readknock()
        #Detect if there has been a knock
        if accel[0] > oldx + d_accel or accel[0] < oldx - d_accel:
            xknock = True
        if accel[1] > oldy + d_accel or accel[1] < oldy - d_accel:
            yknock = True
        if accel[2] > oldz + d_accel or accel[2] < oldz - d_accel:
            zknock = True
        if xknock or yknock or zknock:
            knock = True
            # print("knocked")

        #Detect if there has been a temp change
        if temp > oldtemp + d_temp or temp < oldtemp - d_temp:
            tempchange = True

        # Detect if there has been a humidity change
        if humid > oldhumid+d_humid or humid < oldhumid-d_humid:
            humidchange = True

        year, month, day, weekday, hour, minutes, seconds, subseconds = rtc.datetime()
        clocktime = "%d:%d:%d" % (hour, minutes, seconds)
        # If there are any changes to the data, will then send complete data at that time. Updates old values
        if tempchange or humidchange or knock:
            payload = json.dumps({'name': 'mdeded-01', 'time': clocktime, 'temp': temp, 'knock': knock, 'humid': humid})
            print(payload)
            client.publish('/esys/mdeded/data/', bytes(payload, 'utf-8'))
            oldx = accel[0]
            oldy = accel[1]
            oldz = accel[2]
            oldtemp = temp
            oldhumid = humid

print("Waiting for button")
#Waits until button is pressed before opening communications
while button.value() == 0:
    pass
print("connecting")
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.scan()
sta_if.connect('EEERover', 'exhibition')
time.sleep(0.5)
print(sta_if.isconnected())


#CLIENT_ID = machine.unique_id()
client = MQTTClient('50688', '192.168.0.10')
client.set_callback(sub_msg)
client.connect()
time.sleep(0.5)
client.subscribe("esys/time")
print("Waiting for time")
client.wait_msg()

#Subscribes to topic which user passes input values to
client.subscribe("/esys/mdeded/inputs/")
print("Waiting for inputs")
while d_temp == 0:
    client.wait_msg()

print("Inputs:\n%f\n%f\n%f\n" % (d_temp, d_accel, d_humid))
#turn on LED to represent inputs ave been received
LED.on()
#Waits until button is pressed before starting log
print("Waiting for button")
while button.value() == 0:
    pass
# Turn off LED to save power
LED.off()
#Start Logging data
print("logging")
log()
