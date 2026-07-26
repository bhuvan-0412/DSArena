"use client";

import React from "react";
import { Sparkles, BookOpen, CheckCircle2, FileText, HelpCircle, Brain } from "lucide-react";

export interface DefinitionItem {
  term: string;
  definition: string;
}

export interface TakeawaysData {
  summary?: string;
  important_concepts?: string[];
  definitions?: DefinitionItem[];
  interview_points?: string[];
}

interface SummaryCardProps {
  takeaways?: TakeawaysData | null;
  lessonTitle?: string;
}

export function SummaryCard({ takeaways, lessonTitle = "this lesson" }: SummaryCardProps) {
  const summaryText =
    takeaways?.summary ||
    `Essential overview and foundational principles of ${lessonTitle} in Data Structures & Algorithms.`;

  const concepts = takeaways?.important_concepts?.length
    ? takeaways.important_concepts
    : [
        `Core logic and algorithmic paradigm behind ${lessonTitle}`,
        "Analyzing time and space complexity trade-offs",
        "Key invariant properties and boundary condition handling",
      ];

  const definitions = takeaways?.definitions?.length
    ? takeaways.definitions
    : [
        {
          term: lessonTitle,
          definition: "A standard DSA concept used to structure data or solve algorithmic tasks efficiently.",
        },
        {
          term: "Time Complexity",
          definition: "Measures execution step count relative to input size N.",
        },
        {
          term: "Space Complexity",
          definition: "Measures auxiliary memory allocated during runtime execution.",
        },
      ];

  const interviewPoints = takeaways?.interview_points?.length
    ? takeaways.interview_points
    : [
        `Explain how ${lessonTitle} optimizes step count over naive brute-force approaches.`,
        "Identify common corner cases such as empty inputs, single element, or memory limits.",
        `Describe real-world software applications utilizing ${lessonTitle}.`,
      ];

  return (
    <div className="space-y-6">
      {/* Overview Banner */}
      <div className="p-5 rounded-2xl border border-cyan-500/30 bg-gradient-to-r from-cyan-950/30 via-zinc-950 to-zinc-950 space-y-2 shadow-xl">
        <div className="flex items-center gap-2 text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider">
          <Brain className="w-4 h-4" />
          <span>LESSON SUMMARY</span>
        </div>
        <p className="text-sm text-zinc-200 leading-relaxed font-medium">
          {summaryText}
        </p>
      </div>

      {/* Important Concepts */}
      <div className="rounded-2xl border border-zinc-800 bg-zinc-950/90 p-5 space-y-3 shadow-xl">
        <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-emerald-400" />
          <span>IMPORTANT CONCEPTS</span>
        </h4>
        <div className="space-y-2.5">
          {concepts.map((item, idx) => (
            <div key={idx} className="flex items-start gap-2.5 text-xs text-zinc-300 leading-relaxed">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>{item}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Definitions Grid */}
      <div className="rounded-2xl border border-zinc-800 bg-zinc-950/90 p-5 space-y-3 shadow-xl">
        <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
          <FileText className="w-4 h-4 text-purple-400" />
          <span>KEY DEFINITIONS</span>
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {definitions.map((def, idx) => (
            <div key={idx} className="p-3.5 rounded-xl border border-zinc-800/80 bg-zinc-900/40 space-y-1">
              <span className="text-xs font-bold text-purple-300 font-mono block">
                {def.term}
              </span>
              <span className="text-xs text-zinc-400 leading-relaxed block">
                {def.definition}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Interview Points */}
      <div className="rounded-2xl border border-zinc-800 bg-zinc-950/90 p-5 space-y-3 shadow-xl">
        <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
          <HelpCircle className="w-4 h-4 text-amber-400" />
          <span>CRITICAL INTERVIEW POINTS</span>
        </h4>
        <div className="space-y-2">
          {interviewPoints.map((point, idx) => (
            <div key={idx} className="p-3 rounded-xl bg-amber-950/10 border border-amber-500/20 text-amber-200 text-xs font-mono flex items-start gap-2.5">
              <Sparkles className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <span>{point}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
