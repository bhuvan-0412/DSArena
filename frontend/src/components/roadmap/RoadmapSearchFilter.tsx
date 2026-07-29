import React from "react";
import { Search, Filter, X, CheckCircle2, Clock, Play, Lock } from "lucide-react";

export type FilterStatus = "ALL" | "COMPLETED" | "IN_PROGRESS" | "NOT_STARTED" | "LOCKED" | "UNLOCKED";

interface RoadmapSearchFilterProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  activeFilter: FilterStatus;
  onFilterChange: (filter: FilterStatus) => void;
}

export function RoadmapSearchFilter({
  searchQuery,
  onSearchChange,
  activeFilter,
  onFilterChange,
}: RoadmapSearchFilterProps) {
  const filters: { id: FilterStatus; label: string; icon?: React.ReactNode }[] = [
    { id: "ALL", label: "All Lessons" },
    { id: "COMPLETED", label: "Completed", icon: <CheckCircle2 className="w-3 h-3 text-emerald-400" /> },
    { id: "IN_PROGRESS", label: "In Progress", icon: <Clock className="w-3 h-3 text-amber-400" /> },
    { id: "NOT_STARTED", label: "Not Started", icon: <Play className="w-3 h-3 text-cyan-400" /> },
    { id: "UNLOCKED", label: "Unlocked" },
    { id: "LOCKED", label: "Locked", icon: <Lock className="w-3 h-3 text-slate-500" /> },
  ];

  return (
    <div className="bg-slate-900/80 border border-slate-800/80 rounded-xl p-4 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 shadow-lg shadow-black/20">
      {/* Search Input */}
      <div className="relative flex-1 min-w-[260px]">
        <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          placeholder="Search steps, sections, topics, or lessons..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-10 pr-9 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-all"
        />
        {searchQuery && (
          <button
            onClick={() => onSearchChange("")}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-200 transition-colors"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Filter Pills */}
      <div className="flex items-center flex-wrap gap-1.5 overflow-x-auto py-1">
        <span className="text-[11px] font-semibold uppercase text-slate-500 mr-1 flex items-center space-x-1">
          <Filter className="w-3 h-3 text-slate-400" />
          <span>Filter:</span>
        </span>
        {filters.map((f) => {
          const isActive = activeFilter === f.id;

          return (
            <button
              key={f.id}
              onClick={() => onFilterChange(f.id)}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                isActive
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-500/10"
                  : "bg-slate-950/80 border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800"
              }`}
            >
              {f.icon}
              <span>{f.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
