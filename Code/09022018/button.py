from machine import Pin

button = Pin(12, Pin.IN)

while True:
    while button.value() == 0:
        pass
    print('Button has been pressed' + '\n')