import decimal
from dataclasses import dataclass


@dataclass(frozen=True)
class OrganizationBalance:
    credits: decimal.Decimal
