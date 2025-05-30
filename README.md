# Martian Python SDK

[SDK Documentation](https://withmartian.github.io/martian-sdk-python/)

The Martian Python SDK provides a simple interface to manage judges and routers for LLM evaluation and routing. This SDK allows you to create, update, and manage judges for evaluating LLM responses, as well as routers for directing traffic between different models.

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Git
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver

### Project Setup

We recommend setting up your project with the following structure:
```
martian-hackathon/          # Root directory for all hackathon work
├── .env                    # Environment variables
├── .venv/                  # Virtual environment (will be created by uv, below)
├── martian-sdk-python/     # Cloned SDK repository
└── project/               # Your hackathon project directory
```

1. Create and enter the hackathon root directory:
   ```bash
   mkdir martian-hackathon
   cd martian-hackathon
   ```

2. Clone the SDK repository:
   ```bash
   git clone https://github.com/withmartian/martian-sdk-python.git
   ```

3. Create and activate a virtual environment in the hackathon root directory:
   ```bash
   uv venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate  # On Windows
   ```

4. Install the SDK in editable mode along with Jupyter:
   ```bash
   uv pip install -e martian-sdk-python
   uv pip install jupyter
   ```

5. Create your project directory:
   ```bash
   mkdir project
   ```

6. Create a `.env` file in the hackathon root directory with your Martian credentials:
   ```bash
   cat > .env << EOL
   MARTIAN_API_URL=https://withmartian.com/api
   MARTIAN_API_KEY=your-api-key
   EOL
   ```

   (See `martian-sdk-python/.env.template`)

### Running the Quickstart Guide

The SDK includes a Jupyter notebook that demonstrates key features and usage patterns:

1. From your hackathon parent directory, start Jupyter:
   ```bash
   jupyter notebook
   ```

2. In Jupyter, navigate to `../martian-sdk-python/quickstart_guide.ipynb`

The quickstart guide will walk you through:
- Setting up the Martian client
- Using the gateway to access various LLM models
- Creating and using judges
- Working with routers
- Training and evaluating models


## SDK Reference Docs

For more details, [check out the Martian Python SDK Documentation](https://withmartian.github.io/martian-sdk-python/)
