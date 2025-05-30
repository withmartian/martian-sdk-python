Judge Specifications
===================

.. currentmodule:: martian_apart_hack_sdk.judge_specs

The Martian SDK provides several types of judges that can be used to evaluate model outputs. Each judge type has its own specification class that defines its behavior.

RubricJudgeSpec
--------------

.. autoclass:: RubricJudgeSpec
   :members:
   :exclude-members: to_dict

Example Usage
~~~~~~~~~~~~

.. code-block:: python

   from martian_apart_hack_sdk import judge_specs

   # Create a rubric judge that evaluates responses on a scale of 1-5
   rubric = """
   You are tasked with evaluating whether a restaurant recommendation is good.
   The scoring is as follows:
   - 1: If the recommendation doesn't meet any of the criteria.
   - 2: If the recommendation meets only some small part of the criteria.
   - 3: If the recommendation is reasonable, but not perfect.
   - 4: If the recommendation is almost perfect.
   - 5: If the recommendation is perfect.
   """
   
   judge_spec = judge_specs.RubricJudgeSpec(
       model_type="rubric_judge",
       rubric=rubric,
       model="openai/openai/gpt-4o",
       min_score=1,
       max_score=5,
   )

Other Judge Types
----------------

The following judge types are also available but are primarily used internally or in advanced use cases:

- **GoldMatchJudge**: Similar to RubricJudge but specialized for comparing responses against known good answers.
- **MaxScoreJudge**: Takes multiple judges and returns the highest score among them.
- **MinScoreJudge**: Takes multiple judges and returns the lowest score among them.
- **ConstantJudge**: Always returns a fixed score and reason.
- **AverageScoreJudge**: Takes multiple judges and returns their average score.
- **SumJudge**: Takes multiple judges and returns the sum of their scores.
- **ExactMatchJudge**: Checks if responses exactly match a set of known answers.
- **CaseJudge**: Applies different judges based on conditional logic.

For most use cases, the RubricJudgeSpec is recommended as it provides the most flexibility and natural language understanding capabilities. 