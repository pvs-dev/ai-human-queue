"""
AI Background Worker CLI
A standalone daemon that periodically checks the queue, executes scheduled tasks,
and posts decisions/questions to the human.
"""
import sys
import time
import argparse
from agent_sdk.client import AIQueueClient

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main():
    parser = argparse.ArgumentParser(description="AI Queue Background Worker")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the queue backend")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds (default: 60)")
    parser.add_argument("--once", action="store_true", help="Run a single check and exit")
    args = parser.parse_args()

    client = AIQueueClient(base_url=args.url)
    print(f"[*] AI Worker connected to {args.url} (polling every {args.interval}s)")

    while True:
        try:
            # 1. Fetch pending human questions
            pending_queue = client.get_pending_queue()
            print(f"[{time.strftime('%H:%M:%S')}] Pending human decisions: {len(pending_queue)}")

            # 2. Fetch pending tasks created by user
            pending_tasks = client.get_pending_tasks()
            print(f"[{time.strftime('%H:%M:%S')}] Pending executable tasks: {len(pending_tasks)}")

            for task in pending_tasks:
                task_id = task["id"]
                title = task["title"]
                skills = task.get("skills", [])
                print(f"  -> Processing task '{title}' with skills: {skills}")

                # If task requires human confirmation
                if any(s in skills for s in ["/deploy", "/db-query"]):
                    print(f"  -> Posting confirmation question to human queue...")
                    client.ask_human(
                        title=f"Требуется согласование: {title}",
                        description=f"AI готов запустить процедуру со скиллами: {', '.join(skills)}",
                        item_type="single_choice",
                        options=[
                            {"id": "approve", "label": "Одобрить выполнение"},
                            {"id": "reject", "label": "Отклонить"}
                        ],
                        task_id=task_id,
                        source_agent="worker_cli"
                    )
                    client.update_task_status(task_id, "waiting_human", "Ожидает согласования в очереди решений.")
                else:
                    # Autonomous completion
                    time.sleep(1)
                    client.update_task_status(
                        task_id,
                        "completed",
                        f"Успешно обработано воркером в {time.strftime('%H:%M:%S')}"
                    )
                    print(f"  -> Task '{title}' completed.")

        except Exception as e:
            print(f"[!] Error during poll cycle: {e}")

        if args.once:
            break
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
