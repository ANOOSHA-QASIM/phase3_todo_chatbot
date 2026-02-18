#!/usr/bin/env python3
"""
Migration script to add user_task_id column to tasks table.
This column provides user-specific task IDs starting from 1 for each user.
"""

import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, select, text
from models import Task

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

def migrate():
    """
    Add user_task_id column and populate it for existing tasks.
    Each user's tasks will be numbered starting from 1.
    """
    print("Starting user_task_id migration...")

    with Session(engine) as session:
        # Add the column if it doesn't exist
        try:
            session.exec(text(
                "ALTER TABLE task ADD COLUMN IF NOT EXISTS user_task_id INTEGER"
            ))
            session.commit()
            print("[OK] Added user_task_id column")
        except Exception as e:
            print(f"[WARN] Column might already exist: {e}")
            session.rollback()

        # Create index on user_task_id
        try:
            session.exec(text(
                "CREATE INDEX IF NOT EXISTS ix_task_user_task_id ON task (user_task_id)"
            ))
            session.commit()
            print("[OK] Created index on user_task_id")
        except Exception as e:
            print(f"[WARN] Index might already exist: {e}")
            session.rollback()

        # Get all unique user_ids
        statement = select(Task.user_id).distinct()
        user_ids = session.exec(statement).all()

        print(f"\nPopulating user_task_id for {len(user_ids)} users...")

        # For each user, assign sequential user_task_ids
        for user_id in user_ids:
            statement = select(Task).where(Task.user_id == user_id).order_by(Task.created_at)
            tasks = session.exec(statement).all()

            for idx, task in enumerate(tasks, start=1):
                task.user_task_id = idx
                session.add(task)

            session.commit()
            print(f"[OK] Assigned user_task_ids for user {user_id}: {len(tasks)} tasks")

        print("\n[SUCCESS] Migration completed successfully!")
        print(f"   Total users processed: {len(user_ids)}")

if __name__ == "__main__":
    migrate()
