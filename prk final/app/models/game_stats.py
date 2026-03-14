from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Game:
    id: int
    user_id: int
    game_date: date
    opponent: str


@dataclass(frozen=True)
class GameStats:
    id: int
    game_id: int
    player_name: str
    points: int
    assists: int
    rebounds: int
    steals: int
    blocks: int
    turnovers: int
    minutes_played: float

    def efficiency_rating(self) -> float:
        return float(
            self.points
            + self.assists
            + self.rebounds
            + self.steals
            + self.blocks
            - self.turnovers
        )
