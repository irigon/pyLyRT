import unittest
from libs import db
from nose.tools import raises
from sqlite3 import IntegrityError, OperationalError

class TestDB(unittest.TestCase):

    def setUp(self):
        args = "CompartmentId text CHECK(TYPEOF(CompartmentId) = 'text'), " \
               "CorePlayerId text CHECK(TYPEOF(CorePlayerId) = 'text'), " \
               "PlayerId text CHECK(TYPEOF(PlayerId) = 'text'), " \
               "RoleId text CHECK(TYPEOF(RoleId) = 'text'), " \
               "RelationType text CHECK(TYPEOF(RelationType) = 'text'), " \
               "BindingLevel integer CHECK(TYPEOF(BindingLevel) = 'integer'), " \
               "BindingSequence integer CHECK(TYPEOF(BindingSequence) = 'integer')"
        self.mydb = db.DB('roles_db', args)
        self.mydb.dbconn.execute('CREATE INDEX search_order ON roles_db(BindingLevel DESC, BindingSequence DESC)')


    def tearDown(self):
        self.mydb.dbconn.close()

    def test_db_creation(self):
        args = "CompartmentId text, CorePlayerId text, PlayerId text, RoleId text, RelationType text, " \
               "BindingLevel integer, BindingSequence integer"
        mydb = db.DB('tmp_db', args)
        self.assertTrue(mydb.dbconn is not None)
        mydb.dbconn.close()

    # update levels and sequences
    def test_db_insert_valid_relation(self):
        rows = [('company', 'bob'    , 'bob'      , 'developer' , 'PPR', 1, 1),
                ('company', 'alice'  , 'alice'    , 'accountant', 'PPR', 1, 2),
                ('company', 'ely'    , 'ely'      , 'freelance' , 'PPR', 1, 1),
                ('company', 'ely'    , 'freelance', 'taxpayer'  , 'RPR', 2, 1),
                ('tax'    , 'company', 'company'  , 'taxpayer'  , 'PPR', 1, 1)]
        self.mydb.dbconn.executemany('INSERT INTO roles_db VALUES(?, ?, ?, ?, ?, ?, ?)', rows)

        num_rows =  self.mydb.dbconn.execute('select count(*) from roles_db')
        self.assertEqual(num_rows.fetchone()[0], 5)

    @raises(OperationalError) # last field missing
    def test_db_insert_missing_fields_invalid_relation(self):
        self.mydb.dbconn.execute("INSERT INTO roles_db VALUES('company', 'ely', 'ely' , \
                                                              'freelance', 'PPR', 1)")

    @raises(IntegrityError) # on the first line, the last field is a string; on the second, the first is a number.
    def test_db_insert_invalid_type(self):
        self.mydb.dbconn.execute("INSERT INTO roles_db VALUES('company', 'ely', 'ely' , \
                                                              'freelance', 'PPR', 1, 'me')")
        self.mydb.dbconn.execute("INSERT INTO roles_db VALUES(1, 'ely', 'ely' , \
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
        objects={}
        for i in ['a','b','c','d','e','f','g','h','i','j']:
            objects[i]=Dummy()

        objects['a'].m0=dummyFunc()
        objects['b'].m1=dummyFunc()
        objects['b'].m2=dummyFunc()
        objects['b'].m3=dummyFunc()
        objects['c'].m2=dummyFunc()
        objects['d'].m1=dummyFunc()
        objects['h'].m3=dummyFunc()
        objects['i'].m3=dummyFunc()
        objects['i'].m4=dummyFunc()

        return(rows, objects)

    def test_db_valid_query(self):
        rows, objects = self.setupDBforTesting()
        self.mydb.dbconn.executemany('INSERT INTO roles_db VALUES(?, ?, ?, ?, ?, ?, ?)', rows)
        sequence = self.mydb.dbconn.execute('SELECT * FROM roles_db order by BindingLevel DESC,BindingSequence DESC')
        self.assertEqual(9, len(sequence.fetchall()))

    # searching for leaf (m4)
    def test_db_valid_simple_search_item_present(self):
        rows, objects = self.setupDBforTesting()
        self.mydb.dbconn.executemany('INSERT INTO roles_db VALUES(?, ?, ?, ?, ?, ?, ?)', rows)
        sequence = self.mydb.dbconn.execute('SELECT * FROM roles_db order by BindingLevel DESC,BindingSequence DESC')
        # TODO: use generators instead of fetchall
        # the third in the tuple is the role
        val = next((x[3] for x in sequence.fetchall() if hasattr(objects[x[3]],'m4') is not False), None)
        self.assertTrue(val is not None)

    def test_db_valid_simple_search_item_not_present(self):
        rows, objects = self.setupDBforTesting()
        self.mydb.dbconn.executemany('INSERT INTO roles_db VALUES(?, ?, ?, ?, ?, ?, ?)', rows)
        sequence = self.mydb.dbconn.execute('SELECT * FROM roles_db order by BindingLevel DESC,BindingSequence DESC')
        val = next((x[3] for x in sequence.fetchall() if hasattr(objects[x[3]],'m100') is not False), None)
        self.assertTrue(val is None)

    # core is not going to be found, since this search method go just through the roles
    def test_db_valid_search_method_in_core(self):
        rows, objects = self.setupDBforTesting()
        self.mydb.dbconn.executemany('INSERT INTO roles_db VALUES(?, ?, ?, ?, ?, ?, ?)', rows)
        sequence = self.mydb.dbconn.execute('SELECT * FROM roles_db order by BindingLevel DESC,BindingSequence DESC')
        val = next((x[3] for x in sequence.fetchall() if hasattr(objects[x[3]],'m0') is not False), None)
        self.assertEquals(val, None)
        self.assertTrue(hasattr(objects['a'], 'm0'))

    def test_db_valid_search_same_index_different_deep(self):
        rows, objects = self.setupDBforTesting()
        self.mydb.dbconn.executemany('INSERT INTO roles_db VALUES(?, ?, ?, ?, ?, ?, ?)', rows)
        sequence = self.mydb.dbconn.execute('SELECT * FROM roles_db order by BindingLevel DESC,BindingSequence DESC')
        val = next((x[3] for x in sequence.fetchall() if hasattr(objects[x[3]],'m1') is not False), None)
        self.assertEquals(val, 'd')

    def test_db_valid_search_same_level_different_sequence(self):
        rows, objects = self.setupDBforTesting()
        self.mydb.dbconn.executemany('INSERT INTO roles_db VALUES(?, ?, ?, ?, ?, ?, ?)', rows)
        sequence = self.mydb.dbconn.execute('SELECT * FROM roles_db order by BindingLevel DESC,BindingSequence DESC')
        val = next((x[3] for x in sequence.fetchall() if hasattr(objects[x[3]],'m2') is not False), None)
        self.assertEquals(val, 'c')

    def test_db_valid_search_different_level_and_sequence(self):
        rows, objects = self.setupDBforTesting()
        self.mydb.dbconn.executemany('INSERT INTO roles_db VALUES(?, ?, ?, ?, ?, ?, ?)', rows)
        sequence = self.mydb.dbconn.execute('SELECT * FROM roles_db order by BindingLevel DESC,BindingSequence DESC')
        val = next((x[3] for x in sequence.fetchall() if hasattr(objects[x[3]],'m3') is not False), None)
        self.assertEquals(val, 'i')

    # every insert, we must assure that the sequence becomes the greates of that level
    def test_db_valid_insert_item(self):
        pass

    # update levels and sequences
    # verify consistency of the levels and sequences
    def test_db_delete_relation(self):
        pass



