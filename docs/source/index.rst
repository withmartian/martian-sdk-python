Martian Python SDK
==================

This page explains basic usage and key concepts of the Martian SDK.
For more detailed documentation and actual code examples, see:

* the quickstart notebook in the SDK directory (`martian-sdk-python/quickstart_guide.ipynb`)
* the :doc:`api/index` page for detailed documentation of all SDK features

.. toctree::
   :maxdepth: 2
   :hidden:

   installation
   api/martian_client
   api/judge_specs
   api/judges_client
   api/judge
   api/routers_client
   api/router
   api/routing_constraints

The Martian Client
-----------------

The main entry point to the SDK is the :class:`MartianClient`.
It provides access to the :class:`JudgesClient` and :class:`RoutersClient`.

If you followed the :doc:`installation` instructions,
you should have your API key and endpoint URL in an ``.env`` file.
With that, you can create a MartianClient instance like this:

.. code-block:: python

   from martian_apart_hack_sdk import MartianClient, utils

   # Create a client instance
   config = utils.load_config()
   
   client = MartianClient(
      api_url=config.api_url,
      api_key=config.api_key,
   )


Routers
-------

Routers are the heart of the Martian platform.
They are used to direct requests to different models,
selecting the best model based on the content of the request
and the cost/quality constraints you specify.
A well-trained router can significantly improve the quality of your responses,
while reducing your costs.

Training a Router
^^^^^^^^^^^^^^^^^

When a router is first created,
before training, it sends requests to a single model.

To train a router, you need to provide it with:

* a judge
* a set of requests
* a list of models

The Martian platform will send your requests to each model,
and the judge will evaluate the quality of the responses.
The judge's evaluation is used to train the router to understand the cost/quality trade-offs for various types of requests for each model.
This allows the router to select the best model for each request, based on the cost/quality constraints you specify.

For more details on creating, training, and using routers,
see the :class:`RoutersClient` section.


Judges
------

Judges are used to evaluate the quality of responses during training.
The evaluation criteria is determined by you in a Judge Spec.

There are several types of Judge Spec, but the most common is the `RubricJudgeSpec`,
which evaluates responses based on a natural language rubric
that grades responses on an integer scale (e.g. 1-5).
You specify the criteria for each grade in the rubric,
and the judge will use this rubric to evaluate the quality of the responses.

You can manually run evaluation on a Judge or Judge Spec to test the judge's behavior,
but the real power of judges is in training routers.
Pass a Judge and a set of requests to the :meth:`RoutersClient.run_training_job` method,
and the router will use the judge to learn how each model performs on each type of request.

For more details on creating, training, and using judges,
see the :class:`JudgesClient` section.

Learn More
----------

If you haven't done so,
see the :doc:`installation` page for instructions on how to install the SDK.
Then, walk through the Quickstart Notebook in the SDK directory:

.. code-block:: bash

   cd martian-sdk-python
   jupyter notebook quickstart_guide.ipynb


For details on the Martian SDK API,
see the :doc:`api/index` page.



