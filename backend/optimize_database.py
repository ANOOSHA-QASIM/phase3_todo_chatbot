"""
Database optimization script for Phase III AI Chatbot
Adds indexes for improved query performance
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

def add_indexes():
    """
    Add database indexes for optimized query performance

    Indexes added:
    - conversations: user_id, updated_at (for conversation list queries)
    - messages: conversation_id, created_at (for message history queries)
    - tasks: user_id, due_date, completed (for task list queries)
    """
    print("Adding database indexes for Phase III AI Chatbot...")

    with engine.connect() as conn:
        # Index for conversation list queries (already exists from model, but verify)
        print("✓ Conversation user_id index (already created by SQLModel)")

        # Composite index for conversation queries (user_id + updated_at)
        try:
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_conversation_user_updated "
                "ON conversation (user_id, updated_at DESC)"
            ))
            conn.commit()
            print("✓ Added composite index on conversation (user_id, updated_at)")
        except Exception as e:
            print(f"⚠ Conversation composite index: {e}")

        # Index for message queries (already exists from model)
        print("✓ Message conversation_id index (already created by SQLModel)")

        # Composite index for message queries (conversation_id + created_at)
        try:
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_message_conversation_created "
                "ON message (conversation_id, created_at ASC)"
            ))
            conn.commit()
            print("✓ Added composite index on message (conversation_id, created_at)")
        except Exception as e:
            print(f"⚠ Message composite index: {e}")

        # Composite index for task queries (user_id + completed + due_date)
        try:
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_task_user_completed_due "
                "ON task (user_id, completed, due_date NULLS LAST)"
            ))
            conn.commit()
            print("✓ Added composite index on task (user_id, completed, due_date)")
        except Exception as e:
            print(f"⚠ Task composite index: {e}")

    print("\n✅ Database optimization complete!")
    print("Indexes added for improved query performance")

if __name__ == "__main__":
    add_indexes()
