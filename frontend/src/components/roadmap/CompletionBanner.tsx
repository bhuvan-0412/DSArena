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
      className={`rounded-2xl border p-5 sm:p-6 transition-all duration-300 shadow-md ${
        isCompleted
          ? "border-emerald-500/30 bg-slate-900/90 shadow-emerald-500/5"
          : "border-slate-800 bg-slate-900/80 backdrop-blur-md"
      }`}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-5">
        {/* Left Column: XP Badge, Title & Natural Body Text */}
        <div className="space-y-2 max-w-xl">
          <div className="flex items-center gap-2">
            {isCompleted ? (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Lesson Completed</span>
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-mono font-bold">
                <Trophy className="w-3.5 h-3.5 text-amber-400" />
                <span>+{xpReward} XP Reward</span>
              </span>
            )}
          </div>

          <h3 className="text-lg font-bold text-white tracking-tight leading-snug">
            {isCompleted ? "Great work! You've mastered this lesson." : "Ready to complete this lesson?"}
          </h3>

          <p className="text-xs text-slate-400 leading-relaxed max-w-lg">
            {isCompleted
              ? "Your progress has been saved and your XP has been recorded. Continue to your next lesson on the roadmap."
              : "Review the lesson concepts and click mark as done to record your progress and unlock the next lesson."}
          </p>
        </div>

        {/* Right Column: CTA Button */}
        <div className="shrink-0 pt-1 sm:pt-0">
          {isCompleted ? (
            hasNextNode ? (
              <button
                type="button"
                onClick={onContinueLearning}
                className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all shadow-md shadow-emerald-500/20 cursor-pointer active:scale-95"
              >
                <span>Continue Learning</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <div className="w-full sm:w-auto px-4 py-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                <span>Section Complete</span>
              </div>
            )
          ) : (
            <button
              type="button"
              onClick={onMarkAsDone}
              disabled={completing}
              className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all shadow-md shadow-emerald-500/20 cursor-pointer disabled:opacity-50 active:scale-95"
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
