"use client";

import React from "react";
import { Clock, BarChart2, CheckCircle2, Sparkles, BookOpen } from "lucide-react";

interface LessonHeaderProps {
  lessonNumber: number;
  title: string;
  parentTitle?: string | null;
  estimatedDuration: number;
  difficulty?: string | null;
  status: string;
}

export function LessonHeader({
  lessonNumber,
  title,
  parentTitle,
  estimatedDuration,
  difficulty = "Easy",
  status,
}: LessonHeaderProps) {
  const isCompleted = status === "COMPLETED";

  const getDifficultyColor = (diff?: string | null) => {
    switch (diff?.toLowerCase()) {
      case "hard":
        return "bg-rose-500/10 border-rose-500/30 text-rose-400";
      case "medium":
        return "bg-amber-500/10 border-amber-500/30 text-amber-400";
      case "easy":
      default:
        return "bg-emerald-500/10 border-emerald-500/30 text-emerald-400";
    }
  };

  return (
    <div className="space-y-3 pb-2 border-b border-zinc-800/80">
      {/* Top Meta Badges */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="px-2.5 py-1 rounded-md bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 font-mono text-[11px] font-bold uppercase tracking-wider flex items-center gap-1.5">
            <BookOpen className="w-3.5 h-3.5" />
            <span>LESSON {lessonNumber < 10 ? `0${lessonNumber}` : lessonNumber}</span>
          </span>

          {parentTitle && (
            <span className="text-xs font-medium text-zinc-400 flex items-center gap-1">
              <span className="text-zinc-600">/</span> {parentTitle}
            </span>
          )}
        </div>

        {isCompleted && (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>COMPLETED</span>
          </span>
        )}
      </div>

      {/* Main Lesson Title */}
      <h1 className="text-2xl sm:text-3xl md:text-4xl font-black text-white tracking-tight uppercase leading-snug">
        {title}
      </h1>

      {/* Info Stats Bar */}
      <div className="flex flex-wrap items-center gap-4 text-xs text-zinc-400 pt-1">
        <div className="flex items-center gap-1.5 bg-zinc-900/80 px-2.5 py-1 rounded-lg border border-zinc-800">
          <Clock className="w-3.5 h-3.5 text-cyan-400" />
          <span>{estimatedDuration} mins</span>
        </div>

        <div
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border font-medium ${getDifficultyColor(
            difficulty
          )}`}
        >
          <BarChart2 className="w-3.5 h-3.5" />
          <span>{difficulty || "Easy"}</span>
        </div>

        <div className="flex items-center gap-1.5 bg-zinc-900/80 px-2.5 py-1 rounded-lg border border-zinc-800">
          <CheckCircle2
            className={`w-3.5 h-3.5 ${
              isCompleted ? "text-emerald-400" : "text-zinc-500"
            }`}
          />
          <span className="capitalize">{status.toLowerCase().replace("_", " ")}</span>
        </div>
      </div>
    </div>
  );
}
