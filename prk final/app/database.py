from __future__ import annotations

import sqlite3
from typing import Optional

from app.config import get_settings


class Database:
    def __init__(self, db_path: Optional[str] = None) -> None:
        settings = get_settings()
        self.db_path = db_path or settings.db_path

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    password_salt TEXT NOT NULL,
                    token TEXT,
                    token_expires_at TEXT
                );

                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    game_date TEXT NOT NULL,
                    opponent TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER NOT NULL,
                    player_name TEXT NOT NULL,
                    points INTEGER NOT NULL DEFAULT 0 CHECK(points >= 0),
                    assists INTEGER NOT NULL DEFAULT 0 CHECK(assists >= 0),
                    rebounds INTEGER NOT NULL DEFAULT 0 CHECK(rebounds >= 0),
                    steals INTEGER NOT NULL DEFAULT 0 CHECK(steals >= 0),
                    blocks INTEGER NOT NULL DEFAULT 0 CHECK(blocks >= 0),
                    turnovers INTEGER NOT NULL DEFAULT 0 CHECK(turnovers >= 0),
                    minutes_played REAL NOT NULL DEFAULT 0 CHECK(minutes_played >= 0),
                    FOREIGN KEY (game_id) REFERENCES games (id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_games_user_date ON games (user_id, game_date);
                CREATE INDEX IF NOT EXISTS idx_stats_game ON stats (game_id);
                CREATE INDEX IF NOT EXISTS idx_stats_player ON stats (player_name);
                """
            )
            conn.commit()
