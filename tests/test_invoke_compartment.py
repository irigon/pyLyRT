import unittest
from libs import reg
import app.company_example as ce
from tests import helpers
import os, time
from importlib import reload



class TestInvokeCompartment(unittest.TestCase):

    def setUp(self):
        from libs import g
        self.g = reload(g)
        from libs import monitor
        self.m = reload(monitor)

        self.dbname = 'tmpDB'
        self.myreg = reg.Reg(self.dbname)

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
        self.new_role = '''from libs import rop
import uuid
class Developer(rop.Role):
    classtype = 'developer'
    
    def __init__(self, salary=200, id='developer', instance=None):
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
        self.monitor = self.m.start_monitor_thread('runtime_lib', self.myreg)

        filepath = os.path.abspath('.') + '/runtime_lib/test0.py'

        company = ce.Company(100000, id='company')
        bob = ce.Person('bob', 10000, id='bob')
        alice = ce.Person('alice', 10000, id='alice')
        self.myreg.add_role(ce.Developer)
        bob_developer = self.g.nspace['developer'](100, id='developer')
        self.myreg.bind(company, bob, bob, bob_developer, 'PPR')
        self.assertEquals(1.2, self.myreg.invokeRole(company, bob, 'pay'))

        # create file
        helpers.create_file(self.new_role, filepath)
        time.sleep(0.2)
        # alice will be bound to the "new" role, that pays 20 per coffee
        alice_developer = self.g.nspace['developer'](100, id='developer')
        self.myreg.bind(company, alice, alice, alice_developer, 'PPR')
        self.assertEquals(20, self.myreg.invokeRole(company, alice, 'pay'))

    def test_update_role_with_state(self):
        self.new_role = '''from libs import rop
import uuid
class Developer(rop.Role):
    classtype = 'developer'

    def __init__(self, salary=100, id='developer', instance=None):
        if instance is not None:
            self.uuid = instance.uuid
            self.salary = instance.salary + 100
            print('Instance.savings: {}'.format(instance.savings))
            self.savings = instance.savings 
        else:
            self.salary = instance.salary
            self.uuid = uuid.uuid1() if id is None else id
            self.savings = 0
        super().__init__(self.uuid)

    def getPaid(self):
        self.savings=self.savings+self.salary
        print('receiving money')

    def work(self):
        print('work the whole month...')

    def pay(self):
        print('I just wish myself coffee')
        return 20

    def show_savings(self):
        return 'My savings_method (version 2) {}'.format(self.savings)

'''
        self.monitor = self.m.start_monitor_thread('runtime_lib', self.myreg)

        filepath = os.path.abspath('.') + '/runtime_lib/test1.py'
        print(' ------------ test_update_role_with_state')
        company = ce.Company(100000, id='company')
        bob = ce.Person('bob', 10000, id='bob')
        dev = ce.Developer(salary=1000, id='developer')
        self.myreg.add_role(ce.Developer)
        self.myreg.bind(company, bob, bob, dev, 'PPR')
        self.assertEquals(bob.roles['developer'].savings, 0)

        self.myreg.invokeRole(company, bob, 'getPaid')
        curr_salary = bob.roles['developer'].salary
        self.assertEquals(bob.roles['developer'].savings, curr_salary)

        # create file
        helpers.create_file(self.new_role, filepath)
        time.sleep(0.5)

        # bob still have the same money into his savings:
        self.assertEquals(bob.roles['developer'].savings, curr_salary)
        print('verificou salario')

        # bob was bound to the "new" role, that pays his old salary + 100 bucks
        self.myreg.invokeRole(company, bob, 'getPaid')
        self.assertEquals(bob.roles['developer'].savings, 2*curr_salary + 100)
