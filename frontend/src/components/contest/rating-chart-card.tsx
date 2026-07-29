"use client";

import React, { useState, useEffect } from "react";
import { Trophy, TrendingUp, ShieldCheck, Award, Zap } from "lucide-react";
import { useAuthUser } from "@/hooks/use-auth-user";
import { BACKEND_URL } from "@/lib/api-config";


interface RatingHistoryItem {
  contest_title: string;
  old_rating: number;
  new_rating: number;
  rating_delta: number;
  rank: number;
  recorded_at: string;
}

interface UserContestStats {
  contest_rating: number;
  highest_rating: number;
  contest_rank_title: string;
  best_rank: number;
  total_contests: number;
  rating_history: RatingHistoryItem[];
}

export function RatingChartCard() {
  const { clerkId } = useAuthUser();
  const [data, setData] = useState<UserContestStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (clerkId) {
      fetch(`${BACKEND_URL}/contests/user/history?clerk_id=${clerkId}`)
        .then((res) => res.json())
        .then((resData) => setData(resData))
        .catch((err) => console.error("Error fetching contest stats:", err))
        .finally(() => setLoading(false));
    }
  }, [clerkId]);

  if (loading || !data) return null;

  const getRankBadgeColor = (title: string) => {
    switch (title.toLowerCase()) {
      case "legend": return "bg-red-500/10 text-red-400 border-red-500/30";
      case "grandmaster": return "bg-rose-500/10 text-rose-400 border-rose-500/30";
      case "master": return "bg-amber-500/10 text-amber-400 border-amber-500/30";
      case "expert": return "bg-purple-500/10 text-purple-400 border-purple-500/30";
      case "specialist": return "bg-cyan-500/10 text-cyan-400 border-cyan-500/30";
      default: return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
    }
  };

  return (
    <div className="border border-card-border rounded-3xl p-6 bg-[#0a0a0f] space-y-5 relative overflow-hidden">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
            <Trophy className="w-6 h-6 text-amber-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded border ${getRankBadgeColor(data.contest_rank_title)}`}>
                {data.contest_rank_title} Tier
              </span>
            </div>
            <h3 className="text-xl font-black text-white tracking-tight flex items-center gap-2">
              Contest Elo Rating
            </h3>
          </div>
        </div>

        <div className="flex items-center gap-6 font-mono">
          <div>
            <span className="text-[10px] text-slate-400 uppercase block">Current Rating</span>
            <span className="text-2xl font-black text-amber-400">{data.contest_rating}</span>
          </div>
          <div className="border-l border-slate-800 pl-6">
            <span className="text-[10px] text-slate-400 uppercase block">Highest Rating</span>
            <span className="text-2xl font-black text-emerald-400">{data.highest_rating}</span>
          </div>
        </div>
      </div>

      {/* Rating History List */}
      <div className="space-y-2">
        <h4 className="text-xs font-extrabold uppercase tracking-wider text-slate-400 mb-2">Recent Rating History</h4>
        {data.rating_history.map((h, i) => (
          <div key={i} className="p-3 rounded-2xl bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs font-mono">
            <div>
              <span className="font-bold text-white block">{h.contest_title}</span>
              <span className="text-[10px] text-slate-400">Rank #{h.rank}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-slate-400">{h.old_rating} → {h.new_rating}</span>
              <span className={`font-bold px-2 py-0.5 rounded ${h.rating_delta >= 0 ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"}`}>
                {h.rating_delta >= 0 ? `+${h.rating_delta}` : h.rating_delta}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
