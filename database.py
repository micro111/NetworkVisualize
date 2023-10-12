import os
import time
import sqlite3

class SQLiteDB:
    def __init__(self, database_name=None, dir_name="db/", in_memory=True):
        if in_memory:
            self.conn = sqlite3.connect(":memory:")
        else:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            self.conn = sqlite3.connect(dir_name + database_name)
        
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        columns.append("timestamp INTEGER")
        columns_str = ", ".join(columns)
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        self.cursor.execute(query)
        self.conn.commit()

    def insert_data(self, table_name, data):
        data["timestamp"] = int(time.time())
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data.values()])
        values = tuple(data.values())
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.conn.commit()

    def fetch_all(self, table_name):
        query = f"SELECT * FROM {table_name}"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def cleanup(self, table_name):
        fifteen_minutes_ago = int(time.time()) - 15 * 60
        query = f"DELETE FROM {table_name} WHERE timestamp < ?"
        self.cursor.execute(query, (fifteen_minutes_ago,))
        self.conn.commit()
        
    def close(self):
        if self.conn:
            self.conn.close()

