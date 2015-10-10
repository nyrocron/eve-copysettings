# Copyright 2015 Florian Tautz
# This program is licensed under the MIT License,
# see the contents of the LICENSE file in this directory for details.


import sqlite3
from datetime import datetime


class CacheDb(object):
    TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, db):
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()

    def create_table(self):
        self.cursor.execute('CREATE TABLE cache ('
                            '  key TEXT NOT NULL,'
                            '  value TEXT,'
                            '  cached_until TEXT NOT NULL,'
                            '  PRIMARY KEY (key)'
                            ')')
        self.connection.commit()

    def get(self, item):
        self.cursor.execute('SELECT value, cached_until FROM cache WHERE key = ?',
                            (item,))
        result = self.cursor.fetchone()
        if result is None:
            return None
        value, cached_until_timestamp = result
        cached_until = datetime.strptime(cached_until_timestamp,
                                         CacheDb.TIMESTAMP_FORMAT)
        if cached_until > datetime.utcnow():
            return value
        else:
            self.cursor.execute('DELETE FROM cache WHERE key = ?', (item,))
            self.connection.commit()
            return None

    def set(self, key, value, cached_until):
            self.cursor.execute('INSERT INTO cache (key, value, cached_until)'
                                ' VALUES (?, ?, ?)',
                                (key, value,
                                 cached_until.strftime(CacheDb.TIMESTAMP_FORMAT)))
            self.connection.commit()


if __name__ == '__main__':
    cache = CacheDb('api_cache.db')
    cache.create_table()
