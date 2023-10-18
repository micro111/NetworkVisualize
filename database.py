import os
import time
import threading
import sqlite3

class SQLiteDB:
    def __init__(self, database_name=None, dir_name="db/", in_memory=True ,check_same_thread=True):
        if in_memory:
            self.conn = sqlite3.connect(":memory:",check_same_thread=check_same_thread)
        else:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            self.conn = sqlite3.connect(dir_name + database_name,check_same_thread=check_same_thread)
        self.db_lock = threading.Lock()
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        columns_str = ", ".join(columns)
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        self.cursor.execute(query)
        self.conn.commit()

    def insert_data(self, table_name, data):
        with self.db_lock: 
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data.values()])
            values = tuple(data.values())
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, values)
            self.conn.commit()

    def fetch_all(self, table_name):
        with self.db_lock: 
            query = f"SELECT * FROM {table_name}"
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def clean_data(self,table_name):
        while True:
            with self.db_lock: 
                query = f"DELETE FROM  {table_name} WHERE (? - timestamp) >= 900"
                self.cursor.execute(query, (time.time(),))
                self.conn.commit()
            time.sleep(60)  # 1分ごとに掃除

    def close(self):
        if self.conn:
            self.conn.close()

