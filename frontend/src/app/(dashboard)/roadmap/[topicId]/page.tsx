"use client";

import { useEffect, useState, use } from "react";
import { useAuthUser } from "@/hooks/use-auth-user";
import { ArrowLeft, BookOpen, Video, FileText, CheckCircle2, ChevronRight, Play, Sparkles, Loader2, Lock, Zap, Award } from "lucide-react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";

interface Problem {
  id: string;
  title: string;
  difficulty: string;
  xp_reward: number;
  status?: string;
}

interface Topic {
  id: string;
  title: string;
  description: string;
  xp_reward: number;
  problems: Problem[];
  problems_solved?: number;
  quiz_completed?: boolean;
  video_watched?: boolean;
  notes_read?: boolean;
  boss_battle_completed?: boolean;
  boss_battle_locked?: boolean;
  mastery_percentage?: number;
  estimated_completion?: string;
}

const BACKEND_URL = "http://127.0.0.1:8000/api/v1";

const getStatusBadge = (status?: string) => {
  const normalized = (status || "NOT_STARTED").toUpperCase();
  switch (normalized) {
    case "NOT_STARTED":
      return (
        <span className="flex items-center gap-1.5 text-[9px] font-bold text-zinc-500 uppercase font-mono bg-zinc-950 px-2 py-0.5 rounded border border-zinc-900">
          <span className="w-1.5 h-1.5 rounded-full border border-zinc-500" /> Not Started
        </span>
      );
    case "ATTEMPTED":
      return (
        <span className="flex items-center gap-1.5 text-[9px] font-bold text-yellow-500 uppercase font-mono bg-yellow-500/5 px-2 py-0.5 rounded border border-yellow-500/20">
          <span className="w-1.5 h-1.5 rounded-full bg-yellow-500 shadow-[0_0_4px_#eab308]" /> Attempted
        </span>
      );
    case "SOLVED":
      return (
        <span className="flex items-center gap-1.5 text-[9px] font-bold text-success-emerald uppercase font-mono bg-success-emerald/5 px-2 py-0.5 rounded border border-success-emerald/20">
          <span className="w-1.5 h-1.5 rounded-full bg-success-emerald shadow-[0_0_4px_#10b981]" /> Solved
        </span>
      );
    case "MASTERED":
      return (
        <span className="flex items-center gap-1.5 text-[9px] font-bold text-purple-400 uppercase font-mono bg-purple-500/5 px-2 py-0.5 rounded border border-purple-500/20">
          <span className="w-1.5 h-1.5 rounded-full bg-purple-400 shadow-[0_0_4px_#c084fc]" /> Mastered
        </span>
      );
    case "REVISION_DUE":
      return (
        <span className="flex items-center gap-1.5 text-[9px] font-bold text-red-500 uppercase font-mono bg-red-500/5 px-2 py-0.5 rounded border border-red-500/20 animate-pulse">
          <span className="w-1.5 h-1.5 rounded-full bg-red-500 shadow-[0_0_4px_#ef4444]" /> Revision Due
        </span>
      );
    default:
      return (
        <span className="flex items-center gap-1.5 text-[9px] font-bold text-zinc-500 uppercase font-mono bg-zinc-950 px-2 py-0.5 rounded border border-zinc-900">
          <span className="w-1.5 h-1.5 rounded-full border border-zinc-500" /> Not Started
        </span>
      );
  }
};

export default function TopicPage({ params }: { params: Promise<{ topicId: string }> }) {
  const { topicId } = use(params);
  const { stats, isLoaded, refreshStats } = useAuthUser();
  const [topic, setTopic] = useState<Topic | null>(null);
  const [loading, setLoading] = useState(true);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  useEffect(() => {
    if (!isLoaded) return;

    async function fetchTopic() {
      try {
        setLoading(true);
        const clerkId = stats?.clerk_id || "mock_user_striver";
        const res = await fetch(`${BACKEND_URL}/roadmap/topics/${topicId}?clerk_id=${clerkId}`);
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
  }, [topicId, isLoaded, stats?.clerk_id]);

  const completeActivity = async (activityType: "video" | "notes" | "quiz") => {
    if (!stats) return;
    try {
      const res = await fetch(`${BACKEND_URL}/roadmap/topics/${topicId}/activity?clerk_id=${stats.clerk_id}&activity_type=${activityType}`, {
        method: "POST"
      });
      if (res.ok) {
        const data = await res.json();
        
        // Refresh topic details
        const topicRes = await fetch(`${BACKEND_URL}/roadmap/topics/${topicId}?clerk_id=${stats.clerk_id}`);
        if (topicRes.ok) {
          const updatedTopic = await topicRes.json();
          setTopic(updatedTopic);
        }
        
        // Refresh stats
        await refreshStats();
        
        if (data.xp_gained > 0) {
          showToast(`Completed! Gained +${data.xp_gained} XP!`);
        } else {
          showToast("Activity read successfully!");
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  const completeBossBattle = async () => {
    if (!stats) return;
    try {
      const res = await fetch(`${BACKEND_URL}/roadmap/topics/${topicId}/boss-battle/complete?clerk_id=${stats.clerk_id}`, {
        method: "POST"
      });
      if (res.ok) {
        const data = await res.json();
        
        const topicRes = await fetch(`${BACKEND_URL}/roadmap/topics/${topicId}?clerk_id=${stats.clerk_id}`);
        if (topicRes.ok) {
          const updatedTopic = await topicRes.json();
          setTopic(updatedTopic);
        }
        
        await refreshStats();
        showToast("BOSS SLAYED! Gained +500 XP!");
      }
    } catch (err) {
      console.error(err);
    }
  };

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

  if (!isLoaded || loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh] gap-4">
        <Loader2 className="w-10 h-10 text-primary animate-spin" />
        <p className="text-sm text-muted-foreground font-mono">LOADING OBJECTIVES...</p>
      </div>
    );
  }

  if (!topic) return <div className="text-white">Topic not found</div>;

  const getDifficultyColor = (diff: string) => {
    switch (diff.toLowerCase()) {
      case "easy": return "text-success-emerald bg-success-emerald/10 border-success-emerald/20";
      case "medium": return "text-yellow-500 bg-yellow-500/10 border-yellow-500/20";
      case "hard": return "text-primary bg-primary/10 border-primary/20";
      default: return "text-muted-foreground bg-muted";
    }
  };

  return (
    <div className="space-y-8 pb-16 relative">
      {/* Toast Notification */}
      <AnimatePresence>
        {toastMessage && (
          <motion.div 
            className="fixed bottom-6 right-6 border border-primary/20 px-6 py-4 rounded-2xl bg-[#0a0a0f] text-white text-xs font-bold uppercase tracking-wider flex items-center gap-2.5 z-50 shadow-2xl shadow-primary/10"
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
          >
            <Sparkles className="w-4 h-4 text-xp-gold" />
            <span>{toastMessage}</span>
          </motion.div>
        )}
      </AnimatePresence>

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
            <div className={`border rounded-2xl p-6 transition-all duration-300 ${
              topic.video_watched ? "border-success-emerald/20 bg-success-emerald/[0.02]" : "border-card-border bg-[#050508]/40"
            }`}>
              <div className="flex justify-between items-start mb-4">
                <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <Video className="w-4 h-4 text-red-500" /> Video Tutorials
                </h4>
                {topic.video_watched ? (
                  <span className="text-[10px] text-success-emerald bg-success-emerald/10 border border-success-emerald/20 px-2 py-0.5 rounded uppercase font-bold tracking-wider font-mono">
                    Completed ✓
                  </span>
                ) : (
                  <span className="text-[10px] text-xp-gold bg-xp-gold/10 border border-xp-gold/20 px-2 py-0.5 rounded uppercase font-bold tracking-wider font-mono">
                    +10 XP
                  </span>
                )}
              </div>
              <div className="space-y-3 text-xs">
                <a 
                  href={`https://www.youtube.com/results?search_query=striver+${topic.title}`} 
                  target="_blank" 
                  rel="noreferrer" 
                  onClick={() => completeActivity("video")}
                  className="flex items-center justify-between p-3 rounded-lg border border-card-border bg-[#030303]/60 hover:border-red-500/30 transition-all duration-300"
                >
                  <span className="text-white font-medium">Striver&apos;s {topic.title} Guide</span>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </a>
              </div>
            </div>

            {/* Written Notes */}
            <div className={`border rounded-2xl p-6 transition-all duration-300 ${
              topic.notes_read ? "border-success-emerald/20 bg-success-emerald/[0.02]" : "border-card-border bg-[#050508]/40"
            }`}>
              <div className="flex justify-between items-start mb-4">
                <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <FileText className="w-4 h-4 text-info-cyan" /> Articles & Notes
                </h4>
                {topic.notes_read ? (
                  <span className="text-[10px] text-success-emerald bg-success-emerald/10 border border-success-emerald/20 px-2 py-0.5 rounded uppercase font-bold tracking-wider font-mono">
                    Completed ✓
                  </span>
                ) : (
                  <span className="text-[10px] text-xp-gold bg-xp-gold/10 border border-xp-gold/20 px-2 py-0.5 rounded uppercase font-bold tracking-wider font-mono">
                    +20 XP
                  </span>
                )}
              </div>
              <div className="space-y-3 text-xs">
                <a 
                  href={`https://takeuforward.org/?s=${topic.title}`} 
                  target="_blank" 
                  rel="noreferrer" 
                  onClick={() => completeActivity("notes")}
                  className="flex items-center justify-between p-3 rounded-lg border border-card-border bg-[#030303]/60 hover:border-info-cyan/30 transition-all duration-300"
                >
                  <span className="text-white font-medium">TakeUForward Article Library</span>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </a>
              </div>
            </div>
          </div>

          {/* Interactive Concept Quiz card */}
          <div className={`border rounded-2xl p-6 transition-all duration-300 ${
            topic.quiz_completed ? "border-success-emerald/20 bg-success-emerald/[0.02]" : "border-card-border bg-[#050508]/40"
          } relative overflow-hidden`}>
            <div className="absolute top-0 right-0 w-24 h-24 bg-primary/5 rounded-full blur-2xl pointer-events-none" />
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-md font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Award className="w-4 h-4 text-primary" /> Concept Battle Quiz
              </h3>
              {topic.quiz_completed ? (
                <span className="text-[10px] text-success-emerald bg-success-emerald/10 border border-success-emerald/20 px-2.5 py-1 rounded-full uppercase font-bold tracking-wider font-mono">
                  Quiz Solved ✓
                </span>
              ) : (
                <span className="text-[10px] text-xp-gold bg-xp-gold/10 border border-xp-gold/20 px-2.5 py-1 rounded-full uppercase font-bold tracking-wider font-mono">
                  +50 XP reward
                </span>
              )}
            </div>
            <p className="text-xs text-muted-foreground mb-4">
              Test your theoretical memory and runtime space-complexity knowledge of {topic.title} in a rapid simulation.
            </p>
            {topic.quiz_completed ? (
              <div className="h-12 border border-success-emerald/10 bg-success-emerald/[0.02] text-success-emerald font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 rounded-xl">
                <CheckCircle2 className="w-4 h-4" /> Quiz Arena Conquered
              </div>
            ) : (
              <button 
                onClick={() => completeActivity("quiz")}
                className="w-full py-3 rounded-xl bg-primary hover:bg-primary/95 text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-1.5 transition-colors cursor-pointer shadow-lg shadow-primary/10 hover:shadow-primary/20"
              >
                <Zap className="w-3.5 h-3.5 fill-white" /> Take Concept Quiz (+50 XP)
              </button>
            )}
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
                  const normalizedStatus = (p.status || "NOT_STARTED").toUpperCase();
                  const problemSolved = normalizedStatus === "SOLVED" || normalizedStatus === "MASTERED" || normalizedStatus === "REVISION_DUE" || p.status === "Solved" || p.status === "Mastered" || p.status === "Revision Due";
                  return (
                    <div 
                      key={p.id}
                      className="p-4 rounded-xl border border-card-border bg-[#030303]/40 flex flex-col justify-between gap-4"
                    >
                      <div className="flex justify-between items-start">
                        <div className="space-y-1.5">
                          <h4 className={`text-sm font-bold ${problemSolved ? "text-success-emerald line-through" : "text-white"}`}>
                            {p.title}
                          </h4>
                          <div className="flex flex-wrap items-center gap-1.5">
                            <span className={`text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded border inline-block ${getDifficultyColor(p.difficulty)}`}>
                              {p.difficulty}
                            </span>
                            {getStatusBadge(p.status)}
                          </div>
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

          {/* Boss Battle Locked/Unlocked Node */}
          {topic.boss_battle_completed ? (
            <div className="border border-success-emerald/20 rounded-2xl p-6 bg-success-emerald/[0.02] border-success-emerald/10 flex flex-col items-center justify-center text-center">
              <CheckCircle2 className="w-8 h-8 text-success-emerald mb-3" />
              <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-1">
                Boss Slayed: {topic.title}
              </h4>
              <p className="text-xs text-muted-foreground max-w-xs leading-relaxed">
                You successfully conquered the ultimate Boss Challenge and claimed the +500 XP loot!
              </p>
            </div>
          ) : topic.boss_battle_locked ? (
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
          ) : (
            <div className="border border-red-500/30 rounded-2xl p-6 bg-red-950/10 shadow-lg shadow-red-500/5 flex flex-col items-center justify-center text-center relative overflow-hidden">
              <div className="absolute top-0 inset-x-0 h-0.5 bg-gradient-to-r from-red-500 to-primary animate-pulse" />
              <Play className="w-8 h-8 text-red-500 mb-3 fill-red-500 animate-bounce" />
              <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-1">
                Fight Boss: {topic.title}
              </h4>
              <p className="text-xs text-muted-foreground max-w-xs leading-relaxed mb-4">
                The Boss Arena is unlocked! Challenge the ultimate algorithms battle to claim your massive reward.
              </p>
              <button 
                onClick={completeBossBattle}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-red-600 to-primary hover:opacity-90 text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-1.5 transition-all cursor-pointer shadow-md shadow-red-600/20 hover:scale-103"
              >
                <Zap className="w-3.5 h-3.5 fill-white" /> Slay Boss (+500 XP)
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
