---
id: 0001
title: Create AI Chatbot Spec
stage: spec
date: 2026-02-13
surface: agent
model: claude-opus-4-6
feature: 001-ai-chatbot
branch: 001-ai-chatbot
user: user
command: /sp.specify
labels: ["spec", "ai-chatbot", "multilingual", "phase-iii", "cohere", "mcp", "stateless"]
links:
  spec: specs/001-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-ai-chatbot/spec.md
  - specs/001-ai-chatbot/checklists/requirements.md
tests:
  - none
---

## Prompt

# Phase III – Todo AI Chatbot Specification
# Cohere Powered | MCP Architecture | Stateless Backend
# Location: /specs/sp.specify

====================================================
1. PROJECT OVERVIEW
====================================================

Project Name: Todo AI Chatbot
Goal: Build a multilingual AI-powered todo management chatbot using MCP architecture.

Technology Stack:
- Frontend: OpenAI ChatKit
- Backend: Python FastAPI
- AI Provider: Cohere API (ONLY)
- MCP Server: Official MCP SDK
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth

Architecture: Fully Stateless Server
All conversation state and tasks must persist in database.
Server must hold NO memory between requests.

====================================================
2. CORE REQUIREMENTS
====================================================

The chatbot must:

- Understand English, Urdu, Roman Urdu (auto-detect language)
- Respond in same detected language
- Manage tasks via natural conversation
- Support:
    - Add task
    - List tasks
    - Complete task
    - Delete task
    - Update task
- Support optional:
    - priority (high, medium, low)
    - due_date (stored strictly as DATE type in DB)
- Maintain conversation history
- Support multiple chat sessions
- Have sidebar with chat history
- Have "New Chat" button (ChatGPT-style)
- Dynamically update UI after task operations

====================================================
3. INPUT HANDLING (NO FORMAT RESTRICTIONS)
====================================================

User can send input in ANY format:
- Full natural language
- Broken sentences
- Mixed language
- Roman Urdu
- Short commands
- Long explanation
- JSON-like text
- Casual speech

There is NO fixed format requirement.

The AI must:
- Detect intent
- Extract task title
- Extract optional description
- Extract optional priority
- Extract optional due date
- Normalize all extracted data before calling MCP tools

If required field (title) missing → politely ask user.
If due date ambiguous → ask clarification.
If task not found → respond gracefully.

====================================================
4. DATABASE MODELS
====================================================

Task:
- id (integer)
- user_id (string)
- title (string)
- description (optional string)
- completed (boolean)
- priority (optional enum: high, medium, low)
- due_date (optional DATE type)
- created_at (datetime)
- updated_at (datetime)

Conversation:
- id (integer)
- user_id (string)
- created_at
- updated_at

Message:
- id
- user_id
- conversation_id
- role (user / assistant)
- content
- created_at

====================================================
5. MCP TOOLS SPECIFICATION
====================================================

Tool: add_task
Parameters:
- user_id (required)
- title (required)
- description (optional)
- priority (optional)
- due_date (optional DATE)

Tool: list_tasks
Parameters:
- user_id (required)
- status (optional: all, pending, completed)

Tool: complete_task
Parameters:
- user_id (required)
- task_id (required)

Tool: delete_task
Parameters:
- user_id (required)
- task_id (required)

Tool: update_task
Parameters:
- user_id (required)
- task_id (required)
- title (optional)
- description (optional)
- priority (optional)
- due_date (optional DATE)

====================================================
6. AGENT BEHAVIOR LOGIC
====================================================

Intent Mapping Rules:

If user wants to add something → call add_task
If user wants to see tasks → call list_tasks
If user says done/complete/ho gaya → call complete_task
If user says delete/remove/cancel → call delete_task
If user says change/update/rename → call update_task

Due Date Handling:
- Parse natural language date (e.g. tomorrow, next Friday)
- Convert into exact ISO date
- Store strictly as DATE type in DB

Priority Handling:
- Detect words like urgent, important, high
- Map into enum: high, medium, low

Always:
- Confirm action in friendly tone
- Be concise but helpful
- Use emojis lightly for friendliness
- Never expose raw tool structure to user

====================================================
7. CONVERSATION FLOW (STATELESS)
====================================================

1. Receive request POST /api/{user_id}/chat
2. Fetch conversation history from DB
3. Build message array (history + new message)
4. Store user message
5. Run Cohere AI
6. AI decides tool usage
7. Execute MCP tool
8. Store assistant response
9. Return response to frontend

Server must remain stateless.

====================================================
8. FRONTEND CONTEXT
====================================================

Assume that a fully functional Chat Page
already exists in the application.

The system must:

- Use the existing chat UI
- Use the existing message sending flow
- Use the existing conversation rendering system

The only changes allowed are:

- Updating the backend chat endpoint
- Integrating Cohere AI
- Adding MCP tool execution internally
- Enhancing responses with task functionality

No new chat interface should be created.

All Todo AI features must operate through
the current chat page seamlessly.


====================================================
9. FRONTEND REQUIREMENTS
====================================================

- ChatKit UI
- Real-time UI update after tool execution
- Sidebar with saved conversations
- Click conversation → load messages
- New Chat button → create new conversation
- Friendly greeting on first interaction

====================================================
10. ERROR HANDLING
====================================================

If task not found:
→ Friendly message

If invalid command:
→ Ask user to clarify

If system error:
→ Apologize politely

====================================================
11. AI PROVIDER CONFIGURATION
====================================================

Use Cohere API ONLY.
Environment variable:
COHERE_API_KEY

No OpenAI API usage allowed.

====================================================
12. SUCCESS CRITERIA
====================================================

## Response snapshot

Created comprehensive feature specification for AI-Powered Multilingual Todo Chatbot (001-ai-chatbot).

**Specification includes**:
- 5 prioritized user stories (P1-P5) with independent test criteria
- 25 functional requirements covering language detection, task management, conversation flow, UI integration
- 12 measurable, technology-agnostic success criteria
- 8 edge cases with expected behaviors
- 4 key entities (Task, Conversation, Message, User)
- 10 documented assumptions

**Quality validation**:
- Created spec quality checklist at specs/001-ai-chatbot/checklists/requirements.md
- All checklist items passed validation
- No [NEEDS CLARIFICATION] markers present
- No implementation details in requirements
- All requirements testable and unambiguous

**Branch created**: 001-ai-chatbot
**Spec file**: specs/001-ai-chatbot/spec.md

## Outcome

- ✅ Impact: Complete feature specification created for Phase III AI chatbot with multilingual support, MCP architecture, and stateless backend design. Specification is business-focused, technology-agnostic, and ready for planning phase.
- 🧪 Tests: No tests required for specification phase
- 📁 Files: specs/001-ai-chatbot/spec.md, specs/001-ai-chatbot/checklists/requirements.md
- 🔁 Next prompts: /sp.plan to create implementation plan, /sp.clarify if any requirements need refinement
- 🧠 Reflection: Successfully created comprehensive spec with 5 independently testable user stories prioritized by value. Critical constraint documented: must integrate with existing chat UI without creating new pages. All requirements are measurable and technology-agnostic as required.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Spec quality checklist - PASS (all items validated)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
