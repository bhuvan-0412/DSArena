"use client";

import { useEffect, useState } from "react";
import { useAuthUser } from "@/hooks/use-auth-user";
import { Calendar, CheckCircle2, RefreshCw, Flame, ArrowRight, Loader2 } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

interface RecentActivity {
  id: string;
  type: string;
  title: string;
  topic: string;
  difficulty: string;
  xp: string;
  time: string;
}

interface RevisionTask {
  id: number;
  problem_id: string;
  title: string;
  topic_id: string;
  difficulty: string;
  stage: number;
  scheduled_for: string;
}

const BACKEND_URL = "http://127.0.0.1:8000/api/v1";

export default function RecentProgress() {
  const { stats, isLoaded } = useAuthUser();
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [revisions, setRevisions] = useState<RevisionTask[]>([]);
  const [loading, setLoading] = useState(true);

  const clerkId = stats?.clerk_id || "mock_user_striver";

  useEffect(() => {
    if (!isLoaded) return;

    async function fetchData() {
      try {
        setLoading(true);
        // 1. Fetch revisions
        const revRes = await fetch(`${BACKEND_URL}/roadmap/revisions?clerk_id=${clerkId}`);
        // 2. Fetch recent activity
        const actRes = await fetch(`${BACKEND_URL}/users/${clerkId}/recent-activity`);
        
        if (revRes.ok) {
          const revData = await revRes.json();
          // Merge today and overdue revisions for dashboard display
          setRevisions([...revData.overdue, ...revData.today]);
        }
        
        if (actRes.ok) {
          const actData = await actRes.json();
          setRecentActivities(actData);
        }
      } catch (err) {
        console.error("Error loading recent progress:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [clerkId, isLoaded]);

  const getDifficultyStyles = (diff: string) => {
    switch (diff.toLowerCase()) {
      case "easy": return "bg-success-emerald/10 text-success-emerald border-success-emerald/20";
      case "medium": return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20";
      case "hard": return "bg-primary/10 text-primary border-primary/20";
      case "badge": return "bg-xp-gold/10 text-xp-gold border-xp-gold/20";
      default: return "bg-zinc-800 text-zinc-300 border-zinc-700";
    }
  };

  if (loading) {
    return (
      <div className="border border-card-border rounded-2xl p-6 glass-card flex items-center justify-center min-h-[200px]">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Recent Activities */}
      <div className="lg:col-span-2 border border-card-border rounded-2xl p-6 glass-card">
        <div className="flex items-center gap-2 mb-6">
          <CheckCircle2 className="w-5 h-5 text-success-emerald" />
          <h3 className="text-lg font-bold text-white uppercase tracking-wider">
            Recent Activity
          </h3>
        </div>

        {recentActivities.length === 0 ? (
          <div className="text-center text-xs text-muted-foreground py-10">
            No recent activity recorded yet. Conquer your first arena node!
          </div>
        ) : (
          <div className="space-y-4">
            {recentActivities.map((act) => (
              <div
                key={act.id}
                className="flex justify-between items-center p-4 rounded-xl border border-card-border/50 bg-[#07070b]/40"
              >
                <div className="flex items-center gap-3">
                  <div className="flex flex-col">
                    <span className="text-sm font-bold text-white">{act.title}</span>
                    <span className="text-xs text-muted-foreground">{act.topic}</span>
                  </div>
                </div>
                
                <div className="flex items-center gap-4">
                  <span className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded border ${getDifficultyStyles(act.difficulty)}`}>
                    {act.difficulty}
                  </span>
                  <span className="text-xs font-mono font-bold text-xp-gold">
                    {act.xp}
                  </span>
                  <span className="text-xs text-muted-foreground font-mono hidden md:inline">
                    {act.time}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Revisions Panel */}
      <div className="border border-card-border rounded-2xl p-6 glass-card">
        <div className="flex items-center gap-2 mb-6">
          <RefreshCw className="w-5 h-5 text-info-cyan" />
          <h3 className="text-lg font-bold text-white uppercase tracking-wider">
            Active Revision
          </h3>
        </div>

        {revisions.length === 0 ? (
          <div className="text-center text-xs text-muted-foreground py-10">
            All clear! No pending spaced repetition revisions today.
          </div>
        ) : (
          <div className="space-y-4">
            {revisions.map((rev) => (
              <div
                key={rev.id}
                className="p-4 rounded-xl border border-card-border/50 bg-[#07070b]/40 flex flex-col justify-between"
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-sm font-bold text-white">{rev.title}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-info-cyan/10 text-info-cyan font-mono font-bold uppercase">
                    Stage {rev.stage}
                  </span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-muted-foreground text-[10px]">
                    Spaced repetition review
                  </span>
                  <Link
                    href={`/roadmap/${rev.topic_id}/${rev.problem_id}`}
                    className="text-primary font-bold hover:underline flex items-center gap-1 group"
                  >
                    Review <ArrowRight className="w-3 h-3 transition-transform group-hover:translate-x-0.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
