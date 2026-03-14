from __future__ import annotations

from typing import Optional
import sqlite3

from app.database import Database


class AuthRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def create_user(self, username: str, password_hash: str, password_salt: str) -> int:
        with self.db.connect() as conn:
            cursor = conn.execute(
                "INSERT INTO users (username, password_hash, password_salt) VALUES (?, ?, ?)",
                (username, password_hash, password_salt),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def get_user_by_username(self, username: str) -> Optional[sqlite3.Row]:
        with self.db.connect() as conn:
            return conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,),
            ).fetchone()

    def get_user_by_token(self, token: str) -> Optional[sqlite3.Row]:
        with self.db.connect() as conn:
            return conn.execute(
                "SELECT * FROM users WHERE token = ?",
                (token,),
            ).fetchone()

    def update_token(self, user_id: int, token: str, expires_at: str) -> None:
        with self.db.connect() as conn:
            conn.execute(
                "UPDATE users SET token = ?, token_expires_at = ? WHERE id = ?",
                (token, expires_at, user_id),
            )
            conn.commit()
