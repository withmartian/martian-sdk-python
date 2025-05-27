"""Ogranization API client functions."""

import dataclasses

import httpx

from martian_apart_hack_sdk import utils
from martian_apart_hack_sdk.models.OrganizationBalance import OrganizationBalance


@dataclasses.dataclass(frozen=True)
class OrganizationClient:
    httpx: httpx.Client
    config: utils.ClientConfig

    def get_credit_balance(self):
        resp = self.httpx.get(
            '/credits'
        )
        resp.raise_for_status()
        return OrganizationBalance(**resp.json())