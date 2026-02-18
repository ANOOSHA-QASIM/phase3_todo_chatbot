# Implementation Plan: AI-Powered Multilingual Todo Chatbot

**Branch**: `001-ai-chatbot` | **Date**: 2026-02-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-chatbot/spec.md`

## Summary

Build a multilingual AI-powered todo management chatbot that integrates with the existing chat page. The system uses Cohere API for natural language understanding, MCP SDK for tool exposure, and maintains a fully stateless architecture with all state persisted in Neon PostgreSQL. Users can manage tasks through natural conversation in English, Urdu, or Roman Urdu without following specific command syntax.

**Key Technical Approach**:
- Stateless FastAPI backend with MCP server exposing task management tools
- Cohere API for intent detection, language detection, and natural language processing
- SQLModel ORM for database operations with extended Task model (priority, due_date)
- New Conversation and Message models for chat history persistence
- Integration with existing ChatKit frontend (no new UI pages)
- Natural language date parsing to convert expressions like "tomorrow" to exact dates

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, Cohere Python SDK, Official MCP SDK, SQLModel, psycopg2-binary, python-dateutil (for date parsing), pydantic
**Storage**: Neon PostgreSQL (existing connection from Phase I/II)
**Testing**: pytest, pytest-asyncio
**Target Platform**: Linux server (containerized deployment)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: 100 concurrent users with <200ms average response time per constitution
**Constraints**: Fully stateless server architecture, multilingual support (English/Urdu/Roman Urdu), must integrate with existing chat UI without creating new pages, due_date stored as DATE type
**Scale/Scope**: Hackathon-grade implementation, 5 MCP tools, 3 supported languages, conversation history persistence

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Compliance

✅ **Spec-Driven Development First**: Implementation follows specs/001-ai-chatbot/spec.md with 25 functional requirements
✅ **Reusability**: MCP tools designed as standalone functions, can be reused in Phase IV or converted to Claude Code skills
✅ **User Isolation & Security**: All endpoints require JWT authentication, tasks scoped to authenticated user_id
✅ **Clarity & Consistency**: Following existing FastAPI patterns from Phase I/II backend
✅ **Iterative & Testable**: 5 prioritized user stories (P1-P5) enable incremental implementation

### Phase III Specific Principles

✅ **Multilingual Support**: Cohere API supports English, Urdu, Roman Urdu with automatic language detection
✅ **Stateless MCP Server Architecture**: All conversation state persists in database, server holds no in-memory state
✅ **Natural Language Understanding**: Intent mapping and field extraction implemented in AI service layer
✅ **Task Management Tools**: 5 MCP tools (add_task, list_tasks, complete_task, delete_task, update_task) exposed via Official MCP SDK
✅ **Conversational AI Standards**: Friendly tone, emoji usage, error handling per constitution
🔴 **Frontend Integration Constraint (CRITICAL)**: MUST integrate with existing Chat Page, NO new UI pages allowed
✅ **UI Synchronization**: Real-time updates via existing chat endpoint
✅ **AI Provider Configuration**: Cohere API only (COHERE_API_KEY environment variable)
✅ **Error Handling & State Management**: Friendly error messages, stateless architecture

### Key Standards Compliance

✅ **Backend**: FastAPI, SQLModel ORM, Neon PostgreSQL (existing stack)
✅ **Authentication**: Better Auth + JWT (existing from Phase I/II)
✅ **API**: RESTful endpoint POST /api/chat (extends existing patterns)
✅ **Database**: Extended Task model with priority/due_date, new Conversation/Message models
✅ **Error Handling**: JSON-formatted errors with proper HTTP status codes
✅ **Performance**: <200ms response time target, 100 concurrent users

### Gate Status: ✅ PASSED

All constitution principles satisfied. Critical constraint acknowledged: frontend integration must use existing Chat Page UI.

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-chatbot/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (to be generated)
│   ├── mcp-tools.json   # MCP tool definitions
│   └── chat-api.yaml    # Chat endpoint OpenAPI spec
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── task.py          # Extended with priority, due_date (Phase I/II exists, extend)
│   │   ├── conversation.py  # New model for chat sessions
│   │   └── message.py       # New model for chat messages
│   ├── routes/
│   │   ├── tasks.py         # Existing task CRUD endpoints (Phase I/II)
│   │   └── chat.py          # New chat endpoint
│   ├── services/
│   │   ├── ai_service.py    # Cohere integration, intent detection, NLP
│   │   ├── mcp_service.py   # MCP tool implementations
│   │   └── date_parser.py   # Natural language date parsing
│   ├── mcp/
│   │   ├── server.py        # MCP server setup with Official SDK
│   │   └── tools.py         # Tool definitions and handlers
│   ├── database.py          # Existing DB connection (Phase I/II)
│   ├── auth.py              # Existing Better Auth integration (Phase I/II)
│   └── main.py              # FastAPI app (extend with chat route)
├── tests/
│   ├── test_mcp_tools.py
│   ├── test_ai_service.py
│   └── test_chat_endpoint.py
├── requirements.txt         # Add cohere, mcp, python-dateutil
└── .env                     # Add COHERE_API_KEY

frontend/
├── src/
│   ├── components/
│   │   └── chat/            # Existing ChatKit components (Phase I/II)
│   ├── pages/
│   │   └── chat.tsx         # Existing Chat Page (update API endpoint only)
│   └── services/
│       └── api.ts           # Update chat endpoint integration
└── (no new UI files - use existing structure)
```

**Structure Decision**: Web application structure selected. Backend extends existing Phase I/II FastAPI app with new chat endpoint, MCP server, and AI service layer. Frontend uses existing Chat Page without creating new UI components. This maintains consistency with Phase I/II architecture while adding AI capabilities.

## Complexity Tracking

> No constitution violations requiring justification.

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **Cohere API Integration for Multilingual NLP**
   - Research: Cohere Chat API capabilities for English, Urdu, Roman Urdu
   - Research: Tool calling / function calling support in Cohere
   - Research: Language detection methods
   - Decision needed: Cohere model selection (command, command-light, command-r)

2. **Official MCP SDK Implementation**
   - Research: MCP SDK for Python (installation, setup, tool definition)
   - Research: Stateless tool implementation patterns
   - Research: Error handling and response formatting
   - Decision needed: MCP server hosting approach (embedded vs standalone)

3. **Natural Language Date Parsing**
   - Research: python-dateutil for relative date parsing
   - Research: Multilingual date parsing (Urdu/Roman Urdu date expressions)
   - Research: Timezone handling for date conversion
   - Decision needed: Date parsing library selection

4. **Conversation History Architecture**
   - Research: Efficient conversation retrieval patterns
   - Research: Message pagination strategies
   - Research: Conversation context window management
   - Decision needed: How many messages to include in context

5. **Frontend Integration Strategy**
   - Research: Existing Chat Page implementation (ChatKit)
   - Research: API endpoint structure for chat messages
   - Research: Real-time UI update mechanisms
   - Decision needed: WebSocket vs polling vs SSE for updates

### Output

Research findings will be documented in `research.md` with decisions, rationale, and alternatives considered.

## Phase 1: Design & Contracts

### Data Model Design

**Entities to define in data-model.md**:

1. **Task** (extend existing model)
   - Add: priority (enum: high, medium, low)
   - Add: due_date (DATE type)
   - Existing: id, user_id, title, description, completed, created_at, updated_at

2. **Conversation** (new model)
   - id (integer, primary key)
   - user_id (string, foreign key)
   - created_at (datetime)
   - updated_at (datetime)

3. **Message** (new model)
   - id (integer, primary key)
   - conversation_id (integer, foreign key)
   - user_id (string, foreign key)
   - role (enum: user, assistant)
   - content (text)
   - created_at (datetime)

### API Contracts

**Contracts to generate in /contracts/**:

1. **mcp-tools.json**: MCP tool definitions
   - add_task tool schema
   - list_tasks tool schema
   - complete_task tool schema
   - delete_task tool schema
   - update_task tool schema

2. **chat-api.yaml**: OpenAPI specification
   - POST /api/chat endpoint
   - Request: { conversation_id?, message }
   - Response: { message, conversation_id, tool_results? }

### Quickstart Guide

**quickstart.md** will include:
- Environment setup (COHERE_API_KEY)
- Database migration commands
- Running the MCP server
- Testing chat endpoint with curl examples
- Example conversations in English, Urdu, Roman Urdu

### Agent Context Update

After Phase 1 completion, run:
```bash
.specify/scripts/bash/update-agent-context.sh claude
```

This will update CLAUDE.md with:
- Cohere Python SDK
- Official MCP SDK
- python-dateutil
- New models: Conversation, Message
- Extended Task model with priority, due_date

## Phase 2: Task Generation

Phase 2 is handled by `/sp.tasks` command (not part of this plan).

Tasks will be organized by user story priority (P1-P5) with:
- P1: Add Tasks via Natural Language
- P2: View and Complete Tasks
- P3: Delete and Update Tasks
- P4: Multilingual Conversation Support
- P5: Conversation History and Sessions

## Implementation Notes

### Critical Constraints

1. **Frontend Integration**: MUST NOT create new chat UI. Only update existing Chat Page to call new backend endpoint.

2. **Stateless Architecture**: Server must hold ZERO in-memory state. All conversation context fetched from database on each request.

3. **Date Storage**: due_date MUST be stored as DATE type in database, not string or datetime.

4. **Language Detection**: Automatic detection required, no user language selection UI.

5. **MCP Tool Isolation**: Tools must be pure functions with no side effects beyond database operations.

### Risk Mitigation

1. **Cohere API Multilingual Support**: If Cohere struggles with Urdu/Roman Urdu, implement fallback language detection using langdetect library.

2. **Date Parsing Accuracy**: If python-dateutil doesn't handle Urdu dates, create custom parser for common Urdu date expressions.

3. **Frontend Integration Complexity**: If existing Chat Page structure incompatible, minimal adapter layer allowed but NO new UI pages.

4. **Performance Under Load**: If <200ms target not met, implement database query optimization and conversation context limiting.

### Success Metrics

- All 25 functional requirements from spec.md implemented
- All 12 success criteria from spec.md validated
- Constitution compliance maintained
- No new frontend pages created
- Stateless architecture verified (server restart test)
- Multilingual support validated for all 3 languages
