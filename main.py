#!/usr/bin/python3

from libs import reg, g
from libs.monitor import start_monitor_thread
import app.company_example as ce

monitor = start_monitor_thread('runtime_lib')

myreg = reg.Reg('roles_db')

company = ce.Company(100000, id='company')
bob = ce.Person('bob', 10000, id='bob')
developer = ce.Developer(100, id='developer')
taxpayer = ce.TaxPayer(id='taxpayer')

g.players['bob'] = bob

myreg.bind(company, bob, bob, developer, 'PPR')
myreg.invokeRole(company, bob, 'pay')
myreg.bind(company, bob, developer, taxpayer, 'RPR')
myreg.invokeRole(company, bob, 'pay')
myreg.unbind('bob', 'taxpayer')
myreg.invokeRole(company, bob, 'pay')



