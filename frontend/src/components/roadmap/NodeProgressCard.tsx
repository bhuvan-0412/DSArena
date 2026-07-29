"use client";

import { Lock, Clock, CheckCircle2, Zap, Calendar } from "lucide-react";

export type NodeStatusType = "LOCKED" | "AVAILABLE" | "IN_PROGRESS" | "COMPLETED";

interface NodeProgressCardProps {
  status: NodeStatusType;
  estimatedDuration?: number;
  xpReward?: number;
  startedAt?: string | null;
  completedAt?: string | null;
}

export function NodeProgressCard({
  status,
  xpReward = 50,
  startedAt,
  completedAt,
}: NodeProgressCardProps) {
  const getStatusBadge = () => {
    switch (status) {
      case "COMPLETED":
        return (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-success-emerald/10 border border-success-emerald/30 text-success-emerald font-bold text-xs uppercase tracking-wider shadow-sm">
            <CheckCircle2 className="w-4 h-4" />
            <span>Completed</span>
          </div>
        );
      case "IN_PROGRESS":
        return (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 font-bold text-xs uppercase tracking-wider shadow-sm animate-pulse">
            <Clock className="w-4 h-4" />
            <span>In Progress</span>
          </div>
        );
      case "AVAILABLE":
        return null;
      case "LOCKED":
      default:
        return (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-500 font-bold text-xs uppercase tracking-wider">
            <Lock className="w-4 h-4" />
            <span>Locked</span>
          </div>
        );
    }
  };

  const formatDate = (isoString?: string | null) => {
    if (!isoString) return null;
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return null;
    }
  };

  const badge = getStatusBadge();

  return (
    <div className="glass-card p-5 rounded-2xl border border-card-border space-y-4 shadow-lg">
      <div className="flex items-center justify-between gap-4 border-b border-card-border/60 pb-3">
        <span className="text-xs font-mono uppercase font-bold text-muted-foreground tracking-widest">
          Node Progress Status
        </span>
        {badge}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
        <div className="space-y-1">
          <span className="text-muted-foreground block text-[10px]">XP REWARD</span>
          <div className="flex items-center gap-1.5 font-bold text-xp-gold">
            <Zap className="w-3.5 h-3.5 fill-xp-gold" />
            <span>+{xpReward} XP</span>
          </div>
        </div>

        <div className="space-y-1">
          <span className="text-muted-foreground block text-[10px]">STARTED AT</span>
          <div className="flex items-center gap-1.5 font-medium text-zinc-300">
            <Calendar className="w-3.5 h-3.5 text-zinc-500" />
            <span>{formatDate(startedAt) || "Not started"}</span>
          </div>
        </div>

        <div className="space-y-1">
          <span className="text-muted-foreground block text-[10px]">COMPLETED AT</span>
          <div className="flex items-center gap-1.5 font-medium text-zinc-300">
            <CheckCircle2 className="w-3.5 h-3.5 text-success-emerald" />
            <span>{formatDate(completedAt) || "Incomplete"}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
