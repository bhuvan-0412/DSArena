"use client";

export const dynamic = "force-dynamic";

import React, { useState, useEffect, use } from "react";
import { Trophy, Clock, ArrowLeft, Play, CheckCircle2, XCircle, Code2, Send, Flame, Shield, Layers } from "lucide-react";
import Link from "next/link";
import { useAuthUser } from "@/hooks/use-auth-user";
import { BACKEND_URL } from "@/lib/api-config";


interface ContestProblemItem {
  id: number;
  contest_id: number;
  problem_id: string;
  problem_order: number;
  points: number;
  title: string;
  difficulty: string;
  editorial_markdown?: string;
}

interface ContestDetailData {
  contest: {
    id: number;
    title: string;
    duration_minutes: number;
    prize_xp: number;
    is_ended: boolean;
  };
  problems: ContestProblemItem[];
  has_joined: boolean;
  is_virtual: boolean;
  time_remaining_seconds: number;
}

export default function ContestArenaPage({ params }: { params: Promise<{ contestId: string }> }) {
  const resolvedParams = use(params);
  const contestId = resolvedParams.contestId;
  const { clerkId } = useAuthUser();

  const [data, setData] = useState<ContestDetailData | null>(null);
  const [activeProblemIdx, setActiveProblemIdx] = useState(0);
  const [code, setCode] = useState("def solve():\n    # Write your contest solution here\n    pass");
  const [language, setLanguage] = useState("python");
  const [submitting, setSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<{ status: string; points_awarded: number; message: string } | null>(null);
  const [timeLeft, setTimeLeft] = useState(3600);

  useEffect(() => {
    if (clerkId && contestId) {
      fetch(`${BACKEND_URL}/contests/${contestId}?clerk_id=${clerkId}`)
        .then((res) => res.json())
        .then((resData) => {
          setData(resData);
          setTimeLeft(resData.time_remaining_seconds || 3600);
        })
        .catch((err) => console.error("Error fetching contest detail:", err));
    }
  }, [clerkId, contestId]);

  // Live Timer Countdown
  useEffect(() => {
    if (timeLeft <= 0) return;
    const timer = setInterval(() => setTimeLeft((prev) => Math.max(0, prev - 1)), 1000);
    return () => clearInterval(timer);
  }, [timeLeft]);

  const handleSubmit = async () => {
    if (!data || submitting) return;
    const currentProb = data.problems[activeProblemIdx];
    if (!currentProb) return;

    setSubmitting(true);
    setSubmitResult(null);

    try {
      const res = await fetch(`${BACKEND_URL}/contests/${contestId}/submit?clerk_id=${clerkId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          problem_id: currentProb.problem_id,
          code: code,
          language: language,
        }),
      });
      const resData = await res.json();
      setSubmitResult(resData);
    } catch (e) {
      console.error("Error submitting contest code:", e);
    } finally {
      setSubmitting(false);
    }
  };

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <Trophy className="w-10 h-10 text-amber-400 animate-spin" />
        <span className="text-xs font-mono text-slate-400">Entering Contest Arena...</span>
      </div>
    );
  }

  const formatTimer = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  const activeProblem = data.problems[activeProblemIdx] || {
    title: "Problem Statement",
    points: 500,
    difficulty: "Medium",
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Top Navigation & Live Timer Bar */}
      <div className="border border-slate-800 rounded-2xl p-4 bg-[#0a0a0f] flex items-center justify-between">
        <Link href="/contests" className="inline-flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-white transition-colors">
          <ArrowLeft className="w-4 h-4" /> Contests Directory
        </Link>

        <div className="flex items-center gap-3">
          <span className="text-xs font-extrabold text-white">{data.contest.title}</span>
          <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
            +{data.contest.prize_xp} XP Prize
          </span>
        </div>

        {/* Live Timer readout */}
        <div className="flex items-center gap-2 bg-amber-500/10 border border-amber-500/30 px-3 py-1.5 rounded-xl">
          <Clock className="w-4 h-4 text-amber-400 animate-pulse" />
          <span className="text-sm font-black font-mono text-amber-400">{formatTimer(timeLeft)}</span>
        </div>
      </div>

      {/* Problem Switcher Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
        {data.problems.map((p, idx) => (
          <button
            key={p.id}
            onClick={() => {
              setActiveProblemIdx(idx);
              setSubmitResult(null);
            }}
            className={`px-4 py-2 rounded-xl text-xs font-extrabold transition-all cursor-pointer flex items-center gap-2 ${
              activeProblemIdx === idx
                ? "bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20"
                : "bg-slate-900 border border-slate-800 text-slate-300 hover:text-white"
            }`}
          >
            <span>Problem {String.fromCharCode(65 + idx)}</span>
            <span className="text-[10px] font-mono opacity-80">({p.points} pts)</span>
          </button>
        ))}
      </div>

      {/* Arena Split View Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Problem Statement & Constraints */}
        <div className="border border-card-border rounded-3xl p-6 bg-[#0a0a0f] space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <span className="text-[10px] font-mono font-bold uppercase text-purple-400">
                Problem {String.fromCharCode(65 + activeProblemIdx)} • {activeProblem.points} Points
              </span>
              <h2 className="text-xl font-extrabold text-white">{activeProblem.title}</h2>
            </div>
            <span className="text-xs font-bold px-2.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
              {activeProblem.difficulty}
            </span>
          </div>

          <div className="space-y-3 text-xs text-slate-300 leading-relaxed font-sans">
            <p>
              Given an array of integers, return the optimal solution within the specified time constraints. All solutions are validated against hidden test cases.
            </p>
            <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800/80 font-mono text-[11px] space-y-1">
              <span className="text-slate-500 uppercase block font-bold">Input Format</span>
              <span className="text-slate-300 block">Standard input containing array elements and target value.</span>
            </div>
            <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800/80 font-mono text-[11px] space-y-1">
              <span className="text-slate-500 uppercase block font-bold">Output Format</span>
              <span className="text-slate-300 block">Return the calculated index array or optimal integer result.</span>
            </div>
          </div>
        </div>

        {/* Right: Code Editor & Judge Submission */}
        <div className="border border-card-border rounded-3xl p-6 bg-[#0a0a0f] space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Code2 className="w-4 h-4 text-amber-400" />
                <span className="text-xs font-bold text-white uppercase">Contest Code Editor</span>
              </div>

              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 px-2.5 py-1 rounded-xl"
              >
                <option value="python">Python 3</option>
                <option value="cpp">C++ 20</option>
                <option value="java">Java 17</option>
                <option value="javascript">JavaScript (Node)</option>
              </select>
            </div>

            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className="w-full h-64 p-4 rounded-2xl bg-slate-950 border border-slate-800 font-mono text-xs text-amber-300 focus:outline-none focus:border-amber-500/50 transition-all resize-none"
              placeholder="Write your contest solution here..."
            />

            {submitResult && (
              <div
                className={`p-3 rounded-2xl border text-xs font-mono flex items-center justify-between ${
                  submitResult.status === "ACCEPTED"
                    ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                    : "bg-red-500/10 border-red-500/30 text-red-400"
                }`}
              >
                <div className="flex items-center gap-2">
                  {submitResult.status === "ACCEPTED" ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <XCircle className="w-4 h-4 text-red-400" />
                  )}
                  <span>{submitResult.message}</span>
                </div>
                {submitResult.points_awarded > 0 && (
                  <span className="font-bold text-amber-400">+{submitResult.points_awarded} Pts</span>
                )}
              </div>
            )}
          </div>

          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="w-full py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-black text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-lg shadow-amber-500/20 cursor-pointer disabled:opacity-50 transition-all"
          >
            <Send className="w-4 h-4" />
            <span>{submitting ? "Judging Solution..." : "Submit Solution"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
