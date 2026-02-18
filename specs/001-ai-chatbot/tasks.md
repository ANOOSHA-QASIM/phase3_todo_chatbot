---

description: "Task list for AI-Powered Multilingual Todo Chatbot implementation"
---

# Tasks: AI-Powered Multilingual Todo Chatbot

**Input**: Design documents from `/specs/001-ai-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - not included unless explicitly requested in feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `frontend/src/`
- Paths shown below follow plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Add Cohere SDK to backend/requirements.txt (cohere==5.20.5)
- [x] T002 Add MCP SDK to backend/requirements.txt (mcp[cli]>=1.2.0)
- [x] T003 Add dateparser to backend/requirements.txt (dateparser==1.2.0, pytz==2024.1)
- [x] T004 [P] Add COHERE_API_KEY to backend/.env
- [x] T005 [P] Add COHERE_MODEL=command-r-08-2024 to backend/.env
- [x] T006 Install all new dependencies with pip install -r backend/requirements.txt

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 [P] Extend Task model in backend/models.py with priority field (enum: high, medium, low)
- [x] T008 [P] Extend Task model in backend/models.py with due_date field (DATE type)
- [x] T009 Create Conversation model in backend/models.py with id, user_id, created_at, updated_at
- [x] T010 Create Message model in backend/models.py with id, conversation_id, user_id, role (enum: user, assistant), content, created_at
- [x] T011 Create database migration script to add priority and due_date columns to tasks table
- [x] T012 Create database migration script to create conversations table
- [x] T013 Create database migration script to create messages table
- [x] T014 Run database migrations and verify schema correctness
- [x] T015 Create MCP server instance in backend/app/mcp/server.py using FastMCP
- [x] T016 Configure MCP server lifespan to share database engine
- [x] T017 Create DateParser service in backend/app/services/date_parser.py with parse() method
- [x] T018 Add Roman Urdu date mapping dictionary to DateParser (kal→tomorrow, aaj→today, etc.)
- [x] T019 Implement natural language date parsing using dateparser library in DateParser.parse()
- [x] T020 Create AI service skeleton in backend/app/services/ai_service.py with Cohere client initialization

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Tasks via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks by describing them naturally in conversation without following specific command syntax

**Independent Test**: Send messages like "Add a task to buy groceries tomorrow with high priority" and verify task is created with correct title, due_date, and priority

### Implementation for User Story 1

- [x] T021 [P] [US1] Implement add_task MCP tool in backend/app/mcp/tools.py with parameters (user_id, title, description, priority, due_date)
- [x] T022 [P] [US1] Add input validation for add_task tool (title 1-200 chars, priority enum validation)
- [x] T023 [US1] Implement add_task database operation in backend/app/mcp/tools.py (create Task, save to DB, return success response)
- [x] T024 [US1] Add error handling for add_task tool (return success: false with error message on failure)
- [x] T025 [US1] Register add_task tool with MCP server in backend/app/mcp/server.py using @mcp.tool() decorator
- [x] T026 [US1] Implement intent detection for "add task" in backend/app/services/ai_service.py
- [x] T027 [US1] Implement field extraction (title, description, priority, due_date) from natural language in ai_service.py
- [x] T028 [US1] Integrate DateParser with AI service to convert natural language dates to DATE format
- [x] T029 [US1] Implement priority keyword mapping (urgent→high, important→high, etc.) in ai_service.py
- [x] T030 [US1] Create system prompt for Cohere in ai_service.py with multilingual instructions and task extraction guidance
- [x] T031 [US1] Implement Cohere chat API call with tool definitions in ai_service.py
- [x] T032 [US1] Implement tool call detection and execution flow in ai_service.py
- [x] T033 [US1] Create chat endpoint POST /api/chat in backend/app/routes/chat.py
- [x] T034 [US1] Implement conversation history fetching (last 20 messages) in chat endpoint
- [x] T035 [US1] Implement user message storage in chat endpoint (save to messages table)
- [x] T036 [US1] Integrate AI service with chat endpoint (call Cohere, execute tools, get response)
- [x] T037 [US1] Implement assistant message storage in chat endpoint
- [x] T038 [US1] Add JWT authentication middleware to chat endpoint
- [x] T039 [US1] Return chat response with conversation_id and tool_results in chat endpoint
- [x] T040 [US1] Mount MCP server to FastAPI app in backend/app/main.py

**Checkpoint**: At this point, User Story 1 should be fully functional - users can add tasks via natural language

---

## Phase 4: User Story 2 - View and Complete Tasks (Priority: P2)

**Goal**: Users can ask to see their tasks and mark them as complete through natural conversation

**Independent Test**: Create several tasks, ask "show my tasks", verify list displays, say "task 3 is done", verify it's marked complete

### Implementation for User Story 2

- [x] T041 [P] [US2] Implement list_tasks MCP tool in backend/app/mcp/tools.py with parameters (user_id, status filter)
- [x] T042 [P] [US2] Implement list_tasks database query in tools.py (filter by user_id and status, order by due_date)
- [x] T043 [P] [US2] Add error handling for list_tasks tool (return empty list if no tasks)
- [x] T044 [P] [US2] Register list_tasks tool with MCP server in backend/app/mcp/server.py
- [x] T045 [P] [US2] Implement complete_task MCP tool in backend/app/mcp/tools.py with parameters (user_id, task_id)
- [x] T046 [P] [US2] Implement complete_task database operation in tools.py (find task, update completed=True, save)
- [x] T047 [P] [US2] Add error handling for complete_task tool (return error if task not found)
- [x] T048 [P] [US2] Register complete_task tool with MCP server in backend/app/mcp/server.py
- [x] T049 [US2] Implement intent detection for "list tasks" in backend/app/services/ai_service.py
- [x] T050 [US2] Implement intent detection for "complete task" in backend/app/services/ai_service.py
- [x] T051 [US2] Implement task_id extraction from natural language in ai_service.py
- [x] T052 [US2] Update system prompt in ai_service.py to include list and complete task instructions
- [x] T053 [US2] Implement friendly task list formatting in AI responses (numbered list with details)
- [x] T054 [US2] Implement empty task list handling (friendly message: "You have no tasks yet")

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Delete and Update Tasks (Priority: P3)

**Goal**: Users can remove tasks or update task details through natural conversation

**Independent Test**: Create a task, say "delete task 2", verify removal; say "change task 3 priority to high", verify update

### Implementation for User Story 3

- [x] T055 [P] [US3] Implement delete_task MCP tool in backend/app/mcp/tools.py with parameters (user_id, task_id)
- [x] T056 [P] [US3] Implement delete_task database operation in tools.py (find task, delete from DB)
- [x] T057 [P] [US3] Add error handling for delete_task tool (return error if task not found)
- [x] T058 [P] [US3] Register delete_task tool with MCP server in backend/app/mcp/server.py
- [x] T059 [P] [US3] Implement update_task MCP tool in backend/app/mcp/tools.py with parameters (user_id, task_id, title, description, priority, due_date)
- [x] T060 [P] [US3] Implement update_task database operation in tools.py (find task, update fields, save)
- [x] T061 [P] [US3] Add error handling for update_task tool (return error if task not found)
- [x] T062 [P] [US3] Register update_task tool with MCP server in backend/app/mcp/server.py
- [x] T063 [US3] Implement intent detection for "delete task" in backend/app/services/ai_service.py
- [x] T064 [US3] Implement intent detection for "update task" in backend/app/services/ai_service.py
- [x] T065 [US3] Implement field update detection (which field to update) in ai_service.py
- [x] T066 [US3] Update system prompt in ai_service.py to include delete and update task instructions

**Checkpoint**: All core task management operations (add, list, complete, delete, update) should now be functional

---

## Phase 6: User Story 4 - Multilingual Conversation Support (Priority: P4)

**Goal**: Users can interact in English, Urdu, or Roman Urdu with automatic language detection and matching responses

**Independent Test**: Send messages in each language and verify responses match input language while task operations work correctly

### Implementation for User Story 4

- [x] T067 [P] [US4] Add language detection using Cohere's automatic detection in backend/app/services/ai_service.py
- [x] T068 [P] [US4] Update system prompt in ai_service.py to explicitly support English, Urdu, and Roman Urdu
- [x] T069 [P] [US4] Add instruction in system prompt to respond in same language as user input
- [x] T070 [P] [US4] Extend DateParser in backend/app/services/date_parser.py to handle Urdu date expressions
- [x] T071 [US4] Test Urdu script support and document accuracy limitations in quickstart.md
- [x] T072 [US4] Test Roman Urdu support and verify 80-90% accuracy target
- [x] T073 [US4] Add fallback to English if language detection fails in ai_service.py
- [x] T074 [US4] Implement friendly error message in user's language if intent unclear

**Checkpoint**: Multilingual support should work for all task operations across all three languages

---

## Phase 7: User Story 5 - Conversation History and Sessions (Priority: P5)

**Goal**: Users can maintain multiple conversations, access previous conversations from sidebar, and start new conversations

**Independent Test**: Create multiple conversations, click on previous conversations to verify messages load, click "New Chat" to verify fresh conversation starts

### Implementation for User Story 5

- [x] T075 [P] [US5] Create GET /api/conversations endpoint in backend/routes/conversations.py
- [x] T076 [P] [US5] Implement conversation list query in conversations endpoint (filter by user_id, order by updated_at desc, limit 20)
- [x] T077 [P] [US5] Add JWT authentication to conversations endpoint
- [x] T078 [P] [US5] Create GET /api/conversations/{conversation_id}/messages endpoint in backend/routes/conversations.py
- [x] T079 [P] [US5] Implement message list query in messages endpoint (filter by conversation_id, order by created_at, limit 20)
- [x] T080 [P] [US5] Add JWT authentication and user_id validation to messages endpoint
- [x] T081 [US5] Implement conversation creation logic in chat endpoint (create new conversation if conversation_id is null)
- [x] T082 [US5] Implement conversation update logic in chat endpoint (update updated_at timestamp on new message)
- [x] T083 [US5] Update frontend/src/services/api.ts to call new /api/chat endpoint instead of old endpoint
- [x] T084 [US5] Verify existing chat UI displays AI responses correctly (no UI changes needed)
- [x] T085 [US5] Verify existing sidebar loads conversation list from new endpoint
- [x] T086 [US5] Verify existing "New Chat" button creates new conversation via new endpoint

**Checkpoint**: All user stories should now be independently functional with full conversation history support

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T087 [P] Add comprehensive error handling for database connection failures across all endpoints
- [x] T088 [P] Add request validation middleware to chat endpoint (message length, conversation_id format)
- [x] T089 [P] Implement rate limiting for chat endpoint (prevent abuse)
- [x] T090 [P] Add logging for all MCP tool executions in backend/app/mcp/tools.py
- [x] T091 [P] Add logging for Cohere API calls in backend/app/services/ai_service.py
- [x] T092 [P] Optimize database queries with proper indexes (conversation_id, user_id, created_at)
- [x] T093 [P] Add database connection pooling configuration in backend/app/database.py
- [x] T094 Implement conversation context limiting (ensure only last 20 messages sent to Cohere)
- [x] T095 Add friendly error messages for all edge cases (task not found, invalid date, etc.)
- [x] T096 Verify stateless architecture (test server restart, verify conversation resumes correctly)
- [x] T097 Performance test with 100 concurrent users, verify <200ms response time
- [x] T098 Update quickstart.md with final testing instructions and example conversations
- [x] T099 Document known limitations (Urdu script accuracy, date parsing edge cases) in quickstart.md
- [x] T100 Run constitution compliance check (verify all principles satisfied)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (independently testable)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories (independently testable)
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Enhances all previous stories but independently testable
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - No dependencies on other stories (independently testable)

### Within Each User Story

- MCP tools can be implemented in parallel (marked with [P])
- AI service updates depend on MCP tools being registered
- Chat endpoint integration depends on AI service being complete
- Frontend updates (US5 only) depend on backend endpoints being complete

### Parallel Opportunities

- All Setup tasks (T001-T006) can run in parallel
- All Foundational model tasks (T007-T010) can run in parallel
- All Foundational migration tasks (T011-T014) can run sequentially but are independent of model code
- Within each user story, MCP tool implementations marked [P] can run in parallel
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)

---

## Parallel Example: User Story 1

```bash
# Launch all MCP tool tasks for User Story 1 together:
Task T021: "Implement add_task MCP tool in backend/app/mcp/tools.py"
Task T022: "Add input validation for add_task tool"

# These can run in parallel with AI service work:
Task T026: "Implement intent detection for add task in ai_service.py"
Task T027: "Implement field extraction in ai_service.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T020) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T021-T040)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T021-T040)
   - Developer B: User Story 2 (T041-T054)
   - Developer C: User Story 3 (T055-T066)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- **CRITICAL CONSTRAINT**: No new frontend UI pages - only update existing chat endpoint (T083-T086)
- Tests are OPTIONAL - not included unless explicitly requested in spec
- All tasks include exact file paths for clarity
- Stateless architecture must be maintained throughout (no in-memory state)
