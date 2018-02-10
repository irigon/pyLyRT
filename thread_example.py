#!/usr/bin/python3

import _thread
import time
import sys
import os
import importlib
from inotify_simple import INotify, flags


DYN_LIB_DIR='runtime_lib'
global roles
roles={}

def start_monitor_thread():
   try:
      _thread.start_new_thread( monitor, ("Thread-1", 2, ) )
   except:
      print ("Error: unable to start thread")

# Define a function for the thread
def monitor( threadName, delay):
   global roles
   inotify = INotify()
   watch_flags = flags.CREATE | flags.DELETE | flags.DELETE_SELF
   wd = inotify.add_watch(DYN_LIB_DIR+'/', watch_flags)
   while True:
      for event in inotify.read():
         if event.name.endswith('.py'):
            module_name = DYN_LIB_DIR + '.' + os.path.splitext(event.name)[0]
            for flag in flags.from_mask(event.mask):
               print('{}, Flag name: {}, Module Name: {}  '.format(event, flag.name, module_name))
            i = importlib.import_module(module_name)
            c = { x:y for x,y in i.__dict__.items() if not x.startswith('__') }
            roles.update(c)
            

start_monitor_thread()

while 1:
    time.sleep(1)
    print(roles)
    for role in roles:
       roles[role].play() 

