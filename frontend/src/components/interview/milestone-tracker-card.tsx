"use client";

import React, { useState, useEffect } from "react";
import { Trophy, Award, CheckCircle2, Lock, Zap, ShieldCheck } from "lucide-react";
import { useAuthUser } from "@/hooks/use-auth-user";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

interface MilestoneItem {
  id: number;
  slug: string;
  title: string;
  description: string;
  icon: string;
  xp_reward: number;
  badge_name: string;
  is_completed: boolean;
}

export function MilestoneTrackerCard() {
  const { clerkId } = useAuthUser();
  const [milestones, setMilestones] = useState<MilestoneItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (clerkId) {
      fetch(`${BACKEND_URL}/interview/milestones?clerk_id=${clerkId}`)
        .then((res) => res.json())
        .then((data) => setMilestones(data || []))
        .catch((err) => console.error("Error fetching milestones:", err))
        .finally(() => setLoading(false));
    }
  }, [clerkId]);

  if (loading || milestones.length === 0) return null;

  return (
    <div className="border border-card-border rounded-3xl p-6 bg-[#0a0a0f] space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Trophy className="w-5 h-5 text-amber-400" />
          <h3 className="text-base font-extrabold text-white">Interview Prep Milestones</h3>
        </div>
        <span className="text-xs font-mono font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-0.5 rounded-md">
          {milestones.filter((m) => m.is_completed).length} / {milestones.length} Unlocked
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {milestones.map((m) => (
          <div
            key={m.id}
            className={`p-4 rounded-2xl border transition-all flex items-start justify-between gap-3 ${
              m.is_completed
                ? "bg-amber-500/10 border-amber-500/40 text-white"
                : "bg-slate-900/60 border-slate-800 text-slate-400 opacity-75"
            }`}
          >
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-white">{m.title}</span>
                {m.is_completed && <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />}
              </div>
              <p className="text-[11px] text-slate-400 leading-snug">{m.description}</p>
              <div className="flex items-center gap-2 pt-1">
                <span className="text-[10px] font-mono font-extrabold text-amber-400 flex items-center gap-1">
                  <Zap className="w-3 h-3 fill-amber-400" /> +{m.xp_reward} XP
                </span>
                <span className="text-[10px] font-semibold text-purple-400 bg-purple-500/10 px-1.5 py-0.5 rounded border border-purple-500/20">
                  {m.badge_name}
                </span>
              </div>
            </div>

            {!m.is_completed && <Lock className="w-4 h-4 text-slate-600 shrink-0 mt-1" />}
          </div>
        ))}
      </div>
    </div>
  );
}
