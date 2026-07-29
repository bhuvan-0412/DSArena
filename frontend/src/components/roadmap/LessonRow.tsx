"use client";

import React from "react";
import { motion } from "framer-motion";
import { CheckCircle2, Play, Video, Sparkles, Star, Clock } from "lucide-react";

export type LessonState = "COMPLETED" | "CURRENT" | "IN_PROGRESS" | "NOT_STARTED";

export interface RoadmapNode {
  id: string;
  parent_id?: string;
  title: string;
  slug: string;
  description?: string;
  type: string; // 'step', 'section', 'topic', 'problem', 'lesson'
  order_index: number;
  estimated_time?: number;
  xp_reward: number;
  difficulty?: string;
  status?: string;

  is_completed: boolean;
  is_locked: boolean;
  progress_percentage: number;
  problems_solved: number;
  total_problems: number;
  quiz_completed: boolean;
  quiz_best_score?: number;
  revision_due_count: number;
  youtube_video_id?: string;
  youtube_url?: string;
  thumbnail_url?: string;

  children: RoadmapNode[];
}

interface LessonRowProps {
  lesson: RoadmapNode;
  stepTitle?: string;
  sectionTitle?: string;
  isCurrent?: boolean;
  isSelected?: boolean;
  searchQuery?: string;
  onSelect: (lesson: RoadmapNode, stepTitle?: string, sectionTitle?: string) => void;
  onNavigate?: (lesson: RoadmapNode) => void;
}

export function LessonRow({
  lesson,
  stepTitle,
  sectionTitle,
  isCurrent = false,
  isSelected = false,
  searchQuery = "",
  onSelect,
  onNavigate,
}: LessonRowProps) {
  // Determine visual state for Open Learning Model
  const rawStatus = (lesson.status || "").toUpperCase();
  let state: LessonState = "NOT_STARTED";

  if (lesson.is_completed || rawStatus === "COMPLETED") {
    state = "COMPLETED";
  } else if (isCurrent || rawStatus === "CURRENT") {
    state = "CURRENT";
  } else if (rawStatus === "IN_PROGRESS") {
    state = "IN_PROGRESS";
  } else {
    state = "NOT_STARTED";
  }

  // Highlight search term
  const renderHighlightedText = (text: string, query: string) => {
    if (!query || !query.trim()) return text;
    const parts = text.split(new RegExp(`(${query.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&")})`, "gi"));
    return (
      <span>
        {parts.map((part, i) =>
          part.toLowerCase() === query.toLowerCase() ? (
            <mark key={i} className="bg-cyan-500/30 text-cyan-200 px-1 py-0.5 rounded font-bold">
              {part}
            </mark>
          ) : (
            part
          )
        )}
      </span>
    );
  };

  const getDifficultyBadge = (diff?: string) => {
    const d = (diff || "Easy").toLowerCase();
    switch (d) {
      case "easy":
        return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
      case "medium":
        return "text-amber-400 bg-amber-500/10 border-amber-500/20";
      case "hard":
        return "text-rose-400 bg-rose-500/10 border-rose-500/20";
      default:
        return "text-slate-400 bg-slate-800 border-slate-700";
    }
  };

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onSelect(lesson, stepTitle, sectionTitle);
    if (onNavigate) {
      onNavigate(lesson);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onSelect(lesson, stepTitle, sectionTitle);
      if (onNavigate) {
        onNavigate(lesson);
      }
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.003, x: 2 }}
      whileTap={{ scale: 0.997 }}
      transition={{ duration: 0.15 }}
      role="button"
      tabIndex={0}
      aria-selected={isSelected}
      aria-label={`Lesson: ${lesson.title}, Status: ${state}`}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      className={`group relative flex items-center justify-between p-2.5 sm:p-3 rounded-xl border transition-all cursor-pointer select-none focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 ${
        isSelected
          ? "bg-gradient-to-r from-cyan-950/70 via-slate-900 to-indigo-950/70 border-cyan-500/60 shadow-md shadow-cyan-500/10"
          : state === "COMPLETED"
          ? "bg-slate-900/60 hover:bg-slate-800/80 border-slate-800 hover:border-emerald-500/30"
          : state === "CURRENT"
          ? "bg-cyan-950/30 hover:bg-cyan-900/40 border-cyan-500/40 shadow-sm shadow-cyan-500/5 ring-1 ring-cyan-500/20"
          : state === "IN_PROGRESS"
          ? "bg-amber-950/20 hover:bg-amber-900/30 border-amber-500/30"
          : "bg-slate-900/80 hover:bg-slate-800/90 border-slate-800/90 hover:border-slate-700 text-slate-200"
      }`}
    >
      {/* Left Icon & Title */}
      <div className="flex items-center space-x-2.5 min-w-0 pr-3 flex-1">
        {/* Status Indicator Icon */}
        <div className="flex-shrink-0">
          {state === "COMPLETED" && (
            <div className="w-7 h-7 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:scale-105 transition-transform">
              <CheckCircle2 className="w-3.5 h-3.5 fill-emerald-500/20" />
            </div>
          )}

          {state === "CURRENT" && (
            <div className="relative w-7 h-7 rounded-full bg-cyan-500/20 border border-cyan-400/50 flex items-center justify-center text-cyan-300">
              <span className="absolute inset-0 rounded-full bg-cyan-400/20 animate-ping" />
              <Star className="w-3.5 h-3.5 fill-cyan-400 text-cyan-300 relative z-10" />
            </div>
          )}

          {state === "IN_PROGRESS" && (
            <div className="w-7 h-7 rounded-full bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <Clock className="w-3.5 h-3.5" />
            </div>
          )}

          {state === "NOT_STARTED" && (
            <div className="w-7 h-7 rounded-full bg-slate-800 group-hover:bg-cyan-500/20 border border-slate-700 group-hover:border-cyan-500/40 flex items-center justify-center text-slate-400 group-hover:text-cyan-300 transition-colors">
              <Play className="w-3 h-3 ml-0.5 fill-current" />
            </div>
          )}
        </div>

        {/* Video Icon & Title */}
        <div className="flex flex-col min-w-0 flex-1">
          <div className="flex items-center space-x-2">
            <span className="text-slate-400 group-hover:text-cyan-400 transition-colors flex-shrink-0">
              <Video className="w-3.5 h-3.5" />
            </span>
            <h4
              className={`text-[13px] sm:text-sm font-semibold truncate leading-tight ${
                state === "COMPLETED"
                  ? "text-slate-300 group-hover:text-white"
                  : state === "CURRENT"
                  ? "text-cyan-200 font-bold"
                  : state === "IN_PROGRESS"
                  ? "text-amber-200 font-semibold"
                  : "text-slate-200 group-hover:text-white"
              }`}
            >
              {renderHighlightedText(lesson.title, searchQuery)}
            </h4>
          </div>

          {/* Subtitle / Step context if searching */}
          {searchQuery && (stepTitle || sectionTitle) && (
            <p className="text-[10px] text-slate-500 truncate mt-0.5">
              {stepTitle} {sectionTitle ? `› ${sectionTitle}` : ""}
            </p>
          )}
        </div>
      </div>

      {/* Right Metadata Badges */}
      <div className="flex items-center space-x-2 flex-shrink-0">
        {/* XP Badge */}
        {lesson.xp_reward > 0 && (
          <span className="hidden sm:inline-flex items-center text-[9px] font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">
            +{lesson.xp_reward} XP
          </span>
        )}

        {/* Difficulty */}
        <span
          className={`text-[9px] font-extrabold uppercase tracking-wide px-2 py-0.5 rounded border ${getDifficultyBadge(
            lesson.difficulty
          )}`}
        >
          {lesson.difficulty || "Easy"}
        </span>

        {/* State Tag */}
        {state === "COMPLETED" && (
          <span className="hidden md:inline-flex text-[9px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
            Completed
          </span>
        )}
        {state === "CURRENT" && (
          <span className="hidden md:inline-flex text-[9px] font-bold text-cyan-400 bg-cyan-500/10 border border-cyan-500/20 px-2 py-0.5 rounded">
            Recommended Next
          </span>
        )}
        {state === "IN_PROGRESS" && (
          <span className="hidden md:inline-flex text-[9px] font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">
            In Progress
          </span>
        )}
      </div>
    </motion.div>
  );
}
