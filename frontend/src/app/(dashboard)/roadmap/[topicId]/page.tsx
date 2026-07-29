"use client";

export const dynamic = "force-dynamic";

import { useEffect, useState, use } from "react";
import { useAuthUser } from "@/hooks/use-auth-user";
import { ArrowLeft, BookOpen, Video, FileText, CheckCircle2, ChevronRight, Play, Sparkles, Loader2, Lock, Zap, Award, Clock, Check, X, Bookmark, BookmarkCheck, Code2 } from "lucide-react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";

// Learning Engine Components
import { StickyNavigation } from "@/components/learning/sticky-navigation";
import { OverviewSection } from "@/components/learning/overview-section";
import { ResourcesSection, LearningResource } from "@/components/learning/resources-section";
import { KeyConceptsSection, KeyConceptItem } from "@/components/learning/key-concepts-section";
import { VisualLearningSection, VisualPlaceholder } from "@/components/learning/visual-learning-section";
import { NotesSection } from "@/components/learning/notes-section";
import { ChecklistSection, LearningChecklistData } from "@/components/learning/checklist-section";

interface Problem {
  id: string;
  title: string;
  difficulty: string;
  xp_reward: number;
  status?: string;
  is_bookmarked?: boolean;
}

interface QuizQuestion {
  id: number;
  question: string;
  type: string;
  options: string[];
  difficulty: string;
  order_index: number;
}

interface QuizAttempt {
  id: number;
  score: number;
  time_taken: number;
  attempt_number: number;
  completed_at: string;
}

interface QuizData {
  id: number;
  topic_id: string;
  title: string;
  description: string;
  difficulty: string;
  estimated_time: number;
  questions: QuizQuestion[];
  best_score: number | null;
  previous_attempts: QuizAttempt[];
}

interface QuizExplanation {
  correct: boolean;
  correct_answer: number[];
  explanation: string;
}

interface QuizSubmissionResult {
  score: number;
  xp_earned: number;
  correct_answers_count: number;
  wrong_answers_count: number;
  explanations: Record<string, QuizExplanation>;
  perfect_bonus: boolean;
  speed_bonus: boolean;
  first_attempt_bonus: boolean;
  attempt_number: number;
  newly_unlocked_achievements: Array<{
    id: string;
    title: string;
    description: string;
    icon: string;
  }>;
}

interface TopicOverview {
  id: string;
  title: string;
  description: string;
  difficulty: string;
  estimated_time: number;
  xp_reward: number;
  prerequisites: string[];
  learning_objectives: string[];
  is_bookmarked: boolean;
}

import { BACKEND_URL } from "@/lib/api-config";


export default function TopicPage({ params }: { params: Promise<{ topicId: string }> }) {
  const { topicId } = use(params);
  const { stats, isLoaded, refreshStats } = useAuthUser();
  const clerkId = stats?.clerk_id || "mock_user_striver";

  // Page States
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState("overview");

  // Learning Content States
  const [overview, setOverview] = useState<TopicOverview | null>(null);
  const [resources, setResources] = useState<LearningResource[]>([]);
  const [keyConcepts, setKeyConcepts] = useState<KeyConceptItem[]>([]);
  const [visualPlaceholders, setVisualPlaceholders] = useState<VisualPlaceholder[]>([]);
  const [noteContent, setNoteContent] = useState("");
  const [noteUpdatedAt, setNoteUpdatedAt] = useState<string | null>(null);
  const [checklist, setChecklist] = useState<LearningChecklistData>({
    watched_video: false,
    read_notes: false,
    understood_concepts: false,
    completed_quiz: false,
    solved_problems: false,
  });

  // Problems & Quiz States
  const [problems, setProblems] = useState<Problem[]>([]);
  const [quiz, setQuiz] = useState<QuizData | null>(null);
  const [quizLoading, setQuizLoading] = useState(true);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  useEffect(() => {
    if (!isLoaded) return;

    async function fetchLearningData() {
      try {
        setLoading(true);
        setError(null);

        const [contentRes, topicRes, quizRes, bmarkRes] = await Promise.all([
          fetch(`${BACKEND_URL}/roadmap/topics/${topicId}/learning-content?clerk_id=${clerkId}`),
          fetch(`${BACKEND_URL}/roadmap/topics/${topicId}?clerk_id=${clerkId}`),
          fetch(`${BACKEND_URL}/roadmap/topics/${topicId}/quiz?clerk_id=${clerkId}`),
          fetch(`${BACKEND_URL}/users/${clerkId}/bookmarks`),
        ]);

        if (contentRes.ok) {
          const cData = await contentRes.json();
          setOverview(cData.topic);
          setResources(cData.resources || []);
          setKeyConcepts(cData.key_concepts || []);
          setVisualPlaceholders(cData.visual_learning || []);
          if (cData.user_note) {
            setNoteContent(cData.user_note.content || "");
            setNoteUpdatedAt(cData.user_note.updated_at || null);
          }
          if (cData.checklist) {
            setChecklist(cData.checklist);
          }
        }

        let bookmarkedProbIds = new Set<string>();
        if (bmarkRes.ok) {
          const bData = await bmarkRes.json();
          bookmarkedProbIds = new Set((bData.problems || []).map((p: { target_id: string }) => p.target_id));
        }

        if (topicRes.ok) {
          const tData = await topicRes.json();
          const enriched = (tData.problems || []).map((p: Problem) => ({
            ...p,
            is_bookmarked: bookmarkedProbIds.has(p.id),
          }));
          setProblems(enriched);
        }

        if (quizRes.ok) {
          const qData = await quizRes.json();
          setQuiz(qData);
        }
      } catch (err) {
        console.error("Error fetching learning engine data:", err);
        setError("Failed to load topic learning data. Please try again.");
      } finally {
        setLoading(false);
        setQuizLoading(false);
      }
    }

    fetchLearningData();
  }, [topicId, isLoaded, clerkId]);

  // Section Scroll Target Handler
  const scrollToSection = (secId: string) => {
    setActiveSection(secId);
    const elem = document.getElementById(secId);
    if (elem) {
      elem.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  // Toggle Concept Bookmark
  const toggleConceptBookmark = async () => {
    if (!overview) return;
    try {
      const res = await fetch(`${BACKEND_URL}/users/bookmarks/toggle?clerk_id=${clerkId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_type: "concept", target_id: topicId }),
      });
      if (res.ok) {
        const data = await res.json();
        setOverview({ ...overview, is_bookmarked: data.bookmarked });
        showToast(data.bookmarked ? "Concept bookmarked!" : "Bookmark removed.");
      }
    } catch (err) {
      console.error("Error toggling bookmark:", err);
    }
  };

  // Toggle Resource Bookmark
  const toggleResourceBookmark = async (resourceId: number) => {
    try {
      const res = await fetch(`${BACKEND_URL}/users/bookmarks/toggle?clerk_id=${clerkId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_type: "resource", target_id: resourceId.toString() }),
      });
      if (res.ok) {
        const data = await res.json();
        setResources(
          resources.map((r) => (r.id === resourceId ? { ...r, is_bookmarked: data.bookmarked } : r))
        );
        showToast(data.bookmarked ? "Resource bookmarked!" : "Bookmark removed.");
      }
    } catch (err) {
      console.error("Error toggling resource bookmark:", err);
    }
  };

  // Toggle Problem Bookmark
  const toggleProblemBookmark = async (problemId: string) => {
    try {
      const res = await fetch(`${BACKEND_URL}/users/bookmarks/toggle?clerk_id=${clerkId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_type: "problem", target_id: problemId }),
      });
      if (res.ok) {
        const data = await res.json();
        setProblems(
          problems.map((p) => (p.id === problemId ? { ...p, is_bookmarked: data.bookmarked } : p))
        );
        showToast(data.bookmarked ? "Problem bookmarked!" : "Bookmark removed.");
      }
    } catch (err) {
      console.error("Error toggling problem bookmark:", err);
    }
  };

  // Save Notes Handler
  const handleSaveNotes = async (newContent: string) => {
    try {
      const res = await fetch(`${BACKEND_URL}/roadmap/topics/${topicId}/notes?clerk_id=${clerkId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: newContent }),
      });
      if (res.ok) {
        const data = await res.json();
        setNoteContent(data.content);
        setNoteUpdatedAt(data.updated_at);
      }
    } catch (err) {
      console.error("Error saving notes:", err);
    }
  };

  // Toggle Checklist Handler
  const handleToggleChecklist = async (key: keyof LearningChecklistData) => {
    const updatedVal = !checklist[key];
    const updatedChecklist = { ...checklist, [key]: updatedVal };
    setChecklist(updatedChecklist);

    try {
      const res = await fetch(`${BACKEND_URL}/roadmap/topics/${topicId}/checklist?clerk_id=${clerkId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ [key]: updatedVal }),
      });
      if (res.ok) {
        const data = await res.json();
        setChecklist(data);
        await refreshStats();
        showToast("Learning checklist updated!");
      }
    } catch (err) {
      console.error("Error updating checklist:", err);
    }
  };

  const getDifficultyColor = (diff: string) => {
    switch (diff.toLowerCase()) {
      case "easy":
        return "text-success-emerald bg-success-emerald/10 border-success-emerald/20";
      case "medium":
        return "text-yellow-500 bg-yellow-500/10 border-yellow-500/20";
      case "hard":
        return "text-primary bg-primary/10 border-primary/20";
      default:
        return "text-muted-foreground bg-muted";
    }
  };

  const completedChecklistCount = Object.values(checklist).filter(Boolean).length;
  const progressPercentage = Math.round((completedChecklistCount / 5.0) * 100);

  if (!isLoaded || loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh] gap-4">
        <Loader2 className="w-10 h-10 text-primary animate-spin" />
        <p className="text-xs font-mono text-muted-foreground uppercase tracking-widest">
          LOADING SPRINT 2.4 LEARNING CONTENT ENGINE...
        </p>
      </div>
    );
  }

  if (error || !overview) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[70vh] gap-4 text-center">
        <p className="text-sm text-red-400 font-mono">{error || "Topic content not found."}</p>
        <Link
          href="/roadmap"
          className="px-4 py-2 rounded-xl bg-primary text-white text-xs font-bold uppercase tracking-wider"
        >
          Return to Roadmap
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-20 relative">
      {/* Toast Notification */}
      <AnimatePresence>
        {toastMessage && (
          <motion.div
            className="fixed bottom-6 right-6 border border-primary/30 px-6 py-4 rounded-2xl bg-[#0a0a0f] text-white text-xs font-bold uppercase tracking-wider flex items-center gap-2.5 z-50 shadow-2xl shadow-primary/20"
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
      <Link
        href="/roadmap"
        className="inline-flex items-center gap-2 text-xs font-mono font-bold text-muted-foreground hover:text-white uppercase tracking-wider transition-colors duration-200"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Roadmap
      </Link>

      {/* Sticky Navigation Bar */}
      <StickyNavigation
        activeSection={activeSection}
        onSelectSection={scrollToSection}
        progressPercentage={progressPercentage}
      />

      {/* 1. Overview Section */}
      <OverviewSection
        topic={overview}
        progressPercentage={progressPercentage}
        onToggleBookmark={toggleConceptBookmark}
      />

      {/* 2. Learning Resources Section */}
      <ResourcesSection
        resources={resources}
        onToggleBookmarkResource={toggleResourceBookmark}
      />

      {/* 3. Key Concepts Section */}
      <KeyConceptsSection keyConcepts={keyConcepts} />

      {/* 4. Visual Learning Section */}
      <VisualLearningSection placeholders={visualPlaceholders} />

      {/* 5. Notes Section */}
      <NotesSection
        initialContent={noteContent}
        updatedAt={noteUpdatedAt}
        onSaveNotes={handleSaveNotes}
      />

      {/* 6. Learning Checklist Section */}
      <ChecklistSection
        checklist={checklist}
        onToggleChecklist={handleToggleChecklist}
      />

      {/* 7. Quiz Engine Launch Card Section */}
      <motion.div
        id="quiz"
        className="border border-card-border rounded-3xl p-6 lg:p-8 glass-card space-y-6 relative overflow-hidden"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-card-border/60 pb-4">
          <div>
            <h2 className="text-xl font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Award className="w-5 h-5 text-xp-gold" /> Concept Quiz Battle
            </h2>
            <p className="text-xs text-muted-foreground mt-1">
              Test your recall, unlock XP bonuses, and complete your topic checklist.
            </p>
          </div>

          {quiz && quiz.best_score !== null && (
            <span className="text-xs font-mono font-extrabold text-success-emerald bg-success-emerald/10 border border-success-emerald/20 px-3 py-1.5 rounded-xl flex items-center gap-1.5 shrink-0">
              <CheckCircle2 className="w-4 h-4 text-success-emerald" /> Best Score: {quiz.best_score}%
            </span>
          )}
        </div>

        {quizLoading ? (
          <div className="flex items-center justify-center p-8">
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
          </div>
        ) : !quiz ? (
          <div className="text-center py-6 text-xs text-muted-foreground">
            No quiz available for this topic yet.
          </div>
        ) : (
          <div className="flex flex-col sm:flex-row items-center justify-between gap-6 p-6 rounded-2xl border border-card-border/50 bg-[#030303]/40">
            <div className="space-y-2 text-center sm:text-left">
              <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2">
                <h3 className="text-base font-extrabold text-white">{quiz.title}</h3>
                <span className="text-[10px] font-mono font-bold text-xp-gold bg-xp-gold/10 border border-xp-gold/20 px-2.5 py-0.5 rounded uppercase">
                  {quiz.difficulty}
                </span>
              </div>
              <p className="text-xs text-muted-foreground">{quiz.description}</p>
              <div className="flex items-center justify-center sm:justify-start gap-4 text-xs font-mono text-muted-foreground pt-1">
                <span>⏱ {quiz.estimated_time} Mins</span>
                <span>•</span>
                <span>{quiz.questions ? quiz.questions.length : 5} Questions</span>
                <span>•</span>
                <span className="text-xp-gold font-bold">+50 XP Reward</span>
              </div>
            </div>

            <Link
              href={`/roadmap/${topicId}/quiz`}
              className="w-full sm:w-auto px-6 py-3.5 rounded-2xl bg-gradient-to-r from-primary to-xp-gold hover:opacity-95 text-white font-extrabold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shrink-0 transition-all shadow-lg shadow-primary/20"
            >
              <Zap className="w-4 h-4 fill-white" /> Launch Quiz Battle
            </Link>
          </div>
        )}
      </motion.div>

      {/* 8. Coding Problems Section */}
      <motion.div
        id="problems"
        className="border border-card-border rounded-3xl p-6 lg:p-8 glass-card space-y-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex justify-between items-center border-b border-card-border/60 pb-4">
          <div>
            <h2 className="text-xl font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Code2 className="w-5 h-5 text-primary" /> Roadmap Problems
            </h2>
            <p className="text-xs text-muted-foreground mt-1">
              Practice coding challenges associated with this concept node.
            </p>
          </div>
          <span className="text-xs font-mono font-bold text-muted-foreground px-2.5 py-1 rounded bg-muted border border-card-border">
            {problems.length} PROBLEMS
          </span>
        </div>

        {problems.length === 0 ? (
          <div className="text-center py-8 text-xs text-muted-foreground">
            No coding problems defined for this topic.
          </div>
        ) : (
          <div className="space-y-3">
            {problems.map((p) => {
              const problemSolved =
                p.status === "SOLVED" || p.status === "MASTERED" || p.status === "REVISION_DUE";

              return (
                <div
                  key={p.id}
                  className="p-4 rounded-2xl border border-card-border bg-[#030303]/40 flex items-center justify-between gap-4 hover:border-card-border/80 transition-all"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <h4
                        className={`text-sm font-bold ${
                          problemSolved ? "text-success-emerald line-through" : "text-white"
                        }`}
                      >
                        {p.title}
                      </h4>
                      <span
                        className={`text-[9px] font-extrabold uppercase px-2 py-0.5 rounded border font-mono ${getDifficultyColor(
                          p.difficulty
                        )}`}
                      >
                        {p.difficulty}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => toggleProblemBookmark(p.id)}
                      className={`p-2 rounded-xl border text-xs cursor-pointer transition-all ${
                        p.is_bookmarked
                          ? "bg-xp-gold/10 border-xp-gold/30 text-xp-gold"
                          : "border-card-border text-muted-foreground hover:text-white"
                      }`}
                    >
                      {p.is_bookmarked ? (
                        <BookmarkCheck className="w-4 h-4 fill-xp-gold" />
                      ) : (
                        <Bookmark className="w-4 h-4" />
                      )}
                    </button>

                    <Link
                      href={`/roadmap/${topicId}/${p.id}`}
                      className="px-4 py-2 rounded-xl bg-primary hover:bg-primary/90 text-white font-bold text-xs uppercase tracking-wider flex items-center gap-1 transition-all"
                    >
                      <span>Solve Workspace</span>
                      <ChevronRight className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </motion.div>
    </div>
  );
}
