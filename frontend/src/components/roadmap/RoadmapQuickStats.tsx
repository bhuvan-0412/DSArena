import React from "react";
import { CheckCircle2, FileCode, Flame, Percent } from "lucide-react";

interface RoadmapQuickStatsProps {
  completedLessons: number;
  totalLessons: number;
  currentStreak?: number;
  completionPercentage: number;
}

export function RoadmapQuickStats({
  completedLessons,
  totalLessons,
  currentStreak = 0,
  completionPercentage,
}: RoadmapQuickStatsProps) {
  const lessonsRemaining = Math.max(0, totalLessons - completedLessons);

  return (
    <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3">
      {/* 1. Lessons Completed */}
      <div className="bg-slate-900/90 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between shadow-lg shadow-black/20">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider">Completed</span>
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
        </div>
        <div className="text-2xl font-extrabold text-white tracking-tight">
          {completedLessons}
          <span className="text-xs font-normal text-slate-500 ml-1">/ {totalLessons}</span>
        </div>
        <span className="text-[10px] text-emerald-400 font-medium mt-0.5">Lessons Mastered</span>
      </div>

      {/* 2. Lessons Remaining */}
      <div className="bg-slate-900/90 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between shadow-lg shadow-black/20">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider">Remaining</span>
          <FileCode className="w-4 h-4 text-amber-400" />
        </div>
        <div className="text-2xl font-extrabold text-white tracking-tight">{lessonsRemaining}</div>
        <span className="text-[10px] text-amber-400/90 font-medium mt-0.5">Lessons Unlocked</span>
      </div>

      {/* 3. Current Streak */}
      <div className="bg-slate-900/90 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between shadow-lg shadow-black/20">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider">Streak</span>
          <Flame className="w-4 h-4 text-rose-400" />
        </div>
        <div className="text-2xl font-extrabold text-white tracking-tight">
          {currentStreak} <span className="text-sm font-bold text-rose-400">Days</span>
        </div>
        <span className="text-[10px] text-rose-400/90 font-medium mt-0.5">Active Study Streak</span>
      </div>

      {/* 4. Completion Percentage */}
      <div className="col-span-2 sm:col-span-1 bg-gradient-to-tr from-cyan-950/40 via-slate-900 to-indigo-950/40 border border-cyan-500/30 rounded-xl p-3.5 flex flex-col justify-between shadow-lg shadow-cyan-500/5">
        <div className="flex items-center justify-between text-cyan-300 mb-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider">Overall Progress</span>
          <Percent className="w-4 h-4 text-cyan-400" />
        </div>
        <div className="text-2xl font-extrabold text-cyan-400 tracking-tight">
          {completionPercentage}%
        </div>
        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1">
          <div
            className="bg-gradient-to-r from-cyan-500 to-emerald-400 h-full rounded-full transition-all duration-500"
            style={{ width: `${completionPercentage}%` }}
          />
        </div>
      </div>
    </div>
  );
}
