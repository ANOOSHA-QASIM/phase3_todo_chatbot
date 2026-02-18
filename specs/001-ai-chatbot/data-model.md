# Data Model: AI-Powered Multilingual Todo Chatbot

**Feature**: 001-ai-chatbot
**Date**: 2026-02-13
**Phase**: Phase 1 - Design

## Overview

This document defines the data models for the AI chatbot feature, including extensions to existing models and new models for conversation management.

## Entity Relationship Diagram

```
User (existing from Phase I/II)
  |
  +-- Task (extended)
  |
  +-- Conversation (new)
       |
       +-- Message (new)
```

## 1. Task Model (Extended)

**Purpose**: Represents a todo item with priority and due date support.

**Table Name**: `tasks`

**Extensions from Phase I/II**:
- Add `priority` field (enum: high, medium, low)
- Add `due_date` field (DATE type)

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique task identifier |
| user_id | String | Foreign Key, Not Null, Indexed | Owner of the task |
| title | String(200) | Not Null | Task title |
| description | String(1000) | Nullable | Optional task description |
| completed | Boolean | Not Null, Default: False | Completion status |
| priority | Enum | Nullable, Default: "medium" | Task priority (high, medium, low) |
| due_date | Date | Nullable | Optional due date (DATE type, not datetime) |
| created_at | DateTime | Not Null, Default: UTC now | Creation timestamp |
| updated_at | DateTime | Not Null, Default: UTC now | Last update timestamp |

### Priority Enum

```python
class PriorityEnum(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"
```

### Validation Rules

- `title`: 1-200 characters, required
- `description`: 0-1000 characters, optional
- `priority`: Must be one of: high, medium, low (default: medium)
- `due_date`: Must be valid date, cannot be in the past (validation at application level)
- `user_id`: Must reference existing authenticated user

### Indexes

- `user_id` (for filtering tasks by user)
- `completed` (for filtering by status)
- `due_date` (for sorting by due date)
- Composite: `(user_id, completed)` (for efficient pending/completed queries)

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field
from datetime import date, datetime
from typing import Optional
from enum import Enum

class PriorityEnum(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, nullable=False)
    priority: Optional[PriorityEnum] = Field(default=PriorityEnum.medium)
    due_date: Optional[date] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

## 2. Conversation Model (New)

**Purpose**: Represents a chat session between user and AI assistant.

**Table Name**: `conversations`

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique conversation identifier |
| user_id | String | Foreign Key, Not Null, Indexed | Owner of the conversation |
| created_at | DateTime | Not Null, Default: UTC now | Conversation start timestamp |
| updated_at | DateTime | Not Null, Default: UTC now | Last message timestamp |

### Validation Rules

- `user_id`: Must reference existing authenticated user
- Conversations are never deleted, only archived (soft delete if needed)

### Indexes

- `user_id` (for retrieving user's conversations)
- `updated_at` (for sorting conversations by recency)

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

## 3. Message Model (New)

**Purpose**: Represents a single message in a conversation (user or assistant).

**Table Name**: `messages`

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique message identifier |
| conversation_id | Integer | Foreign Key, Not Null, Indexed | Parent conversation |
| user_id | String | Foreign Key, Not Null, Indexed | Message owner (for security) |
| role | Enum | Not Null | Message sender (user or assistant) |
| content | Text | Not Null | Message content |
| created_at | DateTime | Not Null, Default: UTC now | Message timestamp |

### Role Enum

```python
class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"
```

### Validation Rules

- `conversation_id`: Must reference existing conversation
- `user_id`: Must match conversation's user_id (security check)
- `role`: Must be either "user" or "assistant"
- `content`: Cannot be empty, max length determined by database TEXT type
- Messages are immutable (never updated, only created)

### Indexes

- `conversation_id` (for retrieving conversation messages)
- `created_at` (for ordering messages chronologically)
- Composite: `(conversation_id, created_at)` (for efficient message retrieval)

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True, nullable=False)
    user_id: str = Field(index=True, nullable=False)
    role: MessageRole = Field(nullable=False)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

## Database Migration Strategy

### Migration 1: Extend Task Model

```sql
-- Add priority column
ALTER TABLE tasks
ADD COLUMN priority VARCHAR(10) DEFAULT 'medium';

-- Add due_date column
ALTER TABLE tasks
ADD COLUMN due_date DATE;

-- Create index on due_date
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- Create composite index for efficient queries
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
```

### Migration 2: Create Conversation Table

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at);
```

### Migration 3: Create Message Table

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
```

## Data Access Patterns

### Common Queries

**1. Get user's pending tasks with due dates**
```python
statement = select(Task).where(
    Task.user_id == user_id,
    Task.completed == False
).order_by(Task.due_date.asc())
```

**2. Get user's conversations ordered by recency**
```python
statement = select(Conversation).where(
    Conversation.user_id == user_id
).order_by(Conversation.updated_at.desc()).limit(20)
```

**3. Get last 20 messages for conversation**
```python
statement = select(Message).where(
    Message.conversation_id == conversation_id
).order_by(Message.created_at.desc()).limit(20)

messages = session.exec(statement).all()
messages.reverse()  # Chronological order
```

**4. Create new conversation with first message**
```python
# Create conversation
conversation = Conversation(user_id=user_id)
session.add(conversation)
session.commit()
session.refresh(conversation)

# Add first message
message = Message(
    conversation_id=conversation.id,
    user_id=user_id,
    role=MessageRole.user,
    content=user_message
)
session.add(message)
session.commit()
```

## State Transitions

### Task State Transitions

```
[Created] ---> [Pending] ---> [Completed]
                  |
                  +---> [Updated] ---> [Pending]
                  |
                  +---> [Deleted]
```

### Conversation State Transitions

```
[Created] ---> [Active] ---> [Archived (future)]
                  |
                  +---> [New Message] ---> [Active]
```

## Data Retention

- **Tasks**: Retained indefinitely (user manages deletion)
- **Conversations**: Retained indefinitely (user manages deletion)
- **Messages**: Retained indefinitely (immutable history)

**Future Consideration**: Implement soft delete or archival for old conversations.

## Security Considerations

1. **User Isolation**: All queries MUST filter by `user_id` from authenticated session
2. **Message Ownership**: Verify `message.user_id == conversation.user_id` before operations
3. **No Cross-User Access**: Never expose conversation_id or task_id without user_id validation
4. **Input Validation**: Sanitize all user input before database operations
5. **SQL Injection Prevention**: Use parameterized queries (SQLModel handles this)

## Performance Considerations

1. **Indexes**: All foreign keys and frequently queried fields are indexed
2. **Pagination**: Limit message retrieval to last 20 (configurable)
3. **Connection Pooling**: Reuse database connections via SQLModel engine
4. **Query Optimization**: Use composite indexes for common query patterns
5. **Conversation Context**: Limit to last 20 messages to reduce API payload size

## Testing Strategy

### Unit Tests

```python
def test_task_creation_with_priority():
    task = Task(
        user_id="user123",
        title="Test task",
        priority=PriorityEnum.high,
        due_date=date(2026, 2, 20)
    )
    assert task.priority == PriorityEnum.high
    assert task.due_date == date(2026, 2, 20)

def test_conversation_message_relationship():
    conversation = Conversation(user_id="user123")
    message = Message(
        conversation_id=conversation.id,
        user_id="user123",
        role=MessageRole.user,
        content="Hello"
    )
    assert message.conversation_id == conversation.id
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_create_task_with_due_date():
    # Test creating task with due date via API
    response = await client.post(
        "/api/tasks",
        json={
            "title": "Test task",
            "priority": "high",
            "due_date": "2026-02-20"
        }
    )
    assert response.status_code == 201
    assert response.json()["due_date"] == "2026-02-20"
```

## Summary

This data model extends the existing Task model with priority and due_date fields, and introduces two new models (Conversation and Message) for chat history management. All models follow SQLModel patterns, maintain stateless architecture principles, and include appropriate indexes for performance.
