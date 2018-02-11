from machine import Pin,I2C
import time

#create the i2cport
i2cport = I2C(scl=Pin(5), sda=Pin(4), freq=100000)

def readtemp():
	while True:

	    #send the read temperature command
	    i2cport.writeto(0x40, bytearray([0xe3]))
	    time.sleep(2)

	    #read two bytes of data
	    data1=i2cport.readfrom(0x40, 2)

	    finaldata1=int.from_bytes(data1,'big')
	    tempfinal=((175.72*finaldata1)/65536)-46.85
	    print("Temp at port: ")
	    print(tempfinal)



	    # data2=i2cport.readfrom_mem(0x40,0xe7,2)
	    # finaldata2=int.from_bytes(data2,'big')

	    # print("Data in register: ")
	    # print(finaldata2)
	    print("\n")



	    #convert the two bytes to an int
	    # rawtemp = int.from_bytes(data,'big')
	    # temp = float(rawtemp)/100	#convert into Celsius

	time.sleep(1)

def readhum():
	while True:

	    #send the read temperature command
	    i2cport.writeto(0x40, bytearray([0xe5]))
	    time.sleep(2)

	    #read two bytes of data
	    data1=i2cport.readfrom(0x40, 2)

	    finaldata1=int.from_bytes(data1,'big')
	    humfinal=((125*finaldata1)/65536)-6
	    print("Humidity at port: ")
	    print(humfinal)



	    # data2=i2cport.readfrom_mem(0x40,0xe7,2)
	    # finaldata2=int.from_bytes(data2,'big')

	    # print("Data in register: ")
	    # print(finaldata2)
	    print("\n")



	    #convert the two bytes to an int
	    # rawtemp = int.from_bytes(data,'big')
	    # temp = float(rawtemp)/100	#convert into Celsius

	time.sleep(1)
