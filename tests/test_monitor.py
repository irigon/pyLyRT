import unittest
import time
import sys, os
sys.path.insert(0, os.path.abspath('.'))

# What can be tested:
#   * On monitor call
#       * the thread is created
#       * create a file with extension .py
#           * if the file contains valid python code (e.g a class)
#               * if the class is being loaded for the first time:
#                   * the class should be loaded to g
#               * otherwise, the class will be reloaded, updating g code
#           * if the file contains invalid python code, throw exception, log and continue without breaking the program
#           * if the signature is one of the builtins ('__xxx__'), log a warning and ignore the request
#       * create a file with extension != .py, nothing happens

class TestMonitor(unittest.TestCase):
    from libs import g
    print(sys.path)

    def test_start_monitor(self):
        from libs.monitor import start_monitor_thread
        start_monitor_thread('runtime_lib')
        for i in range(3):
            time.sleep(1)
