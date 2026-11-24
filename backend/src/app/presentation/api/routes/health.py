from fastapi import APIRouter

from app.presentation.api.dependencies import ReadinessUseCase, ServiceStatusUseCase
from app.presentation.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check(use_case: ServiceStatusUseCase) -> HealthResponse:
    status = use_case.execute()
    return HealthResponse.model_validate(status, from_attributes=True)


@router.get("/health/ready", response_model=HealthResponse)
async def readiness_check(use_case: ReadinessUseCase) -> HealthResponse:
    status = await use_case.execute()
    return HealthResponse.model_validate(status, from_attributes=True)
