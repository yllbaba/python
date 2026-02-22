import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("basketball.db")
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
        """)
        self.conn.commit()