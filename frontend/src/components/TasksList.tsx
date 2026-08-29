import React from 'react';
import { motion } from 'framer-motion';
import type { Task } from '../types';
import { Trash2 } from 'lucide-react';
import { triggerHaptic } from '../telegram';

interface TasksListProps {
  tasks: Task[];
  onDeleteTask: (taskId: string) => Promise<void>;
}

const getStatusBadge = (status: Task['status']) => {
  switch (status) {
    case 'running':
      return (
        <span className="text-[10px] font-medium text-amber-400 bg-amber-500/10 border border-amber-500/20 px-1.5 py-0.5 rounded-md">
          Running
        </span>
      );
    case 'waiting_human':
      return (
        <span className="text-[10px] font-medium text-blue-400 bg-blue-500/10 border border-blue-500/20 px-1.5 py-0.5 rounded-md">
          In Queue
        </span>
      );
    case 'completed':
      return (
        <span className="text-[10px] font-medium text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.5 rounded-md">
          Completed
        </span>
      );
    case 'cancelled':
      return (
        <span className="text-[10px] font-medium text-rose-400 bg-rose-500/10 border border-rose-500/20 px-1.5 py-0.5 rounded-md">
          Cancelled
        </span>
      );
    default:
      return (
        <span className="text-[10px] font-medium text-zinc-400 bg-zinc-500/10 border border-zinc-500/20 px-1.5 py-0.5 rounded-md">
          Pending
        </span>
      );
  }
};

export const TasksList: React.FC<TasksListProps> = ({ tasks, onDeleteTask }) => {
  if (tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-10 text-center text-zinc-500 gap-2">
        <p className="text-xs">No tasks in backlog</p>
        <p className="text-[11px] text-zinc-600">Create a task to assign work to AI agents.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      {tasks.map((task) => (
        <motion.div
          key={task.id}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="liquid-glass rounded-2xl p-3 flex flex-col gap-2"
        >
          {/* Top Line */}
          <div className="flex items-start justify-between gap-2">
            <div>
              <h4 className="text-xs font-semibold text-white tracking-tight">{task.title}</h4>
              <p className="text-[11px] text-zinc-300 mt-0.5 leading-relaxed">{task.prompt}</p>
            </div>
            {getStatusBadge(task.status)}
          </div>

          {/* Attached Skills */}
          {task.skills && task.skills.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {task.skills.map((skill) => (
                <span
                  key={skill}
                  className="px-1.5 py-0.5 rounded-md bg-white/[0.04] border border-white/[0.06] text-zinc-300 text-[10px] font-mono"
                >
                  {skill}
                </span>
              ))}
              {task.schedule_cron && (
                <span className="px-1.5 py-0.5 rounded-md bg-purple-500/10 border border-purple-500/20 text-purple-300 text-[10px] font-mono">
                  {task.schedule_cron}
                </span>
              )}
            </div>
          )}

          {/* Result Summary if available */}
          {task.result_summary && (
            <div className="p-2 rounded-xl bg-black/40 border border-white/[0.05] text-[11px] text-zinc-300">
              <span className="text-[9px] text-zinc-500 block mb-0.5 uppercase tracking-wider">Output:</span>
              {task.result_summary}
            </div>
          )}

          {/* Footer */}
          <div className="flex items-center justify-between text-[10px] text-zinc-500 pt-1 border-t border-white/[0.04]">
            <span>{new Date(task.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
            <button
              onClick={() => {
                triggerHaptic('warning');
                onDeleteTask(task.id);
              }}
              className="p-1 text-zinc-500 hover:text-rose-400 transition-colors"
            >
              <Trash2 className="w-3 h-3" />
            </button>
          </div>
        </motion.div>
      ))}
    </div>
  );
};
