import unittest
from importlib import reload
import sys, os
sys.path.insert(0, os.path.abspath('.'))
from libs import g
from libs import reg

class TestInvokeCompartment(unittest.TestCase):

    def setUp(self):

        from tests import helpers
        self.helper = reload(helpers)

        self.dbname = 'tmpDB'
        self.myreg = reg.Reg(self.dbname)


    def tearDown(self):
        self.helper.remove_tmp_files()
        self.myreg.conn.close()
        g.clear()

    def test_creating_something_in_g(self):
        self.assertEquals(len(g.nspace), 0)
        g.nspace['fruit']='bananas'
        self.assertEquals(len(g.nspace), 1)

    # note, we need to call self.g.clear, since the update is not done automatically
    def test_verifying_env_is_NEEDS_TO_BE_RESTARTED(self):
        self.assertEquals(len(g.nspace), 0)
