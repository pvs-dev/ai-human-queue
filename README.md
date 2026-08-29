# 🤖 AI Human-in-the-Loop Action Queue & Telegram Web App

Интерактивное веб-приложение на **Python (FastAPI)** и **React (TypeScript + Tailwind CSS)**, адаптированное для мобильных браузеров (PWA) и **Telegram Mini Apps (TWA)**. 

Система служит удобной очередью задач и решений, в которой:
- **AI-агенты** могут запрашивать у человека подтверждение, выбор вариантов или развернутые инструкции.
- **Человек** видит интерактивные карточки (Single Choice, Multi Choice, Text Input, Cancel) и дает ответы в один тап с телефона.
- При ответе или отмене (`Cancel`) карточка плавно исчезает, а AI мгновенно получает уведомление.
- Человек может создавать новые задачи и прикреплять к ним **скиллы/слэш-команды** (`/web-search`, `/code-analyzer`, `/db-query`, `/git-commit`, `/schedule-cron` и др.).
- В фоне работает периодический планировщик задач (каждую минуту или по расписанию), доступный для любого AI-движка.

---

## 📱 Возможности интерфейса

1. **Очередь решений (Decision Queue)**:
   - **Одиночный выбор (Single Choice)**: Карточки с выбором одной опции (Approve / Reject / etc.).
   - **Множественный выбор (Multi Choice)**: Чекбоксы в стиле чипов с кнопкой `Submit Decision`.
   - **Свободный ввод (Text Input)**: Поле для ввода параметров, API-ключей или инструкций.
   - **Кнопка Cancel на каждой карточке**: Закрывает тред, помечает задачу как отмененную (`cancelled`) и освобождает очередь.
   - **Тактильный отклик и анимации**: Поддержка Telegram Haptic Feedback и анимации свайпа/схлопывания карточек (Framer Motion).
2. **Создание задач со скиллами (Bottom Sheet Modal)**:
   - Интерактивный ввод промпта.
   - Панель прикрепления скиллов в виде тегов (`/web-search`, `/code-analyzer`, `/deploy`...).
   - Включение и настройка расписания (Cron expression: `*/1 * * * *`).
3. **Реестр скиллов и мониторинг воркера**:
   - Просмотр всех доступных AI-скиллов и их описаний.
   - Вкладка задач со статусами выполнения (`Running`, `Waiting Human`, `Completed`, `Cancelled`).
4. **Realtime-синхронизация (SSE)**:
   - Автоматическое обновление данных на клиенте при любых изменениях без необходимости обновлять страницу.

---

## 🚀 Быстрый старт

### 1. Запуск сервера (бэкенд + фронтенд)
Сервер автоматически отдаст собранный React интерфейс и REST API на порту `8000`:

```bash
# В корне проекта c:\work\queue:
.\.venv\Scripts\python run_server.py
```

Откройте в браузере: **`http://localhost:8000`**
Интерактивная документация Swagger API: **`http://localhost:8000/docs`**

---

### 2. Запуск в режиме разработки (Hot-Reload)

**Бэкенд:**
```bash
$env:PYTHONPATH="c:\work\queue\backend"
.\.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

**Фронтенд:**
```bash
cd frontend
npm run dev
```

---

### 3. Интеграция с Telegram Mini App (TWA)

1. Откройте `@BotFather` в Telegram и создайте нового бота или выберите существующего.
2. Отправьте команду `/newapp` или перейдите в `Bot Settings` -> `Menu Button` / `Mini App`.
3. Укажите URL вашего развернутого приложения (например, через ngrok / cloudflare tunnel: `https://your-domain.com`).
4. Приложение автоматически подстроит цветовую палитру Telegram (Dark/Light mode), раскроется на весь экран и включит виброотклик кнопок.

---

## 🤖 Подключение AI-агентов (Python SDK & REST API)

Любой AI агент (включая Antigravity, внешние LLM или bash-скрипты) может легко взаимодействовать с очередью.

### Пример на Python (`agent_sdk`):

```python
from agent_sdk.client import AIQueueClient

client = AIQueueClient("http://localhost:8000")

# 1. AI задает вопрос человеку
item = client.ask_human(
    title="Одобрить деплой новой версии?",
    description="Все тесты пройдены успешно. Запустить обновление прод-сервера?",
    item_type="single_choice",
    options=[
        {"id": "yes", "label": "Да, деплоить"},
        {"id": "no", "label": "Отложить до утра"}
    ],
    source_agent="antigravity"
)

# 2. AI проверяет pending задачи к исполнению
pending_tasks = client.get_pending_tasks()
for task in pending_tasks:
    print(task["title"], task["skills"])
```

### Запуск автономного фонового воркера:
```bash
.\.venv\Scripts\python worker_cli.py --interval 60
```

---

## 🧪 Запуск тестов

```bash
$env:PYTHONPATH="c:\work\queue\backend"
.\.venv\Scripts\pytest backend/tests/test_api.py -v
```
