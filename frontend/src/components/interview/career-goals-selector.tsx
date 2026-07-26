"use client";

import React, { useState, useEffect } from "react";
import { Briefcase, Check, GraduationCap, Building2, Trophy, BookOpen, Zap } from "lucide-react";
import { useAuthUser } from "@/hooks/use-auth-user";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

interface CareerGoalItem {
  id: number;
  slug: string;
  title: string;
  description: string;
  icon: string;
  is_selected: boolean;
}

export function CareerGoalsSelector() {
  const { clerkId } = useAuthUser();
  const [goals, setGoals] = useState<CareerGoalItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (clerkId) {
      fetch(`${BACKEND_URL}/interview/goals?clerk_id=${clerkId}`)
        .then((res) => res.json())
        .then((data) => setGoals(data || []))
        .catch((err) => console.error("Error fetching goals:", err))
        .finally(() => setLoading(false));
    }
  }, [clerkId]);

  const toggleGoal = async (slug: string) => {
    const updated = goals.map((g) => (g.slug === slug ? { ...g, is_selected: !g.is_selected } : g));
    setGoals(updated);

    const selectedSlugs = updated.filter((g) => g.is_selected).map((g) => g.slug);
    setSaving(true);

    try {
      await fetch(`${BACKEND_URL}/interview/goals?clerk_id=${clerkId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ goal_slugs: selectedSlugs }),
      });
    } catch (e) {
      console.error("Error updating goals:", e);
    } finally {
      setSaving(false);
    }
  };

  if (loading || goals.length === 0) return null;

  return (
    <div className="border border-card-border rounded-3xl p-6 bg-[#0a0a0f] space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-base font-extrabold text-white flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-cyan-400" />
            Primary Career Goals
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Select one or more targets to personalize your interview preparation roadmap.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
        {goals.map((g) => (
          <button
            key={g.id}
            onClick={() => toggleGoal(g.slug)}
            className={`p-3.5 rounded-2xl text-left border transition-all flex items-start justify-between cursor-pointer ${
              g.is_selected
                ? "bg-cyan-500/10 border-cyan-500 text-white shadow-lg shadow-cyan-500/10"
                : "bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700"
            }`}
          >
            <div>
              <span className="text-xs font-bold block text-white">{g.title}</span>
              <span className="text-[10px] text-slate-400 mt-0.5 block line-clamp-2 leading-relaxed">
                {g.description}
              </span>
            </div>
            {g.is_selected && <Check className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />}
          </button>
        ))}
      </div>
    </div>
  );
}
