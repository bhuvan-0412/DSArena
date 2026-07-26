"use client";

import React from "react";
import { Trophy, CheckCircle2, Clock, Hourglass, BarChart, Sparkles } from "lucide-react";

interface ProgressCardProps {
  completedCount: number;
  totalCount: number;
  progressPercentage: number;
  estimatedTimeMins?: number;
  lessonStatus?: string;
}

export function ProgressCard({
  completedCount,
  totalCount,
  progressPercentage,
  estimatedTimeMins = 0,
  lessonStatus = "AVAILABLE",
}: ProgressCardProps) {
  const remainingCount = Math.max(0, totalCount - completedCount);
  const totalMinsLeft = remainingCount * 20 + estimatedTimeMins;
  
  const formatTime = (mins: number) => {
    if (mins <= 0) return "0 mins";
    if (mins < 60) return `${mins} mins`;
    const h = Math.floor(mins / 60);
    const m = mins % 60;
    return m > 0 ? `${h}h ${m}m` : `${h}h`;
  };

  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-950/90 p-5 space-y-4 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <BarChart className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-zinc-300">
              PROGRESS SUMMARY
            </h4>
            <p className="text-[11px] text-zinc-400">Roadmap learning metrics</p>
          </div>
        </div>
        <span className="text-xs font-mono font-bold text-cyan-400 bg-cyan-500/10 border border-cyan-500/20 px-2.5 py-1 rounded-full flex items-center gap-1">
          <Sparkles className="w-3 h-3" />
          <span>{progressPercentage}% OVERALL</span>
        </span>
      </div>

      {/* Progress Bar */}
      <div className="space-y-1.5">
        <div className="w-full h-2.5 rounded-full bg-zinc-900 overflow-hidden border border-zinc-800">
          <div
            className="h-full bg-gradient-to-r from-cyan-500 via-teal-400 to-emerald-400 rounded-full transition-all duration-700 ease-out"
            style={{ width: `${Math.min(100, Math.max(0, progressPercentage))}%` }}
          />
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 gap-2.5 pt-1">
        <div className="p-3 rounded-xl border border-zinc-800/80 bg-zinc-900/50 flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
            <CheckCircle2 className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-white">{completedCount}</div>
            <div className="text-[10px] text-zinc-400">Completed Lessons</div>
          </div>
        </div>

        <div className="p-3 rounded-xl border border-zinc-800/80 bg-zinc-900/50 flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
            <Hourglass className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-white">{remainingCount}</div>
            <div className="text-[10px] text-zinc-400">Remaining Lessons</div>
          </div>
        </div>

        <div className="p-3 rounded-xl border border-zinc-800/80 bg-zinc-900/50 flex items-center gap-2.5 col-span-2">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
            <Clock className="w-4 h-4" />
          </div>
          <div className="flex-1 flex items-center justify-between">
            <div>
              <div className="text-xs font-bold text-white">{formatTime(totalMinsLeft)}</div>
              <div className="text-[10px] text-zinc-400">Estimated Time Remaining</div>
            </div>
            <Trophy className="w-4 h-4 text-amber-400/80" />
          </div>
        </div>
      </div>
    </div>
  );
}
