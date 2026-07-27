"use client";

import React from "react";
import { useAuthUser } from "@/hooks/use-auth-user";
import { ShieldCheck, User, Mail, Sparkles, CheckCircle, LogOut } from "lucide-react";
import { motion } from "framer-motion";

export default function SettingsPage() {
  const { user, userDisplayName, userEmail, userAvatarUrl, userUsername, stats, signOut } = useAuthUser();

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8 font-sans">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
          <Sparkles className="w-7 h-7 text-cyan-400" /> Account Settings
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Manage your Supabase Authentication profile, security credentials, and preferences.
        </p>
      </div>

      {/* User Profile Card */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md space-y-6"
      >
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <User className="w-5 h-5 text-indigo-400" /> Identity Profile
        </h2>

        <div className="flex flex-col sm:flex-row items-center gap-6">
          <img
            src={userAvatarUrl}
            alt={userDisplayName}
            className="w-20 h-20 rounded-2xl border-2 border-cyan-500/30 object-cover shadow-lg"
            onError={(e) => {
              (e.target as HTMLElement).setAttribute(
                "src",
                `https://api.dicebear.com/7.x/bottts/svg?seed=${userEmail}`
              );
            }}
          />

          <div className="space-y-1.5 text-center sm:text-left flex-1">
            <h3 className="text-xl font-extrabold text-white">{userDisplayName}</h3>
            <p className="text-sm text-slate-400 font-mono flex items-center gap-2 justify-center sm:justify-start">
              <Mail className="w-4 h-4 text-cyan-400" /> {userEmail}
            </p>
            <div className="flex items-center gap-2 pt-1 justify-center sm:justify-start">
              <span className="px-2.5 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold flex items-center gap-1">
                <CheckCircle className="w-3 h-3" /> Supabase OAuth Active
              </span>
              <span className="px-2.5 py-0.5 rounded-md bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-mono font-bold">
                Level {stats?.level || 1}
              </span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Auth Security Details */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md space-y-6"
      >
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-emerald-400" /> Security & Session
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-1">
            <span className="text-slate-400">Authenticated User ID:</span>
            <p className="text-white truncate font-bold">{user?.id || stats?.clerk_id || "N/A"}</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-1">
            <span className="text-slate-400">Auth Provider:</span>
            <p className="text-cyan-400 font-bold">Google OAuth 2.0 (Supabase Auth)</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-1">
            <span className="text-slate-400">Username:</span>
            <p className="text-white font-bold">{userUsername}</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 space-y-1">
            <span className="text-slate-400">Current Streak:</span>
            <p className="text-amber-400 font-bold">{stats?.current_streak || 0} Days 🔥</p>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-800 flex justify-end">
          <button
            onClick={() => signOut()}
            className="px-6 py-3 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-400 font-extrabold text-xs uppercase tracking-wider flex items-center gap-2 transition-all cursor-pointer"
          >
            <LogOut className="w-4 h-4" /> Sign Out of DSArena
          </button>
        </div>
      </motion.div>
    </div>
  );
}
