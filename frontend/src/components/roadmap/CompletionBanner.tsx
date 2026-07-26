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
      className={`rounded-2xl border p-6 shadow-2xl transition-all duration-500 ${
        isCompleted
          ? "border-emerald-500/40 bg-gradient-to-r from-emerald-950/40 via-zinc-950 to-teal-950/40"
          : "border-zinc-800 bg-zinc-950/90"
      }`}
    >
      <div className="flex flex-col md:flex-row items-center justify-between gap-5 text-center md:text-left">
        {/* Banner Text & Badges */}
        <div className="space-y-2 max-w-xl">
          <div className="flex items-center justify-center md:justify-start gap-2">
            {isCompleted ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-mono font-bold tracking-wider animate-bounce">
                <Sparkles className="w-3.5 h-3.5" />
                <span>LESSON COMPLETE!</span>
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-mono font-bold tracking-wider">
                <Trophy className="w-3.5 h-3.5 text-amber-400" />
                <span>REWARD: +{xpReward} XP</span>
              </span>
            )}
          </div>

          <h3 className="text-xl font-black text-white uppercase tracking-tight">
            {isCompleted ? "Great Work! Lesson Mastered." : "Ready to complete this lesson?"}
          </h3>

          <p className="text-xs text-zinc-400 leading-relaxed">
            {isCompleted
              ? "Your progress has been recorded, XP awarded, and the next lesson in your DSA roadmap has been unlocked!"
              : "Click 'Mark as Done' after reviewing the video & learning objectives to verify completion and unlock your next lesson."}
          </p>
        </div>

        {/* Action Button */}
        <div className="w-full md:w-auto flex flex-col items-center gap-3 shrink-0">
          {isCompleted ? (
            hasNextNode ? (
              <button
                onClick={onContinueLearning}
                className="w-full md:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-emerald-400 to-teal-400 hover:from-emerald-300 hover:to-teal-300 text-zinc-950 font-black text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all shadow-xl shadow-emerald-500/25 cursor-pointer transform hover:scale-[1.02]"
              >
                <span>CONTINUE LEARNING</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <div className="px-6 py-3 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 font-bold text-xs uppercase tracking-wider flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                <span>SECTION COMPLETED</span>
              </div>
            )
          ) : (
            <button
              onClick={onMarkAsDone}
              disabled={completing}
              className="w-full md:w-auto px-8 py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-zinc-950 font-black text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all shadow-xl shadow-emerald-500/20 cursor-pointer disabled:opacity-50"
            >
              {completing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>SAVING PROGRESS...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  <span>MARK AS DONE</span>
                </>
              )}
            </button>
          )}

          {isCompleted && (
            <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
              <Trophy className="w-3 h-3 text-amber-400" />
              <span>+{xpReward} XP Earned</span>
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
