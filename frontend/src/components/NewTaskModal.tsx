import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Check } from 'lucide-react';
import type { Skill } from '../types';
import { triggerHaptic } from '../telegram';

interface NewTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { title?: string; prompt: string; skills: string[]; schedule_cron?: string }) => Promise<void>;
  availableSkills: Skill[];
}

export const NewTaskModal: React.FC<NewTaskModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  availableSkills,
}) => {
  const [prompt, setPrompt] = useState('');
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [enableCron, setEnableCron] = useState(false);
  const [cronExpression, setCronExpression] = useState('*/1 * * * *');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const toggleSkill = (skillId: string) => {
    triggerHaptic('light');
    setSelectedSkills((prev) =>
      prev.includes(skillId) ? prev.filter((s) => s !== skillId) : [...prev, skillId]
    );
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isSubmitting) return;

    setIsSubmitting(true);
    triggerHaptic('success');
    try {
      await onSubmit({
        prompt: prompt.trim(),
        skills: selectedSkills,
        schedule_cron: enableCron ? cronExpression : undefined,
      });
      setPrompt('');
      setSelectedSkills([]);
      setEnableCron(false);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/70 backdrop-blur-sm p-0 sm:p-4">
        <motion.div
          initial={{ opacity: 0, y: 80 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 80 }}
          transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
          className="w-full max-w-md liquid-glass rounded-t-3xl sm:rounded-3xl p-4 shadow-2xl flex flex-col gap-3.5 max-h-[85vh] overflow-y-auto safe-bottom"
        >
          {/* Sheet Handle */}
          <div className="w-9 h-1 bg-white/20 rounded-full mx-auto sm:hidden" />

          {/* Header */}
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold text-white tracking-tight">New AI Task</h2>
            <button
              onClick={onClose}
              className="w-6 h-6 rounded-full bg-white/10 text-zinc-400 hover:text-white flex items-center justify-center transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          <form onSubmit={handleCreate} className="flex flex-col gap-3">
            {/* Prompt textarea */}
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe task or instructions for AI..."
              rows={3}
              required
              className="w-full bg-black/60 border border-white/[0.08] rounded-xl p-2.5 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-[#007AFF] transition-colors resize-none"
            />

            {/* Skills & Slash Commands Pills */}
            <div className="flex flex-col gap-1.5">
              <span className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider">
                Attach Skills / Slash Commands
              </span>
              <div className="flex flex-wrap gap-1">
                {availableSkills.map((skill) => {
                  const isSelected = selectedSkills.includes(skill.id);
                  return (
                    <button
                      key={skill.id}
                      type="button"
                      onClick={() => toggleSkill(skill.id)}
                      className={`px-2 py-1 rounded-lg text-[11px] font-mono transition-all flex items-center gap-1 border ${
                        isSelected
                          ? 'bg-[#007AFF] border-[#007AFF] text-white font-medium shadow-sm'
                          : 'bg-white/[0.04] border-white/[0.06] text-zinc-400 hover:text-zinc-200'
                      }`}
                    >
                      <span>{skill.name}</span>
                      {isSelected && <Check className="w-2.5 h-2.5 stroke-[3]" />}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Schedule / Cron Setting */}
            <div className="bg-white/[0.03] border border-white/[0.05] rounded-xl p-2.5 flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-medium text-zinc-200">Recurring Schedule (Cron)</span>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={enableCron}
                    onChange={(e) => setEnableCron(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-8 h-4.5 bg-zinc-700 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-3.5 after:w-3.5 after:transition-all peer-checked:bg-[#30D158]"></div>
                </label>
              </div>

              {enableCron && (
                <input
                  type="text"
                  value={cronExpression}
                  onChange={(e) => setCronExpression(e.target.value)}
                  placeholder="*/1 * * * * (Every 1m)"
                  className="w-full bg-black/60 border border-white/[0.08] rounded-lg px-2 py-1 text-[11px] text-white font-mono placeholder-zinc-500 focus:outline-none focus:border-[#007AFF]"
                />
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting || !prompt.trim()}
              className="w-full py-2 rounded-xl text-xs font-semibold text-white bg-[#007AFF] hover:bg-[#0071e3] shadow-md active:scale-98 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
            >
              Create Task
            </button>
          </form>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
