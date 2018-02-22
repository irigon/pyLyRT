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
        self.known_modules=set()

    def start_inotify(self):
        self.inotify = INotify()
        watch_flags = flags.CLOSE_WRITE | flags.DELETE
        self.wd = self.inotify.add_watch(self.path + '/', watch_flags)

    def run(self):
        self.alive = True
        try:
            while self.alive == True:
                for event in self.inotify.read():
                    if self.alive == False:
                        break
                    if event.name.endswith('.py'):
                        print('Cheguei em event.name. Name: {}, knownmodules:{}'.format(event.name, self.known_modules))
                        module_name = self.path + '.' + os.path.splitext(event.name)[0]
                        for flag in flags.from_mask(event.mask):
                            if flag.name == 'CLOSE_WRITE':
                                if event.name not in self.known_modules:
                                    print('Primeira vez em known modules ({})'.format(self.known_modules))
                                    self.known_modules.add((event.name))
                                    self.register.add_module(module_name)
                            if flag.name == 'DELETE':
                                # TODO: handle unload from roles / modules
                                pass
        finally:
            self.inotify.rm_watch(self.wd)

    def stop(self):
        self.alive=False
        self.add_mock_file()
        self.remove_mock_file()
        # send a mock event to inotify in order to avoid the need to kill the thread
        self.join()

    def add_mock_file(self):
        with open('{}/___mocking_file.py'.format(self.path), 'w') as f:
            f.write("Mock")

    def remove_mock_file(self):
        os.remove('{}/___mocking_file.py'.format(self.path))

