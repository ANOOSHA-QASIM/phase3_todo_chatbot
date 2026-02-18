"""
MCP Tools for Phase III AI Chatbot
Task management tools exposed via MCP for Cohere AI
"""

from typing import Optional, Dict, Any
from datetime import date, datetime
from sqlmodel import select
from sqlalchemy.orm import Session
import sys, os

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from models import Task, PriorityEnum
from app.mcp.server import mcp, get_session


# ---------------- Helper ----------------
def get_task_by_user_task_id_or_title(
    session: Session,
    user_id: str,
    user_task_id: Optional[int] = None,
    title: Optional[str] = None
) -> Optional[Task]:
    task = None
    if user_task_id is not None:
        statement = select(Task).where(Task.user_task_id == user_task_id, Task.user_id == user_id)
        task = session.exec(statement).first()
    if not task and title:
        statement = select(Task).where(Task.user_id == user_id)
        tasks = session.exec(statement).all()
        for t in tasks:
            if title.strip().lower() == t.title.strip().lower():
                task = t
                break
    return task


# ---------------- Add Task ----------------
@mcp.tool()
def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    if not title or not isinstance(title, str) or len(title.strip()) < 1:
        return {"success": False, "error": "Title is required and must be a string"}

    title = title.strip()
    description = description.strip() if isinstance(description, str) else description

    priority_enum = None
    if priority:
        priority_lower = priority.lower()
        if priority_lower not in ["high", "medium", "low"]:
            return {"success": False, "error": "Priority must be one of: high, medium, low"}
        priority_enum = PriorityEnum(priority_lower)

    due_date_obj = None
    if due_date:
        try:
            due_date_obj = date.fromisoformat(due_date)
        except Exception:
            return {"success": False, "error": "Due date must be in YYYY-MM-DD format"}

    session = get_session()
    try:
        statement = select(Task.user_task_id).where(Task.user_id == user_id).order_by(Task.user_task_id.desc())
        max_user_task_id = session.exec(statement).first()
        next_user_task_id = (max_user_task_id or 0) + 1

        new_task = Task(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority_enum,
            due_date=due_date_obj,
            completed=False,
            user_task_id=next_user_task_id
        )

        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        return {
            "success": True,
            "task": {
                "id": new_task.user_task_id,
                "title": new_task.title,
                "description": new_task.description,
                "priority": new_task.priority.value if new_task.priority else None,
                "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
                "completed": new_task.completed,
                "created_at": new_task.created_at.isoformat()
            },
            "message": f"Task '{new_task.title}' added successfully ✅"
        }

    except Exception as e:
        session.rollback()
        return {"success": False, "error": str(e)}
    finally:
        session.close()


# ---------------- List Tasks ----------------
@mcp.tool()
def list_tasks(user_id: str, status: Optional[str] = None) -> Dict[str, Any]:
    status = status if status in ["pending", "completed", "all"] else "all"
    session = get_session()
    try:
        query = select(Task).where(Task.user_id == user_id)
        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)
        query = query.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc())
        tasks = session.exec(query).all()

        task_list = []
        for t in tasks:
            task_list.append({
                "id": t.user_task_id,
                "title": t.title,
                "description": t.description,
                "priority": t.priority.value if t.priority else None,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "completed": t.completed,
                "created_at": t.created_at.isoformat()
            })

        return {"success": True, "tasks": task_list, "count": len(task_list)}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        session.close()


# ---------------- Update Task ----------------
# ---------------- Update Task ----------------
@mcp.tool()
def update_task(
    user_id: str,
    task_id: Optional[int] = None,
    title: Optional[str] = None,
    new_title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    status: Optional[str] = None   # 👈 ADD THIS
) -> Dict[str, Any]:

    if not task_id and not title:
        return {"success": False, "error": "Provide task_id or title"}

    session = get_session()
    try:
        task = get_task_by_user_task_id_or_title(session, user_id, task_id, title)

        if not task:
            return {"success": False, "error": "Task not found"}

        # -------- Title Update --------
        if new_title:
            task.title = new_title.strip()

        # -------- Description Update --------
        if description is not None:
            task.description = description.strip()

        # -------- Priority Update --------
        if priority:
            priority_lower = priority.lower()
            if priority_lower not in ["high", "medium", "low"]:
                return {"success": False, "error": "Priority must be high, medium or low"}
            task.priority = PriorityEnum(priority_lower)

        # -------- Due Date Update --------
        if due_date:
            try:
                task.due_date = date.fromisoformat(due_date)
            except:
                return {"success": False, "error": "Invalid due date format (YYYY-MM-DD required)"}

        # -------- Status Update (IMPORTANT FIX) --------
        if status:
            if status.lower() in ["completed", "complete"]:
                task.completed = True
            elif status.lower() in ["pending", "incomplete"]:
                task.completed = False

        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "success": True,
            "task": {
                "id": task.user_task_id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value if task.priority else None,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "completed": task.completed
            },
            "message": f"Task '{task.title}' updated successfully ✏️"
        }

    except Exception as e:
        session.rollback()
        return {"success": False, "error": str(e)}
    finally:
        session.close()


# ---------------- Complete Task ----------------
@mcp.tool()
def complete_task(
    user_id: str,
    task_id: Optional[int] = None,
    title: Optional[str] = None,
    completed: Optional[bool] = None
) -> Dict[str, Any]:
    if not task_id and not title:
        return {"success": False, "error": "Provide task_id or title"}

    session = get_session()
    try:
        task = get_task_by_user_task_id_or_title(session, user_id, task_id, title)
        if not task:
            return {"success": False, "error": "Task not found"}

        # If completed is explicitly provided, set it; otherwise toggle
        if completed is not None:
            task.completed = completed
        else:
            task.completed = not task.completed
            
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)

        status_text = "completed ✅" if task.completed else "incomplete ❌"
        return {
            "success": True,
            "task": {
                "id": task.user_task_id,
                "title": task.title,
                "completed": task.completed
            },
            "message": f"Task '{task.title}' marked as {status_text}"
        }
    except Exception as e:
        session.rollback()
        return {"success": False, "error": str(e)}
    finally:
        session.close()


# ---------------- Delete Task ----------------
@mcp.tool()
def delete_task(
    user_id: str,
    task_id: Optional[int] = None,
    title: Optional[str] = None
) -> Dict[str, Any]:
    if not task_id and not title:
        return {"success": False, "error": "Provide task_id or title"}

    session = get_session()
    try:
        task = get_task_by_user_task_id_or_title(session, user_id, task_id, title)
        if not task:
            return {"success": False, "error": "Task not found"}

        session.delete(task)
        session.commit()

        return {
            "success": True,
            "task": {
                "id": task.user_task_id,
                "title": task.title
            },
            "message": f"Task '{task.title}' deleted successfully 🗑️"
        }
    except Exception as e:
        session.rollback()
        return {"success": False, "error": str(e)}
    finally:
        session.close()
