"use client";

import React, { useState, useEffect } from "react";
import { Calendar, Clock, Zap, CheckCircle2, TrendingUp } from "lucide-react";
import { useAuthUser } from "@/hooks/use-auth-user";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

interface CalendarDayActivity {
  date: string;
  study_minutes: number;
  xp_earned: number;
  problems_solved: number;
  quiz_accuracy: number;
  intensity: number;
}

interface CalendarData {
  activities: CalendarDayActivity[];
  monthly_study_hours: number;
  monthly_xp: number;
  monthly_problems: number;
  total_active_days: number;
}

export function InteractiveStudyCalendar() {
  const { clerkId } = useAuthUser();
  const [data, setData] = useState<CalendarData | null>(null);
  const [loading, setLoading] = useState(true);
  const [hoverDay, setHoverDay] = useState<CalendarDayActivity | null>(null);

  useEffect(() => {
    if (clerkId) {
      fetch(`${BACKEND_URL}/engagement/calendar?clerk_id=${clerkId}`)
        .then((res) => res.json())
        .then((resData) => setData(resData))
        .catch((err) => console.error("Error fetching study calendar:", err))
        .finally(() => setLoading(false));
    }
  }, [clerkId]);

  if (loading || !data) return null;

  const getIntensityColor = (intensity: number) => {
    switch (intensity) {
      case 4: return "bg-emerald-500 border-emerald-400";
      case 3: return "bg-emerald-600/80 border-emerald-500";
      case 2: return "bg-emerald-700/60 border-emerald-600";
      case 1: return "bg-emerald-900/40 border-emerald-800";
      default: return "bg-slate-900/60 border-slate-800/80";
    }
  };

  return (
    <div className="border border-card-border rounded-3xl p-6 bg-[#0a0a0f] space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-base font-extrabold text-white flex items-center gap-2">
            <Calendar className="w-5 h-5 text-emerald-400" />
            GitHub-Style Study Contribution Calendar
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Track daily study hours, XP earned, problems solved, and consistency.
          </p>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono">
          <div>
            <span className="text-slate-400 block">Monthly Hours</span>
            <span className="font-extrabold text-emerald-400">{data.monthly_study_hours} hrs</span>
          </div>
          <div>
            <span className="text-slate-400 block">Monthly XP</span>
            <span className="font-extrabold text-amber-400">+{data.monthly_xp}</span>
          </div>
        </div>
      </div>

      {/* GitHub Contribution Grid */}
      <div className="space-y-3">
        <div className="grid grid-cols-6 sm:grid-cols-10 md:grid-cols-15 lg:grid-cols-30 gap-1.5 p-3 rounded-2xl bg-slate-950 border border-slate-800/80 overflow-x-auto">
          {data.activities.map((act) => (
            <div
              key={act.date}
              onMouseEnter={() => setHoverDay(act)}
              className={`w-5 h-5 rounded-md border transition-all cursor-pointer hover:scale-125 ${getIntensityColor(act.intensity)}`}
              title={`${act.date}: ${act.study_minutes} mins, +${act.xp_earned} XP`}
            />
          ))}
        </div>

        {/* Hover Details Box */}
        {hoverDay ? (
          <div className="p-3 rounded-2xl bg-slate-900 border border-slate-800 text-xs flex items-center justify-between font-mono">
            <span className="text-white font-bold">{hoverDay.date} Activity:</span>
            <span className="text-emerald-400">{hoverDay.study_minutes} Mins Studied</span>
            <span className="text-amber-400">+{hoverDay.xp_earned} XP</span>
            <span className="text-cyan-400">{hoverDay.problems_solved} Problems Solved</span>
          </div>
        ) : (
          <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
            <span>Hover over any day square to inspect detailed study activity.</span>
            <div className="flex items-center gap-1.5">
              <span>Less</span>
              <span className="w-3 h-3 rounded bg-slate-900 border border-slate-800" />
              <span className="w-3 h-3 rounded bg-emerald-900/40 border border-emerald-800" />
              <span className="w-3 h-3 rounded bg-emerald-700/60 border border-emerald-600" />
              <span className="w-3 h-3 rounded bg-emerald-500 border border-emerald-400" />
              <span>More</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
