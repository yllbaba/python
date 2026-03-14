from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class GameCreate(BaseModel):
    game_date: date
    opponent: str = Field(..., min_length=1, max_length=100)


class GameOut(BaseModel):
    id: int
    game_date: date
    opponent: str


class StatCreate(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=100)
    points: int = Field(0, ge=0)
    assists: int = Field(0, ge=0)
    rebounds: int = Field(0, ge=0)
    steals: int = Field(0, ge=0)
    blocks: int = Field(0, ge=0)
    turnovers: int = Field(0, ge=0)
    minutes_played: float = Field(0, ge=0)


class StatUpdate(BaseModel):
    points: Optional[int] = Field(None, ge=0)
    assists: Optional[int] = Field(None, ge=0)
    rebounds: Optional[int] = Field(None, ge=0)
    steals: Optional[int] = Field(None, ge=0)
    blocks: Optional[int] = Field(None, ge=0)
    turnovers: Optional[int] = Field(None, ge=0)
    minutes_played: Optional[float] = Field(None, ge=0)


class StatOut(BaseModel):
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
    efficiency_rating: float


class GameDetail(BaseModel):
    id: int
    game_date: date
    opponent: str
    stats: List[StatOut]
    total_points: int


class BestScoringGame(BaseModel):
    game_id: int
    game_date: date
    opponent: str
    total_points: int


class GameSummary(BaseModel):
    games_played: int
    total_points: int
    total_assists: int
    total_rebounds: int
    total_steals: int
    total_blocks: int
    total_turnovers: int
    total_minutes: float
    average_points_per_game: float
    average_assists_per_game: float
    average_rebounds_per_game: float
    best_scoring_game: Optional[BestScoringGame]


class LeaderboardEntry(BaseModel):
    player_name: str
    games_played: int
    total_points: int
    average_points: float
    efficiency_rating: float


class GameTrend(BaseModel):
    game_id: int
    game_date: date
    opponent: str
    total_points: int
    total_assists: int
    total_rebounds: int
