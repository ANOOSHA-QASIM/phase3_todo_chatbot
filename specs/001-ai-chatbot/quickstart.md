# Quickstart Guide: AI-Powered Multilingual Todo Chatbot

**Feature**: 001-ai-chatbot
**Date**: 2026-02-13
**Phase**: Phase 1 - Setup Guide

## Overview

This guide walks you through setting up and testing the AI-powered multilingual todo chatbot. The system uses Cohere API for natural language understanding, MCP SDK for tool exposure, and integrates with the existing chat page.

## Prerequisites

- Python 3.11+
- Neon PostgreSQL database (from Phase I/II)
- Cohere API key
- Existing Phase I/II backend running

## 1. Environment Setup

### Install Dependencies

Add to `backend/requirements.txt`:

```txt
# AI Chatbot Dependencies (Phase III)
cohere==5.20.5              # Cohere API client
mcp[cli]>=1.2.0             # Official MCP SDK
dateparser==1.2.0           # Natural language date parsing
pytz==2024.1                # Timezone handling
langdetect==1.0.9           # Language detection (optional)
```

Install:

```bash
cd backend
pip install -r requirements.txt
```

### Configure Environment Variables

Add to `backend/.env`:

```bash
# Cohere API Configuration
COHERE_API_KEY=your_cohere_api_key_here
COHERE_MODEL=command-r-08-2024

# Optional: Conversation context settings
MAX_CONVERSATION_MESSAGES=20
```

**Get Cohere API Key**:
1. Sign up at https://cohere.com
2. Navigate to API Keys section
3. Create new API key
4. Copy and paste into `.env`

## 2. Database Migration

### Run Migrations

Execute SQL migrations to extend Task model and create new tables:

```bash
# From backend directory
python -m alembic revision --autogenerate -m "Add priority and due_date to tasks"
python -m alembic revision --autogenerate -m "Create conversations and messages tables"
python -m alembic upgrade head
```

**Manual Migration** (if alembic not configured):

```sql
-- Migration 1: Extend Task model
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) DEFAULT 'medium';
ALTER TABLE tasks ADD COLUMN due_date DATE;
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);

-- Migration 2: Create Conversation table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at);

-- Migration 3: Create Message table
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

### Verify Database

```bash
# Connect to Neon database
psql $DATABASE_URL

# Check tables exist
\dt

# Verify Task model has new columns
\d tasks

# Verify new tables
\d conversations
\d messages
```

## 3. Running the Backend

### Start FastAPI Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Verify MCP Server

Check MCP tools are registered:

```bash
curl http://localhost:8000/mcp/tools
```

**Expected Response**:
```json
{
  "tools": [
    {"name": "add_task", "description": "Creates a new task..."},
    {"name": "list_tasks", "description": "Retrieves tasks..."},
    {"name": "complete_task", "description": "Marks a task as completed..."},
    {"name": "delete_task", "description": "Permanently deletes a task..."},
    {"name": "update_task", "description": "Updates one or more fields..."}
  ]
}
```

## 4. Testing the Chat Endpoint

### Get Authentication Token

```bash
# Login to get JWT token (using existing Phase I/II auth)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

**Save the token**:
```bash
export TOKEN="your_jwt_token_here"
```

### Test 1: Add Task (English)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "Add a task to buy groceries tomorrow with high priority",
    "conversation_id": null
  }'
```

**Expected Response**:
```json
{
  "message": "Got it! Task 'Buy groceries' added with high priority for 2026-02-14 ✅",
  "conversation_id": 1,
  "tool_results": [
    {
      "tool": "add_task",
      "success": true,
      "task_id": 1
    }
  ]
}
```

### Test 2: List Tasks (Roman Urdu)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "mere tasks dikhao",
    "conversation_id": 1
  }'
```

**Expected Response** (in Roman Urdu or English):
```json
{
  "message": "Yeh hain aapke tasks:\n1. Buy groceries (high priority, due 2026-02-14)",
  "conversation_id": 1,
  "tool_results": [
    {
      "tool": "list_tasks",
      "success": true,
      "count": 1
    }
  ]
}
```

### Test 3: Complete Task

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "mark task 1 as done",
    "conversation_id": 1
  }'
```

**Expected Response**:
```json
{
  "message": "Great! Task 'Buy groceries' marked as completed ✅",
  "conversation_id": 1,
  "tool_results": [
    {
      "tool": "complete_task",
      "success": true
    }
  ]
}
```

### Test 4: Natural Language Date Parsing

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "remind me to call mom next Monday",
    "conversation_id": 1
  }'
```

**Expected Response**:
```json
{
  "message": "Got it! Task 'Call mom' added for 2026-02-17 ✅",
  "conversation_id": 1,
  "tool_results": [
    {
      "tool": "add_task",
      "success": true,
      "task_id": 2
    }
  ]
}
```

### Test 5: Urdu Script (if supported)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "کل میٹنگ ہے",
    "conversation_id": 1
  }'
```

**Note**: Urdu script support is limited. Expected accuracy: 60-75%. System uses Hindi as proxy.

## 5. Frontend Integration

### Update Chat Page API Endpoint

In `frontend/src/services/api.ts`, update the chat endpoint:

```typescript
// Change from existing endpoint to new AI chat endpoint
export async function sendChatMessage(message: string, conversationId?: number) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAuthToken()}`
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId
    })
  });

  return response.json();
}
```

### Test in Browser

1. Navigate to existing Chat Page
2. Type: "Add a task to buy groceries"
3. Verify AI responds with confirmation
4. Check that task appears in task list

## 6. Conversation History

### Get User's Conversations

```bash
curl -X GET http://localhost:8000/api/conversations \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response**:
```json
{
  "conversations": [
    {
      "id": 1,
      "created_at": "2026-02-13T10:30:00Z",
      "updated_at": "2026-02-13T14:45:00Z",
      "message_count": 8,
      "preview": "Add a task to buy groceries..."
    }
  ]
}
```

### Get Messages for Conversation

```bash
curl -X GET http://localhost:8000/api/conversations/1/messages \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response**:
```json
{
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "Add a task to buy groceries",
      "created_at": "2026-02-13T10:30:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "Got it! Task added ✅",
      "created_at": "2026-02-13T10:30:02Z"
    }
  ]
}
```

## 7. Troubleshooting

### Issue: "Cohere API key not found"

**Solution**:
```bash
# Verify .env file exists and has COHERE_API_KEY
cat backend/.env | grep COHERE_API_KEY

# Restart server after adding key
```

### Issue: "MCP tools not found"

**Solution**:
```bash
# Verify MCP server is mounted in main.py
grep "mcp" backend/app/main.py

# Check MCP tools endpoint
curl http://localhost:8000/mcp/tools
```

### Issue: "Date parsing returns None"

**Solution**:
```bash
# Test date parser directly
python -c "from dateparser import parse; print(parse('tomorrow'))"

# Verify dateparser is installed
pip show dateparser
```

### Issue: "Urdu responses not working"

**Expected Behavior**: Urdu script has 60-75% accuracy due to limited Cohere support.

**Workaround**:
- Use Roman Urdu instead (80-90% accuracy)
- Add custom mapping for common Urdu expressions
- Test with Hindi (fully supported)

### Issue: "Conversation history not loading"

**Solution**:
```bash
# Verify conversations table exists
psql $DATABASE_URL -c "\d conversations"

# Check if messages are being saved
psql $DATABASE_URL -c "SELECT * FROM messages LIMIT 5;"
```

## 8. Performance Testing

### Load Test with Apache Bench

```bash
# Test 100 concurrent requests
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" \
   -p chat_request.json -T application/json \
   http://localhost:8000/api/chat
```

**Target**: <200ms average response time

### Monitor Database Connections

```bash
# Check active connections
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"

# Verify connection pooling is working
```

## 9. Example Conversations

### English Conversation

```
User: "Add a task to finish the report by Friday"
AI: "Got it! Task 'Finish the report' added for 2026-02-14 ✅"

User: "Show my tasks"
AI: "Here are your pending tasks:
1. Finish the report (due 2026-02-14)"

User: "Change task 1 priority to high"
AI: "Updated! Task 'Finish the report' now has high priority ✅"
```

### Roman Urdu Conversation

```
User: "kal meeting hai"
AI: "Theek hai! Task 'Meeting' add kar diya 2026-02-14 ke liye ✅"

User: "mere pending tasks dikhao"
AI: "Yeh hain aapke pending tasks:
1. Meeting (due 2026-02-14)"
```

### Mixed Language Conversation

```
User: "Add task: report likhna hai"
AI: "Got it! Task 'Report likhna hai' added ✅"

User: "task 1 complete kar do"
AI: "Great! Task completed ✅"
```

## 10. Next Steps

After verifying the chatbot works:

1. Run `/sp.tasks` to generate implementation tasks
2. Implement tasks in priority order (P1 → P5)
3. Test multilingual support extensively
4. Deploy to production environment
5. Monitor Cohere API usage and costs

## Support

- **Spec**: `specs/001-ai-chatbot/spec.md`
- **Plan**: `specs/001-ai-chatbot/plan.md`
- **Data Model**: `specs/001-ai-chatbot/data-model.md`
- **API Contracts**: `specs/001-ai-chatbot/contracts/`

## Known Limitations

1. **Urdu Script**: 60-75% accuracy (use Roman Urdu for better results)
2. **Date Parsing**: May struggle with ambiguous dates (e.g., "next week" without day)
3. **Context Window**: Limited to last 20 messages per conversation
4. **Cohere Rate Limits**: Check your API plan limits

## Success Criteria Checklist

- [ ] Backend server starts without errors
- [ ] MCP tools are registered and accessible
- [ ] Chat endpoint responds to English messages
- [ ] Chat endpoint responds to Roman Urdu messages
- [ ] Tasks are created with correct priority and due_date
- [ ] Conversation history persists across sessions
- [ ] Frontend chat page integrates successfully
- [ ] Response time <200ms for 100 concurrent users
- [ ] All 5 MCP tools work correctly
