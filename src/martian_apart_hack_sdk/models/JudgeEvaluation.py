from dataclasses import dataclass

@dataclass(frozen=True)
class JudgeEvaluation:
    score: float
    reason: str