import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Send, Save, Bot, Clock, Wifi, Check } from 'lucide-react';
import type { AppSettings } from '../types';
import { fetchSettings, updateSettings, testTelegramPush } from '../api';
import { triggerHaptic } from '../telegram';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const [settings, setSettings] = useState<AppSettings>({
    telegram_bot_token: '',
    telegram_webapp_url: 'http://localhost:8000',
    telegram_admin_chat_id: '',
    worker_interval_seconds: 60,
    auditor_interval_seconds: 120,
    auto_audit_enabled: true,
    custom_prompt_prefix: '',
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [testStatus, setTestStatus] = useState<string | null>(null);
  const [testLoading, setTestLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      setSavedSuccess(false);
      setTestStatus(null);
      fetchSettings()
        .then(setSettings)
        .catch((err) => console.error('Failed to load settings:', err))
        .finally(() => setLoading(false));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (saving) return;
    setSaving(true);
    setSavedSuccess(false);
    triggerHaptic('medium');
    try {
      const updated = await updateSettings(settings);
      setSettings(updated);
      setSavedSuccess(true);
      triggerHaptic('success');
      setTimeout(() => setSavedSuccess(false), 2500);
    } catch (err) {
      console.error('Failed to save settings:', err);
      triggerHaptic('error');
    } finally {
      setSaving(false);
    }
  };

  const handleTestTelegram = async () => {
    if (testLoading) return;
    setTestLoading(true);
    setTestStatus(null);
    triggerHaptic('light');
    try {
      // First save current form values so test uses newest input
      await updateSettings(settings);
      const res = await testTelegramPush();
      setTestStatus(res.message || 'Push отправлен успешно!');
      triggerHaptic('success');
    } catch (err: any) {
      setTestStatus(err.message || 'Ошибка отправки пуша в Telegram');
      triggerHaptic('error');
    } finally {
      setTestLoading(false);
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/75 backdrop-blur-md p-0 sm:p-4">
        <motion.div
          initial={{ opacity: 0, y: 80 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 80 }}
          transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
          className="w-full max-w-md liquid-glass rounded-t-3xl sm:rounded-3xl p-4 shadow-2xl flex flex-col gap-3.5 max-h-[90vh] overflow-y-auto safe-bottom"
        >
          {/* Sheet Handle */}
          <div className="w-9 h-1 bg-white/20 rounded-full mx-auto sm:hidden" />

          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h2 className="text-xs font-bold text-white tracking-tight">System Settings</h2>
              <span className="text-[10px] text-zinc-500 font-mono">LAN Local</span>
            </div>
            <button
              onClick={onClose}
              className="w-6 h-6 rounded-full bg-white/10 text-zinc-400 hover:text-white flex items-center justify-center transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          {loading ? (
            <div className="p-8 flex items-center justify-center text-zinc-500 text-xs">
              Loading settings...
            </div>
          ) : (
            <form onSubmit={handleSave} className="flex flex-col gap-3.5">
              {/* Section 1: Telegram Bot */}
              <div className="bg-white/[0.03] border border-white/[0.06] rounded-2xl p-3 flex flex-col gap-2.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-white">
                    <Bot className="w-3.5 h-3.5 text-blue-400" />
                    <span>Telegram Bot & Push</span>
                  </div>
                  <span className="text-[10px] text-zinc-500">Уведомления на телефон</span>
                </div>

                <div className="flex flex-col gap-1">
                  <label className="text-[10px] font-medium text-zinc-400">Bot Token (из @BotFather)</label>
                  <input
                    type="password"
                    value={settings.telegram_bot_token}
                    onChange={(e) => setSettings({ ...settings, telegram_bot_token: e.target.value })}
                    placeholder="123456789:ABCdef..."
                    className="w-full bg-black/60 border border-white/[0.08] rounded-xl px-2.5 py-1.5 text-[11px] text-white font-mono placeholder-zinc-600 focus:outline-none focus:border-[#007AFF]"
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <label className="text-[10px] font-medium text-zinc-400">Admin Chat ID (Ваш Telegram ID)</label>
                  <input
                    type="text"
                    value={settings.telegram_admin_chat_id}
                    onChange={(e) => setSettings({ ...settings, telegram_admin_chat_id: e.target.value })}
                    placeholder="e.g. 987654321"
                    className="w-full bg-black/60 border border-white/[0.08] rounded-xl px-2.5 py-1.5 text-[11px] text-white font-mono placeholder-zinc-600 focus:outline-none focus:border-[#007AFF]"
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <label className="text-[10px] font-medium text-zinc-400">Public WebApp URL (для инлайн-кнопки)</label>
                  <input
                    type="text"
                    value={settings.telegram_webapp_url}
                    onChange={(e) => setSettings({ ...settings, telegram_webapp_url: e.target.value })}
                    placeholder="https://your-domain-or-tunnel.com"
                    className="w-full bg-black/60 border border-white/[0.08] rounded-xl px-2.5 py-1.5 text-[11px] text-white font-mono placeholder-zinc-600 focus:outline-none focus:border-[#007AFF]"
                  />
                </div>

                <div className="flex items-center justify-between pt-1 border-t border-white/[0.04]">
                  <button
                    type="button"
                    onClick={handleTestTelegram}
                    disabled={testLoading || !settings.telegram_bot_token || !settings.telegram_admin_chat_id}
                    className="px-2.5 py-1 rounded-lg text-[10px] font-medium bg-blue-500/15 border border-blue-500/25 text-blue-300 hover:bg-blue-500/25 disabled:opacity-30 transition-all flex items-center gap-1"
                  >
                    <Send className="w-3 h-3" />
                    <span>{testLoading ? 'Отправка...' : 'Тест Telegram Push'}</span>
                  </button>

                  {testStatus && (
                    <span className="text-[10px] text-zinc-300 truncate max-w-[200px]">
                      {testStatus}
                    </span>
                  )}
                </div>
              </div>

              {/* Section 2: Worker & Scheduler */}
              <div className="bg-white/[0.03] border border-white/[0.06] rounded-2xl p-3 flex flex-col gap-2.5">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-white">
                  <Clock className="w-3.5 h-3.5 text-purple-400" />
                  <span>Периодичность проверки (сек)</span>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div className="flex flex-col gap-1">
                    <label className="text-[10px] font-medium text-zinc-400">Worker Опрос (сек)</label>
                    <input
                      type="number"
                      min={5}
                      max={3600}
                      value={settings.worker_interval_seconds}
                      onChange={(e) => setSettings({ ...settings, worker_interval_seconds: parseInt(e.target.value) || 60 })}
                      className="w-full bg-black/60 border border-white/[0.08] rounded-xl px-2.5 py-1.5 text-[11px] text-white font-mono focus:outline-none focus:border-[#007AFF]"
                    />
                  </div>

                  <div className="flex flex-col gap-1">
                    <label className="text-[10px] font-medium text-zinc-400">Аудитор UX (сек)</label>
                    <input
                      type="number"
                      min={10}
                      max={3600}
                      value={settings.auditor_interval_seconds}
                      onChange={(e) => setSettings({ ...settings, auditor_interval_seconds: parseInt(e.target.value) || 120 })}
                      className="w-full bg-black/60 border border-white/[0.08] rounded-xl px-2.5 py-1.5 text-[11px] text-white font-mono focus:outline-none focus:border-[#007AFF]"
                    />
                  </div>
                </div>
              </div>

              {/* Section 3: LAN Network Info */}
              <div className="bg-white/[0.03] border border-white/[0.06] rounded-2xl p-3 flex flex-col gap-1.5 text-[11px]">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-white mb-0.5">
                  <Wifi className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Локальная сеть (LAN)</span>
                </div>
                <div className="flex items-center justify-between text-zinc-400 text-[10px] font-mono">
                  <span>Phone URL:</span>
                  <span className="text-emerald-400 font-semibold">{window.location.origin}</span>
                </div>
                <p className="text-[10px] text-zinc-500 mt-0.5">
                  Сессии отключены. Настройки сохраняются в единую локальную базу данных PostgreSQL.
                </p>
              </div>

              {/* Save Button */}
              <button
                type="submit"
                disabled={saving}
                className="w-full py-2 rounded-xl text-xs font-semibold text-white bg-[#007AFF] hover:bg-[#0071e3] shadow-md active:scale-98 disabled:opacity-40 transition-all flex items-center justify-center gap-1.5"
              >
                {savedSuccess ? (
                  <>
                    <Check className="w-3.5 h-3.5" />
                    <span>Сохранено в базу данных!</span>
                  </>
                ) : (
                  <>
                    <Save className="w-3.5 h-3.5" />
                    <span>{saving ? 'Сохранение...' : 'Сохранить настройки'}</span>
                  </>
                )}
              </button>
            </form>
          )}
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
