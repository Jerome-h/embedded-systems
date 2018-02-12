from machine import Pin,I2C
import time
i2cport = I2C(scl=Pin(5), sda=Pin(4), freq=100000)

i2cport.writeto(0x40, bytearray([0xe3]))
i2cport.writeto_mem(0x18, 0x23, bytearray([0b10001000]))
i2cport.writeto_mem(0x18, 0x20, bytearray([0b01110111]))
i2cport.writeto_mem(0x18, 0x1f, bytearray([0xC0]))

while True:
    #send the read temperature command
    time.sleep(0.5)
    data1=i2cport.readfrom(0x40, 2)
    finaldata1=int.from_bytes(data1,'big')
    tempfinal=((175.72*finaldata1)/65536)-46.85
    print("humid temp: ", tempfinal)

    #accel temp
    temp_l=i2cport.readfrom_mem(0x18, 0x0c, 1)[0]
    temp_h=i2cport.readfrom_mem(0x18, 0x0d, 1)[0]
    #accel_temp=int.from_bytes(temp_h + temp_l,'big')
    #print("accel temp: " + accel_temp + " ")
    print((temp_h << 8) + temp_l)
    time.sleep(1)
