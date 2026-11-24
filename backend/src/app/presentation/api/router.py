from fastapi import APIRouter

from app.presentation.api.routes import (
    auth,
    catalogs,
    health,
    organizations,
    permissions,
    recommendations,
    roles,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(roles.router, tags=["roles"])
api_router.include_router(permissions.router, tags=["permissions"])
api_router.include_router(organizations.router, tags=["organizations"])
api_router.include_router(catalogs.router, tags=["catalogs"])
api_router.include_router(recommendations.router, tags=["recommendations"])
