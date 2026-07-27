"use client";

import Link from "next/link";
import { Compass, Flame, Sparkles, Sword, Trophy, Zap, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";
import { useAuthUser } from "@/hooks/use-auth-user";

export default function LandingPage() {
  const { isSignedIn } = useAuthUser();

  const features = [
    {
      title: "Duolingo for DSA",
      desc: "Bite-sized problem solving, XP logging, level progression, and daily streaks to make learning fun and consistent.",
      icon: Zap,
      color: "text-yellow-500 bg-yellow-500/10 border-yellow-500/20",
    },
    {
      title: "Striver A2Z Roadmap",
      desc: "Direct integration with the legendary Striver A2Z roadmap structure. Clear progression nodes from Arrays to Segment Trees.",
      icon: Compass,
      color: "text-primary bg-primary/10 border-primary/20",
    },
    {
      title: "Streak Reinforcement",
      desc: "Visual daily streaks, active revision queues, and XP bonuses to lock in your daily coding habits.",
      icon: Flame,
      color: "text-orange-500 bg-orange-500/10 border-orange-500/20",
    },
    {
      title: "Unlocks & Badges",
      desc: "Unlock Achievements like 'Night Owl' or 'DP Overlord' to showcase your mastery on your gladiator profile.",
      icon: Trophy,
      color: "text-info-cyan bg-info-cyan/10 border-info-cyan/20",
    },
  ];

  return (
    <div className="min-h-screen bg-[#030303] text-slate-100 flex flex-col justify-between relative overflow-hidden">
      
      {/* Background glowing blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-primary/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-info-cyan/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header / Navbar */}
      <header className="container mx-auto px-6 py-6 flex justify-between items-center relative z-10 border-b border-card-border/30 bg-black/20 backdrop-blur-sm sticky top-0">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center font-black text-white text-lg shadow-lg shadow-primary/20">
            Ω
          </div>
          <span className="font-extrabold text-xl tracking-wider">
            DS<span className="text-primary">ARENA</span>
          </span>
        </div>

        <div className="flex items-center gap-4">
          <Link href="/roadmap" className="text-xs uppercase font-extrabold tracking-widest hover:text-white text-muted-foreground transition-colors hidden md:inline">
            Explore Roadmap
          </Link>
          <Link href="/dashboard">
            <button className="px-5 py-2.5 rounded-xl bg-primary hover:bg-primary/95 text-white font-bold text-xs uppercase tracking-wider transition-all duration-300 shadow-md shadow-primary/10 hover:shadow-primary/25 cursor-pointer">
              {isSignedIn ? "Enter Arena" : "Join Arena"}
            </button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-6 py-20 flex-1 flex flex-col items-center justify-center text-center relative z-10 space-y-10">
        <div className="space-y-6 max-w-4xl">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary font-bold text-[10px] uppercase tracking-widest mb-2"
          >
            <Sparkles className="w-3.5 h-3.5" /> Gamified DSA Conquest
          </motion.div>
          
          <motion.h1
            className="text-4xl md:text-7xl font-extrabold tracking-tight leading-none text-white uppercase"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.6 }}
          >
            NOT another <br className="hidden md:inline" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-orange-500 to-xp-gold">DSA sheet</span>.
          </motion.h1>
          
          <motion.p
            className="text-sm md:text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            DSArena merges the gamification of Duolingo, the competitiveness of Valorant ranks, and the structure of Striver&apos;s A2Z Roadmap into a premium RPG learning platform.
          </motion.p>
        </div>

        {/* Action CTAs */}
        <motion.div
          className="flex flex-col sm:flex-row gap-4"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          <Link href="/dashboard">
            <button className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-primary hover:bg-primary/90 text-white font-extrabold text-sm tracking-wider uppercase flex items-center justify-center gap-3 transition-all duration-300 shadow-lg shadow-primary/20 cursor-pointer">
              <Sword className="w-4 h-4" />
              <span>Begin Your Quest</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </Link>
          <Link href="/roadmap">
            <button className="w-full sm:w-auto px-8 py-4 rounded-2xl border border-card-border hover:border-white/10 hover:bg-white/[0.01] text-white font-bold text-sm tracking-wider uppercase flex items-center justify-center gap-2 transition-colors cursor-pointer">
              <Compass className="w-4 h-4" />
              <span>View Roadmap Path</span>
            </button>
          </Link>
        </motion.div>

        {/* Floating Mock Card Previews */}
        <motion.div
          className="w-full max-w-5xl pt-10"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.8 }}
        >
          <div className="border border-card-border rounded-2xl overflow-hidden glass-card shadow-2xl relative shadow-black/80">
            {/* Top window controls */}
            <div className="h-10 bg-black/40 border-b border-card-border flex items-center px-4 gap-2">
              <div className="w-2.5 h-2.5 rounded-full bg-red-500/60" />
              <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/60" />
              <div className="w-2.5 h-2.5 rounded-full bg-green-500/60" />
              <span className="text-[10px] font-mono text-muted-foreground ml-4">dsarena.com/dashboard</span>
            </div>

            {/* Inner image representation */}
            <div className="p-8 grid grid-cols-1 md:grid-cols-3 gap-6 bg-[#030303]/90 text-left">
              {/* Profile Card Mock */}
              <div className="border border-card-border p-5 rounded-xl bg-white/[0.01] flex flex-col justify-between h-40">
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-2.5">
                    <div className="w-9 h-9 rounded-full bg-primary flex items-center justify-center font-bold text-white text-xs">S</div>
                    <div>
                      <h4 className="text-xs font-bold text-white">Striver Ninja</h4>
                      <span className="text-[9px] text-muted-foreground">Level 2 Gladiator</span>
                    </div>
                  </div>
                  <span className="text-[9px] font-mono font-bold text-orange-500 border border-orange-500/20 bg-orange-900/10 px-1.5 py-0.5 rounded">
                    5 DAY STREAK
                  </span>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-[9px] text-muted-foreground">
                    <span>XP Progress</span>
                    <span>450 / 1000 XP</span>
                  </div>
                  <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
                    <div className="h-full bg-xp-gold w-[45%]" />
                  </div>
                </div>
              </div>

              {/* Node Card Mock */}
              <div className="border border-card-border p-5 rounded-xl bg-white/[0.01] flex flex-col justify-between h-40">
                <div>
                  <div className="flex justify-between text-[10px] font-bold text-xp-gold uppercase tracking-wider mb-2">
                    <span>Topic Node 01</span>
                    <span>+200 XP</span>
                  </div>
                  <h4 className="text-sm font-bold text-white mb-1">Arrays & Hashing</h4>
                  <p className="text-[10px] text-muted-foreground leading-relaxed">
                    Master array operations, two pointer techniques, and hash map searches.
                  </p>
                </div>
                <div className="flex justify-between items-center text-[10px]">
                  <span className="text-muted-foreground">2 / 3 Problems Solved</span>
                  <span className="text-success-emerald font-bold">66% Complete</span>
                </div>
              </div>

              {/* Mission Card Mock */}
              <div className="border border-card-border p-5 rounded-xl bg-white/[0.01] flex flex-col justify-between h-40">
                <div className="flex items-center gap-2 border-b border-card-border/50 pb-2">
                  <Zap className="w-4 h-4 text-primary" />
                  <span className="text-xs font-bold text-white uppercase tracking-wider">Today&apos;s Quest</span>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="text-white/80 line-through">Solve 1 Easy Problem</span>
                    <span className="text-success-emerald">+50 XP</span>
                  </div>
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="text-white/80">Complete Sorting Quiz</span>
                    <span className="text-xp-gold">+40 XP</span>
                  </div>
                </div>
                <span className="text-[9px] text-muted-foreground uppercase text-center block pt-2 border-t border-card-border/30">
                  Resets in 14 hours
                </span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Feature Grid Section */}
        <section className="w-full max-w-5xl py-20 border-t border-card-border/40">
          <div className="text-center space-y-4 mb-14">
            <h2 className="text-2xl md:text-4xl font-extrabold uppercase text-white tracking-wide">
              Forged For Arena Consistency
            </h2>
            <p className="text-xs md:text-sm text-muted-foreground max-w-lg mx-auto">
              We ditched boring checklists. We designed features that trigger reward loops, forcing you to learn daily.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feat) => {
              const Icon = feat.icon;
              return (
                <div
                  key={feat.title}
                  className="p-6 rounded-2xl border border-card-border bg-white/[0.01] hover:bg-white/[0.02] flex items-start gap-4 text-left transition-all"
                >
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 border ${feat.color}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="space-y-2">
                    <h3 className="font-bold text-md text-white">{feat.title}</h3>
                    <p className="text-xs text-muted-foreground leading-relaxed">{feat.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="container mx-auto px-6 py-8 border-t border-card-border/30 text-center relative z-10 text-xs text-muted-foreground">
        &copy; {new Date().getFullYear()} DSArena Inc. Designed for premium software engineering mastery.
      </footer>
    </div>
  );
}
