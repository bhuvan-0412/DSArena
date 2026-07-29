"use client";

import { useAuthUser } from "@/hooks/use-auth-user";
import { Flame, Zap } from "lucide-react";
import { motion } from "framer-motion";

export default function StatsBar() {
  const { stats, isLoaded, userAvatarUrl, userDisplayName, userUsername } = useAuthUser();

  if (!isLoaded || !stats) {
    return (
      <header className="h-16 border-b border-card-border bg-[#030303]/60 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-10">
        <div className="w-48 h-4 bg-muted animate-pulse rounded-md"></div>
        <div className="flex items-center gap-6">
          <div className="w-10 h-10 rounded-full bg-muted animate-pulse"></div>
        </div>
      </header>
    );
  }

  // Calculate XP within current level (1000 XP per level)
  const currentLevelXp = stats.xp % 1000;
  const xpNeededForNextLevel = 1000;
  const xpPercentage = (currentLevelXp / xpNeededForNextLevel) * 100;

  return (
    <header className="h-16 border-b border-card-border bg-[#030303]/80 backdrop-blur-md flex items-center justify-between px-6 sm:px-8 sticky top-0 z-10 w-full">
      {/* XP & Level Progress Bar */}
      <div className="flex items-center gap-4 flex-1 max-w-md">
        <div className="flex flex-col w-full">
          <div className="flex justify-between text-xs font-semibold mb-1">
            <span className="text-amber-400 flex items-center gap-1 font-mono text-[11px] font-bold">
              <Zap className="w-3.5 h-3.5 fill-amber-400" /> LEVEL {stats.level}
            </span>
            <span className="text-slate-400 font-mono text-[11px]">
              {currentLevelXp} / {xpNeededForNextLevel} XP
            </span>
          </div>
          <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
            <motion.div
              className="h-full bg-gradient-to-r from-amber-500 to-yellow-400 shadow-[0_0_8px_rgba(234,179,8,0.3)]"
              initial={{ width: 0 }}
              animate={{ width: `${xpPercentage}%` }}
              transition={{ duration: 0.8, ease: "easeOut" }}
            />
          </div>
        </div>
      </div>

      {/* Stats Badges: Streak & User Card */}
      <div className="flex items-center gap-4 sm:gap-6">
        {/* Streak */}
        <motion.div 
          className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-orange-500/10 border border-orange-500/20 text-orange-400 font-bold"
          whileHover={{ scale: 1.03 }}
        >
          <Flame className="w-4 h-4 fill-orange-500 animate-pulse text-orange-500" />
          <span className="text-xs font-mono tracking-wider">{stats.current_streak} DAY STREAK</span>
        </motion.div>

        {/* User Profile Card */}
        <div className="flex items-center gap-2.5 pl-4 border-l border-slate-800">
          <img
            src={userAvatarUrl}
            alt={userDisplayName}
            className="w-8 h-8 rounded-full border border-cyan-500/30 object-cover"
            onError={(e) => {
              (e.target as HTMLElement).setAttribute(
                "src",
                `https://api.dicebear.com/7.x/bottts/svg?seed=${userUsername}`
              );
            }}
          />
          <div className="hidden md:flex flex-col">
            <span className="text-xs font-bold text-white leading-tight">{userDisplayName}</span>
            <span className="text-[10px] text-slate-400 font-mono">@{userUsername}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
