"use client";

import React from "react";
import { useAuthUser } from "@/hooks/use-auth-user";
import StatsGrid from "@/components/dashboard/stats-grid";
import RecentProgress from "@/components/dashboard/recent-progress";
import { ArrowRight, Sparkles, Sword, Loader2, Trophy } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

export default function DashboardPage() {
  const { stats, user, isLoaded } = useAuthUser();

  if (!isLoaded || !stats) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh] gap-4">
        <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" />
        <p className="text-sm text-slate-400 font-mono">LOADING ARENA DATA...</p>
      </div>
    );
  }

  const displayName = stats.display_name || user?.fullName || "Coder";

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto px-2 sm:px-4">
      {/* 1. Welcome Banner */}
      <motion.div
        className="relative border border-slate-800 rounded-3xl p-6 sm:p-8 overflow-hidden bg-gradient-to-r from-slate-900 via-indigo-950/60 to-slate-950 shadow-xl"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2 max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-extrabold uppercase tracking-widest text-cyan-400 bg-cyan-500/10 px-3 py-0.5 rounded-full flex items-center gap-1.5 border border-cyan-500/20">
                <Sparkles className="w-3.5 h-3.5" /> Arena Active
              </span>
            </div>
            <h1 className="text-2xl sm:text-4xl font-black text-white tracking-tight">
              Welcome back, <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-300">{displayName}</span>!
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 max-w-xl leading-relaxed">
              You are currently ranked <span className="text-white font-bold">{stats.rank}</span>. Watch video lessons, master topics, and keep your daily streak alive to level up.
            </p>
          </div>

          <Link href="/roadmap">
            <motion.button
              className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-extrabold text-xs uppercase tracking-wider flex items-center gap-2.5 shadow-lg shadow-cyan-500/20 transition-all cursor-pointer shrink-0"
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
            >
              <Sword className="w-4 h-4" />
              <span>Continue Roadmap</span>
              <ArrowRight className="w-4 h-4" />
            </motion.button>
          </Link>
        </div>
      </motion.div>

      {/* 2. Core Stats Grid */}
      <StatsGrid />

      {/* 3. Level Progression & XP Overview Card */}
      <div className="border border-slate-800 rounded-2xl p-6 bg-slate-900/60 shadow-lg relative overflow-hidden flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-2 max-w-xl">
          <div className="flex items-center space-x-2">
            <Trophy className="w-5 h-5 text-amber-400" />
            <h3 className="text-lg font-extrabold text-white tracking-tight">
              Level {stats.level} Progression
            </h3>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Earn XP by completing curriculum video lessons and topics across the roadmap. Gain 1,000 XP to advance to the next level.
          </p>
          <div className="flex items-center space-x-4 pt-1 text-xs text-slate-300">
            <span>Current XP: <strong className="text-amber-400 font-mono font-bold">{stats.xp.toLocaleString()} XP</strong></span>
            <span>•</span>
            <span>Streak: <strong className="text-rose-400 font-mono font-bold">{stats.current_streak} Days</strong></span>
          </div>
        </div>

        {/* SVG Progress Circle */}
        <div className="relative w-32 h-32 flex items-center justify-center shrink-0">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="64"
              cy="64"
              r="54"
              className="stroke-slate-800 fill-none"
              strokeWidth="8"
            />
            <motion.circle
              cx="64"
              cy="64"
              r="54"
              className="stroke-amber-400 fill-none"
              strokeWidth="8"
              strokeDasharray="339"
              initial={{ strokeDashoffset: 339 }}
              animate={{ strokeDashoffset: 339 - (339 * (stats.xp % 1000)) / 1000 }}
              transition={{ duration: 1, ease: "easeOut" }}
            />
          </svg>
          <div className="absolute flex flex-col items-center">
            <span className="text-3xl font-black text-white font-mono">{stats.level}</span>
            <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Level</span>
          </div>
        </div>
      </div>

      {/* 4. Recent Activity Stream */}
      <RecentProgress />
    </div>
  );
}
