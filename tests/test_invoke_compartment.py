import unittest
from libs import reg
import app.company_example as ce
from tests import helpers
import os, time
from importlib import reload



class TestInvokeCompartment(unittest.TestCase):

    def setUp(self):
        self.dbname = 'tmpDB'
        self.myreg = reg.Reg(self.dbname)

        from libs import g
        self.g = reload(g)

    def tearDown(self):
        helpers.remove_tmp_files()
        self.myreg.conn.close()


    # Create a user, a compartment and a role
    # call the role and verify that it worked
    def test_call_work(self):
        company = ce.Company(100000, id='company')
        bob = ce.Person('bob', 10000, id='bob')
        developer = ce.Developer(100, id='developer')

        self.myreg.bind(company, bob, bob, developer, 'PPR')
        self.assertEquals(1.2, self.myreg.invokeRole(company, bob, 'pay'))

    # Create a user, a compartment and a role
    # call the role and verify that it worked
    # loads the role at run time
    # create another user using the same role
    # verify that it changed
    def test_runtime_change(self):
        new_role = '''from libs import rop
import uuid
class Developer(rop.Role):
    classtype = 'developer'
    
    def __init__(self, salary=200, id='developer'):
        self.salary = salary
        self.uuid = uuid.uuid1() if id is None else id
        super().__init__(self.uuid)
    
    def getPaid(self):
        pass
    
    def work(self):
        print('Typing like I could program...')
    
    def pay(self):
        print('I just pay for golden coffee')
        return 20
'''
        from libs.monitor import start_monitor_thread
        self.monitor = start_monitor_thread('runtime_lib')

        filepath = os.path.abspath('.') + '/runtime_lib/test0.py'

        company = ce.Company(100000, id='company')
        bob = ce.Person('bob', 10000, id='bob')
        alice = ce.Person('alice', 10000, id='alice')
        self.g.nspace['developer'] = ce.Developer(100, id='developer')

        self.myreg.bind(company, bob, bob, self.g.nspace['developer'], 'PPR')
        self.assertEquals(1.2, self.myreg.invokeRole(company, bob, 'pay'))

        # create file
        helpers.create_file(new_role, filepath)
        time.sleep(0.2)
        # alice will be bound to the "new" role, that pays 20 per coffee

        self.myreg.bind(company, alice, alice, self.g.nspace['developer'], 'PPR')
        self.assertEquals(20, self.myreg.invokeRole(company, alice, 'pay'))

