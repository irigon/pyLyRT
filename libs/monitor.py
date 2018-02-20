from inotify_simple import INotify, flags
import threading
import os

def start_monitor_thread(path_to_runtime_lib, register):
    m = Monitor(path_to_runtime_lib, register)
    m.daemon = True                 # the thread should stop if the main thread stop
    m.start_inotify()
    try:
        m.start()
    except:
        print ("Error: unable to start thread")
    return m

class Monitor(threading.Thread):
    def __init__(self, path_to_runtime_lib, register):
        threading.Thread.__init__(self)
        self.path = path_to_runtime_lib
        self.lastrun=0          # get rid of this ugly hack
        self.register=register


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
                            #try:
                            self.register.add_module(module_name)
                            #except Exception as e:
                            #    print('Problem loading the class. {}'.format(e))
                        if flag.name == 'DELETE':
                            # TODO: handle unload from roles / modules
                            pass
