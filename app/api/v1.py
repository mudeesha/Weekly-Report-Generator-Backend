from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.health.router import router as health_router
from app.modules.projects.router import router as projects_router
from app.modules.reports.router import router as reports_router
from app.modules.users.router import router as users_router
from app.modules.dashboard.router import router as dashboard_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(projects_router)
api_router.include_router(reports_router)
api_router.include_router(dashboard_router)