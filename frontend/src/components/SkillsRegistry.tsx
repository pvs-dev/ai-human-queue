import React from 'react';
import type { Skill } from '../types';

interface SkillsRegistryProps {
  skills: Skill[];
}

export const SkillsRegistry: React.FC<SkillsRegistryProps> = ({ skills }) => {
  return (
    <div className="flex flex-col gap-2">
      <div className="p-2.5 liquid-glass-subtle rounded-xl text-[11px] text-zinc-300 leading-relaxed">
        Скиллы и слэш-команды, зарегистрированные для AI-агентов. Прикрепляйте их к задачам для автоматического вызова.
      </div>

      <div className="flex flex-col gap-1.5">
        {skills.map((skill) => (
          <div
            key={skill.id}
            className="liquid-glass rounded-xl p-2.5 flex items-start justify-between gap-2"
          >
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-mono font-bold text-white">{skill.name}</span>
                <span className="text-[9px] px-1.5 py-0.2 rounded-full bg-white/10 text-zinc-400 font-medium">
                  {skill.category}
                </span>
              </div>
              <p className="text-[11px] text-zinc-300 mt-0.5 leading-relaxed">{skill.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
