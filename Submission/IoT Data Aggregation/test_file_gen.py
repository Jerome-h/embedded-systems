import shutil

names=[]
name1='mdeded-'
name2='.csv'

for x in range(98):
    i=x+2
    if i<10:
        names.append(name1+"0"+str(i)+name2)
    else:
        names.append(name1+str(i)+name2)


for z in range(len(names)):
    shutil.copyfile('mdeded-01.csv', names[z])
