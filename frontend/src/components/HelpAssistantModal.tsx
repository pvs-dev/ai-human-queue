import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Copy, Check, Clock, Bot } from 'lucide-react';
import { triggerHaptic } from '../telegram';

interface HelpAssistantModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface CopyableItem {
  id: string;
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  content: string;
}

const COPYABLE_ITEMS: CopyableItem[] = [
  {
    id: 'scheduled_prompt',
    title: 'Промпт для расписания (Scheduled Task Prompt)',
    subtitle: 'Промпт для шедулера (раз в минуту): опрос задач, вопросы в очередь, исполнение решений',
    icon: <Clock className="w-4 h-4 text-purple-400" />,
    content: `Ты — автономный исполнитель очереди AI Action Queue (локальный API: http://localhost:8000/api/v1).

Каждый цикл выполнения (раз в минуту):
1. Запроси задачи, готовые к выполнению:
   GET http://localhost:8000/api/v1/tasks/pending
2. Для каждой задачи:
   - Установи статус running: PATCH /api/v1/tasks/{id}/status с {"status": "running"}.
   - Если для задачи требуется подтверждение, выбор параметров или решение человека:
     * Опубликуй вопрос в очередь: POST /api/v1/queue/ask (single_choice, multi_choice или text_input) с linked task_id.
     * Установи статус waiting_human.
   - Если задача автономная — выполни действия в кодовой базе и отметь completed с отчетом.
3. Проверь ответы пользователя по ранее заданным вопросам:
   GET http://localhost:8000/api/v1/queue/all
   - Если статус resolved — используй выбор пользователя из response_data, заверши задачу и отметь completed.
   - Если статус cancelled — немедленно прекрати работу по этой ветке и отметь задачу cancelled.`,
  },
  {
    id: 'global_skill',
    title: 'Скилл для любой агентской системы (SKILL.md)',
    subtitle: 'Спецификация для подключения любого агента/LLM из любой папки к Action Queue',
    icon: <Bot className="w-4 h-4 text-emerald-400" />,
    content: `---
name: human-action-queue
description: Universal Human-in-the-Loop Action Queue skill. Allows any AI agent from any project folder to delegate choices to the human operator, post questions/proposals, and poll responses via the local Action Queue.
---

# Human-in-the-Loop Action Queue Skill

API Base URL: http://localhost:8000/api/v1

## 1. Post a Question / Decision to Human
POST /api/v1/queue/ask
Content-Type: application/json

{
  "title": "Short title",
  "description": "Context or proposal in Markdown",
  "item_type": "single_choice" | "multi_choice" | "text_input",
  "options": [{"id": "opt1", "label": "Option 1"}, {"id": "opt2", "label": "Option 2"}],
  "task_id": "optional-task-uuid",
  "source_agent": "agent_name"
}

## 2. Check Human Decision / Answer
GET /api/v1/queue/{id}
- If status == "resolved": user response is in response_data (selected_options / text_response). Proceed with execution.
- If status == "cancelled": human aborted this task. Immediately terminate this thread without follow-up questions.

## 3. Fetch Assigned Tasks
GET /api/v1/tasks/pending

## 4. Update Task Status & Report
PATCH /api/v1/tasks/{id}/status
Content-Type: application/json

{
  "status": "running" | "waiting_human" | "completed" | "cancelled" | "failed",
  "result_summary": "Markdown execution summary"
}`,
  },
];

export const HelpAssistantModal: React.FC<HelpAssistantModalProps> = ({ isOpen, onClose }) => {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleCopy = (item: CopyableItem) => {
    navigator.clipboard.writeText(item.content);
    setCopiedId(item.id);
    triggerHaptic('light');
    setTimeout(() => {
      setCopiedId(null);
    }, 2000);
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/75 backdrop-blur-md p-0 sm:p-4">
        <motion.div
          initial={{ opacity: 0, y: 80 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 80 }}
          transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
          className="w-full max-w-md liquid-glass rounded-t-3xl sm:rounded-3xl p-4 shadow-2xl flex flex-col gap-3 max-h-[85vh] overflow-y-auto safe-bottom"
        >
          {/* Sheet Handle */}
          <div className="w-9 h-1 bg-white/20 rounded-full mx-auto sm:hidden" />

          {/* Header */}
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold text-white tracking-tight">AI Setup Assistant</h2>
            <button
              onClick={onClose}
              className="w-6 h-6 rounded-full bg-white/10 text-zinc-400 hover:text-white flex items-center justify-center transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          <p className="text-[11px] text-zinc-400 leading-relaxed bg-white/[0.02] border border-white/[0.05] p-2.5 rounded-xl">
            Нажмите кнопку для копирования нужного текста и вставьте его в настройки агента:
          </p>

          {/* Clean 2 items list */}
          <div className="flex flex-col gap-2.5">
            {COPYABLE_ITEMS.map((item) => {
              const isCopied = copiedId === item.id;
              return (
                <div
                  key={item.id}
                  className="bg-white/[0.03] border border-white/[0.06] hover:border-white/[0.12] rounded-2xl p-3 flex items-center justify-between gap-3 transition-colors"
                >
                  <div className="flex items-start gap-2.5 min-w-0">
                    <div className="p-2 rounded-xl bg-white/[0.04] border border-white/[0.06] mt-0.5 shrink-0">
                      {item.icon}
                    </div>
                    <div className="min-w-0">
                      <h4 className="text-xs font-semibold text-white leading-snug">{item.title}</h4>
                      <p className="text-[10px] text-zinc-400 mt-0.5 leading-relaxed">{item.subtitle}</p>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleCopy(item)}
                    className={`px-2.5 py-1.5 rounded-xl text-[11px] font-medium transition-all shrink-0 flex items-center gap-1 border ${
                      isCopied
                        ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
                        : 'bg-white/[0.06] hover:bg-white/[0.12] border-white/[0.08] text-zinc-200 active:scale-95'
                    }`}
                  >
                    {isCopied ? (
                      <>
                        <Check className="w-3 h-3 text-emerald-400 stroke-[3]" />
                        <span className="text-[10px]">Скопировано</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        <span className="text-[10px]">Копировать</span>
                      </>
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
