"use client";

import React, { useState, useEffect } from "react";
import { Trophy, Clock, Users, ArrowRight, ShieldCheck, Flame, Play, Sparkles, Filter } from "lucide-react";
import Link from "next/link";
import { useAuthUser } from "@/hooks/use-auth-user";
import { RatingChartCard } from "@/components/contest/rating-chart-card";
import { BACKEND_URL } from "@/lib/api-config";


interface ContestItem {
  id: number;
  title: string;
  slug: string;
  contest_type: string;
  description: string;
  difficulty: string;
  duration_minutes: number;
  start_time: string;
  end_time: string;
  prize_xp: number;
  is_active: boolean;
  participant_count: number;
  problem_count: number;
  has_joined: boolean;
  is_ended: boolean;
}

export default function ContestsDirectoryPage() {
  const { clerkId } = useAuthUser();
  const [contests, setContests] = useState<ContestItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>("All");

  useEffect(() => {
    if (clerkId) {
      fetch(`${BACKEND_URL}/contests?clerk_id=${clerkId}`)
        .then((res) => res.json())
        .then((data) => setContests(data || []))
        .catch((err) => console.error("Error fetching contests:", err))
        .finally(() => setLoading(false));
    }
  }, [clerkId]);

  const joinContest = async (contestId: number) => {
    setContests(contests.map((c) => (c.id === contestId ? { ...c, has_joined: true } : c)));
    try {
      await fetch(`${BACKEND_URL}/contests/${contestId}/join?clerk_id=${clerkId}`, { method: "POST" });
    } catch (e) {
      console.error("Error joining contest:", e);
    }
  };

  const startVirtual = async (contestId: number) => {
    try {
      await fetch(`${BACKEND_URL}/contests/${contestId}/start-virtual?clerk_id=${clerkId}`, { method: "POST" });
    } catch (e) {
      console.error("Error starting virtual contest:", e);
    }
  };

  const filteredContests = contests.filter((c) => {
    if (filterType === "All") return true;
    return c.contest_type.toLowerCase() === filterType.toLowerCase();
  });

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <Trophy className="w-10 h-10 text-amber-400 animate-bounce" />
        <span className="text-xs font-mono text-slate-400">Loading Timed Coding Contests...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Header Banner */}
      <div className="border border-amber-500/20 rounded-3xl p-8 bg-gradient-to-r from-[#0f172a] via-[#0a0a0f] to-[#030303] relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 space-y-2">
          <span className="text-xs font-extrabold uppercase tracking-widest px-3 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 inline-flex items-center gap-1.5">
            <Trophy className="w-3.5 h-3.5" /> Competitive Coding Arena
          </span>
          <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight">
            Timed Coding Contests
          </h1>
          <p className="text-sm text-slate-400 max-w-2xl">
            Compete in Codeforces & LeetCode style timed speed challenges. Climb the Elo rating ladder from Beginner to Legend, earn XP bonuses, and replay past contests in Virtual Mode.
          </p>
        </div>
      </div>

      {/* User Contest Rating Card */}
      <RatingChartCard />

      {/* Contest Type Filter Tabs */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2 overflow-x-auto">
          {["All", "Weekly", "Daily", "Company", "Monthly"].map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                filterType === type
                  ? "bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20 font-black"
                  : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-white"
              }`}
            >
              {type === "All" ? "All Contests" : `${type} Contests`}
            </button>
          ))}
        </div>

        <span className="text-xs text-slate-500 font-mono hidden sm:inline">
          Showing {filteredContests.length} Contests
        </span>
      </div>

      {/* Contests Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredContests.map((c) => (
          <div
            key={c.id}
            className={`p-6 rounded-3xl border flex flex-col justify-between space-y-5 relative overflow-hidden transition-all ${
              c.is_active
                ? "bg-gradient-to-b from-[#0f172a] to-[#0a0a0f] border-amber-500/40 shadow-xl shadow-amber-500/5"
                : "bg-[#0a0a0f] border-slate-800/80"
            }`}
          >
            <div>
              {/* Contest Card Top Bar */}
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-extrabold uppercase tracking-widest px-2.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
                  {c.contest_type} Contest
                </span>
                <span className="text-[10px] font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  +{c.prize_xp} XP Prize
                </span>
              </div>

              <h3 className="text-xl font-extrabold text-white mb-1">{c.title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">{c.description}</p>

              {/* Stats Row */}
              <div className="grid grid-cols-3 gap-2 py-3 border-y border-slate-800/80 text-xs font-mono text-slate-300">
                <div className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-amber-400" />
                  <span>{c.duration_minutes} Mins</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Users className="w-3.5 h-3.5 text-cyan-400" />
                  <span>{c.participant_count} Joined</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-purple-400" />
                  <span>{c.problem_count} Problems</span>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="pt-2 flex items-center gap-3">
              {c.is_ended ? (
                <Link
                  href={`/contests/${c.id}/arena`}
                  onClick={() => startVirtual(c.id)}
                  className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs flex items-center justify-center gap-2 border border-slate-700 transition-all"
                >
                  <Play className="w-3.5 h-3.5 text-amber-400" />
                  <span>Virtual Contest Replay</span>
                </Link>
              ) : (
                <>
                  {!c.has_joined ? (
                    <button
                      onClick={() => joinContest(c.id)}
                      className="px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-amber-400 font-bold text-xs hover:bg-slate-800 transition-all cursor-pointer"
                    >
                      Join Contest
                    </button>
                  ) : null}

                  <Link
                    href={`/contests/${c.id}/arena`}
                    className="w-full py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-black text-xs uppercase flex items-center justify-center gap-2 shadow-lg shadow-amber-500/20 transition-all"
                  >
                    <span>Enter Contest Arena</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
