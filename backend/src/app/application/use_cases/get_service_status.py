from app.domain.entities import ServiceStatus


class GetServiceStatus:
    def __init__(self, *, service_name: str, environment: str) -> None:
        self._service_name = service_name
        self._environment = environment

    def execute(self) -> ServiceStatus:
        return ServiceStatus(
            name=self._service_name,
            status="ok",
            environment=self._environment,
        )
