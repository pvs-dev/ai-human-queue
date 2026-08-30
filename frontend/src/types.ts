export type QueueItemType = 'single_choice' | 'multi_choice' | 'text_input' | 'confirmation';
export type QueueItemStatus = 'pending' | 'resolved' | 'cancelled' | 'expired';
export type TaskStatus = 'pending' | 'running' | 'waiting_human' | 'completed' | 'cancelled' | 'failed';

export interface QueueOption {
  id: string;
  label: string;
  description?: string;
}

export interface QueueItem {
  id: string;
  task_id?: string;
  title: string;
  description?: string;
  item_type: QueueItemType;
  options?: QueueOption[];
  response_data?: {
    selected_options?: string[];
    text_response?: string;
    cancelled?: boolean;
    reason?: string;
    [key: string]: any;
  };
  status: QueueItemStatus;
  priority: number;
  source_agent: string;
  created_at: string;
  resolved_at?: string;
}

export interface Task {
  id: string;
  title: string;
  prompt: string;
  skills: string[];
  schedule_cron?: string;
  status: TaskStatus;
  result_summary?: string;
  last_run_at?: string;
  next_run_at?: string;
  created_at: string;
}

export interface Skill {
  id: string;
  name: string;
  display_name: string;
  description: string;
  icon: string;
  category: string;
  parameters_schema?: Record<string, any>;
}

export interface AppSettings {
  telegram_bot_token: string;
  telegram_webapp_url: string;
  telegram_admin_chat_id: string;
  worker_interval_seconds: number;
  auditor_interval_seconds: number;
  auto_audit_enabled: boolean;
  custom_prompt_prefix: string;
}
