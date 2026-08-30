---
name: human-action-queue
description: Universal Human-in-the-Loop Action Queue skill. Enables any AI agent, LLM harness, or background scheduled task from ANY project directory to delegate choices to the user, post proposals, ask clarifying questions, and monitor responses via the local Action Queue (Apple Liquid Glass Web / Telegram Mini App).
---

# 🌐 Global AI Skill: Human-in-the-Loop Action Queue

Этот скилл позволяет любому AI-агенту, LLM или фоновому процессу, находясь **в любой папке любого проекта**, взаимодействовать с оператором (человеком) через локальную очередь **Action Queue**.

- **Локальный API адрес**: `http://localhost:8000/api/v1` (или `http://192.168.0.116:8000/api/v1` в локальной сети).
- **Интерфейс оператора**: веб-приложение на компьютере или Telegram Mini App на iPhone.

---

## 🛠 Протокол работы с очередью (REST API)

### 1. Задать вопрос / Отправить предложение человеку (`POST /queue/ask`)

Используйте этот эндпоинт, когда требуется одобрение, выбор между альтернативами или текстовые параметры от человека:

```http
POST http://localhost:8000/api/v1/queue/ask
Content-Type: application/json

{
  "title": "💡 Краткий и понятный заголовок вопроса",
  "description": "Подробное описание предложения в Markdown (контекст, diff, аргументы)",
  "item_type": "single_choice" | "multi_choice" | "text_input",
  "options": [
    {"id": "opt1", "label": "Вариант 1 (например, Рефакторинг через async)"},
    {"id": "opt2", "label": "Вариант 2 (например, Оставить синхронным)"}
  ],
  "task_id": "optional-linked-task-uuid",
  "priority": 1..5,
  "source_agent": "имя_вашего_агента_или_проекта"
}
```

#### Типы карточек (`item_type`):
1. **`single_choice`**: Одиночный выбор (быстрые кнопки-пилюли). Идеально для «Одобрить / Отклонить», выбора алгоритма или стратегии.
2. **`multi_choice`**: Множественный выбор (чекбоксы в виде чипов). Идеально для выбора набора опций: `[x] Создать бэкап`, `[x] Применить на стейджинге`, `[x] Уведомить команду`.
3. **`text_input`**: Поле свободного ввода. Для параметров, API-ключей, названий веток или развернутых указаний.

---

### 2. Проверить решение человека (`GET /queue/{id}`)

Агент опрашивает статус карточки:

```http
GET http://localhost:8000/api/v1/queue/{id}
```

#### Ответ при согласии/ответе человека (`status == "resolved"`):
```json
{
  "id": "uuid-string",
  "status": "resolved",
  "response_data": {
    "selected_options": ["opt1"],
    "text_response": "Комментарий пользователя..."
  }
}
```

#### Ответ при отмене (`status == "cancelled"`):
```json
{
  "id": "uuid-string",
  "status": "cancelled",
  "response_data": {
    "cancelled": true,
    "reason": "User cancelled from UI"
  }
}
```
> ⚠️ **Критическое правило для AI**: Если статус `cancelled`, агент **ОБЯЗАН немедленно прекратить работу над этой темой** и не задавать повторных или уточняющих вопросов.

---

### 3. Получить задачи, назначенные на AI (`GET /tasks/pending`)

Для фоновых воркеров и шедулеров:

```http
GET http://localhost:8000/api/v1/tasks/pending
```

Возвращает массив задач, созданных пользователем или разблокированных после ответа в очереди.

---

### 4. Обновить статус выполнения задачи (`PATCH /tasks/{id}/status`)

```http
PATCH http://localhost:8000/api/v1/tasks/{id}/status
Content-Type: application/json

{
  "status": "running" | "waiting_human" | "completed" | "cancelled" | "failed",
  "result_summary": "Отчет в Markdown о выполненных изменениях или причина ожидания"
}
```

---

## 🐍 Готовый встроенный Python-хелпер (Zero Dependencies)

Любой агент может выполнить этот короткий Python-сниппет для отправки вопроса в очередь без установки сторонних библиотек (использует только встроенный `urllib.request`):

```python
import json
import urllib.request

def ask_human_queue(title, description, item_type="single_choice", options=None, source="my_agent"):
    url = "http://localhost:8000/api/v1/queue/ask"
    payload = json.dumps({
        "title": title,
        "description": description,
        "item_type": item_type,
        "options": [{"id": f"opt_{i}", "label": opt} for i, opt in enumerate(options)] if options else [],
        "source_agent": source
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))

# Пример вызова:
# ask_human_queue(
#     title="Одобрение архитектурного решения",
#     description="Предлагается вынести слой аналитики в отдельный микросервис.",
#     item_type="single_choice",
#     options=["Одобрить", "Оставить в монолите", "Запросить оценку по времени"]
# )
```

---

## 📋 Шаблоны промптов (Prompt Recipes)

### Рецепт 1: Ежеминутный Scheduled Task в любом Harness (Antigravity / Cron / AutoGen)

Используйте этот промпт для настройки периодической задачи (интервал: 1 минута):

```markdown
Ты — автономный исполнитель очереди AI Action Queue (API: http://localhost:8000/api/v1).

Каждый цикл выполнения (каждую 1 минуту):
1. Запроси список готовых задач: `GET /api/v1/tasks/pending`.
2. Если задачи есть:
   - Переведи первую задачу в статус `running` через `PATCH /api/v1/tasks/{id}/status`.
   - Проанализируй текст задачи и прикрепленные скиллы.
   - Если для задачи требуется подтверждение, выбор архитектуры или деструктивное действие:
     * Опубликуй вопрос в очередь: `POST /api/v1/queue/ask` (single_choice / multi_choice) с привязкой `task_id`.
     * Установи статус задачи `waiting_human`.
   - Если задача автономная:
     * Выполни необходимые действия в текущем репозитории, запусти верификацию/тесты.
     * Установи статус задачи `completed` с markdown-отчетом в `result_summary`.
3. Запроси `GET /api/v1/queue/all`:
   - Если карточка была переведена человеком в `resolved` — забери выбранные им опции из `response_data`, заверши исполнение связанной задачи и отметь её `completed`.
   - Если карточка переведена в `cancelled` — немедленно закрой связанную задачу со статусом `cancelled`.
```

---

### Рецепт 2: Мониторинг задач Zenkit / Jira / GitHub из любого проекта

Промпт для агента, отслеживающего внешний таск-трекер:

```markdown
Ты — ассистент интеграции между Zenkit и нашей Action Queue.

Инструкция:
1. Подключись к Zenkit API и проверь задачи, назначенные на меня (или отредактированные за последние 24 часа).
2. Для каждой новой/обновленной задачи:
   - Проанализируй требования и кодовую базу текущего проекта.
   - Сформулируй 2-3 варианта технической реализации (например: быстрый фикс, полный рефакторинг, альтернативная библиотека).
   - Отправь предложение в очередь через `POST http://localhost:8000/api/v1/queue/ask`:
     * `title`: "Zenkit: [Название задачи]"
     * `description`: Сводка требований и ваше предлагаемое решение.
     * `item_type`: "single_choice"
     * `options`: список предложенных вариантов реализации + вариант "Отклонить".
     * `source_agent`: "zenkit_watcher"
3. После того как я сделаю выбор в мобильном приложении, подхвати задачу в работу.
```

---

### Рецепт 3: Интерактивный `/grill-me` для проработки фич и улучшения UI

Промпт при запуске задачи на проектирование или улучшение кодовой базы:

```markdown
Улучши внешний вид и производительность приложения в текущей папке.

Правила взаимодействия:
- Вместо блокирующих вопросов в терминале, формулируй каждый архитектурный или дизайнерский выбор в виде интерактивной карточки в локальной очереди:
  `POST http://localhost:8000/api/v1/queue/ask`
- Для выбора темы/компоновки используй `single_choice`.
- Для списка фич и оптимизаций используй `multi_choice`.
- Для ввода кастомных требований используй `text_input`.
- Проверяй статус ответа через `GET /api/v1/queue/{id}`. Как только я нажму кнопку на телефоне, применяй утвержденный вариант и переходи к следующему шагу.
```
