"use client";

import { useEffect, useState, use } from "react";
import { useAuthUser } from "@/hooks/use-auth-user";
import { ArrowLeft, BookOpen, Video, FileText, CheckCircle2, ChevronRight, Play, Info, Sparkles, Loader2, Lock } from "lucide-react";
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
  xp_reward: number;
  problems: Problem[];
}

const BACKEND_URL = "http://127.0.0.1:8000/api/v1";

export default function TopicPage({ params }: { params: Promise<{ topicId: string }> }) {
  const { topicId } = use(params);
  const { stats, isLoaded } = useAuthUser();
  const [topic, setTopic] = useState<Topic | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchTopic() {
      try {
        setLoading(true);
        const res = await fetch(`${BACKEND_URL}/roadmap/topics/${topicId}`);
        if (res.ok) {
          const data = await res.json();
          setTopic(data);
        } else {
          setTopic(getFallbackTopic(topicId));
        }
      } catch (err) {
        console.error("Error fetching topic:", err);
        setTopic(getFallbackTopic(topicId));
      } finally {
        setLoading(false);
      }
    }

    fetchTopic();
  }, [topicId]);

  const getFallbackTopic = (id: string): Topic => {
    const defaultTopics: Record<string, Topic> = {
      arrays: {
        id: "arrays",
        title: "Arrays & Hashing",
        description: "Master array operations, two pointer techniques, and hash map searches.",
        xp_reward: 200,
        problems: [
          { id: "two-sum", title: "Two Sum", difficulty: "Easy", xp_reward: 50 },
          { id: "valid-anagram", title: "Valid Anagram", difficulty: "Easy", xp_reward: 50 },
          { id: "max-subarray", title: "Maximum Subarray (Kadane's)", difficulty: "Medium", xp_reward: 100 },
        ],
      },
      sorting: {
        id: "sorting",
        title: "Sorting Algorithms",
        description: "Understand sorting logic: bubble, selection, insertion, merge, and quicksort.",
        xp_reward: 200,
        problems: [
          { id: "bubble-sort", title: "Bubble Sort Implementation", difficulty: "Easy", xp_reward: 50 },
          { id: "quick-sort", title: "Quick Sort Implementation", difficulty: "Medium", xp_reward: 100 },
        ],
      },
      "binary-search": {
        id: "binary-search",
        title: "Binary Search",
        description: "Solve logarithmic search challenges on arrays and virtual search spaces.",
        xp_reward: 200,
        problems: [
          { id: "binary-search-problem", title: "Binary Search", difficulty: "Easy", xp_reward: 50 },
        ],
      },
    };
    return defaultTopics[id] || {
      id,
      title: "Algorithms Node",
      description: "Advanced data structure and algorithmic complexity conquest.",
      xp_reward: 200,
      problems: [],
    };
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh] gap-4">
        <Loader2 className="w-10 h-10 text-primary animate-spin" />
        <p className="text-sm text-muted-foreground font-mono">LOADING OBJECTIVES...</p>
      </div>
    );
  }

  if (!topic) return <div className="text-white">Topic not found</div>;

  const solvedMap: Record<string, boolean> = {
    "two-sum": true,
    "valid-anagram": true,
    "bubble-sort": true,
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
    <div className="space-y-8 pb-16">
      {/* Back Button */}
      <Link href="/roadmap" className="inline-flex items-center gap-2 text-xs font-mono font-bold text-muted-foreground hover:text-white uppercase tracking-wider transition-colors duration-300">
        <ArrowLeft className="w-4 h-4" /> Back to Roadmap
      </Link>

      {/* Header */}
      <div>
        <h1 className="text-4xl font-extrabold text-white uppercase tracking-tight mb-2">
          {topic.title}
        </h1>
        <p className="text-sm text-muted-foreground max-w-3xl leading-relaxed">
          {topic.description}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Columns: Objectives & Learning Materials */}
        <div className="lg:col-span-2 space-y-6">
          {/* Objectives Card */}
          <div className="border border-card-border rounded-2xl p-6 glass-card">
            <h3 className="text-md font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-primary" /> Learning Objectives
            </h3>
            <ul className="space-y-3 text-sm text-muted-foreground list-disc pl-5">
              <li>Understand the basic properties and memory representations of {topic.title}.</li>
              <li>Learn optimal time and space complexity strategies for standard algorithms.</li>
              <li>Master two-pointer techniques, sliding windows, or partition pivots.</li>
              <li>Prepare for interviews with high-frequency questions.</li>
            </ul>
          </div>

          {/* Videos & Articles */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Video Resources */}
            <div className="border border-card-border rounded-2xl p-6 bg-[#050508]/40">
              <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
                <Video className="w-4 h-4 text-red-500" /> Video Tutorials
              </h4>
              <div className="space-y-3 text-xs">
                <a 
                  href={`https://www.youtube.com/results?search_query=striver+${topic.title}`} 
                  target="_blank" 
                  rel="noreferrer" 
                  className="flex items-center justify-between p-3 rounded-lg border border-card-border bg-[#030303]/60 hover:border-red-500/30 transition-all duration-300"
                >
                  <span className="text-white font-medium">Striver&apos;s {topic.title} Guide</span>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </a>
                <a 
                  href={`https://www.youtube.com/results?search_query=algorithms+${topic.title}`} 
                  target="_blank" 
                  rel="noreferrer" 
                  className="flex items-center justify-between p-3 rounded-lg border border-card-border bg-[#030303]/60 hover:border-red-500/30 transition-all duration-300"
                >
                  <span className="text-white font-medium">General Visual Walkthrough</span>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </a>
              </div>
            </div>

            {/* Written Notes */}
            <div className="border border-card-border rounded-2xl p-6 bg-[#050508]/40">
              <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
                <FileText className="w-4 h-4 text-info-cyan" /> Articles & Notes
              </h4>
              <div className="space-y-3 text-xs">
                <a 
                  href={`https://takeuforward.org/?s=${topic.title}`} 
                  target="_blank" 
                  rel="noreferrer" 
                  className="flex items-center justify-between p-3 rounded-lg border border-card-border bg-[#030303]/60 hover:border-info-cyan/30 transition-all duration-300"
                >
                  <span className="text-white font-medium">TakeUForward Article Library</span>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </a>
                <a 
                  href={`https://www.geeksforgeeks.org/${topic.id}/`} 
                  target="_blank" 
                  rel="noreferrer" 
                  className="flex items-center justify-between p-3 rounded-lg border border-card-border bg-[#030303]/60 hover:border-info-cyan/30 transition-all duration-300"
                >
                  <span className="text-white font-medium">GeeksforGeeks Overview</span>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </a>
              </div>
            </div>
          </div>

          {/* Visual Learning Placeholder */}
          <div className="border border-card-border rounded-2xl p-6 bg-[#050508]/40 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-info-cyan/5 rounded-full blur-2xl pointer-events-none" />
            <h3 className="text-md font-bold text-white uppercase tracking-wider mb-2 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-info-cyan" /> Visual Learning Simulator
            </h3>
            <p className="text-xs text-muted-foreground mb-4">
              Interactive graphical animations and visualization simulations are unlocked during solving sessions.
            </p>
            <div className="h-40 rounded-xl bg-zinc-950 border border-card-border/80 flex items-center justify-center text-xs text-muted-foreground font-mono">
              [VISUAL ALGORITHM GRAPHICS PLACEHOLDER]
            </div>
          </div>
        </div>

        {/* Right Column: Problem Workspace List & Boss Battles */}
        <div className="space-y-6">
          <div className="border border-card-border rounded-2xl p-6 glass-card">
            <h3 className="text-md font-bold text-white uppercase tracking-wider mb-4">
              Problems to Solve
            </h3>
            
            {topic.problems.length === 0 ? (
              <div className="text-center text-xs text-muted-foreground py-6">
                No problems currently available for this node.
              </div>
            ) : (
              <div className="space-y-3">
                {topic.problems.map((p) => {
                  const problemSolved = !!solvedMap[p.id];
                  return (
                    <div 
                      key={p.id}
                      className="p-4 rounded-xl border border-card-border bg-[#030303]/40 flex flex-col justify-between gap-4"
                    >
                      <div className="flex justify-between items-start">
                        <div className="space-y-1">
                          <h4 className={`text-sm font-bold ${problemSolved ? "text-success-emerald line-through" : "text-white"}`}>
                            {p.title}
                          </h4>
                          <span className={`text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded border inline-block ${getDifficultyColor(p.difficulty)}`}>
                            {p.difficulty}
                          </span>
                        </div>
                        {problemSolved && <CheckCircle2 className="w-5 h-5 text-success-emerald shrink-0" />}
                      </div>

                      <div className="flex justify-between items-center text-xs">
                        <span className="text-xp-gold font-mono font-extrabold">+{p.xp_reward} XP</span>
                        <Link href={`/roadmap/${topic.id}/${p.id}`}>
                          <button className="px-3 py-1.5 rounded-lg bg-primary hover:bg-primary/95 text-white font-bold text-xs uppercase tracking-wider flex items-center gap-1.5 transition-colors cursor-pointer">
                            <Play className="w-3 h-3 fill-white" /> Fight
                          </button>
                        </Link>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Boss Battle Locked Node */}
          <div className="border border-red-950/20 rounded-2xl p-6 bg-red-950/5 border-red-500/10 flex flex-col items-center justify-center text-center">
            <Lock className="w-8 h-8 text-primary mb-3" />
            <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-1">
              Boss Battle: {topic.title}
            </h4>
            <p className="text-xs text-muted-foreground max-w-xs leading-relaxed mb-4">
              Solve all standard problems in this node to unlock the Boss Battle arena (+500 XP).
            </p>
            <button className="px-4 py-2 rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-600 font-bold text-xs uppercase tracking-wider cursor-not-allowed">
              Locked Node
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
