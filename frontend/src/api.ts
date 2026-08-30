import type { QueueItem, Task, Skill, AppSettings } from './types';

const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1';

export const fetchPendingQueue = async (): Promise<QueueItem[]> => {
  const res = await fetch(`${API_BASE}/queue/pending`);
  if (!res.ok) throw new Error('Failed to fetch pending queue');
  return res.json();
};

export const fetchAllQueue = async (): Promise<QueueItem[]> => {
  const res = await fetch(`${API_BASE}/queue/all`);
  if (!res.ok) throw new Error('Failed to fetch all queue items');
  return res.json();
};

export const answerQueueItem = async (
  itemId: string,
  answer: { selected_options?: string[]; text_response?: string; custom_data?: any }
): Promise<QueueItem> => {
  const res = await fetch(`${API_BASE}/queue/${itemId}/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(answer),
  });
  if (!res.ok) throw new Error('Failed to submit answer');
  return res.json();
};

export const cancelQueueItem = async (
  itemId: string,
  reason: string = 'User cancelled from UI'
): Promise<QueueItem> => {
  const res = await fetch(`${API_BASE}/queue/${itemId}/cancel`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reason }),
  });
  if (!res.ok) throw new Error('Failed to cancel queue item');
  return res.json();
};

export const fetchTasks = async (): Promise<Task[]> => {
  const res = await fetch(`${API_BASE}/tasks`);
  if (!res.ok) throw new Error('Failed to fetch tasks');
  return res.json();
};

export const createTask = async (task: {
  title?: string;
  prompt: string;
  skills: string[];
  schedule_cron?: string;
}): Promise<Task> => {
  const res = await fetch(`${API_BASE}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(task),
  });
  if (!res.ok) throw new Error('Failed to create task');
  return res.json();
};

export const deleteTask = async (taskId: string): Promise<void> => {
  const res = await fetch(`${API_BASE}/tasks/${taskId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete task');
};

export const fetchSkills = async (): Promise<Skill[]> => {
  const res = await fetch(`${API_BASE}/skills`);
  if (!res.ok) throw new Error('Failed to fetch skills');
  return res.json();
};

export const fetchSettings = async (): Promise<AppSettings> => {
  const res = await fetch(`${API_BASE}/settings`);
  if (!res.ok) throw new Error('Failed to fetch settings');
  return res.json();
};

export const updateSettings = async (settings: Partial<AppSettings>): Promise<AppSettings> => {
  const res = await fetch(`${API_BASE}/settings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  if (!res.ok) throw new Error('Failed to update settings');
  return res.json();
};

export const testTelegramPush = async (): Promise<{ ok: boolean; message: string }> => {
  const res = await fetch(`${API_BASE}/settings/test-telegram`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to send test push' }));
    throw new Error(err.detail || 'Failed to send test push');
  }
  return res.json();
};

export const subscribeToEvents = (onEvent: (event: string, data: any) => void) => {
  const eventSource = new EventSource(`${API_BASE}/events/stream`);

  eventSource.onmessage = (e) => {
    try {
      const parsed = JSON.parse(e.data);
      if (parsed.event && parsed.data) {
        onEvent(parsed.event, parsed.data);
      }
    } catch {
      // heartbeats or simple strings
    }
  };

  eventSource.onerror = () => {
    // Attempt reconnect automatically handled by browser EventSource
  };

  return () => {
    eventSource.close();
  };
};
