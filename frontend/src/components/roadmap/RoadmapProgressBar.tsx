"use client";

import { Video, Trophy } from "lucide-react";

interface RoadmapProgressBarProps {
  topicName?: string;
  completedVideos: number;
  totalVideos: number;
  progressPercentage: number;
  overallXp?: number;
}

export function RoadmapProgressBar({
  topicName = "Overall Topic Progress",
  completedVideos,
  totalVideos,
  progressPercentage,
  overallXp = 0,
}: RoadmapProgressBarProps) {
  return (
    <div className="glass-card p-5 rounded-2xl border border-card-border space-y-3 shadow-xl">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-primary/10 border border-primary/20 text-primary">
            <Video className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wide">{topicName}</h3>
            <p className="text-xs text-muted-foreground font-mono">
              {completedVideos} / {totalVideos} videos completed
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 font-mono">
          {overallXp > 0 && (
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-xp-gold/10 border border-xp-gold/30 text-xp-gold text-xs font-bold">
              <Trophy className="w-3.5 h-3.5" />
              <span>{overallXp} XP</span>
            </div>
          )}

          <div className="text-right">
            <span className="text-2xl font-black text-white">{progressPercentage}%</span>
            <span className="text-[10px] text-muted-foreground uppercase font-bold block">Completed</span>
          </div>
        </div>
      </div>

      {/* Progress Bar Container */}
      <div className="relative w-full h-3 bg-zinc-950 rounded-full border border-card-border overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-primary via-info-cyan to-success-emerald transition-all duration-500 rounded-full shadow-[0_0_12px_rgba(168,85,247,0.4)]"
          style={{ width: `${Math.min(100, Math.max(0, progressPercentage))}%` }}
        />
      </div>
    </div>
  );
}
