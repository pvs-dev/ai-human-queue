---
name: human-queue
description: Universal Human-in-the-Loop Queue skill. Enables AI agents to ask clarifying questions, request approvals, and retrieve user-assigned tasks and decisions through the Action Queue web & Telegram interface.
---

# Human-in-the-Loop Queue AI Skill

This skill equips an AI agent with the ability to interact with the human operator via the **Human-in-the-Loop Action Queue**.
Instead of blocking execution in console or making assumptions, the AI can delegate decisions to the user, who responds from mobile, desktop, or Telegram Mini App.

---

## 🛠 API Endpoints & Capabilities

Base URL: `http://localhost:8000/api/v1` (or configured remote URL).

### 1. Ask a question or request a decision (`POST /queue/ask`)

When the AI needs human judgment (e.g., choosing an architecture, approving a migration, selecting between alternatives, or requesting sensitive parameters):

```http
POST /api/v1/queue/ask
Content-Type: application/json

{
  "title": "Short title of the decision",
  "description": "Markdown-formatted explanation, diff, or context",
  "item_type": "single_choice" | "multi_choice" | "text_input",
  "options": [
    {"id": "opt1", "label": "Approve changes"},
    {"id": "opt2", "label": "Reject"}
  ],
  "priority": 1..5,
  "source_agent": "antigravity_agent"
}
```

Response:
```json
{
  "id": "uuid-string",
  "status": "pending",
  "created_at": "..."
}
```

### 2. Check Decision Status (`GET /queue/{id}`)

The agent can poll or check if the human has answered or cancelled the item:

```http
GET /api/v1/queue/{id}
```

Response when answered:
```json
{
  "id": "uuid-string",
  "status": "resolved",
  "response_data": {
    "selected_options": ["opt1"],
    "text_response": "Additional user comment..."
  }
}
```

Response when cancelled by user:
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
> **Rule**: When `status == "cancelled"`, the AI MUST immediately stop working on this topic/thread without asking further questions.

### 3. Fetch User-Assigned Tasks (`GET /tasks/pending`)

If the agent runs on a scheduled cron (e.g. every minute), it queries pending tasks:

```http
GET /api/v1/tasks/pending
```

Returns list of tasks with user prompt, attached skills, and cron schedule.

### 4. Update Task Status (`PATCH /tasks/{id}/status`)

```http
PATCH /api/v1/tasks/{id}/status
Content-Type: application/json

{
  "status": "completed" | "failed" | "waiting_human",
  "result_summary": "Task output or summary"
}
```

---

## 🐍 Python SDK Quick Reference

Any script or agent tool can import `AIQueueClient`:

```python
from agent_sdk.client import AIQueueClient

client = AIQueueClient("http://localhost:8000")

# Ask human for multi-choice decision
item = client.ask_human(
    title="Select services to deploy",
    description="Target environment: Production",
    item_type="multi_choice",
    options=[
        {"id": "api", "label": "FastAPI Backend"},
        {"id": "web", "label": "React Frontend"},
        {"id": "db", "label": "PostgreSQL Migration"}
    ]
)

# Fetch user answer
details = client.get_queue_item(item["id"])
if details["status"] == "resolved":
    selected = details["response_data"]["selected_options"]
    print("User chose:", selected)
```
