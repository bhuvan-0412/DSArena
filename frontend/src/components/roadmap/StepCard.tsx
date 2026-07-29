"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  BookOpen,
  Layers,
  ArrowRight
} from "lucide-react";
import { SectionCard } from "./SectionCard";
import { RoadmapNode } from "./LessonRow";

interface StepCardProps {
  step: RoadmapNode;
  stepIndex: number;
  isExpanded: boolean;
  expandedSections: Record<string, boolean>;
  onToggleStepExpand: (id: string, e?: React.MouseEvent) => void;
  onToggleSectionExpand: (id: string, e?: React.MouseEvent) => void;
  selectedLessonId?: string;
  currentLessonId?: string;
  searchQuery?: string;
  onSelectLesson: (lesson: RoadmapNode, stepTitle?: string, sectionTitle?: string) => void;
  onNavigateLesson?: (lesson: RoadmapNode) => void;
}

export function StepCard({
  step,
  stepIndex,
  isExpanded,
  expandedSections,
  onToggleStepExpand,
  onToggleSectionExpand,
  selectedLessonId,
  currentLessonId,
  searchQuery = "",
  onSelectLesson,
  onNavigateLesson,
}: StepCardProps) {
  const sections = step.children || [];
  
  // Calculate total lessons and completed lessons
  const totalSections = sections.length;
  let totalLessons = 0;
  let completedLessons = 0;
  let firstUnlockedLesson: RoadmapNode | null = null;
  let firstUnlockedSecTitle = "";

  sections.forEach((sec) => {
    const secLessons = sec.children || [];
    secLessons.forEach((l) => {
      totalLessons += 1;
      const isComp = l.is_completed || (l.status || "").toUpperCase() === "COMPLETED";
      if (isComp) {
        completedLessons += 1;
      } else {
        if (!firstUnlockedLesson && !l.is_locked && (l.status || "").toUpperCase() !== "LOCKED") {
          firstUnlockedLesson = l;
          firstUnlockedSecTitle = sec.title;
        }
      }
    });
  });

  const progressPercentage = totalLessons > 0 ? Math.round((completedLessons / totalLessons) * 100) : 0;

  // Determine Step Status: Not Started | In Progress | Completed
  let status: "Not Started" | "In Progress" | "Completed" = "Not Started";
  if (completedLessons === totalLessons && totalLessons > 0) {
    status = "Completed";
  } else if (completedLessons > 0 || progressPercentage > 0) {
    status = "In Progress";
  }

  const getStatusBadgeStyle = (st: typeof status) => {
    switch (st) {
      case "Completed":
        return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
      case "In Progress":
        return "text-cyan-400 bg-cyan-500/10 border-cyan-500/30";
      default:
        return "text-slate-400 bg-slate-800 border-slate-700";
    }
  };

  const handleStepContinue = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (firstUnlockedLesson) {
      onSelectLesson(firstUnlockedLesson, step.title, firstUnlockedSecTitle);
      if (onNavigateLesson) {
        onNavigateLesson(firstUnlockedLesson);
      }
    }
  };

  return (
    <div
      className={`relative rounded-xl border transition-all duration-200 overflow-hidden shadow-lg ${
        status === "Completed"
          ? "bg-slate-900/70 border-emerald-500/30 hover:border-emerald-500/50"
          : status === "In Progress"
          ? "bg-gradient-to-b from-slate-900/95 via-slate-900/80 to-slate-950/90 border-cyan-500/40 shadow-cyan-500/5"
          : "bg-slate-900/50 border-slate-800/80 hover:border-slate-700/80"
      }`}
    >
      {/* Header Container */}
      <div
        role="button"
        tabIndex={0}
        aria-expanded={isExpanded}
        aria-label={`Step ${stepIndex + 1}: ${step.title}, Status: ${status}, Progress: ${progressPercentage}%`}
        onClick={(e) => onToggleStepExpand(step.id, e)}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            onToggleStepExpand(step.id);
          }
        }}
        className="w-full p-4 sm:p-5 cursor-pointer select-none focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400"
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          {/* Left Info */}
          <div className="flex items-start space-x-3.5 min-w-0 flex-1">
            {/* Step Expand Toggle Icon */}
            <button
              type="button"
              aria-label={isExpanded ? "Collapse step" : "Expand step"}
              className="mt-0.5 w-8 h-8 rounded-lg bg-slate-800/90 border border-slate-700/70 flex items-center justify-center text-slate-300 hover:text-white transition-all flex-shrink-0"
            >
              {isExpanded ? <ChevronDown className="w-4 h-4 text-cyan-400" /> : <ChevronRight className="w-4 h-4" />}
            </button>

            <div className="space-y-1 min-w-0 flex-1">
              <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                <span className="text-[10px] font-mono font-extrabold uppercase tracking-widest text-cyan-400 bg-cyan-500/10 border border-cyan-500/20 px-2 py-0.5 rounded">
                  STEP {stepIndex + 1}
                </span>

                <span
                  className={`text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${getStatusBadgeStyle(
                    status
                  )}`}
                >
                  {status}
                </span>
              </div>

              <h2 className="text-lg sm:text-xl font-black text-white tracking-tight leading-snug">
                {step.title}
              </h2>

              {step.description && (
                <p className="text-xs sm:text-[13px] text-slate-400 line-clamp-2 leading-relaxed">
                  {step.description}
                </p>
              )}

              {/* Sub-metrics */}
              <div className="flex items-center space-x-3 text-[11px] font-medium text-slate-400 pt-1 flex-wrap gap-y-1">
                <span className="flex items-center text-slate-300">
                  <Layers className="w-3 h-3 mr-1 text-indigo-400" />
                  {totalSections} Sections
                </span>
                <span>•</span>
                <span className="flex items-center text-slate-300">
                  <BookOpen className="w-3 h-3 mr-1 text-cyan-400" />
                  {completedLessons} / {totalLessons} Lessons Mastered
                </span>
              </div>
            </div>
          </div>

          {/* Right Action / Progress */}
          <div className="flex items-center justify-between sm:justify-end gap-4 border-t sm:border-t-0 border-slate-800/80 pt-3 sm:pt-0 flex-shrink-0">
            {/* Progress Display */}
            <div className="flex flex-col items-start sm:items-end min-w-[120px]">
              <div className="flex items-center space-x-1">
                <span className="text-lg font-extrabold text-cyan-400">{progressPercentage}%</span>
                {status === "Completed" && <CheckCircle2 className="w-4 h-4 text-emerald-400 ml-1" />}
              </div>
              <div className="w-32 bg-slate-950 h-1.5 rounded-full overflow-hidden mt-1 border border-slate-800">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${progressPercentage}%` }}
                  transition={{ duration: 0.5, ease: "easeOut" }}
                  className={`h-full rounded-full ${
                    status === "Completed"
                      ? "bg-gradient-to-r from-emerald-500 to-teal-400"
                      : "bg-gradient-to-r from-cyan-500 via-indigo-500 to-emerald-400"
                  }`}
                />
              </div>
            </div>

            {/* Quick Step Continue CTA */}
            {status !== "Completed" && firstUnlockedLesson && (
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                type="button"
                onClick={handleStepContinue}
                className="flex items-center space-x-1.5 bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-bold text-xs px-3.5 py-2 rounded-xl shadow-md shadow-cyan-500/20 transition-all flex-shrink-0"
              >
                <span>Continue</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </motion.button>
            )}
          </div>
        </div>
      </div>

      {/* Sections Accordion */}
      <AnimatePresence initial={false}>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: "easeInOut" }}
            className="overflow-hidden border-t border-slate-800/80 bg-slate-950/40 p-3 sm:p-4 space-y-2.5"
          >
            {sections.length === 0 ? (
              <div className="text-xs text-slate-500 text-center py-3">No sections available in this step.</div>
            ) : (
              sections.map((sec) => (
                <SectionCard
                  key={sec.id}
                  section={sec}
                  stepTitle={step.title}
                  isExpanded={Boolean(expandedSections[sec.id])}
                  onToggleExpand={onToggleSectionExpand}
                  selectedLessonId={selectedLessonId}
                  currentLessonId={currentLessonId}
                  searchQuery={searchQuery}
                  onSelectLesson={onSelectLesson}
                  onNavigateLesson={onNavigateLesson}
                />
              ))
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
