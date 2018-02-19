from inotify_simple import INotify, flags
import importlib
import threading
import os
import sys
import inspect
from libs import g
import time

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
        self.lastrun=0          # get rid of this ugly hack


    def start_inotify(self):
        self.inotify = INotify()
        watch_flags = flags.CLOSE_WRITE | flags.DELETE
        wd = self.inotify.add_watch(self.path + '/', watch_flags)

    # find a way to avoid replicate inotify events:
    # https://askubuntu.com/questions/710422/why-do-inotify-events-fire-more-than-once
    # class signatures?
    # 0.4 s seems to be enough to avoid error on automated testing. Let 1 second
    # Class updates should be a careful process. Probably there will be no usecase where update should be
    # in millisecond delay... but this solution is just ugly. Fix it.
    # TODO: fix the time bounding delay.
    def add_roles(self, module_name):
        now = time.time()
        if now - self.lastrun > 1:
            self.lastrun = now
            try:
                if module_name in sys.modules:
                    pkg = importlib.reload(sys.modules[module_name])
                else:
                    pkg = importlib.import_module(module_name)
            except Exception as ex:
                print('Module could not be imported, {}'.format(ex))
                pkg = None

            if pkg is not None:
                classes = [getattr(pkg, name) for name in dir(pkg)
                           if inspect.isclass(getattr(pkg, name))]
                for c in classes:
                    if c.classtype in g.roles_played_by:
                        for core in g.roles_played_by[c.classtype]:
                            core.roles[c.classtype] = c(instance=core.roles[c.classtype])

    def run(self):
        while True:
            for event in self.inotify.read():
                if event.name.endswith('.py'):
                    module_name = self.path + '.' + os.path.splitext(event.name)[0]
                    for flag in flags.from_mask(event.mask):
                        if flag.name == 'CLOSE_WRITE':
                            self.add_roles(module_name)
                        if flag.name == 'DELETE':
                            # TODO: handle unload from roles / modules
                            pass
