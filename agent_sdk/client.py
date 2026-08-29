"""
AI Queue Agent SDK
Lightweight client for AI agents (Antigravity, LangChain, AutoGen, custom cron scripts)
to interact with the Human-in-the-Loop Queue.
"""
from typing import List, Optional, Dict, Any
import requests

class AIQueueClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    # ================= Queue Methods (Human-in-the-Loop) =================

    def ask_human(
        self,
        title: str,
        description: Optional[str] = None,
        item_type: str = "single_choice",  # "single_choice", "multi_choice", "text_input", "confirmation"
        options: Optional[List[Dict[str, str]]] = None,  # [{"id": "opt1", "label": "Approve"}]
        task_id: Optional[str] = None,
        priority: int = 1,
        source_agent: str = "ai_worker"
    ) -> Dict[str, Any]:
        """Post a question to the human queue and wait/return the created item."""
        url = f"{self.base_url}/api/v1/queue/ask"
        payload = {
            "title": title,
            "description": description,
            "item_type": item_type,
            "options": options or [],
            "task_id": task_id,
            "priority": priority,
            "source_agent": source_agent
        }
        res = requests.post(url, json=payload)
        res.raise_for_status()
        return res.json()

    def get_pending_queue(self) -> List[Dict[str, Any]]:
        """Get all unanswered questions waiting for human decision."""
        url = f"{self.base_url}/api/v1/queue/pending"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()

    def get_queue_item(self, item_id: str) -> Dict[str, Any]:
        """Get details of a specific queue item including resolution status and answer."""
        url = f"{self.base_url}/api/v1/queue/{item_id}"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()

    # ================= Task Methods =================

    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get tasks created by the user that need execution."""
        url = f"{self.base_url}/api/v1/tasks/pending"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()

    def update_task_status(self, task_id: str, status: str, result_summary: Optional[str] = None) -> Dict[str, Any]:
        """Update task status (e.g. 'running', 'completed', 'failed')."""
        url = f"{self.base_url}/api/v1/tasks/{task_id}/status"
        payload = {"status": status, "result_summary": result_summary}
        res = requests.patch(url, json=payload)
        res.raise_for_status()
        return res.json()

    # ================= Skills Registry =================

    def get_skills(self) -> List[Dict[str, Any]]:
        """Get list of registered skills and tools."""
        url = f"{self.base_url}/api/v1/skills"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
