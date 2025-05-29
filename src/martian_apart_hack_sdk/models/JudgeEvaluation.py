from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class JudgeEvaluation:
    """A dataclass representing the evaluation results from a judge.

    This class encapsulates the results returned when a judge evaluates an LLM response.
    The evaluation includes a numerical score, a detailed explanation for the score,
    and the cost of running the evaluation (if available).

    Attributes:
        score (float): The numerical score assigned by the judge. The valid range and 
            interpretation of this score depends on the judge's rubric specification.
            For example, a binary judge might use 0 and 1, while a scale judge might 
            use 1-5 or 1-10.
        reason (str): A detailed explanation from the judge about why they assigned 
            this score. This typically includes references to specific parts of the 
            response and how they align with or deviate from the rubric criteria.
        cost (float | None): The cost in USD of running this evaluation, if the
            system was able to calculate it. This represents the cost of the LLM 
            calls made by the judge to evaluate the response. May be None if cost
            information was not available.
    """
    score: float
    reason: str
    cost: Optional[float] = None