---
name: dual-agent-workflow
description: Dual-Agent Architecture with Human-in-the-Loop Queue. Process 1 audits codebase and proposes optimizations to the queue; Human decides on mobile; Process 2 picks up approved tasks and executes them.
---

# 🤖🔄🤖 Dual-Agent Workflow: Auditor -> Human Decision -> Executor

Эта архитектура реализует разделение обязанностей между двумя независимыми AI-процессами через мобильную очередь решений:

```mermaid
flowchart LR
    subgraph Process1 ["Процесс 1: Auditor Subagent"]
        Audit[Анализ кодовой базы и UX]
        CreateProposal[Создание задачи и карточки решения]
        Audit --> CreateProposal
    end

    subgraph Queue ["Action Queue (Apple Liquid Glass UI)"]
        DecisionCard["💡 Карточка предложения\n- Single/Multi Choice\n- Cancel / Submit"]
    end

    subgraph HumanUser ["Человек (iPhone / Telegram)"]
        Human[Выбор вариантов или Отмена]
    end

    subgraph Process2 ["Процесс 2: Executor Worker"]
        Watch[Опрос одобренных задач]
        Exec[Применение изменений и тесты]
        Report[Отчет о выполнении]
        Watch --> Exec --> Report
    end

    CreateProposal -->|POST /queue/ask| DecisionCard
    DecisionCard <-->|Push & Tap| Human
    Human -->|POST /queue/{id}/answer| DecisionCard
    DecisionCard -->|Статус: pending| Watch
```

---

## ⚙️ Описание процессов

### 1. Процесс 1 — Аудитор (`scripts/auditor_agent.py`)
- Запускается по расписанию (например, каждые 2-5 минут).
- Исследует репозиторий, замеры производительности, структуру компонентов.
- Находит точку оптимизации и отправляет карточку предложения в очередь:
  - Пример: *«Оптимизация рендеринга карточек очереди (React.memo)»* с вариантами выбора `[Мемоизировать всё]`, `[Добавить виртуализацию]`, `[Пропустить]`.
- Создает связанную задачу со статусом `waiting_human`.

### 2. Человек — Принятие решения (Мобильный WebApp / Telegram)
- Вы получаете Push в Telegram, открываете приложение на iPhone.
- В стиле Apple Liquid Glass выбираете нужные опции или нажимаете `Cancel`.
- При нажатии `Submit Decision` карточка исчезает, а связанная задача переходит в статус `pending` с записанными вашими точными указаниями.

### 3. Процесс 2 — Исполнитель (`scripts/executor_agent.py`)
- Независимый фоновый воркер, опрашивающий эндпоинт `GET /api/v1/tasks/pending`.
- Как только задача одобрена человеком, Исполнитель:
  1. Забирает задачу и ставит статус `running`.
  2. Выполняет кодовые изменения / оптимизации с учетом выбранных вами опций.
  3. Прогоняет автоматические тесты.
  4. Записывает подробный отчет и переводит статус в `completed`.

---

## 🚀 Запуск двухпроцессной системы

### Быстрый запуск обоих процессов сразу:
```bash
# В папке c:\work\queue:
.\.venv\Scripts\python scripts/run_dual_agent_system.py
```

### Или запуск в двух отдельных терминалах:
**Терминал 1 (Исполнитель):**
```bash
.\.venv\Scripts\python scripts/executor_agent.py --interval 5
```

**Терминал 2 (Аудитор):**
```bash
.\.venv\Scripts\python scripts/auditor_agent.py --interval 60
```
