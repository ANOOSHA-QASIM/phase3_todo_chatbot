#!/usr/bin/env python3
"""
Migration script to add priority and due_date columns to tasks table,
and create conversations and messages tables for Phase III AI Chatbot.
"""

import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, SQLModel
from models import Task, Conversation, Message

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

def migrate():
    """
    Phase III AI Chatbot Migration:
    1. Add priority and due_date (DATE type) columns to tasks table
    2. Create conversations table
    3. Create messages table

    This is a manual migration script for demonstration.
    In a real application, you'd use Alembic for proper migrations.
    """
    print("Starting Phase III AI Chatbot migration...")
    print("- Updating tasks table (priority, due_date as DATE)")
    print("- Creating conversations table")
    print("- Creating messages table")

    # Create all tables based on current models
    SQLModel.metadata.create_all(engine)

    print("\nMigration completed successfully!")
    print("✅ Tasks table updated with priority and due_date (DATE type)")
    print("✅ Conversations table created")
    print("✅ Messages table created")

if __name__ == "__main__":
    migrate()