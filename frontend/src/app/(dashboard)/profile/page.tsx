"use client";

// Prevent static generation — requires live user auth and backend data
export const dynamic = "force-dynamic";

import { useEffect, useState } from "react";
import { useAuthUser } from "@/hooks/use-auth-user";
import { Trophy, Award, Lock, Shield, Flame, Zap, Layers, GitFork, TrendingUp, Moon, Sun, Loader2, Sparkles, FileText, Cpu, ChevronRight, Video, BarChart2, Calendar, Bookmark, BookOpen } from "lucide-react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { AISettingsModal } from "@/components/ai/ai-settings-modal";
import { InteractiveStudyCalendar } from "@/components/engagement/interactive-study-calendar";
import { TitleEquipModal } from "@/components/engagement/title-equip-modal";
import { RatingChartCard } from "@/components/contest/rating-chart-card";

interface AnalyticsData {
  strengths: string[];
  weaknesses: string[];
  average_solving_time: string;
  topic_completion: string;
  revision_completion_percentage: number;
  current_focus: string;
  achievements_count: number;
  achievements: { id: string; unlocked_at: string }[];
  problems_solved: number;
  problems_attempted: number;
  problems_mastered: number;
  average_quiz_score: number;
  quiz_accuracy?: number;
  total_quizzes_completed: number;
  perfect_scores_count?: number;
  weakest_quiz_concepts?: string[];
  strongest_quiz_concepts?: string[];
  best_topic: string;
  weakest_topic: string;
  personal_notes_count?: number;
  resources_completed_count?: number;
  bookmarked_topics_count?: number;
  bookmarked_problems_count?: number;
  bookmarked_resources_count?: number;
}

interface BookmarkItem {
  id: number;
  target_type: string;
  target_id: string;
  title: string;
  description?: string;
  difficulty?: string;
  created_at?: string;
}

interface UserBookmarks {
  concepts: BookmarkItem[];
  problems: BookmarkItem[];
  resources: BookmarkItem[];
}

interface TimelineData {
  study_days: number;
  problems_solved: number;
  xp_earned: number;
  longest_streak: number;
  avg_duration_minutes: number;
  calendar: { date: string; count: number; xp: number; duration: number }[];
}

import { BACKEND_URL } from "@/lib/api-config";


export default function ProfilePage() {
  const { stats, isLoaded } = useAuthUser();
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [timeline, setTimeline] = useState<TimelineData | null>(null);
  const [bookmarks, setBookmarks] = useState<UserBookmarks | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAiSettingsOpen, setIsAiSettingsOpen] = useState(false);

  const clerkId = stats?.clerk_id || "mock_user_striver";

  useEffect(() => {
    if (!isLoaded) return;

    async function fetchProfileData() {
      try {
        setLoading(true);
        const [analyticsRes, timelineRes, bookmarksRes] = await Promise.all([
          fetch(`${BACKEND_URL}/users/${clerkId}/learning-analytics`),
          fetch(`${BACKEND_URL}/users/${clerkId}/timeline`),
          fetch(`${BACKEND_URL}/users/${clerkId}/bookmarks`),
        ]);

        if (analyticsRes.ok) {
          const aData = await analyticsRes.json();
          setAnalytics(aData);
        }
        if (timelineRes.ok) {
          const tData = await timelineRes.json();
          setTimeline(tData);
        }
        if (bookmarksRes.ok) {
          const bData = await bookmarksRes.json();
          setBookmarks(bData);
        }
        if (timelineRes.ok) {
          const tData = await timelineRes.json();
          setTimeline(tData);
        }
      } catch (err) {
        console.error("Error fetching profile details:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchProfileData();
  }, [clerkId, isLoaded]);

  // Catalog of achievements
  const allAchievements = [
    { id: "first_problem", title: "First Blood", description: "Complete your first DSA problem in DSArena.", icon: Shield },
    { id: "first_topic", title: "Topic Conqueror", description: "Master all problems within your first topic node.", icon: Trophy },
    { id: "7_day_streak", title: "Week of Fire", description: "Maintain a login/solving streak for 7 consecutive days.", icon: Flame },
    { id: "30_day_streak", title: "Ascended Routine", description: "Maintain a login/solving streak for 30 consecutive days.", icon: Zap },
    { id: "100_problems", title: "Centurion", description: "Solve 100 problems on the roadmap.", icon: Award },
    { id: "array_master", title: "Array Commander", description: "Complete all Arrays and Hashing nodes.", icon: Layers },
    { id: "graph_explorer", title: "Graph Cartographer", description: "Complete the Graph and Trees nodes.", icon: GitFork },
    { id: "dp_survivor", title: "DP Overlord", description: "Successfully conquer the Dynamic Programming nodes.", icon: TrendingUp },
    { id: "night_owl", title: "Night Owl", description: "Submit a correct solution between 12:00 AM and 4:00 AM.", icon: Moon },
    { id: "early_bird", title: "Early Bird", description: "Submit a correct solution between 5:00 AM and 8:00 AM.", icon: Sun },
  ];

  // Helper to check if unlocked
  const getAchievementUnlockTime = (id: string) => {
    if (!analytics) return null;
    const match = analytics.achievements.find((a) => a.id === id);
    return match ? match.unlocked_at : null;
  };

  // Helper to generate calendar contribution cells for last 365 days
  const getTimelineCells = () => {
    if (!timeline) return [];
    
    // We generate 53 weeks x 7 days
    const cells = [];
    const now = new Date();
    // Start from 364 days ago
    for (let i = 370; i >= 0; i--) {
      const d = new Date();
      d.setDate(now.getDate() - i);
      const dateStr = d.toISOString().split("T")[0];
      
      const activity = timeline.calendar.find((c) => c.date === dateStr);
      cells.push({
        date: dateStr,
        count: activity ? activity.count : 0,
        xp: activity ? activity.xp : 0,
      });
    }
    return cells;
  };

  const getShadingColor = (count: number, xp: number) => {
    if (xp === 0) return "bg-zinc-950/80 border-card-border/20";
    if (count === 0 && xp > 0) return "bg-success-emerald/10 border-success-emerald/10";
    if (count === 1) return "bg-success-emerald/30 border-success-emerald/20";
    if (count === 2) return "bg-success-emerald/65 border-success-emerald/40 shadow-[0_0_6px_rgba(16,185,129,0.15)]";
    return "bg-success-emerald border-success-emerald/60 shadow-[0_0_10px_rgba(16,185,129,0.3)]";
  };

  if (!isLoaded || loading || !stats) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh] gap-4">
        <Loader2 className="w-10 h-10 text-primary animate-spin" />
        <p className="text-sm text-muted-foreground font-mono">LOADING PROFILE CARD...</p>
      </div>
    );
  }

  const cells = getTimelineCells();
  const unlockedCount = allAchievements.filter((a) => !!getAchievementUnlockTime(a.id)).length;

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
              <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-1 rounded bg-orange-950/20 text-orange-500 border border-orange-500/20">
                {stats.current_streak} Day Streak
              </span>
            </div>

            <button
              onClick={() => setIsAiSettingsOpen(true)}
              className="mt-3 text-xs font-bold px-3 py-1.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 hover:bg-rose-500/20 transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <Cpu className="w-3.5 h-3.5" />
              <span>Configure AI Coach</span>
            </button>
          </div>
        </div>

        <div className="flex flex-col items-center md:items-end justify-center text-center md:text-right border-t md:border-t-0 md:border-l border-card-border pt-6 md:pt-0 md:pl-10 min-w-[150px]">
          <span className="text-4xl font-black text-xp-gold font-mono">{stats.xp.toLocaleString()}</span>
          <span className="text-xs uppercase font-extrabold tracking-widest text-muted-foreground">Total XP Gained</span>
        </div>
      </motion.div>

      <AISettingsModal isOpen={isAiSettingsOpen} onClose={() => setIsAiSettingsOpen(false)} />

      {/* Problem Statuses Grid */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="border border-card-border rounded-2xl p-5 bg-[#0a0a0f] flex items-center justify-between">
            <div>
              <span className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground block mb-1">Problems Solved</span>
              <span className="text-2xl font-black text-success-emerald font-mono">{analytics.problems_solved}</span>
            </div>
            <div className="w-10 h-10 rounded-xl bg-success-emerald/10 text-success-emerald flex items-center justify-center border border-success-emerald/20 font-bold text-lg">🟢</div>
          </div>
          <div className="border border-card-border rounded-2xl p-5 bg-[#0a0a0f] flex items-center justify-between">
            <div>
              <span className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground block mb-1">Problems Attempted</span>
              <span className="text-2xl font-black text-yellow-500 font-mono">{analytics.problems_attempted}</span>
            </div>
            <div className="w-10 h-10 rounded-xl bg-yellow-500/10 text-yellow-500 flex items-center justify-center border border-yellow-500/20 font-bold text-lg">🟡</div>
          </div>
          <div className="border border-card-border rounded-2xl p-5 bg-[#0a0a0f] flex items-center justify-between">
            <div>
              <span className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground block mb-1">Problems Mastered</span>
              <span className="text-2xl font-black text-purple-500 font-mono">{analytics.problems_mastered}</span>
            </div>
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-500 flex items-center justify-center border border-purple-500/20 font-bold text-lg">🟣</div>
          </div>
        </div>
      )}

      {/* Analytics Grid */}
      {analytics && (
        <div className="border border-card-border rounded-2xl p-6 glass-card space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 mb-2">
            <BarChart2 className="w-4 h-4 text-primary" /> Learning Analytics
          </h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs pt-1">
            <div className="p-3 rounded-xl border border-card-border/50 bg-[#030303]/40 flex justify-between items-center">
              <span className="text-muted-foreground uppercase font-bold text-[9px] tracking-widest">Topic Nodes Completed</span>
              <span className="text-white font-bold font-mono">{analytics.topic_completion}</span>
            </div>
            <div className="p-3 rounded-xl border border-card-border/50 bg-[#030303]/40 flex justify-between items-center">
              <span className="text-muted-foreground uppercase font-bold text-[9px] tracking-widest">Average Quiz Score</span>
              <span className="text-xp-gold font-bold font-mono">{analytics.average_quiz_score}%</span>
            </div>
            <div className="p-3 rounded-xl border border-card-border/50 bg-[#030303]/40 flex justify-between items-center">
              <span className="text-muted-foreground uppercase font-bold text-[9px] tracking-widest">Quiz Accuracy</span>
              <span className="text-success-emerald font-bold font-mono">{analytics.quiz_accuracy ?? analytics.average_quiz_score}%</span>
            </div>
            <div className="p-3 rounded-xl border border-card-border/50 bg-[#030303]/40 flex justify-between items-center">
              <span className="text-muted-foreground uppercase font-bold text-[9px] tracking-widest">Perfect Scores (100%)</span>
              <span className="text-xp-gold font-bold font-mono">{analytics.perfect_scores_count ?? 0}</span>
            </div>
            <div className="p-3 rounded-xl border border-card-border/50 bg-[#030303]/40 flex justify-between items-center">
              <span className="text-muted-foreground uppercase font-bold text-[9px] tracking-widest">Quizzes Conquered</span>
              <span className="text-white font-bold font-mono">{analytics.total_quizzes_completed} nodes</span>
            </div>
            <div className="p-3 rounded-xl border border-card-border/50 bg-[#030303]/40 flex justify-between items-center">
              <span className="text-muted-foreground uppercase font-bold text-[9px] tracking-widest">Revision Completion</span>
              <span className="text-info-cyan font-bold font-mono">{analytics.revision_completion_percentage}%</span>
            </div>
          </div>
        </div>
      )}

      {/* GitHub Style Learning Timeline */}
      {timeline && (
        <div className="border border-card-border rounded-3xl p-6 glass-card space-y-6">
          <div className="flex flex-col md:flex-row justify-between md:items-center gap-4">
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-primary" />
              <h2 className="text-lg font-bold text-white uppercase tracking-wider">
                Gladiator Timeline
              </h2>
            </div>
            
            {/* Summary statistics row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
              <div className="px-3 py-1.5 rounded-lg border border-card-border bg-[#030303]/40">
                <span className="text-muted-foreground block text-[9px] uppercase tracking-widest mb-0.5">Study Days</span>
                <span className="text-white font-bold font-mono">{timeline.study_days} days</span>
              </div>
              <div className="px-3 py-1.5 rounded-lg border border-card-border bg-[#030303]/40">
                <span className="text-muted-foreground block text-[9px] uppercase tracking-widest mb-0.5">Solved</span>
                <span className="text-success-emerald font-bold font-mono">{timeline.problems_solved} nodes</span>
              </div>
              <div className="px-3 py-1.5 rounded-lg border border-card-border bg-[#030303]/40">
                <span className="text-muted-foreground block text-[9px] uppercase tracking-widest mb-0.5">Max Streak</span>
                <span className="text-orange-500 font-bold font-mono">{timeline.longest_streak} days</span>
              </div>
              <div className="px-3 py-1.5 rounded-lg border border-card-border bg-[#030303]/40">
                <span className="text-muted-foreground block text-[9px] uppercase tracking-widest mb-0.5">Avg Session</span>
                <span className="text-info-cyan font-bold font-mono">{timeline.avg_duration_minutes} mins</span>
              </div>
            </div>
          </div>

          {/* Grid wrapper */}
          <div className="relative border border-card-border bg-[#030303]/40 p-4 rounded-2xl overflow-x-auto">
            {/* The contribution cells grid */}
            <div className="grid grid-flow-col grid-rows-7 gap-1 min-w-[700px]">
              {cells.map((cell, idx) => (
                <div 
                  key={idx}
                  className={`w-3.5 h-3.5 rounded-[2px] border ${getShadingColor(cell.count, cell.xp)}`}
                  title={`${cell.date}: ${cell.count} solved, +${cell.xp} XP`}
                />
              ))}
            </div>
            
            {/* Legend */}
            <div className="flex justify-end items-center gap-1.5 text-[9px] text-muted-foreground mt-4 uppercase font-bold tracking-widest">
              <span>Less</span>
              <div className="w-3 h-3 rounded-[2px] border bg-zinc-950/80 border-card-border/20" />
              <div className="w-3 h-3 rounded-[2px] border bg-success-emerald/10 border-success-emerald/10" />
              <div className="w-3 h-3 rounded-[2px] border bg-success-emerald/30 border-success-emerald/20" />
              <div className="w-3 h-3 rounded-[2px] border bg-success-emerald/65 border-success-emerald/40" />
              <div className="w-3 h-3 rounded-[2px] border bg-success-emerald border-success-emerald/60" />
              <span>More</span>
            </div>
          </div>
        </div>
      )}

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
            {unlockedCount} / {allAchievements.length} UNLOCKED
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {allAchievements.map((ach, idx) => {
            const Icon = ach.icon;
            const unlockTime = getAchievementUnlockTime(ach.id);
            const isUnlocked = !!unlockTime;
            
            return (
              <motion.div
                key={ach.id}
                className={`border rounded-2xl p-5 relative overflow-hidden transition-all duration-300 ${
                  isUnlocked
                    ? "glass-card border-xp-gold/30 hover:border-xp-gold/60 shadow-lg shadow-xp-gold/[0.02]"
                    : "bg-[#050508]/30 border-card-border/40 opacity-50"
                }`}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.05 }}
              >
                {/* Visual Glow for Unlocked Badges */}
                {isUnlocked && (
                  <div className="absolute top-0 right-0 w-24 h-24 bg-xp-gold/5 rounded-full blur-2xl pointer-events-none" />
                )}

                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 border ${
                    isUnlocked
                      ? "bg-xp-gold/10 text-xp-gold border-xp-gold/20"
                      : "bg-zinc-950 text-zinc-600 border-zinc-900"
                  }`}>
                    {isUnlocked ? (
                      <motion.div
                        initial={{ rotate: -10, scale: 0.8 }}
                        animate={{ rotate: 0, scale: 1 }}
                        transition={{ delay: idx * 0.06, type: "spring" }}
                      >
                        <Icon className="w-6 h-6 animate-pulse" />
                      </motion.div>
                    ) : (
                      <Lock className="w-5 h-5" />
                    )}
                  </div>

                  <div className="space-y-1">
                    <h3 className={`font-bold text-sm ${isUnlocked ? "text-white" : "text-zinc-500"}`}>
                      {ach.title}
                    </h3>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      {ach.description}
                    </p>
                    {unlockTime && (
                      <span className="text-[9px] text-muted-foreground font-mono block pt-1 uppercase">
                        Unlocked {new Date(unlockTime).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Bookmarked Learning Items & Personal Notes */}
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Bookmark className="w-5 h-5 text-xp-gold fill-xp-gold" />
            <h2 className="text-xl font-bold text-white uppercase tracking-wider">
              Bookmarked Items & Learning Notes
            </h2>
          </div>
          {analytics && (
            <div className="flex gap-2 font-mono text-xs font-bold text-muted-foreground">
              <span className="px-2.5 py-1 rounded bg-muted border border-card-border">
                {analytics.personal_notes_count || 0} Personal Notes
              </span>
              <span className="px-2.5 py-1 rounded bg-muted border border-card-border">
                {analytics.resources_completed_count || 0} Resources Completed
              </span>
            </div>
          )}
        </div>

        {/* Phase 7 Contest Platform Rating & Stats */}
        <RatingChartCard />

        {/* Phase 6 Engagement: GitHub Style Study Contribution Calendar */}
        <InteractiveStudyCalendar />

        {/* Bookmarks Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Bookmarked Topics */}
          <div className="border border-card-border rounded-2xl p-6 glass-card space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center justify-between">
              <span className="flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-primary" /> Bookmarked Topics
              </span>
              <span className="text-xs font-mono font-extrabold text-primary">
                {bookmarks?.concepts.length || 0}
              </span>
            </h3>
            {(!bookmarks || bookmarks.concepts.length === 0) ? (
              <p className="text-xs text-muted-foreground italic">No topics bookmarked yet.</p>
            ) : (
              <div className="space-y-2.5 max-h-[220px] overflow-y-auto pr-1">
                {bookmarks.concepts.map((c) => (
                  <Link
                    key={c.id}
                    href={`/roadmap/${c.target_id}`}
                    className="p-3 rounded-xl border border-card-border bg-[#030303]/40 hover:border-primary/40 flex justify-between items-center transition-all group"
                  >
                    <div className="space-y-0.5">
                      <h4 className="text-xs font-bold text-white group-hover:text-primary transition-colors">
                        {c.title}
                      </h4>
                      <span className="text-[9px] font-mono text-muted-foreground">{c.difficulty}</span>
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-white" />
                  </Link>
                ))}
              </div>
            )}
          </div>

          {/* Bookmarked Problems */}
          <div className="border border-card-border rounded-2xl p-6 glass-card space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center justify-between">
              <span className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-success-emerald" /> Bookmarked Problems
              </span>
              <span className="text-xs font-mono font-extrabold text-success-emerald">
                {bookmarks?.problems.length || 0}
              </span>
            </h3>
            {(!bookmarks || bookmarks.problems.length === 0) ? (
              <p className="text-xs text-muted-foreground italic">No problems bookmarked yet.</p>
            ) : (
              <div className="space-y-2.5 max-h-[220px] overflow-y-auto pr-1">
                {bookmarks.problems.map((p) => (
                  <div
                    key={p.id}
                    className="p-3 rounded-xl border border-card-border bg-[#030303]/40 flex justify-between items-center"
                  >
                    <div className="space-y-0.5">
                      <h4 className="text-xs font-bold text-white">{p.title}</h4>
                      <span className="text-[9px] font-mono text-muted-foreground">{p.difficulty}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Bookmarked Resources */}
          <div className="border border-card-border rounded-2xl p-6 glass-card space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Video className="w-4 h-4 text-red-500" /> Bookmarked Resources
              </span>
              <span className="text-xs font-mono font-extrabold text-red-500">
                {bookmarks?.resources.length || 0}
              </span>
            </h3>
            {(!bookmarks || bookmarks.resources.length === 0) ? (
              <p className="text-xs text-muted-foreground italic">No learning resources bookmarked yet.</p>
            ) : (
              <div className="space-y-2.5 max-h-[220px] overflow-y-auto pr-1">
                {bookmarks.resources.map((r) => (
                  <div
                    key={r.id}
                    className="p-3 rounded-xl border border-card-border bg-[#030303]/40 space-y-1"
                  >
                    <h4 className="text-xs font-bold text-white">{r.title}</h4>
                    <p className="text-[10px] text-muted-foreground">{r.description}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
