from pydantic import BaseModel


class HealthResponse(BaseModel):
    name: str
    status: str
    environment: str
