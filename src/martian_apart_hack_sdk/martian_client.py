"""The main client for the Martian SDK."""

import dataclasses
import functools
from typing import Optional

import httpx

from martian_apart_hack_sdk import utils
from martian_apart_hack_sdk.backend_clients import judges as judges_client
from martian_apart_hack_sdk.backend_clients import routers as routers_client
from martian_apart_hack_sdk.backend_clients import organization as organization_client


@dataclasses.dataclass(frozen=True)
class MartianClient:
    api_url: str
    api_key: str
    org_id: Optional[str] = None

    def __post_init__(self):
        if self.org_id is None:
            object.__setattr__(self, 'org_id', self._get_org_id())

    def _get_org_id(self) -> str:
        """Get the organization ID from the API.
        
        Returns:
            str: The organization ID
        """
        client = httpx.Client(base_url=self.api_url, headers=self._headers(), follow_redirects=True)
        response = client.get("/organizations")
        if response.status_code != 200:
            raise ValueError(f"Failed to get org id: {response.status_code} {response.text}")
        return response.json()[0]["uid"]

    def _headers(self) -> dict[str, str]:
        return {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    @functools.cached_property
    def base_url(self) -> str:
        return f"{self.api_url}/v1/organizations/{self.org_id}"

    @functools.cached_property
    def judges(self) -> judges_client.JudgesClient:
        return judges_client.JudgesClient(self._client, self._config)

    @functools.cached_property
    def routers(self) -> routers_client.RoutersClient:
        return routers_client.RoutersClient(self._client, self._config)

    @functools.cached_property
    def organization(self) -> organization_client.OrganizationClient:
        client = httpx.Client(base_url=f"{self.api_url}/organizations/{self.org_id}", headers=self._headers())
        return organization_client.OrganizationClient(client, self._config)

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
