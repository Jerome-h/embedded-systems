import pandas as pd
import glob

devices=[]      # array to hold device names
filedatas=[]    # array to hold files
times=[]        # 2d array to hold times of knocks - times[device][times]


files=glob.glob('*.csv')            # create array of csv files
for entry in range(len(files)):
    device = files[entry].replace('-', '')
    device = device.replace('.csv', '')
    devices.append(device)          # create list of all device names

for z in range(len(files)):
    filedatas.append(pd.read_csv(files[z], sep=',',header=None))
    times.append([])
    for entry in range(len(filedatas[z])):
        if(filedatas[z].values[entry][4] == True):
            times[z].append(filedatas[z].values[entry][1])


knocks=[]
present = False

for entry in range(len(times)):
    for x in range(len(times[entry])):
        for i in range(len(knocks)):
            if knocks[i][0]==times[entry][x]:
                present=True
        if not present:
            knocks.append([times[entry][x]])
        present=False


for entry in range(len(knocks)):
    for x in range(len(times)):
        for y in range(len(times[x])):
            if times[x][y]==knocks[entry][0]:
                knocks[entry].append(devices[x])



print("\n")
for entry in range(len(knocks)):
    print("At time: " + str(knocks[entry][0]) + " there were ", len(knocks[entry])-1, " knocks.")

print("")

for entry in range(len(knocks)):
    if len(knocks[entry])-1  <= 0.35*len(devices):
        print("\nAt time: " + str(knocks[entry][0]) + " only ", len(knocks[entry])-1,
            " containers were knocked, check individual containers:", end=" ")
        for x in range(len(knocks[entry])):
            if x>0:
                print(str(knocks[entry][x]), end=", ")

print("\n")

for entry in range(len(knocks)):
    if len(knocks[entry])-1  >= 0.95*len(devices):
        print("\nAt time: " + str(knocks[entry][0]) + " at least 95% of the containers were knocked, possible shipment incident")

print("\n")
