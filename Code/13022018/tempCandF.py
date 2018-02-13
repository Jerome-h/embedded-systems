import time
import machine
from machine import Pin,I2C

i2cport = I2C(scl=Pin(5), sda=Pin(4), freq=100000)

    #send the read temperature command
i2cport.writeto(0x44,bytearray([0xf3]))

time.sleep(0.5)
    #read two bytes of data
data=i2cport.readfrom_mem(0x44,0x03,2)

# Convert the data to 14-bits
cTemp = ((data[0] * 256 + (data[1] & 0xFC)) / 4)
if cTemp > 8191 :
	cTemp -= 16384
cTemp = cTemp * 0.03125
fTemp = cTemp * 1.8 + 32

# Output data to screen
print ("Object Temperature in Celsius : %.2f C" %cTemp)
print ("Object Temperature in Fahrenheit : %.2f F" %fTemp)
