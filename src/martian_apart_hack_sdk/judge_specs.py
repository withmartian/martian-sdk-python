"""Specifications for judges."""

import dataclasses
from typing import Any, Dict, Literal, Optional


@dataclasses.dataclass(frozen=True)
class RubricJudgeSpec:
    """A specification for a rubric-based judge that evaluates submissions against defined criteria.

    This class defines the configuration for a judge that uses a rubric and a language model
    to evaluate submissions. The judge applies the rubric using the specified model to generate
    a numerical score within the defined range.

    Args:
        model_type (Literal["rubric_judge"]): The type of judge, must be "rubric_judge".
        rubric (str): The evaluation criteria or rubric text that the judge will use to assess submissions.
        model (str): The identifier of the language model to be used for evaluation.
        min_score (float): The minimum possible score that can be assigned.
        max_score (float): The maximum possible score that can be assigned.
        prescript (Optional[str]): Optional instructions or context to be provided before the evaluation.
        postscript (Optional[str]): Optional instructions or processing steps to be applied after the evaluation.
        extract_variables (Optional[Dict[str, Any]]): Optional configuration for extracting variables from the evaluation.
        extract_judgement (Optional[Dict[str, Any]]): Optional configuration for extracting the final judgment details.

    Examples:
        >>> rubric = '''
        ... You are tasked with evaluating whether a restaurant recommendation is good.
        ... The scoring is as follows:
        ... - 1: If the recommendation doesn't meet any of the criteria.
        ... - 2: If the recommendation meets only some small part of the criteria.
        ... - 3: If the recommendation is reasonable, but not perfect.
        ... - 4: If the recommendation is almost perfect.
        ... - 5: If the recommendation is perfect.
        ... '''
        >>> rubric_judge_spec = RubricJudgeSpec(
        ...     model_type="rubric_judge",
        ...     rubric=rubric,
        ...     model="openai/openai/gpt-4o",
        ...     min_score=1,
        ...     max_score=5,
        ... )
    """
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
