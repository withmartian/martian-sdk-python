"""A demo script for using the Martian SDK.

Example usage:

    uv run -m demo.main

"""
import dotenv
import logging

from martian_apart_hack_sdk.resources.judge import Judge
import openai
from openai.types.chat import (
    chat_completion,
    chat_completion_message,
    chat_completion_message_param,
)

from martian_apart_hack_sdk import judge_specs, martian_client, utils
from martian_apart_hack_sdk.judge_specs import JudgeSpec
from martian_apart_hack_sdk.models.RouterConstraints import (
    RoutingConstraint,
    CostConstraint,
    QualityConstraint,
    ConstraintValue,
    render_extra_body_router_constraint
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def managing_judges_demo(client) -> Judge:
    """Demonstrates judge management operations including creation, updating, and evaluation.

    Args:
        client: MartianClient instance
    Returns:
        Judge: The updated judge instance
    """
    rubric_judge_spec = judge_specs.RubricJudgeSpec(
        model_type="rubric_judge",
        rubric="You are helpful assistant to evaluate restaurant recommendation response.",
        model="openai/openai/gpt-4o",
        min_score=1,
        max_score=5,
    )

    judges = client.judges.list()
    print(f"Found {len(judges)} judges")
    new_judge_id = "my-rubric-judge"
    new_judge = client.judges.get(new_judge_id)
    if not new_judge:
        print("Creating rubric judge using spec")
        new_judge = client.judges.create_judge(new_judge_id, judge_spec=rubric_judge_spec)
    print(new_judge)
    print("Changing the judge spec")
    new_judge = client.judges.get(new_judge_id)
    new_judge.judgeSpec["min_score"] = 2
    new_judge.judgeSpec["model"] = "openai/openai/gpt-4o-mini"
    print(new_judge.judgeSpec)
    updated_judge = client.judges.update_judge(new_judge.id, judge_spec=JudgeSpec(**new_judge.judgeSpec))
    completion_request = {
        "model": "openai/openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": "What is the capital of France?"}],
    }
    chat_completion_response = chat_completion.ChatCompletion(
        id="123",
        choices=[
            chat_completion.Choice(
                finish_reason="stop",
                index=0,
                message=chat_completion_message.ChatCompletionMessage(
                    role="assistant",
                    content="Paris",
                ),
            )
        ],
        created=0,
        model="gpt-4o",
        object="chat.completion",
        service_tier=None,
    )
    print("Evaluating judge using id and version")
    evaluation_result = client.judges.evaluate_judge(
        updated_judge,
        completion_request=completion_request,
        completion_response=chat_completion_response,
    )
    print(evaluation_result)
    print("Evaluating judge using spec")
    evaluation_result = client.judges.evaluate_judge_spec(
        rubric_judge_spec.to_dict(),
        completion_request=completion_request,
        completion_response=chat_completion_response,
    )
    print(evaluation_result)
    return updated_judge

def openai_evaluation_demo(client, openai_client, judge, openai_completion_request):
    """Demonstrates OpenAI evaluation using a judge.

    Args:
        client: MartianClient instance
        openai_client: OpenAI client instance
        judge: Judge instance to use for evaluation
         openai_completion_request: OpenAI Request to evaluate
    """
    print("Testing OpenAI evaluation")
    # Call OpenAI to get the response
    openai_chat_completion_response = openai_client.chat.completions.create(**openai_completion_request)

    # Judge the OpenAI response using the existing judge
    print("Judging OpenAI response to 'how to grow potatos on Mars'")
    mars_evaluation_result = client.judges.evaluate_judge(
        judge,
        completion_request=openai_completion_request,
        completion_response=openai_chat_completion_response
    )
    print(mars_evaluation_result)

def managing_routers_demo(client):
    print("Let's test routers")
    print("Listing routers:")
    routers = client.routers.list()
    print("Found %d routers" % len(routers))
    base_model = "openai/openai/gpt-4o"
    new_router_id = "new-super-router"
    new_router = client.routers.get(new_router_id)
    if not new_router:
        new_router = client.routers.create_router(new_router_id, base_model, description="It's a new cool router")
    print(new_router)
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
    updated_router = client.routers.update_router(new_router_id, updated_router_spec,
                                                  description="It's a new cool router")
    print(updated_router)
    return updated_router


def train_router_demo(client, judge, openai_client):
    print("Testing router training job")
    # Test router training job
    training_requests = [
        {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is the capital of France?"}
            ]
        },
        {
            "messages": [
                {"role": "user", "content": "Explain quantum computing in simple terms."}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": "You are a coding expert."},
                {"role": "user", "content": "Write a Python function to calculate fibonacci numbers."}
            ]
        }
    ]
    # Create a new router for training
    training_router_id = "training-test-router"
    training_router = client.routers.get(training_router_id)
    if not training_router:
        print(f"Creating new router {training_router_id} for training")
        training_router = client.routers.create_router(
            training_router_id,
            base_model="openai/openai/gpt-4o",
            description="Router for training with multiple models"
        )
    # Start training job with multiple models
    print("Starting training job with multiple models")
    training_job = client.routers.run_training_job(
        router=training_router,
        judge=judge,
        llms=[
            "openai/openai/gpt-4o",
            "openai/openai/gpt-4o-mini",
            "openai/openai/gpt-4.1-mini"
        ],
        requests=training_requests
    )
    print(f"Training job started: {training_job.name}")
    # Poll the training job until completion
    try:
        final_job = client.routers.poll_training_job(
            training_job.name,
            poll_interval=10,  # Poll every 10 seconds
            poll_timeout=30 * 60  # 30 minutes timeout
        )
        print(f"Training job completed with status: {final_job.status}")
        print(f"Started at: {final_job.create_time}")
        print(f"Finished at: {final_job.update_time}")

        if final_job.status == "SUCCESS":
            # Test the trained router
            print("\nTesting trained router with OpenAI client:")
            test_request = {
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is the best way to learn Python?"}
                ]
            }

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

            # Test with different constraints
            print("\nTesting with cost constraint (0.5):")
            cost_response = openai_client.chat.completions.create(
                **test_request | {"model": training_router.name},
                extra_body={
                    **render_extra_body_router_constraint(cost_constraint)
                }
            )
            print(f"Chosen model: {cost_response.model}")
            print(f"Response: {cost_response.choices[0].message.content}")

            print("\nTesting with quality constraint (0.7):")
            quality_response = openai_client.chat.completions.create(
                **test_request | {"model": training_router.name},
                extra_body={
                    **render_extra_body_router_constraint(quality_constraint)
                }
            )
            print(f"Chosen model: {quality_response.model}")
            print(f"Response: {quality_response.choices[0].message.content}")

    except TimeoutError as e:
        print(f"Error: {e}")
        print("Training job did not complete within the timeout period")
    except Exception as e:
        print(f"Error polling training job: {e}")


def main():
    config = utils.load_config()

    client = martian_client.MartianClient(
        api_url=config.api_url,
        api_key=config.api_key,
        org_id=config.org_id,
    )

    openai_client = openai.OpenAI(
        api_key=config.api_key,
        base_url=config.openai_api_url,
    )

    # print("Getting credit balance:")
    # print(client.org_id)
    # credit_balance = client.organization.get_credit_balance()
    # print(credit_balance)

    judge = managing_judges_demo(client)

    # Prepare the OpenAI chat completion request
    openai_completion_request = {
        "model": "openai/openai/gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": "How to grow potatoes on Mars?"
            }
        ],
        "max_tokens": 100
    }

    openai_evaluation_demo(client, openai_client, judge, openai_completion_request)

    updated_router = managing_routers_demo(client)
    # uncomment if you want to just use router
    # updated_router = client.routers.get("new-super-router")

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

    # Testing router via OpenAI client:
    print("\nTesting router via OpenAI client with cost in extra_body:")
    print(cost_constraint.to_dict())
    response = openai_client.chat.completions.create(
        **openai_completion_request | {"model": updated_router.name},
        extra_body={
            **render_extra_body_router_constraint(cost_constraint)
        }
    )
    print(f"Chosen model: {response.model}")
    print(f"Response with cost=0.5: {response}")

    print("\nTesting router via OpenAI client with quality in extra_body:")
    response = openai_client.chat.completions.create(
        **openai_completion_request | {"model": updated_router.name},
        extra_body={
            **render_extra_body_router_constraint(quality_constraint)
        }
    )
    print(f"Chosen model: {response.model}")
    print(f"Response with quality=0.7: {response}")

    print(f"Testing router via run method")
    response = client.routers.run(updated_router, quality_constraint, openai_completion_request)
    print(response)

    print(f"Evaluating router {updated_router.name} response with judge: {judge.id}")
    judge_score = client.judges.evaluate_judge(judge, completion_request=openai_completion_request, completion_response=response)
    print(f"Judge score: {judge_score}")

    train_router_demo(client, judge, openai_client)


if __name__ == "__main__":
    main()
