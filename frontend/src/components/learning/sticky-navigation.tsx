"use client";

import { BookOpen, Video, Lightbulb, Play, Edit3, CheckSquare, Code2, Award } from "lucide-react";

interface StickyNavigationProps {
  activeSection: string;
  onSelectSection: (sectionId: string) => void;
  progressPercentage: number;
}

export function StickyNavigation({ activeSection, onSelectSection, progressPercentage }: StickyNavigationProps) {
  const sections = [
    { id: "overview", label: "Overview", icon: BookOpen },
    { id: "resources", label: "Resources", icon: Video },
    { id: "key-concepts", label: "Key Concepts", icon: Lightbulb },
    { id: "visual-learning", label: "Visual Learning", icon: Play },
    { id: "notes", label: "Notes", icon: Edit3 },
    { id: "checklist", label: "Checklist", icon: CheckSquare },
    { id: "quiz", label: "Quiz", icon: Award },
    { id: "problems", label: "Problems", icon: Code2 },
  ];

  return (
    <div className="sticky top-4 z-40 bg-[#050508]/90 backdrop-blur-md border border-card-border/80 rounded-2xl p-2 shadow-xl shadow-black/40">
      <div className="flex items-center justify-between gap-2 overflow-x-auto no-scrollbar">
        <div className="flex items-center gap-1.5 min-w-max">
          {sections.map((sec) => {
            const Icon = sec.icon;
            const isActive = activeSection === sec.id;
            return (
              <button
                key={sec.id}
                onClick={() => onSelectSection(sec.id)}
                className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-bold transition-all duration-200 cursor-pointer ${
                  isActive
                    ? "bg-primary text-white shadow-md shadow-primary/20"
                    : "text-muted-foreground hover:text-white hover:bg-white/[0.04]"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{sec.label}</span>
              </button>
            );
          })}
        </div>

        {/* Progress Bar indicator in sticky nav */}
        <div className="hidden md:flex items-center gap-3 shrink-0 border-l border-card-border/60 pl-3 pr-2">
          <div className="flex flex-col items-end">
            <span className="text-[9px] uppercase font-mono font-bold text-muted-foreground">Topic Progress</span>
            <span className="text-xs font-mono font-extrabold text-success-emerald">{progressPercentage}%</span>
          </div>
          <div className="w-16 h-2 bg-zinc-900 rounded-full overflow-hidden border border-card-border/40">
            <div
              className="h-full bg-success-emerald transition-all duration-500"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
