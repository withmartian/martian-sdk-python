MartianClient
============

.. currentmodule:: martian_apart_hack_sdk.martian_client

.. autoclass:: MartianClient
   :members:

Example Usage
------------

.. code-block:: python

   from martian_apart_hack_sdk import MartianClient

   # Create a client instance
   client = MartianClient(
       api_url="https://api.martian.com",
       api_key="your-api-key",
       org_id="your-org-id"  # Optional - will be fetched from API if not provided
   )

   # Access the judges client
   judges = client.judges

   # Access the routers client
   routers = client.routers

   # Access organization features
   balance = client.organization.get_credit_balance() 