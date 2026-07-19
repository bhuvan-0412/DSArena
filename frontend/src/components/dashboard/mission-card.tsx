"use client";

import { useEffect, useState } from "react";
import { useAuthUser } from "@/hooks/use-auth-user";
import { Award, CheckCircle2, Circle, Target, Loader2, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

interface Mission {
  id: string;
  title: string;
  description: string;
  xp_reward: number;
  completed: boolean;
  progress: number;
  target: number;
}

const BACKEND_URL = "http://127.0.0.1:8000/api/v1";

export default function MissionCard() {
  const { user, isLoaded } = useAuthUser();
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(true);

  const clerkId = user?.id || "mock_user_striver";

  useEffect(() => {
    if (!isLoaded) return;

    async function fetchMissions() {
      try {
        setLoading(true);
        const res = await fetch(`${BACKEND_URL}/users/${clerkId}/missions`);
        if (res.ok) {
          const data = await res.json();
          setMissions(data.missions);
        } else {
          // Fallback static data if backend is offline
          setMissions(getFallbackMissions());
        }
      } catch (err) {
        console.error("Error loading missions:", err);
        setMissions(getFallbackMissions());
      } finally {
        setLoading(false);
      }
    }

    fetchMissions();
  }, [clerkId, isLoaded]);

  const getFallbackMissions = (): Mission[] => [
    {
      id: "mission-1",
      title: "Solve 1 Easy Problem",
      description: "Complete any Easy difficulty problem in Arrays or Sorting.",
      xp_reward: 50,
      completed: false,
      progress: 0,
      target: 1,
    },
    {
      id: "mission-2",
      title: "Complete Array Concept notes",
      description: "Read the concept overview for Arrays and Hashing.",
      xp_reward: 20,
      completed: true,
      progress: 1,
      target: 1,
    },
    {
      id: "mission-3",
      title: "Watch Quick-Sort Visualization",
      description: "Watch the sorting algorithm visual walkthrough.",
      xp_reward: 10,
      completed: false,
      progress: 0,
      target: 1,
    },
  ];

  if (loading) {
    return (
      <div className="border border-card-border rounded-2xl p-6 glass-card flex items-center justify-center min-h-[300px]">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    );
  }

  const completedCount = missions.filter((m) => m.completed).length;

  return (
    <div className="border border-card-border rounded-2xl p-6 glass-card relative overflow-hidden flex flex-col justify-between h-full">
      {/* Title Accent */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-3xl pointer-events-none" />

      <div>
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-bold text-white uppercase tracking-wider">
              Today&apos;s Missions
            </h3>
          </div>
          <span className="text-xs font-mono font-bold px-2 py-1 rounded bg-muted text-muted-foreground border border-card-border">
            {completedCount} / {missions.length} COMPLETED
          </span>
        </div>

        {/* Missions List */}
        <div className="space-y-4">
          {missions.map((mission, idx) => (
            <motion.div
              key={mission.id}
              className={`p-4 rounded-xl border flex items-start gap-4 transition-colors ${
                mission.completed
                  ? "bg-success-emerald/5 border-success-emerald/20"
                  : "bg-white/[0.01] border-card-border hover:bg-white/[0.02]"
              }`}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              {/* Completed/Uncompleted checkbox representation */}
              {mission.completed ? (
                <CheckCircle2 className="w-5 h-5 text-success-emerald shrink-0 mt-0.5" />
              ) : (
                <Circle className="w-5 h-5 text-muted-foreground shrink-0 mt-0.5" />
              )}

              <div className="flex-1">
                <div className="flex justify-between items-baseline mb-1">
                  <h4
                    className={`text-sm font-bold ${
                      mission.completed ? "text-success-emerald line-through" : "text-white"
                    }`}
                  >
                    {mission.title}
                  </h4>
                  <span className="text-xs font-mono font-extrabold text-xp-gold">
                    +{mission.xp_reward} XP
                  </span>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {mission.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Bonus Box */}
      {completedCount === missions.length && (
        <motion.div
          className="mt-6 p-4 rounded-xl bg-xp-gold/10 border border-xp-gold/20 flex items-center gap-3 text-xp-gold"
          initial={{ scale: 0.95 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring" }}
        >
          <Sparkles className="w-5 h-5 animate-pulse" />
          <div className="text-xs font-bold">
            All missions cleared! Daily login bonus (+15 XP) unlocked.
          </div>
        </motion.div>
      )}
    </div>
  );
}
