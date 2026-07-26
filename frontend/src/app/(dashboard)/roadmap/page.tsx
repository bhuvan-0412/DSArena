"use client";

import { useEffect, useState } from "react";
import { useAuthUser } from "@/hooks/use-auth-user";
import { 
  Compass, 
  Play, 
  CheckCircle2, 
  ChevronRight, 
  ChevronDown, 
  Lock, 
  Loader2, 
  Clock, 
  Zap, 
  TrendingUp,
  Video
} from "lucide-react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { RoadmapProgressBar } from "@/components/roadmap/RoadmapProgressBar";

interface RoadmapNode {
  id: string;
  parent_id?: string;
  title: string;
  slug: string;
  description?: string;
  type: string;  // 'step', 'section', 'subsection', 'topic', 'problem'
  order_index: number;
  estimated_time?: number;
  xp_reward: number;
  difficulty?: string;
  status?: string;
  
  is_completed: boolean;
  is_locked: boolean;
  progress_percentage: number;
  problems_solved: number;
  total_problems: number;
  quiz_completed: boolean;
  quiz_best_score?: number;
  revision_due_count: number;
  
  children: RoadmapNode[];
}

interface OverallProgress {
  topic_name: string;
  completed_videos: number;
  total_videos: number;
  progress_percentage: number;
  overall_xp: number;
}

const BACKEND_URL = "http://127.0.0.1:8000/api/v1";

export default function RoadmapPage() {
  const { stats, isLoaded } = useAuthUser();
  const [nodes, setNodes] = useState<RoadmapNode[]>([]);
  const [overallProgress, setOverallProgress] = useState<OverallProgress>({
    topic_name: "Striver A2Z DSA Roadmap",
    completed_videos: 0,
    total_videos: 0,
    progress_percentage: 0,
    overall_xp: 0,
  });
  const [loading, setLoading] = useState(true);
  const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>({});

  useEffect(() => {
    if (!isLoaded) return;
    
    async function fetchRoadmapData() {
      try {
        setLoading(true);
        const clerkId = stats?.clerk_id || "mock_user_striver";
        
        const [nodesRes, progRes] = await Promise.all([
          fetch(`${BACKEND_URL}/roadmap/nodes?clerk_id=${clerkId}`),
          fetch(`${BACKEND_URL}/roadmap/progress?clerk_id=${clerkId}`),
        ]);

        if (nodesRes.ok) {
          const data = await nodesRes.json();
          setNodes(data);
          
          // Auto-expand active path
          const autoExpanded = getAutoExpandedNodes(data);
          setExpandedNodes(autoExpanded);
        }

        if (progRes.ok) {
          const pData = await progRes.json();
          setOverallProgress(pData);
        }
      } catch (err) {
        console.error("Error fetching roadmap data:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchRoadmapData();
  }, [isLoaded, stats?.clerk_id]);

  const getAutoExpandedNodes = (nodeList: RoadmapNode[]): Record<string, boolean> => {
    const expanded: Record<string, boolean> = {};
    
    const traverse = (list: RoadmapNode[]): boolean => {
      for (const node of list) {
        if (node.type === "step") {
          expanded[node.id] = true;
        }

        if (!node.is_completed) {
          expanded[node.id] = true;
          if (node.parent_id) {
            expanded[node.parent_id] = true;
          }
          return true;
        }

        if (node.children && node.children.length > 0) {
          const found = traverse(node.children);
          if (found) {
            expanded[node.id] = true;
            return true;
          }
        }
      }
      return false;
    };
    
    traverse(nodeList);
    return expanded;
  };

  const toggleExpand = (id: string) => {
    setExpandedNodes(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  if (!isLoaded || loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh] gap-4">
        <Loader2 className="w-10 h-10 text-primary animate-spin" />
        <p className="text-sm text-muted-foreground font-mono">RETRIEVING video learning paths...</p>
      </div>
    );
  }

  const getDifficultyColor = (diff?: string) => {
    if (!diff) return "text-zinc-400 bg-zinc-900 border-zinc-800";
    switch (diff.toLowerCase()) {
      case "easy": return "text-success-emerald bg-success-emerald/10 border-success-emerald/20";
      case "medium": return "text-yellow-500 bg-yellow-500/10 border-yellow-500/20";
      case "hard": return "text-primary bg-primary/10 border-primary/20";
      default: return "text-zinc-400 bg-zinc-900 border-zinc-800";
    }
  };

  const renderStatusBadge = (node: RoadmapNode) => {
    const status = node.status || (node.is_completed ? "COMPLETED" : node.is_locked ? "LOCKED" : "AVAILABLE");
    
    switch (status) {
      case "COMPLETED":
        return (
          <span className="flex items-center gap-1 text-[10px] font-mono text-success-emerald font-bold uppercase px-2 py-0.5 rounded-full bg-success-emerald/10 border border-success-emerald/30">
            <CheckCircle2 className="w-3 h-3" />
            <span>Completed</span>
          </span>
        );
      case "IN_PROGRESS":
        return (
          <span className="flex items-center gap-1 text-[10px] font-mono text-yellow-400 font-bold uppercase px-2 py-0.5 rounded-full bg-yellow-500/10 border border-yellow-500/30 animate-pulse">
            <Clock className="w-3 h-3" />
            <span>In Progress</span>
          </span>
        );
      case "AVAILABLE":
        return (
          <span className="flex items-center gap-1 text-[10px] font-mono text-info-cyan font-bold uppercase px-2 py-0.5 rounded-full bg-info-cyan/10 border border-info-cyan/30">
            <Play className="w-3 h-3 fill-info-cyan" />
            <span>Available</span>
          </span>
        );
      case "LOCKED":
      default:
        return (
          <span className="flex items-center gap-1 text-[10px] font-mono text-zinc-500 font-bold uppercase px-2 py-0.5 rounded-full bg-zinc-900 border border-zinc-800">
            <Lock className="w-3 h-3" />
            <span>Locked</span>
          </span>
        );
    }
  };

  return (
    <div className="space-y-10 pb-16">
      {/* Page Header */}
      <div className="space-y-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Compass className="w-5 h-5 text-primary" />
            <span className="text-xs font-bold uppercase tracking-widest text-primary font-mono">Learning Roadmap</span>
          </div>
          <h1 className="text-4xl font-extrabold text-white tracking-tight mb-2 uppercase">
            Striver A2Z DSA Sheet
          </h1>
          <p className="text-sm text-muted-foreground max-w-2xl">
            Sequential Video Learning Journey. Watch video tutorials step-by-step, mark lessons as done, and unlock your path to mastering algorithms.
          </p>
        </div>

        {/* Overall Topic Progress Bar */}
        <RoadmapProgressBar
          topicName={overallProgress.topic_name}
          completedVideos={overallProgress.completed_videos}
          totalVideos={overallProgress.total_videos}
          progressPercentage={overallProgress.progress_percentage}
          overallXp={overallProgress.overall_xp}
        />
      </div>

      {/* Explorer Tree */}
      <div className="space-y-8 max-w-4xl mx-auto relative pl-4 md:pl-6">
        {/* Connector Line for Steps */}
        <div className="absolute left-0 top-6 bottom-6 w-[2px] bg-gradient-to-b from-primary/80 via-info-cyan/40 to-muted/20" />

        {nodes.map((step) => {
          const isStepExpanded = expandedNodes[step.id];
          return (
            <div key={step.id} className="relative space-y-4">
              {/* Step indicator node */}
              <div className={`absolute -left-[21px] md:-left-[29px] w-6 h-6 md:w-8 md:h-8 rounded-full border-2 flex items-center justify-center font-bold text-xs md:text-sm z-20 ${
                step.is_completed 
                  ? "bg-success-emerald border-success-emerald text-zinc-950" 
                  : step.is_locked
                    ? "bg-zinc-950 border-zinc-800 text-zinc-600"
                    : "bg-zinc-950 border-primary text-primary shadow-[0_0_10px_rgba(168,85,247,0.3)]"
              }`}>
                {step.is_completed ? "✓" : step.order_index}
              </div>

              {/* Step Card Header */}
              <div 
                onClick={() => toggleExpand(step.id)}
                className={`w-full p-4 rounded-xl border flex flex-col md:flex-row md:items-center justify-between gap-4 cursor-pointer select-none transition-all duration-300 ${
                  step.is_locked
                    ? "bg-zinc-950/30 border-zinc-900 opacity-60 pointer-events-none"
                    : "glass-card border-card-border hover:border-primary/40 shadow-lg shadow-black/10"
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-xp-gold uppercase font-bold">Step 0{step.order_index}</span>
                    <span className={`text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded border ${getDifficultyColor(step.difficulty)}`}>
                      {step.difficulty}
                    </span>
                  </div>
                  <h2 className="text-xl font-black text-white">{step.title}</h2>
                  <p className="text-xs text-muted-foreground max-w-xl">{step.description}</p>
                </div>

                <div className="flex items-center gap-4 self-end md:self-center">
                  <div className="text-right">
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-mono">
                      <span>PROGRESS:</span>
                      <span className="text-xp-gold font-bold">{step.progress_percentage}%</span>
                    </div>
                    <div className="w-24 h-1.5 bg-zinc-950 border border-card-border rounded-full mt-1 overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-xp-gold to-yellow-500 transition-all duration-300"
                        style={{ width: `${step.progress_percentage}%` }}
                      />
                    </div>
                  </div>

                  {isStepExpanded ? <ChevronDown className="w-5 h-5 text-zinc-400" /> : <ChevronRight className="w-5 h-5 text-zinc-400" />}
                </div>
              </div>

              {/* Step Sections (collapsible) */}
              <AnimatePresence>
                {isStepExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden pl-4 md:pl-8 space-y-4 relative"
                  >
                    {/* Section Connector Line */}
                    <div className="absolute left-1 top-2 bottom-6 w-[1px] bg-zinc-800" />

                    {step.children.map((section) => {
                      const isSectionExpanded = expandedNodes[section.id];
                      return (
                        <div key={section.id} className="relative space-y-3">
                          {/* Section indicator dot */}
                          <div className={`absolute -left-[20px] md:-left-[36px] w-3 h-3 rounded-full border z-20 ${
                            section.is_completed
                              ? "bg-success-emerald border-success-emerald"
                              : section.is_locked
                                ? "bg-zinc-950 border-zinc-800"
                                : "bg-zinc-950 border-info-cyan shadow-[0_0_6px_rgba(6,182,212,0.4)]"
                          }`} />

                          {/* Section Header */}
                          <div 
                            onClick={() => toggleExpand(section.id)}
                            className={`p-3 rounded-lg border flex items-center justify-between gap-4 cursor-pointer select-none transition-all duration-200 ${
                              section.is_locked
                                ? "bg-zinc-950/20 border-zinc-900/60 opacity-50"
                                : "bg-zinc-950/40 border-card-border/80 hover:border-info-cyan/40"
                            }`}
                          >
                            <div className="space-y-0.5">
                              <span className="text-[9px] font-mono text-zinc-500 uppercase font-bold">Section {section.order_index}</span>
                              <h3 className="text-md font-bold text-white/90">{section.title}</h3>
                            </div>

                            <div className="flex items-center gap-3">
                              <span className="text-xs font-mono text-muted-foreground">
                                {section.children?.filter(c => c.is_completed || c.status === "COMPLETED").length || 0} / {section.children?.length || 0} Lessons
                              </span>
                              {isSectionExpanded ? <ChevronDown className="w-4 h-4 text-zinc-500" /> : <ChevronRight className="w-4 h-4 text-zinc-500" />}
                            </div>
                          </div>

                          {/* Section Topics (collapsible) */}
                          <AnimatePresence>
                            {isSectionExpanded && (
                              <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: "auto", opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                transition={{ duration: 0.25 }}
                                className="overflow-hidden pl-4 md:pl-6 space-y-3 relative"
                              >
                                {/* Topic Connector Line */}
                                <div className="absolute left-1 top-2 bottom-6 w-[1px] bg-zinc-800/60 border-dashed border-l border-zinc-800" />

                                {section.children.map((topic) => {
                                  const nodeStatus = topic.status || (topic.is_completed ? "COMPLETED" : topic.is_locked ? "LOCKED" : "AVAILABLE");
                                  const isLocked = nodeStatus === "LOCKED";

                                  return (
                                    <div key={topic.id} className="relative">
                                      {/* Topic Dot */}
                                      <div className={`absolute -left-[20px] md:-left-[28px] w-2.5 h-2.5 rounded-full border z-20 ${
                                        nodeStatus === "COMPLETED"
                                          ? "bg-success-emerald border-success-emerald"
                                          : isLocked
                                            ? "bg-zinc-950 border-zinc-900"
                                            : "bg-zinc-950 border-info-cyan shadow-[0_0_6px_rgba(6,182,212,0.4)]"
                                      }`} />

                                      {/* Topic Card */}
                                      <div 
                                        className={`p-4 rounded-xl border flex flex-col md:flex-row md:items-center justify-between gap-4 transition-all duration-300 ${
                                          isLocked
                                            ? "bg-[#06060a]/20 border-zinc-900/40 opacity-40 select-none"
                                            : "glass-card border-card-border hover:border-zinc-700 shadow-md"
                                        }`}
                                      >
                                        <div className="space-y-2 flex-1">
                                          <div className="flex flex-wrap items-center gap-2">
                                            <h4 className="text-sm font-bold text-white">{topic.title}</h4>
                                            <span className={`text-[8px] font-extrabold uppercase px-1 rounded border ${getDifficultyColor(topic.difficulty)}`}>
                                              {topic.difficulty}
                                            </span>
                                            {renderStatusBadge(topic)}
                                          </div>
                                          {topic.description && (
                                            <p className="text-[11px] text-muted-foreground leading-relaxed max-w-xl">
                                              {topic.description}
                                            </p>
                                          )}

                                          {/* Metrics Grid */}
                                          {!isLocked && (
                                            <div className="flex flex-wrap items-center gap-4 pt-1 border-t border-card-border/50">
                                              <div className="flex items-center gap-1.5 text-[10px] text-zinc-500 font-mono">
                                                <Clock className="w-3 h-3 text-info-cyan" />
                                                <span>EST: {topic.estimated_time || 15} mins</span>
                                              </div>
                                              <div className="flex items-center gap-1.5 text-[10px] text-xp-gold font-mono font-bold">
                                                <Zap className="w-3 h-3 text-xp-gold" />
                                                <span>+{topic.xp_reward} XP</span>
                                              </div>
                                              <div className="flex items-center gap-1.5 text-[10px] text-zinc-500 font-mono">
                                                <Video className="w-3 h-3 text-primary" />
                                                <span>Video Tutorial Attached</span>
                                              </div>
                                            </div>
                                          )}
                                        </div>

                                        <div className="flex items-center justify-end">
                                          {isLocked ? (
                                            <div className="p-2 rounded-lg bg-zinc-950 border border-zinc-900/60 text-zinc-700">
                                              <Lock className="w-4 h-4" />
                                            </div>
                                          ) : (
                                            <Link href={`/roadmap/node/${topic.id}`}>
                                              <button className="px-4 py-2.5 rounded-lg bg-primary hover:bg-primary/90 text-white font-bold text-xs uppercase tracking-wide flex items-center justify-center gap-1.5 shadow-md shadow-primary/10 transition-all duration-200 cursor-pointer">
                                                <Play className="w-3 h-3 fill-white" />
                                                <span>Watch Video</span>
                                                <ChevronRight className="w-3.5 h-3.5" />
                                              </button>
                                            </Link>
                                          )}
                                        </div>
                                      </div>
                                    </div>
                                  );
                                })}
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      );
                    })}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </div>
  );
}
