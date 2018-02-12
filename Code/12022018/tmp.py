def readtemp():
    #send the read temperature command
    i2cport.writeto(0x44,bytearray([0xf3]))

    #read two bytes of data
    #data=i2cport.readfrom(0x40,2)  This didnt work
    data=i2cport.readfrom_mem(0x44,0x03,2)
    #convert to Celcius
    temp=(data[0]*32 + data[1])*0.03125
    #convert the two bytes to an int
    rawtemp = float.from_bytes(data,'big')


    #print(temp)     #print temperature
    return temp
