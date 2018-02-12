from inotify_simple import INotify, flags
import importlib
import _thread
import os
import sys

from libs import g


def start_monitor_thread(path_to_runtime_lib):
   try:
      _thread.start_new_thread( monitor, (path_to_runtime_lib, ) )
   except:
      print ("Error: unable to start thread")

# Define a function for the thread
def monitor(path_to_runtime_lib):
   print(os.getcwd())
   inotify = INotify()
   watch_flags = flags.CREATE | flags.DELETE | flags.DELETE_SELF
   wd = inotify.add_watch(path_to_runtime_lib + '/', watch_flags)
   while True:
      for event in inotify.read():
         if event.name.endswith('.py'):
            module_name = path_to_runtime_lib + '.' + os.path.splitext(event.name)[0]
            for flag in flags.from_mask(event.mask):
               print('{}, Flag name: {}, Module Name: {}  '.format(event, flag.name, module_name))
            try:
                if module_name in sys.modules:
                    i = importlib.reload(sys.modules[module_name])
                else:
                    i = importlib.import_module(module_name)
            except Exception as e:
                    print('Module {} could not be loaded'.format(module_name))
                    i = None
            if i is not None:
                c = { x:y for x,y in i.__dict__.items() if not x.startswith('__') }
                g.roles.update(c)




if __name__ == '__main__':
    monitor('../runtime_lib')

