"""Utility functions and classes for the SDK."""

import dataclasses


@dataclasses.dataclass(frozen=True)
class ClientConfig:
    api_url: str
    org_id: str
    api_key: str
