import unittest
from nose.tools import raises
from sqlite3 import IntegrityError, OperationalError
import sys, os

sys.path.insert(0, os.path.abspath('.'))
from app import company_example as ce
from libs import reg
from libs import rop
from libs import g

db_name = 'roles_db'

class TestDB(unittest.TestCase):

    def setUp(self):
        self.myreg = reg.Reg(db_name)
        self.mock_objs = {}
        for role in [ ce.Freelance, ce.TaxPayer, ce.TaxEmployee, ce.Developer, ce.Accountant ]:
            self.myreg.add_role(role)

    def tearDown(self):
        self.myreg.conn.close()

    def test_db_creation(self):
        args = "CompartmentId text, CorePlayerId text, PlayerId text, RoleId text, RelationType text, " \
               "BindingLevel integer, BindingSequence integer"
        mydb = reg.Reg('tmp_db')
        self.assertTrue(mydb.conn is not None)
        mydb.conn.close()

    # update levels and sequences
    def test_db_insert_valid_relation(self):
        rows = [('company', 'bob'    , 'bob'      , 'developer' , 'PPR', 1, 1),
                ('company', 'alice'  , 'alice'    , 'accountant', 'PPR', 1, 2),
                ('company', 'ely'    , 'ely'      , 'freelance' , 'PPR', 1, 1),
                ('company', 'ely'    , 'freelance', 'taxpayer'  , 'RPR', 2, 1),
                ('tax'    , 'company', 'company'  , 'taxpayer'  , 'PPR', 1, 1)]
        self.myreg.conn.executemany('INSERT INTO {} VALUES(?, ?, ?, ?, ?, ?, ?)'.format(db_name), rows)

        num_rows =  self.myreg.conn.execute('select count(*) from roles_db')
        self.assertEqual(num_rows.fetchone()[0], 5)

    @raises(OperationalError) # last field missing
    def test_db_insert_missing_fields_invalid_relation(self):
        self.myreg.conn.execute("INSERT INTO roles_db VALUES('company', 'ely', 'ely' , \
                                                              'freelance', 'PPR', 1)")

    @raises(IntegrityError) # on the first line, the last field is a string; on the second, the first is a number.
    def test_db_insert_invalid_type(self):
        self.myreg.conn.execute("INSERT INTO roles_db VALUES('company', 'ely', 'ely' , \
                                                              'freelance', 'PPR', 1, 'me')")
        self.myreg.conn.execute("INSERT INTO roles_db VALUES(1, 'ely', 'ely' , \
                                                              'freelance', 'PPR', 1, 1)")


    ## for the following tests I will consider the following structure:
    # [a, b, c..., j] are objects. A is the core, the other are roles
    # a(m0)     -- b(m1, m2, m3)
    #           -- c(m2)
    #               -- d(m1)
    #               -- e
    #                   -- g
    #                       -- h(m3)
    #                       -- i(m3, m4)
    #               -- f
    #                   -- j


    def setupDBforTesting(self):
        class Dummy:
            pass

        def dummyFunc():
            pass

        rows = [('company', 'a', 'a', 'b', 'PPR', 1, 1),
                ('company', 'a', 'a', 'c', 'PPR', 1, 2),
                ('company', 'a', 'c', 'd', 'RPR', 2, 1),
                ('company', 'a', 'c', 'e', 'RPR', 2, 2),
                ('company', 'a', 'c', 'f', 'RPR', 2, 3),
                ('company', 'a', 'e', 'g', 'RPR', 3, 1),
                ('company', 'a', 'g', 'h', 'RPR', 4, 1),
                ('company', 'a', 'g', 'i', 'RPR', 4, 2),
                ('company', 'a', 'f', 'j', 'RPR', 3, 2)]
        for i in ['a','b','c','d','e','f','g','h','i','j']:
            self.mock_objs[i]=Dummy()

        self.mock_objs['a'].m0=dummyFunc()
        self.mock_objs['b'].m1=dummyFunc()
        self.mock_objs['b'].m2=dummyFunc()
        self.mock_objs['b'].m3=dummyFunc()
        self.mock_objs['c'].m2=dummyFunc()
        self.mock_objs['d'].m1=dummyFunc()
        self.mock_objs['h'].m3=dummyFunc()
        self.mock_objs['i'].m3=dummyFunc()
        self.mock_objs['i'].m4=dummyFunc()

        return(rows, self.mock_objs)

    def feed_db_and_select_ordered(self, rows):
        self.myreg.conn.executemany('INSERT INTO roles_db VALUES(?, ?, ?, ?, ?, ?, ?)', rows)
        ordered_list = self.myreg.conn.execute('SELECT * FROM ' + db_name + \
                                            ' order by BindingLevel DESC,BindingSequence DESC')
        return ordered_list

    def select_current_context_for_method(self, rows, method_name):
        ordered_list = self.feed_db_and_select_ordered(rows)
        return next((x[3] for x in ordered_list.fetchall() if hasattr(self.mock_objs[x[3]],method_name) is not False), None)

    def test_db_valid_query(self):
        rows, objects = self.setupDBforTesting()
        ordered_list = self.feed_db_and_select_ordered(rows)
        self.assertEqual(9, len(ordered_list.fetchall()))

    # searching for leaf (m4)
    def test_db_valid_simple_search_item_present(self):
        rows, objects = self.setupDBforTesting()
        ordered_list = self.feed_db_and_select_ordered(rows)
        # TODO: use generators (with fetchmany) instead of fetchall
        # the third in the tuple is the role
        val = self.select_current_context_for_method(rows, 'm4')
        self.assertTrue(val is not None)

    def test_db_valid_simple_search_item_not_present(self):
        rows, objects = self.setupDBforTesting()
        val = self.select_current_context_for_method(rows, 'm100')
        self.assertTrue(val is None)

    # core is not going to be found, since this search method go just through the roles
    def test_db_valid_search_method_in_core(self):
        rows, objects = self.setupDBforTesting()
        val = self.select_current_context_for_method(rows, 'm0')
        self.assertEquals(val, None)
        self.assertTrue(hasattr(objects['a'], 'm0'))

    def test_db_valid_search_same_index_different_deep(self):
        rows, objects = self.setupDBforTesting()
        val = self.select_current_context_for_method(rows, 'm1')
        self.assertEquals(val, 'd')

    def test_db_valid_search_same_level_different_sequence(self):
        rows, objects = self.setupDBforTesting()
        val = self.select_current_context_for_method(rows, 'm2')
        self.assertEquals(val, 'c')

    def test_db_valid_search_different_level_and_sequence(self):
        rows, objects = self.setupDBforTesting()
        val = self.select_current_context_for_method(rows, 'm3')
        self.assertEquals(val, 'i')

    # we assume that a bind has always a role and a compartment to it
    # we can create a dummy compartment and a dummy role to use in case none should be there
    # every insert, we must assure that the sequence becomes the greates of that level
    #def test_db_valid_bind_person_to_company(self):
    #    company = ce.Company(1000, id='company')
    #    pedro = ce.Person('bob', 10, id='bob')
    #    self.myreg.bind(company, pedro)
    #
    #   self.assertEquals(len(company.players), 1)
    #    self.assertTrue(pedro.uuid in company.players)

    def test_bind_role_to_person(self):
        company = ce.Company(100000, id='company')
        bob = ce.Person('bob', 10000, id='bob')
        developer = g.nspace['developer'](100, id='developer')
        self.myreg.bind(company, bob, bob, developer, 'PPR')
        line = self.myreg.conn.execute("SELECT * FROM {} ".format(self.myreg.name)).fetchall()[0]
        self.assertEquals(('company', 'bob', 'bob', 'developer', 'PPR', 1, 1), line)

    def test_second_bind_role_to_person(self):
        company = ce.Company(100000, id='company')
        bob = ce.Person('bob', 10000, id='bob')
        developer = ce.Developer(100, id='developer')
        accountant = ce.Accountant(100, id='accountant')
        self.myreg.bind(company, bob, bob, developer, 'PPR')
        self.myreg.bind(company, bob, bob, accountant, 'PPR')
        line = self.myreg.conn.execute("SELECT * FROM {} WHERE CorePlayerId='{}' and PlayerId='{}' \
                                        order by BindingLevel DESC,BindingSequence DESC".format \
                                         (self.myreg.name, bob.uuid, bob.uuid)).fetchall()[0]
        self.assertEquals(('company', 'bob', 'bob', 'accountant', 'PPR', 1, 2), line)

    def test_second_bind_roles_as_in_paper(self):
        company = ce.Company(100000, id='company')
        tax = ce.TaxDepartment(100000, id='tax')
        bob = ce.Person('bob', 10000, id='bob')
        ely = ce.Person('ely', 10000, id='ely')
        developer = ce.Developer(100, id='developer')
        accountant = ce.Accountant(100, id='accountant')
        freelance = ce.Freelance(100, id='freelance')
        taxpayer = ce.TaxPayer(id='taxpayer')
        self.myreg.bind(company, bob, bob, developer, 'PPR')
        self.myreg.bind(company, bob, bob, accountant, 'PPR')
        self.myreg.bind(company, ely, ely, freelance, 'PPR')
        self.myreg.bind(company, ely, freelance, taxpayer, 'RPR')
        self.myreg.bind(company, company, company, taxpayer, 'PPR')
        table = self.myreg.conn.execute("SELECT * FROM {}  \
                                        order by BindingLevel DESC,BindingSequence DESC".format \
                                         (self.myreg.name)).fetchall()

        table_goal= [('company', 'ely', 'freelance', 'taxpayer', 'RPR', 2, 1),
                    ('company', 'bob', 'bob', 'accountant', 'PPR', 1, 2),
                    ('company', 'bob', 'bob', 'developer', 'PPR', 1, 1),
                    ('company', 'ely', 'ely', 'freelance', 'PPR', 1, 1),
                    ('company', 'company', 'company', 'taxpayer', 'PPR', 1, 1)]
        self.assertEquals(table, table_goal)

    # update levels and sequences
    # verify consistency of the levels and sequences
    def test_db_delete_relation(self):
        pass


class TestFindNextLevel(unittest.TestCase):

    #Create test setup
    #  [a, b, c..., j] are objects. A is the core, the other are roles
    # a         -- b
    #           -- c
    #               -- d
    #               -- e
    #                   -- g
    #                       -- h
    #                       -- i
    #               -- f
    #                   -- j


    def setUp(self):
        self.myreg = reg.Reg(db_name)

        rows = [('company', 'a', 'a', 'b', 'PPR', 1, 1),
                ('company', 'a', 'a', 'c', 'PPR', 1, 2),
                ('company', 'a', 'c', 'd', 'RPR', 2, 1),
                ('company', 'a', 'c', 'e', 'RPR', 2, 2),
                ('company', 'a', 'c', 'f', 'RPR', 2, 3),
                ('company', 'a', 'e', 'g', 'RPR', 3, 1),
                ('company', 'a', 'g', 'h', 'RPR', 4, 1),
                ('company', 'a', 'g', 'i', 'RPR', 4, 2),
                ('company', 'a', 'f', 'j', 'RPR', 3, 2)]
        self.myreg.conn.executemany('INSERT INTO {} VALUES(?, ?, ?, ?, ?, ?, ?)'.format(db_name), rows)

    def test_add_role_to_core(self):
        self.assertEquals(self.myreg.find_next_level_and_sequence('a', 'a', 'X', 'PPR'), (1, 3))

    def test_add_role_to_role_at_tree_begin(self):
        self.assertEquals(self.myreg.find_next_level_and_sequence('a', 'b', 'X', 'RPR'), (2, 4))

    def test_add_role_to_role_at_tree_leaf(self):
        self.assertEquals(self.myreg.find_next_level_and_sequence('a', 'c', 'X', 'RPR'), (2, 4))

    def test_add_role_to_role_when_the_next_level_does_not_exist_beginning(self):
        self.assertEquals(self.myreg.find_next_level_and_sequence('a', 'h', 'X', 'RPR'), (5, 1))

    def test_add_role_to_role_when_the_next_level_does_not_exist_leaf(self):
        self.assertEquals(self.myreg.find_next_level_and_sequence('a', 'i', 'X', 'RPR'), (5, 1))

    def test_add_first_role(self):
        self.assertEquals(self.myreg.find_next_level_and_sequence('A', 'A', 'X', 'PPR'), (1, 1))

    @raises(IndexError)
    def test_throw_exception_when_RPR_on_core_obj(self):
        self.myreg.find_next_level_and_sequence('A', 'A', 'X', 'RPR')

    def tearDown(self):
        self.myreg.conn.close()


class TestUnbind(unittest.TestCase):

    class P_A(rop.Player):
        def __init__(self):
            self.uuid = 'coreA'
            self.roles = {}
            self.classtype = 'P_A'

    class C_A(rop.Compartment):
        def __init__(self):
            self.uuid = 'compartmentA'
            self.players={}
            self.classtype = 'C_A'

    class R_B(rop.Role):
        def __init__(self):
            self.uuid = 'b'
            self.roles={}
            self.classtype = 'R_B'

    class R_C(rop.Role):
        def __init__(self):
            self.uuid = 'c'
            self.roles={}
            self.classtype = 'R_C'

    class R_D(rop.Role):
        def __init__(self):
            self.uuid = 'd'
            self.roles={}
            self.classtype = 'R_D'

    class R_E(rop.Role):
        def __init__(self):
            self.uuid = 'e'
            self.roles={}
            self.classtype = 'R_E'

    class R_F(rop.Role):
        def __init__(self):
            self.uuid = 'f'
            self.roles={}
            self.classtype = 'R_F'

    class R_G(rop.Role):
        def __init__(self):
            self.uuid = 'g'
            self.roles={}
            self.classtype = 'R_G'

    class R_H(rop.Role):
        def __init__(self):
            self.uuid = 'h'
            self.roles={}
            self.classtype = 'R_H'

    class R_I(rop.Role):
        def __init__(self):
            self.uuid = 'i'
            self.roles={}
            self.classtype = 'R_I'

    class R_J(rop.Role):
        def __init__(self):
            self.uuid = 'j'
            self.roles={}
            self.classtype = 'R_J'

    # a         -- b
    #           -- c
    #               -- d
    #               -- e
    #                   -- g
    #                       -- h
    #                       -- i
    #               -- f
    #                   -- j



    def setUp(self):
        self.myreg = reg.Reg(db_name)
        ca = self.C_A()
        pa = self.P_A()
        rb = self.R_B()
        rc = self.R_C()
        rd = self.R_D()
        re = self.R_E()
        rf = self.R_F()
        rg = self.R_G()
        rh = self.R_H()
        ri = self.R_I()
        rj = self.R_J()
        self.myreg.bind(ca, pa, pa, rb, 'PPR')
        self.myreg.bind(ca, pa, pa, rc, 'PPR')
        self.myreg.bind(ca, pa, rc, rd, 'RPR')
        self.myreg.bind(ca, pa, rc, re, 'RPR')
        self.myreg.bind(ca, pa, rc, rf, 'RPR')
        self.myreg.bind(ca, pa, re, rg, 'RPR')
        self.myreg.bind(ca, pa, re, rj, 'RPR')
        self.myreg.bind(ca, pa, rg, rh, 'RPR')
        self.myreg.bind(ca, pa, rg, ri, 'RPR')

        ## basically load the classes to g
        #for player in [pa]:
        #    g.players[player.uuid] = player

        #for compartment in [ca]:
        #    g.compartments[compartment.classtype] = compartment

        #for role in [rb, rc, rd, re, rf, rg, rh, ri, rj]:
        #    g.roles[role.classtype] = role

        self.wholeTable=[('compartmentA', 'coreA', 'coreA', 'b', 'PPR', 1, 1),
                        ('compartmentA', 'coreA', 'coreA', 'c', 'PPR', 1, 2),
                        ('compartmentA', 'coreA', 'c', 'd', 'RPR', 2, 1),
                        ('compartmentA', 'coreA', 'c', 'e', 'RPR', 2, 2),
                        ('compartmentA', 'coreA', 'c', 'f', 'RPR', 2, 3),
                        ('compartmentA', 'coreA', 'e', 'g', 'RPR', 3, 1),
                        ('compartmentA', 'coreA', 'e', 'j', 'RPR', 3, 2),
                        ('compartmentA', 'coreA', 'g', 'h', 'RPR', 4, 1),
                        ('compartmentA', 'coreA', 'g', 'i', 'RPR', 4, 2)]

        resultFetched = self.myreg.conn.execute("SELECT * FROM {} ".format(self.myreg.name)).fetchall()
        # assure the table is right. If something change the test should fail
        self.assertEquals(self.wholeTable, resultFetched)

    def tearDown(self):
        self.myreg.conn.close()

    def test_unbind_b(self):
        self.myreg.unbind('coreA', 'b')
        resultFetched = self.myreg.conn.execute("SELECT * FROM {} ".format(self.myreg.name)).fetchall()
        result_without_b=[('compartmentA', 'coreA', 'coreA', 'c', 'PPR', 1, 2),
                        ('compartmentA', 'coreA', 'c', 'd', 'RPR', 2, 1),
                        ('compartmentA', 'coreA', 'c', 'e', 'RPR', 2, 2),
                        ('compartmentA', 'coreA', 'c', 'f', 'RPR', 2, 3),
                        ('compartmentA', 'coreA', 'e', 'g', 'RPR', 3, 1),
                        ('compartmentA', 'coreA', 'e', 'j', 'RPR', 3, 2),
                        ('compartmentA', 'coreA', 'g', 'h', 'RPR', 4, 1),
                        ('compartmentA', 'coreA', 'g', 'i', 'RPR', 4, 2)]
        self.assertEquals(resultFetched, result_without_b)

    def test_unbind_c(self):
        self.myreg.unbind('coreA', 'c')
        resultFetched = self.myreg.conn.execute("SELECT * FROM {} ".format(self.myreg.name)).fetchall()
        result_without_b=[('compartmentA', 'coreA', 'coreA', 'b', 'PPR', 1, 1)]
        self.assertEquals(resultFetched, result_without_b)

    def test_unbind_d(self):
        self.myreg.unbind('coreA', 'd')
        resultFetched = self.myreg.conn.execute("SELECT * FROM {} ".format(self.myreg.name)).fetchall()
        result_without_d=[('compartmentA', 'coreA', 'coreA', 'b', 'PPR', 1, 1),
                        ('compartmentA', 'coreA', 'coreA', 'c', 'PPR', 1, 2),
                        ('compartmentA', 'coreA', 'c', 'e', 'RPR', 2, 2),
                        ('compartmentA', 'coreA', 'c', 'f', 'RPR', 2, 3),
                        ('compartmentA', 'coreA', 'e', 'g', 'RPR', 3, 1),
                        ('compartmentA', 'coreA', 'e', 'j', 'RPR', 3, 2),
                        ('compartmentA', 'coreA', 'g', 'h', 'RPR', 4, 1),
                        ('compartmentA', 'coreA', 'g', 'i', 'RPR', 4, 2)]
        self.assertEquals(resultFetched, result_without_d)

    def test_unbind_e(self):
        self.myreg.unbind('coreA', 'e')
        resultFetched = self.myreg.conn.execute("SELECT * FROM {} ".format(self.myreg.name)).fetchall()
        result_without_e=[('compartmentA', 'coreA', 'coreA', 'b', 'PPR', 1, 1),
                        ('compartmentA', 'coreA', 'coreA', 'c', 'PPR', 1, 2),
                        ('compartmentA', 'coreA', 'c', 'd', 'RPR', 2, 1),
                        ('compartmentA', 'coreA', 'c', 'f', 'RPR', 2, 3)]

        self.assertEquals(resultFetched, result_without_e)

    def test_unbind_f(self):
        self.myreg.unbind('coreA', 'f')
        resultFetched = self.myreg.conn.execute("SELECT * FROM {} ".format(self.myreg.name)).fetchall()
        result_without_f=[('compartmentA', 'coreA', 'coreA', 'b', 'PPR', 1, 1),
                        ('compartmentA', 'coreA', 'coreA', 'c', 'PPR', 1, 2),
                        ('compartmentA', 'coreA', 'c', 'd', 'RPR', 2, 1),
                        ('compartmentA', 'coreA', 'c', 'e', 'RPR', 2, 2),
                        ('compartmentA', 'coreA', 'e', 'g', 'RPR', 3, 1),
                        ('compartmentA', 'coreA', 'e', 'j', 'RPR', 3, 2),
                        ('compartmentA', 'coreA', 'g', 'h', 'RPR', 4, 1),
                        ('compartmentA', 'coreA', 'g', 'i', 'RPR', 4, 2)]
        self.assertEquals(resultFetched, result_without_f)

    def test_unbind_g(self):
        self.myreg.unbind('coreA', 'g')
        resultFetched = self.myreg.conn.execute("SELECT * FROM {} ".format(self.myreg.name)).fetchall()
        result_without_g=[('compartmentA', 'coreA', 'coreA', 'b', 'PPR', 1, 1),
                        ('compartmentA', 'coreA', 'coreA', 'c', 'PPR', 1, 2),
                        ('compartmentA', 'coreA', 'c', 'd', 'RPR', 2, 1),
                        ('compartmentA', 'coreA', 'c', 'e', 'RPR', 2, 2),
                        ('compartmentA', 'coreA', 'c', 'f', 'RPR', 2, 3),
                        ('compartmentA', 'coreA', 'e', 'j', 'RPR', 3, 2)]
        self.assertEquals(resultFetched, result_without_g)

    def test_unbind_h(self):
        self.myreg.unbind('coreA', 'h')
        resultFetched = self.myreg.conn.execute("SELECT * FROM {} ".format(self.myreg.name)).fetchall()
        result_without_h=[('compartmentA', 'coreA', 'coreA', 'b', 'PPR', 1, 1),
                        ('compartmentA', 'coreA', 'coreA', 'c', 'PPR', 1, 2),
                        ('compartmentA', 'coreA', 'c', 'd', 'RPR', 2, 1),
                        ('compartmentA', 'coreA', 'c', 'e', 'RPR', 2, 2),
                        ('compartmentA', 'coreA', 'c', 'f', 'RPR', 2, 3),
                        ('compartmentA', 'coreA', 'e', 'g', 'RPR', 3, 1),
                        ('compartmentA', 'coreA', 'e', 'j', 'RPR', 3, 2),
                        ('compartmentA', 'coreA', 'g', 'i', 'RPR', 4, 2)]
        self.assertEquals(resultFetched, result_without_h)

    def test_unbind_i(self):
        self.myreg.unbind('coreA', 'i')
        resultFetched = self.myreg.conn.execute("SELECT * FROM {} ".format(self.myreg.name)).fetchall()
        result_without_i=[('compartmentA', 'coreA', 'coreA', 'b', 'PPR', 1, 1),
                        ('compartmentA', 'coreA', 'coreA', 'c', 'PPR', 1, 2),
                        ('compartmentA', 'coreA', 'c', 'd', 'RPR', 2, 1),
                        ('compartmentA', 'coreA', 'c', 'e', 'RPR', 2, 2),
                        ('compartmentA', 'coreA', 'c', 'f', 'RPR', 2, 3),
                        ('compartmentA', 'coreA', 'e', 'g', 'RPR', 3, 1),
                        ('compartmentA', 'coreA', 'e', 'j', 'RPR', 3, 2),
                        ('compartmentA', 'coreA', 'g', 'h', 'RPR', 4, 1)]

        self.assertEquals(resultFetched, result_without_i)

