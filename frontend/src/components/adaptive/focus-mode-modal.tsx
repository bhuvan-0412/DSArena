"use client";

import React, { useState, useEffect } from "react";
import { Play, Pause, RotateCcw, X, Target, CheckCircle2, Circle, Coffee, Zap, Shield, Sparkles } from "lucide-react";
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

interface FocusSessionConfig {
  today_goal: string;
  session_duration_minutes: number;
  break_duration_minutes: number;
  recommended_tasks: TaskItem[];
  target_company: string;
  xp_bonus: number;
}

interface FocusModeModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function FocusModeModal({ isOpen, onClose }: FocusModeModalProps) {
  const { clerkId } = useAuthUser();
  const [config, setConfig] = useState<FocusSessionConfig | null>(null);
  const [secondsLeft, setSecondsLeft] = useState(25 * 60);
  const [isActive, setIsActive] = useState(false);
  const [isBreak, setIsBreak] = useState(false);
  const [tasks, setTasks] = useState<TaskItem[]>([]);

  useEffect(() => {
    if (isOpen && clerkId) {
      fetch(`${BACKEND_URL}/adaptive/focus-session?clerk_id=${clerkId}`)
        .then((res) => res.json())
        .then((data: FocusSessionConfig) => {
          setConfig(data);
          setSecondsLeft(data.session_duration_minutes * 60);
          setTasks(data.recommended_tasks || []);
        })
        .catch((err) => console.error("Error fetching focus session:", err));
    }
  }, [isOpen, clerkId]);

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    if (isActive && secondsLeft > 0) {
      interval = setInterval(() => {
        setSecondsLeft((sec) => sec - 1);
      }, 1000);
    } else if (secondsLeft === 0 && isActive) {
      if (!isBreak) {
        setIsBreak(true);
        setSecondsLeft((config?.break_duration_minutes || 5) * 60);
      } else {
        setIsBreak(false);
        setSecondsLeft((config?.session_duration_minutes || 25) * 60);
        setIsActive(false);
      }
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isActive, secondsLeft, isBreak, config]);

  if (!isOpen) return null;

  const minutes = Math.floor(secondsLeft / 60);
  const seconds = secondsLeft % 60;
  const timeFormatted = `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;

  const toggleTask = (taskId: string) => {
    setTasks(tasks.map((t) => (t.id === taskId ? { ...t, is_completed: !t.is_completed } : t)));
  };

  const completedCount = tasks.filter((t) => t.is_completed).length;

  return (
    <div className="fixed inset-0 bg-black/90 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-[#0f172a] text-slate-100 border border-slate-800 max-w-2xl w-full shadow-2xl rounded-3xl p-8 relative space-y-6">
        <button
          onClick={onClose}
          className="absolute top-6 right-6 text-slate-400 hover:text-white p-2 rounded-xl bg-slate-900 border border-slate-800"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Focus Header */}
        <div className="text-center space-y-2">
          <span className="text-[10px] font-extrabold uppercase tracking-widest px-3 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/30 inline-flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5" /> Distraction-Free Focus Session
          </span>
          <h2 className="text-2xl font-black text-white tracking-tight">
            {config?.today_goal || "Complete Today's Adaptive Plan"}
          </h2>
          <p className="text-xs text-slate-400">
            Targeting <span className="text-rose-400 font-bold">{config?.target_company || "FAANG"}</span> • Complete to earn +{config?.xp_bonus || 50} XP Bonus
          </p>
        </div>

        {/* Timer Display */}
        <div className="bg-slate-950 border border-slate-800 rounded-3xl p-8 text-center relative overflow-hidden space-y-4">
          <div className="absolute inset-0 bg-rose-500/5 blur-2xl pointer-events-none" />
          
          <div className="flex justify-center items-center gap-2 text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
            {isBreak ? (
              <span className="text-emerald-400 flex items-center gap-1">
                <Coffee className="w-4 h-4" /> Break Time ({config?.break_duration_minutes || 5} Mins)
              </span>
            ) : (
              <span className="text-rose-400 flex items-center gap-1">
                <Zap className="w-4 h-4 fill-rose-400" /> Deep Work Pomodoro ({config?.session_duration_minutes || 25} Mins)
              </span>
            )}
          </div>

          <div className="text-6xl font-black font-mono tracking-tighter text-white drop-shadow-lg">
            {timeFormatted}
          </div>

          <div className="flex justify-center items-center gap-3 pt-2">
            <button
              onClick={() => setIsActive(!isActive)}
              className="px-6 py-2.5 rounded-2xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-sm uppercase tracking-wider flex items-center gap-2 shadow-lg shadow-rose-600/20 cursor-pointer transition-all"
            >
              {isActive ? <Pause className="w-4 h-4 fill-white" /> : <Play className="w-4 h-4 fill-white" />}
              {isActive ? "Pause" : "Start Session"}
            </button>
            <button
              onClick={() => {
                setIsActive(false);
                setSecondsLeft((config?.session_duration_minutes || 25) * 60);
              }}
              className="p-2.5 rounded-2xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-all"
              title="Reset Timer"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Task Progress inside Focus Session */}
        <div className="space-y-3">
          <div className="flex justify-between items-center text-xs font-semibold">
            <span className="text-slate-300">Session Goal Progress</span>
            <span className="text-rose-400 font-mono">{completedCount} / {tasks.length} Completed</span>
          </div>
          <div className="space-y-2 max-h-48 overflow-y-auto no-scrollbar">
            {tasks.map((t) => (
              <div
                key={t.id}
                onClick={() => toggleTask(t.id)}
                className={`p-3 rounded-2xl border transition-all flex items-center justify-between cursor-pointer ${
                  t.is_completed
                    ? "bg-slate-900/40 border-slate-800 text-slate-400 line-through"
                    : "bg-slate-900 border-slate-800 text-white hover:border-slate-700"
                }`}
              >
                <div className="flex items-center gap-3">
                  {t.is_completed ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  ) : (
                    <Circle className="w-4 h-4 text-slate-500 shrink-0" />
                  )}
                  <span className="text-xs font-semibold">{t.title}</span>
                </div>
                <span className="text-[10px] font-mono text-slate-500">{t.estimated_minutes}m</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
