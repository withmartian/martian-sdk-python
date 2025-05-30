"""The main client for the Martian SDK."""

import dataclasses
import functools

import httpx

from martian_apart_hack_sdk import utils
from martian_apart_hack_sdk.backend_clients import judges as judges_client
from martian_apart_hack_sdk.backend_clients import organization as organization_client
from martian_apart_hack_sdk.backend_clients import routers as routers_client


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

    @functools.cached_property
    def organization(self) -> organization_client.OrganizationClient:
        """Get the organization client."""
        return organization_client.OrganizationClient(
            self._organization_client, self._config
        )

    @functools.cached_property
    def judges(self) -> judges_client.JudgesClient:
        """Get the judges client."""
        return judges_client.JudgesClient(self._client, self._config)

    @functools.cached_property
    def routers(self) -> routers_client.RoutersClient:
        """Get the routers client."""
        return routers_client.RoutersClient(self._client, self._config)

    @functools.cached_property
    def org_id(self) -> str:
        """Get the organization ID from the API."""
        response = httpx.get(
            f"{self.api_url}/organizations",
            headers=self._headers(),
            follow_redirects=True,
        )
        if response.status_code != 200:
            raise ValueError(
                f"Failed to get org id: {response.status_code} {response.text}"
            )
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
    def _organization_client(self) -> httpx.Client:
        return httpx.Client(
            base_url=f"{self.api_url}/organizations/{self.org_id}",
            headers=self._headers(),
            follow_redirects=True,
        )

    @functools.cached_property
    def _client(self) -> httpx.Client:
        return httpx.Client(
            base_url=f"{self.api_url}/v1/organizations/{self.org_id}",
            headers=self._headers(),
            follow_redirects=True,
        )

    @functools.cached_property
    def _config(self) -> utils.ClientConfig:
        return utils.ClientConfig(
            api_url=self.api_url,
            api_key=self.api_key,
        )
