"use client";

import { useAuthUser } from "@/hooks/use-auth-user";
import { Flame, Zap, TrendingUp, CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";

export default function StatsGrid() {
  const { stats } = useAuthUser();

  if (!stats) return null;

  const currentLevelXp = stats.xp % 1000;

  const cards = [
    {
      title: "Current Level",
      value: `Level ${stats.level}`,
      desc: `${currentLevelXp} / 1000 XP to next level`,
      icon: Zap,
      color: "text-amber-400 border-amber-500/10 bg-amber-950/5",
      accent: "from-amber-500/20 to-transparent",
    },
    {
      title: "Solving Streak",
      value: `${stats.current_streak} Days`,
      desc: `Best streak: ${stats.max_streak} days`,
      icon: Flame,
      color: "text-orange-500 border-orange-500/10 bg-orange-950/5",
      accent: "from-orange-500/20 to-transparent",
    },
    {
      title: "Total XP Earned",
      value: `${stats.xp.toLocaleString()} XP`,
      desc: "All-time score across problems & quizzes",
      icon: TrendingUp,
      color: "text-cyan-400 border-cyan-500/10 bg-cyan-950/5",
      accent: "from-cyan-500/20 to-transparent",
    },
    {
      title: "Learning Status",
      value: "Active",
      desc: "Striver A2Z Roadmap Progress",
      icon: CheckCircle2,
      color: "text-emerald-400 border-emerald-500/10 bg-emerald-950/5",
      accent: "from-emerald-500/20 to-transparent",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <motion.div
            key={card.title}
            className="border border-slate-800 rounded-2xl p-6 relative overflow-hidden bg-slate-900/60 backdrop-blur-md transition-all duration-300 hover:border-slate-700"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1, duration: 0.4 }}
            whileHover={{ y: -3 }}
          >
            <div className={`absolute top-0 left-0 w-full h-1/2 bg-gradient-to-b ${card.accent} opacity-20 pointer-events-none`} />

            <div className="flex justify-between items-start mb-4">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
                {card.title}
              </span>
              <Icon className={`w-5 h-5 ${card.color.split(" ")[0]}`} />
            </div>

            <div className="relative z-10">
              <h3 className="text-3xl font-black text-white font-mono tracking-tight mb-1">
                {card.value}
              </h3>
              <p className="text-xs text-slate-400 font-medium">
                {card.desc}
              </p>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
