import pandas as pd
import glob

devices=[]
filedatas=[]
times=[]


files=glob.glob('*.csv')
for entry in range(len(files)):
    device = files[entry].replace('-', '')
    device = device.replace('.csv', '')
    devices.append(device)

for z in range(len(files)):
    filedatas.append(pd.read_csv(files[z], sep=',',header=None))
    times.append([])
    for entry in range(len(filedatas[z])):
        if(filedatas[z].values[entry][4] == True):
            times[z].append(filedatas[z].values[entry][1])

for x in range(len(times[0])):
    for y in range(len(times[1])):
        if(times[0][x] == times[1][y]):
            print(times[0][x])

for x in 
