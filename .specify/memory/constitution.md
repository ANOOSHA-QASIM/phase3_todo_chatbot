<!-- SYNC IMPACT REPORT
Version change: 1.2.0 → 1.3.0
Modified principles: None
Added sections: AI Chatbot Integration Principles, Multilingual Support Standards, MCP Server Architecture, Conversational AI Standards, Frontend Integration Constraints, AI Provider Configuration
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ reviewed - generic template compatible with Phase III
  - .specify/templates/spec-template.md ✅ reviewed - generic template compatible with Phase III
  - .specify/templates/tasks-template.md ✅ reviewed - generic template compatible with Phase III
  - .specify/templates/commands/*.md ⚠ pending review
Follow-up TODOs: None
Rationale: MINOR version bump - adding Phase III chatbot functionality principles without breaking existing Phase I/II principles
-->

# Hackathon II – Todo Full-Stack Web Application Constitution

## Core Principles

### Spec-Driven Development First
All implementation must strictly follow specifications defined in /specs. No manual coding outside Claude Code.

### Reusability
Any functionality (task handling, auth, API helpers) should be reusable in later phases (Phase III chatbot, Phase IV Kubernetes deployment).

### User Isolation & Security
Every feature must enforce proper authentication & authorization (JWT-based Better Auth integration).

### Clarity & Consistency
Code, API responses, UI components, and database models must be consistent with specs and naming conventions.

### Iterative & Testable
Features should be built incrementally, tested at each step, and spec updated if changes occur.

### Human as Tool Strategy
Treat the user as a specialized tool for clarification and decision-making when encountering situations that require human judgment.

## Key Standards

### Frontend
Next.js 16+, TypeScript, Tailwind CSS. Follow component-based architecture.

### Backend
FastAPI, SQLModel ORM, Neon PostgreSQL.

### Authentication
Better Auth + JWT. All endpoints secured.

### API
RESTful endpoints must adhere to @specs/api/rest-endpoints.md.

### Database
Follow @specs/database/schema.md. Ensure referential integrity and indexes.

### Error Handling
Return clear, JSON-formatted errors. Use HTTP status codes correctly.

### Documentation
Every implemented feature must reference its spec in /specs.

### Reusability for Agents/Skills
Define any helper functionality (task validation, auth helpers) in a way that can be converted into Claude Code agents/skills in future phases.

### Performance & Load Considerations
Backend endpoints must handle 100 concurrent users with <200ms average response time. Judge can verify with basic load testing.

### Accessibility & Responsiveness Standards
Frontend must follow WCAG accessibility standards. Fully responsive on desktop and mobile devices.

## AI Chatbot Integration Principles (Phase III)

### Multilingual Support
The AI agent MUST support English, Urdu, and Roman Urdu. Language detection must be automatic, and responses must match the user's input language. All natural language processing must maintain clarity and natural tone across all supported languages.

### Stateless MCP Server Architecture
The MCP server MUST be stateless. All conversation history, task state, and user context must persist in Neon PostgreSQL database. The server must expose tools via the Official MCP SDK for task management operations.

### Natural Language Understanding
The AI agent MUST understand implicit commands and map casual language to correct tool usage. Examples:
- "remind me to call mom tomorrow" → add_task with parsed due_date
- "show my pending work" → list_tasks filtered by status
- "I'm done with task 5" → complete_task

The agent MUST parse natural language dates (e.g., "tomorrow", "next Monday", "15 Feb") to exact date values stored as proper `date` type in database.

### Task Management Tools
The MCP server MUST expose these tools:
- **add_task**: Create task with optional priority (high/medium/low) and due_date
- **list_tasks**: Retrieve tasks filtered by status (pending/completed/all)
- **complete_task**: Mark task as completed
- **delete_task**: Remove task after confirmation
- **update_task**: Modify title, description, priority, or due_date

### Conversational AI Standards
- Always confirm actions in friendly tone: "Got it! Task added ✅"
- Handle errors gracefully: "Sorry, I couldn't find that task 😔"
- Ask clarifying questions politely when needed: "Which priority should I assign to this task?"
- Response style: friendly, concise, polite, encouraging
- Emoji usage allowed for better user engagement

### Frontend Integration Constraint (CRITICAL)
The AI Todo functionality MUST integrate into the existing Chat Page. It is STRICTLY PROHIBITED to:
- Create a new chatbot page
- Create a duplicate chat UI
- Replace the existing frontend architecture

All new logic MUST be implemented at:
- Backend processing layer
- AI reasoning layer
- MCP tool layer

The frontend UI structure MUST remain unchanged. The user experience should feel like an upgrade to the existing chat, not a new feature page.

### UI Synchronization
Updates to tasks via chatbot MUST reflect immediately in the frontend (ChatKit). Chat history MUST appear on sidebar with clickable conversations. New Chat button MUST start a fresh conversation in sidebar.

### AI Provider Configuration
The system MUST support both OpenAI Agents SDK and Cohere API for AI reasoning. The AI provider is determined by environment variables:
- If `COHERE_API_KEY` is set, use Cohere API
- If `OPENAI_API_KEY` is set, use OpenAI API
- Multilingual understanding MUST work with both providers

### Error Handling & State Management
- Task not found → friendly error message
- Invalid command → ask user to rephrase
- Maintain stateless architecture; all state MUST persist in Neon DB
- Conversation history MUST be stored in database for access across sessions

## Constraints

- All CRUD operations must work only for the **authenticated user**.
- All JWT tokens must be validated by backend middleware.
- Task fields: title (1-200 chars), description (optional, max 1000 chars), completed (boolean), priority (optional: high/medium/low), due_date (optional, date type), timestamps.
- Use monorepo structure as per /spec-kit/config.yaml.
- Frontend must be responsive for desktop & mobile.
- **Phase III**: MCP server must be stateless; all state in Neon DB.
- **Phase III**: AI agent must support English, Urdu, and Roman Urdu with automatic detection.
- **Phase III**: No new chat UI pages; integrate into existing Chat Page only.
- **Phase III**: Task properties must include task_id, title, description, completed, priority, due_date, created_at, updated_at.

## Success Criteria

### Phase I & II (Basic Todo Application)
- All 5 Basic Level features implemented and fully working:
  1. Add Task
  2. Delete Task
  3. Update Task
  4. View Task List
  5. Mark as Complete
- JWT auth integrated; all endpoints require valid token.
- API responses filtered by authenticated user.
- Code is fully spec-driven, referenceable in /specs.
- Ready for Phase III expansion with reusable agents & skills.
- Judge-ready: clearly follows spec, fully functional, secure, and clean architecture.

### Phase III (AI Chatbot Integration)
- MCP server successfully exposes all task management tools (add_task, list_tasks, complete_task, delete_task, update_task).
- AI agent correctly detects and responds in English, Urdu, and Roman Urdu.
- Natural language commands correctly parsed and mapped to tool calls.
- Date parsing works for natural language inputs ("tomorrow", "next Monday", "15 Feb").
- Task priority and due_date stored correctly in database as proper types.
- Conversation history persisted in Neon DB and accessible across sessions.
- Chat interface integrated into existing Chat Page without creating new UI pages.
- Task updates via chatbot reflect immediately in frontend.
- Chat history appears in sidebar with clickable conversations.
- New Chat button starts fresh conversation while preserving history access.
- Both OpenAI and Cohere API providers supported and configurable via environment variables.
- Friendly, emoji-enhanced responses with proper error handling.
- Stateless MCP server architecture maintained with all state in database.

## Development Guidelines

### Authoritative Source Mandate
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. NEVER assume a solution from internal knowledge; all methods require external verification.

### Execution Flow
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. PREFER CLI interactions (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**
1.  **Ambiguous Requirements:** When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding.
2.  **Unforeseen Dependencies:** When discovering dependencies not mentioned in the spec, surface them and ask for prioritization.
3.  **Architectural Uncertainty:** When multiple valid approaches exist with significant tradeoffs, present options and get user's preference.
4.  **Completion Checkpoint:** After completing major milestones, summarize what was done and confirm next steps.

### Default Policies
- Clarify and plan first - keep business understanding separate from technical plan and carefully architect and implement.
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing.
- Never hardcode secrets or tokens; use `.env` and docs.
- Prefer the smallest viable diff; do not refactor unrelated code.
- Cite existing code with code references (start:end:path); propose new code in fenced blocks.
- Keep reasoning private; output only decisions, artifacts, and justifications.

## Governance

This constitution supersedes all other practices. All implementations must strictly adhere to the specified principles and standards. Amendments require formal documentation and approval process. All code reviews must verify compliance with these principles.

**Version**: 1.3.0 | **Ratified**: 2026-01-13 | **Last Amended**: 2026-02-13