"use client";

import React, { useState, useEffect } from "react";
import { Sparkles, Clock, Zap, CheckCircle2, Circle, ArrowRight, Target, Brain, Play } from "lucide-react";
import Link from "next/link";
import { useAuthUser } from "@/hooks/use-auth-user";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

interface TaskItem {
  id: string;
  type: string;
  title: string;
  target_id: string;
  estimated_minutes: number;
  is_completed: boolean;
}

interface PlanData {
  id: number;
  plan_date: string;
  concept_id: string;
  concept_title: string;
  quiz_id: number;
  quiz_title: string;
  tasks: TaskItem[];
  estimated_time_minutes: number;
  xp_reward: number;
  priority_level: string;
  is_completed: boolean;
  completed_tasks_count: number;
  total_tasks_count: number;
}

interface DailyAdaptivePlanCardProps {
  onOpenFocusMode?: () => void;
}

export function DailyAdaptivePlanCard({ onOpenFocusMode }: DailyAdaptivePlanCardProps) {
  const { clerkId } = useAuthUser();
  const [plan, setPlan] = useState<PlanData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (clerkId) {
      fetch(`${BACKEND_URL}/adaptive/daily-plan?clerk_id=${clerkId}`)
        .then((res) => res.json())
        .then((data) => setPlan(data))
        .catch((err) => console.error("Error fetching daily plan:", err))
        .finally(() => setLoading(false));
    }
  }, [clerkId]);

  const toggleTask = async (taskId: string, currentStatus: boolean) => {
    if (!plan) return;

    // Optimistic UI update
    const updatedTasks = plan.tasks.map((t) => (t.id === taskId ? { ...t, is_completed: !currentStatus } : t));
    const completedCount = updatedTasks.filter((t) => t.is_completed).length;
    setPlan({
      ...plan,
      tasks: updatedTasks,
      completed_tasks_count: completedCount,
      is_completed: completedCount === updatedTasks.length,
    });

    try {
      await fetch(`${BACKEND_URL}/adaptive/daily-plan/complete-task?clerk_id=${clerkId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          plan_id: plan.id,
          task_id: taskId,
          is_completed: !currentStatus,
        }),
      });
    } catch (e) {
      console.error("Error completing task:", e);
    }
  };

  if (loading || !plan) {
    return (
      <div className="p-6 rounded-3xl bg-[#0a0a0f] border border-card-border/50 animate-pulse h-48 flex items-center justify-center">
          <span className="text-xs text-[#94a3b8]">Generating Today&apos;s Adaptive Study Plan...</span>
      </div>
    );
  }

  const progressPercent = Math.round((plan.completed_tasks_count / max1(plan.total_tasks_count)) * 100);

  function max1(val: number) {
    return val > 0 ? val : 1;
  }

  const getTaskLink = (task: TaskItem) => {
    if (task.type === "concept") return `/roadmap/${task.target_id}`;
    if (task.type === "quiz") return `/roadmap/${plan.concept_id || "topic_3_2_1"}/quiz`;
    if (task.type === "problem") return `/roadmap/${plan.concept_id || "topic_3_2_1"}/${task.target_id}`;
    return `/dashboard`;
  };

  return (
    <div className="border border-rose-500/30 rounded-3xl p-6 bg-gradient-to-b from-[#0f172a] to-[#0a0a0f] shadow-2xl relative overflow-hidden space-y-5">
      <div className="absolute top-0 right-0 w-64 h-64 bg-rose-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Card Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 relative z-10">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-extrabold uppercase tracking-widest px-2.5 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 flex items-center gap-1">
              <Brain className="w-3 h-3" /> Adaptive Plan
            </span>
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
              {plan.priority_level} Priority
            </span>
          </div>
          <h2 className="text-xl font-black text-white tracking-tight flex items-center gap-2">
            Today&apos;s Personalized Study Plan
          </h2>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="flex items-center gap-1.5 text-xs text-slate-400 justify-end">
              <Clock className="w-3.5 h-3.5 text-cyan-400" />
              <span>{plan.estimated_time_minutes} Mins</span>
            </div>
            <div className="flex items-center gap-1 text-sm font-extrabold text-xp-gold">
              <Zap className="w-4 h-4 fill-xp-gold" />
              <span>+{plan.xp_reward} XP</span>
            </div>
          </div>

          {onOpenFocusMode && (
            <button
              onClick={onOpenFocusMode}
              className="px-3.5 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs uppercase tracking-wider flex items-center gap-1.5 transition-all shadow-lg shadow-rose-600/20 cursor-pointer shrink-0"
            >
              <Play className="w-3.5 h-3.5 fill-white" /> Focus Mode
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-xs font-mono">
          <span className="text-slate-400">Progress Today ({plan.completed_tasks_count}/{plan.total_tasks_count} Tasks)</span>
          <span className="text-rose-400 font-bold">{progressPercent}%</span>
        </div>
        <div className="w-full h-2.5 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
          <div
            className="h-full bg-gradient-to-r from-rose-500 via-purple-500 to-emerald-500 transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Task Checklist */}
      <div className="space-y-2 pt-1">
        {plan.tasks.map((task) => (
          <div
            key={task.id}
            className={`p-3 rounded-2xl border transition-all flex items-center justify-between gap-3 ${
              task.is_completed
                ? "bg-slate-900/40 border-slate-800/60 opacity-70"
                : "bg-slate-900/90 border-slate-800 hover:border-slate-700"
            }`}
          >
            <div className="flex items-center gap-3 min-w-0">
              <button
                onClick={() => toggleTask(task.id, task.is_completed)}
                className="text-slate-400 hover:text-white transition-colors shrink-0"
              >
                {task.is_completed ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400 fill-emerald-400/20" />
                ) : (
                  <Circle className="w-5 h-5" />
                )}
              </button>
              <div className="min-w-0">
                <span
                  className={`text-xs font-semibold block truncate ${
                    task.is_completed ? "line-through text-slate-400" : "text-white"
                  }`}
                >
                  {task.title}
                </span>
                <span className="text-[10px] text-slate-500 font-mono">Est. {task.estimated_minutes} mins</span>
              </div>
            </div>

            <Link
              href={getTaskLink(task)}
              className="text-xs font-bold px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white transition-all flex items-center gap-1 shrink-0"
            >
              Start <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
