import uuid
from datetime import datetime, date, time
from typing import List, Optional
from sqlalchemy import (
    Boolean, Column, DateTime, Date, ForeignKey, 
    String, Time, Float, Text, CheckConstraint, 
    Interval, JSON, and_, TypeDecorator, CHAR, Integer
)
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression
from app.db.database import Base
from sqlalchemy.types import TypeDecorator, TEXT
import json

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses String(36) as storage, but handles UUIDs."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif isinstance(value, str):
            return str(value)
        else:
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)

class JSONArray(TypeDecorator):
    """Represents a list as a JSON string in SQLite"""
    impl = TEXT
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None
    
    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return []

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(GUID(), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(15), nullable=False, default="pending")
    priority = Column(String(10), nullable=False, default="medium")
    color_label = Column(String(20))
    
    # For SQLite, we'll use integer seconds for intervals
    estimated_duration = Column(Integer)  # Seconds
    
    deadline = Column(DateTime, index=True)
    reminder_enabled = Column(Boolean, default=True)
    reminder_time = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Using JSONArray for tags - no need for tag_list method
    tags = Column(JSONArray)
    
    is_recurring = Column(Boolean, nullable=False, default=False)
    
    # Add relationship to RecurringTask
    recurring_pattern = relationship("RecurringTask", back_populates="task", uselist=False, cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'in_progress', 'done')", name="chk_status"),
        CheckConstraint("priority IN ('low', 'medium', 'high', 'urgent')", name="chk_priority"),
    )

class RecurringTask(Base):
    __tablename__ = "recurring_tasks"
    
    id = Column(GUID(), primary_key=True, index=True, default=uuid.uuid4)
    task_id = Column(GUID(), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    
    # Type of recurrence
    recurrence_type = Column(String(10), nullable=False)
    
    # For hourly/custom recurrence
    time_interval = Column(Integer)  # Seconds
    
    # For weekly recurrence
    monday = Column(Boolean, default=False)
    tuesday = Column(Boolean, default=False)
    wednesday = Column(Boolean, default=False)
    thursday = Column(Boolean, default=False)
    friday = Column(Boolean, default=False)
    saturday = Column(Boolean, default=False)
    sunday = Column(Boolean, default=False)
    time_of_day = Column(Time)
    
    # Common fields
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    last_generated = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to Task
    task = relationship("Task", back_populates="recurring_pattern")
    
    __table_args__ = (
        CheckConstraint(
            "recurrence_type IN ('hourly', 'daily', 'weekly', 'monthly', 'custom')", 
            name="chk_recurrence_type"
        ),
    )
