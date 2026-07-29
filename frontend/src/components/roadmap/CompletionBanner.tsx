"use client";

import React from "react";
import { CheckCircle2, Sparkles, Trophy, ArrowRight, Loader2 } from "lucide-react";

interface CompletionBannerProps {
  isCompleted: boolean;
  completing: boolean;
  xpReward?: number;
  onMarkAsDone: () => void;
  onContinueLearning?: () => void;
  hasNextNode: boolean;
}

export function CompletionBanner({
  isCompleted,
  completing,
  xpReward = 100,
  onMarkAsDone,
  onContinueLearning,
  hasNextNode,
}: CompletionBannerProps) {
  return (
    <div
      className={`rounded-2xl border px-4 py-3.5 sm:px-6 sm:py-4 transition-all duration-300 shadow-md ${
        isCompleted
          ? "border-emerald-500/30 bg-slate-900/90 shadow-emerald-500/5"
          : "border-slate-800 bg-slate-900/80 backdrop-blur-md"
      }`}
    >
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 sm:gap-4">
        {/* XP Reward Badge Only */}
        <div className="flex items-center">
          {isCompleted ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold">
              <Sparkles className="w-4 h-4 text-emerald-400" />
              <span>+{xpReward} XP Earned</span>
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-mono font-bold">
              <Trophy className="w-4 h-4 text-amber-400" />
              <span>+{xpReward} XP Reward</span>
            </span>
          )}
        </div>

        {/* Primary Action Button */}
        <div className="w-full sm:w-auto shrink-0">
          {isCompleted ? (
            hasNextNode ? (
              <button
                type="button"
                onClick={onContinueLearning}
                className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-slate-950 font-extrabold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all shadow-md shadow-emerald-500/20 cursor-pointer transform hover:scale-[1.02] active:scale-95"
              >
                <span>Continue Learning</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <div className="w-full sm:w-auto px-4 py-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-extrabold text-xs uppercase tracking-wider flex items-center justify-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                <span>Section Completed</span>
              </div>
            )
          ) : (
            <button
              type="button"
              onClick={onMarkAsDone}
              disabled={completing}
              className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-slate-950 font-extrabold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all shadow-md shadow-emerald-500/20 cursor-pointer disabled:opacity-50 transform hover:scale-[1.02] active:scale-95"
            >
              {completing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                  <span>Saving Progress...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Mark as Done</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
