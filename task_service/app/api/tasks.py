import json
from datetime import datetime, timedelta, date, time
from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Header, Query, status, Path
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session, joinedload
from app.db.database import get_db
from app.db.models import Task, RecurringTask
from shared.schemas.tasks import (
    TaskCreate, TaskUpdate, TaskResponse, 
    TaskWithRecurringCreate, TaskWithRecurringUpdate
)
from app.cache.redis import (
    cache_task, cache_task_list, get_cached_task, 
    get_cached_task_list, invalidate_user_task_cache
)
from app.core.config import settings

router = APIRouter()

# Helper function to validate user_id from headers
def get_user_id(x_user_id: str = Header(...)) -> UUID:
    try:
        return UUID(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID",
        )

@router.post("/create-task", response_model=TaskResponse)
async def create_task(
    task_in: TaskWithRecurringCreate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_user_id)
):
    """Create a new task with optional recurring pattern"""
    try:
        print(f"Received task creation request: {task_in.dict()}")  # Debug print
        
        # Set the user_id from the header
        task_in.user_id = user_id
        
        # Create the task dict from pydantic model
        task_data = task_in.dict(exclude={"recurring_pattern"})
        
        # Tags are now handled as JSON array - no need for conversion
        # Set is_recurring based on recurring_pattern
        task_data["is_recurring"] = task_in.recurring_pattern is not None
        
        # Create the task
        db_task = Task(**task_data)
        db.add(db_task)
        db.flush()
        
        if task_in.recurring_pattern:
            recurring_data = task_in.recurring_pattern.dict()
            recurring_data["task_id"] = db_task.id
            db_recurring = RecurringTask(**recurring_data)
            db.add(db_recurring)
        
        db.commit()
        db.refresh(db_task)
        
        # Create response manually to avoid tag_list method
        response = TaskResponse(
            id=db_task.id,
            user_id=db_task.user_id,
            title=db_task.title,
            description=db_task.description,
            status=db_task.status,
            priority=db_task.priority,
            color_label=db_task.color_label,
            estimated_duration=db_task.estimated_duration,
            deadline=db_task.deadline,
            reminder_enabled=db_task.reminder_enabled,
            reminder_time=db_task.reminder_time,
            tags=db_task.tags,  # JSONArray directly returns list
            is_recurring=db_task.is_recurring,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at,
            completed_at=db_task.completed_at,
            recurring_pattern=db_task.recurring_pattern
        )
        
        return response
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/get-task/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID = Path(...),
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_user_id)
):
    """Get a single task by ID"""
    print(f"Task Service: Received get task request for task_id={task_id}, user_id={user_id}")
    
    try:
        task = db.query(Task).options(
            joinedload(Task.recurring_pattern)
        ).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()
        
        print(f"Task Service: Query result: {task is not None}")
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        
        # Create response manually
        response = TaskResponse(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            color_label=task.color_label,
            estimated_duration=task.estimated_duration,
            deadline=task.deadline,
            reminder_enabled=task.reminder_enabled,
            reminder_time=task.reminder_time,
            tags=task.tags,  # JSONArray directly returns list
            is_recurring=task.is_recurring,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at,
            recurring_pattern=task.recurring_pattern
        )
        print(f"Task Service: Generated response: {response.dict()}")
        return response
        
    except Exception as e:
        print(f"Task Service: Error occurred: {str(e)}")
        raise

@router.put("/update-task/{task_id}", response_model=TaskResponse)
async def update_task(
    task_in: TaskWithRecurringUpdate,
    task_id: UUID = Path(...),
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_user_id)
):
    """Update a task with optional recurring pattern"""
    try:
        # Get the task
        task = db.query(Task).options(
            joinedload(Task.recurring_pattern)
        ).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        
        # Update task fields
        task_data = task_in.dict(exclude={"recurring_pattern"}, exclude_unset=True)
        
        # Handle tags directly as JSON array
        if "tags" in task_data:
            task.tags = task_data.pop("tags")
        
        # Set completed_at if status changed to 'done'
        if task_data.get("status") == "done" and task.status != "done":
            task_data["completed_at"] = datetime.utcnow()
        elif task_data.get("status") and task_data["status"] != "done":
            task_data["completed_at"] = None
        
        # Update task
        for field, value in task_data.items():
            setattr(task, field, value)
        
        # Update or create recurring pattern
        if task_in.recurring_pattern:
            recurring_data = task_in.recurring_pattern.dict(exclude_unset=True)
            
            if task.recurring_pattern:
                # Update existing recurring pattern
                for field, value in recurring_data.items():
                    setattr(task.recurring_pattern, field, value)
            else:
                recurring_data["task_id"] = task.id
                db_recurring = RecurringTask(**recurring_data)
                db.add(db_recurring)
                task.is_recurring = True
        
        db.commit()
        db.refresh(task)
        
        # Create response manually
        response = TaskResponse(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            color_label=task.color_label,
            estimated_duration=task.estimated_duration,
            deadline=task.deadline,
            reminder_enabled=task.reminder_enabled,
            reminder_time=task.reminder_time,
            tags=task.tags,
            is_recurring=task.is_recurring,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at,
            recurring_pattern=task.recurring_pattern
        )
        
        return response
        
    except Exception as e:
        print(f"Error updating task: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/delete-task/{task_id}")  # Remove status_code=204
async def delete_task(
    task_id: UUID = Path(...),
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_user_id)
):
    """Delete a task"""
    
    # Get the task
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    # Store task title before deletion
    task_title = task.title
    
    # Delete the task (cascade will delete recurring pattern)
    db.delete(task)
    db.commit()

    #TODO: Invalidate cache for this task if it exists
    
    return {"message": f"Task '{task_title}' deleted successfully"}

@router.get("/list-tasks", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    deadline_before: Optional[str] = Query(None),  # Changed from datetime to str
    deadline_after: Optional[str] = Query(None),   # Changed from datetime to str
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_user_id)
):
    """List and filter tasks"""
    try:
        # Build the query
        query = db.query(Task).options(
            joinedload(Task.recurring_pattern)
        ).filter(Task.user_id == user_id)
        
        # Apply filters
        if status:
            query = query.filter(Task.status == status)
        
        if priority:
            query = query.filter(Task.priority == priority)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Task.title.ilike(search_term),
                    Task.description.ilike(search_term)
                )
            )
        
        if tags:
            tag_list = tags.split(",")
            for tag in tag_list:
                query = query.filter(Task.tags.like(f"%{tag}%"))
        
        # Parse datetime strings if provided
        if deadline_before:
            try:
                deadline_before_dt = datetime.fromisoformat(deadline_before.replace('Z', '+00:00'))
                query = query.filter(Task.deadline <= deadline_before_dt)
            except ValueError:
                pass
        
        if deadline_after:
            try:
                deadline_after_dt = datetime.fromisoformat(deadline_after.replace('Z', '+00:00'))
                query = query.filter(Task.deadline >= deadline_after_dt)
            except ValueError:
                pass
        
        # Apply sorting
        if sort_order.lower() == "asc":
            query = query.order_by(getattr(Task, sort_by).asc())
        else:
            query = query.order_by(getattr(Task, sort_by).desc())
        
        # Execute query
        tasks = query.all()
        
        # Convert to response models
        responses = []
        for task in tasks:
            responses.append(TaskResponse(
                id=task.id,
                user_id=task.user_id,
                title=task.title,
                description=task.description,
                status=task.status,
                priority=task.priority,
                color_label=task.color_label,
                estimated_duration=task.estimated_duration,
                deadline=task.deadline,
                reminder_enabled=task.reminder_enabled,
                reminder_time=task.reminder_time,
                tags=task.tags,  # Using JSONArray
                is_recurring=task.is_recurring,
                created_at=task.created_at,
                updated_at=task.updated_at,
                completed_at=task.completed_at,
                recurring_pattern=task.recurring_pattern
            ))
        
        return responses
        
    except Exception as e:
        print(f"Error in list_tasks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
