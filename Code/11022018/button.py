from machine import Pin
import time

button = Pin(16, Pin.IN)

while True:
    if button.value() == 0:
    	print ("Button is not pressed")
    	time.sleep(0.3)

    else:
    	print("Button has been pressed")
    	time.sleep(0.3)
