from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, database
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

class TaskCreate(BaseModel):
    title: str
    description: str
    due_date: str
    priority: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    due_date: str
    priority: str

    class Config:
        orm_mode = True

@app.post("/tasks/", response_model=TaskOut)
def create_task(task: TaskCreate, db: Session = Depends(database.get_db)):
    return crud.create_task(db, task.title, task.description, task.due_date, task.priority)

@app.get("/tasks/", response_model=List[TaskOut])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return crud.get_tasks(db, skip=skip, limit=limit)

@app.get("/tasks/{task_id}", response_model=TaskOut)
def read_task(task_id: int, db: Session = Depends(database.get_db)):
    db_task = crud.get_task(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(database.get_db)):
    db_task = crud.update_task(db, task_id, task.title, task.description, task.due_date, task.priority)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.delete("/tasks/{task_id}", response_model=TaskOut)
def delete_task(task_id: int, db: Session = Depends(database.get_db)):
    db_task = crud.delete_task(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

