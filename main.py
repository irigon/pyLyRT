#!/usr/bin/python3

import time
from libs import g
from libs.monitor import start_monitor_thread

start_monitor_thread('runtime_lib')

while 1:
    time.sleep(1)
    print(g.roles)
    for role in g.roles:
       try:
           g.roles[role].play() 
       except Exception as e:
           print("Could not play: {}".format(e))
           

