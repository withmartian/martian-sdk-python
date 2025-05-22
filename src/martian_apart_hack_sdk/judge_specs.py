"""Specifications for judges."""

import dataclasses
from typing import Any, Dict, Literal, Optional


@dataclasses.dataclass(frozen=True)
class RubricJudgeSpec:
    model_type: Literal["rubric_judge"]
    rubric: str
    model: str
    min_score: float
    max_score: float
    prescript: Optional[str] = None
    postscript: Optional[str] = None
    extract_variables: Optional[Dict[str, Any]] = None
    extract_judgement: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = dataclasses.asdict(self)
        # Filter out None values.
        return {k: v for k, v in result.items() if v is not None}


JudgeSpec = RubricJudgeSpec
