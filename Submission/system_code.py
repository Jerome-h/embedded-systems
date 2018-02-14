### This code is to be run on the IoT device, firstly it connects to the wifi
### network and broker address. Next it waits for the time and sets the local
### clock, it then waits for the resolution iputs from the server code. It
### then constantly reads the sensor data and transmits this when there is a
### knock or an increase in temperature or humidity.

from umqtt.simple import MQTTClient
import network
import ujson
import json
import time
import machine
from machine import Pin,I2C

# set up the I2C port and I/O pins
i2cport = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
button = Pin(16, Pin.IN)
LED_G = Pin(14, Pin.OUT)
LED_R = Pin(0, Pin.OUT)
LED_R.on() # note the built-in LED on pin 0 is active low so .on() is actually off

i2cport.writeto(0x44,bytearray([0xf3]))
time.sleep(0.5)

rtc = machine.RTC()

global d_accel, d_temp, d_humid
d_accel, d_temp, d_humid = float(0), float(0), float(0)

#----------------------------------------------------------------------------------------
#----------------------- Function to read the temperature sensor ------------------------
#----------------------------------------------------------------------------------------
def readtemp():
    #send the read temperature command
    # i2cport.writeto(0x44,bytearray([0xf3]))
    # time.sleep(0.5)

    # read two bytes of data
    data=i2cport.readfrom_mem(0x44,0x03,2)

    # Convert the data to Celsius
    temp = ((data[0] * 256 + (data[1] & 0xFC)) / 4)
    if temp > 8191 :
    	temp -= 16384
    temp = temp * 0.03125

    return temp
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------
#------------------------- Function to read the humidity sensor -------------------------
#----------------------------------------------------------------------------------------
def readhumid():
    # send the read temperature command
    i2cport.writeto(0x40, bytearray([0xe5]))
    time.sleep(0.3)
    # read two bytes of data
    data1 = i2cport.readfrom(0x40, 2)
    finaldata1 = int.from_bytes(data1, 'big')
    humidfinal = ((125 * finaldata1) / 65536) - 6

    return humidfinal
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------
#-------------------------- Function to read the accelerometer --------------------------
#----------------------------------------------------------------------------------------
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
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------
#------- Callback function run when a PUBLISH message is received from the server -------
#----------------------------------------------------------------------------------------
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

    elif topic.decode('utf-8') == "/esys/mdeded/inputs/":
        print(msg.decode('utf-8'))
        inputs = json.loads(msg.decode('utf-8'))
        d_accel = inputs["accel"]
        d_temp = inputs["temp"]
        d_humid = inputs["humid"]
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------
#----------- Function to log data and send if resolution values are exceeded ------------
#----------------------------------------------------------------------------------------
def log():
    global d_temp, d_humid, d_accel
    offset=time.ticks_ms()/1000
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
        # Detect if there has been a knock
        if accel[0] > oldx + d_accel or accel[0] < oldx - d_accel:
            xknock = True
        if accel[1] > oldy + d_accel or accel[1] < oldy - d_accel:
            yknock = True
        if accel[2] > oldz + d_accel or accel[2] < oldz - d_accel:
            zknock = True
        if xknock or yknock or zknock:
            knock = True

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
            secs=time.ticks_ms()/1000
            payload = json.dumps({'name': 'mdeded-01', 'time': clocktime, 'temp': temp, 'knock': knock, 'humid': humid, 'secs': secs-offset})
            print(payload)
            client.publish('/esys/mdeded/data/', bytes(payload, 'utf-8'))
            oldx = accel[0]
            oldy = accel[1]
            oldz = accel[2]
            oldtemp = temp
            oldhumid = humid
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------



print("Waiting for button")
#Waits until button is pressed before opening communications
while button.value() == 0:
    pass
LED_R.off()
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
LED_G.on()
#Subscribes to topic which user passes input values to
client.subscribe("/esys/mdeded/inputs/")
print("Waiting for inputs")

while d_temp == 0:
    client.wait_msg()
LED_R.on()
print("Inputs:\n%f\n%f\n%f\n" % (d_temp, d_accel, d_humid))
#turn on LED_G to represent inputs ave been received
LED_G.on()
#Waits until button is pressed before starting log
print("Waiting for button")
while button.value() == 0:
    pass
# Turn off LED_G to save power
LED_G.off()
#Start Logging data
print("logging")
log()
