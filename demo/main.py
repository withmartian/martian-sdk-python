"""A demo script for using the Martian SDK.

Example usage:

    uv run -m demo.main

"""
import json
import openai
from typing import TypedDict

import dotenv
from openai.types.chat import chat_completion, chat_completion_message, chat_completion_message_param

from martian_apart_hack_sdk import judge_specs, martian_client


class _ClientConfig(TypedDict):
    martian_api_url: str
    martian_api_key: str
    martian_org_id: str


def _load_config() -> _ClientConfig:
    config = dotenv.dotenv_values()

    api_url = config.get("MARTIAN_API_URL")
    api_key = config.get("MARTIAN_API_KEY")
    org_id = config.get("MARTIAN_ORG_ID")

    if api_url is None:
        raise ValueError("MARTIAN_API_URL not set in .env")
    if api_key is None:
        raise ValueError("MARTIAN_API_KEY not set in .env")
    if org_id is None:
        raise ValueError("MARTIAN_ORG_ID not set in .env")

    return _ClientConfig(
        martian_api_url=api_url,
        martian_api_key=api_key,
        martian_org_id=org_id,
    )


def main():
    config = _load_config()

    client = martian_client.MartianClient(
        api_url=config["martian_api_url"],
        api_key=config["martian_api_key"],
        org_id=config["martian_org_id"],
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
    print("Creating rubric judge using spec")
    new_judge_id = "rubric-judge-test-id"
    existing_judge = client.judges.get(new_judge_id, version=1)
    print(existing_judge.judgeSpec)
    # new_judge = client.judges.create_judge(new_judge_id, judge_spec=rubric_judge_spec.to_dict())
    # print(new_judge)
    # print("Changing the judge spec")
    # existing_judge = client.judges.get(new_judge_id)
    # existing_judge.judgeSpec["min_score"] = 2
    # existing_judge.judgeSpec["model"] = "openai/openai/gpt-4o-mini"
    # updated_judge = client.judges.update_judge(existing_judge.id, existing_judge.judgeSpec)
    # completion_request = {
    #     "model": "openai/openai/gpt-4o-mini",
    #     "messages": [
    #         {
    #             "role": "user",
    #             "content": "What is the capital of France?"
    #         }
    #     ]
    # }
    # chat_completion_response = chat_completion.ChatCompletion(id="123",
    #                                                           choices=[
    #                                                               chat_completion.Choice(finish_reason="stop", index=0,
    #                                                                                      message=chat_completion_message.ChatCompletionMessage(
    #                                                                                          role="assistant",
    #                                                                                          content="Paris", ))],
    #                                                           created=0,
    #                                                           model="gpt-4o",
    #                                                           object="chat.completion",
    #                                                           service_tier=None)
    # print("Evaluating judge using id and version")
    # evaluation_result = client.judges.evaluate_judge(existing_judge,
    #                                                  completion_request=completion_request,
    #                                                  completion_response=chat_completion_response)
    # print(evaluation_result)
    # print("Evaluating judge using spec")
    # evaluation_result = client.judges.evaluate_judge_spec(rubric_judge_spec.to_dict(),
    #                                                       completion_request=completion_request,
    #                                                       completion_response=chat_completion_response
    #                                                       )
    # print(evaluation_result)

    # Call OpenAI with the question "how to grow potatos on Mars" and judge the response with existing_judge
    # Do the real request via OpenAI SDK

    # Set OpenAI API key and endpoint (Martian API endpoint and key)
    openai_client = openai.OpenAI(
        api_key=config["martian_api_key"],
        # TODO Add field in config to be able to get openai/v1
        base_url=config["martian_api_url"] + "/openai/v1"
    )

    # Prepare the OpenAI chat completion request
    openai_completion_request = {
        "model": "openai/openai/gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": "How to grow potatos on Mars?"
            }
        ]
    }
    print("Testing OpenAI evaluation")
    # Call OpenAI to get the response
    openai_chat_completion_response = openai_client.chat.completions.create(**openai_completion_request)

    # Judge the OpenAI response using the existing judge
    print("Judging OpenAI response to 'how to grow potatos on Mars'")
    mars_evaluation_result = client.judges.evaluate_judge(
        existing_judge,
        completion_request=openai_completion_request,
        completion_response=openai_chat_completion_response
    )
    print(mars_evaluation_result)

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


if __name__ == "__main__":
    main()
