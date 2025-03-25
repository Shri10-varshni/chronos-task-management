from sqlalchemy.orm import Session
from . import models

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Task).offset(skip).limit(limit).all()

def create_task(db: Session, title: str, description: str, due_date: str, priority: str):
    db_task = models.Task(title=title, description=description, due_date=due_date, priority=priority)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, title: str, description: str, due_date: str, priority: str):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db_task.title = title
        db_task.description = description
        db_task.due_date = due_date
        db_task.priority = priority
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task
