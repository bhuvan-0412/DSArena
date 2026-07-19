"use client";

import { useEffect, useState } from "react";
import { useAuthUser } from "@/hooks/use-auth-user";
import { Award, Compass, Play, CheckCircle2, ChevronRight, Lock, BookOpen, Loader2 } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

interface Problem {
  id: string;
  title: string;
  difficulty: string;
  xp_reward: number;
}

interface Topic {
  id: string;
  title: string;
  description: string;
  order: number;
  xp_reward: number;
  problems: Problem[];
}

const BACKEND_URL = "http://127.0.0.1:8000/api/v1";

export default function RoadmapPage() {
  const { stats, isLoaded } = useAuthUser();
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchRoadmap() {
      try {
        setLoading(true);
        const res = await fetch(`${BACKEND_URL}/roadmap/topics`);
        if (res.ok) {
          const data = await res.json();
          setTopics(data);
        } else {
          setTopics(getFallbackTopics());
        }
      } catch (err) {
        console.error("Error fetching roadmap:", err);
        setTopics(getFallbackTopics());
      } finally {
        setLoading(false);
      }
    }

    fetchRoadmap();
  }, []);

  const getFallbackTopics = (): Topic[] => [
    {
      id: "arrays",
      title: "Arrays & Hashing",
      description: "Master array operations, two pointer techniques, and hash map searches.",
      order: 1,
      xp_reward: 200,
      problems: [
        { id: "two-sum", title: "Two Sum", difficulty: "Easy", xp_reward: 50 },
        { id: "valid-anagram", title: "Valid Anagram", difficulty: "Easy", xp_reward: 50 },
        { id: "max-subarray", title: "Maximum Subarray (Kadane's)", difficulty: "Medium", xp_reward: 100 },
      ],
    },
    {
      id: "sorting",
      title: "Sorting Algorithms",
      description: "Understand sorting logic: bubble, selection, insertion, merge, and quicksort.",
      order: 2,
      xp_reward: 200,
      problems: [
        { id: "bubble-sort", title: "Bubble Sort Implementation", difficulty: "Easy", xp_reward: 50 },
        { id: "quick-sort", title: "Quick Sort Implementation", difficulty: "Medium", xp_reward: 100 },
      ],
    },
    {
      id: "binary-search",
      title: "Binary Search",
      description: "Solve logarithmic search challenges on arrays and virtual search spaces.",
      order: 3,
      xp_reward: 200,
      problems: [
        { id: "binary-search-problem", title: "Binary Search", difficulty: "Easy", xp_reward: 50 },
      ],
    },
    {
      id: "recursion",
      title: "Recursion & Backtracking",
      description: "Learn divide-and-conquer, backtracking, and recursive trees.",
      order: 4,
      xp_reward: 200,
      problems: [],
    },
    {
      id: "linked-list",
      title: "Linked Lists",
      description: "Implement singly and doubly linked list pointer manipulations.",
      order: 5,
      xp_reward: 200,
      problems: [],
    },
    {
      id: "trees",
      title: "Binary Trees & BST",
      description: "Traverse and manipulate hierarchical trees, binary search trees.",
      order: 6,
      xp_reward: 200,
      problems: [],
    },
  ];

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh] gap-4">
        <Loader2 className="w-10 h-10 text-primary animate-spin" />
        <p className="text-sm text-muted-foreground font-mono">RETRIEVING ROADMAP NODES...</p>
      </div>
    );
  }

  // Get problem count solved by user (mocked based on topic index for visual purposes)
  const getSolvedCount = (topicId: string) => {
    if (topicId === "arrays") return 2; // Two sum & bubble sort completed in mock logs
    if (topicId === "sorting") return 1;
    return 0;
  };

  const getDifficultyColor = (diff: string) => {
    switch (diff.toLowerCase()) {
      case "easy": return "text-success-emerald bg-success-emerald/10 border-success-emerald/20";
      case "medium": return "text-yellow-500 bg-yellow-500/10 border-yellow-500/20";
      case "hard": return "text-primary bg-primary/10 border-primary/20";
      default: return "text-muted-foreground bg-muted";
    }
  };

  return (
    <div className="space-y-10 pb-16">
      {/* Page Header */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Compass className="w-5 h-5 text-primary" />
          <span className="text-xs font-bold uppercase tracking-widest text-primary font-mono">Progress Roadmap</span>
        </div>
        <h1 className="text-4xl font-extrabold text-white tracking-tight mb-2 uppercase">
          Striver A2Z roadmap
        </h1>
        <p className="text-sm text-muted-foreground max-w-2xl">
          Conquer each node sequentially. Solve problems to earn XP, trigger boss fights, and unlock advanced data structure arenas.
        </p>
      </div>

      {/* Nodes Map */}
      <div className="relative flex flex-col items-center gap-12 py-8">
        {/* Winding Vertical Connector Line */}
        <div className="absolute top-10 bottom-10 w-1 bg-gradient-to-b from-primary via-info-cyan to-muted z-0 pointer-events-none" />

        {topics.map((topic, idx) => {
          const solved = getSolvedCount(topic.id);
          const total = topic.problems.length;
          const isCompleted = total > 0 && solved === total;
          const isLocked = idx > 2; // Lock recursion, linked lists, trees for MVP visual demo

          return (
            <motion.div
              key={topic.id}
              className={`w-full max-w-3xl relative z-10 grid grid-cols-1 md:grid-cols-4 gap-6 p-6 border rounded-2xl transition-all duration-300 ${
                isLocked 
                  ? "bg-[#06060a]/40 border-card-border/50 opacity-60" 
                  : "glass-card border-card-border hover:border-white/10"
              }`}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1, duration: 0.5 }}
            >
              {/* Left Column: Icon/Order & Connection Info */}
              <div className="flex md:flex-col justify-between items-start">
                <div className="flex items-center gap-3 md:flex-col md:items-start">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-black border text-lg ${
                    isCompleted 
                      ? "bg-success-emerald/10 text-success-emerald border-success-emerald/20 shadow-lg shadow-success-emerald/5" 
                      : isLocked 
                        ? "bg-zinc-950 text-zinc-600 border-zinc-900" 
                        : "bg-primary/10 text-primary border-primary/20 shadow-lg shadow-primary/5"
                  }`}>
                    {isLocked ? <Lock className="w-5 h-5" /> : `0${topic.order}`}
                  </div>
                  <div className="md:mt-3">
                    <span className="text-xs font-mono font-bold text-xp-gold uppercase block">
                      +{topic.xp_reward} XP Node
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {total > 0 ? `${solved} / ${total} Solved` : "0 problems"}
                    </span>
                  </div>
                </div>
              </div>

              {/* Middle Column: Node Info & Problem Previews (2 cols) */}
              <div className="md:col-span-2 space-y-4">
                <div>
                  <h3 className="text-xl font-bold text-white mb-1 flex items-center gap-2">
                    {topic.title}
                    {isCompleted && <CheckCircle2 className="w-5 h-5 text-success-emerald inline" />}
                  </h3>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    {topic.description}
                  </p>
                </div>

                {/* Problems Previews inside Node */}
                {!isLocked && topic.problems.length > 0 && (
                  <div className="space-y-2 border-t border-card-border/50 pt-3">
                    <span className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground block">Problem Workspace:</span>
                    <div className="grid grid-cols-1 gap-2">
                      {topic.problems.map((p) => {
                        const problemSolved = topic.id === "arrays" ? (p.id !== "max-subarray") : (p.id === "bubble-sort");
                        return (
                          <div 
                            key={p.id} 
                            className="flex justify-between items-center px-3 py-2 rounded-lg border border-card-border bg-[#030303]/60 hover:bg-[#07070b]/60 transition-colors"
                          >
                            <span className={`text-xs font-medium ${problemSolved ? "text-success-emerald/80 line-through" : "text-white/90"}`}>
                              {p.title}
                            </span>
                            <div className="flex items-center gap-2">
                              <span className={`text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded border ${getDifficultyColor(p.difficulty)}`}>
                                {p.difficulty}
                              </span>
                              {problemSolved ? (
                                <CheckCircle2 className="w-3.5 h-3.5 text-success-emerald" />
                              ) : (
                                <span className="text-[9px] font-mono font-bold text-xp-gold">+{p.xp_reward} XP</span>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>

              {/* Right Column: Call to Action */}
              <div className="flex items-center justify-end">
                {isLocked ? (
                  <button className="w-full md:w-auto px-4 py-2.5 rounded-xl bg-zinc-950 border border-zinc-900 text-zinc-600 font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 cursor-not-allowed">
                    <Lock className="w-4 h-4" /> Locked
                  </button>
                ) : (
                  <Link href={`/roadmap/${topic.id}`} className="w-full md:w-auto">
                    <button className="w-full md:w-auto px-5 py-3 rounded-xl bg-primary hover:bg-primary/90 text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all duration-300 shadow-md shadow-primary/10 hover:shadow-primary/20 group cursor-pointer">
                      <Play className="w-4 h-4 fill-white transition-transform group-hover:scale-110" />
                      <span>Enter Arena</span>
                      <ChevronRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
                    </button>
                  </Link>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
