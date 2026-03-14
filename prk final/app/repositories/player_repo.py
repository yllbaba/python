from __future__ import annotations

from typing import List, Optional, Tuple
import sqlite3

from app.database import Database


class PlayerRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def leaderboard(
        self,
        user_id: int,
        limit: int,
        date_from: Optional[str],
        date_to: Optional[str],
        opponent: Optional[str],
    ) -> List[sqlite3.Row]:
        filter_sql, filter_params = self._game_filters(date_from, date_to, opponent)
        query = (
            "SELECT stats.player_name, "
            "COUNT(DISTINCT stats.game_id) AS games_played, "
            "COALESCE(SUM(stats.points), 0) AS total_points, "
            "COALESCE(SUM(stats.points + stats.assists + stats.rebounds + stats.steals + stats.blocks - stats.turnovers), 0) "
            "AS efficiency_total "
            "FROM stats "
            "JOIN games ON stats.game_id = games.id "
            "WHERE games.user_id = ?"
        )
        params: List[object] = [user_id]
        query += filter_sql
        params.extend(filter_params)
        query += " GROUP BY stats.player_name ORDER BY total_points DESC LIMIT ?"
        params.append(limit)
        with self.db.connect() as conn:
            return conn.execute(query, params).fetchall()

    def player_profiles(
        self,
        user_id: int,
        date_from: Optional[str],
        date_to: Optional[str],
        opponent: Optional[str],
    ) -> List[sqlite3.Row]:
        filter_sql, filter_params = self._game_filters(date_from, date_to, opponent)
        query = (
            "SELECT stats.player_name, "
            "COUNT(DISTINCT stats.game_id) AS games_played, "
            "COALESCE(SUM(stats.points), 0) AS total_points, "
            "COALESCE(SUM(stats.assists), 0) AS total_assists, "
            "COALESCE(SUM(stats.rebounds), 0) AS total_rebounds, "
            "COALESCE(SUM(stats.points + stats.assists + stats.rebounds + stats.steals + stats.blocks - stats.turnovers), 0) "
            "AS efficiency_total "
            "FROM stats "
            "JOIN games ON stats.game_id = games.id "
            "WHERE games.user_id = ?"
        )
        params: List[object] = [user_id]
        query += filter_sql
        params.extend(filter_params)
        query += " GROUP BY stats.player_name ORDER BY stats.player_name ASC"
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
