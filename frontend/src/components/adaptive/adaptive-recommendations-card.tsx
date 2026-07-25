"use client";

import React, { useState, useEffect } from "react";
import { Sparkles, ArrowRight, Lightbulb, RefreshCcw, Briefcase, BookOpen } from "lucide-react";
import Link from "next/link";
import { useAuthUser } from "@/hooks/use-auth-user";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

interface Recommendation {
  id: number;
  type: string;
  title: string;
  description: string;
  target_node_id?: string;
  target_problem_id?: string;
  reason: string;
  priority: string;
}

export function AdaptiveRecommendationsCard() {
  const { clerkId } = useAuthUser();
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (clerkId) {
      fetch(`${BACKEND_URL}/adaptive/recommendations?clerk_id=${clerkId}`)
        .then((res) => res.json())
        .then((data) => setRecommendations(data || []))
        .catch((err) => console.error("Error fetching recommendations:", err))
        .finally(() => setLoading(false));
    }
  }, [clerkId]);

  if (loading || recommendations.length === 0) return null;

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "interview_question": return Briefcase;
      case "revision": return RefreshCcw;
      case "extra_practice": return Lightbulb;
      default: return BookOpen;
    }
  };

  const getTargetLink = (r: Recommendation) => {
    if (r.target_problem_id) return `/roadmap/topic_3_2_1/${r.target_problem_id}`;
    if (r.target_node_id) return `/roadmap/${r.target_node_id}`;
    return `/roadmap`;
  };

  return (
    <div className="border border-card-border rounded-3xl p-6 bg-[#0a0a0f] space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-400" />
          <h3 className="text-base font-bold text-white">Adaptive Learning Recommendations</h3>
        </div>
        <span className="text-[10px] font-mono text-slate-400 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded-md">
          Real-time Engine
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {recommendations.slice(0, 3).map((r) => {
          const Icon = getTypeIcon(r.type);
          return (
            <div
              key={r.id}
              className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-purple-500/40 transition-all flex flex-col justify-between space-y-3 group"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20 flex items-center gap-1">
                    <Icon className="w-3 h-3" /> {r.type.replace("_", " ")}
                  </span>
                </div>
                <h4 className="text-xs font-bold text-white group-hover:text-purple-300 transition-colors">
                  {r.title}
                </h4>
                <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                  {r.description}
                </p>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-800/60">
                <span className="text-[9px] text-slate-500 font-mono truncate max-w-[140px]">{r.reason}</span>
                <Link
                  href={getTargetLink(r)}
                  className="text-xs font-bold text-purple-400 group-hover:text-purple-300 flex items-center gap-1"
                >
                  Action <ArrowRight className="w-3 h-3 transition-transform group-hover:translate-x-1" />
                </Link>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
