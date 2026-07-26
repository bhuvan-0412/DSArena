"use client";

import React from "react";
import Link from "next/link";
import { CheckCircle2, Lock, ArrowRight, Layers } from "lucide-react";

export interface PrerequisiteItem {
  id: string;
  title: string;
  status: string; // 'COMPLETED' | 'AVAILABLE' | 'LOCKED'
  is_completed: boolean;
  is_locked: boolean;
}

interface PrerequisiteCardProps {
  prerequisites?: PrerequisiteItem[] | null;
}

export function PrerequisiteCard({ prerequisites }: PrerequisiteCardProps) {
  if (!prerequisites || prerequisites.length === 0) {
    return (
      <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-950/60 text-zinc-400 text-xs flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-emerald-400" />
          <span className="font-medium text-zinc-300">Prerequisites:</span>
          <span>No prior lessons required. Ready to learn!</span>
        </div>
        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-mono font-bold uppercase">
          READY
        </span>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-950/90 p-5 space-y-3 shadow-xl">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <span>PREREQUISITE LESSONS</span>
        </h4>
        <span className="text-[11px] font-mono text-zinc-500">
          {prerequisites.filter((p) => p.is_completed).length}/{prerequisites.length} Satisfied
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {prerequisites.map((item) => {
          const isCompleted = item.is_completed || item.status === "COMPLETED";
          const isLocked = item.is_locked || item.status === "LOCKED";

          if (isLocked) {
            return (
              <div
                key={item.id}
                className="p-3 rounded-xl border border-zinc-800/80 bg-zinc-900/30 text-zinc-500 text-xs flex items-center justify-between cursor-not-allowed opacity-75"
              >
                <div className="flex items-center gap-2 truncate">
                  <Lock className="w-3.5 h-3.5 text-zinc-600 shrink-0" />
                  <span className="truncate font-medium">{item.title}</span>
                </div>
                <span className="text-[10px] font-mono uppercase text-zinc-600 font-bold px-1.5 py-0.5 rounded bg-zinc-800">
                  LOCKED
                </span>
              </div>
            );
          }

          return (
            <Link key={item.id} href={`/roadmap/node/${item.id}`}>
              <div
                className={`p-3 rounded-xl border text-xs flex items-center justify-between transition-all cursor-pointer group ${
                  isCompleted
                    ? "border-emerald-500/30 bg-emerald-950/10 hover:bg-emerald-950/20 text-emerald-300"
                    : "border-cyan-500/30 bg-cyan-950/10 hover:bg-cyan-950/20 text-cyan-300"
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  {isCompleted ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  ) : (
                    <span className="w-2 h-2 rounded-full bg-cyan-400 shrink-0 animate-pulse" />
                  )}
                  <span className="truncate font-medium group-hover:underline">
                    {item.title}
                  </span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-zinc-500 group-hover:text-white transition-transform group-hover:translate-x-0.5" />
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
