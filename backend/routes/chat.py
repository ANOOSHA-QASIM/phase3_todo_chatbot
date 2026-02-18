"""
Chat routes for Phase III AI Chatbot
Handles conversation with Cohere AI and MCP tool execution
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
import sys
import os
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models import Conversation, Message, RoleEnum
from dependencies import get_current_user
from db import get_session
from app.services.ai_service import AIService
from app.mcp.tools import add_task, list_tasks, complete_task, delete_task, update_task

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize AI service
ai_service = AIService()


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[int] = None

    @validator('message')
    def validate_message(cls, v):
        """Validate message is not empty after stripping"""
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    message: str
    conversation_id: int
    tool_results: Optional[List[Dict[str, Any]]] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Chat endpoint for AI-powered todo management

    Stateless conversation flow:
    1. Fetch conversation history from DB
    2. Append new user message
    3. Save user message
    4. Call Cohere AI with tools
    5. Execute tool calls if any
    6. Save assistant response
    7. Return response

    Args:
        request: Chat request with message and optional conversation_id
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        Chat response with AI message and conversation_id
    """
    user_id = current_user


    try:
        logger.info(f"Chat request from user {user_id}, conversation_id: {request.conversation_id}")

        # Step 1: Get or create conversation
        conversation = None
        if request.conversation_id:
            # Load existing conversation
            conversation = session.get(Conversation, request.conversation_id)
            if not conversation or conversation.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            # Create new conversation
            conversation = Conversation(user_id=user_id)
            session.add(conversation)
            session.commit()
            session.refresh(conversation)

        # Step 2: Fetch conversation history (last 20 messages)
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(20)
        )
        messages = session.exec(statement).all()
        messages.reverse()  # Oldest first

        # Format history for Cohere
        conversation_history = [
            {
                "role": "USER" if msg.role == RoleEnum.user else "CHATBOT",
                "content": msg.content
            }
            for msg in messages
        ]

        # Step 3: Save user message
        user_message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role=RoleEnum.user,
            content=request.message
        )
        session.add(user_message)
        session.commit()

        # Step 4: Define MCP tools for Cohere
        tools = [
            {
                "name": "add_task",
                "description": "Add a new task for the user. Always separate title, description, priority and due_date correctly. Title should be short and clean. Description should contain extra details only.",
                "parameter_definitions": {
                    "user_id": {
                        "description": "User ID (automatically provided)",
                        "type": "string",
                        "required": True
                    },
                    "title": {
                        "description": "Short task title only. Do NOT include description here.",
                        "type": "string",
                        "required": True
                    },
                    "description": {
                        "description": "Extra details about the task (optional)",
                        "type": "string",
                        "required": False
                    },
                    "priority": {
                        "description": "Task priority: high, medium, or low",
                        "type": "string",
                        "required": False
                    },
                    "due_date": {
                        "description": "Due date in ISO format YYYY-MM-DD",
                        "type": "string",
                        "required": False
                    }
                }
            },

            {
                "name": "list_tasks",
                "description": "List all tasks for the user with optional status filter",
                "parameter_definitions": {
                    "user_id": {
                        "description": "User ID (automatically provided)",
                        "type": "string",
                        "required": True
                    },
                    "status": {
                        "description": "Filter by status: pending, completed, or all (default: all)",
                        "type": "string",
                        "required": False
                    }
                }
            },
            {
                "name": "complete_task",
                "description": "Mark a task as completed or pending. You can identify task using task_id OR title.",
                "parameter_definitions": {
                    "user_id": {
                        "description": "User ID (automatically provided)",
                        "type": "string",
                        "required": True
                    },
                    "task_id": {
                        "description": "ID of the task",
                        "type": "integer",
                        "required": False
                    },
                    "title": {
                        "description": "Title of the task (if task_id not provided)",
                        "type": "string",
                        "required": False
                    },
                    "completed": {
                        "description": "True to mark complete, False to mark pending",
                        "type": "boolean",
                        "required": False
                    }
                }
            },

            {
                "name": "delete_task",
                "description": "Delete a task permanently",
                "parameter_definitions": {
                    "user_id": {
                        "description": "User ID (automatically provided)",
                        "type": "string",
                        "required": True
                    },
                    "task_id": {
                        "description": "ID of the task to delete",
                        "type": "integer",
                        "required": True
                    },
                }
            },
            {
                "name": "update_task",
                "description": "Update a task. You can identify the task using task_id OR title. Only update the fields provided. Do not require all fields.",
                "parameter_definitions": {
                    "user_id": {
                        "description": "User ID (automatically provided)",
                        "type": "string",
                        "required": True
                    },
                    "task_id": {
                        "description": "ID of the task to update (optional if title is provided)",
                        "type": "integer",
                        "required": False
                    },
                    "title": {
                        "description": "Current title of the task (used to find task if task_id not provided)",
                        "type": "string",
                        "required": False
                    },
                    "new_title": {
                        "description": "New task title",
                        "type": "string",
                        "required": False
                    },
                    "description": {
                        "description": "New task description",
                        "type": "string",
                        "required": False
                    },
                    "priority": {
                        "description": "New priority: high, medium, or low",
                        "type": "string",
                        "required": False
                    },
                    "due_date": {
                        "description": "New due date in ISO format YYYY-MM-DD",
                        "type": "string",
                        "required": False
                    },
                    "status": {
                        "description": "Update task status: completed or pending",
                        "type": "string",
                        "required": False
                    }
                }
            }

        ]

        # Step 5: Call Cohere AI
        logger.info(f"Calling Cohere AI for user {user_id}")
        ai_response = ai_service.chat(
            message=request.message,
            conversation_history=conversation_history,
            tools=tools,
            user_id=user_id
        )

        # Step 6: Execute tool calls if any
        tool_results = []
        if ai_response.get("tool_calls"):
            logger.info(f"Executing {len(ai_response['tool_calls'])} tool calls")
            for tool_call in ai_response["tool_calls"]:
                tool_name = tool_call["name"]
                parameters = tool_call["parameters"]

                # Inject user_id into parameters
                parameters["user_id"] = user_id

                logger.info(f"Executing tool: {tool_name}")

                # Execute the appropriate tool
                try:
                    if tool_name == "add_task":
                        result = add_task(**parameters)
                    elif tool_name == "list_tasks":
                        result = list_tasks(**parameters)
                    elif tool_name == "complete_task":
                        result = complete_task(**parameters)
                    elif tool_name == "delete_task":
                        result = delete_task(**parameters)
                    elif tool_name == "update_task":
                        result = update_task(**parameters)
                except Exception as e:
                    result = {"success": False, "error": str(e)}

                tool_results.append({
                    "tool_name": tool_name,
                    "parameters": parameters,
                    "result": result
                })


        # Step 7: Generate friendly response based on tool results
        final_response_text = ai_response.get("text", "")

        if tool_results:
            tool_result = tool_results[0]["result"]
            tool_name = tool_results[0]["tool_name"]

            if tool_name == "add_task":
                if tool_result.get("success"):
                    task_data = tool_result.get("task", {})
                    final_response_text = f"Got it! Task '{task_data.get('title')}' added successfully ✅"
                else:
                    error_msg = tool_result.get("error", "Unknown error")
                    final_response_text = f"Sorry, I couldn't add the task: {error_msg} 😔"

            elif tool_name == "list_tasks":
                if tool_result.get("success"):
                    tasks = tool_result.get("tasks", [])
                    count = tool_result.get("count", 0)

                    if count == 0:
                        final_response_text = "You have no tasks yet. Want to add one? 📝"
                    else:
                        # Format task list
                        task_lines = []
                        for i, task in enumerate(tasks, 1):
                            task_status = "✅" if task.get("completed") else "⬜"
                            title = task.get("title")
                            priority = task.get("priority")
                            due_date = task.get("due_date")

                            line = f"{i}. {task_status} {title}"
                            if priority:
                                line += f" [{priority}]"
                            if due_date:
                                line += f" (Due: {due_date})"

                            task_lines.append(line)

                        final_response_text = f"Here are your tasks ({count} total):\n\n" + "\n".join(task_lines)
                else:
                    error_msg = tool_result.get("error", "Unknown error")
                    final_response_text = f"Sorry, I couldn't fetch your tasks: {error_msg} 😔"

            elif tool_name == "complete_task":
                if tool_result.get("success"):
                    task_data = tool_result.get("task", {})
                    is_completed = task_data.get("completed", False)
                    status_text = "complete ✅" if is_completed else "incomplete ❌"
                    final_response_text = f"Great! Task '{task_data.get('title')}' marked as {status_text}"
                else:
                    error_msg = tool_result.get("error", "Unknown error")
                    final_response_text = f"Sorry, I couldn't complete the task: {error_msg} 😔"

            elif tool_name == "delete_task":
                if tool_result.get("success"):
                    message = tool_result.get("message", "Task deleted")
                    final_response_text = f"{message} 🗑️"
                else:
                    error_msg = tool_result.get("error", "Unknown error")
                    final_response_text = f"Sorry, I couldn't delete the task: {error_msg} 😔"

            elif tool_name == "update_task":
                if tool_result.get("success"):
                    task_data = tool_result.get("task", {})
                    final_response_text = f"Perfect! Task '{task_data.get('title')}' updated successfully ✏️"
                else:
                    error_msg = tool_result.get("error", "Unknown error")
                    final_response_text = f"Sorry, I couldn't update the task: {error_msg} 😔"

        # Step 8: Save assistant response
        assistant_message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role=RoleEnum.assistant,
            content=final_response_text
        )
        session.add(assistant_message)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()

        # Step 9: Return response
        return ChatResponse(
            message=final_response_text,
            conversation_id=conversation.id,
            tool_results=tool_results if tool_results else None
        )

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat error: {str(e)}"
        )
