"""
Auditor & UX Optimizer Subagent (Process 1)
Periodically inspects the application and codebase for:
- Performance & Query optimizations
- Mobile UI/UX improvements & usability issues
- Missing error handling or refactoring opportunities

When it finds an opportunity, it creates a Proposal Decision Card in the Queue
and pauses until the human reviews and approves/modifies/cancels it in Telegram/Web.
"""
import os
import sys
import time
import argparse
import random

# Ensure root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import requests
from agent_sdk.client import AIQueueClient

# Sample audit checks and proposals generator for real-world workflow simulation
AUDIT_CHECKS = [
    {
        "title": "Оптимизация рендеринга карточек очереди (Framer Motion memo)",
        "description": "Аудит показал лишние ререндеры при большом количестве элементов. Предлагается мемоизировать QueueCard через React.memo и вынести селекторы.",
        "skills": ["/code-analyzer", "/deploy"],
        "options": [
            {"id": "memoize_all", "label": "Применить React.memo к QueueCard и Header"},
            {"id": "virtual_list", "label": "Внедрить виртуализацию списка (@tanstack/virtual)"},
            {"id": "skip", "label": "Оставить как есть"}
        ]
    },
    {
        "title": "Кэширование API-запросов и индексы PostgreSQL",
        "description": "При частом опросе эндпоинта /queue/pending создается нагрузка на таблицу queue_items. Рекомендуется добавить составной индекс (status, priority, created_at).",
        "skills": ["/db-query", "/code-analyzer"],
        "options": [
            {"id": "add_index", "label": "Создать составной индекс в PostgreSQL"},
            {"id": "add_redis_cache", "label": "Включить in-memory кэширование на 3 сек"},
            {"id": "both", "label": "Применить индекс + кэширование"}
        ]
    },
    {
        "title": "Улучшение мобильного UX: Быстрые свайп-действия на iPhone",
        "description": "Для удобства работы одной рукой с телефона предлагается добавить свайп влево для отмены задачи и свайп вправо для быстрого одобрения.",
        "skills": ["/code-analyzer"],
        "options": [
            {"id": "add_swipes", "label": "Добавить жестовое управление свайпами"},
            {"id": "haptic_only", "label": "Усилить тактильный отклик Haptics"},
            {"id": "keep_buttons", "label": "Оставить только кнопки"}
        ]
    }
]

def run_codebase_inspection(client: AIQueueClient):
    """Inspects codebase and finds improvement items."""
    print(f"[{time.strftime('%H:%M:%S')}] 🔍 [AUDITOR] Сканирование кодовой базы и UX...")
    time.sleep(1)

    # Pick an audit finding that isn't already active in the queue
    pending_items = client.get_pending_queue()
    existing_titles = {item["title"] for item in pending_items}

    available_checks = [c for c in AUDIT_CHECKS if f"Предложение оптимизации: {c['title']}" not in existing_titles and c['title'] not in existing_titles]

    if not available_checks:
        print(f"[{time.strftime('%H:%M:%S')}] ✨ [AUDITOR] Все найденные предложения уже находятся в очереди или рассмотрены.")
        return

    # Select check
    check = random.choice(available_checks)
    print(f"[{time.strftime('%H:%M:%S')}] 💡 [AUDITOR] Найдена возможность улучшения: '{check['title']}'")

    # 1. Create a parent Task in 'waiting_human' status
    task_res = requests.post(
        f"{client.base_url}/api/v1/tasks",
        json={
            "title": f"Оптимизация: {check['title']}",
            "prompt": f"{check['description']}\nСкиллы: {', '.join(check['skills'])}",
            "skills": check["skills"],
        }
    )
    task_res.raise_for_status()
    task = task_res.json()

    # Update task to waiting_human
    client.update_task_status(task["id"], "waiting_human", "Ожидание решения пользователя в очереди.")

    # 2. Create the interactive decision QueueItem for the human
    queue_item = client.ask_human(
        title=f"💡 Предложение: {check['title']}",
        description=check["description"],
        item_type="multi_choice" if len(check["options"]) > 2 else "single_choice",
        options=check["options"],
        task_id=task["id"],
        priority=3,
        source_agent="auditor_subagent"
    )

    print(f"[{time.strftime('%H:%M:%S')}] 📤 [AUDITOR] Карточка решения отправлена в очередь (ID: {queue_item['id']}).")
    print(f"       -> Пользователь получил Push-уведомление в Telegram и может выбрать варианты с телефона.")

def main():
    parser = argparse.ArgumentParser(description="Auditor & UX Optimizer Subagent (Process 1)")
    parser.add_argument("--url", default="http://localhost:8000", help="Queue Backend URL")
    parser.add_argument("--interval", type=int, default=120, help="Audit interval in seconds (default: 120s)")
    parser.add_argument("--once", action="store_true", help="Run single audit and exit")
    args = parser.parse_args()

    client = AIQueueClient(base_url=args.url)
    print("==================================================")
    print(f"🔍 Auditor Subagent (Process 1) Running")
    print(f"📡 API: {args.url}")
    print(f"⏱️ Интервал аудита: {args.interval} сек")
    print("==================================================")

    while True:
        try:
            run_codebase_inspection(client)
        except Exception as e:
            print(f"⚠️ [AUDITOR ERROR]: {e}")

        if args.once:
            break
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
