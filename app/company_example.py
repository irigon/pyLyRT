from libs import g
from libs import rop
import uuid

############################### -- CORE CLASSES
class Person(rop.Player):
    classtype = 'person'

    def __init__(self, name, saving, id=None):
        self.name = name
        self.saving = saving
        self.roles={}   # this should be probably and attribute of the father class player
        self.uuid = uuid.uuid1() if id is None else id
        super().__init__()

############################### -- COMPARTMENT CLASSES
class Company(rop.Compartment):
    classtype = 'company'

    def __init__(self, revenue, tax=0.2, id=None):
        self.revenue = revenue
        self.tax = tax
        self.uuid = uuid.uuid1() if id is None else id
        self.players={} # this should be probably and attribute of the father class compartment
        super().__init__()

    def taxToBePaid(self):
        pass

    def deductRevenue(self, amount):
        pass

class TaxDepartment(rop.Compartment):
    classtype = 'taxdepartment'

    def __init__(self, revenue, id=None):
        self.uuid = uuid.uuid1() if id is None else id
        self.players={} # this should be probably and attribute of the father class compartment
        super().__init__()

    def getRevenue(self):
        pass

    def setRevenue(self):
        pass

############################### -- ROLE CLASSES
class Freelance(rop.Role):
    classtype = 'freelance'

    def __init__(self, wage, tax=0.1, id=None):
        self.wage = wage
        self.tax = tax
        self.uuid = uuid.uuid1() if id is None else id
        self.roles = {}
        super().__init__(self.uuid)

    def earn(self, amount):
        pass

    def taxToBePaid(self):
        pass

class TaxEmployee(rop.Role):
    classtype = 'taxemployee'

    def __init__(self, id=None):
        self.uuid = uuid.uuid1() if id is None else id
        super().__init__(self.uuid)

    def collectTax(self):
        pass

class TaxPayer(rop.Role):
    classtype = 'taxpayer'

    def __init__(self, id=None):
        self.uuid = uuid.uuid1() if id is None else id
        super().__init__(self.uuid)

    def pay(self):
        print('Paying taxes')

class Developer(rop.Role):
    classtype = 'developer'

    def __init__(self, salary, id=None):
        self.salary = salary
        self.uuid = uuid.uuid1() if id is None else id
        self.savings=0
        super().__init__(self.uuid)

    def getPaid(self):
        self.savings=self.savings+self.salary
        print('receiving money')

    def work(self):
        print('work the whole month...')

    def pay(self):
        print('Paying coffee')
        return 1.2

    def show_savings(self):
        return 'So far I saved {}'.format(self.savings)

class Accountant(rop.Role):
    classtype = 'accountant'

    def __init__(self, salary, id=None):
        self.salary = salary
        self.uuid = uuid.uuid1() if id is None else id
        super().__init__(self.uuid)

    def paySalary(self):
        pass