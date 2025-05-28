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
        prescript (Optional[str]): Optional instructions or context to be provided before the evaluation. This is included in the prompt that is sent to the judge, before the rubric.
        postscript (Optional[str]): Optional instructions or processing steps to be applied after the evaluation. This is included in the prompt that is sent to the judge, after the rubric.
        extract_variables (Optional[Dict[str, Any]]): Optional configuration for extracting variables from the evaluation.
        extract_judgement (Optional[Dict[str, Any]]): Optional configuration for extracting the final judgment details.

    Notes:
        The default prescript is:
            
            ```
            You are a helpful assistant that scores responses between ${min_score} and ${max_score} according to the following rubric:
            ```

            `${min_score}` and `${max_score}` are replaced with the `min_score` and `max_score` args.

        The default postscript is:

            ```
            Here's the conversation you are judging:
            <content>
            ${content}
            </content>

            Please evaluate the assistant's response in the conversation above according to the rubric.
            Think step-by-step to produce a score, and please provide a rationale for your score.
            Your score should be between ${min_score} and ${max_score}.

            Your response MUST include:
            1. A <rationale>...</rationale> tag containing your explanation
            2. A <score>...</score> tag containing your numerical score
            ```

            `${content}` is replaced with the content of the conversation you are judging.

            `${min_score}` and `${max_score}` are replaced with the `min_score` and `max_score` args.


        The full judging prompt looks like:
            {filled_prescript}

            <rubric>
            {filled_rubric}
            </rubric>

            {filled_postscript}

    Warning:
        If you override the default prescript or postscript, you must include the `${min_score}`, `${max_score}`, and `${content}` tags in the prompt,
        and instruct the judge to include the <rationale> and <score> tags in the response.
        We do not recommend overriding the default prescript or postscript.



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
        """Convert the judge specification to a dictionary format suitable for API requests.

        This method serializes the specification, removing any None values to ensure
        only meaningful configuration is sent to the API.

        Returns:
            Dict[str, Any]: A dictionary containing all non-None attributes of this
                specification, ready to be sent to the API.
        """
        result = dataclasses.asdict(self)
        # Filter out None values.
        return {k: v for k, v in result.items() if v is not None}


# For backward compatibility and future extensibility, JudgeSpec is an alias for RubricJudgeSpec.
# If we add other types of judges in the future, this will become a Union type.
JudgeSpec = RubricJudgeSpec
