from app.application.ports.health import DatabaseHealthPort
from app.domain.entities import ServiceStatus
from app.domain.exceptions import ServiceUnavailableError


class CheckReadiness:
    def __init__(
        self,
        database: DatabaseHealthPort,
        *,
        service_name: str,
        environment: str,
    ) -> None:
        self.database = database
        self.service_name = service_name
        self.environment = environment

    async def execute(self) -> ServiceStatus:
        if not await self.database.is_ready():
            raise ServiceUnavailableError("База данных недоступна")
        return ServiceStatus(
            name=self.service_name,
            status="ready",
            environment=self.environment,
        )
