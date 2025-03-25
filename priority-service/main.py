from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from . import priority, cache

app = FastAPI()

cache_client = cache.Cache()

class TaskPriorityRequest(BaseModel):
    task_id: int
    due_date: str
    description: str

class TaskPriorityResponse(BaseModel):
    task_id: int
    priority: str

@app.post("/priority/", response_model=TaskPriorityResponse)
def calculate_priority(task: TaskPriorityRequest):
    # Check if we have cached priority
    cached_priority = cache_client.get(f"task_priority_{task.task_id}")
    
    if cached_priority:
        return TaskPriorityResponse(task_id=task.task_id, priority=cached_priority["priority"])

    # Otherwise, calculate the priority
    priority_value = priority.calculate_priority(task.due_date, task.description)

    # Cache the result
    cache_client.set(f"task_priority_{task.task_id}", {"priority": priority_value})

    return TaskPriorityResponse(task_id=task.task_id, priority=priority_value)
