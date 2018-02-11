from inotify_simple import INotify, flags
import importlib
import os
import sys

from libs import g

DYN_LIB_DIR='runtime_lib'

# Define a function for the thread
def monitor(name, delay):
   inotify = INotify()
   watch_flags = flags.CREATE | flags.DELETE | flags.DELETE_SELF
   wd = inotify.add_watch(DYN_LIB_DIR+'/', watch_flags)
   while True:
      for event in inotify.read():
         if event.name.endswith('.py'):
            module_name = DYN_LIB_DIR + '.' + os.path.splitext(event.name)[0]
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
