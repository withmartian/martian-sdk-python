Installation
============

Prerequisites
-------------

Before installing the Martian SDK, ensure you have:

* Python 3.9 or higher
* Git
* `uv <https://docs.astral.sh/uv/>`_ - Fast Python package installer and resolver

Project Setup
-------------

We recommend setting up your project with the following structure:

.. code-block:: none

    martian-hackathon/          # Root directory for all hackathon work
    ├── .env                    # Environment variables
    ├── .venv/                  # Virtual environment (will be created by uv, below)
    ├── martian-sdk-python/     # Cloned SDK repository
    └── project/                # Your hackathon project directory

Step-by-Step Setup
------------------

1. Create and enter the hackathon root directory:

   .. code-block:: bash

      mkdir martian-hackathon
      cd martian-hackathon

2. Clone the SDK repository:

   .. code-block:: bash

      git clone https://github.com/withmartian/martian-sdk-python.git

3. Create and activate a virtual environment in the hackathon root directory:

   On Linux/macOS:

   .. code-block:: bash

      uv venv
      source .venv/bin/activate

   On Windows:

   .. code-block:: bash

      uv venv
      .venv/Scripts/activate

4. Install the SDK in editable mode along with Jupyter:

   .. code-block:: bash

      uv pip install -e martian-sdk-python
      uv pip install jupyter

5. Create your project directory:

   .. code-block:: bash

      mkdir project

6. Create a `.env` file in the hackathon root directory with your Martian credentials:

   .. code-block:: bash

      cat > .env << EOL
      MARTIAN_API_URL=https://withmartian.com/api
      MARTIAN_API_KEY=your-api-key
      EOL

   See ``martian-sdk-python/.env.template`` for an example.

Running the Quickstart Notebook
-------------------------------

The SDK includes a Jupyter notebook that demonstrates key features and usage patterns:

1. From your hackathon parent directory, start Jupyter:

   .. code-block:: bash

      jupyter notebook

2. In Jupyter, navigate to ``martian-sdk-python/quickstart_guide.ipynb``

The quickstart notebook will walk you through:

* Setting up the Martian client
* Using the gateway to access various LLM models
* Creating and using judges
* Working with routers
* Training and evaluating models


Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

1. **ImportError: No module named 'martian_apart_hack_sdk'**

   * Make sure you've installed the package with `-e` flag
   * Check your virtual environment is activated
   * Verify the installation directory is in your Python path

2. **Authentication Errors**

   * Verify your API key is correct in the `.env` file
   * Check your API URL is correct
   * Ensure your environment variables are being loaded

3. **Virtual Environment Issues**

   * Make sure you're using the correct Python version (3.9 or higher)
   * Ensure `uv` is installed and up to date
   * Try recreating the virtual environment if issues persist