"use client";

import React, { useState, useEffect } from "react";
import { Building2, Check, ArrowRight, ShieldCheck, Clock, Sparkles, Filter } from "lucide-react";
import Link from "next/link";
import { useAuthUser } from "@/hooks/use-auth-user";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

interface CompanyItem {
  id: number;
  slug: string;
  name: string;
  logo_url: string;
  difficulty: string;
  interview_rounds: string[];
  high_frequency_topics: string[];
  recommended_problem_count: number;
  expected_prep_days: number;
  is_selected: boolean;
  readiness_percentage: number;
}

export default function CompaniesPage() {
  const { clerkId } = useAuthUser();
  const [companies, setCompanies] = useState<CompanyItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterDifficulty, setFilterDifficulty] = useState<string>("All");

  useEffect(() => {
    if (clerkId) {
      fetch(`${BACKEND_URL}/interview/companies?clerk_id=${clerkId}`)
        .then((res) => res.json())
        .then((data) => setCompanies(data || []))
        .catch((err) => console.error("Error fetching companies:", err))
        .finally(() => setLoading(false));
    }
  }, [clerkId]);

  const toggleTargetCompany = async (slug: string) => {
    const updated = companies.map((c) => (c.slug === slug ? { ...c, is_selected: !c.is_selected } : c));
    setCompanies(updated);

    const selectedSlugs = updated.filter((c) => c.is_selected).map((c) => c.slug);
    try {
      await fetch(`${BACKEND_URL}/interview/companies?clerk_id=${clerkId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ company_slugs: selectedSlugs }),
      });
    } catch (e) {
      console.error("Error updating target companies:", e);
    }
  };

  const filteredCompanies = companies.filter((c) => {
    if (filterDifficulty === "All") return true;
    return c.difficulty.toLowerCase() === filterDifficulty.toLowerCase();
  });

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <Building2 className="w-10 h-10 text-rose-500 animate-bounce" />
        <span className="text-xs font-mono text-slate-400">Loading Target Companies & Dashboards...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Header Banner */}
      <div className="border border-rose-500/20 rounded-3xl p-8 bg-gradient-to-r from-[#0f172a] via-[#0a0a0f] to-[#030303] relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-rose-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="relative z-10 space-y-2">
          <span className="text-xs font-extrabold uppercase tracking-widest px-3 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/30 inline-flex items-center gap-1.5">
            <Building2 className="w-3.5 h-3.5" /> Target Company Directories
          </span>
          <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight">
            Interview Operating System
          </h1>
          <p className="text-sm text-slate-400 max-w-2xl">
            Select your dream target companies (Amazon, Google, Microsoft, Atlassian, Uber, etc.) to access high-frequency problem sets, interview rounds breakdown, and readiness tracking.
          </p>
        </div>
      </div>

      {/* Difficulty Filter Tabs */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2">
          {["All", "Hard", "Medium", "Easy"].map((diff) => (
            <button
              key={diff}
              onClick={() => setFilterDifficulty(diff)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                filterDifficulty === diff
                  ? "bg-rose-600 text-white shadow-lg shadow-rose-600/20"
                  : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-white"
              }`}
            >
              {diff === "All" ? "All Companies" : `${diff} Tier`}
            </button>
          ))}
        </div>

        <span className="text-xs text-slate-500 font-mono">
          Showing {filteredCompanies.length} Target Companies
        </span>
      </div>

      {/* Company Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCompanies.map((comp) => (
          <div
            key={comp.id}
            className={`p-6 rounded-3xl border transition-all flex flex-col justify-between space-y-5 relative overflow-hidden ${
              comp.is_selected
                ? "bg-gradient-to-b from-[#0f172a] to-[#0a0a0f] border-rose-500/40 shadow-xl shadow-rose-500/5"
                : "bg-[#0a0a0f] border-slate-800/80 hover:border-slate-700"
            }`}
          >
            <div>
              {/* Card Top Row */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center p-2">
                    {/* Fallback logo display */}
                    <span className="font-extrabold text-sm text-rose-400 uppercase">{comp.name.slice(0, 2)}</span>
                  </div>
                  <div>
                    <h3 className="font-extrabold text-base text-white">{comp.name}</h3>
                    <span className="text-[10px] font-mono text-slate-400">{comp.expected_prep_days} Days Prep Time</span>
                  </div>
                </div>

                <button
                  onClick={() => toggleTargetCompany(comp.slug)}
                  className={`px-3 py-1 rounded-xl text-xs font-bold border transition-all flex items-center gap-1.5 cursor-pointer ${
                    comp.is_selected
                      ? "bg-rose-500/20 text-rose-400 border-rose-500/40"
                      : "bg-slate-900 border-slate-800 text-slate-400 hover:text-white"
                  }`}
                >
                  {comp.is_selected && <Check className="w-3.5 h-3.5" />}
                  {comp.is_selected ? "Targeting" : "+ Target"}
                </button>
              </div>

              {/* Company Badges & Stats */}
              <div className="flex items-center gap-2 mb-4">
                <span
                  className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded border ${
                    comp.difficulty === "Hard"
                      ? "bg-red-500/10 text-red-400 border-red-500/30"
                      : comp.difficulty === "Medium"
                      ? "bg-amber-500/10 text-amber-400 border-amber-500/30"
                      : "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                  }`}
                >
                  {comp.difficulty}
                </span>
                <span className="text-[10px] font-semibold text-slate-400 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded">
                  {comp.interview_rounds.length} Interview Rounds
                </span>
                <span className="text-[10px] font-semibold text-purple-400 bg-purple-500/10 border border-purple-500/20 px-2 py-0.5 rounded">
                  {comp.recommended_problem_count} Problems
                </span>
              </div>

              {/* Progress & Readiness Bar */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-400">Prep Readiness</span>
                  <span className="text-rose-400 font-mono">{comp.readiness_percentage}%</span>
                </div>
                <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                  <div
                    className="h-full bg-gradient-to-r from-rose-500 to-emerald-500 transition-all duration-500"
                    style={{ width: `${comp.readiness_percentage}%` }}
                  />
                </div>
              </div>
            </div>

            {/* View Dashboard Button */}
            <div className="pt-2 border-t border-slate-800/80">
              <Link
                href={`/companies/${comp.slug}`}
                className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 hover:text-white font-bold text-xs flex items-center justify-center gap-2 border border-slate-800 transition-all"
              >
                <span>Company Dashboard</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
