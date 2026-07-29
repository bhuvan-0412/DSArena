"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ChevronRight, Layers, CheckCircle2 } from "lucide-react";
import { LessonRow, RoadmapNode } from "./LessonRow";

interface SectionCardProps {
  section: RoadmapNode;
  stepTitle: string;
  isExpanded: boolean;
  onToggleExpand: (id: string, e?: React.MouseEvent) => void;
  selectedLessonId?: string;
  currentLessonId?: string;
  searchQuery?: string;
  onSelectLesson: (lesson: RoadmapNode, stepTitle?: string, sectionTitle?: string) => void;
  onNavigateLesson?: (lesson: RoadmapNode) => void;
}

export function SectionCard({
  section,
  stepTitle,
  isExpanded,
  onToggleExpand,
  selectedLessonId,
  currentLessonId,
  searchQuery = "",
  onSelectLesson,
  onNavigateLesson,
}: SectionCardProps) {
  const lessons = section.children || [];
  const totalLessons = lessons.length;

  // Calculate completed lessons
  const completedCount = lessons.filter(
    (l) => l.is_completed || (l.status || "").toUpperCase() === "COMPLETED"
  ).length;

  const progressPct = totalLessons > 0 ? Math.round((completedCount / totalLessons) * 100) : 0;
  const isFullyCompleted = totalLessons > 0 && completedCount === totalLessons;

  return (
    <div className="border border-slate-800/80 bg-slate-950/40 rounded-xl overflow-hidden shadow-sm transition-colors hover:border-slate-700/80">
      {/* Section Header */}
      <div
        role="button"
        tabIndex={0}
        aria-expanded={isExpanded}
        aria-label={`Section: ${section.title}, Progress: ${progressPct}%`}
        onClick={(e) => onToggleExpand(section.id, e)}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            onToggleExpand(section.id);
          }
        }}
        className="w-full flex items-center justify-between p-3 sm:p-3.5 bg-slate-900/70 hover:bg-slate-900/90 transition-colors cursor-pointer select-none focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400"
      >
        {/* Left Section Info */}
        <div className="flex items-center space-x-2.5 min-w-0 pr-3 flex-1">
          <button
            type="button"
            aria-label={isExpanded ? "Collapse section" : "Expand section"}
            className="w-6 h-6 rounded-lg bg-slate-800/80 border border-slate-700/60 flex items-center justify-center text-slate-400 hover:text-white transition-transform flex-shrink-0"
          >
            {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
          </button>

          <div className="flex items-center space-x-2.5 min-w-0 flex-1">
            <Layers className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />
            <h3 className="text-[13px] sm:text-sm font-bold text-slate-100 truncate tracking-tight">
              {section.title}
            </h3>

            {isFullyCompleted ? (
              <span className="inline-flex items-center text-[9px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full flex-shrink-0">
                <CheckCircle2 className="w-2.5 h-2.5 mr-1" /> Done
              </span>
            ) : (
              <span className="text-[11px] text-slate-400 flex-shrink-0">
                (<strong className="text-slate-200">{completedCount}</strong>/{totalLessons} Lessons)
              </span>
            )}
          </div>
        </div>

        {/* Right Progress Bar & % */}
        <div className="flex items-center space-x-3 flex-shrink-0">
          <div className="hidden sm:flex items-center space-x-2">
            <div className="w-28 bg-slate-800 h-1.5 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${progressPct}%` }}
                transition={{ duration: 0.4, ease: "easeOut" }}
                className={`h-full rounded-full ${
                  isFullyCompleted
                    ? "bg-emerald-400"
                    : progressPct > 0
                    ? "bg-gradient-to-r from-indigo-500 to-cyan-400"
                    : "bg-slate-700"
                }`}
              />
            </div>
            <span className="text-[11px] font-bold text-slate-300 w-8 text-right">{progressPct}%</span>
          </div>
        </div>
      </div>

      {/* Expanded Lessons List */}
      <AnimatePresence initial={false}>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: "easeInOut" }}
            className="overflow-hidden border-t border-slate-800/80 bg-slate-950/60 p-2.5 space-y-1.5"
          >
            {lessons.length === 0 ? (
              <div className="text-xs text-slate-500 py-2 text-center italic">
                No lessons available in this section.
              </div>
            ) : (
              lessons.map((lesson) => (
                <LessonRow
                  key={lesson.id}
                  lesson={lesson}
                  stepTitle={stepTitle}
                  sectionTitle={section.title}
                  isSelected={selectedLessonId === lesson.id}
                  isCurrent={currentLessonId === lesson.id}
                  searchQuery={searchQuery}
                  onSelect={onSelectLesson}
                  onNavigate={onNavigateLesson}
                />
              ))
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
