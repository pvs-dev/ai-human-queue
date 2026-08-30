import React from 'react';
import { Plus, Settings, HelpCircle } from 'lucide-react';

interface HeaderProps {
  activeTab: 'queue' | 'tasks' | 'skills';
  setActiveTab: (tab: 'queue' | 'tasks' | 'skills') => void;
  pendingCount: number;
  onOpenNewTask: () => void;
  onOpenSettings: () => void;
  onOpenHelp: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  pendingCount,
  onOpenNewTask,
  onOpenSettings,
  onOpenHelp,
}) => {
  return (
    <header className="sticky top-0 z-30 bg-black/75 backdrop-blur-2xl border-b border-white/[0.07] px-4 py-2.5">
      <div className="max-w-md mx-auto flex flex-col gap-2.5">
        {/* Navigation Bar Top */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h1 className="text-sm font-semibold tracking-tight text-white">
              AI Action Queue
            </h1>
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[10px] font-medium text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>AI Connected</span>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            {pendingCount > 0 && (
              <span className="px-2 py-0.5 text-[10px] font-semibold rounded-full bg-blue-500/15 text-blue-400 border border-blue-500/25">
                {pendingCount} Pending
              </span>
            )}
            <button
              onClick={onOpenHelp}
              className="w-7 h-7 rounded-full bg-white/[0.08] hover:bg-white/[0.14] text-zinc-300 hover:text-white flex items-center justify-center border border-white/[0.08] active:scale-95 transition-all"
              title="AI Setup Assistant & Prompts"
            >
              <HelpCircle className="w-3.5 h-3.5 text-indigo-400" />
            </button>
            <button
              onClick={onOpenSettings}
              className="w-7 h-7 rounded-full bg-white/[0.08] hover:bg-white/[0.14] text-zinc-300 hover:text-white flex items-center justify-center border border-white/[0.08] active:scale-95 transition-all"
              title="Settings"
            >
              <Settings className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={onOpenNewTask}
              className="w-7 h-7 rounded-full bg-[#007AFF] text-white flex items-center justify-center shadow-sm hover:bg-[#0071e3] active:scale-95 transition-transform"
              title="New Task"
            >
              <Plus className="w-4 h-4 stroke-[2.5]" />
            </button>
          </div>
        </div>

        {/* Apple Segmented Control Tab Bar */}
        <div className="flex p-0.5 bg-[#1C1C1E]/80 backdrop-blur-md rounded-lg border border-white/[0.06] text-xs font-medium">
          <button
            onClick={() => setActiveTab('queue')}
            className={`flex-1 py-1 rounded-[6px] text-center text-[11px] font-medium transition-all ${
              activeTab === 'queue'
                ? 'bg-[#636366]/40 text-white shadow-sm font-semibold'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Queue {pendingCount > 0 && `(${pendingCount})`}
          </button>

          <button
            onClick={() => setActiveTab('tasks')}
            className={`flex-1 py-1 rounded-[6px] text-center text-[11px] font-medium transition-all ${
              activeTab === 'tasks'
                ? 'bg-[#636366]/40 text-white shadow-sm font-semibold'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Tasks
          </button>

          <button
            onClick={() => setActiveTab('skills')}
            className={`flex-1 py-1 rounded-[6px] text-center text-[11px] font-medium transition-all ${
              activeTab === 'skills'
                ? 'bg-[#636366]/40 text-white shadow-sm font-semibold'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Skills
          </button>
        </div>
      </div>
    </header>
  );
};
