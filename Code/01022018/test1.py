
#import the necessary modules
from machine import Pin,I2C
import time

#create the i2cport
i2cport = I2C(scl=Pin(5), sda=Pin(4), freq=100000)

print("Enter test1.help() for list of commands")

#function to read temperature once
def readtemp():
    #send the read temperature command
    i2cport.writeto(0x40,bytearray([0xf3]))

    #read two bytes of data
    #data=i2cport.readfrom(0x40,2)  This didnt work
    data=i2cport.readfrom_mem(0x40,0x01,2)

    #convert the two bytes to an int
    rawtemp = int.from_bytes(data,'big')
    temp = float(rawtemp)/100	#convert into Celsius

    #print(temp)     #print temperature
    return(temp)


#function to read temperature every second
def monitortemp():
    while True:
        #send the read temperature command
        i2cport.writeto(0x40,bytearray([0xf3]))

        #read two bytes of data
        #data=i2cport.readfrom(0x40,2)  This didnt work
        data=i2cport.readfrom_mem(0x40,0x01,2)

        #convert the two bytes to an int
        rawtemp = int.from_bytes(data,'big')
        temp = float(rawtemp)/100	#convert into Celsius

        print(temp)     #print temperature
        time.sleep(1)


def readhumidity():
    #send the read temperature command
    i2cport.writeto(0x40,bytearray([0xf5]))
    #i2cport.writeto(0x40,bytearray([0xe7]))

    #read two bytes of data
    data=i2cport.readfrom(0x40,2)  #This didnt work
    #data=i2cport.readfrom_mem(0x40,0xe7,2)

    #convert the two bytes to an int
    rawtemp = int.from_bytes(data,'big')
    #temp = float(rawtemp)/100	#convert into Celsius

    print(rawtemp)     #print temperature



def help():
    print("Commands:")
    print("\nreadtemp()\t-\treads the temperature once")
    print("\nmonitortemp()\t-\treads the temperature every second")
