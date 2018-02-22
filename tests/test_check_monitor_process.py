import unittest
from libs import reg
import os, time
from importlib import reload
from libs import monitor


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
