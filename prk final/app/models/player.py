from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Player:
    name: str
    position: Optional[str] = None
    team: Optional[str] = None
