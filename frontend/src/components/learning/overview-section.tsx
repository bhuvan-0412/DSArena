"use client";

import { Zap, Bookmark, CheckCircle2, BookmarkCheck } from "lucide-react";
import { motion } from "framer-motion";

interface OverviewSectionProps {
  topic: {
    id: string;
    title: string;
    description: string;
    difficulty: string;
    estimated_time?: number;
    xp_reward: number;
    prerequisites?: string[];
    learning_objectives?: string[];
    is_bookmarked: boolean;
  };
  progressPercentage: number;
  onToggleBookmark: () => void;
}

export function OverviewSection({ topic, progressPercentage, onToggleBookmark }: OverviewSectionProps) {
  const getDifficultyBadge = (diff: string) => {
    switch (diff.toLowerCase()) {
      case "easy":
        return "text-success-emerald bg-success-emerald/10 border-success-emerald/20";
      case "medium":
        return "text-yellow-500 bg-yellow-500/10 border-yellow-500/20";
      case "hard":
        return "text-primary bg-primary/10 border-primary/20";
      default:
        return "text-muted-foreground bg-muted";
    }
  };

  return (
    <motion.div
      id="overview"
      className="border border-card-border rounded-3xl p-6 lg:p-8 glass-card space-y-6 relative overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="absolute top-0 right-0 w-72 h-72 bg-primary/5 rounded-full blur-3xl pointer-events-none" />

      {/* Title & Actions Row */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-card-border/60 pb-6">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2.5">
            <span className={`text-[10px] font-extrabold uppercase px-2.5 py-1 rounded border font-mono ${getDifficultyBadge(topic.difficulty)}`}>
              {topic.difficulty} Difficulty
            </span>
            <span className="text-[10px] text-xp-gold bg-xp-gold/10 border border-xp-gold/20 px-2.5 py-1 rounded uppercase font-bold tracking-wider font-mono flex items-center gap-1">
              <Zap className="w-3 h-3 fill-xp-gold" /> +{topic.xp_reward} XP
            </span>
          </div>

          <h1 className="text-3xl lg:text-4xl font-extrabold text-white uppercase tracking-tight">
            {topic.title}
          </h1>
        </div>

        <button
          onClick={onToggleBookmark}
          className={`self-start sm:self-center px-4 py-2.5 rounded-xl border text-xs font-bold uppercase tracking-wider flex items-center gap-2 transition-all cursor-pointer ${
            topic.is_bookmarked
              ? "bg-xp-gold/10 border-xp-gold/40 text-xp-gold shadow-lg shadow-xp-gold/10"
              : "border-card-border hover:bg-white/[0.04] text-muted-foreground hover:text-white"
          }`}
        >
          {topic.is_bookmarked ? (
            <>
              <BookmarkCheck className="w-4 h-4 text-xp-gold fill-xp-gold" /> Bookmarked
            </>
          ) : (
            <>
              <Bookmark className="w-4 h-4" /> Bookmark Concept
            </>
          )}
        </button>
      </div>

      {/* Description */}
      <p className="text-sm text-muted-foreground leading-relaxed">
        {topic.description}
      </p>

      {/* Progress Bar & Status */}
      <div className="p-4 rounded-2xl border border-card-border/60 bg-[#030303]/40 space-y-2">
        <div className="flex justify-between items-center text-xs">
          <span className="text-muted-foreground font-mono font-bold uppercase tracking-widest flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-success-emerald" /> Completion Status
          </span>
          <span className="font-mono font-black text-success-emerald text-sm">{progressPercentage}%</span>
        </div>
        <div className="w-full h-2.5 bg-zinc-950 rounded-full overflow-hidden border border-card-border/30">
          <div
            className="h-full bg-gradient-to-r from-primary to-success-emerald transition-all duration-500"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
      </div>
    </motion.div>
  );
}
