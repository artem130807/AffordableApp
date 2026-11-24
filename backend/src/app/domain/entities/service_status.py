from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ServiceStatus:
    """Framework-independent representation of the service state."""

    name: str
    status: str
    environment: str
