---
id: 0002
title: Create AI Chatbot Plan
stage: plan
date: 2026-02-13
surface: agent
model: claude-opus-4-6
feature: 001-ai-chatbot
branch: 001-ai-chatbot
user: user
command: /sp.plan
labels: ["plan", "ai-chatbot", "cohere", "mcp", "multilingual", "stateless", "phase-iii"]
links:
  spec: specs/001-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-ai-chatbot/plan.md
  - specs/001-ai-chatbot/research.md
  - specs/001-ai-chatbot/data-model.md
  - specs/001-ai-chatbot/quickstart.md
  - specs/001-ai-chatbot/contracts/mcp-tools.json
  - specs/001-ai-chatbot/contracts/chat-api.yaml
  - CLAUDE.md
tests:
  - none
---

## Prompt

# Phase III – Todo AI Chatbot Implementation Plan
# Generated from sp.specify
# Cohere Powered | MCP Architecture | Stateless Backend

====================================================
OBJECTIVE
====================================================

Generate a complete implementation plan for building
a multilingual Todo AI Chatbot using:

- FastAPI backend
- Cohere API for AI reasoning
- Official MCP SDK for tool exposure
- SQLModel ORM
- Neon PostgreSQL database
- OpenAI ChatKit frontend
- Fully Stateless Architecture

No OpenAI API usage allowed.

====================================================
IMPORTANT IMPLEMENTATION CONSTRAINT
====================================================

This system MUST be implemented inside the existing
Chat Page of the application.

DO NOT create a new chat UI.
DO NOT create a separate chatbot interface.
DO NOT duplicate frontend structure.

All AI Todo functionality must be integrated into
the already built Chat page.

[Full prompt content provided by user with implementation phases and architecture principles]

## Response snapshot

Created comprehensive implementation plan for AI-Powered Multilingual Todo Chatbot (001-ai-chatbot).

**Phase 0: Research Completed**
- Researched Cohere API capabilities (Command R model recommended)
- Critical finding: Urdu not officially supported, Hindi used as proxy
- Researched MCP SDK implementation (embedded FastMCP in FastAPI)
- Researched date parsing solutions (dateparser with custom Roman Urdu mapping)
- Documented all findings in research.md

**Phase 1: Design & Contracts Completed**
- Created data-model.md with 3 entities (Task extended, Conversation new, Message new)
- Generated MCP tools contract (mcp-tools.json) with 5 tool definitions
- Generated chat API contract (chat-api.yaml) with OpenAPI 3.0 specification
- Created quickstart.md with setup instructions and testing examples
- Updated CLAUDE.md with new technologies (Cohere SDK, MCP SDK, dateparser)

**Technical Decisions**:
- Model: Cohere Command R (command-r-08-2024)
- Architecture: Embedded MCP server in FastAPI (stateless)
- Date Parsing: dateparser + custom Roman Urdu mapping
- Conversation Context: Last 20 messages
- Frontend Integration: Update existing endpoint only (no new UI)

**Constitution Check**: ✅ PASSED - All principles satisfied

**Critical Constraint Acknowledged**: Frontend integration must use existing Chat Page UI without creating new pages.

## Outcome

- ✅ Impact: Complete implementation plan created with Phase 0 research and Phase 1 design artifacts. Plan includes technical context, constitution compliance check, project structure, research findings, data models, API contracts, and quickstart guide. Ready for Phase 2 task generation.
- 🧪 Tests: No tests required for planning phase
- 📁 Files: plan.md, research.md, data-model.md, quickstart.md, contracts/mcp-tools.json, contracts/chat-api.yaml, CLAUDE.md (updated)
- 🔁 Next prompts: /sp.tasks to generate implementation tasks organized by user story priority (P1-P5)
- 🧠 Reflection: Successfully completed planning with comprehensive research on Cohere API (identified Urdu limitation with Hindi proxy workaround), MCP SDK (embedded architecture chosen), and date parsing (dateparser with custom mapping). All design artifacts created including data models, API contracts, and quickstart guide. Critical frontend integration constraint clearly documented throughout plan.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution check - PASS (all principles satisfied)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
