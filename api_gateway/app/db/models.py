import uuid
from datetime import datetime, time, timedelta
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, 
    String, Time, Interval, Text, CheckConstraint, TypeDecorator, CHAR
)
from app.db.database import Base

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

class User(Base):
    __tablename__ = "users"
    
    id = Column(GUID(), primary_key=True, index=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Reminder preferences
    reminder_enabled = Column(Boolean, nullable=False, default=True)
    reminder_default_time = Column(Interval, nullable=False, default=timedelta(minutes=30))
    reminder_notify_method = Column(String(10), nullable=False, default='email')
    
    # User preferences for scheduler
    theme_preference = Column(String(20), default='light')
    daily_start_time = Column(Time, default=time(9, 0))
    daily_end_time = Column(Time, default=time(17, 0))
    break_duration = Column(Interval, default=timedelta(minutes=15))
    break_frequency = Column(Interval, default=timedelta(minutes=90))
    
    is_active = Column(Boolean, nullable=False, default=True)
    role = Column(String(10), nullable=False, default='regular')
    
    __table_args__ = (
        CheckConstraint("reminder_notify_method IN ('email', 'push', 'sms')", name="chk_reminder_notify_method"),
        CheckConstraint("role IN ('admin', 'regular')", name="chk_role"),
    )
