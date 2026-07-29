"use client";

import React, { useState, useEffect, useMemo, useRef } from "react";
import { 
  Flame, Trophy, Calendar, Sparkles, Code2, BookOpen, 
  Layers, TrendingUp, Clock, Award, ChevronRight, X, 
  AlertCircle, ArrowRight, CheckCircle2, Zap
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { useAuthUser } from "@/hooks/use-auth-user";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export interface DailyActivityItem {
  date: string;
  day_of_week: number; // 0=Monday ... 6=Sunday
  xp_earned: number;
  problems_solved: number;
  lessons_completed: number;
  topics_completed: number;
  study_minutes: number;
  streak_active: boolean;
  streak_count: number;
  intensity_level: number; // 0..4
  is_today: boolean;
  is_future: boolean;
}

export interface ActivityStatistics {
  current_streak: number;
  longest_streak: number;
  total_active_days: number;
  broken_streaks: number;
  total_xp_earned: number;
  problems_solved: number;
  lessons_completed: number;
  topics_completed: number;
  completion_percentage: number;
}

export interface DayDetail {
  date: string;
  xp_earned: number;
  problems_solved_count: number;
  lessons_completed_count: number;
  topics_completed_count: number;
  study_minutes: number;
  streak_count: number;
  completed_lessons: { id: string; title: string; type: string; difficulty?: string }[];
  completed_topics: { id: string; title: string; type: string; difficulty?: string }[];
  completed_problems: { id: string; title: string; difficulty: string; xp_reward: number }[];
  achievements_unlocked: { id: string; title: string; description: string; icon?: string }[];
}

const MONTH_NAMES = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
];

const DAY_LABELS = ["Mon", "", "Wed", "", "Fri", "", ""];

export function LearningActivityHeatmap() {
  const { clerkId } = useAuthUser();
  const [stats, setStats] = useState<ActivityStatistics | null>(null);
  const [activities, setActivities] = useState<DailyActivityItem[]>([]);
  const [todayDate, setTodayDate] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Hover Tooltip State
  const [hoveredDay, setHoveredDay] = useState<DailyActivityItem | null>(null);
  const [tooltipPos, setTooltipPos] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  // Click Detail Modal State
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [dayDetail, setDayDetail] = useState<DayDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);

  const containerRef = useRef<HTMLDivElement>(null);

  // Fetch Heatmap Data
  useEffect(() => {
    async function fetchHeatmap() {
      try {
        setLoading(true);
        setError(null);
        const res = await fetch(`${BACKEND_URL}/activity/heatmap?clerk_id=${clerkId || "mock_user_striver"}`);
        if (!res.ok) {
          throw new Error("Failed to load activity heatmap data");
        }
        const data = await res.json();
        setStats(data.statistics);
        setActivities(data.daily_activities || []);
        setTodayDate(data.today_date || "");
      } catch (err: unknown) {
        console.error("Heatmap fetch error:", err);
        setError(err instanceof Error ? err.message : "Could not fetch activity data");
      } finally {
        setLoading(false);
      }
    }

    fetchHeatmap();
  }, [clerkId]);

  // Fetch Day Detail when day clicked
  useEffect(() => {
    if (!selectedDate) {
      setDayDetail(null);
      return;
    }

    async function fetchDayDetail() {
      try {
        setLoadingDetail(true);
        const res = await fetch(`${BACKEND_URL}/activity/day/${selectedDate}?clerk_id=${clerkId || "mock_user_striver"}`);
        if (res.ok) {
          const data = await res.json();
          setDayDetail(data);
        } else {
          setDayDetail(null);
        }
      } catch (err) {
        console.error("Error fetching day detail:", err);
        setDayDetail(null);
      } finally {
        setLoadingDetail(false);
      }
    }

    fetchDayDetail();
  }, [selectedDate, clerkId]);

  // Organize activities into 52-53 weeks (columns) x 7 days (rows)
  const { weeks, monthHeaders } = useMemo(() => {
    if (!activities.length) return { weeks: [], monthHeaders: [] };

    const weeksArr: (DailyActivityItem | null)[][] = [];
    let currentWeek: (DailyActivityItem | null)[] = [];
    const mHeaders: { label: string; weekIndex: number }[] = [];
    let lastMonth = -1;

    activities.forEach((act) => {
      // If it's Monday and we have items, push previous week
      if (act.day_of_week === 0 && currentWeek.length > 0) {
        weeksArr.push(currentWeek);
        currentWeek = [];
      }

      // Check month header at start of week
      const dateObj = new Date(act.date + "T00:00:00");
      const monthIdx = dateObj.getMonth();
      if (act.day_of_week === 0 && monthIdx !== lastMonth) {
        mHeaders.push({
          label: MONTH_NAMES[monthIdx],
          weekIndex: weeksArr.length,
        });
        lastMonth = monthIdx;
      }

      currentWeek.push(act);
    });

    if (currentWeek.length > 0) {
      // Pad out currentWeek to 7 days if needed
      while (currentWeek.length < 7) {
        currentWeek.push(null);
      }
      weeksArr.push(currentWeek);
    }

    return { weeks: weeksArr, monthHeaders: mHeaders };
  }, [activities]);

  const handleMouseEnterCell = (act: DailyActivityItem, e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const containerRect = containerRef.current?.getBoundingClientRect();
    
    if (containerRect) {
      setTooltipPos({
        x: rect.left - containerRect.left + rect.width / 2,
        y: rect.top - containerRect.top - 10,
      });
    }
    setHoveredDay(act);
  };

  const formatStudyTime = (minutes: number) => {
    if (!minutes || minutes <= 0) return "0m";
    const hrs = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hrs > 0) {
      return `${hrs}h ${mins > 0 ? `${mins}m` : ""}`;
    }
    return `${mins}m`;
  };

  const formatDateDisplay = (dateStr: string) => {
    if (!dateStr) return "";
    const [y, m, d] = dateStr.split("-").map(Number);
    const dateObj = new Date(y, m - 1, d);
    return dateObj.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const getIntensityClass = (level: number, isToday: boolean, xp: number) => {
    if (isToday && xp > 0) {
      return "bg-emerald-400 border-emerald-300 ring-2 ring-cyan-400 ring-offset-2 ring-offset-slate-950 animate-pulse";
    }
    if (isToday) {
      return "bg-slate-800 border-cyan-500/80 ring-2 ring-cyan-400/60 ring-offset-2 ring-offset-slate-950";
    }

    switch (level) {
      case 4:
        return "bg-emerald-400 border-emerald-300 shadow-[0_0_8px_rgba(52,211,153,0.5)]";
      case 3:
        return "bg-emerald-600 border-emerald-500";
      case 2:
        return "bg-emerald-700/80 border-emerald-600";
      case 1:
        return "bg-emerald-900/60 border-emerald-800/80";
      case 0:
      default:
        return "bg-[#161b22] border-[#21262d] hover:border-slate-700";
    }
  };

  if (loading) {
    return (
      <div className="border border-card-border rounded-3xl p-8 bg-[#0a0a0f] flex flex-col items-center justify-center min-h-[300px] gap-3">
        <Sparkles className="w-8 h-8 text-cyan-400 animate-spin" />
        <span className="text-xs text-slate-400 font-mono uppercase tracking-widest">
          Loading Learning Heatmap...
        </span>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="border border-rose-900/50 rounded-3xl p-6 bg-rose-950/20 text-center space-y-3">
        <AlertCircle className="w-8 h-8 text-rose-400 mx-auto" />
        <p className="text-sm font-semibold text-rose-200">Unable to load activity heatmap</p>
        <p className="text-xs text-slate-400">{error || "Server issue"}</p>
      </div>
    );
  }

  const isTotalEmpty = stats.total_active_days === 0;

  return (
    <div className="space-y-6" ref={containerRef}>
      {/* 1. Statistics Cards Section */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
        {/* Current Streak */}
        <div className="border border-slate-800 rounded-2xl p-3.5 bg-slate-900/80 backdrop-blur-md relative overflow-hidden group hover:border-amber-500/50 transition-all">
          <div className="flex items-center justify-between text-xs text-slate-400 font-medium mb-1">
            <span>Current Streak</span>
            <Flame className="w-4 h-4 text-amber-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="text-xl sm:text-2xl font-black text-white font-mono flex items-baseline gap-1">
            {stats.current_streak}
            <span className="text-xs font-sans text-slate-400 font-normal">days</span>
          </div>
        </div>

        {/* Longest Streak */}
        <div className="border border-slate-800 rounded-2xl p-3.5 bg-slate-900/80 backdrop-blur-md relative overflow-hidden group hover:border-yellow-500/50 transition-all">
          <div className="flex items-center justify-between text-xs text-slate-400 font-medium mb-1">
            <span>Max Streak</span>
            <Trophy className="w-4 h-4 text-yellow-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="text-xl sm:text-2xl font-black text-white font-mono flex items-baseline gap-1">
            {stats.longest_streak}
            <span className="text-xs font-sans text-slate-400 font-normal">days</span>
          </div>
        </div>

        {/* Active Days */}
        <div className="border border-slate-800 rounded-2xl p-3.5 bg-slate-900/80 backdrop-blur-md relative overflow-hidden group hover:border-emerald-500/50 transition-all">
          <div className="flex items-center justify-between text-xs text-slate-400 font-medium mb-1">
            <span>Active Days</span>
            <Calendar className="w-4 h-4 text-emerald-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="text-xl sm:text-2xl font-black text-white font-mono">
            {stats.total_active_days}
          </div>
        </div>

        {/* Total XP */}
        <div className="border border-slate-800 rounded-2xl p-3.5 bg-slate-900/80 backdrop-blur-md relative overflow-hidden group hover:border-cyan-500/50 transition-all">
          <div className="flex items-center justify-between text-xs text-slate-400 font-medium mb-1">
            <span>Total XP</span>
            <Sparkles className="w-4 h-4 text-cyan-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="text-xl sm:text-2xl font-black text-amber-400 font-mono">
            {stats.total_xp_earned.toLocaleString()}
          </div>
        </div>

        {/* Problems Solved */}
        <div className="border border-slate-800 rounded-2xl p-3.5 bg-slate-900/80 backdrop-blur-md relative overflow-hidden group hover:border-indigo-500/50 transition-all">
          <div className="flex items-center justify-between text-xs text-slate-400 font-medium mb-1">
            <span>Problems Solved</span>
            <Code2 className="w-4 h-4 text-indigo-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="text-xl sm:text-2xl font-black text-white font-mono">
            {stats.problems_solved}
          </div>
        </div>

        {/* Lessons Completed */}
        <div className="border border-slate-800 rounded-2xl p-3.5 bg-slate-900/80 backdrop-blur-md relative overflow-hidden group hover:border-violet-500/50 transition-all">
          <div className="flex items-center justify-between text-xs text-slate-400 font-medium mb-1">
            <span>Lessons</span>
            <BookOpen className="w-4 h-4 text-violet-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="text-xl sm:text-2xl font-black text-white font-mono">
            {stats.lessons_completed}
          </div>
        </div>

        {/* Topics Completed */}
        <div className="border border-slate-800 rounded-2xl p-3.5 bg-slate-900/80 backdrop-blur-md relative overflow-hidden group hover:border-pink-500/50 transition-all">
          <div className="flex items-center justify-between text-xs text-slate-400 font-medium mb-1">
            <span>Topics</span>
            <Layers className="w-4 h-4 text-pink-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="text-xl sm:text-2xl font-black text-white font-mono">
            {stats.topics_completed}
          </div>
        </div>

        {/* Completion % */}
        <div className="border border-slate-800 rounded-2xl p-3.5 bg-slate-900/80 backdrop-blur-md relative overflow-hidden group hover:border-blue-500/50 transition-all">
          <div className="flex items-center justify-between text-xs text-slate-400 font-medium mb-1">
            <span>Roadmap %</span>
            <TrendingUp className="w-4 h-4 text-blue-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="text-xl sm:text-2xl font-black text-white font-mono">
            {stats.completion_percentage}%
          </div>
        </div>
      </div>

      {/* 2. Main Heatmap Container Card */}
      <div className="border border-card-border rounded-3xl p-6 bg-[#0a0a0f] space-y-5 relative shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-emerald-400" />
              <h3 className="text-base font-extrabold text-white tracking-tight">
                Daily Learning Activity & Consistency
              </h3>
              {stats.current_streak > 0 && (
                <span className="text-[10px] font-extrabold uppercase tracking-wider text-amber-400 bg-amber-500/10 px-2.5 py-0.5 rounded-full border border-amber-500/20 flex items-center gap-1">
                  <Flame className="w-3 h-3 fill-amber-400" /> {stats.current_streak} Day Streak
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Visualizing 365 days of learning actions across DSArena. Click any square for detailed history.
            </p>
          </div>

          <div className="flex items-center gap-4 text-xs font-mono shrink-0">
            <div className="text-slate-400">
              Active Days: <strong className="text-emerald-400">{stats.total_active_days}</strong>
            </div>
            <div className="text-slate-400">
              Broken Streaks: <strong className="text-slate-300">{stats.broken_streaks}</strong>
            </div>
          </div>
        </div>

        {/* Empty State Banner if 0 active days */}
        {isTotalEmpty && (
          <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-indigo-900/40 text-center space-y-3">
            <Zap className="w-8 h-8 text-amber-400 mx-auto" />
            <h4 className="text-sm font-extrabold text-white">No learning activity recorded yet</h4>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Start your first video lesson, solve a problem, or complete a topic today to initiate your daily study streak!
            </p>
            <Link href="/roadmap" className="inline-block pt-1">
              <button className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-extrabold text-xs uppercase tracking-wider flex items-center gap-2 shadow-lg shadow-cyan-500/20 cursor-pointer">
                <span>Continue Learning</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </Link>
          </div>
        )}

        {/* Heatmap Matrix & Grid */}
        <div className="relative overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-slate-800">
          <div className="min-w-[760px] space-y-2 select-none">
            {/* Month Labels Header */}
            <div className="flex text-[10px] font-mono text-slate-400 pl-8 h-4 relative">
              {monthHeaders.map((mh, idx) => (
                <div
                  key={idx}
                  className="absolute"
                  style={{ left: `calc(32px + ${mh.weekIndex * 14}px)` }}
                >
                  {mh.label}
                </div>
              ))}
            </div>

            {/* Grid with Day Labels (y-axis) + Weeks (x-axis) */}
            <div className="flex gap-1.5">
              {/* Day of Week Row Labels (Mon, Wed, Fri) */}
              <div className="flex flex-col justify-between text-[9px] font-mono text-slate-400 w-6 py-0.5 shrink-0">
                {DAY_LABELS.map((lbl, idx) => (
                  <span key={idx} className="h-3 flex items-center leading-none">
                    {lbl}
                  </span>
                ))}
              </div>

              {/* Week Columns */}
              <div className="flex gap-1">
                {weeks.map((week, wIdx) => (
                  <div key={wIdx} className="flex flex-col gap-1">
                    {week.map((act, dIdx) => {
                      if (!act) {
                        return (
                          <div
                            key={`empty-${wIdx}-${dIdx}`}
                            className="w-3 h-3 rounded-[3px] bg-slate-900/30 opacity-20"
                          />
                        );
                      }

                      const intensityClass = getIntensityClass(
                        act.intensity_level,
                        act.is_today,
                        act.xp_earned
                      );

                      return (
                        <div
                          key={act.date}
                          tabIndex={0}
                          role="gridcell"
                          aria-label={`Activity on ${formatDateDisplay(act.date)}: ${act.xp_earned} XP, ${act.problems_solved} problems solved`}
                          onMouseEnter={(e) => handleMouseEnterCell(act, e)}
                          onMouseLeave={() => setHoveredDay(null)}
                          onClick={() => setSelectedDate(act.date)}
                          onKeyDown={(e) => {
                            if (e.key === "Enter" || e.key === " ") {
                              e.preventDefault();
                              setSelectedDate(act.date);
                            }
                          }}
                          className={`w-3 h-3 rounded-[3px] border transition-all cursor-pointer hover:scale-125 hover:z-30 focus:outline-none focus:ring-2 focus:ring-cyan-400 ${intensityClass}`}
                        />
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Desktop Hover Floating Tooltip */}
          <AnimatePresence>
            {hoveredDay && (
              <motion.div
                initial={{ opacity: 0, y: 4, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.15 }}
                className="absolute z-50 pointer-events-none -translate-x-1/2 -translate-y-full mb-2 px-3 py-2.5 rounded-xl bg-slate-900/95 border border-slate-700 shadow-2xl text-xs backdrop-blur-md min-w-[200px]"
                style={{
                  left: `${tooltipPos.x}px`,
                  top: `${tooltipPos.y}px`,
                }}
              >
                <div className="font-extrabold text-white border-b border-slate-800 pb-1.5 mb-1.5 flex items-center justify-between gap-2">
                  <span>{formatDateDisplay(hoveredDay.date)}</span>
                  {hoveredDay.is_today && (
                    <span className="text-[9px] font-extrabold uppercase text-cyan-400 bg-cyan-500/10 px-1.5 py-0.5 rounded border border-cyan-500/30">
                      Today
                    </span>
                  )}
                </div>

                <div className="space-y-1 font-mono text-[11px]">
                  <div className="flex justify-between items-center text-slate-300">
                    <span>Problems Solved:</span>
                    <strong className="text-cyan-400 font-bold">{hoveredDay.problems_solved}</strong>
                  </div>
                  <div className="flex justify-between items-center text-slate-300">
                    <span>Lessons Completed:</span>
                    <strong className="text-violet-400 font-bold">{hoveredDay.lessons_completed}</strong>
                  </div>
                  <div className="flex justify-between items-center text-slate-300">
                    <span>Topics Completed:</span>
                    <strong className="text-pink-400 font-bold">{hoveredDay.topics_completed}</strong>
                  </div>
                  <div className="flex justify-between items-center text-slate-300">
                    <span>XP Earned:</span>
                    <strong className="text-amber-400 font-bold">+{hoveredDay.xp_earned} XP</strong>
                  </div>
                  <div className="flex justify-between items-center text-slate-300">
                    <span>Study Time:</span>
                    <strong className="text-emerald-400 font-bold">{formatStudyTime(hoveredDay.study_minutes)}</strong>
                  </div>
                  <div className="flex justify-between items-center text-slate-300 pt-1 border-t border-slate-800/80">
                    <span>Streak:</span>
                    <strong className={hoveredDay.streak_active ? "text-amber-400 font-bold flex items-center gap-1" : "text-slate-500"}>
                      {hoveredDay.streak_active ? (
                        <>
                          <Flame className="w-3 h-3 fill-amber-400" /> Day {hoveredDay.streak_count}
                        </>
                      ) : (
                        "No Activity"
                      )}
                    </strong>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* 3. Heatmap Legend */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-slate-400 pt-2 border-t border-slate-800/60 font-mono">
          <span className="text-slate-500 text-[11px]">
            Hover over any day square to inspect stats. Click to view day activity logs.
          </span>

          <div className="flex items-center gap-2 shrink-0">
            <span className="text-[11px] text-slate-400">Less</span>
            <div className="flex items-center gap-1">
              <div title="No Activity" className="w-3 h-3 rounded-[3px] bg-[#161b22] border border-[#21262d]" />
              <div title="Low Activity" className="w-3 h-3 rounded-[3px] bg-emerald-900/60 border border-emerald-800/80" />
              <div title="Medium Activity" className="w-3 h-3 rounded-[3px] bg-emerald-700/80 border border-emerald-600" />
              <div title="High Activity" className="w-3 h-3 rounded-[3px] bg-emerald-600 border border-emerald-500" />
              <div title="Very High Activity" className="w-3 h-3 rounded-[3px] bg-emerald-400 border border-emerald-300" />
            </div>
            <span className="text-[11px] text-slate-400">More</span>
          </div>
        </div>
      </div>

      {/* 4. Click Day Activity Detail Modal / Side Panel */}
      <AnimatePresence>
        {selectedDate && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 15 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 15 }}
              transition={{ duration: 0.2 }}
              className="relative w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl overflow-hidden space-y-6 max-h-[90vh] overflow-y-auto"
            >
              {/* Close Button */}
              <button
                onClick={() => setSelectedDate(null)}
                className="absolute top-5 right-5 p-2 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white transition-all cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>

              {/* Modal Header */}
              <div className="space-y-1 pr-8">
                <div className="flex items-center gap-2.5">
                  <Calendar className="w-5 h-5 text-cyan-400" />
                  <h3 className="text-xl font-black text-white tracking-tight">
                    {formatDateDisplay(selectedDate)}
                  </h3>
                  {selectedDate === todayDate && (
                    <span className="text-xs font-extrabold uppercase text-cyan-400 bg-cyan-500/10 px-2.5 py-0.5 rounded-full border border-cyan-500/20">
                      Today
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-400">
                  Detailed activity log, completed problems, lessons, and rewards earned on this date.
                </p>
              </div>

              {loadingDetail ? (
                <div className="py-12 flex flex-col items-center justify-center gap-3">
                  <Sparkles className="w-8 h-8 text-cyan-400 animate-spin" />
                  <span className="text-xs text-slate-400 font-mono">Fetching day activity logs...</span>
                </div>
              ) : dayDetail ? (
                <div className="space-y-6">
                  {/* Summary Metric Badges */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800">
                      <span className="text-[11px] text-slate-400 block font-medium">XP Earned</span>
                      <span className="text-lg font-black text-amber-400 font-mono">+{dayDetail.xp_earned} XP</span>
                    </div>

                    <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800">
                      <span className="text-[11px] text-slate-400 block font-medium">Problems Solved</span>
                      <span className="text-lg font-black text-cyan-400 font-mono">{dayDetail.problems_solved_count}</span>
                    </div>

                    <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800">
                      <span className="text-[11px] text-slate-400 block font-medium">Study Minutes</span>
                      <span className="text-lg font-black text-emerald-400 font-mono">{dayDetail.study_minutes}m</span>
                    </div>

                    <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800">
                      <span className="text-[11px] text-slate-400 block font-medium">Streak Day</span>
                      <span className="text-lg font-black text-amber-400 font-mono flex items-center gap-1">
                        {dayDetail.streak_count > 0 ? (
                          <>
                            <Flame className="w-4 h-4 fill-amber-400" /> #{dayDetail.streak_count}
                          </>
                        ) : (
                          "0"
                        )}
                      </span>
                    </div>
                  </div>

                  {/* Completed Problems List */}
                  {dayDetail.completed_problems.length > 0 && (
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                        <Code2 className="w-4 h-4 text-cyan-400" />
                        Completed Problems ({dayDetail.completed_problems.length})
                      </h4>
                      <div className="space-y-2">
                        {dayDetail.completed_problems.map((prob) => (
                          <div
                            key={prob.id}
                            className="p-3 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs"
                          >
                            <div className="flex items-center gap-2.5">
                              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                              <span className="text-white font-semibold">{prob.title}</span>
                            </div>
                            <div className="flex items-center gap-2 font-mono">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                prob.difficulty === "Easy" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" :
                                prob.difficulty === "Medium" ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" :
                                "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                              }`}>
                                {prob.difficulty}
                              </span>
                              <span className="text-amber-400 font-bold">+{prob.xp_reward} XP</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Completed Lessons & Topics */}
                  {(dayDetail.completed_lessons.length > 0 || dayDetail.completed_topics.length > 0) && (
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                        <BookOpen className="w-4 h-4 text-violet-400" />
                        Completed Curriculum Nodes
                      </h4>
                      <div className="space-y-2">
                        {dayDetail.completed_topics.map((top) => (
                          <div
                            key={top.id}
                            className="p-3 rounded-2xl bg-slate-950 border border-purple-900/40 flex items-center justify-between text-xs"
                          >
                            <div className="flex items-center gap-2.5">
                              <Layers className="w-4 h-4 text-purple-400 shrink-0" />
                              <span className="text-white font-semibold">{top.title}</span>
                            </div>
                            <span className="text-[10px] font-bold text-purple-400 uppercase tracking-wider bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
                              Topic Mastered
                            </span>
                          </div>
                        ))}
                        {dayDetail.completed_lessons.map((les) => (
                          <div
                            key={les.id}
                            className="p-3 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs"
                          >
                            <div className="flex items-center gap-2.5">
                              <BookOpen className="w-4 h-4 text-violet-400 shrink-0" />
                              <span className="text-white font-semibold">{les.title}</span>
                            </div>
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider bg-slate-800 px-2 py-0.5 rounded">
                              Lesson Complete
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Unlocked Achievements */}
                  {dayDetail.achievements_unlocked.length > 0 && (
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-2">
                        <Award className="w-4 h-4 text-amber-400" />
                        Achievements Unlocked ({dayDetail.achievements_unlocked.length})
                      </h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {dayDetail.achievements_unlocked.map((ach) => (
                          <div
                            key={ach.id}
                            className="p-3.5 rounded-2xl bg-gradient-to-r from-amber-950/30 to-slate-950 border border-amber-500/30 flex items-center gap-3"
                          >
                            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 shrink-0">
                              <Trophy className="w-5 h-5" />
                            </div>
                            <div>
                              <h5 className="text-xs font-bold text-white">{ach.title}</h5>
                              <p className="text-[11px] text-slate-400 leading-snug">{ach.description}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* No specific logs fallback */}
                  {dayDetail.xp_earned === 0 &&
                    dayDetail.completed_problems.length === 0 &&
                    dayDetail.completed_lessons.length === 0 &&
                    dayDetail.completed_topics.length === 0 && (
                      <div className="p-8 rounded-2xl bg-slate-950 border border-slate-800 text-center space-y-2">
                        <Calendar className="w-8 h-8 text-slate-600 mx-auto" />
                        <p className="text-xs text-slate-400">No learning activity logged on this date.</p>
                      </div>
                    )}
                </div>
              ) : (
                <div className="py-8 text-center text-xs text-slate-400">
                  No activity record found for this day.
                </div>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
