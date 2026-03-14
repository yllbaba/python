from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional
import sqlite3

import pandas as pd

from app.models.game_stats import GameStats
from app.repositories.player_repo import PlayerRepository
from app.repositories.stats_repo import StatsRepository
from app.schemas.game_schema import (
    BestScoringGame,
    GameDetail,
    GameOut,
    GameSummary,
    GameTrend,
    LeaderboardEntry,
    StatOut,
)
from app.schemas.player_schema import PlayerProfile


class StatsService:
    def __init__(self, stats_repo: StatsRepository, player_repo: PlayerRepository) -> None:
        self.stats_repo = stats_repo
        self.player_repo = player_repo

    def create_game(self, user_id: int, game_date: date, opponent: str) -> GameOut:
        game_id = self.stats_repo.create_game(user_id, game_date.isoformat(), opponent)
        return GameOut(id=game_id, game_date=game_date, opponent=opponent)

    def list_games(
        self,
        user_id: int,
        date_from: Optional[date],
        date_to: Optional[date],
        opponent: Optional[str],
    ) -> List[GameOut]:
        rows = self.stats_repo.list_games(
            user_id,
            date_from.isoformat() if date_from else None,
            date_to.isoformat() if date_to else None,
            opponent,
        )
        return [
            GameOut(
                id=int(row["id"]),
                game_date=date.fromisoformat(row["game_date"]),
                opponent=str(row["opponent"]),
            )
            for row in rows
        ]

    def get_game_detail(self, user_id: int, game_id: int) -> Optional[GameDetail]:
        game = self.stats_repo.get_game(user_id, game_id)
        if not game:
            return None
        stats_rows = self.stats_repo.list_stats_for_game(game_id)
        stats = [self._row_to_stat(row) for row in stats_rows]
        total_points = sum(stat.points for stat in stats)
        return GameDetail(
            id=int(game["id"]),
            game_date=date.fromisoformat(game["game_date"]),
            opponent=str(game["opponent"]),
            stats=stats,
            total_points=total_points,
        )

    def create_stat(
        self,
        user_id: int,
        game_id: int,
        player_name: str,
        points: int,
        assists: int,
        rebounds: int,
        steals: int,
        blocks: int,
        turnovers: int,
        minutes_played: float,
    ) -> StatOut:
        game = self.stats_repo.get_game(user_id, game_id)
        if not game:
            raise ValueError("Game not found")
        stat_id = self.stats_repo.create_stat(
            game_id,
            player_name,
            points,
            assists,
            rebounds,
            steals,
            blocks,
            turnovers,
            minutes_played,
        )
        return StatOut(
            id=stat_id,
            game_id=game_id,
            player_name=player_name,
            points=points,
            assists=assists,
            rebounds=rebounds,
            steals=steals,
            blocks=blocks,
            turnovers=turnovers,
            minutes_played=minutes_played,
            efficiency_rating=self._efficiency(
                points, assists, rebounds, steals, blocks, turnovers
            ),
        )

    def update_stat(self, user_id: int, stat_id: int, fields: Dict[str, object]) -> bool:
        stat = self.stats_repo.get_stat_for_user(user_id, stat_id)
        if not stat:
            raise ValueError("Stat not found")
        return self.stats_repo.update_stat(user_id, stat_id, fields)

    def delete_stat(self, user_id: int, stat_id: int) -> bool:
        return self.stats_repo.delete_stat(user_id, stat_id)

    def summary(
        self,
        user_id: int,
        date_from: Optional[date],
        date_to: Optional[date],
        opponent: Optional[str],
    ) -> GameSummary:
        summary_row = self.stats_repo.summary(
            user_id,
            date_from.isoformat() if date_from else None,
            date_to.isoformat() if date_to else None,
            opponent,
        )
        games_played = int(summary_row["games_played"]) if summary_row else 0
        total_points = int(summary_row["total_points"]) if summary_row else 0
        total_assists = int(summary_row["total_assists"]) if summary_row else 0
        total_rebounds = int(summary_row["total_rebounds"]) if summary_row else 0
        total_steals = int(summary_row["total_steals"]) if summary_row else 0
        total_blocks = int(summary_row["total_blocks"]) if summary_row else 0
        total_turnovers = int(summary_row["total_turnovers"]) if summary_row else 0
        total_minutes = float(summary_row["total_minutes"]) if summary_row else 0.0

        best_game_row = self.stats_repo.best_scoring_game(
            user_id,
            date_from.isoformat() if date_from else None,
            date_to.isoformat() if date_to else None,
            opponent,
        )
        best_game = None
        if best_game_row and games_played > 0:
            best_game = BestScoringGame(
                game_id=int(best_game_row["game_id"]),
                game_date=date.fromisoformat(best_game_row["game_date"]),
                opponent=str(best_game_row["opponent"]),
                total_points=int(best_game_row["total_points"]),
            )

        avg_points = total_points / games_played if games_played else 0.0
        avg_assists = total_assists / games_played if games_played else 0.0
        avg_rebounds = total_rebounds / games_played if games_played else 0.0

        return GameSummary(
            games_played=games_played,
            total_points=total_points,
            total_assists=total_assists,
            total_rebounds=total_rebounds,
            total_steals=total_steals,
            total_blocks=total_blocks,
            total_turnovers=total_turnovers,
            total_minutes=total_minutes,
            average_points_per_game=avg_points,
            average_assists_per_game=avg_assists,
            average_rebounds_per_game=avg_rebounds,
            best_scoring_game=best_game,
        )

    def leaderboard(
        self,
        user_id: int,
        limit: int,
        date_from: Optional[date],
        date_to: Optional[date],
        opponent: Optional[str],
    ) -> List[LeaderboardEntry]:
        rows = self.player_repo.leaderboard(
            user_id,
            limit,
            date_from.isoformat() if date_from else None,
            date_to.isoformat() if date_to else None,
            opponent,
        )
        entries: List[LeaderboardEntry] = []
        for row in rows:
            games_played = int(row["games_played"])
            total_points = int(row["total_points"])
            avg_points = total_points / games_played if games_played else 0.0
            efficiency_rating = float(row["efficiency_total"]) / games_played if games_played else 0.0
            entries.append(
                LeaderboardEntry(
                    player_name=str(row["player_name"]),
                    games_played=games_played,
                    total_points=total_points,
                    average_points=avg_points,
                    efficiency_rating=efficiency_rating,
                )
            )
        return entries

    def player_profiles(
        self,
        user_id: int,
        date_from: Optional[date],
        date_to: Optional[date],
        opponent: Optional[str],
    ) -> List[PlayerProfile]:
        rows = self.player_repo.player_profiles(
            user_id,
            date_from.isoformat() if date_from else None,
            date_to.isoformat() if date_to else None,
            opponent,
        )
        profiles: List[PlayerProfile] = []
        for row in rows:
            games_played = int(row["games_played"])
            total_points = int(row["total_points"])
            total_assists = int(row["total_assists"])
            total_rebounds = int(row["total_rebounds"])
            avg_points = total_points / games_played if games_played else 0.0
            avg_assists = total_assists / games_played if games_played else 0.0
            avg_rebounds = total_rebounds / games_played if games_played else 0.0
            efficiency_rating = float(row["efficiency_total"]) / games_played if games_played else 0.0
            profiles.append(
                PlayerProfile(
                    player_name=str(row["player_name"]),
                    games_played=games_played,
                    total_points=total_points,
                    total_assists=total_assists,
                    total_rebounds=total_rebounds,
                    average_points=avg_points,
                    average_assists=avg_assists,
                    average_rebounds=avg_rebounds,
                    efficiency_rating=efficiency_rating,
                )
            )
        return profiles

    def trends(
        self,
        user_id: int,
        date_from: Optional[date],
        date_to: Optional[date],
        opponent: Optional[str],
    ) -> List[GameTrend]:
        rows = self.stats_repo.game_trends(
            user_id,
            date_from.isoformat() if date_from else None,
            date_to.isoformat() if date_to else None,
            opponent,
        )
        return [
            GameTrend(
                game_id=int(row["game_id"]),
                game_date=date.fromisoformat(row["game_date"]),
                opponent=str(row["opponent"]),
                total_points=int(row["total_points"]),
                total_assists=int(row["total_assists"]),
                total_rebounds=int(row["total_rebounds"]),
            )
            for row in rows
        ]

    def export_csv(
        self,
        user_id: int,
        date_from: Optional[date],
        date_to: Optional[date],
        opponent: Optional[str],
    ) -> str:
        rows = self.stats_repo.export_rows(
            user_id,
            date_from.isoformat() if date_from else None,
            date_to.isoformat() if date_to else None,
            opponent,
        )
        if not rows:
            return ""
        data = [dict(row) for row in rows]
        dataframe = pd.DataFrame(data)
        return dataframe.to_csv(index=False)

    def _row_to_stat(self, row: sqlite3.Row) -> StatOut:
        stat = GameStats(
            id=int(row["id"]),
            game_id=int(row["game_id"]),
            player_name=str(row["player_name"]),
            points=int(row["points"]),
            assists=int(row["assists"]),
            rebounds=int(row["rebounds"]),
            steals=int(row["steals"]),
            blocks=int(row["blocks"]),
            turnovers=int(row["turnovers"]),
            minutes_played=float(row["minutes_played"]),
        )
        return StatOut(
            id=stat.id,
            game_id=stat.game_id,
            player_name=stat.player_name,
            points=stat.points,
            assists=stat.assists,
            rebounds=stat.rebounds,
            steals=stat.steals,
            blocks=stat.blocks,
            turnovers=stat.turnovers,
            minutes_played=stat.minutes_played,
            efficiency_rating=stat.efficiency_rating(),
        )

    def _efficiency(
        self,
        points: int,
        assists: int,
        rebounds: int,
        steals: int,
        blocks: int,
        turnovers: int,
    ) -> float:
        return float(points + assists + rebounds + steals + blocks - turnovers)
