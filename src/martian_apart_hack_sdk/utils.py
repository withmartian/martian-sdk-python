"""Utility functions and classes for the SDK."""

import dataclasses
import json
import httpx
from typing import Dict, Any

import dotenv

def get_org_id(api_url: str, api_key: str) -> str:
    client = httpx.Client(base_url=api_url, headers={"Authorization": f"Bearer {api_key}"}, follow_redirects=True)
    response = client.get("/organizations")
    if response.status_code != 200:
        raise ValueError(f"Failed to get org id: {response.status_code} {response.text}")
    return response.json()[0]["uid"]


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
    config = dotenv.dotenv_values()

    api_url = config.get("MARTIAN_API_URL")
    api_key = config.get("MARTIAN_API_KEY")
    org_id = config.get("MARTIAN_ORG_ID")

    if api_url is None:
        raise ValueError("MARTIAN_API_URL not set in .env")
    if api_key is None:
        raise ValueError("MARTIAN_API_KEY not set in .env")
    if org_id is None:
        org_id = get_org_id(api_url, api_key)

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
