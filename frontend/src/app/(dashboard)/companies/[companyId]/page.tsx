"use client";

import React, { useState, useEffect, use } from "react";
import { Building2, Check, ArrowLeft, ArrowRight, ShieldCheck, Clock, Layers, Sparkles, CheckCircle2, Circle } from "lucide-react";
import Link from "next/link";
import { useAuthUser } from "@/hooks/use-auth-user";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

interface CompanyDashboardData {
  company: {
    id: number;
    slug: string;
    name: string;
    difficulty: string;
    interview_rounds: string[];
    high_frequency_topics: string[];
    recommended_problem_count: number;
    expected_prep_days: number;
    is_selected: boolean;
    readiness_percentage: number;
  };
  preparation_progress_percentage: number;
  recommended_topics: { id: string; title: string; difficulty: string }[];
  estimated_completion_days: number;
  readiness_percentage: number;
  high_frequency_problems: { id: string; title: string; difficulty: string; topic_id: string; status: string }[];
}

export default function CompanyDashboardPage({ params }: { params: Promise<{ companyId: string }> }) {
  const resolvedParams = use(params);
  const companySlug = resolvedParams.companyId;
  const { clerkId } = useAuthUser();
  const [data, setData] = useState<CompanyDashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (clerkId && companySlug) {
      fetch(`${BACKEND_URL}/interview/companies/${companySlug}?clerk_id=${clerkId}`)
        .then((res) => res.json())
        .then((resData) => setData(resData))
        .catch((err) => console.error("Error fetching company dashboard:", err))
        .finally(() => setLoading(false));
    }
  }, [clerkId, companySlug]);

  if (loading || !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <Building2 className="w-10 h-10 text-rose-500 animate-pulse" />
        <span className="text-xs font-mono text-slate-400">Loading Company Interview Dashboard...</span>
      </div>
    );
  }

  const comp = data.company;

  return (
    <div className="space-y-8 pb-12">
      {/* Back Link */}
      <Link
        href="/companies"
        className="inline-flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Target Companies Directory
      </Link>

      {/* Header Banner */}
      <div className="border border-rose-500/20 rounded-3xl p-8 bg-gradient-to-r from-[#0f172a] via-[#0a0a0f] to-[#030303] relative overflow-hidden space-y-6">
        <div className="absolute top-0 right-0 w-80 h-80 bg-rose-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-extrabold uppercase tracking-widest px-3 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/30 flex items-center gap-1.5">
                <Building2 className="w-3.5 h-3.5" /> Company Prep Dashboard
              </span>
              <span className="text-xs font-bold uppercase px-2.5 py-0.5 rounded border border-purple-500/30 bg-purple-500/10 text-purple-300">
                {comp.difficulty} Tier
              </span>
            </div>
            <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight flex items-center gap-3">
              {comp.name} Interview Prep
            </h1>
            <p className="text-xs text-slate-400 font-mono">
              Est. Prep Time: {comp.expected_prep_days} Days • Recommended Problems: {comp.recommended_problem_count}
            </p>
          </div>

          <div className="flex items-center gap-4 bg-slate-900/80 border border-slate-800 rounded-2xl p-4">
            <div className="text-right">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Company Readiness</span>
              <span className="text-2xl font-black font-mono text-rose-400">{data.readiness_percentage}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Interview Rounds Timeline */}
      <div className="border border-card-border rounded-3xl p-6 bg-[#0a0a0f] space-y-4">
        <h3 className="text-base font-extrabold text-white flex items-center gap-2">
          <Layers className="w-5 h-5 text-rose-400" />
          {comp.name} Interview Process & Rounds
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {comp.interview_rounds.map((round, idx) => (
            <div
              key={idx}
              className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2 relative"
            >
              <span className="text-[10px] font-mono font-bold uppercase text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
                Round {idx + 1}
              </span>
              <h4 className="text-xs font-bold text-white leading-snug">{round}</h4>
            </div>
          ))}
        </div>
      </div>

      {/* High Frequency Topics & Problems Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recommended Topics */}
        <div className="border border-card-border rounded-3xl p-6 bg-[#0a0a0f] space-y-4">
          <h3 className="text-base font-extrabold text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-400" />
            High Frequency Topics
          </h3>
          <div className="space-y-2.5">
            {data.recommended_topics.map((t) => (
              <div key={t.id} className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold text-white block">{t.title}</span>
                  <span className="text-[10px] text-purple-400 font-mono">Priority Focus</span>
                </div>
                <Link
                  href={`/roadmap/${t.id}`}
                  className="text-xs font-bold text-rose-400 hover:text-rose-300 flex items-center gap-1"
                >
                  View <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            ))}
          </div>
        </div>

        {/* High Frequency Problems */}
        <div className="lg:col-span-2 border border-card-border rounded-3xl p-6 bg-[#0a0a0f] space-y-4">
          <h3 className="text-base font-extrabold text-white flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            Top High-Frequency Interview Problems
          </h3>
          <div className="space-y-2.5">
            {data.high_frequency_problems.map((p) => {
              const isSolved = p.status === "solved" || p.status === "mastered";
              return (
                <div
                  key={p.id}
                  className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    {isSolved ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                    ) : (
                      <Circle className="w-5 h-5 text-slate-500 shrink-0" />
                    )}
                    <div>
                      <span className="text-xs font-bold text-white block">{p.title}</span>
                      <span className="text-[10px] text-slate-400 font-mono">Difficulty: {p.difficulty}</span>
                    </div>
                  </div>

                  <Link
                    href={`/roadmap/${p.topic_id}/${p.id}`}
                    className="px-3 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs flex items-center gap-1 transition-all"
                  >
                    Solve Problem <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
