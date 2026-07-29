"use client";

// Prevent static generation — this page requires live user auth and backend data
export const dynamic = "force-dynamic";

import React, { useEffect, useState, useMemo, useRef } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

import { useAuthUser } from "@/hooks/use-auth-user";
import { RoadmapHeader } from "@/components/roadmap/RoadmapHeader";
import { RoadmapQuickActions } from "@/components/roadmap/RoadmapQuickActions";
import { StepCard } from "@/components/roadmap/StepCard";
import { RecentlyCompletedSection } from "@/components/roadmap/RecentlyCompletedSection";
import { AchievementsSection } from "@/components/roadmap/AchievementsSection";
import { RoadmapNode } from "@/components/roadmap/LessonRow";

interface OverallProgress {
  topic_name: string;
  completed_videos: number;
  total_videos: number;
  progress_percentage: number;
  overall_xp: number;
}

interface RecentlyViewedLesson {
  id: string;
  title: string;
  stepTitle?: string;
}

import { BACKEND_URL } from "@/lib/api-config";


export default function RoadmapPage() {
  const router = useRouter();
  const { stats, isLoaded } = useAuthUser();

  const [nodes, setNodes] = useState<RoadmapNode[]>([]);
  const [overallProgress, setOverallProgress] = useState<OverallProgress>({
    topic_name: "Striver A2Z DSA Sheet",
    completed_videos: 0,
    total_videos: 0,
    progress_percentage: 0,
    overall_xp: 0,
  });
  const [loading, setLoading] = useState(true);
  const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>({});

  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState("");
  const [activeFilter, setActiveFilter] = useState("ALL");

  // Recently viewed lessons history
  const [recentlyViewed, setRecentlyViewed] = useState<RecentlyViewedLesson[]>([]);

  // Ref to container for scroll jump
  const stepContainerRef = useRef<HTMLDivElement>(null);

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
          const data: RoadmapNode[] = await nodesRes.json();
          setNodes(data);

          // Smart auto-expansion: expand active current path, collapse completed steps
          const autoExpanded = getSmartExpandedNodes(data);
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

  // Smart Collapsing Logic:
  // - Completed steps collapsed by default
  // - Current active step & section expanded
  const getSmartExpandedNodes = (nodeList: RoadmapNode[]): Record<string, boolean> => {
    const expanded: Record<string, boolean> = {};
    let currentFound = false;

    for (const step of nodeList) {
      const stepSections = step.children || [];
      const stepLessons = stepSections.flatMap((s) => s.children || []);
      const isStepCompleted =
        stepLessons.length > 0 &&
        stepLessons.every((l) => l.is_completed || (l.status || "").toUpperCase() === "COMPLETED");

      if (!isStepCompleted && !currentFound) {
        // Expand current step
        expanded[step.id] = true;
        currentFound = true;

        for (const sec of stepSections) {
          const secLessons = sec.children || [];
          const isSecCompleted =
            secLessons.length > 0 &&
            secLessons.every((l) => l.is_completed || (l.status || "").toUpperCase() === "COMPLETED");

          if (!isSecCompleted) {
            expanded[sec.id] = true;
            break;
          }
        }
      }
    }

    // Fallback: If all are completed or none expanded, expand Step 1
    if (Object.keys(expanded).length === 0 && nodeList.length > 0) {
      expanded[nodeList[0].id] = true;
      if (nodeList[0].children?.[0]) {
        expanded[nodeList[0].children[0].id] = true;
      }
    }

    return expanded;
  };

  // Locate next unlocked lesson
  const findNextUnlockedLesson = (
    nodeList: RoadmapNode[]
  ): { lesson: RoadmapNode; stepTitle: string; secTitle: string } | null => {
    for (const step of nodeList) {
      for (const sec of step.children || []) {
        for (const lesson of sec.children || []) {
          const status = (
            lesson.status || (lesson.is_completed ? "COMPLETED" : lesson.is_locked ? "LOCKED" : "AVAILABLE")
          ).toUpperCase();

          if (status !== "COMPLETED" && status !== "LOCKED") {
            return { lesson, stepTitle: step.title, secTitle: sec.title };
          }
        }
      }
    }
    // Fallback to first lesson
    if (nodeList[0]?.children[0]?.children[0]) {
      return {
        lesson: nodeList[0].children[0].children[0],
        stepTitle: nodeList[0].title,
        secTitle: nodeList[0].children[0].title,
      };
    }
    return null;
  };

  const nextUnlockedInfo = useMemo(() => {
    return findNextUnlockedLesson(nodes);
  }, [nodes]);

  // Aggregate metrics (Duration calculations removed)
  const { totalLessonsCount, completedLessonsCount, allCompletedLessons } = useMemo(() => {
    let total = 0;
    let completed = 0;
    const completedList: RoadmapNode[] = [];

    nodes.forEach((step) => {
      (step.children || []).forEach((sec) => {
        (sec.children || []).forEach((lesson) => {
          total += 1;
          const status = (
            lesson.status || (lesson.is_completed ? "COMPLETED" : "LOCKED")
          ).toUpperCase();

          if (status === "COMPLETED" || lesson.is_completed) {
            completed += 1;
            completedList.push(lesson);
          }
        });
      });
    });

    return {
      totalLessonsCount: total,
      completedLessonsCount: completed,
      allCompletedLessons: completedList,
    };
  }, [nodes]);

  // Toggle node expansion
  const toggleStepExpand = (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setExpandedNodes((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const toggleSectionExpand = (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setExpandedNodes((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  // Expand all / Collapse all handlers
  const handleExpandAll = () => {
    const allExpanded: Record<string, boolean> = {};
    nodes.forEach((step) => {
      allExpanded[step.id] = true;
      (step.children || []).forEach((sec) => {
        allExpanded[sec.id] = true;
      });
    });
    setExpandedNodes(allExpanded);
  };

  const handleCollapseAll = () => {
    setExpandedNodes({});
  };

  const handleJumpToCurrentStep = () => {
    if (stepContainerRef.current) {
      stepContainerRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  const handleContinueLearning = () => {
    if (nextUnlockedInfo) {
      router.push(`/roadmap/node/${nextUnlockedInfo.lesson.id}`);
    }
  };

  const handleSelectLesson = (lesson: RoadmapNode, stepTitle?: string) => {
    // Update recently viewed history
    setRecentlyViewed((prev) => {
      const filtered = prev.filter((item) => item.id !== lesson.id);
      return [{ id: lesson.id, title: lesson.title, stepTitle }, ...filtered].slice(0, 5);
    });
  };

  const handleNavigateLesson = (lesson: RoadmapNode) => {
    router.push(`/roadmap/node/${lesson.id}`);
  };

  // Filtered nodes logic based on search query or active status filter
  const processedNodes = useMemo(() => {
    if (!searchQuery.trim() && activeFilter === "ALL") {
      return nodes;
    }

    const q = searchQuery.toLowerCase().trim();

    return nodes
      .map((step) => {
        const stepMatches =
          !q ||
          step.title.toLowerCase().includes(q) ||
          (step.description && step.description.toLowerCase().includes(q));

        const filteredSections = (step.children || [])
          .map((sec) => {
            const secMatches = !q || sec.title.toLowerCase().includes(q);

            const filteredLessons = (sec.children || []).filter((lesson) => {
              const status = (
                lesson.status || (lesson.is_completed ? "COMPLETED" : lesson.is_locked ? "LOCKED" : "AVAILABLE")
              ).toUpperCase();

              // Status Filter Check
              if (activeFilter === "COMPLETED" && !(status === "COMPLETED" || lesson.is_completed)) return false;
              if (activeFilter === "IN_PROGRESS" && status !== "IN_PROGRESS") return false;
              if (activeFilter === "NOT_STARTED" && (status === "COMPLETED" || status === "IN_PROGRESS" || lesson.is_completed)) return false;

              // Search Match Check
              if (!q) return true;
              return (
                lesson.title.toLowerCase().includes(q) ||
                lesson.slug.toLowerCase().includes(q) ||
                lesson.id.toLowerCase().includes(q) ||
                stepMatches ||
                secMatches
              );
            });

            if (filteredLessons.length > 0 || secMatches) {
              return { ...sec, children: filteredLessons };
            }
            return null;
          })
          .filter(Boolean) as RoadmapNode[];

        if (filteredSections.length > 0 || stepMatches) {
          return { ...step, children: filteredSections };
        }
        return null;
      })
      .filter(Boolean) as RoadmapNode[];
  }, [nodes, searchQuery, activeFilter]);

  // Auto-expand matching steps/sections when searching
  useEffect(() => {
    if (searchQuery.trim()) {
      const searchExpanded: Record<string, boolean> = {};
      processedNodes.forEach((step) => {
        searchExpanded[step.id] = true;
        (step.children || []).forEach((sec) => {
          searchExpanded[sec.id] = true;
        });
      });
      setExpandedNodes(searchExpanded);
    }
  }, [searchQuery, processedNodes]);

  if (!isLoaded || loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" />
        <p className="text-sm font-semibold text-slate-400">Loading DSA Arena Roadmap...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 pb-16 max-w-6xl mx-auto px-2 sm:px-4">
      {/* 1. TOP HEADER & CONTINUE LEARNING CARD */}
      <RoadmapHeader
        userName={stats?.display_name || "Coder"}
        completedLessons={completedLessonsCount}
        totalLessons={totalLessonsCount}
        overallProgressPct={overallProgress.progress_percentage || 0}
        currentStepTitle={nextUnlockedInfo?.stepTitle || "Step 1: Learn the Basics"}
        nextUnlockedLesson={nextUnlockedInfo}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        activeFilter={activeFilter}
        onFilterChange={setActiveFilter}
        onContinueLearning={handleContinueLearning}
      />

      {/* 2. QUICK ACTIONS BAR */}
      <RoadmapQuickActions
        onExpandAll={handleExpandAll}
        onCollapseAll={handleCollapseAll}
        onJumpToCurrentStep={handleJumpToCurrentStep}
        onResumeLastLesson={handleContinueLearning}
        recentlyViewed={recentlyViewed}
        onSelectRecentLesson={(id) => {
          for (const step of nodes) {
            for (const sec of step.children || []) {
              for (const l of sec.children || []) {
                if (l.id === id) {
                  handleSelectLesson(l, step.title);
                  handleNavigateLesson(l);
                  return;
                }
              }
            }
          }
        }}
      />

      {/* 3. EXPANDED FULL-WIDTH LEARNING JOURNEY */}
      <div ref={stepContainerRef} className="space-y-4 pt-1">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-extrabold text-white tracking-tight">Learning Journey</h2>
          <span className="text-xs font-semibold text-slate-400">
            {processedNodes.length} Steps
          </span>
        </div>

        {processedNodes.length === 0 ? (
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-10 text-center space-y-3">
            <p className="text-sm font-bold text-slate-300">No lessons found</p>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              No step, section, or lesson matches &quot;{searchQuery}&quot;. Try clearing filters or searching for another term.
            </p>
            <button
              type="button"
              onClick={() => {
                setSearchQuery("");
                setActiveFilter("ALL");
              }}
              className="mt-2 text-xs font-bold text-cyan-400 bg-cyan-500/10 border border-cyan-500/20 px-3.5 py-1.5 rounded-lg hover:bg-cyan-500/20"
            >
              Clear Search & Filters
            </button>
          </div>
        ) : (
          processedNodes.map((step, idx) => (
            <StepCard
              key={step.id}
              step={step}
              stepIndex={idx}
              isExpanded={Boolean(expandedNodes[step.id])}
              expandedSections={expandedNodes}
              onToggleStepExpand={toggleStepExpand}
              onToggleSectionExpand={toggleSectionExpand}
              currentLessonId={nextUnlockedInfo?.lesson.id}
              searchQuery={searchQuery}
              onSelectLesson={handleSelectLesson}
              onNavigateLesson={handleNavigateLesson}
            />
          ))
        )}
      </div>

      {/* 4. BOTTOM SECTION: RECENTLY COMPLETED & ACHIEVEMENTS */}
      <RecentlyCompletedSection
        completedLessons={allCompletedLessons}
        onSelectLesson={(lesson) => {
          handleSelectLesson(lesson);
          handleNavigateLesson(lesson);
        }}
      />

      <AchievementsSection />

      {/* 5. MOBILE STICKY FLOATING CONTINUE LEARNING CTA */}
      {nextUnlockedInfo && (
        <div className="sm:hidden fixed bottom-4 left-4 right-4 z-40 bg-slate-950/95 border border-cyan-500/40 p-3 rounded-xl shadow-2xl backdrop-blur-md flex items-center justify-between">
          <div className="truncate pr-2">
            <span className="text-[9px] font-mono text-cyan-400 uppercase font-bold block">Continue Learning</span>
            <span className="text-xs font-bold text-white truncate block">{nextUnlockedInfo.lesson.title}</span>
          </div>

          <button
            type="button"
            onClick={handleContinueLearning}
            className="px-3.5 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-indigo-600 text-slate-950 font-extrabold text-xs uppercase tracking-wider flex items-center space-x-1 shrink-0 shadow-md shadow-cyan-500/30 active:scale-95"
          >
            <span>Resume</span>
          </button>
        </div>
      )}
    </div>
  );
}
