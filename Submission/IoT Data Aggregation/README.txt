This code stands separately to the system and server code. It would run on the server and read the outputted .csv data log files.

It demonstrates the possibility of processing data from a large number of devices working simultaneously in a swarm. It analyses the data and if a knock is detected on less than 35% of the devices at a particular time, if detects and prints this. This simulates if for example a few containers become loose or unstable. It also detects if a knock is registered by over 95% of the devices, this symbolises an issue in the shipment for instance the lorry crashing. 

This is a demonstration, in the real thing instead of percentages of number of devices it could also use the magnitudes of the knocks to indicate the how bad the issue is.

Included here is:
  The python code
  6 example system output .csv files
  A screenshot of the python code output run on the example files
