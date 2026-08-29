# 🤖 AI Human-in-the-Loop Action Queue & Telegram Web App

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/pvs-dev/ai-human-queue)

Интерактивное веб-приложение на **Python (FastAPI)**, **PostgreSQL** и **React (TypeScript + Tailwind CSS)** в стиле **Apple Liquid Glass (iOS 18)**, адаптированное для мобильных устройств (PWA), десктопа и **Telegram Mini Apps (TWA)**.

Репозиторий проекта: **[https://github.com/pvs-dev/ai-human-queue](https://github.com/pvs-dev/ai-human-queue)**

---

## 📱 Возможности и Архитектура

1. **Дизайн Apple Liquid Glass**:
   - Минималистичный интерфейс, чистый черный фон `#000000`, полупрозрачные карточки из матового стекла (`backdrop-blur`), системные шрифты Apple SF Pro.
   - Высокая плотность информации без лишних громоздких элементов.
   - Компактный Apple Segmented Control (`Queue`, `Tasks`, `Skills`).
   - Кнопка `Cancel Task` на каждой карточке — закрывает тему треда и освобождает очередь.
2. **PostgreSQL & База данных**:
   - Полная поддержка PostgreSQL через SQLAlchemy и `psycopg2`.
   - Автоматические миграции и создание таблиц при старте.
3. **Telegram Bot & Push Notifications**:
   - Автоматическая отправка уведомления в Telegram при появлении нового вопроса от AI с инлайн-кнопкой для мгновенного открытия Mini App на iPhone.
4. **Чистая шина для AI (AI-First Skill)**:
   - Бэкенд не вызывает сторонние LLM напрямую, выступая исключительно шиной очереди.
   - Внешние AI-агенты (Antigravity, Claude, OpenAI и др.) подключают готовый скилл `skills/human-queue/SKILL.md`.
5. **Docker & Docker Compose**:
   - Полная контейнеризация бэкенда, фронтенда и базы данных PostgreSQL в один клик.

---

## 🐳 Запуск через Docker Compose (Рекомендуемый способ)

```bash
# 1. Склонируйте репозиторий (если запускаете на новом сервере):
git clone https://github.com/pvs-dev/ai-human-queue.git
cd ai-human-queue

# 2. Создайте файл настроек окружения:
cp .env.example .env

# 3. Запустите стек (PostgreSQL + FastAPI/React):
docker compose up -d --build
```

- 🌐 Веб-интерфейс (Apple Liquid Glass): **`http://localhost:8000`**
- 📚 Документация REST API (Swagger): **`http://localhost:8000/docs`**
- 🐘 PostgreSQL порт: **`5432`**

---

## 💻 Локальный запуск без Docker

### 1. Установка зависимостей
```bash
# Python виртуальное окружение:
python -m venv .venv
.\.venv\Scripts\pip install -r backend/requirements.txt

# Сборка фронтенда:
cd frontend
npm install
npm run build
cd ..
```

### 2. Запуск сервера
```bash
.\.venv\Scripts\python run_server.py
```

### 3. Запуск тестов
```bash
$env:PYTHONPATH="backend"
.\.venv\Scripts\pytest backend/tests/test_api.py -v
```

---

## 🤖 Подключение AI-агентов (AI Skill)

Инструкции и спецификация инструментов для AI-агентов находятся в файле:
👉 **[`skills/human-queue/SKILL.md`](file:///c:/work/queue/skills/human-queue/SKILL.md)**

```python
from agent_sdk.client import AIQueueClient

client = AIQueueClient("http://localhost:8000")

# AI запрашивает решение у человека
item = client.ask_human(
    title="Одобрить деплой в продакшн?",
    description="Все тесты пройдены. Запустить миграции?",
    item_type="single_choice",
    options=[
        {"id": "yes", "label": "Одобрить"},
        {"id": "no", "label": "Отклонить"}
    ],
    source_agent="antigravity"
)
```
