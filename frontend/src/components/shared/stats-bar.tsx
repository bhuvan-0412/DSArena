"use client";

import { useAuthUser } from "@/hooks/use-auth-user";
import { Flame, Trophy, Award, Zap } from "lucide-react";
import { motion } from "framer-motion";

export default function StatsBar() {
  const { stats, isLoaded } = useAuthUser();

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

  // Calculate XP within the current level (assuming 1000 XP per level)
  const currentLevelXp = stats.xp % 1000;
  const xpNeededForNextLevel = 1000;
  const xpPercentage = (currentLevelXp / xpNeededForNextLevel) * 100;

  // Get Rank colors
  const getRankBadgeColor = (rank: string) => {
    switch (rank.toLowerCase()) {
      case "unranked": return "bg-zinc-950 text-zinc-400 border-zinc-800";
      case "iron": return "bg-gray-800 text-gray-300 border-gray-600";
      case "bronze": return "bg-amber-900/30 text-amber-500 border-amber-800/50";
      case "silver": return "bg-slate-700/30 text-slate-300 border-slate-600/50";
      case "gold": return "bg-yellow-600/20 text-yellow-400 border-yellow-500/30";
      case "platinum": return "bg-teal-900/30 text-teal-400 border-teal-800/50";
      case "diamond": return "bg-cyan-900/30 text-cyan-400 border-cyan-800/50";
      case "ascendant": return "bg-emerald-900/30 text-emerald-400 border-emerald-800/50";
      case "master": return "bg-purple-900/30 text-purple-400 border-purple-800/50";
      case "grandmaster": return "bg-pink-900/30 text-pink-400 border-pink-800/50";
      case "legend": return "bg-red-950 text-primary border-primary/40";
      default: return "bg-zinc-900 text-zinc-300 border-zinc-800";
    }
  };

  return (
    <header className="h-20 border-b border-card-border bg-[#030303]/60 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-10 w-full">
      {/* XP Level Bar */}
      <div className="flex items-center gap-4 flex-1 max-w-xl">
        <div className="flex flex-col">
          <div className="flex justify-between text-xs font-semibold mb-1">
            <span className="text-xp-gold flex items-center gap-1 font-mono">
              <Zap className="w-3.5 h-3.5 fill-xp-gold" /> LEVEL {stats.level}
            </span>
            <span className="text-muted-foreground font-mono">
              {currentLevelXp} / {xpNeededForNextLevel} XP
            </span>
          </div>
          <div className="w-64 md:w-80 h-2.5 bg-muted rounded-full overflow-hidden border border-card-border">
            <motion.div
              className="h-full bg-gradient-to-r from-xp-gold to-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.3)]"
              initial={{ width: 0 }}
              animate={{ width: `${xpPercentage}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
            />
          </div>
        </div>
      </div>

      {/* Stats Badges */}
      <div className="flex items-center gap-6">
        {/* Streak */}
        <motion.div 
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-orange-950/20 border border-orange-500/20 text-orange-500 font-bold"
          whileHover={{ scale: 1.05 }}
        >
          <Flame className="w-4 h-4 fill-orange-500 animate-pulse" />
          <span className="text-sm font-mono">{stats.current_streak} DAY STREAK</span>
        </motion.div>

        {/* Rank Badge */}
        <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border font-extrabold text-xs uppercase tracking-wider ${getRankBadgeColor(stats.rank)} shadow-sm shadow-black/40`}>
          <Trophy className="w-3.5 h-3.5" />
          <span>{stats.rank}</span>
        </div>

        {/* User Card */}
        <div className="flex items-center gap-3 pl-4 border-l border-card-border">
          <img
            src={`https://api.dicebear.com/7.x/pixel-art/svg?seed=${stats.username}`}
            alt="User avatar"
            className="w-9 h-9 rounded-full bg-[#12121f] border border-card-border"
          />
          <div className="hidden md:flex flex-col">
            <span className="text-sm font-bold text-white">{stats.display_name}</span>
            <span className="text-xs text-muted-foreground font-mono">@{stats.username}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
