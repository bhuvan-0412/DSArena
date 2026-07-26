"use client";

import React, { useState } from "react";
import { Target, HelpCircle, Globe, Lightbulb, CheckCircle2, ChevronDown, Sparkles } from "lucide-react";

interface LearningObjectives {
  what_you_will_learn?: string[];
  why_this_topic_matters?: string | null;
  real_world_applications?: string[];
  interview_questions?: string[];
}

interface LearningObjectivesCardProps {
  objectives?: LearningObjectives | null;
  lessonTitle?: string;
}

export function LearningObjectivesCard({ objectives, lessonTitle = "this lesson" }: LearningObjectivesCardProps) {
  const [activeTab, setActiveTab] = useState<"learn" | "why" | "realworld" | "interview">("learn");

  const learnList = objectives?.what_you_will_learn?.length
    ? objectives.what_you_will_learn
    : [
        `Understand core concepts of ${lessonTitle}`,
        "Master step-by-step logic & implementation details",
        "Analyze time and space complexities efficiently",
      ];

  const whyText =
    objectives?.why_this_topic_matters ||
    `${lessonTitle} builds fundamental problem-solving intuition essential for technical interviews and scalable system design.`;

  const realWorldList = objectives?.real_world_applications?.length
    ? objectives.real_world_applications
    : [
        "High-performance memory allocation & data processing",
        "Optimizing backend services & database indexing algorithms",
        "Designing scalable system architectures",
      ];

  const interviewList = objectives?.interview_questions?.length
    ? objectives.interview_questions
    : [
        `Explain the core mechanism of ${lessonTitle}.`,
        `How would you optimize time complexity for ${lessonTitle}?`,
        `What are the critical edge cases to consider when implementing ${lessonTitle}?`,
      ];

  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-950/90 overflow-hidden shadow-xl">
      {/* Card Header */}
      <div className="p-5 border-b border-zinc-800/80 bg-gradient-to-r from-zinc-900/80 to-zinc-950 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <span>Learning Objectives</span>
              <Sparkles className="w-4 h-4 text-cyan-400" />
            </h3>
            <p className="text-xs text-zinc-400">Essential takeaways, application & interview preparation</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-zinc-800 bg-zinc-900/40 p-1 gap-1 overflow-x-auto no-scrollbar">
        <button
          onClick={() => setActiveTab("learn")}
          className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
            activeTab === "learn"
              ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
              : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
          }`}
        >
          <Lightbulb className="w-3.5 h-3.5" />
          <span>What You Will Learn</span>
        </button>

        <button
          onClick={() => setActiveTab("why")}
          className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
            activeTab === "why"
              ? "bg-purple-500/20 text-purple-300 border border-purple-500/30"
              : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
          }`}
        >
          <Target className="w-3.5 h-3.5" />
          <span>Why It Matters</span>
        </button>

        <button
          onClick={() => setActiveTab("realworld")}
          className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
            activeTab === "realworld"
              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
              : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
          }`}
        >
          <Globe className="w-3.5 h-3.5" />
          <span>Real-World Uses</span>
        </button>

        <button
          onClick={() => setActiveTab("interview")}
          className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
            activeTab === "interview"
              ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
              : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
          }`}
        >
          <HelpCircle className="w-3.5 h-3.5" />
          <span>Interview Qs</span>
        </button>
      </div>

      {/* Tab Content */}
      <div className="p-5">
        {activeTab === "learn" && (
          <ul className="space-y-3">
            {learnList.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2.5 text-xs text-zinc-300 leading-relaxed">
                <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        )}

        {activeTab === "why" && (
          <div className="p-4 rounded-xl bg-purple-950/20 border border-purple-500/20 text-purple-200 text-xs leading-relaxed">
            <p className="font-medium">{whyText}</p>
          </div>
        )}

        {activeTab === "realworld" && (
          <ul className="space-y-3">
            {realWorldList.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2.5 text-xs text-zinc-300 leading-relaxed">
                <Globe className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        )}

        {activeTab === "interview" && (
          <div className="space-y-2.5">
            {interviewList.map((item, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-amber-950/20 border border-amber-500/20 text-amber-200 text-xs font-mono flex items-start gap-2.5"
              >
                <HelpCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
