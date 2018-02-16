#!/usr/bin/python3

import time
from libs import g
from libs.monitor import start_monitor_thread
import app.company_example as ce

monitor = start_monitor_thread('runtime_lib')

ely = ce.Person('Ely', 13000)

ely.scream()

while 1:
    time.sleep(1)
    print(g.nspace)
    print('Monitor is alive: {}'.format(monitor.is_alive()))
    for one_class in g.nspace:
       try:
           g.nspace[one_class].play()
       except Exception as e:
           print("Could not play: {}".format(e))
           

