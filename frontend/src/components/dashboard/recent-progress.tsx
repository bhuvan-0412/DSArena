"use client";

import { useEffect, useState } from "react";
import { useAuthUser } from "@/hooks/use-auth-user";
import { CheckCircle2, Loader2, Video } from "lucide-react";
import { BACKEND_URL } from "@/lib/api-config";

interface RecentActivity {
  id: string;
  type: string;
  title: string;
  topic: string;
  difficulty: string;
  xp: string;
  time: string;
}



export default function RecentProgress() {
  const { stats, isLoaded } = useAuthUser();
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);

  const clerkId = stats?.clerk_id || "mock_user_striver";

  useEffect(() => {
    if (!isLoaded) return;

    async function fetchData() {
      try {
        setLoading(true);
        const actRes = await fetch(`${BACKEND_URL}/users/${clerkId}/recent-activity`);
        
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
    switch ((diff || "").toLowerCase()) {
      case "easy": return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
      case "medium": return "bg-amber-500/10 text-amber-400 border-amber-500/20";
      case "hard": return "bg-rose-500/10 text-rose-400 border-rose-500/20";
      case "badge": return "bg-amber-400/10 text-amber-400 border-amber-400/20";
      default: return "bg-slate-800 text-slate-300 border-slate-700";
    }
  };

  if (loading) {
    return (
      <div className="border border-slate-800 rounded-2xl p-6 bg-slate-900/60 flex items-center justify-center min-h-[160px]">
        <Loader2 className="w-6 h-6 text-cyan-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="border border-slate-800 rounded-2xl p-6 bg-slate-900/60 shadow-lg space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          <h3 className="text-base font-extrabold text-white uppercase tracking-wider">
            Recent Activity
          </h3>
        </div>
        <span className="text-xs font-semibold text-slate-400">
          Completed Tasks & Lessons
        </span>
      </div>

      {recentActivities.length === 0 ? (
        <div className="text-center text-xs text-slate-500 py-8 italic">
          No recent activity recorded yet. Explore the roadmap to get started!
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {recentActivities.map((act) => (
            <div
              key={act.id}
              className="flex justify-between items-center p-3.5 rounded-xl border border-slate-800/80 bg-slate-950/60 hover:bg-slate-950 transition-colors"
            >
              <div className="flex items-center gap-3 min-w-0">
                <Video className="w-4 h-4 text-cyan-400 shrink-0" />
                <div className="flex flex-col min-w-0">
                  <span className="text-xs font-bold text-white truncate">{act.title}</span>
                  <span className="text-[11px] text-slate-400 truncate">{act.topic}</span>
                </div>
              </div>
              
              <div className="flex items-center gap-2.5 shrink-0">
                <span className={`text-[9px] font-extrabold uppercase px-2 py-0.5 rounded border ${getDifficultyStyles(act.difficulty)}`}>
                  {act.difficulty}
                </span>
                <span className="text-xs font-mono font-bold text-amber-400">
                  {act.xp}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
