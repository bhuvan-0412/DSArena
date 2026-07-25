"use client";

import React, { useState, useEffect } from "react";
import { Briefcase, Clock, Sliders, Code2, Sparkles, Check, Save } from "lucide-react";
import { useAuthUser } from "@/hooks/use-auth-user";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

interface PreferencesData {
  target_company: string;
  daily_time_available_minutes: number;
  difficulty_preference: string;
  learning_style: string;
  favorite_language: string;
  most_productive_time: string;
}

export function UserPreferencesForm() {
  const { clerkId } = useAuthUser();
  const [targetCompany, setTargetCompany] = useState("FAANG / Top Tech");
  const [dailyTime, setDailyTime] = useState(60);
  const [difficulty, setDifficulty] = useState("Adaptive");
  const [learningStyle, setLearningStyle] = useState("Visual & Hands-on");
  const [favoriteLang, setFavoriteLang] = useState("python");
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    if (clerkId) {
      fetch(`${BACKEND_URL}/adaptive/preferences?clerk_id=${clerkId}`)
        .then((res) => res.json())
        .then((data: PreferencesData) => {
          if (data) {
            setTargetCompany(data.target_company || "FAANG / Top Tech");
            setDailyTime(data.daily_time_available_minutes || 60);
            setDifficulty(data.difficulty_preference || "Adaptive");
            setLearningStyle(data.learning_style || "Visual & Hands-on");
            setFavoriteLang(data.favorite_language || "python");
          }
        })
        .catch((err) => console.error("Error fetching preferences:", err));
    }
  }, [clerkId]);

  const handleSave = async () => {
    setSaving(true);
    setSavedSuccess(false);
    try {
      await fetch(`${BACKEND_URL}/adaptive/preferences?clerk_id=${clerkId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target_company: targetCompany,
          daily_time_available_minutes: dailyTime,
          difficulty_preference: difficulty,
          learning_style: learningStyle,
          favorite_language: favoriteLang,
        }),
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (e) {
      console.error("Error saving preferences:", e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="border border-card-border rounded-3xl p-6 bg-[#0a0a0f] space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h3 className="text-lg font-extrabold text-white flex items-center gap-2">
            <Sliders className="w-5 h-5 text-rose-400" />
            Adaptive Learning Preferences
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Configure your target goal, study time, dynamic difficulty, and favorite language.
          </p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-rose-600/20 transition-all cursor-pointer disabled:opacity-50"
        >
          {savedSuccess ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
          {savedSuccess ? "Saved!" : "Save Preferences"}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Target Company */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <Briefcase className="w-4 h-4 text-cyan-400" /> Target Company / Tier
          </label>
          <select
            value={targetCompany}
            onChange={(e) => setTargetCompany(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 text-white rounded-xl p-3 text-xs focus:outline-none focus:border-rose-500/50"
          >
            <option value="FAANG / Top Tech">FAANG / Top Tech (Google, Meta, Amazon, Microsoft)</option>
            <option value="High Growth Unicorns">High Growth Unicorns (Stripe, Uber, Airbnb)</option>
            <option value="Product Startups">Fast Paced Product Startups</option>
            <option value="General DSA Mastery">General DSA Mastery & Competitions</option>
          </select>
        </div>

        {/* Daily Time Available */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <Clock className="w-4 h-4 text-amber-400" /> Daily Time Available
          </label>
          <select
            value={dailyTime}
            onChange={(e) => setDailyTime(Number(e.target.value))}
            className="w-full bg-slate-900 border border-slate-800 text-white rounded-xl p-3 text-xs focus:outline-none focus:border-rose-500/50"
          >
            <option value={30}>30 Minutes / Day (Quick Sprint)</option>
            <option value={60}>60 Minutes / Day (Balanced Standard)</option>
            <option value={90}>90 Minutes / Day (Intensive Prep)</option>
            <option value={120}>120+ Minutes / Day (Full Hardcore Mode)</option>
          </select>
        </div>

        {/* Difficulty Preference */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-purple-400" /> Difficulty Scaling Mode
          </label>
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 text-white rounded-xl p-3 text-xs focus:outline-none focus:border-rose-500/50"
          >
            <option value="Adaptive">Adaptive (Auto-scales based on performance)</option>
            <option value="Easy">Beginner Friendly (Easy focus)</option>
            <option value="Medium">Interview Standard (Medium focus)</option>
            <option value="Hard">Hardcore FAANG (Hard focus)</option>
          </select>
        </div>

        {/* Favorite Language */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <Code2 className="w-4 h-4 text-emerald-400" /> Primary Programming Language
          </label>
          <select
            value={favoriteLang}
            onChange={(e) => setFavoriteLang(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 text-white rounded-xl p-3 text-xs focus:outline-none focus:border-rose-500/50"
          >
            <option value="python">Python 3</option>
            <option value="cpp">C++ (GCC 11)</option>
            <option value="java">Java 17</option>
            <option value="javascript">JavaScript (Node.js)</option>
          </select>
        </div>
      </div>
    </div>
  );
}
