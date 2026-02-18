"""
AI Service for Phase III AI Chatbot
Handles Cohere API integration for natural language understanding
"""

import os
from typing import Optional, List, Dict, Any
import cohere
from dotenv import load_dotenv
from app.services.date_parser import DateParser

load_dotenv()

class AIService:
    """
    AI Service using Cohere API for natural language understanding
    and intent detection for task management
    """

    # Priority keyword mapping
    PRIORITY_KEYWORDS = {
        "urgent": "high",
        "important": "high",
        "critical": "high",
        "asap": "high",
        "high": "high",
        "medium": "medium",
        "normal": "medium",
        "low": "low",
        "minor": "low",
    }

    # System prompt for Cohere
    SYSTEM_PROMPT = """You are a helpful, friendly multilingual AI assistant that helps users manage their todo tasks through natural conversation.

**Languages Supported:**
- English
- Urdu (اردو)
- Roman Urdu (Urdu written in Latin script)

**Your Capabilities:**
You can help users with the following task management operations:
1. **Add tasks** - Create new todo items with optional priority and due dates
2. **List tasks** - Show pending, completed, or all tasks
3. **Complete tasks** - Mark tasks as done
4. **Delete tasks** - Remove tasks
5. **Update tasks** - Modify task details

**Important Guidelines:**
- Always respond in the SAME language the user is using
- Be conversational, friendly, and concise
- Use the available tools to perform task operations
- Extract task details from natural language (no fixed format required)
- For dates, accept natural language like "tomorrow", "next Friday", "kal", "agle peer"
- For priority, detect keywords like "urgent", "important" → high priority
- If critical information is missing (like task title), politely ask the user
- Confirm actions in a friendly tone
- Handle errors gracefully with helpful messages

**Tool Usage:**
When the user wants to manage tasks, use the appropriate tool:
- To add a task → use add_task tool
- To view tasks → use list_tasks tool
- To mark complete → use complete_task tool
- To remove a task → use delete_task tool
- To modify a task → use update_task tool

**Response Style:**
- Keep responses short and friendly
- Confirm actions: "Got it! Task added ✅"
- Be empathetic on errors: "Sorry, I couldn't find that task 😔"
- Use light emojis for friendliness
- Never expose technical details or raw tool responses to users"""

    def __init__(self):
        """
        Initialize Cohere client with API key from environment
        """
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key or api_key == "your_cohere_api_key_here":
            raise ValueError(
                "COHERE_API_KEY not configured. "
                "Please set a valid Cohere API key in backend/.env"
            )

        self.model = os.getenv("COHERE_MODEL", "command-r-08-2024")
        self.client = cohere.Client(api_key)
        self.date_parser = DateParser()

    def _map_priority(self, text: str) -> Optional[str]:
        """
        Map priority keywords from natural language to priority enum

        Args:
            text: User message text

        Returns:
            Priority string (high, medium, low) or None
        """
        text_lower = text.lower()
        for keyword, priority in self.PRIORITY_KEYWORDS.items():
            if keyword in text_lower:
                return priority
        return None

    def _extract_date_from_text(self, text: str) -> Optional[str]:
        """
        Extract and parse date from natural language text

        Args:
            text: User message text

        Returns:
            ISO date string (YYYY-MM-DD) or None
        """
        parsed_date = self.date_parser.parse(text)
        if parsed_date:
            return parsed_date.isoformat()
        return None

    def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a chat message to Cohere API with tool support

        Args:
            message: User message
            conversation_history: Previous messages in conversation
            tools: Available MCP tools for the AI to use
            user_id: User ID for tool execution context

        Returns:
            Dictionary with response text and tool calls
        """
        try:
            # Build chat history for Cohere
            chat_history = []
            if conversation_history:
                for msg in conversation_history:
                    chat_history.append({
                        "role": msg.get("role", "USER"),
                        "message": msg.get("content", "")
                    })

            # Call Cohere chat API
            response = self.client.chat(
                model=self.model,
                message=message,
                chat_history=chat_history,
                tools=tools if tools else [],
                preamble=self.SYSTEM_PROMPT
            )

            # Extract response
            result = {
                "text": response.text,
                "tool_calls": []
            }

            # Check if Cohere wants to call tools
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    result["tool_calls"].append({
                        "name": tool_call.name,
                        "parameters": tool_call.parameters
                    })

            return result

        except Exception as e:
            return {
                "text": f"Sorry, I encountered an error: {str(e)}",
                "tool_calls": [],
                "error": str(e)
            }

    def format_tool_results_for_cohere(
        self,
        tool_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Format tool execution results for Cohere's next response

        Args:
            tool_results: List of tool execution results

        Returns:
            Formatted tool results for Cohere
        """
        formatted = []
        for result in tool_results:
            formatted.append({
                "call": {
                    "name": result.get("tool_name"),
                    "parameters": result.get("parameters", {})
                },
                "outputs": [result.get("result", {})]
            })
        return formatted
