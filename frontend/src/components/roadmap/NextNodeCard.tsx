"use client";

import { ChevronRight, CheckCircle2, Play, Clock } from "lucide-react";

interface NextNodeInfo {
  id: string;
  title: string;
  estimated_duration?: number;
  thumbnail_url?: string | null;
  status?: string;
  is_locked?: boolean;
}

interface NextNodeCardProps {
  isCompleted: boolean;
  nextNode?: NextNodeInfo | null;
  onNavigateNext: () => void;
  loading?: boolean;
}

export function NextNodeCard({
  isCompleted,
  nextNode,
  onNavigateNext,
  loading = false,
}: NextNodeCardProps) {
  if (!isCompleted) {
    return (
      <div className="glass-card p-6 rounded-2xl border border-card-border/60 opacity-60 text-center space-y-2">
        <span className="text-xs font-mono uppercase font-bold text-zinc-500 tracking-widest block">
          NEXT LESSON UNLOCK
        </span>
        <p className="text-xs text-muted-foreground">
          Complete watching the current video and click &quot;Mark as Done&quot; above to unlock the next roadmap node.
        </p>
      </div>
    );
  }

  if (!nextNode) {
    return (
      <div className="glass-card p-6 rounded-2xl border border-success-emerald/40 bg-success-emerald/5 text-center space-y-3 shadow-xl">
        <div className="w-12 h-12 rounded-full bg-success-emerald/20 border border-success-emerald/40 flex items-center justify-center mx-auto text-success-emerald">
          <CheckCircle2 className="w-6 h-6" />
        </div>
        <div>
          <h4 className="text-lg font-black text-white">Congratulations!</h4>
          <p className="text-xs text-success-emerald/90 font-mono mt-1">
            You completed this section.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card p-6 rounded-2xl border border-card-border space-y-4 shadow-xl">
      <div className="flex items-center justify-between">
        <span className="text-xs font-mono uppercase font-bold text-info-cyan tracking-widest">
          UP NEXT IN ROADMAP
        </span>
        <span className="text-xs font-mono text-success-emerald font-bold flex items-center gap-1">
          <Play className="w-3 h-3 fill-success-emerald" /> Unlocked
        </span>
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl bg-zinc-950/60 border border-zinc-800">
        {nextNode.thumbnail_url ? (
          <div 
            className="w-full sm:w-28 h-16 rounded-lg bg-cover bg-center border border-zinc-800 flex-shrink-0 relative overflow-hidden"
            style={{ backgroundImage: `url(${nextNode.thumbnail_url})` }}
          >
            <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
              <Play className="w-5 h-5 text-white fill-white" />
            </div>
          </div>
        ) : null}

        <div className="space-y-1 flex-1">
          <h4 className="text-base font-bold text-white leading-tight">{nextNode.title}</h4>
          <div className="flex items-center gap-2 text-xs text-muted-foreground font-mono">
            <Clock className="w-3 h-3" />
            <span>EST: {nextNode.estimated_duration || 15} mins</span>
          </div>
        </div>

        <button
          onClick={onNavigateNext}
          disabled={loading}
          className="w-full sm:w-auto px-6 py-3 rounded-xl bg-primary hover:bg-primary/90 text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-lg shadow-primary/20 transition-all cursor-pointer"
        >
          <span>Go To Next Node</span>
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
