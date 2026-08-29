from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.models import TaskStatus
from app import crud
from app.api.events import notifier

router = APIRouter()

@router.get("", response_model=List[TaskResponse])
def get_all_tasks(status: Optional[TaskStatus] = None, limit: int = 50, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db, status=status, limit=limit)
    return [
        TaskResponse(
            id=t.id,
            title=t.title,
            prompt=t.prompt,
            skills=t.skills,
            schedule_cron=t.schedule_cron,
            status=t.status,
            result_summary=t.result_summary,
            last_run_at=t.last_run_at,
            next_run_at=t.next_run_at,
            created_at=t.created_at
        )
        for t in tasks
    ]

@router.get("/pending", response_model=List[TaskResponse])
def get_pending_tasks(limit: int = 20, db: Session = Depends(get_db)):
    """Convenient endpoint for background AI workers to pull tasks."""
    tasks = crud.get_tasks(db, status=TaskStatus.PENDING, limit=limit)
    return [
        TaskResponse(
            id=t.id,
            title=t.title,
            prompt=t.prompt,
            skills=t.skills,
            schedule_cron=t.schedule_cron,
            status=t.status,
            result_summary=t.result_summary,
            last_run_at=t.last_run_at,
            next_run_at=t.next_run_at,
            created_at=t.created_at
        )
        for t in tasks
    ]

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(
        id=task.id,
        title=task.title,
        prompt=task.prompt,
        skills=task.skills,
        schedule_cron=task.schedule_cron,
        status=task.status,
        result_summary=task.result_summary,
        last_run_at=task.last_run_at,
        next_run_at=task.next_run_at,
        created_at=task.created_at
    )

@router.post("", response_model=TaskResponse, status_code=201)
async def create_new_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    task = crud.create_task(db, task_in)
    await notifier.broadcast("task_created", {
        "id": task.id,
        "title": task.title,
        "skills": task.skills
    })
    return TaskResponse(
        id=task.id,
        title=task.title,
        prompt=task.prompt,
        skills=task.skills,
        schedule_cron=task.schedule_cron,
        status=task.status,
        result_summary=task.result_summary,
        last_run_at=task.last_run_at,
        next_run_at=task.next_run_at,
        created_at=task.created_at
    )

@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(task_id: str, update_in: TaskUpdate, db: Session = Depends(get_db)):
    task = crud.update_task(db, task_id, update_in)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await notifier.broadcast("task_updated", {
        "id": task.id,
        "status": task.status.value,
        "result_summary": task.result_summary
    })
    return TaskResponse(
        id=task.id,
        title=task.title,
        prompt=task.prompt,
        skills=task.skills,
        schedule_cron=task.schedule_cron,
        status=task.status,
        result_summary=task.result_summary,
        last_run_at=task.last_run_at,
        next_run_at=task.next_run_at,
        created_at=task.created_at
    )

@router.delete("/{task_id}")
async def delete_task(task_id: str, db: Session = Depends(get_db)):
    success = crud.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    await notifier.broadcast("task_deleted", {"id": task_id})
    return {"ok": True}
