"use client";

import { useAuthUser } from "@/hooks/use-auth-user";
import { Trophy, Award, Lock, Shield, Flame, Zap, Layers, GitFork, TrendingUp, Moon, Sun, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

export default function ProfilePage() {
  const { stats, isLoaded } = useAuthUser();

  if (!isLoaded || !stats) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh] gap-4">
        <Loader2 className="w-10 h-10 text-primary animate-spin" />
        <p className="text-sm text-muted-foreground font-mono">LOADING PROFILE CARD...</p>
      </div>
    );
  }

  // Catalog of achievements mapping icons
  const achievementsList = [
    { id: "first_problem", title: "First Blood", description: "Complete your first DSA problem in DSArena.", icon: Shield, unlocked: true },
    { id: "first_topic", title: "Topic Conqueror", description: "Master all problems within your first topic node.", icon: Trophy, unlocked: true },
    { id: "7_day_streak", title: "Week of Fire", description: "Maintain a login/solving streak for 7 consecutive days.", icon: Flame, unlocked: false },
    { id: "30_day_streak", title: "Ascended Routine", description: "Maintain a login/solving streak for 30 consecutive days.", icon: Zap, unlocked: false },
    { id: "100_problems", title: "Centurion", description: "Solve 100 problems on the roadmap.", icon: Award, unlocked: false },
    { id: "array_master", title: "Array Commander", description: "Complete all Arrays and Hashing nodes.", icon: Layers, unlocked: false },
    { id: "graph_explorer", title: "Graph Cartographer", description: "Complete the Graph and Trees nodes.", icon: GitFork, unlocked: false },
    { id: "dp_survivor", title: "DP Overlord", description: "Successfully conquer the Dynamic Programming nodes.", icon: TrendingUp, unlocked: false },
    { id: "night_owl", title: "Night Owl", description: "Submit a correct solution between 12:00 AM and 4:00 AM.", icon: Moon, unlocked: true },
    { id: "early_bird", title: "Early Bird", description: "Submit a correct solution between 5:00 AM and 8:00 AM.", icon: Sun, unlocked: false },
  ];

  const unlockedCount = achievementsList.filter((a) => a.unlocked).length;

  return (
    <div className="space-y-10 pb-16">
      {/* Profile Header Card */}
      <motion.div
        className="border border-card-border rounded-3xl p-8 glass-card flex flex-col md:flex-row items-center md:items-start justify-between gap-8 relative overflow-hidden"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="absolute top-0 right-0 w-80 h-80 bg-primary/5 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row items-center gap-6 relative z-10">
          <img
            src={`https://api.dicebear.com/7.x/pixel-art/svg?seed=${stats.username}`}
            alt="User avatar"
            className="w-24 h-24 rounded-2xl bg-[#12121f] border-2 border-primary shadow-lg shadow-primary/10"
          />
          <div className="text-center md:text-left space-y-2">
            <h1 className="text-3xl font-extrabold text-white">{stats.display_name}</h1>
            <p className="text-sm font-mono text-muted-foreground">@{stats.username}</p>
            <div className="flex flex-wrap justify-center md:justify-start gap-3 mt-2">
              <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-1 rounded bg-muted text-muted-foreground border border-card-border">
                Level {stats.level}
              </span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-1 rounded bg-primary/15 text-primary border border-primary/25">
                {stats.rank} Rank
              </span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-1 rounded bg-orange-950/20 text-orange-500 border border-orange-500/20">
                {stats.current_streak} Day Streak
              </span>
            </div>
          </div>
        </div>

        <div className="flex flex-col items-center md:items-end justify-center text-center md:text-right border-t md:border-t-0 md:border-l border-card-border pt-6 md:pt-0 md:pl-10 min-w-[150px]">
          <span className="text-4xl font-black text-xp-gold font-mono">{stats.xp.toLocaleString()}</span>
          <span className="text-xs uppercase font-extrabold tracking-widest text-muted-foreground">Total XP Gained</span>
        </div>
      </motion.div>

      {/* Achievements Section */}
      <div>
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-2">
            <Trophy className="w-5 h-5 text-xp-gold" />
            <h2 className="text-xl font-bold text-white uppercase tracking-wider">
              Unlocked Achievements
            </h2>
          </div>
          <span className="text-xs font-mono font-bold px-2 py-1 rounded bg-muted text-muted-foreground border border-card-border">
            {unlockedCount} / {achievementsList.length} UNLOCKED
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {achievementsList.map((ach, idx) => {
            const Icon = ach.icon;
            return (
              <motion.div
                key={ach.id}
                className={`border rounded-2xl p-5 relative overflow-hidden transition-all duration-300 ${
                  ach.unlocked
                    ? "glass-card border-xp-gold/30 hover:border-xp-gold/60"
                    : "bg-[#050508]/30 border-card-border/40 opacity-50"
                }`}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.05 }}
              >
                {/* Visual Glow for Unlocked Badges */}
                {ach.unlocked && (
                  <div className="absolute top-0 right-0 w-24 h-24 bg-xp-gold/5 rounded-full blur-2xl pointer-events-none" />
                )}

                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 border ${
                    ach.unlocked
                      ? "bg-xp-gold/10 text-xp-gold border-xp-gold/20"
                      : "bg-zinc-950 text-zinc-600 border-zinc-900"
                  }`}>
                    {ach.unlocked ? <Icon className="w-6 h-6" /> : <Lock className="w-5 h-5" />}
                  </div>

                  <div className="space-y-1">
                    <h3 className={`font-bold text-sm ${ach.unlocked ? "text-white" : "text-zinc-500"}`}>
                      {ach.title}
                    </h3>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      {ach.description}
                    </p>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
