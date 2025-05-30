JudgesClient
===========

.. currentmodule:: martian_apart_hack_sdk.backend_clients.judges

.. autoclass:: JudgesClient
   :members:

Example Usage
------------

.. code-block:: python

   from martian_apart_hack_sdk import MartianClient
   from martian_apart_hack_sdk import judge_specs

   # Create a client instance
   client = MartianClient(
       api_url="https://api.martian.com",
       api_key="your-api-key"
   )

   # Create a new judge
   judge_spec = judge_specs.RubricJudgeSpec(
       rubric="Rate the response on a scale of 1-10",
       min_score=1,
       max_score=10
   )
   judge = client.judges.create_judge(
       judge_id="my-judge",
       judge_spec=judge_spec,
       description="A judge that rates responses on a scale of 1-10"
   )

   # List all judges
   all_judges = client.judges.list()

   # Get a specific judge
   my_judge = client.judges.get("my-judge")

   # Get all versions of a judge
   judge_versions = client.judges.get_versions("my-judge")

   # Update a judge
   updated_spec = judge_specs.RubricJudgeSpec(
       rubric="Rate the response on a scale of 1-5",
       min_score=1,
       max_score=5
   )
   updated_judge = client.judges.update_judge("my-judge", updated_spec)

   # Evaluate an LLM response
   from openai.types.chat import ChatCompletion
   completion_request = {
       "messages": [{"role": "user", "content": "Tell me a joke"}]
   }
   completion_response = ChatCompletion(
       id="123",
       choices=[{"message": {"role": "assistant", "content": "Why did the chicken cross the road?"}}],
       model="gpt-4"
   )
   evaluation = client.judges.evaluate(judge, completion_request, completion_response) 