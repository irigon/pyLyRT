#!/usr/bin/python3

from libs import reg, g
from libs.monitor import start_monitor_thread
import app.company_example as ce
import time

myreg = reg.Reg('roles_db')
monitor = start_monitor_thread('runtime_lib')

company = ce.Company(100000, id='company')
bob = ce.Person('bob', 10000, id='bob')
g.nspace['developer'] = ce.Developer(100, id='developer')
g.nspace['taxpayer'] = ce.TaxPayer(id='taxpayer')

g.players['bob'] = bob

myreg.bind(company, bob, bob, g.nspace['developer'], 'PPR')
myreg.invokeRole(company, bob, 'pay')
myreg.bind(company, bob, g.nspace['developer'], g.nspace['taxpayer'], 'RPR')
myreg.invokeRole(company, bob, 'pay')
myreg.unbind('bob', 'taxpayer')
myreg.invokeRole(company, bob, 'pay')


while True:
    time.sleep(0.1)
    myreg.invokeRole(company, bob, 'pay')



