"use client";

import React from "react";
import { Award, Flame, Zap, Star, ShieldCheck, Lock } from "lucide-react";

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  unlocked: boolean;
  progressPct?: number;
}

export function AchievementsSection() {
  const achievements: Achievement[] = [
    {
      id: "first_lesson",
      title: "First Step Forward",
      description: "Complete your first lesson video in the DSA Arena catalog.",
      icon: <Zap className="w-5 h-5 text-amber-400" />,
      unlocked: true,
    },
    {
      id: "streak_3",
      title: "Consistent Learner",
      description: "Maintain an active study streak for 3 consecutive days.",
      icon: <Flame className="w-5 h-5 text-rose-400" />,
      unlocked: true,
    },
    {
      id: "step_master",
      title: "Step Master",
      description: "Complete all sections and lessons inside any single Step.",
      icon: <Award className="w-5 h-5 text-cyan-400" />,
      unlocked: false,
      progressPct: 60,
    },
    {
      id: "algo_champion",
      title: "Algorithmic Champion",
      description: "Master 50+ problem solving topics across the roadmap.",
      icon: <ShieldCheck className="w-5 h-5 text-indigo-400" />,
      unlocked: false,
      progressPct: 20,
    },
  ];

  return (
    <div className="space-y-4 pt-4 border-t border-slate-800/80">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Award className="w-5 h-5 text-amber-400" />
          <h2 className="text-lg font-extrabold text-white tracking-tight">Achievements & Badges</h2>
        </div>
        <span className="text-xs font-semibold text-slate-400">Placeholder Showcase</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {achievements.map((ach) => (
          <div
            key={ach.id}
            className={`relative rounded-xl p-4 border transition-all ${
              ach.unlocked
                ? "bg-slate-900/80 border-slate-800 shadow-lg"
                : "bg-slate-950/40 border-slate-900 opacity-60"
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800">
                {ach.icon}
              </div>

              {ach.unlocked ? (
                <span className="text-[10px] font-extrabold uppercase text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                  Unlocked
                </span>
              ) : (
                <span className="text-[10px] font-bold uppercase text-slate-500 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded flex items-center">
                  <Lock className="w-2.5 h-2.5 mr-1" /> Locked
                </span>
              )}
            </div>

            <div className="mt-3 space-y-1">
              <h4 className="text-xs font-extrabold text-white">{ach.title}</h4>
              <p className="text-[11px] text-slate-400 leading-relaxed">{ach.description}</p>
            </div>

            {!ach.unlocked && ach.progressPct !== undefined && (
              <div className="mt-3 space-y-1">
                <div className="flex justify-between text-[10px] text-slate-500 font-semibold">
                  <span>Progress</span>
                  <span>{ach.progressPct}%</span>
                </div>
                <div className="w-full bg-slate-900 h-1 rounded-full overflow-hidden">
                  <div
                    className="bg-indigo-500 h-full rounded-full"
                    style={{ width: `${ach.progressPct}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
