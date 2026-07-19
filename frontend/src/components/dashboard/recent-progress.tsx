"use client";

import { Calendar, CheckCircle2, RefreshCw, Flame, ArrowRight } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

export default function RecentProgress() {
  // Curated premium mock data for Phase 1
  const recentActivities = [
    {
      id: "act-1",
      type: "solved",
      title: "Two Sum",
      topic: "Arrays & Hashing",
      difficulty: "Easy",
      xp: "+50 XP",
      time: "2 hours ago",
    },
    {
      id: "act-2",
      type: "solved",
      title: "Bubble Sort Implementation",
      topic: "Sorting Algorithms",
      difficulty: "Easy",
      xp: "+50 XP",
      time: "Yesterday",
    },
    {
      id: "act-3",
      type: "unlocked",
      title: "Topic Conqueror",
      topic: "Achievement Unlocked",
      difficulty: "Badge",
      xp: "+100 XP",
      time: "2 days ago",
    },
  ];

  const revisions = [
    {
      id: "rev-1",
      title: "Binary Search",
      due: "Due today",
      problemsLeft: 3,
      topicId: "binary-search",
    },
    {
      id: "rev-2",
      title: "Maximum Subarray (Kadane's)",
      due: "In 2 days",
      problemsLeft: 1,
      topicId: "arrays",
    },
  ];

  const getDifficultyStyles = (diff: string) => {
    switch (diff.toLowerCase()) {
      case "easy": return "bg-success-emerald/10 text-success-emerald border-success-emerald/20";
      case "medium": return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20";
      case "hard": return "bg-primary/10 text-primary border-primary/20";
      case "badge": return "bg-xp-gold/10 text-xp-gold border-xp-gold/20";
      default: return "bg-zinc-800 text-zinc-300 border-zinc-700";
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Recent Activities */}
      <div className="lg:col-span-2 border border-card-border rounded-2xl p-6 glass-card">
        <div className="flex items-center gap-2 mb-6">
          <CheckCircle2 className="w-5 h-5 text-success-emerald" />
          <h3 className="text-lg font-bold text-white uppercase tracking-wider">
            Recent Activity
          </h3>
        </div>

        <div className="space-y-4">
          {recentActivities.map((act) => (
            <div
              key={act.id}
              className="flex justify-between items-center p-4 rounded-xl border border-card-border/50 bg-[#07070b]/40"
            >
              <div className="flex items-center gap-3">
                <div className="flex flex-col">
                  <span className="text-sm font-bold text-white">{act.title}</span>
                  <span className="text-xs text-muted-foreground">{act.topic}</span>
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                <span className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded border ${getDifficultyStyles(act.difficulty)}`}>
                  {act.difficulty}
                </span>
                <span className="text-xs font-mono font-bold text-xp-gold">
                  {act.xp}
                </span>
                <span className="text-xs text-muted-foreground font-mono hidden md:inline">
                  {act.time}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Revisions Panel */}
      <div className="border border-card-border rounded-2xl p-6 glass-card">
        <div className="flex items-center gap-2 mb-6">
          <RefreshCw className="w-5 h-5 text-info-cyan" />
          <h3 className="text-lg font-bold text-white uppercase tracking-wider">
            Active Revision
          </h3>
        </div>

        <div className="space-y-4">
          {revisions.map((rev) => (
            <div
              key={rev.id}
              className="p-4 rounded-xl border border-card-border/50 bg-[#07070b]/40 flex flex-col justify-between"
            >
              <div className="flex justify-between items-start mb-2">
                <span className="text-sm font-bold text-white">{rev.title}</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-info-cyan/10 text-info-cyan font-mono font-bold uppercase">
                  {rev.due}
                </span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-muted-foreground">
                  {rev.problemsLeft} problems remaining
                </span>
                <Link
                  href={`/roadmap/${rev.topicId}`}
                  className="text-primary font-bold hover:underline flex items-center gap-1 group"
                >
                  Review <ArrowRight className="w-3 h-3 transition-transform group-hover:translate-x-0.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
