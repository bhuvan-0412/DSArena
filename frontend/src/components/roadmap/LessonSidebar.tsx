"use client";

import React from "react";
import Link from "next/link";
import { CheckCircle2, Lock, PlayCircle, ListTree, ChevronRight } from "lucide-react";

export interface SidebarLessonNode {
  id: string;
  title: string;
  order: number;
  status: string; // 'COMPLETED' | 'AVAILABLE' | 'LOCKED'
  is_completed?: boolean;
  is_locked?: boolean;
  parent_id?: string | null;
  parent_title?: string | null;
}

interface LessonSidebarProps {
  currentNodeId: string;
  lessons: SidebarLessonNode[];
}

export function LessonSidebar({ currentNodeId, lessons }: LessonSidebarProps) {
  if (!lessons || lessons.length === 0) {
    return (
      <div className="p-4 rounded-2xl border border-zinc-800 bg-zinc-950/90 text-zinc-500 text-xs font-mono text-center">
        No roadmap lessons available.
      </div>
    );
  }

  // Group lessons by parent section/title
  const groupedLessons = lessons.reduce((acc, lesson) => {
    const groupKey = lesson.parent_title || "General DSA Roadmap";
    if (!acc[groupKey]) {
      acc[groupKey] = [];
    }
    acc[groupKey].push(lesson);
    return acc;
  }, {} as Record<string, SidebarLessonNode[]>);

  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-950/90 p-4 space-y-4 shadow-xl sticky top-20 max-h-[80vh] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <ListTree className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-white">
              ROADMAP LESSONS
            </h4>
            <p className="text-[10px] text-zinc-400">{lessons.length} Total Modules</p>
          </div>
        </div>
        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
          {lessons.filter((l) => l.status === "COMPLETED" || l.is_completed).length} / {lessons.length} DONE
        </span>
      </div>

      {/* Lesson List Scroll Area */}
      <div className="overflow-y-auto space-y-4 pr-1 scrollbar-thin scrollbar-thumb-zinc-800 flex-1">
        {Object.entries(groupedLessons).map(([groupTitle, groupLessons]) => (
          <div key={groupTitle} className="space-y-1.5">
            <div className="text-[10px] font-mono uppercase tracking-wider text-zinc-500 font-bold px-2 flex items-center gap-1.5">
              <ChevronRight className="w-3 h-3 text-cyan-400" />
              <span className="truncate">{groupTitle}</span>
            </div>

            <div className="space-y-1">
              {groupLessons.map((lesson) => {
                const isCurrent = lesson.id === currentNodeId;
                const isCompleted = lesson.status === "COMPLETED" || lesson.is_completed;
                const isLocked = !isCompleted && !isCurrent && (lesson.status === "LOCKED" || lesson.is_locked);

                if (isLocked) {
                  return (
                    <div
                      key={lesson.id}
                      className="w-full px-3 py-2 rounded-xl text-xs flex items-center justify-between bg-zinc-900/20 text-zinc-600 border border-transparent opacity-60 cursor-not-allowed"
                    >
                      <div className="flex items-center gap-2 truncate">
                        <Lock className="w-3.5 h-3.5 text-zinc-600 shrink-0" />
                        <span className="truncate font-medium">{lesson.title}</span>
                      </div>
                      <span className="text-[10px] font-mono text-zinc-700">🔒</span>
                    </div>
                  );
                }

                return (
                  <Link key={lesson.id} href={`/roadmap/node/${lesson.id}`}>
                    <div
                      className={`w-full px-3 py-2 rounded-xl text-xs flex items-center justify-between transition-all cursor-pointer ${
                        isCurrent
                          ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-lg font-bold"
                          : isCompleted
                          ? "bg-emerald-950/20 text-emerald-300 border border-emerald-500/20 hover:bg-emerald-950/40"
                          : "bg-zinc-900/50 text-zinc-300 border border-zinc-800/80 hover:bg-zinc-800"
                      }`}
                    >
                      <div className="flex items-center gap-2 truncate">
                        {isCurrent ? (
                          <PlayCircle className="w-3.5 h-3.5 text-cyan-400 shrink-0 animate-pulse" />
                        ) : isCompleted ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        ) : (
                          <div className="w-3.5 h-3.5 rounded-full border border-cyan-400/50 shrink-0" />
                        )}
                        <span className="truncate">{lesson.title}</span>
                      </div>

                      {isCurrent ? (
                        <span className="text-[9px] font-mono font-bold uppercase bg-cyan-400 text-zinc-950 px-1.5 py-0.5 rounded">
                          CURRENT
                        </span>
                      ) : isCompleted ? (
                        <span className="text-[10px] font-mono text-emerald-400">✅</span>
                      ) : null}
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
