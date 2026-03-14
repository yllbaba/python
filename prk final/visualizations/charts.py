from __future__ import annotations

from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd


def _prepare_dataframe(rows: List[Dict[str, object]]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    if "game_date" in df.columns:
        df["game_date"] = pd.to_datetime(df["game_date"])
    return df


def points_per_game_chart(rows: List[Dict[str, object]]) -> Optional[plt.Figure]:
    df = _prepare_dataframe(rows)
    if df.empty:
        return None
    fig, ax = plt.subplots()
    ax.plot(df["game_date"], df["total_points"], marker="o")
    ax.set_title("Points Per Game")
    ax.set_xlabel("Game Date")
    ax.set_ylabel("Total Points")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig


def assists_per_game_chart(rows: List[Dict[str, object]]) -> Optional[plt.Figure]:
    df = _prepare_dataframe(rows)
    if df.empty:
        return None
    fig, ax = plt.subplots()
    ax.plot(df["game_date"], df["total_assists"], marker="o", color="#2a6f97")
    ax.set_title("Assists Per Game")
    ax.set_xlabel("Game Date")
    ax.set_ylabel("Total Assists")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig


def rebounds_per_game_chart(rows: List[Dict[str, object]]) -> Optional[plt.Figure]:
    df = _prepare_dataframe(rows)
    if df.empty:
        return None
    fig, ax = plt.subplots()
    ax.plot(df["game_date"], df["total_rebounds"], marker="o", color="#ef6f6c")
    ax.set_title("Rebounds Per Game")
    ax.set_xlabel("Game Date")
    ax.set_ylabel("Total Rebounds")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig


def performance_trend_chart(rows: List[Dict[str, object]]) -> Optional[plt.Figure]:
    df = _prepare_dataframe(rows)
    if df.empty:
        return None
    fig, ax = plt.subplots()
    ax.plot(df["game_date"], df["total_points"], marker="o", label="Points")
    ax.plot(df["game_date"], df["total_assists"], marker="o", label="Assists")
    ax.plot(df["game_date"], df["total_rebounds"], marker="o", label="Rebounds")
    ax.set_title("Performance Trends")
    ax.set_xlabel("Game Date")
    ax.set_ylabel("Totals")
    ax.legend()
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig
