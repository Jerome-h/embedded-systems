Import comms.py
comms.py calls test1.py

comms:
    Makes connection to router
    Initialises clock
    Has function run():
        Calls test1 to retrieve temperature
        Publishes temperature to topic /esys/mdeded/   
