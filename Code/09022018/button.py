from machine import Pin
import time

button = Pin(16, Pin.IN)

while True:
    if button.value() == 0:
    	print ("Button is not pressed")
    	time.sleep(1)
    
    else:
    	print('Button has been pressed' + '\n')
    	time.sleep(1)
