"""
Dual-Agent Orchestrator
Launches both:
1. Auditor Subagent (Process 1 - Scans app, proposes improvements to queue)
2. Task Executor Worker (Process 2 - Monitors approved tasks, executes changes)
"""
import os
import sys
import time
import subprocess
import threading

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def run_process(cmd: list, label: str):
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    for line in iter(proc.stdout.readline, ''):
        print(f"[{label}] {line.strip()}")
    proc.stdout.close()
    proc.wait()

def main():
    python_exe = sys.executable
    auditor_script = os.path.join(os.path.dirname(__file__), "auditor_agent.py")
    executor_script = os.path.join(os.path.dirname(__file__), "executor_agent.py")

    print("==================================================================")
    print("🚀 Запуск двухпроцессной системы AI-агентов:")
    print("   1. [AUDITOR]  Аудитор кодовой базы / UX -> создает предложения в очередь")
    print("   2. [HUMAN]    Вы одобряете / выбираете варианты в Telegram или Web")
    print("   3. [EXECUTOR] Исполнитель подхватывает одобренные задачи и выполняет их")
    print("==================================================================")

    # Thread 1: Executor Worker (checks every 5s)
    t_executor = threading.Thread(
        target=run_process,
        args=([python_exe, executor_script, "--interval", "5"], "EXECUTOR"),
        daemon=True
    )

    # Thread 2: Auditor Worker (scans every 30s for demo/workflow)
    t_auditor = threading.Thread(
        target=run_process,
        args=([python_exe, auditor_script, "--interval", "30"], "AUDITOR"),
        daemon=True
    )

    t_executor.start()
    time.sleep(1)
    t_auditor.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Завершение работы процессов агентов...")

if __name__ == "__main__":
    main()
