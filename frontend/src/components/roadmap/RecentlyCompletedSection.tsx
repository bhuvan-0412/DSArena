"use client";

import React from "react";
import { CheckCircle2, Trophy, Video } from "lucide-react";
import { RoadmapNode } from "./LessonRow";

interface RecentlyCompletedProps {
  completedLessons: RoadmapNode[];
  onSelectLesson?: (lesson: RoadmapNode) => void;
}

export function RecentlyCompletedSection({ completedLessons, onSelectLesson }: RecentlyCompletedProps) {
  if (completedLessons.length === 0) return null;

  // Take last 4 completed lessons
  const recent = completedLessons.slice(-4).reverse();

  return (
    <div className="space-y-3 pt-3 border-t border-slate-800/80">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <h2 className="text-base font-extrabold text-white tracking-tight">Recently Completed</h2>
        </div>
        <span className="text-xs font-semibold text-slate-400">
          Total Mastered: {completedLessons.length}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {recent.map((lesson) => (
          <div
            key={lesson.id}
            onClick={() => onSelectLesson && onSelectLesson(lesson)}
            className="group cursor-pointer bg-slate-900/60 hover:bg-slate-900 border border-slate-800 hover:border-emerald-500/40 rounded-xl p-3 space-y-1.5 transition-all shadow-sm"
          >
            <div className="flex items-center justify-between text-emerald-400">
              <span className="text-[9px] font-mono font-bold uppercase tracking-wider bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.5 rounded">
                COMPLETED
              </span>
              <Trophy className="w-3.5 h-3.5" />
            </div>

            <h4 className="text-xs font-bold text-slate-200 group-hover:text-white line-clamp-1 truncate">
              {lesson.title}
            </h4>

            <div className="flex items-center justify-between text-[10px] text-slate-400">
              <span className="flex items-center">
                <Video className="w-3 h-3 mr-1 text-slate-500" />
                Lesson
              </span>
              {lesson.xp_reward > 0 && (
                <span className="font-bold text-amber-400">+{lesson.xp_reward} XP</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
