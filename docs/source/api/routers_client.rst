.. currentmodule:: martian_apart_hack_sdk.backend_clients.routers


RoutersClient
=============

The ``RoutersClient`` provides methods for creating, managing, and using routers. Routers are used to intelligently direct traffic between different LLM models based on your requirements.

Router Lifecycle
----------------

1. **Initial Creation**: When a router is first created with ``create_router``, it only routes to a single model (specified by ``base_model``).
2. **Training**: To enable routing between multiple models, use ``run_training_job`` to train the router with a set of models.
3. **Routing**: After training, the router can intelligently route between any of the models it was trained on.

Creating a Router
-----------------

.. code-block:: python

    router = client.routers.create_router(
        router_id="my-router",
        base_model="anthropic/anthropic/claude-3-opus-latest",  # Initial model before training
        description="Routes between different models based on quality and cost"
    )

Training a Router
-----------------

To enable routing between multiple models, train the router using ``run_training_job``. You can specify which models to include:

.. code-block:: python

    from martian_apart_hack_sdk.models.llm_models import ANTHROPIC_MODELS, OPENAI_MODELS

    # Train on all Anthropic and OpenAI models
    training_job = client.routers.run_training_job(
        router=router,
        judge=quality_judge,
        llms=list(ANTHROPIC_MODELS | OPENAI_MODELS),  # Combine model sets using set operations
        requests=example_requests
    )

    # Or train on specific models
    training_job = client.routers.run_training_job(
        router=router,
        judge=quality_judge,
        llms=[
            "anthropic/anthropic/claude-3-opus-latest",
            "openai/openai/gpt-4o",
            "together/mistralai/Mistral-Small-24B-Instruct-2501"
        ],
        requests=example_requests
    )

Available Model Sets
--------------------

The SDK provides predefined sets of models in ``martian_apart_hack_sdk.models.llm_models``:

- ``OPENAI_MODELS``: All OpenAI models (GPT-4 variants)
- ``ANTHROPIC_MODELS``: All Anthropic models (Claude variants)
- ``TOGETHER_MODELS``: All models available through Together
- ``GEMINI_MODELS``: All Google Gemini models
- ``ALL_MODELS``: Union of all available models

You can use these sets to easily specify which models to include in router training:

.. code-block:: python

    from martian_apart_hack_sdk.models.llm_models import ALL_MODELS

    # Train on every available model
    training_job = client.routers.run_training_job(
        router=router,
        judge=quality_judge,
        llms=list(ALL_MODELS),  # Convert set to list
        requests=example_requests
    )


.. autoclass:: RoutersClient
   :members:

Example Usage
-------------

.. code-block:: python

   from martian_apart_hack_sdk import MartianClient
   from martian_apart_hack_sdk.models.RouterConstraints import RoutingConstraint

   # Create a client instance
   client = MartianClient(
       api_url="https://api.martian.com",
       api_key="your-api-key"
   )

   # Create a new router (initially routes only to the base model)
   router = client.routers.create_router(
       router_id="my-router",
       base_model="anthropic/anthropic/claude-3-opus-latest",
       description="A router for intelligent model selection"
   )

   # List all routers
   all_routers = client.routers.list()

   # Get a specific router
   my_router = client.routers.get("my-router")

   # Train the router with multiple models
   training_requests = [
       {
           "messages": [
               {"role": "user", "content": "What is Python?"}
           ]
       },
       {
           "messages": [
               {"role": "system", "content": "You are a helpful assistant."},
               {"role": "user", "content": "Explain machine learning."}
           ]
       }
   ]

   # Train the router to work with multiple models
   training_job = client.routers.run_training_job(
       router=router,
       judge=quality_judge,
       llms=[
           "anthropic/anthropic/claude-3-opus-latest",
           "openai/openai/gpt-4o",
           "together/mistralai/Mistral-Small-24B-Instruct-2501"
       ],
       requests=training_requests
   )

   # Wait for training to complete
   final_job = client.routers.wait_training_job(
       job_name=training_job.name,
       poll_interval=15,    # Check every 15 seconds
       poll_timeout=600     # Wait up to 10 minutes
   )

   # After training, use the router with constraints
   completion_request = {
       "messages": [{"role": "user", "content": "Tell me a joke"}]
   }
   routing_constraint = RoutingConstraint(
       quality_vs_latency=0.8  # Prefer quality over latency
   )
   response = client.routers.run(
       router=my_router,
       routing_constraint=routing_constraint,
       completion_request=completion_request
   ) 