from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from app.api import users, auth
from app.core.config import settings
from app.core.service_registry import forward_request
from app.api.auth import get_current_user
from app.db.models import User

router = APIRouter(prefix=settings.API_V1_STR)  # This prefixes all routes with /api/v1

# Include authentication routes
router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"],
)

# Include user routes
router.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
)

# Task service proxy routes
@router.api_route(
    "/tasks{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["tasks"],
)
async def tasks_proxy(
    request: Request,
    path: str,
    current_user: User = Depends(get_current_user),
):
    """
    Proxy all task-related requests to the task service
    """
    # Extract request details
    method = request.method
    headers = dict(request.headers)
    params = dict(request.query_params)
    
    # Add user ID to headers for service-to-service communication
    headers["X-User-ID"] = str(current_user.id)
    
    # Get request body for methods that support it
    body = None
    if method in ["POST", "PUT", "PATCH"]:
        body = await request.json()
    
    # Forward request to task service
    result = await forward_request(
        service_url=settings.TASK_SERVICE_URL,
        path=path,
        method=method,
        headers=headers,
        params=params,
        json=body
    )
    
    # Return response from task service
    return JSONResponse(
        content=result["content"],
        status_code=result["status_code"],
        headers=result["headers"]
    )