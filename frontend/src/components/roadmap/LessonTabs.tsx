"use client";

import React, { useState } from "react";
import { Tv, FileText, BookOpen, ChevronDown } from "lucide-react";

export type LessonTabType = "learn" | "notes" | "resources";

interface LessonTabsProps {
  activeTab: LessonTabType;
  onTabChange: (tab: LessonTabType) => void;
  learnContent: React.ReactNode;
  notesContent: React.ReactNode;
  resourcesContent: React.ReactNode;
}

export function LessonTabs({
  activeTab,
  onTabChange,
  learnContent,
  notesContent,
  resourcesContent,
}: LessonTabsProps) {
  // State for mobile accordion expand/collapse
  const [expandedMobile, setExpandedMobile] = useState<Record<LessonTabType, boolean>>({
    learn: true,
    notes: false,
    resources: false,
  });

  const toggleMobileTab = (tab: LessonTabType) => {
    setExpandedMobile((prev) => ({ ...prev, [tab]: !prev[tab] }));
  };

  const tabsConfig: { id: LessonTabType; label: string; icon: React.ReactNode }[] = [
    { id: "learn", label: "Learn", icon: <Tv className="w-4 h-4" /> },
    { id: "notes", label: "Notes", icon: <FileText className="w-4 h-4" /> },
    { id: "resources", label: "Resources", icon: <BookOpen className="w-4 h-4" /> },
  ];

  const renderContentForTab = (tabId: LessonTabType) => {
    switch (tabId) {
      case "learn":
        return learnContent;
      case "notes":
        return notesContent;
      case "resources":
        return resourcesContent;
      default:
        return learnContent;
    }
  };

  return (
    <div className="space-y-6">
      {/* DESKTOP TAB BAR (hidden on small mobile screens) */}
      <div className="hidden md:flex items-center gap-1.5 border-b border-zinc-800 bg-zinc-950/80 p-1.5 rounded-2xl border overflow-x-auto shadow-xl">
        {tabsConfig.map((t) => {
          const isActive = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => onTabChange(t.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs uppercase tracking-wider transition-all whitespace-nowrap cursor-pointer ${
                isActive
                  ? "bg-gradient-to-r from-cyan-500/20 to-teal-500/20 text-cyan-300 border border-cyan-500/40 shadow-lg"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60"
              }`}
            >
              {t.icon}
              <span>{t.label}</span>
            </button>
          );
        })}
      </div>

      {/* DESKTOP TAB CONTENT CONTAINER */}
      <div className="hidden md:block transition-all duration-300">
        {renderContentForTab(activeTab)}
      </div>

      {/* MOBILE RESPONSIVE ACCORDION SECTIONS (visible on < md screens) */}
      <div className="md:hidden space-y-3">
        {tabsConfig.map((t) => {
          const isOpen = expandedMobile[t.id];
          return (
            <div
              key={t.id}
              className="rounded-2xl border border-zinc-800 bg-zinc-950/90 overflow-hidden shadow-xl"
            >
              <button
                type="button"
                onClick={() => toggleMobileTab(t.id)}
                className="w-full p-4 bg-zinc-900/60 flex items-center justify-between text-left font-bold text-xs uppercase text-white tracking-wider"
              >
                <div className="flex items-center gap-2.5 text-cyan-400">
                  {t.icon}
                  <span className="text-zinc-100">{t.label}</span>
                </div>
                <ChevronDown
                  className={`w-4 h-4 text-zinc-400 transition-transform duration-300 ${
                    isOpen ? "rotate-180 text-cyan-400" : ""
                  }`}
                />
              </button>

              {isOpen && <div className="p-4 border-t border-zinc-800">{renderContentForTab(t.id)}</div>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
