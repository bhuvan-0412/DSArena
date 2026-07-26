"use client";

import React from "react";
import { AlertTriangle, CheckCircle2, Bookmark, Lightbulb, ShieldAlert } from "lucide-react";

export interface TipsData {
  common_mistakes?: string[];
  best_practices?: string[];
  things_to_remember?: string[];
  interview_tips?: string[];
}

interface TipCardProps {
  tips?: TipsData | null;
  lessonTitle?: string;
}

export function TipCard({ tips, lessonTitle = "this topic" }: TipCardProps) {
  const mistakes = tips?.common_mistakes?.length
    ? tips.common_mistakes
    : [
        `Off-by-one errors during loop indexing or pointer bounds in ${lessonTitle}`,
        "Forgetting edge cases like empty inputs, duplicate values, or integer overflow",
        "Unnecessary re-allocations inside hot loops reducing overall execution speed",
      ];

  const practices = tips?.best_practices?.length
    ? tips.best_practices
    : [
        "Always validate inputs and check boundary edge cases first",
        "Use descriptive variable names for readability during live coding interviews",
        "Manually dry-run logic on sample inputs before finalizing your solution",
      ];

  const rememberList = tips?.things_to_remember?.length
    ? tips.things_to_remember
    : [
        "Analyze time & space requirements before writing complete code",
        "Keep pointer boundaries strictly in-range to prevent memory faults",
        "Prefer iterative or tail-recursive patterns when call stack depth is large",
      ];

  const interviewTips = tips?.interview_tips?.length
    ? tips.interview_tips
    : [
        "Communicate your thought process out loud clearly to your interviewer",
        "Start with a simple working approach before optimizing complexity",
        "Proactively write edge case tests to prove solution correctness",
      ];

  return (
    <div className="space-y-6">
      {/* Common Mistakes */}
      <div className="rounded-2xl border border-rose-500/30 bg-gradient-to-r from-rose-950/20 via-zinc-950 to-zinc-950 p-5 space-y-3 shadow-xl">
        <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-rose-400 flex items-center gap-2">
          <ShieldAlert className="w-4 h-4" />
          <span>COMMON MISTAKES TO AVOID</span>
        </h4>
        <div className="space-y-2.5">
          {mistakes.map((item, idx) => (
            <div key={idx} className="flex items-start gap-2.5 text-xs text-rose-200/90 leading-relaxed">
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <span>{item}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Best Practices */}
      <div className="rounded-2xl border border-emerald-500/30 bg-gradient-to-r from-emerald-950/20 via-zinc-950 to-zinc-950 p-5 space-y-3 shadow-xl">
        <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" />
          <span>BEST PRACTICES</span>
        </h4>
        <div className="space-y-2.5">
          {practices.map((item, idx) => (
            <div key={idx} className="flex items-start gap-2.5 text-xs text-emerald-200/90 leading-relaxed">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>{item}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Things to Remember */}
      <div className="rounded-2xl border border-zinc-800 bg-zinc-950/90 p-5 space-y-3 shadow-xl">
        <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-2">
          <Bookmark className="w-4 h-4" />
          <span>THINGS TO REMEMBER</span>
        </h4>
        <div className="space-y-2.5">
          {rememberList.map((item, idx) => (
            <div key={idx} className="p-3 rounded-xl bg-cyan-950/20 border border-cyan-500/20 text-xs text-cyan-200 font-mono">
              <span>💡 {item}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Interview Tips */}
      <div className="rounded-2xl border border-amber-500/30 bg-gradient-to-r from-amber-950/20 via-zinc-950 to-zinc-950 p-5 space-y-3 shadow-xl">
        <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-amber-400 flex items-center gap-2">
          <Lightbulb className="w-4 h-4" />
          <span>INTERVIEW PRO TIPS</span>
        </h4>
        <div className="space-y-2.5">
          {interviewTips.map((item, idx) => (
            <div key={idx} className="p-3 rounded-xl bg-amber-950/30 border border-amber-500/30 text-amber-200 text-xs font-mono">
              <span>🎯 {item}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
