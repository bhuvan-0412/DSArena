"use client";

import React, { useState } from "react";
import { useAuthUser } from "@/hooks/use-auth-user";
import StatsGrid from "@/components/dashboard/stats-grid";
import MissionCard from "@/components/dashboard/mission-card";
import RecentProgress from "@/components/dashboard/recent-progress";
import { DailyAdaptivePlanCard } from "@/components/adaptive/daily-adaptive-plan-card";
import { AdaptiveRecommendationsCard } from "@/components/adaptive/adaptive-recommendations-card";
import { FocusModeModal } from "@/components/adaptive/focus-mode-modal";
import { DailyLoginRewardsCard } from "@/components/engagement/daily-login-rewards-card";
import { SeasonPassCard } from "@/components/engagement/season-pass-card";
import { WeeklyMonthlyChallengesCard } from "@/components/engagement/weekly-monthly-challenges-card";
import { RewardChestModal } from "@/components/engagement/reward-chest-modal";
import { ArrowRight, Sparkles, Sword, Loader2 } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

export default function DashboardPage() {
  const { stats, user, isLoaded } = useAuthUser();
  const [isFocusModeOpen, setIsFocusModeOpen] = useState(false);
  const [isChestModalOpen, setIsChestModalOpen] = useState(false);

  if (!isLoaded || !stats) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh] gap-4">
        <Loader2 className="w-10 h-10 text-primary animate-spin" />
        <p className="text-sm text-muted-foreground font-mono">LOADING ARENA DATA...</p>
      </div>
    );
  }

  // Welcome message username fallback
  const displayName = stats.display_name || user?.fullName || "Striver";

  return (
    <div className="space-y-8 pb-12">
      {/* Welcome Banner */}
      <motion.div
        className="relative border border-primary/20 rounded-3xl p-8 overflow-hidden bg-gradient-to-r from-primary/10 via-[#0a0a0f] to-[#030303] shadow-lg shadow-primary/5"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-bold uppercase tracking-widest text-primary bg-primary/10 px-2.5 py-1 rounded-full flex items-center gap-1.5 border border-primary/20">
                <Sparkles className="w-3.5 h-3.5" /> Arena Active
              </span>
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight mb-2">
              Welcome back, <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-100 to-primary">{displayName}</span>!
            </h1>
            <p className="text-sm md:text-base text-muted-foreground max-w-xl">
              You are currently ranked <span className="text-white font-bold">{stats.rank}</span>. Solve problems, complete quizzes, and keep your daily streak alive to reach <span className="text-primary font-bold">Legend</span> status.
            </p>
          </div>

          <Link href="/roadmap">
            <motion.button
              className="px-6 py-4 rounded-2xl bg-primary hover:bg-primary/90 text-white font-bold text-sm tracking-wider uppercase flex items-center gap-3 transition-colors duration-300 shadow-lg shadow-primary/25 cursor-pointer shrink-0"
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.98 }}
            >
              <Sword className="w-4 h-4" />
              <span>Continue Learning</span>
              <ArrowRight className="w-4 h-4" />
            </motion.button>
          </Link>
        </div>
      </motion.div>

      {/* Phase 6 Engagement: Daily Login Rewards Chain */}
      <DailyLoginRewardsCard onOpenChestModal={() => setIsChestModalOpen(true)} />

      {/* Phase 6 Engagement: Weekly & Monthly Quests */}
      <WeeklyMonthlyChallengesCard />

      {/* Phase 6 Engagement: Valorant Season Pass */}
      <SeasonPassCard />

      {/* Adaptive Learning Engine: Today's Personalized Plan */}
      <DailyAdaptivePlanCard onOpenFocusMode={() => setIsFocusModeOpen(true)} />

      {/* Adaptive Learning Engine: Recommendations */}
      <AdaptiveRecommendationsCard />

      {/* Stats Grid */}
      <StatsGrid />

      {/* Main Grid: Mission Card (2/3) & Visual Level Up Progress (1/3) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <MissionCard />
        </div>

        {/* Level Up details box */}
        <div className="border border-card-border rounded-2xl p-6 glass-card relative overflow-hidden flex flex-col justify-between">
          <div className="absolute top-0 right-0 w-32 h-32 bg-xp-gold/5 rounded-full blur-3xl pointer-events-none" />
          
          <div>
            <h3 className="text-lg font-bold text-white uppercase tracking-wider mb-4">
              Level Progression
            </h3>
            <div className="flex flex-col items-center justify-center py-6">
              <div className="relative w-36 h-36 flex items-center justify-center">
                {/* SVG Progress Circle */}
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="72"
                    cy="72"
                    r="64"
                    className="stroke-[#12121f] fill-none"
                    strokeWidth="10"
                  />
                  <motion.circle
                    cx="72"
                    cy="72"
                    r="64"
                    className="stroke-xp-gold fill-none"
                    strokeWidth="10"
                    strokeDasharray="402"
                    initial={{ strokeDashoffset: 402 }}
                    animate={{ strokeDashoffset: 402 - (402 * (stats.xp % 1000)) / 1000 }}
                    transition={{ duration: 1.2, ease: "easeOut" }}
                  />
                </svg>
                <div className="absolute flex flex-col items-center">
                  <span className="text-4xl font-black text-white font-mono">{stats.level}</span>
                  <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Level</span>
                </div>
              </div>
            </div>
          </div>

          <div className="text-center border-t border-card-border pt-4">
            <span className="text-xs text-muted-foreground">
              Tip: Solving 1 Medium problem awards <strong className="text-xp-gold">+100 XP</strong>.
            </span>
          </div>
        </div>
      </div>

      {/* Recent Progress */}
      <RecentProgress />

      {/* Focus Mode & Reward Chest Modals */}
      <FocusModeModal isOpen={isFocusModeOpen} onClose={() => setIsFocusModeOpen(false)} />
      <RewardChestModal isOpen={isChestModalOpen} onClose={() => setIsChestModalOpen(false)} />
    </div>
  );
}
