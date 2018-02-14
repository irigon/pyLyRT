from libs import g

############################### -- CORE CLASSES
class Person:
    def Person(self, name, saving):
        self.name = name
        self.saving = saving

############################### -- COMPARTMENT CLASSES
class Company:
    def Company(self, revenue, tax=0.2):
        self.revenue = revenue
        self.tax = tax

    def taxToBePaid(self):
        pass

    def deductRevenue(self, amount):
        pass

class TaxDepartment:
    def TaxDepartment(self, revenue):
        pass

    def getRevenue(self):
        pass

    def setRevenue(self):
        pass

############################### -- ROLE CLASSES
class Freelance:
    def Freelance(self, wage, tax=0.1):
        self.wage = wage
        self.tax = tax

    def earn(self, amount):
        pass

    def taxToBePaid(self):
        pass

class TaxEmployee:
    def TaxEmployee(self):
        pass

    def collectTax(self):
        pass

class TaxPayer:
    def TaxPayer(self):
        pass

    def pay(self):
        pass

class Developer:
    def Developer(self, salary):
        self.salary = salary

    def getPaid(self):
        pass

    def work(self):
        pass

class Accountant:
    def Accountant(self, salary):
        self.salary = salary

    def paySalary(self):
        pass