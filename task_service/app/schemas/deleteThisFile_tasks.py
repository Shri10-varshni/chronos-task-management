#This was moved to shared schema

from datetime import datetime, date, time
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from pydantic import BaseModel, Field, validator

# Base Task Schema
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "pending"
    priority: str = "medium"
    color_label: Optional[str] = None
    estimated_duration: Optional[int] = None  # Seconds
    deadline: Optional[datetime] = None
    reminder_enabled: bool = True
    reminder_time: Optional[datetime] = None
    tags: Optional[List[str]] = None
    is_recurring: bool = False
    task_metadata: Optional[Dict[str, Any]] = None  # renamed from metadata
    
    @validator('status')
    def validate_status(cls, v):
        if v not in ['pending', 'in_progress', 'done']:
            raise ValueError('Status must be pending, in_progress, or done')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in ['low', 'medium', 'high', 'urgent']:
            raise ValueError('Priority must be low, medium, high, or urgent')
        return v

# Schema for creating a task
class TaskCreate(TaskBase):
    user_id: Optional[UUID] = None  # Will be set from the token

# Schema for updating a task
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    color_label: Optional[str] = None
    estimated_duration: Optional[int] = None
    deadline: Optional[datetime] = None
    reminder_enabled: Optional[bool] = None
    reminder_time: Optional[datetime] = None
    tags: Optional[List[str]] = None
    task_metadata: Optional[Dict[str, Any]] = None  # renamed from metadata
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None and v not in ['pending', 'in_progress', 'done']:
            raise ValueError('Status must be pending, in_progress, or done')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v is not None and v not in ['low', 'medium', 'high', 'urgent']:
            raise ValueError('Priority must be low, medium, high, or urgent')
        return v

# Recurring Task Schemas
class RecurringTaskBase(BaseModel):
    recurrence_type: str
    time_interval: Optional[int] = None  # Seconds
    monday: Optional[bool] = False
    tuesday: Optional[bool] = False
    wednesday: Optional[bool] = False
    thursday: Optional[bool] = False
    friday: Optional[bool] = False
    saturday: Optional[bool] = False
    sunday: Optional[bool] = False
    time_of_day: Optional[time] = None
    start_date: date
    end_date: Optional[date] = None
    
    @validator('recurrence_type')
    def validate_recurrence_type(cls, v):
        if v not in ['hourly', 'daily', 'weekly', 'monthly', 'custom']:
            raise ValueError('Recurrence type must be hourly, daily, weekly, monthly, or custom')
        return v

class RecurringTaskCreate(RecurringTaskBase):
    pass

class RecurringTaskUpdate(BaseModel):
    recurrence_type: Optional[str] = None
    time_interval: Optional[int] = None
    monday: Optional[bool] = None
    tuesday: Optional[bool] = None
    wednesday: Optional[bool] = None
    thursday: Optional[bool] = None
    friday: Optional[bool] = None
    saturday: Optional[bool] = None
    sunday: Optional[bool] = None
    time_of_day: Optional[time] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    @validator('recurrence_type')
    def validate_recurrence_type(cls, v):
        if v is not None and v not in ['hourly', 'daily', 'weekly', 'monthly', 'custom']:
            raise ValueError('Recurrence type must be hourly, daily, weekly, monthly, or custom')
        return v

# Complete Task Schemas for responses
class RecurringTaskResponse(RecurringTaskBase):
    id: UUID
    task_id: UUID
    last_generated: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class TaskResponse(TaskBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    recurring_pattern: Optional[RecurringTaskResponse] = None
    
    class Config:
        orm_mode = True

# Schemas for paginated responses
class PaginatedResponse(BaseModel):
    items: List[TaskResponse]
    total: int
    page: int
    page_size: int
    pages: int

# Schema for task creation with recurring pattern
class TaskWithRecurringCreate(TaskCreate):
    recurring_pattern: Optional[RecurringTaskCreate] = None

# Schema for task update with recurring pattern
class TaskWithRecurringUpdate(TaskUpdate):
    recurring_pattern: Optional[RecurringTaskUpdate] = None