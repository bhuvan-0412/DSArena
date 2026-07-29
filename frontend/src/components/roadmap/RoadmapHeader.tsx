"use client";

import React from "react";
import { motion } from "framer-motion";
import {
  Sparkles,
  CheckCircle2,
  Search,
  Filter,
  Layers
} from "lucide-react";
import { RoadmapNode } from "./LessonRow";

interface RoadmapHeaderProps {
  userName?: string;
  completedLessons: number;
  totalLessons: number;
  overallProgressPct: number;
  currentStepTitle?: string;
  nextUnlockedLesson?: { lesson: RoadmapNode; stepTitle: string; secTitle: string } | null;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  activeFilter: string;
  onFilterChange: (filter: string) => void;
  onContinueLearning: () => void;
}

export function RoadmapHeader({
  completedLessons,
  totalLessons,
  overallProgressPct,
  currentStepTitle = "Step 1: Learn the Basics",
  searchQuery,
  onSearchChange,
  activeFilter,
  onFilterChange,
}: RoadmapHeaderProps) {
  const filterOptions = [
    { key: "ALL", label: "All Lessons" },
    { key: "IN_PROGRESS", label: "In Progress" },
    { key: "COMPLETED", label: "Completed" },
    { key: "NOT_STARTED", label: "Not Started" },
  ];

  return (
    <div className="space-y-3.5">
      {/* Compact Metrics Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {/* 1. Overall Progress */}
        <div className="bg-slate-900/70 border border-slate-800/80 rounded-xl p-3 space-y-1.5 shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[10px] font-bold uppercase tracking-wider font-mono">Overall Progress</span>
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <div className="flex items-baseline justify-between">
            <div className="text-lg font-black text-white font-mono">{overallProgressPct}%</div>
            <span className="text-[10px] text-slate-400 font-mono">{completedLessons}/{totalLessons} Solved</span>
          </div>
          <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden border border-slate-800/80">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${overallProgressPct}%` }}
              transition={{ duration: 0.5 }}
              className="bg-gradient-to-r from-cyan-500 to-emerald-400 h-full rounded-full"
            />
          </div>
        </div>

        {/* 2. Lessons Mastered */}
        <div className="bg-slate-900/70 border border-slate-800/80 rounded-xl p-3 space-y-1 shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[10px] font-bold uppercase tracking-wider font-mono">Lessons Mastered</span>
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="text-lg font-black text-white font-mono">
            {completedLessons} <span className="text-xs font-normal text-slate-500">/ {totalLessons}</span>
          </div>
          <p className="text-[10px] text-emerald-400 font-medium truncate">
            {totalLessons - completedLessons} lessons remaining
          </p>
        </div>

        {/* 3. Current Focus */}
        <div className="bg-slate-900/70 border border-slate-800/80 rounded-xl p-3 space-y-1 shadow-sm">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[10px] font-bold uppercase tracking-wider font-mono">Current Focus</span>
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
          </div>
          <div className="text-xs font-bold text-white truncate">{currentStepTitle}</div>
          <p className="text-[10px] text-indigo-400 font-medium truncate">Active Learning Node</p>
        </div>
      </div>

      {/* Instant Search Bar & Filter Controls */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-2.5 bg-slate-900/80 border border-slate-800/80 rounded-xl p-2.5 shadow-sm">
        {/* Search Input */}
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search Step, Section, or Lesson..."
            className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 transition-all font-sans"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => onSearchChange("")}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] text-slate-400 hover:text-white"
            >
              Clear
            </button>
          )}
        </div>

        {/* Status Filter Buttons */}
        <div className="flex items-center space-x-1 overflow-x-auto w-full md:w-auto pb-1 md:pb-0 scrollbar-none">
          <Filter className="w-3.5 h-3.5 text-slate-500 mr-1 flex-shrink-0 hidden sm:block" />
          {filterOptions.map((opt) => (
            <button
              key={opt.key}
              type="button"
              onClick={() => onFilterChange(opt.key)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-bold transition-all whitespace-nowrap ${
                activeFilter === opt.key
                  ? "bg-cyan-500 text-slate-950 shadow-sm shadow-cyan-500/20"
                  : "bg-slate-950 text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
