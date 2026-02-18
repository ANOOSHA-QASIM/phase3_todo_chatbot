---
id: 0005
title: implement user task id enhancement
stage: green
date: 2026-02-14
surface: agent
model: claude-opus-4-6
feature: 001-ai-chatbot
branch: 001-ai-chatbot
user: system
command: /sp.implement
labels: ["database", "api", "mcp", "enhancement", "user-task-id"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/models.py
  - backend/routes/tasks.py
  - backend/app/mcp/tools.py
  - backend/migrate_user_task_id.py
  - backend/test_user_task_id.py
  - frontend/types/todo.ts
  - frontend/lib/api.ts
  - USER_TASK_ID_IMPLEMENTATION.md
tests:
  - backend/test_user_task_id.py (integration test - PASSED)
---

## Prompt

Implement directly now.

Do NOT create a new spec.
Do NOT use /sp.specify.
Do NOT use planning mode.

This is an enhancement of the existing system, not a new feature spec.

Modify the existing Task model and MCP tools directly.

Requirements:

1) Add a new column:
   user_task_id (int, indexed)

2) user_task_id must:
   - Start from 1 for each user
   - Increment per user
   - Be calculated using max(user_task_id where user_id = current_user) + 1

3) Modify:
   - add_task
   - delete_task
   - update_task
   - complete_task

4) All operations must:
   - Work using user_task_id (optional)
   - OR title (optional, case-insensitive exact match)
   - If both provided → prioritize user_task_id

5) Always filter by user_id.

6) Do not use database primary key id for user operations.

7) Use SQLModel best practices:
   - select()
   - session.exec()

Implement clean production-ready code.
No spec creation.

## Response snapshot

Successfully implemented user_task_id enhancement across the entire stack:

**Database Layer:**
- Added user_task_id column to Task model with index
- Created migration script that successfully migrated 3 users with 6 tasks
- Each user's tasks now have sequential IDs starting from 1

**Backend API Routes:**
- Modified create_task to calculate next user_task_id using max(user_task_id) + 1
- Updated all CRUD operations (update, delete, toggle, get) to use user_task_id
- Created helper function get_task_by_id_or_title with prioritization logic
- All operations support user_task_id OR title (case-insensitive)
- Always filters by user_id for security

**MCP Tools:**
- Updated all 5 MCP tools (add_task, list_tasks, delete_task, update_task, complete_task)
- Created shared helper function for consistent lookup logic
- Returns user_task_id as "id" in responses

**Frontend:**
- Updated Todo interface to include userTaskId field
- Modified API client methods to use correct backend endpoints with user_task_id query params

**Testing:**
- Created comprehensive integration test verifying sequential assignment, lookup by ID, lookup by title, and user isolation
- All tests passed successfully

## Outcome

- ✅ Impact: User-facing task IDs now start from 1 per user and increment sequentially, providing intuitive task references for chat interactions
- 🧪 Tests: Integration test created and passed - verified sequential assignment, lookup operations, and user isolation
- 📁 Files: 8 files modified/created across backend models, routes, MCP tools, migration, tests, frontend types, and API client
- 🔁 Next prompts: Test end-to-end with chat interface, verify frontend displays user_task_id correctly
- 🧠 Reflection: Clean implementation following SQLModel best practices, proper separation of concerns with helper functions, comprehensive migration with backward compatibility

## Evaluation notes (flywheel)

- Failure modes observed: Initial migration script had emoji encoding issues on Windows (fixed by removing emojis)
- Graders run and results (PASS/FAIL): Integration test PASS, Model imports PASS, Routes imports PASS, MCP tools imports PASS
- Prompt variant (if applicable): Direct implementation without spec/plan (appropriate for enhancement)
- Next experiment (smallest change to try): Monitor production usage to ensure user_task_id sequence doesn't have race conditions under concurrent requests
