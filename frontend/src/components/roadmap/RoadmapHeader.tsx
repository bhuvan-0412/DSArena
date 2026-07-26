"use client";

import React from "react";
import { motion } from "framer-motion";
import {
  Sparkles,
  Play,
  CheckCircle2,
  Search,
  Filter,
  ArrowRight,
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
  userName = "Coder",
  completedLessons,
  totalLessons,
  overallProgressPct,
  currentStepTitle = "Step 1: Learn the Basics",
  nextUnlockedLesson,
  searchQuery,
  onSearchChange,
  activeFilter,
  onFilterChange,
  onContinueLearning,
}: RoadmapHeaderProps) {
  const isNewUser = completedLessons === 0;

  const filterOptions = [
    { key: "ALL", label: "All Lessons" },
    { key: "IN_PROGRESS", label: "In Progress" },
    { key: "UNLOCKED", label: "Unlocked" },
    { key: "COMPLETED", label: "Completed" },
    { key: "LOCKED", label: "Locked" },
  ];

  return (
    <div className="space-y-5">
      {/* Top Banner: Welcome + Hero CTA Card */}
      <div className="relative rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/60 to-slate-900 border border-slate-800 p-5 sm:p-7 overflow-hidden shadow-xl">
        {/* Glowing backdrop elements */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl -z-0 pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl -z-0 pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-5">
          {/* Left Column: Greeting & Current Focus */}
          <div className="space-y-2.5 max-w-2xl flex-1">
            <div className="inline-flex items-center space-x-2 bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-[11px] font-bold px-2.5 py-0.5 rounded-full">
              <Sparkles className="w-3 h-3" />
              <span>DSA Arena Learning Path</span>
            </div>

            <h1 className="text-xl sm:text-3xl font-black text-white tracking-tight">
              Welcome back, <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-300">{userName}</span> 👋
            </h1>

            <p className="text-xs sm:text-[13px] text-slate-300 leading-relaxed">
              Master Data Structures & Algorithms systematically with structured lessons, video tutorials, and interactive problem solving.
            </p>

            {/* Current Step Pill */}
            <div className="flex items-center space-x-2 text-xs font-medium text-slate-400 pt-0.5">
              <span className="text-slate-500 text-[11px]">Current Focus:</span>
              <span className="text-cyan-300 text-[11px] font-bold bg-cyan-950/60 border border-cyan-500/30 px-2.5 py-0.5 rounded-md truncate max-w-md">
                {currentStepTitle}
              </span>
            </div>
          </div>

          {/* Right Column: Hero CTA Card */}
          <motion.div
            whileHover={{ scale: 1.01 }}
            className="flex-shrink-0 bg-slate-900/90 border border-cyan-500/40 rounded-xl p-4 shadow-lg shadow-cyan-500/10 max-w-xs w-full space-y-3 backdrop-blur-md"
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono font-extrabold uppercase tracking-wider text-cyan-400">
                {isNewUser ? "GET STARTED" : "CONTINUE LEARNING"}
              </span>
              <span className="text-[10px] text-slate-400 font-semibold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                Next Lesson
              </span>
            </div>

            {nextUnlockedLesson ? (
              <div className="space-y-0.5">
                <h3 className="text-sm font-extrabold text-white line-clamp-1">
                  {nextUnlockedLesson.lesson.title}
                </h3>
                <p className="text-[11px] text-slate-400 truncate">
                  {nextUnlockedLesson.stepTitle} › {nextUnlockedLesson.secTitle}
                </p>
              </div>
            ) : (
              <div className="space-y-0.5">
                <h3 className="text-sm font-extrabold text-white">Striver A2Z DSA Roadmap</h3>
                <p className="text-[11px] text-slate-400">Begin your algorithmic journey</p>
              </div>
            )}

            <button
              type="button"
              onClick={onContinueLearning}
              className="w-full flex items-center justify-center space-x-2 bg-gradient-to-r from-cyan-500 via-indigo-600 to-indigo-500 hover:from-cyan-400 hover:to-indigo-400 text-white font-extrabold text-xs py-2.5 px-3 rounded-lg shadow-md shadow-cyan-500/20 transition-all group active:scale-[0.98]"
            >
              <Play className="w-3.5 h-3.5 fill-white" />
              <span>{isNewUser ? "Start Learning" : "Continue Learning"}</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </button>
          </motion.div>
        </div>
      </div>

      {/* Metrics Row: 3 Rebalanced Stat Cards (Duration removed) */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
        {/* 1. Overall Progress */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 space-y-1.5 shadow-md">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[10px] font-bold uppercase tracking-wider">Overall Progress</span>
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <div className="text-xl font-black text-white">{overallProgressPct}%</div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${overallProgressPct}%` }}
              transition={{ duration: 0.5 }}
              className="bg-gradient-to-r from-cyan-500 to-emerald-400 h-full rounded-full"
            />
          </div>
        </div>

        {/* 2. Lessons Mastered */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 space-y-1.5 shadow-md">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[10px] font-bold uppercase tracking-wider">Lessons Mastered</span>
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="text-xl font-black text-white">
            {completedLessons} <span className="text-xs font-semibold text-slate-500">/ {totalLessons}</span>
          </div>
          <p className="text-[10px] text-emerald-400 font-medium truncate">
            {totalLessons - completedLessons} lessons remaining
          </p>
        </div>

        {/* 3. Current Focus */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 space-y-1.5 shadow-md">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[10px] font-bold uppercase tracking-wider">Current Focus</span>
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
          </div>
          <div className="text-sm font-extrabold text-white truncate">{currentStepTitle}</div>
          <p className="text-[10px] text-indigo-400 font-medium truncate">Keep up the momentum!</p>
        </div>
      </div>

      {/* Instant Search Bar & Filter Controls */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-3 bg-slate-900/90 border border-slate-800/80 rounded-xl p-3 shadow-md">
        {/* Search Input */}
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search Step, Section, or Lesson..."
            className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 transition-all"
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
        <div className="flex items-center space-x-1.5 overflow-x-auto w-full md:w-auto pb-1 md:pb-0 scrollbar-none">
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
