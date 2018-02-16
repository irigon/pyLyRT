from inotify_simple import INotify, flags
import importlib
import threading
import os
import sys

from libs import g

def start_monitor_thread(path_to_runtime_lib):
    m = Monitor(path_to_runtime_lib)
    m.daemon = True                 # the thread should stop if the main thread stop
    m.start_inotify()
    try:
        m.start()
    except:
        print ("Error: unable to start thread")
    return m



class Monitor(threading.Thread):
    def __init__(self, path_to_runtime_lib):
        threading.Thread.__init__(self)
        self.path = path_to_runtime_lib

    def start_inotify(self):
        self.inotify = INotify()
        watch_flags = flags.CLOSE_WRITE | flags.DELETE
        wd = self.inotify.add_watch(self.path + '/', watch_flags)

    def run(self):
        while True:
            for event in self.inotify.read():
                if event.name.endswith('.py'):
                    module_name = self.path + '.' + os.path.splitext(event.name)[0]
                    for flag in flags.from_mask(event.mask):
                        if flag.name == 'CLOSE_WRITE':
                            try:
                                if module_name in sys.modules:
                                    i = importlib.reload(sys.modules[module_name])
                                else:
                                    i = importlib.import_module(module_name)
                            except Exception as ex:
                                i = None

                            if i is not None:
                                c = {x: y for x, y in i.__dict__.items() if not x.startswith('__')}
                                g.nspace.update(c)

                        if flag.name == 'DELETE':
                            # TODO: handle unload from roles / modules
                            pass
