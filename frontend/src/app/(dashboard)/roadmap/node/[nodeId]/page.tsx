"use client";

import React, { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { useAuthUser } from "@/hooks/use-auth-user";
import { ArrowLeft, AlertCircle, Loader2, StickyNote, Sparkles } from "lucide-react";
import Link from "next/link";

import { VideoPlayer } from "@/components/roadmap/VideoPlayer";
import { LessonHeader } from "@/components/roadmap/LessonHeader";
import { LearningObjectivesCard } from "@/components/roadmap/LearningObjectivesCard";
import { PrerequisiteCard, PrerequisiteItem } from "@/components/roadmap/PrerequisiteCard";
import { ProgressCard } from "@/components/roadmap/ProgressCard";
import { LessonSidebar, SidebarLessonNode } from "@/components/roadmap/LessonSidebar";
import { LessonNavigation, NavigationNode } from "@/components/roadmap/LessonNavigation";
import { CompletionBanner } from "@/components/roadmap/CompletionBanner";
import { CompletionDialog } from "@/components/roadmap/CompletionDialog";

import { LessonTabs, LessonTabType } from "@/components/roadmap/LessonTabs";
import { NotesPanel } from "@/components/roadmap/NotesPanel";
import { SummaryCard, TakeawaysData } from "@/components/roadmap/SummaryCard";
import { TipCard, TipsData } from "@/components/roadmap/TipCard";
import { ResourceCard, ResourceItem } from "@/components/roadmap/ResourceCard";

interface NodeData {
  id: string;
  title: string;
  description?: string | null;
  order: number;
  parent_id?: string | null;
  parent_title?: string | null;
  difficulty?: string | null;
  estimated_duration: number;
  youtube_url?: string | null;
  youtube_video_id?: string | null;
  thumbnail_url?: string | null;
  is_locked: boolean;
  status: string;
  prerequisites?: string[];
  prerequisites_details?: PrerequisiteItem[];
  learning_objectives?: {
    what_you_will_learn?: string[];
    why_this_topic_matters?: string | null;
    real_world_applications?: string[];
    interview_questions?: string[];
  } | null;
  metadata?: Record<string, any>;
  progress?: {
    user_id: number;
    node_id: string;
    status: string;
    started_at?: string | null;
    completed_at?: string | null;
    completed: boolean;
  } | null;
}

interface HubData {
  notes?: { id: number; node_id: string; content: string; updated_at?: string | null };
  takeaways?: TakeawaysData;
  tips?: TipsData;
  resources?: ResourceItem[];
}

interface RoadmapProgressStats {
  totalVideos: number;
  completedVideos: number;
  progressPercentage: number;
}

const BACKEND_URL = "http://127.0.0.1:8000/api/v1";

export default function LessonPage({ params }: { params: Promise<{ nodeId: string }> }) {
  const { nodeId } = use(params);
  const router = useRouter();
  const { stats, isLoaded } = useAuthUser();
  const clerkId = stats?.clerk_id || "mock_user_striver";

  const [node, setNode] = useState<NodeData | null>(null);
  const [hubData, setHubData] = useState<HubData | null>(null);
  const [previousNode, setPreviousNode] = useState<NavigationNode | null>(null);
  const [nextNode, setNextNode] = useState<NavigationNode | null>(null);
  const [allLessons, setAllLessons] = useState<SidebarLessonNode[]>([]);
  const [progressStats, setProgressStats] = useState<RoadmapProgressStats>({
    totalVideos: 0,
    completedVideos: 0,
    progressPercentage: 0,
  });

  const [activeTab, setActiveTab] = useState<LessonTabType>("learn");
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCompletionDialog, setShowCompletionDialog] = useState(false);
  const [quickNoteText, setQuickNoteText] = useState("");

  useEffect(() => {
    if (!isLoaded) return;

    async function fetchLessonData() {
      try {
        setLoading(true);
        setError(null);

        // Parallel fetch for lesson details, hub content, prev, next, nodes tree, and progress
        const [nodeRes, hubRes, prevRes, nextRes, nodesRes, progressRes] = await Promise.all([
          fetch(`${BACKEND_URL}/roadmap/nodes/${nodeId}?clerk_id=${clerkId}`),
          fetch(`${BACKEND_URL}/roadmap/nodes/${nodeId}/hub?clerk_id=${clerkId}`),
          fetch(`${BACKEND_URL}/roadmap/nodes/${nodeId}/previous?clerk_id=${clerkId}`),
          fetch(`${BACKEND_URL}/roadmap/nodes/${nodeId}/next?clerk_id=${clerkId}`),
          fetch(`${BACKEND_URL}/roadmap/all_topics?clerk_id=${clerkId}`),
          fetch(`${BACKEND_URL}/roadmap/progress?clerk_id=${clerkId}`),
        ]);

        if (!nodeRes.ok) {
          throw new Error("Failed to load lesson details.");
        }

        const nodeData: NodeData = await nodeRes.json();
        setNode(nodeData);

        if (hubRes.ok) {
          const hubDataObj: HubData = await hubRes.json();
          setHubData(hubDataObj);
          if (hubDataObj.notes?.content) {
            setQuickNoteText(hubDataObj.notes.content);
          }
        }

        if (prevRes.ok) {
          const prevData = await prevRes.json();
          setPreviousNode(prevData.next_node || null);
        }

        if (nextRes.ok) {
          const nextData = await nextRes.json();
          setNextNode(nextData.next_node || null);
        }

        if (nodesRes.ok) {
          const rawNodes = await nodesRes.json();
          const mappedLessons: SidebarLessonNode[] = (Array.isArray(rawNodes) ? rawNodes : []).map(
            (item: any) => ({
              id: item.id,
              title: item.title,
              order: item.order || item.order_index || 1,
              status: item.status || (item.is_completed ? "COMPLETED" : "LOCKED"),
              is_completed: item.is_completed || item.status === "COMPLETED",
              is_locked: item.is_locked,
              parent_id: item.parent_id,
              parent_title: item.parent_title || item.step_title || "DSA Roadmap",
            })
          );
          setAllLessons(mappedLessons);
        }

        if (progressRes.ok) {
          const progData = await progressRes.json();
          setProgressStats({
            totalVideos: progData.total_videos || 0,
            completedVideos: progData.completed_videos || 0,
            progressPercentage: progData.progress_percentage || 0,
          });
        }
      } catch (err: any) {
        console.error("Error loading lesson page:", err);
        setError(err.message || "Unable to fetch lesson data.");
      } finally {
        setLoading(false);
      }
    }

    fetchLessonData();
  }, [nodeId, isLoaded, clerkId]);

  const handleMarkAsDone = async () => {
    if (!node || completing) return;

    try {
      setCompleting(true);
      const res = await fetch(
        `${BACKEND_URL}/roadmap/nodes/${node.id}/complete?clerk_id=${clerkId}`,
        { method: "POST" }
      );

      if (res.ok) {
        const result = await res.json();

        // Update local status
        setNode((prev) =>
          prev
            ? {
                ...prev,
                status: "COMPLETED",
                is_locked: false,
                progress: {
                  user_id: prev.progress?.user_id || 1,
                  node_id: prev.id,
                  status: "COMPLETED",
                  started_at: prev.progress?.started_at || new Date().toISOString(),
                  completed_at: result.completed_at || new Date().toISOString(),
                  completed: true,
                },
              }
            : null
        );

        if (result.next_node) {
          setNextNode(result.next_node);
        }

        // Update sidebar and overall stats
        setAllLessons((prevList) =>
          prevList.map((l) => (l.id === node.id ? { ...l, status: "COMPLETED", is_completed: true } : l))
        );

        if (result.progress_percentage !== undefined) {
          setProgressStats((prev) => ({
            ...prev,
            completedVideos: prev.completedVideos + 1,
            progressPercentage: result.progress_percentage,
          }));
        }

        setShowCompletionDialog(true);
      } else {
        console.error("Failed to complete node");
      }
    } catch (err) {
      console.error("Error completing lesson:", err);
    } finally {
      setCompleting(false);
    }
  };

  const handleGoToNextNode = () => {
    if (nextNode) {
      router.push(`/roadmap/node/${nextNode.id}`);
    }
  };

  if (!isLoaded || loading) {
    return (
      <div className="max-w-7xl mx-auto space-y-8 p-4 sm:p-6 pb-20 animate-pulse">
        <div className="h-6 w-36 bg-zinc-900 rounded-xl" />
        <div className="h-10 w-2/3 bg-zinc-900 rounded-2xl" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <div className="h-12 w-full bg-zinc-900 rounded-2xl" />
            <div className="aspect-video w-full bg-zinc-900 rounded-3xl" />
            <div className="h-40 w-full bg-zinc-900 rounded-3xl" />
          </div>
          <div className="space-y-6">
            <div className="h-48 w-full bg-zinc-900 rounded-3xl" />
            <div className="h-64 w-full bg-zinc-900 rounded-3xl" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !node) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[70vh] gap-4 text-center p-6">
        <div className="p-4 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400">
          <AlertCircle className="w-10 h-10" />
        </div>
        <h2 className="text-2xl font-bold text-white uppercase">Lesson Not Found</h2>
        <p className="text-sm text-zinc-400 max-w-md">
          {error || "The requested roadmap lesson could not be loaded."}
        </p>
        <Link href="/roadmap">
          <button className="px-5 py-2.5 rounded-xl bg-zinc-900 border border-zinc-800 text-white font-bold text-xs uppercase flex items-center gap-2 hover:bg-zinc-800">
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Roadmap</span>
          </button>
        </Link>
      </div>
    );
  }

  const isCompleted = node.status === "COMPLETED" || Boolean(node.progress?.completed);

  // Tab 1 Learn Content Node
  const learnTabContent = (
    <div className="space-y-6">
      {/* Video Player */}
      <VideoPlayer
        youtubeUrl={node.youtube_url}
        videoId={node.youtube_video_id}
        thumbnailUrl={node.thumbnail_url}
        title={node.title}
      />

      {/* Learning Objectives */}
      <LearningObjectivesCard
        objectives={node.learning_objectives}
        lessonTitle={node.title}
      />

      {/* Prerequisites */}
      <PrerequisiteCard prerequisites={node.prerequisites_details} />
    </div>
  );

  // Tab 2 Notes Content Node
  const notesTabContent = (
    <NotesPanel
      nodeId={node.id}
      clerkId={clerkId}
      initialContent={hubData?.notes?.content || quickNoteText}
      onNoteUpdated={(txt) => setQuickNoteText(txt)}
    />
  );

  // Tab 3 Key Takeaways Content Node
  const takeawaysTabContent = (
    <SummaryCard takeaways={hubData?.takeaways} lessonTitle={node.title} />
  );

  // Tab 4 Tips Content Node
  const tipsTabContent = (
    <TipCard tips={hubData?.tips} lessonTitle={node.title} />
  );

  // Tab 5 Resources Content Node
  const resourcesTabContent = (
    <ResourceCard resources={hubData?.resources} />
  );

  return (
    <div className="max-w-7xl mx-auto space-y-8 p-4 sm:p-6 pb-24">
      {/* Top Navigation Bar */}
      <div className="flex items-center justify-between">
        <Link href="/roadmap">
          <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-zinc-900/80 hover:bg-zinc-800 border border-zinc-800 text-zinc-300 font-bold text-xs uppercase tracking-wider transition-all">
            <ArrowLeft className="w-4 h-4 text-zinc-400" />
            <span>Back to Roadmap</span>
          </button>
        </Link>
      </div>

      {/* Lesson Header */}
      <LessonHeader
        lessonNumber={node.order}
        title={node.title}
        parentTitle={node.parent_title}
        estimatedDuration={node.estimated_duration}
        difficulty={node.difficulty}
        status={node.status}
      />

      {/* Two Column Responsive Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* LEFT COLUMN: 5-Tab Knowledge Hub (Learn, Notes, Takeaways, Tips, Resources) */}
        <div className="lg:col-span-2 space-y-6">
          <LessonTabs
            activeTab={activeTab}
            onTabChange={(tab) => setActiveTab(tab)}
            learnContent={learnTabContent}
            notesContent={notesTabContent}
            takeawaysContent={takeawaysTabContent}
            tipsContent={tipsTabContent}
            resourcesContent={resourcesTabContent}
          />
        </div>

        {/* RIGHT COLUMN: Status, Progress, Quick Notes & Sidebar */}
        <div className="space-y-6">
          {/* Completion Banner */}
          <CompletionBanner
            isCompleted={isCompleted}
            completing={completing}
            xpReward={node.metadata?.xp_reward || 100}
            onMarkAsDone={handleMarkAsDone}
            onContinueLearning={handleGoToNextNode}
            hasNextNode={Boolean(nextNode)}
          />

          {/* Progress Metrics Summary */}
          <ProgressCard
            completedCount={progressStats.completedVideos}
            totalCount={progressStats.totalVideos}
            progressPercentage={progressStats.progressPercentage}
            estimatedTimeMins={node.estimated_duration}
            lessonStatus={node.status}
          />

          {/* Quick Notes Widget */}
          <div className="rounded-2xl border border-zinc-800 bg-zinc-950/90 p-5 space-y-3 shadow-xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-mono font-bold uppercase tracking-wider text-zinc-300">
                <StickyNote className="w-4 h-4 text-cyan-400" />
                <span>QUICK NOTES</span>
              </div>
              <span className="text-[10px] text-zinc-500 font-mono">AUTOSAVED</span>
            </div>
            <textarea
              value={quickNoteText}
              onChange={(e) => setQuickNoteText(e.target.value)}
              placeholder="Jot down quick thoughts or revision formulas..."
              className="w-full h-24 p-3 rounded-xl bg-zinc-900/60 border border-zinc-800/80 text-xs text-zinc-200 placeholder:text-zinc-600 focus:outline-none focus:border-cyan-500/50 resize-none font-mono"
            />
          </div>

          {/* Sidebar Roadmap */}
          <LessonSidebar currentNodeId={node.id} lessons={allLessons} />
        </div>
      </div>

      {/* Lesson Navigation Footer */}
      <LessonNavigation
        previousNode={previousNode}
        currentNode={{ id: node.id, title: node.title }}
        nextNode={nextNode}
        isCompleted={isCompleted}
        onNavigateNext={handleGoToNextNode}
      />

      {/* Completion Celebration Modal */}
      <CompletionDialog
        isOpen={showCompletionDialog}
        onClose={() => setShowCompletionDialog(false)}
        nodeTitle={node.title}
        nextNodeId={nextNode?.id}
        onGoToNextNode={handleGoToNextNode}
      />
    </div>
  );
}
