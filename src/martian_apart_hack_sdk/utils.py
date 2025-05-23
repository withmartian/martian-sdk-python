"""Utility functions and classes for the SDK."""

import dataclasses
import json
from typing import Dict, Any

import dotenv


@dataclasses.dataclass(frozen=True)
class ClientConfig:
    api_url: str
    org_id: str
    api_key: str
    evaluation_timeout: int = 100


def load_config() -> ClientConfig:
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
