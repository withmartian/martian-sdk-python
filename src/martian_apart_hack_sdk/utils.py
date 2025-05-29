"""Utility functions and classes for the SDK."""

import dataclasses
import json
from typing import Dict, Any
from pathlib import Path

import dotenv

@dataclasses.dataclass(frozen=True)
class ClientConfig:
    api_url: str
    org_id: str
    api_key: str
    evaluation_timeout: int = 100

    @property
    def openai_api_url(self) -> str:
        """Get the OpenAI API URL.
        
        Returns:
            str: The OpenAI API URL constructed from the base API URL
        """
        return f"{self.api_url}/openai/v2"

    


def load_config() -> ClientConfig:
    # Try current directory first
    config = dotenv.dotenv_values()
    
    # If not found, try parent directory
    if not config:
        parent_env = Path("../.env")
        if parent_env.exists():
            config = dotenv.dotenv_values(parent_env)
    
    # If still not found, try parent's parent directory
    if not config:
        parent_parent_env = Path("../../.env")
        if parent_parent_env.exists():
            config = dotenv.dotenv_values(parent_parent_env)

    api_url = config.get("MARTIAN_API_URL")
    api_key = config.get("MARTIAN_API_KEY")
    org_id = config.get("MARTIAN_ORG_ID")

    if api_url is None:
        raise ValueError("MARTIAN_API_URL not set in .env")
    if api_key is None:
        raise ValueError("MARTIAN_API_KEY not set in .env")

    return ClientConfig(
        api_url=api_url,
        api_key=api_key,
        org_id=org_id,
    )


def get_evaluation_json_payload(data: Dict[str, Any]) -> Dict[str, str]:
    """Convert data dictionary to JSON payload format expected by the API.

    Args:
        data: Dictionary to convert to JSON payload

    Returns:
        Dictionary with jsonPayload field containing JSON string
    """
    return {"jsonPayload": json.dumps(data)}
