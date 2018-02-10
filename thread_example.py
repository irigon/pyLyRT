#!/usr/bin/python3

import _thread
import time
import sys

global roles
roles=[]

def start_monitor_thread():
   try:
      _thread.start_new_thread( print_time, ("Thread-1", 2, ) )
   except:
      print ("Error: unable to start thread")

# Define a function for the thread
def print_time( threadName, delay):
   global roles
   count = 0
   while count < 5:
      if count == 3:
          print('import lib')
          from runtime_lib import me
          print(sys.modules)
      count +=1
      time.sleep(delay)

start_monitor_thread()

while 1:
    time.sleep(1)
    #print('dir from main: {}, roles: {}'.format(dir(), roles))
    print('main:{}'.format(sys.modules))
