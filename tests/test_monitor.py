import unittest
import time
import sys, os
from importlib import reload
from tests import helpers


sys.path.insert(0, os.path.abspath('.'))
from nose.tools import raises

# What can be tested:
#   * On monitor call
#       * the thread is createdf
#       * create a file with extension .py ** (notes 1)
#           * if the file contains valid python code (e.g a class)
#               * if the class is being loaded for the first time:
#                   * the class should be loaded to g
#               * otherwise, the class will be reloaded, updating g code
#           * otherwise (file contains invalid python code), throw exception, continue without breaking the program
#           * if the signature is one of the builtins ('__xxx__'), log a warning and ignore the request
# TODO      * create a file with extension != .py, nothing happens
# TODO      * add logs

# Notes 1) we tried at first use the same file for all tests
#   however when both tests -- test_valid_input_code.py && test_reload_code -- were executed in parallel, the tests failed.
#   even though I remove the files and recreated them, the test_valid_input_code ended with 2 objects in the "g.nspace" dict
#   The only reasonably explanation is that test_reload_code ran before test_valid_input_code and did not clean the file (effectively remove its content) when the
#   signal CLOSE_WRITE was triggered


invalid_python_code= '''class Doug:
    def play):
        print('hey')
'''

valid_python_code_1='''class DougValid:
    classtype="DougValid"
    def play():
        print('Doug valid class plays method')
'''

valid_python_code_2='''class NewClass2:
    classtype="DougValid"
    def plays():
        print('Doug class plays method')
'''

class TestMonitor(unittest.TestCase):

    def setUp(self):
        from libs import g
        self.g = reload(g)
        self.filepath = os.path.abspath('.') + '/runtime_lib/test0.py'
        helpers.remove_tmp_files()

        from libs.monitor import start_monitor_thread
        self.monitor = start_monitor_thread('runtime_lib')

    def tearDown(self):
        helpers.remove_tmp_files()

    # verify if the thread runs
    def test_start_monitor(self):
        time.sleep(0.5)
        self.assertTrue(self.monitor.is_alive() == True)

    # create an invalid file with extension .py under /runtime_lib
    # verify that the code does not break
    @raises
    def test_invalid_input_code(self):
        helpers.create_file(invalid_python_code, self.filepath)
        time.sleep(0.5)
        self.assertTrue(self.monitor.is_alive() == True)

    # @the object is not held in g.nspace anymore, therefore this test makes less sense
    # create a valid file with extention .py under /runtime_lib
    # verify that the code is loaded to g.nspace
    #def test_valid_input_code(self):
    #    helpers.create_file(valid_python_code_1, self.filepath)
    #    time.sleep(0.2)
    #    self.assertTrue(self.monitor.is_alive() == True)
    #    self.assertEqual(ns_size, 1)

    def test_reload_code(self):
        helpers.create_file(valid_python_code_1, 'runtime_lib/test1.py')
        helpers.create_file(valid_python_code_2, 'runtime_lib/test1.py')
        time.sleep(0.2)
        self.assertTrue(self.monitor.is_alive() == True)


    def test_ignore_files_with_extension_other_then_py(self):
        helpers.create_file(valid_python_code_1, 'runtime_lib/test2.xx')
        time.sleep(0.2)
        self.assertTrue(self.monitor.is_alive() == True)
        self.assertEqual(len(self.g.nspace), 0)

