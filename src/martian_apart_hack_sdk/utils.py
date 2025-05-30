"""Utility functions and classes for the SDK."""

import dataclasses
import json
from typing import Any, Dict

import dotenv


@dataclasses.dataclass(frozen=True)
class ClientConfig:
    api_url: str
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

    if api_url is None:
        raise ValueError("MARTIAN_API_URL not set in .env")
    if api_key is None:
        raise ValueError("MARTIAN_API_KEY not set in .env")

    return ClientConfig(
        api_url=api_url,
        api_key=api_key,
    )


def get_evaluation_json_payload(data: Dict[str, Any]) -> Dict[str, str]:
    """Convert data dictionary to JSON payload format expected by the API.

    Args:
        data: Dictionary to convert to JSON payload

    Returns:
        Dictionary with jsonPayload field containing JSON string
    """
    return {"jsonPayload": json.dumps(data)}
