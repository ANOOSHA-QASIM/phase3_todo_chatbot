#!/usr/bin/env python3
"""
Integration test for user_task_id functionality
Tests that user_task_id is correctly assigned and used for operations
"""

import os
from dotenv import load_dotenv
from sqlmodel import Session, select
from models import Task
from db import engine

load_dotenv()

def test_user_task_id():
    """Test user_task_id assignment and operations"""

    test_user_id = "test-user-12345"

    with Session(engine) as session:
        # Clean up any existing test tasks
        statement = select(Task).where(Task.user_id == test_user_id)
        existing_tasks = session.exec(statement).all()
        for task in existing_tasks:
            session.delete(task)
        session.commit()

        print("[TEST] Creating first task for test user...")
        # Create first task
        statement = select(Task.user_task_id).where(Task.user_id == test_user_id).order_by(Task.user_task_id.desc())
        max_user_task_id = session.exec(statement).first()
        next_user_task_id = (max_user_task_id or 0) + 1

        task1 = Task(
            user_id=test_user_id,
            title="Test Task 1",
            description="First test task",
            user_task_id=next_user_task_id,
            completed=False
        )
        session.add(task1)
        session.commit()
        session.refresh(task1)

        assert task1.user_task_id == 1, f"Expected user_task_id=1, got {task1.user_task_id}"
        print(f"[OK] Task 1 created with user_task_id={task1.user_task_id}")

        print("[TEST] Creating second task for test user...")
        # Create second task
        statement = select(Task.user_task_id).where(Task.user_id == test_user_id).order_by(Task.user_task_id.desc())
        max_user_task_id = session.exec(statement).first()
        next_user_task_id = (max_user_task_id or 0) + 1

        task2 = Task(
            user_id=test_user_id,
            title="Test Task 2",
            description="Second test task",
            user_task_id=next_user_task_id,
            completed=False
        )
        session.add(task2)
        session.commit()
        session.refresh(task2)

        assert task2.user_task_id == 2, f"Expected user_task_id=2, got {task2.user_task_id}"
        print(f"[OK] Task 2 created with user_task_id={task2.user_task_id}")

        print("[TEST] Finding task by user_task_id...")
        # Find task by user_task_id
        statement = select(Task).where(
            Task.user_task_id == 1,
            Task.user_id == test_user_id
        )
        found_task = session.exec(statement).first()

        assert found_task is not None, "Task not found by user_task_id"
        assert found_task.title == "Test Task 1", f"Expected 'Test Task 1', got '{found_task.title}'"
        print(f"[OK] Found task by user_task_id: {found_task.title}")

        print("[TEST] Finding task by title (case-insensitive)...")
        # Find task by title (case-insensitive)
        statement = select(Task).where(Task.user_id == test_user_id)
        tasks = session.exec(statement).all()
        found_by_title = None
        for t in tasks:
            if t.title.lower() == "test task 2".lower():
                found_by_title = t
                break

        assert found_by_title is not None, "Task not found by title"
        assert found_by_title.user_task_id == 2, f"Expected user_task_id=2, got {found_by_title.user_task_id}"
        print(f"[OK] Found task by title: {found_by_title.title} (user_task_id={found_by_title.user_task_id})")

        print("[TEST] Cleaning up test tasks...")
        # Clean up
        for task in [task1, task2]:
            session.delete(task)
        session.commit()
        print("[OK] Test tasks cleaned up")

        print("\n[SUCCESS] All user_task_id tests passed!")

if __name__ == "__main__":
    test_user_task_id()
