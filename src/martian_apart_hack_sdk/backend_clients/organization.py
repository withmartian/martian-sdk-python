"""Organization API client functions."""

import dataclasses

import httpx

from martian_apart_hack_sdk import utils
from martian_apart_hack_sdk.models import organization_balance


@dataclasses.dataclass(frozen=True)
class OrganizationClient:
    """The client for the Martian Organization API. Use the OrganizationClient to access organization-level features.

    Normally, you don't need to create an OrganizationClient directly. Instead, use the MartianClient.organization property to access the OrganizationClient.

    Args:
        httpx (httpx.Client): The HTTP client to use for the API.
        config (utils.ClientConfig): The configuration for the API.
    """

    httpx: httpx.Client
    config: utils.ClientConfig

    def get_credit_balance(self) -> organization_balance.OrganizationBalance:
        """Get the current credit balance for the organization.

        Returns:
            OrganizationBalance: The organization's current credit balance in USD.

        Raises:
            httpx.HTTPError: If the request fails.
            httpx.TimeoutException: If the request times out.
        """
        resp = self.httpx.get("/credits")
        resp.raise_for_status()
        return organization_balance.OrganizationBalance(**resp.json())
