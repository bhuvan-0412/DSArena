"use client";

import React, { useState, useEffect } from "react";
import { Award, Shield, Lock, CheckCircle2, Sparkles, Trophy } from "lucide-react";
import { useAuthUser } from "@/hooks/use-auth-user";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

interface SeasonLevel {
  level: number;
  xp_required: number;
  free_reward: string;
  premium_reward?: string;
  is_unlocked: boolean;
}

interface SeasonPassData {
  season_name: string;
  season_level: number;
  season_xp: number;
  next_level_xp: number;
  levels: SeasonLevel[];
}

export function SeasonPassCard() {
  const { clerkId } = useAuthUser();
  const [data, setData] = useState<SeasonPassData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (clerkId) {
      fetch(`${BACKEND_URL}/engagement/season-pass?clerk_id=${clerkId}`)
        .then((res) => res.json())
        .then((resData) => setData(resData))
        .catch((err) => console.error("Error fetching season pass:", err))
        .finally(() => setLoading(false));
    }
  }, [clerkId]);

  if (loading || !data) return null;

  return (
    <div className="border border-card-border rounded-3xl p-6 bg-[#0a0a0f] space-y-5 relative overflow-hidden">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-extrabold uppercase tracking-widest px-2.5 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/30 flex items-center gap-1">
              <Trophy className="w-3.5 h-3.5" /> Valorant Season Pass
            </span>
            <span className="text-[10px] font-bold text-slate-400 font-mono">
              Level {data.season_level} / 20
            </span>
          </div>
          <h3 className="text-lg font-black text-white tracking-tight">
            {data.season_name}
          </h3>
        </div>

        <div className="text-right font-mono">
          <span className="text-xs text-slate-400">Season XP</span>
          <span className="text-sm font-extrabold text-purple-400 block">{data.season_xp} XP</span>
        </div>
      </div>

      {/* Horizontal Battlepass Track */}
      <div className="flex gap-3 overflow-x-auto no-scrollbar pb-2 pt-1">
        {data.levels.slice(0, 10).map((lvl) => (
          <div
            key={lvl.level}
            className={`min-w-[130px] p-3.5 rounded-2xl border flex flex-col justify-between space-y-2 shrink-0 transition-all ${
              lvl.is_unlocked
                ? "bg-purple-500/10 border-purple-500/50 text-white shadow-lg shadow-purple-500/5"
                : "bg-slate-900/60 border-slate-800 text-slate-500"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono font-bold text-slate-400 uppercase">Lvl {lvl.level}</span>
              {lvl.is_unlocked ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              ) : (
                <Lock className="w-3.5 h-3.5 text-slate-600" />
              )}
            </div>

            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-purple-300 block">Free Reward</span>
              <span className="text-xs font-semibold text-white block truncate">{lvl.free_reward}</span>
            </div>

            <div className="pt-1 border-t border-slate-800/60">
              <span className="text-[9px] font-mono text-slate-500">{lvl.xp_required} XP Req</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
