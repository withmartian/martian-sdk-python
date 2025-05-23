from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class JudgeEvaluation:
    score: float
    reason: str
    cost: Optional[float] = None