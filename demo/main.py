"""A demo script for using the Martian SDK.

Example usage:

    uv run -m demo.main

"""

import json
from typing import TypedDict

import openai
from openai.types.chat import (
    chat_completion,
    chat_completion_message,
    chat_completion_message_param,
)

from martian_apart_hack_sdk import judge_specs, martian_client, utils
from martian_apart_hack_sdk.models.RouterConstraints import (
    RoutingConstraint,
    CostConstraint,
    QualityConstraint,
    ConstraintValue,
)


def main():
    config = utils.load_config()

    client = martian_client.MartianClient(
        api_url=config.api_url,
        api_key=config.api_key,
        org_id=config.org_id,
    )

    rubric_judge_spec = judge_specs.RubricJudgeSpec(
        model_type="rubric_judge",
        rubric="You are helpful assistant to evaluate restaurant recommendation response.",
        model="openai/openai/gpt-4o",
        min_score=1,
        max_score=5,
    )

    judges = client.judges.list()
    print(f"Found {len(judges)} judges")
    # print("Creating rubric judge using spec")
    # new_judge_id = "rubric-judge-test-id"
    # existing_judge = client.judges.get(new_judge_id, version=1)
    # print(existing_judge.judgeSpec)
    # new_judge = client.judges.create_judge(new_judge_id, judge_spec=rubric_judge_spec.to_dict())
    # print(new_judge)
    # print("Changing the judge spec")
    # existing_judge = client.judges.get(new_judge_id)
    # existing_judge.judgeSpec["min_score"] = 2
    # existing_judge.judgeSpec["model"] = "openai/openai/gpt-4o-mini"
    # updated_judge = client.judges.update_judge(existing_judge.id, existing_judge.judgeSpec)
    # completion_request = {
    #     "model": "openai/openai/gpt-4o-mini",
    #     "messages": [{"role": "user", "content": "What is the capital of France?"}],
    # }
    # chat_completion_response = chat_completion.ChatCompletion(
    #     id="123",
    #     choices=[
    #         chat_completion.Choice(
    #             finish_reason="stop",
    #             index=0,
    #             message=chat_completion_message.ChatCompletionMessage(
    #                 role="assistant",
    #                 content="Paris",
    #             ),
    #         )
    #     ],
    #     created=0,
    #     model="gpt-4o",
    #     object="chat.completion",
    #     service_tier=None,
    # )
    # print("Evaluating judge using id and version")
    # evaluation_result = client.judges.evaluate_judge(
    #     existing_judge,
    #     completion_request=completion_request,
    #     completion_response=chat_completion_response,
    # )
    # print(evaluation_result)
    # print("Evaluating judge using spec")
    # evaluation_result = client.judges.evaluate_judge_spec(
    #     rubric_judge_spec.to_dict(),
    #     completion_request=completion_request,
    #     completion_response=chat_completion_response,
    # )
    # print(evaluation_result)

    # Call OpenAI with the question "how to grow potatos on Mars" and judge the response with existing_judge
    # Do the real request via OpenAI SDK

    # Set OpenAI API key and endpoint (Martian API endpoint and key)
    openai_client = openai.OpenAI(
        api_key=config.api_key,
        # TODO Add field in config to be able to get openai/v1
        base_url=config.api_url + "/openai/v1"
    )

    openai_client_v2 = openai.OpenAI(
        api_key=config.api_key,
        # TODO Add field in config to be able to get openai/v2
        base_url=config.api_url + "/openai/v2"
    )

    # Prepare the OpenAI chat completion request
    openai_completion_request = {
        "model": "openai/openai/gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": "How to grow potatos on Mars?"
            }
        ],
        "max_tokens": 10
    }
    # print("Testing OpenAI evaluation")
    # # Call OpenAI to get the response
    # openai_chat_completion_response = openai_client.chat.completions.create(**openai_completion_request)
    #
    # # Judge the OpenAI response using the existing judge
    # print("Judging OpenAI response to 'how to grow potatos on Mars'")
    # mars_evaluation_result = client.judges.evaluate_judge(
    #     existing_judge,
    #     completion_request=openai_completion_request,
    #     completion_response=openai_chat_completion_response
    # )
    # print(mars_evaluation_result)

    # rubric = "You are helpful assistant to evaluate restaurant recommendation response."
    # judge_model = "openai/openai/gpt-4o"
    # new_judge = client.judges.create_rubric_judge(
    #     new_judge_id,
    #     rubric=rubric,
    #     model=judge_model,
    #     min_score=1,
    #     max_score=5,
    #     description="This is a new judge description.",
    # )
    # print(f"Created judge: {new_judge}")

    # print("Listing judges:")
    # all_judges = client.judges.list()
    # print("Found %d judges" % len(all_judges))

    # print("Getting Judge by ID and version 1")
    # judge_id = "my_cool_judge_id"
    # judge = client.judges.get(judge_id, version=1)
    # print(judge)
    # print("Refreshing Judge to get the latest version:")
    # refreshed_judge = judge.refresh()
    # print(refreshed_judge.to_dict())

    print("Let's test routers")
    print("Listing routers:")
    routers = client.routers.list()
    print("Found %d routers" % len(routers))
    base_model = "openai/openai/gpt-4o"
    # new_router = client.routers.create_router("new-super-router-id", base_model, description="It's a new cool router")
    # print(new_router)
    print("Reading router by ID:")
    print(client.routers.get("new-super-router"))
    print("Updating router:")
    # TODO Create method to generate router spec
    updated_router_spec = {
            'points': [
                {
                    'point': {
                        'x': 0.5,
                        'y': 0.5
                    },
                    'executor': {
                        'spec': {
                            'executor_type': 'ModelExecutor',
                            'model_name': "openai/openai/gpt-4o"
                        }
                    }
                },
                {
                    'point': {
                        'x': 1.0,
                        'y': 1.0
                    },
                    'executor': {
                        'spec': {
                            'executor_type': 'ModelExecutor',
                            'model_name': "openai/openai/gpt-4o"
                        }
                    }
                }
            ]
        }
    updated_router = client.routers.update_router("new-super-router-id", updated_router_spec, description="It's a new cool router")
    print(updated_router)

    # Test router run with different constraints
    completion_request = {
        "model": "openai/openai/gpt-4o",
        "messages": [{"role": "user", "content": "What is the capital of France?"}],
    }

    # Test with cost constraint only
    cost_constraint = RoutingConstraint(
        cost_constraint=CostConstraint(
            value=ConstraintValue(numeric_value=0.5)
        )
    )

    # Test with quality constraint only
    quality_constraint = RoutingConstraint(
        quality_constraint=QualityConstraint(
            value=ConstraintValue(numeric_value=0.7)
        )
    )

    cost_quality_constraint = RoutingConstraint(
        quality_constraint=QualityConstraint(
            value=ConstraintValue(numeric_value=0.7)
        ),
        cost_constraint=CostConstraint(
            value=ConstraintValue(numeric_value=0.5)
        )
    )

    # Testing router via OpenAI client:
    # print("\nTesting router via OpenAI client with cost in extra_body:")
    # print(cost_constraint.to_dict())
    # response = openai_client_v2.chat.completions.create(
    #     **openai_completion_request | {"model": updated_router.name},
    #     extra_body={
    #         "routing_constraint": cost_constraint.to_dict()
    #     }
    # )
    # print(f"Response with cost=0.5: {response.llm_response}")
    #
    # print("\nTesting router via OpenAI client with quality in extra_body:")
    # response = openai_client_v2.chat.completions.create(
    #     **openai_completion_request | {"model": updated_router.name},
    #     extra_body={
    #         "routing_constraint": quality_constraint.to_dict()
    #     }
    # )
    # print(f"Response with quality=0.7: {response}")

    print("\nTesting router via OpenAI client with both quality and cost in extra_body:")
    response = openai_client_v2.chat.completions.create(
        **openai_completion_request | {"model": updated_router.name},
        extra_body={
            "routing_constraint": cost_quality_constraint.to_dict()
        }
    )
    print(f"Response with quality=0.7 and cost=0.5: {response.llm_response['choices'][0]['message']['content']}")

    # print("\nTesting router via OpenAI client with cost model in extra_body:")
    # model_cost_constraint = RoutingConstraint(
    #     cost_constraint=CostConstraint(
    #         value=ConstraintValue(model_name="openai/openai/gpt-4o")
    #     )
    # )
    # print(model_cost_constraint.to_dict())
    # response = openai_client_v2.chat.completions.create(
    #     **openai_completion_request | {"model": updated_router.name},
    #     extra_body={
    #         "routing_constraint": model_cost_constraint.to_dict()
    #     }
    # )
    # print(f"Response with cost=model: {response}")
    #
    # print("\nTesting router via OpenAI client with quality model in extra_body:")
    # model_quality_constraint = RoutingConstraint(
    #     quality_constraint=QualityConstraint(
    #         value=ConstraintValue(model_name="openai/openai/gpt-4o")
    #     )
    # )
    # response = openai_client_v2.chat.completions.create(
    #     **openai_completion_request | {"model": updated_router.name},
    #     extra_body={
    #         "routing_constraint": model_quality_constraint.to_dict()
    #     }
    # )
    # print(f"Response with quality=model: {response}")

if __name__ == "__main__":
    main()
