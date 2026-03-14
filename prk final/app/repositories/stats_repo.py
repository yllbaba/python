from __future__ import annotations

from typing import Dict, List, Optional, Tuple
import sqlite3

from app.database import Database


class StatsRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def create_game(self, user_id: int, game_date: str, opponent: str) -> int:
        with self.db.connect() as conn:
            cursor = conn.execute(
                "INSERT INTO games (user_id, game_date, opponent) VALUES (?, ?, ?)",
                (user_id, game_date, opponent),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def list_games(
        self,
        user_id: int,
        date_from: Optional[str],
        date_to: Optional[str],
        opponent: Optional[str],
    ) -> List[sqlite3.Row]:
        query = "SELECT id, game_date, opponent FROM games WHERE user_id = ?"
        params: List[object] = [user_id]
        filter_sql, filter_params = self._game_filters(date_from, date_to, opponent)
        query += filter_sql
        params.extend(filter_params)
        query += " ORDER BY game_date DESC, id DESC"
        with self.db.connect() as conn:
            return conn.execute(query, params).fetchall()

    def get_game(self, user_id: int, game_id: int) -> Optional[sqlite3.Row]:
        with self.db.connect() as conn:
            return conn.execute(
                "SELECT id, game_date, opponent FROM games WHERE id = ? AND user_id = ?",
                (game_id, user_id),
            ).fetchone()

    def create_stat(
        self,
        game_id: int,
        player_name: str,
        points: int,
        assists: int,
        rebounds: int,
        steals: int,
        blocks: int,
        turnovers: int,
        minutes_played: float,
    ) -> int:
        with self.db.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO stats (
                    game_id, player_name, points, assists, rebounds, steals, blocks, turnovers, minutes_played
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    game_id,
                    player_name,
                    points,
                    assists,
                    rebounds,
                    steals,
                    blocks,
                    turnovers,
                    minutes_played,
                ),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def list_stats_for_game(self, game_id: int) -> List[sqlite3.Row]:
        with self.db.connect() as conn:
            return conn.execute(
                "SELECT * FROM stats WHERE game_id = ? ORDER BY id ASC",
                (game_id,),
            ).fetchall()

    def get_stat_for_user(self, user_id: int, stat_id: int) -> Optional[sqlite3.Row]:
        with self.db.connect() as conn:
            return conn.execute(
                """
                SELECT stats.* FROM stats
                JOIN games ON stats.game_id = games.id
                WHERE stats.id = ? AND games.user_id = ?
                """,
                (stat_id, user_id),
            ).fetchone()

    def update_stat(self, user_id: int, stat_id: int, fields: Dict[str, object]) -> bool:
        if not fields:
            return False
        assignments = ", ".join(f"{key} = ?" for key in fields.keys())
        params: List[object] = list(fields.values())
        params.append(stat_id)
        params.append(user_id)
        query = (
            f"UPDATE stats SET {assignments} "
            "WHERE id = ? AND game_id IN (SELECT id FROM games WHERE user_id = ?)"
        )
        with self.db.connect() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0

    def delete_stat(self, user_id: int, stat_id: int) -> bool:
        with self.db.connect() as conn:
            cursor = conn.execute(
                """
                DELETE FROM stats
                WHERE id = ?
                AND game_id IN (SELECT id FROM games WHERE user_id = ?)
                """,
                (stat_id, user_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def summary(
        self,
        user_id: int,
        date_from: Optional[str],
        date_to: Optional[str],
        opponent: Optional[str],
    ) -> Optional[sqlite3.Row]:
        filter_sql, filter_params = self._game_filters(date_from, date_to, opponent)
        query = (
            "SELECT "
            "COUNT(DISTINCT games.id) AS games_played, "
            "COALESCE(SUM(stats.points), 0) AS total_points, "
            "COALESCE(SUM(stats.assists), 0) AS total_assists, "
            "COALESCE(SUM(stats.rebounds), 0) AS total_rebounds, "
            "COALESCE(SUM(stats.steals), 0) AS total_steals, "
            "COALESCE(SUM(stats.blocks), 0) AS total_blocks, "
            "COALESCE(SUM(stats.turnovers), 0) AS total_turnovers, "
            "COALESCE(SUM(stats.minutes_played), 0) AS total_minutes "
            "FROM games "
            "LEFT JOIN stats ON stats.game_id = games.id "
            "WHERE games.user_id = ?"
        )
        params: List[object] = [user_id]
        query += filter_sql
        params.extend(filter_params)
        with self.db.connect() as conn:
            return conn.execute(query, params).fetchone()

    def best_scoring_game(
        self,
        user_id: int,
        date_from: Optional[str],
        date_to: Optional[str],
        opponent: Optional[str],
    ) -> Optional[sqlite3.Row]:
        filter_sql, filter_params = self._game_filters(date_from, date_to, opponent)
        query = (
            "SELECT games.id AS game_id, games.game_date, games.opponent, "
            "COALESCE(SUM(stats.points), 0) AS total_points "
            "FROM games "
            "LEFT JOIN stats ON stats.game_id = games.id "
            "WHERE games.user_id = ?"
        )
        params: List[object] = [user_id]
        query += filter_sql
        params.extend(filter_params)
        query += " GROUP BY games.id ORDER BY total_points DESC LIMIT 1"
        with self.db.connect() as conn:
            return conn.execute(query, params).fetchone()

    def game_trends(
        self,
        user_id: int,
        date_from: Optional[str],
        date_to: Optional[str],
        opponent: Optional[str],
    ) -> List[sqlite3.Row]:
        filter_sql, filter_params = self._game_filters(date_from, date_to, opponent)
        query = (
            "SELECT games.id AS game_id, games.game_date, games.opponent, "
            "COALESCE(SUM(stats.points), 0) AS total_points, "
            "COALESCE(SUM(stats.assists), 0) AS total_assists, "
            "COALESCE(SUM(stats.rebounds), 0) AS total_rebounds "
            "FROM games "
            "LEFT JOIN stats ON stats.game_id = games.id "
            "WHERE games.user_id = ?"
        )
        params: List[object] = [user_id]
        query += filter_sql
        params.extend(filter_params)
        query += " GROUP BY games.id ORDER BY games.game_date ASC, games.id ASC"
        with self.db.connect() as conn:
            return conn.execute(query, params).fetchall()

    def export_rows(
        self,
        user_id: int,
        date_from: Optional[str],
        date_to: Optional[str],
        opponent: Optional[str],
    ) -> List[sqlite3.Row]:
        filter_sql, filter_params = self._game_filters(date_from, date_to, opponent)
        query = (
            "SELECT games.game_date, games.opponent, stats.player_name, "
            "stats.points, stats.assists, stats.rebounds, stats.steals, "
            "stats.blocks, stats.turnovers, stats.minutes_played, "
            "(stats.points + stats.assists + stats.rebounds + stats.steals + stats.blocks - stats.turnovers) "
            "AS efficiency_rating "
            "FROM stats "
            "JOIN games ON stats.game_id = games.id "
            "WHERE games.user_id = ?"
        )
        params: List[object] = [user_id]
        query += filter_sql
        params.extend(filter_params)
        query += " ORDER BY games.game_date ASC, stats.player_name ASC"
        with self.db.connect() as conn:
            return conn.execute(query, params).fetchall()

    def _game_filters(
        self,
        date_from: Optional[str],
        date_to: Optional[str],
        opponent: Optional[str],
    ) -> Tuple[str, List[object]]:
        clauses: List[str] = []
        params: List[object] = []
        if date_from:
            clauses.append("games.game_date >= ?")
            params.append(date_from)
        if date_to:
            clauses.append("games.game_date <= ?")
            params.append(date_to)
        if opponent:
            clauses.append("games.opponent LIKE ?")
            params.append(f"%{opponent}%")
        if clauses:
            return " AND " + " AND ".join(clauses), params
        return "", params
