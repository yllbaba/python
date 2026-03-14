from __future__ import annotations

from pydantic import BaseModel


class PlayerProfile(BaseModel):
    player_name: str
    games_played: int
    total_points: int
    total_assists: int
    total_rebounds: int
    average_points: float
    average_assists: float
    average_rebounds: float
    efficiency_rating: float
