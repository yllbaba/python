import hashlib
from database.db import Database

class Auth:
    def __init__(self):
        self.db = Database()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password):
        hashed = self.hash_password(password)
        try:
            self.db.conn.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, hashed)
            )
            self.db.conn.commit()
            return "Registered!"
        except:
            return "User exists!"

    def login(self, username, password):
        hashed = self.hash_password(password)
        cursor = self.db.conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, hashed)
        )
        return cursor.fetchone() is not None