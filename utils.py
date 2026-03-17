from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import random
import time


class AttentionState(str, Enum):
    ATTENTIVE = "attentive"
    DISTRACTED = "distracted"
    ABSENT = "absent"  # e.g., not looking / not present


@dataclass
class EpisodeStats:
    total_steps: int = 0
    tasks_attempted: int = 0
    tasks_completed: int = 0
    consecutive_success: int = 0
    consecutive_fail: int = 0
    last_task_success: Optional[bool] = None


class RNG:
    """
    Small wrapper so modules can share a seeded RNG.
    """

    def __init__(self, seed: int | None = 7) -> None:
        self._rng = random.Random(seed)

    def random(self) -> float:
        return float(self._rng.random())

    def randint(self, a: int, b: int) -> int:
        return int(self._rng.randint(a, b))

    def choice(self, seq):
        return self._rng.choice(seq)

    def shuffle(self, seq) -> None:
        self._rng.shuffle(seq)


class RateLimiter:
    """
    Prevent spamming the user with repeated prompts.
    """

    def __init__(self, min_interval_s: float = 1.0) -> None:
        self.min_interval_s = float(min_interval_s)
        self._last_t = 0.0

    def ready(self) -> bool:
        now = time.perf_counter()
        if (now - self._last_t) >= self.min_interval_s:
            self._last_t = now
            return True
        return False

