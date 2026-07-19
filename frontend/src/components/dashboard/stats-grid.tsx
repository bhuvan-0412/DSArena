"use client";

import { useAuthUser } from "@/hooks/use-auth-user";
import { Flame, Trophy, Award, Zap, TrendingUp } from "lucide-react";
import { motion } from "framer-motion";

export default function StatsGrid() {
  const { stats } = useAuthUser();

  if (!stats) return null;

  const currentLevelXp = stats.xp % 1000;
  const xpPercentage = (currentLevelXp / 1000) * 100;

  const cards = [
    {
      title: "Current Level",
      value: `Level ${stats.level}`,
      desc: `${currentLevelXp} / 1000 XP to next level`,
      icon: Zap,
      color: "text-xp-gold border-xp-gold/10 bg-yellow-950/5",
      accent: "from-yellow-500/20 to-transparent",
    },
    {
      title: "Arena Rank",
      value: stats.rank,
      desc: "Based on overall progression",
      icon: Trophy,
      color: "text-primary border-primary/10 bg-red-950/5",
      accent: "from-red-500/20 to-transparent",
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
      color: "text-info-cyan border-info-cyan/10 bg-cyan-950/5",
      accent: "from-cyan-500/20 to-transparent",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <motion.div
            key={card.title}
            className={`border rounded-2xl p-6 relative overflow-hidden glass-card transition-all duration-300 hover:border-white/20`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1, duration: 0.5 }}
            whileHover={{ y: -4 }}
          >
            {/* Top gradient glow overlay */}
            <div className={`absolute top-0 left-0 w-full h-1/2 bg-gradient-to-b ${card.accent} opacity-20 pointer-events-none`} />

            <div className="flex justify-between items-start mb-4">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-widest">
                {card.title}
              </span>
              <Icon className={`w-5 h-5 ${card.color.split(" ")[0]}`} />
            </div>

            <div className="relative z-10">
              <h3 className="text-3xl font-black text-white font-mono tracking-tight mb-1">
                {card.value}
              </h3>
              <p className="text-xs text-muted-foreground font-medium">
                {card.desc}
              </p>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
