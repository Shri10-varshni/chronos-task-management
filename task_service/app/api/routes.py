from fastapi import APIRouter
from app.core.config import settings
from app.api import tasks

router = APIRouter(prefix=settings.API_V1_STR)

# Include task routes
router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["tasks"],
)