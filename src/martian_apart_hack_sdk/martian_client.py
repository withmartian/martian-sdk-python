"""The main client for the Martian SDK."""

import dataclasses
import functools

import httpx

from martian_apart_hack_sdk import utils
from martian_apart_hack_sdk.backend_clients import judges as judges_client
from martian_apart_hack_sdk.backend_clients import routers as routers_client


@dataclasses.dataclass(frozen=True)
class MartianClient:
    """The main client for the Martian SDK.
    Use the MartianClient to interact with the Judges and Routers Clients.
    
    Args:
        api_url: The base URL for the Martian API.
        org_id: The ID of the organization to use.
        api_key: The API key to use for authentication.
    """

    api_url: str
    org_id: str
    api_key: str

    def _headers(self) -> dict[str, str]:
        return {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    @functools.cached_property
    def base_url(self) -> str:
        """Returns the base URL for the Martian API."""
        return f"{self.api_url}/v1/organizations/{self.org_id}/"

    @functools.cached_property
    def judges(self) -> judges_client.JudgesClient:
        """Returns the Martian Judges client, which can be used to create, update, and list judges."""
        return judges_client.JudgesClient(self._client, self._config)

    @functools.cached_property
    def routers(self) -> routers_client.RoutersClient:
        """Returns the Martian Routers client, which can be used to create, update, and list routers."""
        return routers_client.RoutersClient(self._client, self._config)

    @functools.cached_property
    def _client(self) -> httpx.Client:
        return httpx.Client(base_url=self.base_url, headers=self._headers())

    @functools.cached_property
    def _config(self) -> utils.ClientConfig:
        return utils.ClientConfig(
            api_url=self.api_url,
            org_id=self.org_id,
            api_key=self.api_key,
        )
