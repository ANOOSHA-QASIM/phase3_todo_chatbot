from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Optional
from models import Task, TaskCreate, TaskUpdate, TaskRead, SuccessResponse, ErrorResponse, PaginatedTasksResponse
from db import get_session
from dependencies import get_current_user
from datetime import datetime

router = APIRouter()


# ---------------- Helper function ----------------
def get_task_by_id_or_title(session: Session, user_id: str, user_task_id: Optional[int], title: Optional[str]):
    """
    Find a task by user_task_id or title (case-insensitive).
    Prioritizes user_task_id if both are provided.
    Always filters by user_id.
    """
    task = None

    # Prioritize user_task_id if provided
    if user_task_id is not None:
        statement = select(Task).where(
            Task.user_task_id == user_task_id,
            Task.user_id == user_id
        )
        task = session.exec(statement).first()

    # Fall back to title if user_task_id not provided or not found
    if not task and title:
        statement = select(Task).where(Task.user_id == user_id)
        tasks = session.exec(statement).all()
        for t in tasks:
            if t.title.lower() == title.lower():
                task = t
                break

    return task


# ---------------- Get all tasks ----------------
@router.get("/", response_model=PaginatedTasksResponse)
async def get_tasks(
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> PaginatedTasksResponse:
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    task_list = [task.dict() for task in tasks]

    return PaginatedTasksResponse(
        success=True,
        data={
            "tasks": task_list,
            "total": len(task_list),
            "page": 1,
            "limit": len(task_list)
        }
    )


# ---------------- Create task ----------------
@router.post("/", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> SuccessResponse:
    statement = select(Task.user_task_id).where(Task.user_id == user_id).order_by(Task.user_task_id.desc())
    max_user_task_id = session.exec(statement).first()
    next_user_task_id = (max_user_task_id or 0) + 1

    task = Task(
        title=task_data.title,
        description=task_data.description,
        completed=task_data.completed,
        priority=task_data.priority,
        due_date=task_data.due_date,
        user_id=user_id,
        user_task_id=next_user_task_id
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    return SuccessResponse(
        success=True,
        data={"message": f"Task '{task.title}' added successfully ✅", "task_id": task.user_task_id}
    )


# ---------------- Update task ----------------
@router.put("/edit", response_model=SuccessResponse)
async def update_task(
    user_task_id: Optional[int] = None,
    title: Optional[str] = None,
    new_title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    completed: Optional[bool] = None,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> SuccessResponse:

    print("Looking for user_task_id:", user_task_id)
    print("Current logged-in user_id:", user_id)

    task = get_task_by_id_or_title(session, user_id, user_task_id, title)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if new_title:
        task.title = new_title.strip()
    if description is not None:
        task.description = description.strip() if description else None
    if priority:
        task.priority = priority
    if due_date:
        try:
            task.due_date = datetime.fromisoformat(due_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid due date format")
    if completed is not None:
        task.completed = completed

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    return SuccessResponse(success=True, data=task.dict())


# ---------------- Delete task ----------------
@router.delete("/delete", response_model=SuccessResponse)
async def delete_task(
    user_task_id: Optional[int] = None,
    title: Optional[str] = None,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> SuccessResponse:
    task = get_task_by_id_or_title(session, user_id, user_task_id, title)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_title = task.title
    session.delete(task)
    session.commit()

    return SuccessResponse(success=True, data={"message": f"Task '{task_title}' deleted successfully 🗑️"})


# ---------------- Toggle completion ----------------
@router.patch("/toggle", response_model=SuccessResponse)
async def toggle_task_completion(
    user_task_id: Optional[int] = None,
    title: Optional[str] = None,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> SuccessResponse:

    print("Looking for user_task_id:", user_task_id)
    print("Current logged-in user_id:", user_id)

    task = get_task_by_id_or_title(session, user_id, user_task_id, title)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = not task.completed
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    status_text = "complete ✅" if task.completed else "incomplete ❌"
    return SuccessResponse(success=True, data={"message": f"Task '{task.title}' marked as {status_text}"})


# ---------------- Get single task ----------------
@router.get("/{user_task_id}", response_model=SuccessResponse)
async def get_task(
    user_task_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> SuccessResponse:
    statement = select(Task).where(Task.user_task_id == user_task_id, Task.user_id == user_id)
    task = session.exec(statement).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return SuccessResponse(success=True, data=task.dict())
