#!/usr/bin/python3

from libs import reg, g
from libs.monitor import start_monitor_thread
import app.company_example as ce
import time

myreg = reg.Reg('roles_db')
monitor = start_monitor_thread('runtime_lib', myreg)

company = ce.Company(100000, id='company')
bob = ce.Person('bob', 10000, id='bob')
for role in [ce.Developer, ce.TaxPayer]:
    myreg.add_role(role)

developer = g.nspace['developer'](100, id='developer')
taxpayer = g.nspace['taxpayer'](id='taxpayer')

myreg.bind(company, bob, bob, developer, 'PPR')
myreg.invokeRole(company, bob, 'pay')
myreg.bind(company, bob, developer, taxpayer, 'RPR')
myreg.invokeRole(company, bob, 'pay')
myreg.unbind('bob', 'taxpayer')
myreg.invokeRole(company, bob, 'pay')


while True:
    time.sleep(1)
    myreg.invokeRole(company, bob, 'work')
    myreg.invokeRole(company, bob, 'getPaid')
    print('Hi, I am {}. {}'.format(bob.name, myreg.invokeRole(company, bob, 'show_savings')))
