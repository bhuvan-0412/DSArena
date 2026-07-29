"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ChevronDown,
  ChevronsDown,
  ChevronsUp,
  Target,
  RotateCcw,
  History
} from "lucide-react";

interface RecentlyViewedLesson {
  id: string;
  title: string;
  stepTitle?: string;
}

interface RoadmapQuickActionsProps {
  onExpandAll: () => void;
  onCollapseAll: () => void;
  onJumpToCurrentStep: () => void;
  onResumeLastLesson: () => void;
  recentlyViewed?: RecentlyViewedLesson[];
  onSelectRecentLesson?: (id: string) => void;
}

export function RoadmapQuickActions({
  onExpandAll,
  onCollapseAll,
  onJumpToCurrentStep,
  onResumeLastLesson,
  recentlyViewed = [],
  onSelectRecentLesson,
}: RoadmapQuickActionsProps) {
  const [showRecentDropdown, setShowRecentDropdown] = useState(false);

  return (
    <div className="flex flex-wrap items-center justify-between gap-2.5 bg-slate-900/60 border border-slate-800/80 rounded-xl p-2.5 shadow-sm">
      {/* Left Quick Navigation Buttons */}
      <div className="flex items-center space-x-2 flex-wrap gap-y-2">
        {/* Resume Last Lesson */}
        <button
          type="button"
          onClick={onResumeLastLesson}
          className="flex items-center space-x-1.5 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-xs font-bold px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Resume Last Lesson</span>
        </button>

        {/* Jump to Current Step */}
        <button
          type="button"
          onClick={onJumpToCurrentStep}
          className="flex items-center space-x-1.5 bg-slate-800/90 hover:bg-slate-800 text-slate-200 border border-slate-700/80 text-xs font-bold px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
        >
          <Target className="w-3.5 h-3.5 text-indigo-400" />
          <span>Jump to Current Step</span>
        </button>

        {/* Recently Viewed Dropdown */}
        {recentlyViewed.length > 0 && (
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowRecentDropdown(!showRecentDropdown)}
              className="flex items-center space-x-1.5 bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs font-medium px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
            >
              <History className="w-3.5 h-3.5 text-amber-400" />
              <span>Recently Viewed ({recentlyViewed.length})</span>
              <ChevronDown className="w-3 h-3 ml-0.5" />
            </button>

            <AnimatePresence>
              {showRecentDropdown && (
                <motion.div
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 5 }}
                  className="absolute left-0 top-full mt-2 w-64 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl z-50 p-2 space-y-1"
                >
                  <div className="text-[10px] font-bold text-slate-500 uppercase px-2 py-1">
                    Recent Activity
                  </div>
                  {recentlyViewed.map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => {
                        if (onSelectRecentLesson) onSelectRecentLesson(item.id);
                        setShowRecentDropdown(false);
                      }}
                      className="w-full text-left px-2.5 py-1.5 rounded-lg hover:bg-slate-800 text-xs text-slate-200 transition-colors truncate cursor-pointer"
                    >
                      <div className="font-semibold truncate">{item.title}</div>
                      {item.stepTitle && (
                        <div className="text-[10px] text-slate-500 truncate">{item.stepTitle}</div>
                      )}
                    </button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Right Expand / Collapse Controls */}
      <div className="flex items-center space-x-2">
        <button
          type="button"
          onClick={onExpandAll}
          className="flex items-center space-x-1 text-xs font-semibold text-slate-400 hover:text-white bg-slate-950 hover:bg-slate-800 border border-slate-800/80 px-2.5 py-1.5 rounded-lg transition-colors cursor-pointer"
        >
          <ChevronsDown className="w-3.5 h-3.5 text-cyan-400" />
          <span>Expand All</span>
        </button>

        <button
          type="button"
          onClick={onCollapseAll}
          className="flex items-center space-x-1 text-xs font-semibold text-slate-400 hover:text-white bg-slate-950 hover:bg-slate-800 border border-slate-800/80 px-2.5 py-1.5 rounded-lg transition-colors cursor-pointer"
        >
          <ChevronsUp className="w-3.5 h-3.5 text-amber-400" />
          <span>Collapse All</span>
        </button>
      </div>
    </div>
  );
}
