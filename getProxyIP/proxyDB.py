# -*- coding: utf-8 -*-


import sqlite3


def init_db(database):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    # create table ip_pools
    c.execute('''CREATE TABLE ip_pools
                    (address text, port text)''')
    conn.commit()
    conn.close()


class HandlerDB(object):
    def __init__(self, database):
        self.conn = sqlite3.connect(database)
        self.cursor = self.conn.cursor()

    def insert(self, addr, port):
        try:
            with self.conn:
                self.cursor.execute('INSERT INTO ip_pools VALUES (?, ?)',
                                    (addr, port))
        except sqlite3.IntegrityError:
            print("couldn't add ({}, {})".format(addr, port))

    # insert many records use a list contain every (address, port)
    def insert_many(self, *args):
        try:
            with self.conn:
                self.cursor.executemany(
                    'INSERT INTO ip_pools VALUES (?, ?)', *args)
        except sqlite3.IntegrityError:
            print("couldn't insert many records")

    def fetch_many(self):
        rs = self.cursor.execute('SELECT * FROM ip_pools')
        return rs.fetchall()

    def clean_data(self):
        self.cursor.execute('DELETE FROM ip_pools')
        self.conn.commit()

    def close(self):
        self.conn.close()
