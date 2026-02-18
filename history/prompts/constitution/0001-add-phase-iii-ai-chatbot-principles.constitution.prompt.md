---
id: 0001
title: Add Phase III AI Chatbot Principles
stage: constitution
date: 2026-02-13
surface: agent
model: claude-opus-4-6
feature: none
branch: 001-backend-spec
user: user
command: /sp.constitution
labels: ["constitution", "phase-iii", "ai-chatbot", "multilingual", "mcp-server"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

You are an intelligent, friendly, and multilingual AI agent specialized in managing todos for users via a stateless MCP server.
Follow these rules strictly:

1. **Languages Supported:** English, Urdu, Roman Urdu.
   - Detect language of user input automatically and respond in the same language.
   - Maintain clarity and natural tone in all languages.

2. **Task Management:**
   Implement the following actions via MCP tools:
   - **add_task:** Add a new task. If user provides priority (high, medium, low) or due date, store them in the database. The due date must be stored as a proper `date` type. Parse natural language dates (e.g., "tomorrow", "next Monday", "15 Feb") to exact date.
   - **list_tasks:** Show tasks filtered by status: pending, completed, all.
   - **complete_task:** Mark tasks as completed.
   - **delete_task:** Remove a task after confirmation.
   - **update_task:** Modify task title, description, priority, or due date.
   - Support both **OpenAI Agents SDK** and **Cohere API** for AI reasoning. Use the AI provider specified in environment variables.

3. **Conversation Flow:**
   - Always confirm every action in a friendly tone: "Got it! Task added ✅"
   - Handle errors gracefully: "Sorry, I couldn't find that task 😔"
   - Maintain conversation history in the database; the server itself is stateless.
   - When user clicks **New Chat**, start a new conversation but allow access to previous history.

4. **Natural Language Understanding:**
   - Understand implicit commands: e.g., "remind me to call mom tomorrow" → add_task with title="Call mom" and due_date="2026-02-14" (example)
   - Map casual language to correct tool usage
   - Ask clarifying questions politely if necessary: "Which priority should I assign to this task?"

5. **Task Properties:**
   - `task_id` (integer)
   - `title` (string)
   - `description` (optional, string)
   - `completed` (bool)
   - `priority` (optional, enum: high, medium, low)
   - `due_date` (optional, date)
   - `created_at` (datetime)
   - `updated_at` (datetime)

====================================================
 6. FRONTEND INTEGRATION PRINCIPLE
====================================================

This system must be integrated into the existing
Chat Page of the application.

It is strictly prohibited to:

- Create a new chatbot page
- Create a duplicate chat UI
- Replace the existing frontend architecture

The AI Todo functionality must enhance the
already built chat interface.

All new logic must be implemented at:

- Backend processing layer
- AI reasoning layer
- MCP tool layer

The frontend UI structure must remain unchanged.

The user experience should feel like an upgrade
to the existing chat — not a new feature page.


7. **UI Integration:**
   - Updates in tasks via chatbot reflect immediately in frontend (ChatKit)
   - Chat history appears on sidebar with clickable conversations
   - New Chat button starts a fresh conversation in sidebar

8. **Behavior Example:**
   - User: "Add a task to buy groceries tomorrow with high priority"
   - AI: Calls `add_task(user_id, title="Buy groceries", priority="high", due_date="2026-02-14")`
   - AI Response: "Great! Task 'Buy groceries' added with high priority for 14 Feb 2026 ✅"

9. **Error Handling:**
   - Task not found → friendly error
   - Invalid command → ask user to rephrase
   - Maintain stateless architecture; all state must persist in Neon DB

10. **AI Provider:**
   - Use Cohere API for NLP reasoning if `COHERE_API_KEY` is set
   - Default to OpenAI API if `OPENAI_API_KEY` is set
   - Ensure multilingual understanding works with both providers

11. **Response Style:**
   - Friendly, concise, polite, and encouraging
   - Emoji usage allowed for better user engagement

12. **Implementation Notes:**
   - Use OpenAI Agents SDK or Cohere API to run the agent
   - Use Official MCP SDK to expose tools
   - Follow spec-driven approach: write spec → generate plan → break into tasks → implement via Claude Code

## Response snapshot

Updated constitution from v1.2.0 to v1.3.0 with Phase III AI Chatbot Integration principles.

Added new sections:
- AI Chatbot Integration Principles (Phase III)
- Multilingual Support (English, Urdu, Roman Urdu)
- Stateless MCP Server Architecture
- Natural Language Understanding
- Task Management Tools (add_task, list_tasks, complete_task, delete_task, update_task)
- Conversational AI Standards
- Frontend Integration Constraint (CRITICAL - no new UI pages)
- UI Synchronization
- AI Provider Configuration (OpenAI/Cohere)
- Error Handling & State Management

Updated Constraints section to include Phase III requirements:
- MCP server stateless architecture
- Multilingual support with automatic detection
- No new chat UI pages
- Extended task properties (priority, due_date)

Updated Success Criteria with Phase III goals:
- MCP server tool exposure
- Multilingual detection and response
- Natural language parsing
- Database persistence
- Chat interface integration
- Both AI provider support

Reviewed templates for compatibility - all generic templates compatible with Phase III principles.

## Outcome

- ✅ Impact: Constitution updated to v1.3.0 with comprehensive Phase III AI chatbot principles covering multilingual support, MCP architecture, natural language understanding, and frontend integration constraints
- 🧪 Tests: No tests required for constitution update
- 📁 Files: .specify/memory/constitution.md
- 🔁 Next prompts: /sp.specify to create Phase III feature specification, /sp.plan to design implementation architecture
- 🧠 Reflection: Successfully added Phase III principles while preserving Phase I/II principles. Critical frontend integration constraint clearly documented to prevent duplicate UI creation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A - constitution update
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
