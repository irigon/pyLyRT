import sqlite3

class DB:
    def __init__(self, table_name, args):
        self.dbconn = sqlite3.connect(":memory:")
        self.dbconn.execute("CREATE TABLE " + table_name + " (" + args + ")")
        self.dbconn.commit()

    def __del__(self):
        self.dbconn.close()
