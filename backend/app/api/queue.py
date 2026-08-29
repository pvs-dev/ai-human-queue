from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import QueueItemCreate, QueueItemAnswer, QueueItemResponse
from app import crud
from app.api.events import notifier
from app.telegram_bot import send_telegram_notification

router = APIRouter()

@router.get("/pending", response_model=List[QueueItemResponse])
def get_pending_items(db: Session = Depends(get_db)):
    """Get all items currently in queue waiting for human response."""
    items = crud.get_pending_queue_items(db)
    return [
        QueueItemResponse(
            id=item.id,
            task_id=item.task_id,
            title=item.title,
            description=item.description,
            item_type=item.item_type,
            options=item.options,
            response_data=item.response_data,
            status=item.status,
            priority=item.priority,
            source_agent=item.source_agent,
            created_at=item.created_at,
            resolved_at=item.resolved_at
        )
        for item in items
    ]

@router.get("/all", response_model=List[QueueItemResponse])
def get_all_items(limit: int = 50, db: Session = Depends(get_db)):
    """Get all queue items (pending, resolved, cancelled)."""
    items = crud.get_all_queue_items(db, limit=limit)
    return [
        QueueItemResponse(
            id=item.id,
            task_id=item.task_id,
            title=item.title,
            description=item.description,
            item_type=item.item_type,
            options=item.options,
            response_data=item.response_data,
            status=item.status,
            priority=item.priority,
            source_agent=item.source_agent,
            created_at=item.created_at,
            resolved_at=item.resolved_at
        )
        for item in items
    ]

@router.get("/{item_id}", response_model=QueueItemResponse)
def get_single_item(item_id: str, db: Session = Depends(get_db)):
    item = crud.get_queue_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    return QueueItemResponse(
        id=item.id,
        task_id=item.task_id,
        title=item.title,
        description=item.description,
        item_type=item.item_type,
        options=item.options,
        response_data=item.response_data,
        status=item.status,
        priority=item.priority,
        source_agent=item.source_agent,
        created_at=item.created_at,
        resolved_at=item.resolved_at
    )

@router.post("/ask", response_model=QueueItemResponse, status_code=201)
async def ask_question(item_in: QueueItemCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Endpoint for AI agents to ask a question requiring human decision/input."""
    item = crud.create_queue_item(db, item_in)
    
    # Broadcast to SSE
    await notifier.broadcast("queue_item_created", {
        "id": item.id,
        "title": item.title,
        "item_type": item.item_type.value
    })
    
    # Push notification to Telegram bot
    background_tasks.add_task(send_telegram_notification, item.title, item.description, item.id)

    return QueueItemResponse(
        id=item.id,
        task_id=item.task_id,
        title=item.title,
        description=item.description,
        item_type=item.item_type,
        options=item.options,
        response_data=item.response_data,
        status=item.status,
        priority=item.priority,
        source_agent=item.source_agent,
        created_at=item.created_at,
        resolved_at=item.resolved_at
    )

@router.post("/{item_id}/answer", response_model=QueueItemResponse)
async def answer_item(item_id: str, answer_in: QueueItemAnswer, db: Session = Depends(get_db)):
    """User provides answer/selection. The item is resolved and removed from active queue."""
    item = crud.answer_queue_item(db, item_id, answer_in)
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    
    await notifier.broadcast("queue_item_resolved", {
        "id": item.id,
        "status": item.status.value,
        "response_data": item.response_data
    })
    return QueueItemResponse(
        id=item.id,
        task_id=item.task_id,
        title=item.title,
        description=item.description,
        item_type=item.item_type,
        options=item.options,
        response_data=item.response_data,
        status=item.status,
        priority=item.priority,
        source_agent=item.source_agent,
        created_at=item.created_at,
        resolved_at=item.resolved_at
    )

@router.post("/{item_id}/cancel", response_model=QueueItemResponse)
async def cancel_item(item_id: str, reason: Optional[str] = "User cancelled from UI", db: Session = Depends(get_db)):
    """User cancels the queue item. The thread is closed and AI will not continue this topic."""
    item = crud.cancel_queue_item(db, item_id, reason=reason)
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    
    await notifier.broadcast("queue_item_cancelled", {
        "id": item.id,
        "status": item.status.value,
        "reason": reason
    })
    return QueueItemResponse(
        id=item.id,
        task_id=item.task_id,
        title=item.title,
        description=item.description,
        item_type=item.item_type,
        options=item.options,
        response_data=item.response_data,
        status=item.status,
        priority=item.priority,
        source_agent=item.source_agent,
        created_at=item.created_at,
        resolved_at=item.resolved_at
    )
