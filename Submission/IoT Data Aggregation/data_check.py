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
                                    # (same as file name but with .csv and - removed)

    
# create 2d array of knock times where each row is a different device 
for z in range(len(files)):
    filedatas.append(pd.read_csv(files[z], sep=',',header=None))
    times.append([])
    for entry in range(len(filedatas[z])):
        if(filedatas[z].values[entry][4] == True):
            times[z].append(filedatas[z].values[entry][1])


knocks=[]
present = False

# Creates new 2d array (knocks) where first value in each row is time of knocks
# boolean 'present' will ensure there are no duplicates
for entry in range(len(times)):
    for x in range(len(times[entry])):
        for i in range(len(knocks)):
            if knocks[i][0]==times[entry][x]:
                present=True
        if not present:
            knocks.append([times[entry][x]])
        present=False


# Goes through 2d array 'knocks' and appends devices which were knocked at
# each time to the relevent row
for entry in range(len(knocks)):
    for x in range(len(times)):
        for y in range(len(times[x])):
            if times[x][y]==knocks[entry][0]:
                knocks[entry].append(devices[x])


# Print number of knocks which occured at each time across all devices
print("\n")
for entry in range(len(knocks)):
    print("At time: " + str(knocks[entry][0]) + " there were ", len(knocks[entry])-1, " knocks.")

# Print the times when <35% of the devices experienced knocks and the names of those which did
print("")
for entry in range(len(knocks)):
    if len(knocks[entry])-1  <= 0.35*len(devices):
        print("\nAt time: " + str(knocks[entry][0]) + " only ", len(knocks[entry])-1,
            " containers were knocked, check individual containers:", end=" ")
        for x in range(len(knocks[entry])):
            if x>0:
                print(str(knocks[entry][x]), end=", ")

# Print the times when >90% of the devices experienced knocks, also prints the percentage of
# all devices which experienced this knock
print("\n")
for entry in range(len(knocks)):
    if len(knocks[entry])-1  >= 0.90*len(devices):
        percent = (len(knocks[entry])-1)/len(devices)
        percent = percent*100
        percent = int(round(percent))
        print("\nAt time: " + str(knocks[entry][0]) + ", " + str(percent) +" % of the containers were knocked, possible shipment incident")

print("\n")
