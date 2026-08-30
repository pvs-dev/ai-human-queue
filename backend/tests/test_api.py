import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.seeds import seed_skills

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_queue.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_skills(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_health_check():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_list_skills():
    res = client.get("/api/v1/skills")
    assert res.status_code == 200
    skills = res.json()
    assert len(skills) >= 5
    assert any(s["id"] == "/web-search" for s in skills)

def test_create_and_resolve_queue_item():
    # 1. AI creates a question
    ask_payload = {
        "title": "Выберите конфигурацию БД",
        "description": "Нужно выбрать тип репликации",
        "item_type": "single_choice",
        "options": [
            {"id": "async_rep", "label": "Async Replication"},
            {"id": "sync_rep", "label": "Sync Replication"}
        ],
        "priority": 2,
        "source_agent": "db_agent"
    }
    create_res = client.post("/api/v1/queue/ask", json=ask_payload)
    assert create_res.status_code == 201
    item = create_res.json()
    item_id = item["id"]
    assert item["status"] == "pending"

    # 2. Check pending queue
    pending_res = client.get("/api/v1/queue/pending")
    assert pending_res.status_code == 200
    pending_ids = [p["id"] for p in pending_res.json()]
    assert item_id in pending_ids

    # 3. User answers the question
    answer_payload = {
        "selected_options": ["async_rep"],
        "text_response": ""
    }
    ans_res = client.post(f"/api/v1/queue/{item_id}/answer", json=answer_payload)
    assert ans_res.status_code == 200
    assert ans_res.json()["status"] == "resolved"
    assert ans_res.json()["response_data"]["selected_options"] == ["async_rep"]

    # 4. Ensure it disappeared from pending
    pending_res2 = client.get("/api/v1/queue/pending")
    pending_ids2 = [p["id"] for p in pending_res2.json()]
    assert item_id not in pending_ids2

def test_cancel_queue_item():
    # AI asks a question
    ask_payload = {
        "title": "Уточните параметры деплоя",
        "description": "Тест отмены задачи",
        "item_type": "text_input",
        "priority": 1,
        "source_agent": "deploy_agent"
    }
    create_res = client.post("/api/v1/queue/ask", json=ask_payload)
    item_id = create_res.json()["id"]

    # User clicks Cancel
    cancel_res = client.post(f"/api/v1/queue/{item_id}/cancel", json={"reason": "Topic dropped"})
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"

    # Verify not in pending
    pending_res = client.get("/api/v1/queue/pending")
    assert item_id not in [p["id"] for p in pending_res.json()]

def test_create_task_with_skills():
    task_payload = {
        "title": "Сбор данных о рынке",
        "prompt": "Собрать сводку новостей за неделю",
        "skills": ["/web-search", "/schedule-cron"],
        "schedule_cron": "*/5 * * * *"
    }
    task_res = client.post("/api/v1/tasks", json=task_payload)
    assert task_res.status_code == 201
    task = task_res.json()
    assert "/web-search" in task["skills"]
    assert task["status"] == "pending"

def test_get_and_update_settings():
    # 1. Get default settings
    res = client.get("/api/v1/settings")
    assert res.status_code == 200
    settings = res.json()
    assert "telegram_bot_token" in settings
    assert "worker_interval_seconds" in settings

    # 2. Update settings via API
    update_payload = {
        "telegram_bot_token": "test_token_12345",
        "telegram_admin_chat_id": "999888777",
        "worker_interval_seconds": 45
    }
    put_res = client.put("/api/v1/settings", json=update_payload)
    assert put_res.status_code == 200
    updated = put_res.json()
    assert updated["telegram_bot_token"] == "test_token_12345"
    assert updated["telegram_admin_chat_id"] == "999888777"
    assert updated["worker_interval_seconds"] == 45

