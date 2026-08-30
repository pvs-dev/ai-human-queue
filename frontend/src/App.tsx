import { useState, useEffect, useCallback } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Header } from './components/Header';
import { QueueCard } from './components/QueueCard';
import { NewTaskModal } from './components/NewTaskModal';
import { SettingsModal } from './components/SettingsModal';
import { TasksList } from './components/TasksList';
import { SkillsRegistry } from './components/SkillsRegistry';
import {
  fetchPendingQueue,
  answerQueueItem,
  cancelQueueItem,
  fetchTasks,
  createTask,
  deleteTask,
  fetchSkills,
  subscribeToEvents,
} from './api';
import type { QueueItem, Task, Skill } from './types';
import { initTelegramWebApp } from './telegram';
import { Check } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<'queue' | 'tasks' | 'skills'>('queue');
  const [queueItems, setQueueItems] = useState<QueueItem[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  // Initialize Telegram Web App SDK
  useEffect(() => {
    initTelegramWebApp();
  }, []);

  // Fetch initial data
  const loadData = useCallback(async () => {
    try {
      const [pending, allTasks, allSkills] = await Promise.all([
        fetchPendingQueue(),
        fetchTasks(),
        fetchSkills(),
      ]);
      setQueueItems(pending);
      setTasks(allTasks);
      setSkills(allSkills);
    } catch (err) {
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();

    // Subscribe to SSE updates
    const unsubscribe = subscribeToEvents((event, data) => {
      console.log('Realtime Event Received:', event, data);
      loadData();
    });

    return () => {
      unsubscribe();
    };
  }, [loadData]);

  // Handle human answer on a queue card
  const handleAnswer = async (
    itemId: string,
    data: { selected_options?: string[]; text_response?: string }
  ) => {
    // Optimistic UI update: immediately remove card from state
    setQueueItems((prev) => prev.filter((item) => item.id !== itemId));
    try {
      await answerQueueItem(itemId, data);
      fetchTasks().then(setTasks);
    } catch (err) {
      console.error('Failed to submit answer:', err);
      loadData();
    }
  };

  // Handle human cancel on a queue card
  const handleCancel = async (itemId: string) => {
    // Optimistic UI update
    setQueueItems((prev) => prev.filter((item) => item.id !== itemId));
    try {
      await cancelQueueItem(itemId);
      fetchTasks().then(setTasks);
    } catch (err) {
      console.error('Failed to cancel item:', err);
      loadData();
    }
  };

  // Create new task
  const handleCreateTask = async (taskData: {
    title?: string;
    prompt: string;
    skills: string[];
    schedule_cron?: string;
  }) => {
    try {
      await createTask(taskData);
      const updatedTasks = await fetchTasks();
      setTasks(updatedTasks);
      setActiveTab('tasks');
    } catch (err) {
      console.error('Failed to create task:', err);
    }
  };

  // Delete task
  const handleDeleteTask = async (taskId: string) => {
    try {
      await deleteTask(taskId);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    } catch (err) {
      console.error('Failed to delete task:', err);
    }
  };

  return (
    <div className="min-h-screen bg-black text-[#F2F2F7] flex flex-col antialiased selection:bg-[#007AFF]/30 selection:text-white">
      {/* Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        pendingCount={queueItems.length}
        onOpenNewTask={() => setIsModalOpen(true)}
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-md w-full mx-auto p-3 flex flex-col gap-3">
        {loading ? (
          <div className="flex flex-col items-center justify-center p-12 gap-2 text-zinc-500">
            <div className="w-5 h-5 border-2 border-[#007AFF] border-t-transparent rounded-full animate-spin" />
            <span className="text-[11px]">Syncing...</span>
          </div>
        ) : (
          <>
            {activeTab === 'queue' && (
              <div className="flex flex-col gap-2.5">
                {queueItems.length === 0 ? (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="liquid-glass rounded-2xl p-6 flex flex-col items-center justify-center text-center gap-2 mt-2"
                  >
                    <div className="w-8 h-8 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center">
                      <Check className="w-4 h-4 stroke-[2.5]" />
                    </div>
                    <h3 className="text-xs font-semibold text-white">Queue Empty</h3>
                    <p className="text-[11px] text-zinc-400 max-w-xs leading-relaxed">
                      All decisions resolved. Waiting for new triggers from AI or scheduled workflows.
                    </p>
                    <button
                      onClick={() => setIsModalOpen(true)}
                      className="mt-1 px-3 py-1.5 rounded-lg text-[11px] font-medium bg-white/[0.08] hover:bg-white/[0.12] border border-white/[0.08] text-white transition-colors"
                    >
                      New Task
                    </button>
                  </motion.div>
                ) : (
                  <AnimatePresence mode="popLayout">
                    {queueItems.map((item) => (
                      <QueueCard
                        key={item.id}
                        item={item}
                        onAnswer={handleAnswer}
                        onCancel={handleCancel}
                      />
                    ))}
                  </AnimatePresence>
                )}
              </div>
            )}

            {activeTab === 'tasks' && (
              <TasksList tasks={tasks} onDeleteTask={handleDeleteTask} />
            )}

            {activeTab === 'skills' && <SkillsRegistry skills={skills} />}
          </>
        )}
      </main>

      {/* New Task Modal */}
      <NewTaskModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreateTask}
        availableSkills={skills}
      />

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </div>
  );
}

export default App;
