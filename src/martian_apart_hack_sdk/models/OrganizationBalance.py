import decimal
from dataclasses import dataclass


@dataclass(frozen=True)
class OrganizationBalance:
    """Represents an organization's credit balance information.

    This class provides information about the available credits in an organization's account.
    Credits are used to pay for API usage and other Martian services.

    Args:
        credits (decimal.Decimal): The current number of credits available to the organization, in USD.
        
            Credits are represented as a decimal to ensure precise accounting.
    """
    credits: decimal.Decimal
