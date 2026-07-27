"use client";

import React from "react";
import Link from "next/link";
import { ArrowLeft, Lock, CheckCircle2, Sparkles } from "lucide-react";

export interface NavigationNode {
  id: string;
  title: string;
  order?: number;
  status?: string;
  is_locked?: boolean;
}

interface LessonNavigationProps {
  previousNode?: NavigationNode | null;
  currentNode: NavigationNode;
  nextNode?: NavigationNode | null;
  isCompleted: boolean;
  onNavigateNext?: () => void;
}

export function LessonNavigation({
  previousNode,
  currentNode,
  nextNode,
  isCompleted,
  onNavigateNext,
}: LessonNavigationProps) {
  return (
    <div className="p-4 rounded-2xl border border-zinc-800 bg-zinc-950/90 flex flex-col sm:flex-row items-center justify-between gap-3 shadow-xl">
      {/* Previous Lesson Button */}
      {previousNode ? (
        <Link href={`/roadmap/node/${previousNode.id}`} className="w-full sm:w-auto">
          <button className="w-full sm:w-auto px-4 py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-300 font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all group">
            <ArrowLeft className="w-4 h-4 text-zinc-400 group-hover:-translate-x-0.5 transition-transform" />
            <div className="text-left max-w-[150px] truncate">
              <span className="block text-[10px] text-zinc-500 font-mono">PREVIOUS LESSON</span>
              <span className="truncate block text-xs">{previousNode.title}</span>
            </div>
          </button>
        </Link>
      ) : (
        <button
          disabled
          className="w-full sm:w-auto px-4 py-2.5 rounded-xl bg-zinc-900/40 border border-zinc-800/40 text-zinc-600 font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 cursor-not-allowed opacity-50"
        >
          <ArrowLeft className="w-4 h-4 text-zinc-600" />
          <span>START OF ROADMAP</span>
        </button>
      )}

      {/* Current Lesson Badge */}
      <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-900 border border-zinc-800 text-xs font-mono text-zinc-400">
        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
        <span className="font-bold text-white max-w-[200px] truncate">{currentNode.title}</span>
      </div>

      {/* Next Lesson / Continue Learning Button */}
      {nextNode ? (
        isCompleted ? (
          <button
            onClick={onNavigateNext}
            className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-400 to-teal-400 hover:from-emerald-300 hover:to-teal-300 text-zinc-950 font-black text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all shadow-lg shadow-emerald-500/20 cursor-pointer"
          >
            <span>CONTINUE LEARNING</span>
            <Sparkles className="w-4 h-4" />
          </button>
        ) : (
          <button
            disabled
            className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-500 font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 cursor-not-allowed opacity-75"
          >
            <span>NEXT LESSON</span>
            <Lock className="w-3.5 h-3.5 text-zinc-600" />
          </button>
        )
      ) : (
        <div className="px-4 py-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-xs uppercase tracking-wider flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" />
          <span>ROADMAP COMPLETED!</span>
        </div>
      )}
    </div>
  );
}
