"use client";

import React, { useState, useEffect } from "react";
import { ShieldCheck, Award, TrendingUp, AlertCircle, Sparkles, CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";
import { useAuthUser } from "@/hooks/use-auth-user";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

interface ReadinessData {
  overall_score: number;
  confidence_level: string;
  topic_coverage_score: number;
  problem_completion_score: number;
  quiz_accuracy_score: number;
  revision_completion_score: number;
  company_scores: Record<string, number>;
  suggestions: string[];
}

export function ReadinessGaugeCard() {
  const { clerkId } = useAuthUser();
  const [data, setData] = useState<ReadinessData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (clerkId) {
      fetch(`${BACKEND_URL}/interview/readiness?clerk_id=${clerkId}`)
        .then((res) => res.json())
        .then((resData) => setData(resData))
        .catch((err) => console.error("Error fetching readiness:", err))
        .finally(() => setLoading(false));
    }
  }, [clerkId]);

  if (loading || !data) {
    return (
      <div className="p-6 rounded-3xl bg-[#0a0a0f] border border-card-border/50 animate-pulse h-48 flex items-center justify-center">
        <span className="text-xs text-muted-foreground font-mono">Computing Interview Readiness Score...</span>
      </div>
    );
  }

  const score = data.overall_score || 0;
  const strokeDash = 402 - (402 * score) / 100;

  const getConfidenceBadgeColor = (level: string) => {
    switch (level) {
      case "Interview Ready":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
      case "On Track":
        return "bg-cyan-500/10 text-cyan-400 border-cyan-500/30";
      case "Needs Reinforcement":
        return "bg-amber-500/10 text-amber-400 border-amber-500/30";
      default:
        return "bg-purple-500/10 text-purple-400 border-purple-500/30";
    }
  };

  return (
    <div className="border border-card-border rounded-3xl p-6 bg-[#0a0a0f] relative overflow-hidden space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-extrabold uppercase tracking-widest px-2.5 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" /> Interview OS
            </span>
            <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${getConfidenceBadgeColor(data.confidence_level)}`}>
              {data.confidence_level}
            </span>
          </div>
          <h3 className="text-lg font-black text-white tracking-tight">
            Interview Readiness Score
          </h3>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
        {/* Animated Circular Gauge */}
        <div className="flex flex-col items-center justify-center py-2">
          <div className="relative w-36 h-36 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="72"
                cy="72"
                r="64"
                className="stroke-[#12121f] fill-none"
                strokeWidth="10"
              />
              <motion.circle
                cx="72"
                cy="72"
                r="64"
                className="stroke-rose-500 fill-none"
                strokeWidth="10"
                strokeDasharray="402"
                initial={{ strokeDashoffset: 402 }}
                animate={{ strokeDashoffset: strokeDash }}
                transition={{ duration: 1.2, ease: "easeOut" }}
              />
            </svg>
            <div className="absolute flex flex-col items-center">
              <span className="text-4xl font-black text-white font-mono">{score}%</span>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Readiness</span>
            </div>
          </div>
        </div>

        {/* Score Breakdown Bars */}
        <div className="md:col-span-2 space-y-3">
          {[
            { label: "Topic Coverage", val: data.topic_coverage_score, weight: "25%" },
            { label: "Problem Completion", val: data.problem_completion_score, weight: "35%" },
            { label: "Quiz Accuracy", val: data.quiz_accuracy_score, weight: "15%" },
            { label: "Revision Schedule", val: data.revision_completion_score, weight: "15%" },
          ].map((item) => (
            <div key={item.label} className="space-y-1">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-slate-300">{item.label} <span className="text-[10px] text-slate-500">({item.weight})</span></span>
                <span className="text-rose-400 font-mono">{item.val}%</span>
              </div>
              <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                <div className="h-full bg-rose-500 transition-all duration-500" style={{ width: `${item.val}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Improvement Suggestions */}
      {data.suggestions && data.suggestions.length > 0 && (
        <div className="p-3.5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1.5">
          <div className="text-[11px] font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5" /> Actionable Improvement Tips
          </div>
          <ul className="space-y-1">
            {data.suggestions.map((s, idx) => (
              <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                <span className="text-rose-500 font-bold">•</span> {s}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
