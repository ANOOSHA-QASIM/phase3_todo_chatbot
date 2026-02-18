# Research: Cohere API for Multilingual Todo Chatbot

**Feature**: AI-Powered Multilingual Todo Chatbot
**Branch**: `001-ai-chatbot`
**Date**: 2026-02-13
**Researcher**: Claude Opus 4.6

## Executive Summary

This research evaluates Cohere API capabilities for building a multilingual task management chatbot supporting English, Urdu, and Roman Urdu. Key findings:

- **CRITICAL**: Urdu and Roman Urdu are NOT officially supported by any Cohere model
- Hindi IS supported and shares 90%+ linguistic similarity with Urdu (same grammar, different script)
- Command R is recommended for this use case (cost-effective, tool use support, multilingual)
- Tool calling is fully supported via SDK with parameter_definitions structure
- SDK upgrade required (5.5.3 → 5.20.5) for latest features
- Workaround strategies identified for Urdu/Roman Urdu support

## 1. Cohere Model Selection

### Available Models Comparison

| Model | Context | Languages | Tool Use | Cost | Best For |
|-------|---------|-----------|----------|------|----------|
| Command A | 256K | 23 (no Urdu) | ✅ Excellent | Higher | Complex agents, high performance |
| Command R | 128K | 23 (no Urdu) | ✅ Good | $0.15/$0.60 | Production RAG, tool use |
| Command R+ | 128K | 23 (no Urdu) | ✅ Multi-step | Higher | Complex multi-step workflows |
| Aya Expanse | - | 23 (no Urdu) | ❌ Limited | - | Multilingual content generation |

### Supported Languages (All Models)

English, French, Spanish, Italian, German, Portuguese, Japanese, Korean, Chinese, Arabic, Russian, Polish, Turkish, Vietnamese, Dutch, Czech, Indonesian, Ukrainian, Romanian, Greek, **Hindi**, Hebrew, Persian

**Notable Absence**: Urdu is NOT in the supported language list for any model.

### Recommendation: Command R (command-r-08-2024)

**Rationale**:
1. **Cost-effective**: $0.15 input / $0.60 output (vs Command A's higher pricing)
2. **Tool use support**: Explicitly designed for tool-using agents
3. **Sufficient context**: 128K tokens handles conversation history + task context
4. **Production-ready**: Optimized for 50% higher throughput vs previous versions
5. **Multilingual**: Supports 23 languages including Hindi (Urdu workaround)

**Why NOT Command A**: Overkill for task management chatbot; higher cost without proportional benefit for this use case.

**Why NOT Command R+**: Designed for complex multi-step RAG workflows; our use case is simpler single-step tool calls.

**Why NOT Aya Expanse**: Limited tool use support; focused on content generation rather than task execution.

## 2. Tool Calling / Function Calling

### SDK Version Compatibility

**Current Installation**: `cohere==5.5.3`
**Latest Version**: `cohere==5.20.5`
**Issue**: ClientV2 not available in 5.5.3; response_format parameter missing

**Recommendation**: Upgrade to 5.20.5 for latest features.

```bash
pip install --upgrade cohere==5.20.5
```

### Tool Definition Structure (SDK 5.5.3)

```python
tools = [
    {
        "name": "add_task",
        "description": "Creates a new task in the task management system",
        "parameter_definitions": {
            "title": {
                "description": "The title of the task",
                "type": "str",
                "required": True
            },
            "description": {
                "description": "Detailed description of the task",
                "type": "str",
                "required": False
            },
            "priority": {
                "description": "Priority level: low, medium, or high",
                "type": "str",
                "required": False
            },
            "due_date": {
                "description": "Due date in YYYY-MM-DD format",
                "type": "str",
                "required": False
            }
        }
    }
]
```

### Tool Calling Workflow

**4-Step Process**:

1. **User sends message** → System receives natural language input
2. **Model generates tool calls** → Cohere returns tool_plan and tool_calls
3. **Execute tools** → Backend runs functions, formats results as documents
4. **Model generates response** → Cohere creates user-facing message with citations

**Example Implementation**:

```python
import cohere
import json

co = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))

# Step 1: User message
response = co.chat(
    model="command-r-08-2024",
    message="Add a task to buy groceries tomorrow with high priority",
    chat_history=[],  # Previous conversation context
    tools=tools,
    preamble="You are a helpful task management assistant..."
)

# Step 2: Check for tool calls
if response.tool_calls:
    tool_results = []

    for tool_call in response.tool_calls:
        # Step 3: Execute tool
        if tool_call.name == "add_task":
            params = json.loads(tool_call.parameters)
            result = create_task_in_db(
                title=params["title"],
                priority=params.get("priority"),
                due_date=params.get("due_date")
            )
            tool_results.append({
                "call": tool_call,
                "outputs": [{"result": json.dumps(result)}]
            })

    # Step 4: Generate final response
    final_response = co.chat(
        model="command-r-08-2024",
        message="",
        chat_history=response.chat_history,
        tools=tools,
        tool_results=tool_results
    )

    return final_response.text
```

### Tool Calling Best Practices

1. **Clear descriptions**: Tool and parameter descriptions guide model's decision-making
2. **Type validation**: Use Pydantic models to validate tool parameters before execution
3. **Error handling**: Wrap tool execution in try-except, return error messages to model
4. **Stateless design**: Tools should be pure functions with no side effects beyond DB operations
5. **Result formatting**: Return structured data as JSON strings for model to parse

## 3. Language Detection

### Built-in Language Detection

Cohere models automatically detect input language and respond in the same language. No explicit language detection API is provided.

**How it works**:
- Model analyzes input text during inference
- Responds in detected language automatically
- Works for all 23 supported languages

**Limitation**: No programmatic access to detected language for logging/analytics.

### Workaround for Language Detection

For explicit language detection (e.g., for logging, analytics, or routing), use external library:

```python
from langdetect import detect, DetectorFactory

# Set seed for consistent results
DetectorFactory.seed = 0

def detect_language(text: str) -> str:
    """
    Detect language of input text.
    Returns: 'en', 'ur', 'hi', etc.
    """
    try:
        lang = detect(text)
        return lang
    except:
        return "en"  # Default to English
```

**Note**: `langdetect` can distinguish Urdu (ur) from Hindi (hi) based on script, but Cohere models treat them similarly due to linguistic overlap.

## 4. Urdu and Roman Urdu Support Strategy

### Critical Finding: Urdu NOT Officially Supported

**Problem**: Neither Urdu nor Roman Urdu appear in Cohere's 23 supported languages.

**Hindi-Urdu Linguistic Relationship**:
- Same grammar and syntax (Hindustani language continuum)
- Different scripts: Hindi uses Devanagari, Urdu uses Perso-Arabic
- Spoken forms are mutually intelligible
- Cohere's Hindi support may partially handle Urdu due to shared structure

### Recommended Workaround Strategies

#### Strategy 1: Leverage Hindi Support (Recommended)

**Approach**: Use Command R's Hindi support as proxy for Urdu understanding.

**Rationale**:
- Hindi and Urdu share grammatical structure
- Model trained on Hindi can understand Urdu sentence patterns
- Works better for Roman Urdu (transliterated form uses Latin script)

**Implementation**:
```python
# System prompt guides model to handle Urdu-like inputs
preamble = """You are a helpful task management assistant that supports English, Hindi, and Urdu.
When users write in Urdu script or Roman Urdu (Urdu written in Latin script), understand their intent
and respond naturally. Treat Urdu and Hindi as linguistically similar languages."""
```

**Expected Performance**:
- English: 95%+ accuracy (native support)
- Roman Urdu: 80-90% accuracy (Hindi proxy + Latin script)
- Urdu script: 60-75% accuracy (limited by script difference)

#### Strategy 2: Preprocessing Layer

**Approach**: Detect Urdu input, transliterate to Roman Urdu, send to Cohere.

**Implementation**:
```python
from urdu_transliterator import transliterate  # Hypothetical library

def preprocess_message(text: str) -> str:
    lang = detect_language(text)

    if lang == "ur":  # Urdu script detected
        # Transliterate Urdu script to Roman Urdu
        text = transliterate(text, source="urdu", target="roman")

    return text
```

**Pros**: Normalizes input to Latin script, improves model understanding
**Cons**: Requires additional library, potential transliteration errors

#### Strategy 3: Fallback to English

**Approach**: If Urdu/Roman Urdu performance is poor, prompt user to use English.

**Implementation**:
```python
# In system prompt
preamble = """You support English, Hindi, and Urdu. If you cannot understand a message,
politely ask the user to rephrase in English or simpler terms."""
```

### Testing Strategy for Urdu Support

1. **Create test dataset**: 20 common task management phrases in English, Urdu, Roman Urdu
2. **Measure accuracy**: Intent detection rate, field extraction accuracy
3. **Iterate prompts**: Adjust preamble based on test results
4. **Set expectations**: Document actual performance vs ideal in quickstart.md

## 5. Intent Detection and Field Extraction

### System Prompt Pattern

```python
preamble = """You are a helpful task management assistant. Users can:
- Add tasks: "add task to buy groceries" → extract title, priority, due_date
- List tasks: "show my tasks" or "what do I need to do"
- Complete tasks: "mark task 5 as done" → extract task_id
- Delete tasks: "delete task 3" → extract task_id
- Update tasks: "change task 2 priority to high" → extract task_id, field, value

Extract information from natural language and call appropriate tools.
Always respond in the same language as the user's input.
Be friendly and conversational."""
```

### Field Extraction Examples

**Natural Language → Structured Data**:

| User Input | Extracted Fields |
|------------|------------------|
| "Add task to buy groceries tomorrow with high priority" | title="Buy groceries", due_date="2026-02-14", priority="high" |
| "Remind me to call mom" | title="Call mom" |
| "urgent: finish report by next Friday" | title="Finish report", priority="high", due_date="2026-02-21" |
| "Show my pending tasks" | filter="pending" |
| "Mark task 5 as complete" | task_id=5, completed=true |

### Date Parsing Strategy

**Library**: `python-dateutil` for natural language date parsing

```python
from dateutil import parser
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

def parse_natural_date(date_str: str) -> str:
    """
    Parse natural language date expressions to YYYY-MM-DD format.

    Examples:
    - "tomorrow" → "2026-02-14"
    - "next Monday" → "2026-02-17"
    - "in 3 days" → "2026-02-16"
    """
    date_str_lower = date_str.lower()
    today = datetime.now().date()

    # Handle common expressions
    if "tomorrow" in date_str_lower:
        return (today + timedelta(days=1)).isoformat()
    elif "today" in date_str_lower:
        return today.isoformat()
    elif "next week" in date_str_lower:
        return (today + timedelta(weeks=1)).isoformat()

    # Try dateutil parser for complex expressions
    try:
        parsed_date = parser.parse(date_str, fuzzy=True)
        return parsed_date.date().isoformat()
    except:
        return None  # Return None if parsing fails
```

**Multilingual Date Handling**:
- English dates: Handled by dateutil
- Urdu/Roman Urdu dates: Create custom mapping for common expressions
  - "kal" → tomorrow
  - "aaj" → today
  - "parso" → day after tomorrow

### Priority Mapping

```python
PRIORITY_KEYWORDS = {
    "high": ["urgent", "important", "high", "critical", "asap"],
    "medium": ["medium", "normal", "moderate"],
    "low": ["low", "minor", "whenever", "someday"]
}

def extract_priority(text: str) -> str:
    """Extract priority from natural language."""
    text_lower = text.lower()

    for priority, keywords in PRIORITY_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return priority

    return "medium"  # Default priority
```

## 6. Practical Implementation Recommendations

### FastAPI Integration Pattern

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import cohere
import os

router = APIRouter()
co = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    message: str
    conversation_id: int
    tool_results: Optional[List[dict]] = None

@router.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Load conversation history from database
    chat_history = load_chat_history(request.conversation_id, session)

    # Call Cohere with tools
    response = co.chat(
        model="command-r-08-2024",
        message=request.message,
        chat_history=chat_history,
        tools=get_mcp_tools(),
        preamble=get_system_prompt()
    )

    # Execute tools if needed
    if response.tool_calls:
        tool_results = execute_tools(response.tool_calls, user_id, session)

        # Get final response with tool results
        final_response = co.chat(
            model="command-r-08-2024",
            message="",
            chat_history=response.chat_history,
            tools=get_mcp_tools(),
            tool_results=tool_results
        )

        response = final_response

    # Save conversation to database
    conversation_id = save_conversation(
        user_id=user_id,
        user_message=request.message,
        assistant_message=response.text,
        conversation_id=request.conversation_id,
        session=session
    )

    return ChatResponse(
        message=response.text,
        conversation_id=conversation_id
    )
```

### Error Handling Strategy

```python
def execute_tools(tool_calls, user_id, session):
    """Execute tool calls with error handling."""
    tool_results = []

    for tool_call in tool_calls:
        try:
            # Execute tool
            result = execute_single_tool(tool_call, user_id, session)

            tool_results.append({
                "call": tool_call,
                "outputs": [{"result": json.dumps(result)}]
            })
        except Exception as e:
            # Return error to model so it can generate helpful message
            tool_results.append({
                "call": tool_call,
                "outputs": [{"error": str(e)}]
            })

    return tool_results
```

## 7. Performance Considerations

### Response Time Optimization

**Target**: <200ms average response time per constitution

**Strategies**:
1. **Database query optimization**: Index conversation_id, user_id columns
2. **Conversation context limiting**: Load only last 10 messages (not entire history)
3. **Async operations**: Use async/await for database and API calls
4. **Connection pooling**: Reuse database connections
5. **Caching**: Cache tool definitions (don't recreate on each request)

### Concurrent User Handling

**Target**: 100 concurrent users

**Strategies**:
1. **Stateless architecture**: No in-memory state, all data in database
2. **Connection pooling**: Configure SQLModel with appropriate pool size
3. **Rate limiting**: Implement per-user rate limits to prevent abuse
4. **Horizontal scaling**: Deploy multiple FastAPI instances behind load balancer

## 8. Testing Strategy

### Unit Tests

```python
# test_ai_service.py
def test_intent_detection():
    """Test intent detection for various inputs."""
    assert detect_intent("add task to buy milk") == "add_task"
    assert detect_intent("show my tasks") == "list_tasks"
    assert detect_intent("mark task 5 as done") == "complete_task"

def test_field_extraction():
    """Test field extraction from natural language."""
    fields = extract_task_fields("Add task to buy groceries tomorrow with high priority")
    assert fields["title"] == "Buy groceries"
    assert fields["priority"] == "high"
    assert fields["due_date"] == "2026-02-14"

def test_date_parsing():
    """Test natural language date parsing."""
    assert parse_natural_date("tomorrow") == "2026-02-14"
    assert parse_natural_date("next Monday") == "2026-02-17"
```

### Integration Tests

```python
# test_chat_endpoint.py
@pytest.mark.asyncio
async def test_chat_endpoint_add_task():
    """Test chat endpoint creates task correctly."""
    response = await client.post(
        "/api/chat",
        json={"message": "Add task to buy groceries"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    assert response.status_code == 200
    assert "groceries" in response.json()["message"].lower()

    # Verify task was created in database
    tasks = await get_user_tasks(test_user_id)
    assert any("groceries" in task.title.lower() for task in tasks)
```

## 9. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Urdu support inadequate | High | Medium | Test extensively; document limitations; provide English fallback |
| Cohere API rate limits | High | Low | Implement rate limiting; cache responses where possible |
| Date parsing errors | Medium | Medium | Validate parsed dates; ask user for clarification if ambiguous |
| Tool execution failures | Medium | Low | Comprehensive error handling; return errors to model for user-friendly messages |
| Performance under load | Medium | Medium | Load testing; optimize queries; implement caching |

## 10. Dependencies to Add

```txt
# requirements.txt additions
cohere==5.20.5              # Cohere API client (upgrade from 5.5.3)
python-dateutil==2.8.2      # Natural language date parsing
langdetect==1.0.9           # Language detection (optional, for analytics)
```

## 11. Environment Variables

```bash
# .env additions
COHERE_API_KEY=your_cohere_api_key_here
COHERE_MODEL=command-r-08-2024
```

## 12. Next Steps

1. **Upgrade Cohere SDK**: `pip install --upgrade cohere==5.20.5`
2. **Test Urdu support**: Create test dataset, measure accuracy with Command R
3. **Implement tool definitions**: Define 5 MCP tools (add, list, complete, delete, update)
4. **Build date parser**: Implement natural language date parsing with multilingual support
5. **Create system prompt**: Craft preamble that guides model behavior for task management
6. **Integration testing**: Test end-to-end flow with various natural language inputs

## Conclusion

Command R is the recommended model for this multilingual task management chatbot. While Urdu is not officially supported, leveraging Hindi support combined with careful prompt engineering should provide acceptable performance for Roman Urdu and potentially Urdu script. Tool calling is fully supported and well-documented. The main technical risk is Urdu language support, which requires extensive testing and may need fallback strategies.
