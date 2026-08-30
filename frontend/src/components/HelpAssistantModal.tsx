import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Copy, Check, Sparkles, Terminal, Clock, Bot, Code, Layers } from 'lucide-react';
import { triggerHaptic } from '../telegram';

interface HelpAssistantModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface CopyableItem {
  id: string;
  title: string;
  subtitle: string;
  category: string;
  icon: React.ReactNode;
  content: string;
}

const COPYABLE_ITEMS: CopyableItem[] = [
  {
    id: 'scheduled_prompt',
    title: 'Scheduled Task Prompt (1 Min Cron)',
    subtitle: 'Для Antigravity /schedule, cron-воркеров и периодических агентов',
    category: 'Prompts',
    icon: <Clock className="w-3.5 h-3.5 text-purple-400" />,
    content: `Ты — автономный исполнитель очереди AI Action Queue (локальный API: http://localhost:8000/api/v1).

Каждый цикл выполнения (каждую 1 минуту):
1. Запроси список готовых задач: GET http://localhost:8000/api/v1/tasks/pending
2. Если есть задачи:
   - Возьми первую задачу в работу, переведя статус в running: PATCH /api/v1/tasks/{id}/status с {"status": "running"}
   - Проанализируй текст задачи, кодовую базу и прикрепленные скиллы.
   - Если задача требует подтверждения, выбора архитектуры или ввода параметров:
     * Создай карточку в очереди: POST /api/v1/queue/ask с типами single_choice, multi_choice или text_input и привязкой task_id.
     * Переведи статус задачи в waiting_human.
   - Если задача автономная:
     * Выполни действия в репозитории, запусти тесты/линтеры.
     * Обнови статус задачи на completed с кратким отчетом в result_summary.
3. Проверь статус ранее заданных вопросов: GET /api/v1/queue/all
   - Если карточка переведена человеком в resolved — забери выбранные опции/комментарий из response_data, заверши исполнение связанной задачи и отметь её completed.
   - Если карточка переведена в cancelled — немедленно прекрати работу по этой ветке и отметь связанную задачу как cancelled.`,
  },
  {
    id: 'zenkit_prompt',
    title: 'Zenkit / Task Tracker Watcher Prompt',
    subtitle: 'Мониторинг внешних трекеров и отправка предложений решений в очередь',
    category: 'Prompts',
    icon: <Layers className="w-3.5 h-3.5 text-blue-400" />,
    content: `Ты — ассистент интеграции между Zenkit и моей локальной Action Queue.

Инструкция:
1. Проверь новые или отредактированные задачи в Zenkit, назначенные на меня.
2. Для каждой задачи проанализируй требования и кодовую базу текущего проекта.
3. Сформулируй 2-3 варианта технической реализации (например: "Быстрый фикс", "Полный рефакторинг", "Альтернативная библиотека").
4. Отправь предложение в мою очередь:
   POST http://localhost:8000/api/v1/queue/ask
   {
     "title": "Zenkit: [Название задачи]",
     "description": "Сводка требований и варианты решения в Markdown",
     "item_type": "single_choice",
     "options": [
       {"id": "opt1", "label": "Вариант 1: Быстрый патч"},
       {"id": "opt2", "label": "Вариант 2: Рефакторинг модуля"},
       {"id": "skip", "label": "Отложить задачу"}
     ],
     "source_agent": "zenkit_watcher"
   }
5. Как только я сделаю выбор на телефоне или нажму Cancel, подхвати результат и начни выполнение.`,
  },
  {
    id: 'grill_me_prompt',
    title: 'Interactive /grill-me UI & Feature Prompt',
    subtitle: 'Делегирование вопросов проектирования и UI в очередь вместо консоли',
    category: 'Prompts',
    icon: <Sparkles className="w-3.5 h-3.5 text-amber-400" />,
    content: `Улучши внешний вид и удобство использования приложения в текущей папке.

Правила взаимодействия:
- Вместо блокирующих вопросов в терминале, формулируй каждый выбор архитектуры или дизайна в виде карточки в локальной очереди:
  POST http://localhost:8000/api/v1/queue/ask
- Для выбора темы/структуры используй single_choice.
- Для набора подключаемых фич используй multi_choice.
- Для произвольных правок используй text_input.
- Опрашивай статус ответа через GET http://localhost:8000/api/v1/queue/{id}. Как только я выберу варианты на телефоне, применяй их в кодовой базе и переходи к следующему шагу.`,
  },
  {
    id: 'global_skill',
    title: 'Global AI Skill (human-action-queue/SKILL.md)',
    subtitle: 'Полная спецификация скилла для любого LLM / агента в любом проекте',
    category: 'Skills',
    icon: <Bot className="w-3.5 h-3.5 text-emerald-400" />,
    content: `---
name: human-action-queue
description: Universal Human-in-the-Loop Action Queue skill. Enables any AI agent, LLM harness, or background scheduled task from ANY project directory to delegate choices to the user, post proposals, ask clarifying questions, and monitor responses via the local Action Queue (Apple Liquid Glass Web / Telegram Mini App).
---

# Global AI Skill: Human-in-the-Loop Action Queue
API Base: http://localhost:8000/api/v1 (or LAN IP http://192.168.0.116:8000/api/v1)

Endpoints:
1. POST /api/v1/queue/ask -> Post question or proposal card (single_choice, multi_choice, text_input)
2. GET /api/v1/queue/{id} -> Check user decision (status == "resolved" or status == "cancelled")
3. GET /api/v1/tasks/pending -> Get tasks assigned to AI
4. PATCH /api/v1/tasks/{id}/status -> Update execution status (running, waiting_human, completed, cancelled)

Rules:
- When status == "cancelled", immediately abort the topic.
- Format descriptions in clean Markdown.`,
  },
  {
    id: 'python_snippet',
    title: 'Python Zero-Dependency Client',
    subtitle: 'Быстрый вызов очереди из Python без сторонних библиотек',
    category: 'Code',
    icon: <Code className="w-3.5 h-3.5 text-sky-400" />,
    content: `import json, urllib.request

def push_to_queue(title, description, options=None, item_type="single_choice"):
    payload = json.dumps({
        "title": title,
        "description": description,
        "item_type": item_type,
        "options": [{"id": str(i), "label": opt} for i, opt in enumerate(options or [])],
        "source_agent": "cross_project_agent"
    }).encode("utf-8")
    req = urllib.request.Request("http://localhost:8000/api/v1/queue/ask", data=payload, headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read().decode("utf-8"))`,
  },
  {
    id: 'docker_command',
    title: 'Docker Compose Start Command',
    subtitle: 'Команда запуска стека (PostgreSQL + FastAPI/React)',
    category: 'DevOps',
    icon: <Terminal className="w-3.5 h-3.5 text-zinc-400" />,
    content: `docker compose up -d --build`,
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
          className="w-full max-w-md liquid-glass rounded-t-3xl sm:rounded-3xl p-4 shadow-2xl flex flex-col gap-3 max-h-[88vh] overflow-y-auto safe-bottom"
        >
          {/* Sheet Handle */}
          <div className="w-9 h-1 bg-white/20 rounded-full mx-auto sm:hidden" />

          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h2 className="text-xs font-bold text-white tracking-tight">AI Setup Assistant</h2>
              <span className="text-[10px] text-zinc-500 font-mono">Prompts & Skills</span>
            </div>
            <button
              onClick={onClose}
              className="w-6 h-6 rounded-full bg-white/10 text-zinc-400 hover:text-white flex items-center justify-center transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Intro description */}
          <p className="text-[11px] text-zinc-400 leading-relaxed bg-white/[0.02] border border-white/[0.05] p-2.5 rounded-xl">
            Копируйте готовые промпты и спецификацию скилла в один клик для передачи в Antigravity, внешние LLM или фоновые шедулеры.
          </p>

          {/* List of compact copyable items */}
          <div className="flex flex-col gap-2">
            {COPYABLE_ITEMS.map((item) => {
              const isCopied = copiedId === item.id;
              return (
                <div
                  key={item.id}
                  className="bg-white/[0.03] border border-white/[0.06] hover:border-white/[0.12] rounded-2xl p-2.5 flex items-center justify-between gap-3 transition-colors"
                >
                  <div className="flex items-start gap-2.5 min-w-0">
                    <div className="p-2 rounded-xl bg-white/[0.04] border border-white/[0.06] mt-0.5 shrink-0">
                      {item.icon}
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-1.5">
                        <h4 className="text-xs font-semibold text-white truncate">{item.title}</h4>
                        <span className="text-[9px] px-1.5 py-0.2 rounded-full bg-white/10 text-zinc-400 font-medium shrink-0">
                          {item.category}
                        </span>
                      </div>
                      <p className="text-[10px] text-zinc-400 mt-0.5 truncate">{item.subtitle}</p>
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
