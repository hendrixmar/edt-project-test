from fastapi.routing import APIRouter

from test_project_edt.web.api import monitoring
from test_project_edt.web.api import restaurants

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(restaurants.router)
