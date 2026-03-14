from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.deps import get_current_user, get_stats_service
from app.schemas.game_schema import (
    GameCreate,
    GameDetail,
    GameOut,
    GameSummary,
    GameTrend,
    LeaderboardEntry,
    StatCreate,
    StatOut,
    StatUpdate,
)
from app.schemas.player_schema import PlayerProfile
from app.services.auth_service import AuthenticatedUser
from app.services.stats_service import StatsService

router = APIRouter(prefix="/stats", tags=["stats"])


@router.post("/games", response_model=GameOut, status_code=status.HTTP_201_CREATED)
def create_game(
    payload: GameCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: StatsService = Depends(get_stats_service),
) -> GameOut:
    return service.create_game(current_user.id, payload.game_date, payload.opponent)


@router.get("/games", response_model=List[GameOut])
def list_games(
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: StatsService = Depends(get_stats_service),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    opponent: Optional[str] = Query(None),
) -> List[GameOut]:
    return service.list_games(current_user.id, date_from, date_to, opponent)


@router.get("/games/{game_id}", response_model=GameDetail)
def get_game_detail(
    game_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: StatsService = Depends(get_stats_service),
) -> GameDetail:
    game_detail = service.get_game_detail(current_user.id, game_id)
    if not game_detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return game_detail


@router.post("/games/{game_id}/stats", response_model=StatOut, status_code=status.HTTP_201_CREATED)
def create_stat(
    game_id: int,
    payload: StatCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: StatsService = Depends(get_stats_service),
) -> StatOut:
    try:
        return service.create_stat(
            current_user.id,
            game_id,
            payload.player_name,
            payload.points,
            payload.assists,
            payload.rebounds,
            payload.steals,
            payload.blocks,
            payload.turnovers,
            payload.minutes_played,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/entries/{stat_id}")
def update_stat(
    stat_id: int,
    payload: StatUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: StatsService = Depends(get_stats_service),
) -> dict:
    fields = payload.dict(exclude_none=True)
    if not fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
    try:
        updated = service.update_stat(current_user.id, stat_id, fields)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return {"updated": updated}


@router.delete("/entries/{stat_id}")
def delete_stat(
    stat_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: StatsService = Depends(get_stats_service),
) -> dict:
    deleted = service.delete_stat(current_user.id, stat_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stat not found")
    return {"deleted": deleted}


@router.get("/summary", response_model=GameSummary)
def summary(
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: StatsService = Depends(get_stats_service),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    opponent: Optional[str] = Query(None),
) -> GameSummary:
    return service.summary(current_user.id, date_from, date_to, opponent)


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
def leaderboard(
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: StatsService = Depends(get_stats_service),
    limit: int = Query(10, ge=1, le=100),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    opponent: Optional[str] = Query(None),
) -> List[LeaderboardEntry]:
    return service.leaderboard(current_user.id, limit, date_from, date_to, opponent)


@router.get("/players", response_model=List[PlayerProfile])
def player_profiles(
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: StatsService = Depends(get_stats_service),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    opponent: Optional[str] = Query(None),
) -> List[PlayerProfile]:
    return service.player_profiles(current_user.id, date_from, date_to, opponent)


@router.get("/trends", response_model=List[GameTrend])
def trends(
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: StatsService = Depends(get_stats_service),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    opponent: Optional[str] = Query(None),
) -> List[GameTrend]:
    return service.trends(current_user.id, date_from, date_to, opponent)


@router.get("/export")
def export_csv(
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: StatsService = Depends(get_stats_service),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    opponent: Optional[str] = Query(None),
) -> Response:
    csv_data = service.export_csv(current_user.id, date_from, date_to, opponent)
    return Response(content=csv_data, media_type="text/csv")
