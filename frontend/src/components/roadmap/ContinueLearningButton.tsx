"use client";

import React from "react";
import { ArrowRight, Lock, Sparkles } from "lucide-react";

interface ContinueLearningButtonProps {
  isUnlocked: boolean;
  onContinue: () => void;
  nextLessonTitle?: string;
}

export function ContinueLearningButton({
  isUnlocked,
  onContinue,
  nextLessonTitle,
}: ContinueLearningButtonProps) {
  if (!isUnlocked) {
    return (
      <button
        disabled
        className="w-full px-6 py-3.5 rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-500 font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 cursor-not-allowed opacity-70"
      >
        <span>NEXT LESSON LOCKED</span>
        <Lock className="w-4 h-4 text-zinc-600" />
      </button>
    );
  }

  return (
    <button
      onClick={onContinue}
      className="w-full px-6 py-3.5 rounded-xl bg-gradient-to-r from-cyan-400 via-teal-400 to-emerald-400 hover:from-cyan-300 hover:to-emerald-300 text-zinc-950 font-black text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all shadow-xl shadow-cyan-500/20 cursor-pointer group transform hover:scale-[1.01]"
    >
      <div className="flex items-center gap-2 truncate">
        <Sparkles className="w-4 h-4 text-zinc-950" />
        <span className="truncate">CONTINUE LEARNING</span>
        {nextLessonTitle && (
          <span className="text-[10px] opacity-80 truncate hidden sm:inline">
            : {nextLessonTitle}
          </span>
        )}
      </div>
      <ArrowRight className="w-4 h-4 text-zinc-950 group-hover:translate-x-1 transition-transform shrink-0" />
    </button>
  );
}
