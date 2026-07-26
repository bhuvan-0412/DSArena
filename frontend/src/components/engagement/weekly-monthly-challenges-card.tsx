"use client";

import React, { useState, useEffect } from "react";
import { Target, CheckCircle2, Zap, Calendar, Sparkles } from "lucide-react";
import { useAuthUser } from "@/hooks/use-auth-user";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

interface ChallengeItem {
  id: number;
  title: string;
  description: string;
  target_count: number;
  current_progress: number;
  xp_reward: number;
  is_completed: boolean;
  is_claimed: boolean;
}

export function WeeklyMonthlyChallengesCard() {
  const { clerkId } = useAuthUser();
  const [weekly, setWeekly] = useState<ChallengeItem[]>([]);
  const [monthly, setMonthly] = useState<ChallengeItem[]>([]);
  const [activeTab, setActiveTab] = useState<"weekly" | "monthly">("weekly");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (clerkId) {
      fetch(`${BACKEND_URL}/engagement/challenges?clerk_id=${clerkId}`)
        .then((res) => res.json())
        .then((data) => {
          setWeekly(data.weekly || []);
          setMonthly(data.monthly || []);
        })
        .catch((err) => console.error("Error fetching challenges:", err))
        .finally(() => setLoading(false));
    }
  }, [clerkId]);

  if (loading) return null;

  const currentList = activeTab === "weekly" ? weekly : monthly;

  return (
    <div className="border border-card-border rounded-3xl p-6 bg-[#0a0a0f] space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Target className="w-5 h-5 text-rose-500" />
          <h3 className="text-base font-extrabold text-white">Weekly & Monthly Quests</h3>
        </div>

        <div className="flex items-center gap-1.5 p-1 bg-slate-900 border border-slate-800 rounded-xl">
          <button
            onClick={() => setActiveTab("weekly")}
            className={`px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              activeTab === "weekly" ? "bg-rose-600 text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            Weekly
          </button>
          <button
            onClick={() => setActiveTab("monthly")}
            className={`px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              activeTab === "monthly" ? "bg-rose-600 text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            Monthly
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {currentList.map((item) => {
          const percent = Math.min(100, Math.round((item.current_progress / item.target_count) * 100));
          return (
            <div
              key={item.id}
              className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-white">{item.title}</span>
                  <span className="text-xs font-extrabold font-mono text-amber-400 flex items-center gap-0.5">
                    <Zap className="w-3.5 h-3.5 fill-amber-400" /> +{item.xp_reward} XP
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 leading-snug">{item.description}</p>
              </div>

              <div className="space-y-1 pt-1">
                <div className="flex justify-between text-[10px] font-mono text-slate-400">
                  <span>Progress</span>
                  <span className="text-rose-400 font-bold">{item.current_progress} / {item.target_count}</span>
                </div>
                <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                  <div className="h-full bg-rose-500 transition-all duration-500" style={{ width: `${percent}%` }} />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
