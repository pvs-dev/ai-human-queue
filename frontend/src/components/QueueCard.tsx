import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';
import type { QueueItem } from '../types';
import { triggerHaptic } from '../telegram';

interface QueueCardProps {
  item: QueueItem;
  onAnswer: (itemId: string, data: { selected_options?: string[]; text_response?: string }) => Promise<void>;
  onCancel: (itemId: string) => Promise<void>;
}

export const QueueCard: React.FC<QueueCardProps> = ({ item, onAnswer, onCancel }) => {
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  const [textInput, setTextInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isSingleChoice = item.item_type === 'single_choice';
  const isMultiChoice = item.item_type === 'multi_choice';
  const isTextInput = item.item_type === 'text_input';

  const handleOptionToggle = (optId: string) => {
    triggerHaptic('light');
    if (isSingleChoice) {
      setSelectedOptions([optId]);
    } else {
      setSelectedOptions((prev) =>
        prev.includes(optId) ? prev.filter((id) => id !== optId) : [...prev, optId]
      );
    }
  };

  const handleSubmit = async () => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    triggerHaptic('medium');
    try {
      if (isTextInput) {
        await onAnswer(item.id, { text_response: textInput.trim() });
      } else {
        await onAnswer(item.id, { selected_options: selectedOptions });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = async () => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    triggerHaptic('warning');
    try {
      await onCancel(item.id);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 15, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.94, height: 0, marginBottom: 0 }}
      transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
      className="liquid-glass rounded-2xl p-3.5 flex flex-col gap-2.5 relative overflow-hidden"
    >
      {/* Header Info */}
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="text-xs font-semibold text-white tracking-tight">{item.title}</h3>
          <span className="text-[10px] text-zinc-400 flex items-center gap-1 mt-0.5">
            <span>{item.source_agent}</span>
            <span>•</span>
            <span className="capitalize">{item.item_type.replace('_', ' ')}</span>
          </span>
        </div>
      </div>

      {/* Description / Context */}
      {item.description && (
        <p className="text-[11px] text-zinc-300 bg-white/[0.03] p-2 rounded-xl border border-white/[0.05] leading-relaxed whitespace-pre-wrap">
          {item.description}
        </p>
      )}

      {/* Single Choice: Apple Segmented Pill Layout */}
      {isSingleChoice && item.options && item.options.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5 p-1 bg-black/40 rounded-xl border border-white/[0.05]">
          {item.options.map((opt) => {
            const isSelected = selectedOptions.includes(opt.id);
            return (
              <button
                key={opt.id}
                type="button"
                onClick={() => handleOptionToggle(opt.id)}
                className={`py-1.5 px-2 rounded-lg text-[11px] font-medium transition-all text-center truncate ${
                  isSelected
                    ? 'bg-[#007AFF] text-white shadow-sm font-semibold'
                    : 'bg-white/[0.04] text-zinc-300 hover:bg-white/[0.08] active:scale-98'
                }`}
                title={opt.label}
              >
                {opt.label}
              </button>
            );
          })}
        </div>
      )}

      {/* Multi Choice: Apple Minimal Checkboxes */}
      {isMultiChoice && item.options && item.options.length > 0 && (
        <div className="flex flex-col gap-1">
          {item.options.map((opt) => {
            const isSelected = selectedOptions.includes(opt.id);
            return (
              <button
                key={opt.id}
                type="button"
                onClick={() => handleOptionToggle(opt.id)}
                className={`w-full text-left px-2.5 py-1.5 rounded-xl border text-[11px] font-medium transition-all flex items-center justify-between gap-2 ${
                  isSelected
                    ? 'bg-[#007AFF]/15 border-[#007AFF]/40 text-white'
                    : 'bg-white/[0.02] border-white/[0.04] text-zinc-300 hover:border-white/[0.1] active:scale-[0.99]'
                }`}
              >
                <div className="flex items-center gap-2">
                  <div
                    className={`w-3.5 h-3.5 rounded-md border flex items-center justify-center transition-colors ${
                      isSelected
                        ? 'bg-[#007AFF] border-[#007AFF] text-white'
                        : 'border-zinc-600 bg-white/[0.04]'
                    }`}
                  >
                    {isSelected && <Check className="w-2.5 h-2.5 stroke-[3]" />}
                  </div>
                  <span>{opt.label}</span>
                </div>
              </button>
            );
          })}
        </div>
      )}

      {/* Text Input */}
      {isTextInput && (
        <textarea
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          placeholder="Type your response..."
          rows={2}
          className="w-full bg-black/50 border border-white/[0.08] rounded-xl p-2 text-[11px] text-white placeholder-zinc-500 focus:outline-none focus:border-[#007AFF] transition-colors resize-none"
        />
      )}

      {/* Compact Minimal Footer */}
      <div className="flex items-center justify-end gap-1.5 pt-1 border-t border-white/[0.05]">
        <button
          type="button"
          onClick={handleCancel}
          disabled={isSubmitting}
          className="px-2.5 py-1 rounded-lg text-[11px] font-medium text-zinc-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
        >
          Cancel
        </button>

        <button
          type="button"
          onClick={handleSubmit}
          disabled={
            isSubmitting ||
            (isTextInput && !textInput.trim()) ||
            (!isTextInput && selectedOptions.length === 0)
          }
          className="px-3 py-1 rounded-lg text-[11px] font-medium bg-[#007AFF] hover:bg-[#0071e3] text-white shadow-sm active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
        >
          Submit
        </button>
      </div>
    </motion.div>
  );
};
