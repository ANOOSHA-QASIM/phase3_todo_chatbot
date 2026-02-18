"""
Conversation routes for Phase III AI Chatbot
Handles conversation history and session management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from pydantic import BaseModel
from datetime import datetime
import json


import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models import Conversation, Message, RoleEnum
from dependencies import get_current_user
from db import get_session

router = APIRouter()


class ConversationResponse(BaseModel):
    """Response model for conversation"""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    """Response model for message"""
    id: int
    conversation_id: int
    user_id: str
    role: str
    content: str
    created_at: datetime


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # ----- Safe handling -----
    if isinstance(current_user, str):
        try:
            current_user = json.loads(current_user)
        except json.JSONDecodeError:
            current_user = {"user_id": current_user}

    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user info"
        )
    # ------------------------

    try:
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(20)
        )
        conversations = session.exec(statement).all()
        return conversations

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversations: {str(e)}"
        )



@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # ----- Safe handling of current_user -----
    if isinstance(current_user, str):
        try:
            current_user = json.loads(current_user)
        except json.JSONDecodeError:
            # Agar parse fail ho, treat as plain string user_id
            current_user = {"user_id": current_user}

    # Ensure user_id exists
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user info"
        )
    # ----------------------------------------

    try:
        # Verify conversation exists and belongs to user
        conversation = session.get(Conversation, conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this conversation"
            )

        # Query messages for conversation
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(20)
        )

        messages = session.exec(statement).all()

        return messages

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching messages: {str(e)}"
        )
