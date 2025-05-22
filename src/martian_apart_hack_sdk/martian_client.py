"""The main client for the Martian SDK."""

import dataclasses
import functools

import httpx

from martian_apart_hack_sdk import utils
from martian_apart_hack_sdk.backend_clients import judges as judges_client


@dataclasses.dataclass(frozen=True)
class MartianClient:
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
        return f"{self.api_url}/v1/organizations/{self.org_id}/"

    @functools.cached_property
    def judges(self) -> judges_client.JudgesClient:
        return judges_client.JudgesClient(self._client, self._config)

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
