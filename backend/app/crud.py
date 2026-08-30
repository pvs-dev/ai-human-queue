from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import QueueItem, QueueItemStatus, QueueItemType, Task, TaskStatus, Skill, SystemSetting
from app.schemas import QueueItemCreate, QueueItemAnswer, TaskCreate, TaskUpdate, SkillCreate, AppSettings, SettingsUpdate
from app.config import settings as env_settings

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

# ==================== Settings CRUD ====================

def get_setting_value(db: Session, key: str, default: str = "") -> str:
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if setting and setting.value is not None:
        return setting.value
    return default

def set_setting_value(db: Session, key: str, value: str):
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not setting:
        setting = SystemSetting(key=key, value=value)
        db.add(setting)
    else:
        setting.value = value
        setting.updated_at = datetime.utcnow()
    db.commit()

def get_app_settings(db: Session) -> AppSettings:
    """Retrieve full app settings merging DB values with environment defaults."""
    token = get_setting_value(db, "telegram_bot_token", env_settings.TELEGRAM_BOT_TOKEN)
    url = get_setting_value(db, "telegram_webapp_url", env_settings.TELEGRAM_WEBAPP_URL)
    chat_id = get_setting_value(db, "telegram_admin_chat_id", env_settings.TELEGRAM_ADMIN_CHAT_ID)
    
    worker_int_raw = get_setting_value(db, "worker_interval_seconds", str(env_settings.WORKER_INTERVAL_SECONDS))
    auditor_int_raw = get_setting_value(db, "auditor_interval_seconds", "120")
    auto_audit_raw = get_setting_value(db, "auto_audit_enabled", "true")
    prefix = get_setting_value(db, "custom_prompt_prefix", "")

    return AppSettings(
        telegram_bot_token=token,
        telegram_webapp_url=url,
        telegram_admin_chat_id=chat_id,
        worker_interval_seconds=int(worker_int_raw) if worker_int_raw.isdigit() else 60,
        auditor_interval_seconds=int(auditor_int_raw) if auditor_int_raw.isdigit() else 120,
        auto_audit_enabled=auto_audit_raw.lower() in ("true", "1", "yes"),
        custom_prompt_prefix=prefix
    )

def update_app_settings(db: Session, update_in: SettingsUpdate) -> AppSettings:
    """Update settings in database."""
    if update_in.telegram_bot_token is not None:
        set_setting_value(db, "telegram_bot_token", update_in.telegram_bot_token)
    if update_in.telegram_webapp_url is not None:
        set_setting_value(db, "telegram_webapp_url", update_in.telegram_webapp_url)
    if update_in.telegram_admin_chat_id is not None:
        set_setting_value(db, "telegram_admin_chat_id", update_in.telegram_admin_chat_id)
    if update_in.worker_interval_seconds is not None:
        set_setting_value(db, "worker_interval_seconds", str(update_in.worker_interval_seconds))
    if update_in.auditor_interval_seconds is not None:
        set_setting_value(db, "auditor_interval_seconds", str(update_in.auditor_interval_seconds))
    if update_in.auto_audit_enabled is not None:
        set_setting_value(db, "auto_audit_enabled", "true" if update_in.auto_audit_enabled else "false")
    if update_in.custom_prompt_prefix is not None:
        set_setting_value(db, "custom_prompt_prefix", update_in.custom_prompt_prefix)

    return get_app_settings(db)
