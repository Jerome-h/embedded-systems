This code stands separately to the system and server code. It would run on the server and read the outputted .csv data log files.

It demonstrates the possibility of processing data from a large number of devices working simultaneously in a swarm. It analyses the data and if a knock is detected on less than 35% of the devices at a particular time, if detects and prints this. This simulates if for example a few containers become loose or unstable. It also detects if a knock is registered by over 90% of the devices, this symbolises an issue in the shipment for instance the lorry crashing. 

The code was tested on 99 example output csv files and identifies the times when >90% of the devices were knocked. It also identifies the times when less than 35% were knocked.

This is a demonstration, in the real thing instead of percentages of number of devices it could also use the magnitudes of the knocks to indicate the how bad the issue is, and a similar analysis could be applied to humidity and temperature data.

This also provides an avenue for machine learning, as algortithms which incorrectly predicted the state of containers could be reviewed and updated according to the new data.

Cloud functionality could also be implemented, allowing remote monitoring of devices by those interested. 

Included files are:
  data_check.py    -    The python code to analyse data
  mdeded-0*.csv    -    6 example system output .csv files
  test_file_gen.py -    Python code to produce 99 copies of mdeded-01.py
  screenshot       -    Screenshot showing output after analysing 99  example files
