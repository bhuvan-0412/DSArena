"use client";

import React, { useState, useEffect } from "react";
import { Gift, Flame, Shield, Check, Lock, Sparkles, Zap, Package } from "lucide-react";
import { useAuthUser } from "@/hooks/use-auth-user";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

interface RewardItem {
  day_number: number;
  reward_type: string;
  reward_value: string;
  reward_title: string;
  is_claimed: boolean;
  is_current_day: boolean;
}

interface DailyRewardsData {
  current_streak: number;
  current_day: number;
  rewards: RewardItem[];
  has_streak_freeze: boolean;
  freezes_count: number;
}

interface DailyLoginRewardsCardProps {
  onOpenChestModal?: () => void;
}

export function DailyLoginRewardsCard({ onOpenChestModal }: DailyLoginRewardsCardProps) {
  const { clerkId } = useAuthUser();
  const [data, setData] = useState<DailyRewardsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [claiming, setClaiming] = useState(false);

  useEffect(() => {
    if (clerkId) {
      fetch(`${BACKEND_URL}/engagement/daily-rewards?clerk_id=${clerkId}`)
        .then((res) => res.json())
        .then((resData) => setData(resData))
        .catch((err) => console.error("Error fetching daily rewards:", err))
        .finally(() => setLoading(false));
    }
  }, [clerkId]);

  const claimReward = async (dayNumber: number) => {
    if (!data || claiming) return;
    setClaiming(true);

    try {
      const res = await fetch(`${BACKEND_URL}/engagement/claim-daily-reward?day_number=${dayNumber}&clerk_id=${clerkId}`, {
        method: "POST",
      });
      const result = await res.json();
      if (result.success) {
        setData({
          ...data,
          rewards: data.rewards.map((r) => (r.day_number === dayNumber ? { ...r, is_claimed: true } : r)),
        });
        if (result.reward_type === "chest" && onOpenChestModal) {
          onOpenChestModal();
        }
      }
    } catch (e) {
      console.error("Error claiming reward:", e);
    } finally {
      setClaiming(false);
    }
  };

  if (loading || !data) return null;

  const firstWeekRewards = data.rewards.slice(0, 7);

  return (
    <div className="border border-card-border rounded-3xl p-6 bg-[#0a0a0f] space-y-5 relative overflow-hidden">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-extrabold uppercase tracking-widest px-2.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 flex items-center gap-1">
              <Gift className="w-3.5 h-3.5" /> Daily Rewards Chain
            </span>
            {data.has_streak_freeze && (
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center gap-1">
                <Shield className="w-3 h-3" /> {data.freezes_count} Streak Freeze Active
              </span>
            )}
          </div>
          <h3 className="text-lg font-black text-white tracking-tight flex items-center gap-2">
            7-Day Streak Rewards
          </h3>
        </div>

        <div className="flex items-center gap-1.5 bg-rose-500/10 border border-rose-500/20 px-3 py-1.5 rounded-2xl">
          <Flame className="w-4 h-4 text-rose-500 fill-rose-500" />
          <span className="text-sm font-black font-mono text-white">{data.current_streak} Day Streak</span>
        </div>
      </div>

      {/* 7-Day Reward Chain Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-2.5">
        {firstWeekRewards.map((r) => {
          const canClaim = r.is_current_day && !r.is_claimed;
          return (
            <div
              key={r.day_number}
              className={`p-3 rounded-2xl border text-center flex flex-col justify-between items-center transition-all ${
                r.is_claimed
                  ? "bg-slate-900/40 border-slate-800 text-slate-500"
                  : canClaim
                  ? "bg-gradient-to-b from-amber-500/20 to-[#0a0a0f] border-amber-500/60 shadow-lg shadow-amber-500/10 text-white"
                  : "bg-slate-900/80 border-slate-800/80 text-slate-400"
              }`}
            >
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider">Day {r.day_number}</span>

              <div className="my-2.5 flex items-center justify-center">
                {r.reward_type === "chest" ? (
                  <Package className={`w-6 h-6 ${canClaim ? "text-amber-400 animate-bounce" : "text-amber-500/60"}`} />
                ) : (
                  <Zap className={`w-5 h-5 ${canClaim ? "text-amber-400 fill-amber-400" : "text-slate-500"}`} />
                )}
              </div>

              <span className="text-[11px] font-extrabold block mb-2">{r.reward_title}</span>

              {r.is_claimed ? (
                <span className="text-[9px] font-bold uppercase text-emerald-400 flex items-center justify-center gap-0.5">
                  <Check className="w-3 h-3" /> Claimed
                </span>
              ) : canClaim ? (
                <button
                  onClick={() => claimReward(r.day_number)}
                  disabled={claiming}
                  className="w-full py-1 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-black text-[10px] uppercase transition-all shadow cursor-pointer"
                >
                  Claim
                </button>
              ) : (
                <span className="text-[9px] text-slate-600 font-mono">Locked</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
