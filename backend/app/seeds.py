from sqlalchemy.orm import Session
from app.models import Skill, QueueItem, QueueItemType, QueueItemStatus, Task, TaskStatus

def seed_skills(db: Session):
    skills_data = [
        {
            "id": "/web-search",
            "name": "/web-search",
            "display_name": "Web Search",
            "description": "Поиск актуальной информации в интернете, документации и сводок",
            "icon": "Globe",
            "category": "research"
        },
        {
            "id": "/code-analyzer",
            "name": "/code-analyzer",
            "display_name": "Code Analyzer",
            "description": "Анализ структуры репозитория, поиск багов и архитектурных проблем",
            "icon": "Code",
            "category": "development"
        },
        {
            "id": "/db-query",
            "name": "/db-query",
            "display_name": "DB Query",
            "description": "Генерация и валидация SQL-запросов и миграций базы данных",
            "icon": "Database",
            "category": "database"
        },
        {
            "id": "/git-commit",
            "name": "/git-commit",
            "display_name": "Git Commit",
            "description": "Автоматическое создание коммита с осмысленным описанием изменений",
            "icon": "GitBranch",
            "category": "vcs"
        },
        {
            "id": "/schedule-cron",
            "name": "/schedule-cron",
            "display_name": "Schedule Cron",
            "description": "Запуск задачи по периодическому расписанию (каждую минуту, час и т.д.)",
            "icon": "Clock",
            "category": "automation"
        },
        {
            "id": "/deploy",
            "name": "/deploy",
            "display_name": "Deploy",
            "description": "Сборка и деплой приложения на стейджинг или прод сервер",
            "icon": "Rocket",
            "category": "devops"
        }
    ]

    for s_data in skills_data:
        existing = db.query(Skill).filter(Skill.id == s_data["id"]).first()
        if not existing:
            skill = Skill(
                id=s_data["id"],
                name=s_data["name"],
                display_name=s_data["display_name"],
                description=s_data["description"],
                icon=s_data["icon"],
                category=s_data["category"]
            )
            db.add(skill)
    db.commit()

def seed_demo_items(db: Session):
    existing_items = db.query(QueueItem).count()
    if existing_items > 0:
        return  # already seeded

    # 1. Multi-choice item
    item1 = QueueItem(
        title="Стратегия миграции базы данных",
        description="AI воркер подготовил скрипты миграции для PostgreSQL. Выберите необходимые предварительные шаги перед запуском:",
        item_type=QueueItemType.MULTI_CHOICE,
        options=[
            {"id": "staging", "label": "Применить сначала на Staging окружении"},
            {"id": "backup", "label": "Создать полный бэкап БД перед стартом"},
            {"id": "notify", "label": "Уведомить команду в Telegram канале"},
            {"id": "vacuum", "label": "Выполнить VACUUM ANALYZE после миграции"}
        ],
        priority=3,
        source_agent="antigravity_agent",
        status=QueueItemStatus.PENDING
    )

    # 2. Single-choice item
    item2 = QueueItem(
        title="Подтверждение рефакторинга модуля auth.py",
        description="Обнаружены устаревшие методы валидации JWT-токенов. Требуется ли переход на асинхронную сессию?",
        item_type=QueueItemType.SINGLE_CHOICE,
        options=[
            {"id": "approve", "label": "Одобрить переход на async"},
            {"id": "keep_sync", "label": "Оставить синхронным"},
            {"id": "need_details", "label": "Показать diff перед решением"}
        ],
        priority=2,
        source_agent="code_reviewer",
        status=QueueItemStatus.PENDING
    )

    # 3. Text input item
    item3 = QueueItem(
        title="Укажите ключ API или параметры окружения",
        description="Для выполнения скилла /web-search требуется указать параметр PROXY_URL или нажать Cancel, если поиск не нужен.",
        item_type=QueueItemType.TEXT_INPUT,
        options=[],
        priority=1,
        source_agent="research_worker",
        status=QueueItemStatus.PENDING
    )

    db.add_all([item1, item2, item3])

    # Sample Task
    demo_task = Task(
        title="Мониторинг обновлений зависимостей",
        prompt="Ежеминутная проверка актуальности версий библиотек и генерация отчета в очередь при наличии критических патчей.",
        skills=["/schedule-cron", "/code-analyzer"],
        schedule_cron="*/1 * * * *",
        status=TaskStatus.RUNNING,
        result_summary="Воркер активен, проверяет репозиторий каждые 60 секунд."
    )
    db.add(demo_task)
    db.commit()
