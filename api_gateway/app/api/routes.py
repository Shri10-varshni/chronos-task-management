from fastapi import APIRouter, Depends, Request, Response, HTTPException, status, Body
from fastapi.responses import JSONResponse
from app.api import users, auth
from app.core.config import settings
from app.core.service_registry import forward_request
from app.api.auth import get_current_user
from app.db.models import User
# Import Task Service schemas to reuse them
from shared.schemas.tasks import (
    TaskWithRecurringCreate, TaskWithRecurringUpdate,
    TaskResponse
)
from typing import Dict, Any, Optional, List
from datetime import datetime, date, time
import json

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

def parse_datetime(dt_str: str) -> datetime:
    """Parse datetime string with optional timezone"""
    if dt_str.endswith('Z'):
        dt_str = dt_str[:-1]  # Remove 'Z' suffix
    return datetime.fromisoformat(dt_str)

# Task management endpoints under /task-management
# Task service proxy routes with explicit endpoints
@router.post("/tasks/create", response_model=TaskResponse)
async def create_task(
    task_data: TaskWithRecurringCreate,  # Use Task Service schema
    current_user: User = Depends(get_current_user),
):
    """Create a new task"""
    headers = {"X-User-ID": str(current_user.id)}
    
    # Convert Pydantic model to dict and handle datetime serialization
    task_dict = json.loads(
        task_data.json(exclude_none=True),
        object_hook=lambda d: {
            k: parse_datetime(v) if isinstance(v, str) and "T" in v else v
            for k, v in d.items()
        }
    )
    
    result = await forward_request(
        service_url=settings.TASK_SERVICE_URL,
        path="/tasks/create-task",
        method="POST",
        headers=headers,
        json_data=task_dict  # Changed from json to json_data
    )
    
    return result["content"]

@router.get("/tasks/list", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    tags: Optional[str] = None,
    deadline_before: Optional[str] = None,  # Changed from datetime to str
    deadline_after: Optional[str] = None,   # Changed from datetime to str
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_user: User = Depends(get_current_user),
):
    """List all tasks with filtering"""
    headers = {"X-User-ID": str(current_user.id)}
    
    # Clean up None values and empty strings from params
    params = {
        k: v for k, v in locals().items() 
        if v is not None and v != "" and k not in ['current_user', 'headers']
    }
    
    result = await forward_request(
        service_url=settings.TASK_SERVICE_URL,
        path="/tasks/list-tasks",
        method="GET",
        headers=headers,
        params=params
    )
    
    # Ensure we return a list
    content = result.get("content", [])
    if not isinstance(content, list):
        content = []
    
    return content

@router.get("/tasks/{task_id}", tags=["tasks"])
async def get_task(
    request: Request,
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    # Add debug logging
    print(f"Getting task with ID: {task_id}")
    return await forward_task_request(request, f"/get-task/{task_id}", current_user)

@router.put("/tasks/{task_id}/update-task", response_model=TaskResponse, tags=["tasks"])
async def update_task(
    task_id: str,
    task_data: TaskWithRecurringUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update a task with optional recurring pattern"""
    try:
        headers = {"X-User-ID": str(current_user.id)}
        
        # Convert task data to dict and handle datetime serialization
        task_dict = json.loads(
            task_data.json(exclude_none=True),
            object_hook=lambda d: {
                k: parse_datetime(v) if isinstance(v, str) and "T" in v else v
                for k, v in d.items()
            }
        )
        
        print(f"Updating task {task_id}")
        print(f"Update data: {task_dict}")
        
        result = await forward_request(
            service_url=settings.TASK_SERVICE_URL,
            path=f"/tasks/update-task/{task_id}",
            method="PUT",
            headers=headers,
            json_data=task_dict
        )
        
        if not result or "content" not in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No response from task service"
            )
            
        return result["content"]
        
    except Exception as e:
        print(f"Error updating task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating task: {str(e)}"
        )

@router.delete("/tasks/{task_id}/delete-task", tags=["tasks"])
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a task"""
    try:
        headers = {"X-User-ID": str(current_user.id)}
        
        result = await forward_request(
            service_url=settings.TASK_SERVICE_URL,
            path=f"/tasks/delete-task/{task_id}",
            method="DELETE",
            headers=headers
        )
        
        return result["content"]  # This will contain the success message
        
    except Exception as e:
        print(f"Error deleting task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting task: {str(e)}"
        )

async def forward_task_request(request: Request, path: str, current_user: User):
    """Helper function to forward requests to task service"""
    headers = dict(request.headers)
    headers["X-User-ID"] = str(current_user.id)
    
    # Add debug logging
    print(f"Forwarding request to path: {path}")
    print(f"Headers: {headers}")
    
    result = await forward_request(
        service_url=settings.TASK_SERVICE_URL,
        path=f"/tasks{path}",
        method=request.method,
        headers=headers,
        params=dict(request.query_params),
        json_data=await request.json() if request.method in ["POST", "PUT", "PATCH"] else None  # Changed from json to json_data
    )
    
    # Add debug logging
    print(f"Received response: {result}")
    
    return JSONResponse(
        content=result["content"],
        status_code=result["status_code"],
        headers=result["headers"]
    )