import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.models import Task, TaskStatus, QueueItem, QueueItemType, QueueItemStatus
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scheduler")

def process_scheduled_tasks():
    """Background job executed periodically (e.g. every minute) to check and process tasks."""
    db = SessionLocal()
    try:
        pending_tasks = db.query(Task).filter(
            Task.status.in_([TaskStatus.PENDING, TaskStatus.RUNNING])
        ).all()

        for task in pending_tasks:
            # If task has a cron schedule or pending execution
            now = datetime.utcnow()
            task.last_run_at = now
            
            # Example logic: if task has skills and is still pending, process it
            if task.status == TaskStatus.PENDING:
                logger.info(f"Processing Task '{task.title}' with skills {task.skills}")
                
                # Check if task requests human approval or action
                # If task includes /deploy or /db-query, create human confirmation queue item if none exists
                if any(s in task.skills for s in ["/deploy", "/db-query", "/code-analyzer"]):
                    existing_queue = db.query(QueueItem).filter(
                        QueueItem.task_id == task.id,
                        QueueItem.status == QueueItemStatus.PENDING
                    ).first()

                    if not existing_queue:
                        item = QueueItem(
                            task_id=task.id,
                            title=f"Требуется согласование: {task.title}",
                            description=f"AI планирует выполнить задачу: {task.prompt}\nСкиллы: {', '.join(task.skills)}",
                            item_type=QueueItemType.SINGLE_CHOICE,
                            options=[
                                {"id": "proceed", "label": "Запустить выполнение"},
                                {"id": "modify", "label": "Изменить параметры"}
                            ],
                            priority=2,
                            source_agent="cron_worker",
                            status=QueueItemStatus.PENDING
                        )
                        db.add(item)
                        task.status = TaskStatus.WAITING_HUMAN
                        task.result_summary = "Ожидание подтверждения от пользователя в очереди."
                        db.commit()
                        logger.info(f"Created QueueItem for Task {task.id}")
                else:
                    # Autonomous task execution simulation
                    task.status = TaskStatus.COMPLETED
                    task.result_summary = f"Успешно выполнено в {now.strftime('%H:%M:%S')} с использованием {', '.join(task.skills) if task.skills else 'автономного AI'}"
                    db.commit()
                    logger.info(f"Completed Task {task.id}")
    except Exception as e:
        logger.error(f"Error in scheduler job: {e}")
    finally:
        db.close()

scheduler = BackgroundScheduler()

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            process_scheduled_tasks,
            'interval',
            seconds=settings.WORKER_INTERVAL_SECONDS,
            id='task_checker_job',
            replace_existing=True
        )
        scheduler.start()
        logger.info(f"Scheduler started with interval {settings.WORKER_INTERVAL_SECONDS}s")

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
