from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import QueueItem, QueueItemStatus, QueueItemType, Task, TaskStatus, Skill
from app.schemas import QueueItemCreate, QueueItemAnswer, TaskCreate, TaskUpdate, SkillCreate

# ==================== QueueItem CRUD ====================

def get_pending_queue_items(db: Session) -> List[QueueItem]:
    return db.query(QueueItem).filter(
        QueueItem.status == QueueItemStatus.PENDING
    ).order_by(QueueItem.priority.desc(), QueueItem.created_at.asc()).all()

def get_all_queue_items(db: Session, limit: int = 50) -> List[QueueItem]:
    return db.query(QueueItem).order_by(QueueItem.created_at.desc()).limit(limit).all()

def get_queue_item(db: Session, item_id: str) -> Optional[QueueItem]:
    return db.query(QueueItem).filter(QueueItem.id == item_id).first()

def create_queue_item(db: Session, item_in: QueueItemCreate) -> QueueItem:
    options_list = [opt.model_dump() for opt in item_in.options] if item_in.options else []
    db_item = QueueItem(
        title=item_in.title,
        description=item_in.description,
        task_id=item_in.task_id,
        item_type=item_in.item_type,
        options=options_list,
        priority=item_in.priority,
        source_agent=item_in.source_agent,
        status=QueueItemStatus.PENDING
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def answer_queue_item(db: Session, item_id: str, answer_in: QueueItemAnswer) -> Optional[QueueItem]:
    db_item = get_queue_item(db, item_id)
    if not db_item:
        return None
    
    db_item.response_data = {
        "selected_options": answer_in.selected_options or [],
        "text_response": answer_in.text_response or "",
        "custom_data": answer_in.custom_data or {}
    }
    db_item.status = QueueItemStatus.RESOLVED
    db_item.resolved_at = datetime.utcnow()

    # If linked to a Task, update the task with user's choices
    if db_item.task_id:
        task = db.query(Task).filter(Task.id == db_item.task_id).first()
        if task:
            user_choices = []
            if answer_in.selected_options:
                user_choices.append(f"Выбранные опции: {', '.join(answer_in.selected_options)}")
            if answer_in.text_response:
                user_choices.append(f"Комментарий пользователя: {answer_in.text_response}")
            
            if user_choices:
                task.prompt = f"{task.prompt}\n\n[Решение пользователя]:\n" + "\n".join(user_choices)
            
            task.status = TaskStatus.PENDING  # Resume task for Executor agent

    db.commit()
    db.refresh(db_item)
    return db_item

def cancel_queue_item(db: Session, item_id: str, reason: str = "User cancelled") -> Optional[QueueItem]:
    db_item = get_queue_item(db, item_id)
    if not db_item:
        return None
    
    db_item.status = QueueItemStatus.CANCELLED
    db_item.resolved_at = datetime.utcnow()
    db_item.response_data = {"cancelled": True, "reason": reason}

    # If linked to a Task, cancel the task as well
    if db_item.task_id:
        task = db.query(Task).filter(Task.id == db_item.task_id).first()
        if task:
            task.status = TaskStatus.CANCELLED
            task.result_summary = f"Cancelled by user in queue: {reason}"

    db.commit()
    db.refresh(db_item)
    return db_item

# ==================== Task CRUD ====================

def get_tasks(db: Session, status: Optional[TaskStatus] = None, limit: int = 50) -> List[Task]:
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)
    return query.order_by(Task.created_at.desc()).limit(limit).all()

def get_task(db: Session, task_id: str) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()

def create_task(db: Session, task_in: TaskCreate) -> Task:
    title = task_in.title or (task_in.prompt[:40] + "..." if len(task_in.prompt) > 40 else task_in.prompt)
    db_task = Task(
        title=title,
        prompt=task_in.prompt,
        skills=task_in.skills,
        schedule_cron=task_in.schedule_cron,
        status=TaskStatus.PENDING
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: str, update_in: TaskUpdate) -> Optional[Task]:
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    if update_in.status is not None:
        db_task.status = update_in.status
    if update_in.result_summary is not None:
        db_task.result_summary = update_in.result_summary
    db_task.last_run_at = datetime.utcnow()
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: str) -> bool:
    db_task = get_task(db, task_id)
    if not db_task:
        return False
    db.delete(db_task)
    db.commit()
    return True

# ==================== Skill CRUD ====================

def get_all_skills(db: Session) -> List[Skill]:
    return db.query(Skill).all()

def get_skill(db: Session, skill_id: str) -> Optional[Skill]:
    return db.query(Skill).filter(Skill.id == skill_id).first()

def create_or_update_skill(db: Session, skill_in: SkillCreate) -> Skill:
    db_skill = get_skill(db, skill_in.id)
    if not db_skill:
        db_skill = Skill(
            id=skill_in.id,
            name=skill_in.name,
            display_name=skill_in.display_name,
            description=skill_in.description,
            icon=skill_in.icon,
            category=skill_in.category,
            parameters_schema=skill_in.parameters_schema
        )
        db.add(db_skill)
    else:
        db_skill.name = skill_in.name
        db_skill.display_name = skill_in.display_name
        db_skill.description = skill_in.description
        db_skill.icon = skill_in.icon
        db_skill.category = skill_in.category
        db_skill.parameters_schema = skill_in.parameters_schema
    
    db.commit()
    db.refresh(db_skill)
    return db_skill
