from sqlmodel import SQLModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: Optional[PriorityEnum] = Field(default=PriorityEnum.medium)
    due_date: Optional[date] = Field(default=None)  # Store as DATE type

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # This will store the user ID from JWT
    user_task_id: Optional[int] = Field(default=None, index=True)  # User-specific task ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[date] = None

class TaskRead(TaskBase):
    id: int
    user_id: str
    user_task_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

# Conversation model for chat history
class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Message model for conversation messages
class RoleEnum(str, Enum):
    user = "user"
    assistant = "assistant"

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    user_id: str = Field(index=True)
    role: RoleEnum = Field()
    content: str = Field()
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Standardized response models
class SuccessResponse(SQLModel):
    success: bool = True
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

class ErrorResponse(SQLModel):
    success: bool = False
    error: Dict[str, Any]

class PaginatedTasksResponse(SQLModel):
    success: bool = True
    data: Dict[str, Any]