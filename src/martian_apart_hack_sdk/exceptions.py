class MartianApartHackError(Exception):
    """Base exception class for all MartianApartHack SDK errors."""
    pass


class AuthenticationError(MartianApartHackError):
    """Raised when there are authentication-related issues."""
    pass


class InvalidOrganizationError(AuthenticationError):
    """Raised when the organization name is invalid or not found."""
    pass


class APIError(MartianApartHackError):
    """Raised when there are issues with API communication."""
    pass


class ValidationError(MartianApartHackError):
    """Raised when input validation fails."""
    pass


class InvalidParameterError(ValidationError):
    """Raised when required parameters are missing or invalid."""
    pass


class JSONParsingError(ValidationError):
    """Raised when there are issues parsing JSON data."""
    pass


class ConfigurationError(MartianApartHackError):
    """Raised when there are issues with SDK configuration."""
    pass


class RateLimitError(MartianApartHackError):
    """Raised when API rate limits are exceeded."""
    pass


class ResourceNotFoundError(MartianApartHackError):
    """Raised when a requested resource is not found."""
    pass

class ResourceAlreadyExistsError(MartianApartHackError):
    """Raised when attempting to create a resource that already exists."""
    pass
