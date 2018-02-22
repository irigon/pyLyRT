import unittest
import os, time, sys
from importlib import reload
sys.path.insert(0, os.path.abspath('.'))
from libs import monitor
from libs import reg


class TestInvokeCompartment(unittest.TestCase):

    def setUp(self):
        from libs import g
        self.g = reload(g)

        from tests import helpers
        self.helper = reload(helpers)

        self.dbname = 'tmpDB'
        self.myreg = reg.Reg(self.dbname)


    def tearDown(self):
        self.helper.remove_tmp_files()
        self.myreg.conn.close()
        self.monitor.stop()

    def test1(self):
        self.monitor = monitor.start_monitor_thread('runtime_lib', self.myreg)

    def test2(self):
        self.monitor = monitor.start_monitor_thread('runtime_lib', self.myreg)

    def test3(self):
        self.monitor = monitor.start_monitor_thread('runtime_lib', self.myreg)
        #while True:
        #    time.sleep(1)
