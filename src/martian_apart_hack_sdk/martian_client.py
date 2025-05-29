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
    """The main client for the Martian SDK.
    Use the MartianClient to interact with the Judges and Routers Clients.
    
    Args:
        api_url (str): The base URL for the Martian API.
        api_key (str): The API key to use for authentication.
        org_id (Optional[str], optional): The organization ID to use for authentication. If not provided, the organization ID will be fetched from the API.
        
    Attributes:
        organization (OrganizationClient): Client for organization-specific operations like checking credits.
        judges (JudgesClient): Client for creating, updating, and managing judges.
        routers (RoutersClient): Client for creating, updating, and managing routers.
        
    Notes:
        The MartianClient is a singleton. You should not create multiple instances of the MartianClient.
    """

    api_url: str
    api_key: str
    org_id: Optional[str] = None
    httpx_client_factory: dataclasses.InitVar[type[httpx.Client]] = httpx.Client

    def __post_init__(self, httpx_client_factory):
        if self.org_id is None:
            object.__setattr__(self, 'org_id', self._get_org_id(httpx_client_factory))
        object.__setattr__(self, '_client', httpx_client_factory(base_url=self._base_url, headers=self._headers()))
        self._init_organization_client(httpx_client_factory)

    def _init_organization_client(self, httpx_client_factory):
        organization_httpx = httpx_client_factory(base_url=f"{self.api_url}/organizations/{self.org_id}",
                                                  headers=self._headers())
        object.__setattr__(self, 'organization',
                           organization_client.OrganizationClient(organization_httpx, self._config))

    def _get_org_id(self, httpx_client_factory) -> str:
        """Get the organization ID from the API.

        Returns:
            str: The organization ID
        """
        client = httpx_client_factory(base_url=self.api_url, headers=self._headers(), follow_redirects=True)
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
    def _base_url(self) -> str:
        """Get the base URL for API requests.

        Returns:
            str: The base URL in the format "{api_url}/v1/organizations/{org_id}".
                For example, if api_url is "https://api.martian.com" and org_id is "my-org",
                the base URL would be "https://api.martian.com/v1/organizations/my-org".
        """
        return f"{self.api_url}/v1/organizations/{self.org_id}"


    @functools.cached_property
    def judges(self) -> judges_client.JudgesClient:
        return judges_client.JudgesClient(self._client, self._config)

    @functools.cached_property
    def routers(self) -> routers_client.RoutersClient:
        return routers_client.RoutersClient(self._client, self._config)

    @functools.cached_property
    def _config(self) -> utils.ClientConfig:
        return utils.ClientConfig(
            api_url=self.api_url,
            org_id=self.org_id,
            api_key=self.api_key,
        )
