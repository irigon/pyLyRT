import unittest
from libs import reg
import app.company_example as ce


class TestInvokeCompartment(unittest.TestCase):

    def setUp(self):
        self.dbname = 'tmpDB'
        self.myreg = reg.Reg(self.dbname)


    def tearDown(self):
        self.myreg.conn.close()


    def test_call_work(self):
        company = ce.Company(100000, id='company')
        bob = ce.Person('bob', 10000, id='bob')
        developer = ce.Developer(100, id='developer')
        taxpayer = ce.TaxPayer(id='taxpayer')

        self.myreg.bind(company, bob, bob, developer, 'PPR')
        self.myreg.invokeRole(company, bob, 'pay')
        self.myreg.bind(company, bob, developer, taxpayer, 'RPR')
        self.myreg.invokeRole(company, bob, 'pay')
        self.myreg.invokeRole(company, bob, 'swimm')
