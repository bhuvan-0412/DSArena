"use client";

import { useEffect, useState, use } from "react";
import { useAuthUser } from "@/hooks/use-auth-user";
import {
  ArrowLeft,
  Award,
  Clock,
  Zap,
  CheckCircle2,
  XCircle,
  AlertCircle,
  HelpCircle,
  Bookmark,
  BookmarkCheck,
  Flag,
  RotateCcw,
  ChevronRight,
  ChevronLeft,
  Sparkles,
  Loader2,
  Check,
  X,
  Target,
  Trophy,
  BarChart2,
  BookOpen
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

interface QuizStartData {
  id: number;
  topic_id: string;
  title: string;
  description: string;
  difficulty: string;
  estimated_time: number;
  xp_reward: number;
  pass_mark: number;
  question_count: number;
  best_score: number | null;
  attempt_count: number;
  previous_attempts: Array<{
    id: number;
    score: number;
    time_taken: number;
    attempt_number: number;
    xp_earned: number;
    completed_at: string;
  }>;
}

interface Question {
  id: number;
  question: string;
  type: string; // 'MCQ', 'MULTIPLE_SELECT', 'TRUE_FALSE', 'ARRANGE_ORDER', 'FILL_BLANK'
  options: string[];
  difficulty: string;
  order_index: number;
  tags?: string[];
  concept?: string;
  expected_time_seconds?: number;
  hints?: string[];
}

interface QuestionReview {
  id: number;
  question: string;
  type: string;
  options: string[];
  user_answer: number[];
  correct_answer: number[];
  is_correct: boolean;
  is_skipped: boolean;
  explanation?: string;
  option_explanations?: string[];
  concept?: string;
  tags?: string[];
}

interface QuizSubmissionResult {
  attempt_id: number;
  score: number;
  passed: boolean;
  correct_count: number;
  incorrect_count: number;
  skipped_count: number;
  time_taken: number;
  xp_earned: number;
  bonus_xp: number;
  perfect_bonus: boolean;
  speed_bonus: boolean;
  first_attempt_bonus: boolean;
  attempt_number: number;
  questions_review: QuestionReview[];
  newly_unlocked_achievements: Array<{
    id: string;
    title: string;
    description: string;
    icon: string;
  }>;
}

import { BACKEND_URL } from "@/lib/api-config";


export default function StandaloneQuizPage({ params }: { params: Promise<{ topicId: string }> }) {
  const { topicId } = use(params);
  const router = useRouter();
  const { stats, isLoaded, refreshStats } = useAuthUser();
  const clerkId = stats?.clerk_id || "mock_user_striver";

  // Flow State: 'START' | 'QUESTIONS' | 'RESULTS'
  const [quizState, setQuizState] = useState<"START" | "QUESTIONS" | "RESULTS">("START");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Data States
  const [startInfo, setStartInfo] = useState<QuizStartData | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);

  // User Interaction States
  const [answers, setAnswers] = useState<Record<string, number[]>>({});
  const [flagged, setFlagged] = useState<Set<number>>(new Set());
  const [bookmarked, setBookmarked] = useState<Set<number>>(new Set());
  const [skipped, setSkipped] = useState<Set<number>>(new Set());
  const [timer, setTimer] = useState(0);

  // Submission State
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<QuizSubmissionResult | null>(null);
  const [showHint, setShowHint] = useState(false);

  // Toast
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3500);
  };

  // Timer Effect
  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | undefined;
    if (quizState === "QUESTIONS") {
      interval = setInterval(() => {
        setTimer((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [quizState]);

  // Initial Fetch
  useEffect(() => {
    if (!isLoaded) return;
    async function loadQuiz() {
      try {
        setLoading(true);
        const [startRes, qRes] = await Promise.all([
          fetch(`${BACKEND_URL}/roadmap/topics/${topicId}/quiz?clerk_id=${clerkId}`),
          fetch(`${BACKEND_URL}/roadmap/topics/${topicId}/quiz/questions?clerk_id=${clerkId}`),
        ]);

        if (startRes.ok) {
          const sData = await startRes.json();
          setStartInfo(sData);
        } else {
          setError("No quiz available for this topic.");
        }

        if (qRes.ok) {
          const qData = await qRes.json();
          setQuestions(qData.questions || []);
        }
      } catch (err) {
        console.error("Error loading quiz:", err);
        setError("Failed to load quiz data. Please refresh.");
      } finally {
        setLoading(false);
      }
    }
    loadQuiz();
  }, [topicId, isLoaded, clerkId]);

  // Keyboard navigation for questions (1-4, Left, Right)
  useEffect(() => {
    if (quizState !== "QUESTIONS" || questions.length === 0) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;

      const q = questions[currentIdx];
      const qIdStr = q.id.toString();

      // Number keys 1-4 for option selection
      if (["1", "2", "3", "4"].includes(e.key)) {
        const optionIdx = parseInt(e.key) - 1;
        if (optionIdx < q.options.length) {
          toggleOption(q, optionIdx);
        }
      } else if (e.key === "ArrowRight") {
        if (currentIdx < questions.length - 1) {
          setCurrentIdx((prev) => prev + 1);
        }
      } else if (e.key === "ArrowLeft") {
        if (currentIdx > 0) {
          setCurrentIdx((prev) => prev - 1);
        }
      } else if (e.key.toLowerCase() === "s") {
        handleSkip();
      } else if (e.key.toLowerCase() === "f") {
        toggleFlag(q.id);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [quizState, currentIdx, questions, answers]);

  // Option selection logic
  const toggleOption = (q: Question, optionIdx: number) => {
    const qIdStr = q.id.toString();
    const currentAns = answers[qIdStr] || [];

    // Remove from skipped if user answers
    if (skipped.has(q.id)) {
      const nextSkipped = new Set(skipped);
      nextSkipped.delete(q.id);
      setSkipped(nextSkipped);
    }

    if (q.type === "MULTIPLE_SELECT") {
      const updated = currentAns.includes(optionIdx)
        ? currentAns.filter((i) => i !== optionIdx)
        : [...currentAns, optionIdx];
      setAnswers({ ...answers, [qIdStr]: updated });
    } else {
      setAnswers({ ...answers, [qIdStr]: [optionIdx] });
    }
  };

  const handleSkip = () => {
    const q = questions[currentIdx];
    const nextSkipped = new Set(skipped);
    nextSkipped.add(q.id);
    setSkipped(nextSkipped);
    showToast(`Question ${currentIdx + 1} skipped.`);
    if (currentIdx < questions.length - 1) {
      setCurrentIdx((prev) => prev + 1);
    }
  };

  const toggleFlag = (qId: number) => {
    const next = new Set(flagged);
    if (next.has(qId)) {
      next.delete(qId);
      showToast("Flag removed.");
    } else {
      next.add(qId);
      showToast("Question flagged for review.");
    }
    setFlagged(next);
  };

  const toggleBookmark = (qId: number) => {
    const next = new Set(bookmarked);
    if (next.has(qId)) {
      next.delete(qId);
      showToast("Bookmark removed.");
    } else {
      next.add(qId);
      showToast("Question bookmarked!");
    }
    setBookmarked(next);
  };

  const handleSubmit = async () => {
    if (!startInfo) return;
    setSubmitting(true);
    try {
      const payload = {
        time_taken: timer,
        answers: answers,
        flagged_questions: Array.from(flagged),
        skipped_questions: Array.from(skipped),
      };

      const res = await fetch(`${BACKEND_URL}/roadmap/topics/${topicId}/quiz/submit?clerk_id=${clerkId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const resData: QuizSubmissionResult = await res.json();
        setResult(resData);
        setQuizState("RESULTS");
        await refreshStats();
        showToast("Quiz submitted successfully!");
      } else {
        showToast("Error submitting quiz. Please try again.");
      }
    } catch (err) {
      console.error(err);
      showToast("Submission failed. Network error.");
    } finally {
      setSubmitting(false);
    }
  };

  const startQuiz = () => {
    setAnswers({});
    setSkipped(new Set());
    setFlagged(new Set());
    setTimer(0);
    setCurrentIdx(0);
    setResult(null);
    setQuizState("QUESTIONS");
  };

  if (!isLoaded || loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh] gap-4">
        <Loader2 className="w-10 h-10 text-primary animate-spin" />
        <p className="text-xs font-mono text-muted-foreground uppercase tracking-widest">
          INITIALIZING INTERACTIVE QUIZ ENGINE...
        </p>
      </div>
    );
  }

  if (error || !startInfo) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[70vh] gap-4 text-center">
        <AlertCircle className="w-12 h-12 text-red-500" />
        <p className="text-sm font-mono text-red-400">{error || "Quiz not found."}</p>
        <Link
          href={`/roadmap/${topicId}`}
          className="px-5 py-2.5 rounded-xl bg-primary text-white font-bold text-xs uppercase tracking-wider hover:bg-primary/90 transition-all"
        >
          Return to Topic Page
        </Link>
      </div>
    );
  }

  const currentQ = questions[currentIdx];
  const formattedTime = `${Math.floor(timer / 60)}:${(timer % 60).toString().padStart(2, "0")}`;

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-20 relative">
      {/* Toast Notification */}
      <AnimatePresence>
        {toastMsg && (
          <motion.div
            className="fixed bottom-6 right-6 border border-primary/30 px-6 py-4 rounded-2xl bg-[#0a0a0f] text-white text-xs font-bold uppercase tracking-wider flex items-center gap-2.5 z-50 shadow-2xl shadow-primary/20"
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
          >
            <Sparkles className="w-4 h-4 text-xp-gold" />
            <span>{toastMsg}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Top Header Navigation */}
      <div className="flex items-center justify-between">
        <Link
          href={`/roadmap/${topicId}`}
          className="inline-flex items-center gap-2 text-xs font-mono font-bold text-muted-foreground hover:text-white uppercase tracking-wider transition-colors duration-200"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Topic
        </Link>

        {quizState === "QUESTIONS" && (
          <div className="flex items-center gap-4">
            <span className="text-xs font-mono font-bold text-xp-gold flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-xp-gold/10 border border-xp-gold/20">
              <Clock className="w-4 h-4" /> {formattedTime}
            </span>
            <button
              onClick={() => setQuizState("START")}
              className="text-xs font-mono text-muted-foreground hover:text-red-400 font-bold uppercase tracking-wider transition-colors cursor-pointer"
            >
              Quit Battle
            </button>
          </div>
        )}
      </div>

      {/* ========================================================================= */}
      {/* PHASE 1: START SCREEN */}
      {/* ========================================================================= */}
      {quizState === "START" && (
        <motion.div
          className="border border-card-border rounded-3xl p-8 lg:p-12 glass-card space-y-8 relative overflow-hidden"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary/30 bg-primary/10 text-primary text-xs font-mono font-bold uppercase">
              <Trophy className="w-3.5 h-3.5" /> Concept Quiz Engine
            </div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">{startInfo.title}</h1>
            <p className="text-sm text-muted-foreground leading-relaxed max-w-2xl">
              {startInfo.description || "Master core principles, boost your accuracy, and earn bonus XP rewards."}
            </p>
          </div>

          {/* Quiz Metadata Stats Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-2">
            <div className="p-4 rounded-2xl border border-card-border/60 bg-[#030303]/40 space-y-1">
              <span className="text-[10px] font-mono text-muted-foreground uppercase font-bold">Estimated Time</span>
              <p className="text-sm font-extrabold text-white font-mono flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-info-cyan" /> {startInfo.estimated_time} Mins
              </p>
            </div>

            <div className="p-4 rounded-2xl border border-card-border/60 bg-[#030303]/40 space-y-1">
              <span className="text-[10px] font-mono text-muted-foreground uppercase font-bold">Questions</span>
              <p className="text-sm font-extrabold text-white font-mono flex items-center gap-1">
                <BookOpen className="w-3.5 h-3.5 text-primary" /> {startInfo.question_count}
              </p>
            </div>

            <div className="p-4 rounded-2xl border border-card-border/60 bg-[#030303]/40 space-y-1">
              <span className="text-[10px] font-mono text-muted-foreground uppercase font-bold">Difficulty</span>
              <p className="text-sm font-extrabold text-xp-gold font-mono">{startInfo.difficulty}</p>
            </div>

            <div className="p-4 rounded-2xl border border-card-border/60 bg-[#030303]/40 space-y-1">
              <span className="text-[10px] font-mono text-muted-foreground uppercase font-bold">XP Reward</span>
              <p className="text-sm font-extrabold text-xp-gold font-mono flex items-center gap-1">
                <Zap className="w-3.5 h-3.5 fill-xp-gold" /> +{startInfo.xp_reward} XP
              </p>
            </div>

            <div className="p-4 rounded-2xl border border-card-border/60 bg-[#030303]/40 space-y-1 col-span-2 sm:col-span-1">
              <span className="text-[10px] font-mono text-muted-foreground uppercase font-bold">Pass Requirement</span>
              <p className="text-sm font-extrabold text-success-emerald font-mono flex items-center gap-1">
                <Target className="w-3.5 h-3.5 text-success-emerald" /> {startInfo.pass_mark}% Score
              </p>
            </div>
          </div>

          {/* Previous Attempts Section */}
          {startInfo.previous_attempts && startInfo.previous_attempts.length > 0 && (
            <div className="space-y-4 pt-4 border-t border-card-border/50">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-mono font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                  <BarChart2 className="w-4 h-4 text-primary" /> Attempt History ({startInfo.attempt_count})
                </h3>
                {startInfo.best_score !== null && (
                  <span className="text-xs font-mono font-bold text-success-emerald bg-success-emerald/10 border border-success-emerald/20 px-2.5 py-1 rounded">
                    Best Score: {startInfo.best_score}%
                  </span>
                )}
              </div>

              <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
                {startInfo.previous_attempts.map((att) => (
                  <div
                    key={att.id}
                    className="p-3 rounded-xl border border-card-border/50 bg-[#030303]/40 flex items-center justify-between text-xs"
                  >
                    <span className="font-mono text-muted-foreground font-bold">Attempt #{att.attempt_number}</span>
                    <span
                      className={`font-extrabold font-mono ${
                        att.score >= startInfo.pass_mark ? "text-success-emerald" : "text-red-400"
                      }`}
                    >
                      {att.score}% Score
                    </span>
                    <span className="font-mono text-muted-foreground">
                      {Math.floor(att.time_taken / 60)}m {att.time_taken % 60}s
                    </span>
                    <span className="font-mono text-xp-gold font-bold">+{att.xp_earned} XP</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="pt-4 flex flex-col sm:flex-row gap-4">
            <button
              onClick={startQuiz}
              className="flex-1 py-4 rounded-2xl bg-gradient-to-r from-primary to-xp-gold hover:opacity-95 text-white font-extrabold text-xs uppercase tracking-wider flex items-center justify-center gap-2.5 transition-all shadow-xl shadow-primary/20 cursor-pointer"
            >
              <Zap className="w-4 h-4 fill-white" /> Start Quiz Battle
            </button>
          </div>
        </motion.div>
      )}

      {/* ========================================================================= */}
      {/* PHASE 2: QUESTION SCREEN */}
      {/* ========================================================================= */}
      {quizState === "QUESTIONS" && currentQ && (
        <div className="space-y-6">
          {/* Progress & Header */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-mono font-bold text-muted-foreground uppercase">
                Question {currentIdx + 1} of {questions.length}
              </span>
              <div className="flex items-center gap-2 font-mono text-[10px]">
                {currentQ.concept && (
                  <span className="px-2 py-0.5 rounded bg-primary/10 border border-primary/20 text-primary font-bold">
                    {currentQ.concept}
                  </span>
                )}
                <span className="px-2 py-0.5 rounded bg-card-border text-muted-foreground font-bold">
                  {currentQ.type}
                </span>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full h-1.5 bg-zinc-950 rounded-full overflow-hidden border border-card-border/40">
              <motion.div
                className="h-full bg-gradient-to-r from-primary to-xp-gold"
                initial={{ width: "0%" }}
                animate={{ width: `${((currentIdx + 1) / questions.length) * 100}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </div>

          {/* Floating Question Card */}
          <motion.div
            key={currentQ.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="border border-card-border rounded-3xl p-6 lg:p-8 glass-card space-y-6 relative"
          >
            {/* Question Text */}
            <div className="space-y-3">
              <h2 className="text-lg lg:text-xl font-bold text-white leading-relaxed">
                {currentQ.question}
              </h2>
              {currentQ.type === "MULTIPLE_SELECT" && (
                <p className="text-xs font-mono text-primary font-semibold">
                  (Select all options that apply)
                </p>
              )}
            </div>

            {/* Options List */}
            <div className="grid grid-cols-1 gap-3 pt-2">
              {currentQ.options.map((optText, optIdx) => {
                const qIdStr = currentQ.id.toString();
                const isSelected = (answers[qIdStr] || []).includes(optIdx);

                return (
                  <button
                    key={optIdx}
                    onClick={() => toggleOption(currentQ, optIdx)}
                    className={`w-full text-left p-4 rounded-2xl border text-xs lg:text-sm font-medium transition-all duration-200 cursor-pointer flex items-center justify-between group ${
                      isSelected
                        ? "bg-primary/15 border-primary text-white font-semibold shadow-lg shadow-primary/10"
                        : "bg-[#030303]/40 border-card-border/60 hover:border-card-border hover:bg-white/[0.02] text-muted-foreground hover:text-white"
                    }`}
                  >
                    <div className="flex items-center gap-3.5">
                      <span
                        className={`w-6 h-6 rounded-lg border text-xs font-mono font-bold flex items-center justify-center shrink-0 transition-colors ${
                          isSelected
                            ? "bg-primary border-primary text-white"
                            : "border-card-border text-muted-foreground group-hover:border-zinc-600"
                        }`}
                      >
                        {String.fromCharCode(65 + optIdx)}
                      </span>
                      <span>{optText}</span>
                    </div>

                    <div
                      className={`w-5 h-5 rounded-full border flex items-center justify-center shrink-0 ${
                        isSelected ? "border-primary bg-primary text-white" : "border-zinc-800"
                      }`}
                    >
                      {isSelected && <Check className="w-3 h-3 stroke-[3]" />}
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Hint Box (if available) */}
            {currentQ.hints && currentQ.hints.length > 0 && (
              <div className="pt-2">
                {!showHint ? (
                  <button
                    onClick={() => setShowHint(true)}
                    className="text-xs font-mono text-info-cyan hover:underline flex items-center gap-1.5 cursor-pointer"
                  >
                    <HelpCircle className="w-3.5 h-3.5" /> Need a hint?
                  </button>
                ) : (
                  <div className="p-3 rounded-xl border border-info-cyan/30 bg-info-cyan/10 text-xs text-info-cyan space-y-1 font-mono">
                    <span className="font-bold uppercase tracking-wider block">💡 Hint:</span>
                    <p>{currentQ.hints[0]}</p>
                  </div>
                )}
              </div>
            )}

            {/* Action Toolbar */}
            <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-card-border/60">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => toggleFlag(currentQ.id)}
                  className={`p-2.5 rounded-xl border text-xs font-mono flex items-center gap-1.5 transition-all cursor-pointer ${
                    flagged.has(currentQ.id)
                      ? "bg-red-500/10 border-red-500/30 text-red-400 font-bold"
                      : "border-card-border text-muted-foreground hover:text-white"
                  }`}
                >
                  <Flag className="w-4 h-4" />
                  <span className="hidden sm:inline">Flag</span>
                </button>

                <button
                  onClick={() => toggleBookmark(currentQ.id)}
                  className={`p-2.5 rounded-xl border text-xs font-mono flex items-center gap-1.5 transition-all cursor-pointer ${
                    bookmarked.has(currentQ.id)
                      ? "bg-xp-gold/10 border-xp-gold/30 text-xp-gold font-bold"
                      : "border-card-border text-muted-foreground hover:text-white"
                  }`}
                >
                  {bookmarked.has(currentQ.id) ? (
                    <BookmarkCheck className="w-4 h-4 text-xp-gold" />
                  ) : (
                    <Bookmark className="w-4 h-4" />
                  )}
                  <span className="hidden sm:inline">Bookmark</span>
                </button>

                <button
                  onClick={handleSkip}
                  className="px-3.5 py-2.5 rounded-xl border border-card-border hover:bg-white/[0.02] text-xs font-mono text-muted-foreground hover:text-white font-bold transition-all cursor-pointer"
                >
                  Skip
                </button>
              </div>

              <div className="flex items-center gap-3">
                <button
                  disabled={currentIdx === 0}
                  onClick={() => setCurrentIdx((prev) => prev - 1)}
                  className="px-4 py-2.5 rounded-xl border border-card-border hover:bg-white/[0.02] text-white font-bold text-xs uppercase tracking-wider disabled:opacity-30 cursor-pointer flex items-center gap-1"
                >
                  <ChevronLeft className="w-4 h-4" /> Prev
                </button>

                {currentIdx < questions.length - 1 ? (
                  <button
                    onClick={() => setCurrentIdx((prev) => prev + 1)}
                    className="px-6 py-2.5 rounded-xl bg-primary hover:bg-primary/90 text-white font-bold text-xs uppercase tracking-wider cursor-pointer flex items-center gap-1 shadow-lg shadow-primary/10"
                  >
                    Next <ChevronRight className="w-4 h-4" />
                  </button>
                ) : (
                  <button
                    disabled={submitting}
                    onClick={handleSubmit}
                    className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-primary to-xp-gold hover:opacity-95 text-white font-bold text-xs uppercase tracking-wider flex items-center gap-1.5 cursor-pointer shadow-lg shadow-primary/20"
                  >
                    {submitting ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" /> Submitting...
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="w-4 h-4" /> Submit Battle
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* PHASE 3: RESULTS SCREEN */}
      {/* ========================================================================= */}
      {quizState === "RESULTS" && result && (
        <motion.div
          className="border border-card-border rounded-3xl p-6 lg:p-10 glass-card space-y-8 relative overflow-hidden"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          {/* Result Header Banner */}
          <div className="flex flex-col sm:flex-row items-center gap-6 p-6 border border-card-border/60 bg-[#030303]/60 rounded-3xl">
            {/* Animated Score Circle */}
            <div className="relative w-28 h-28 flex items-center justify-center shrink-0">
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="56" cy="56" r="48" className="stroke-zinc-900 fill-none" strokeWidth="8" />
                <circle
                  cx="56"
                  cy="56"
                  r="48"
                  className={result.passed ? "stroke-success-emerald fill-none" : "stroke-red-500 fill-none"}
                  strokeWidth="8"
                  strokeDasharray="301.5"
                  strokeDashoffset={301.5 - (301.5 * result.score) / 100}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute text-center">
                <span className="text-xl font-extrabold text-white font-mono block">{result.score}%</span>
                <span className="text-[9px] font-mono text-muted-foreground uppercase font-bold">Score</span>
              </div>
            </div>

            {/* Banner Text */}
            <div className="text-center sm:text-left space-y-2 flex-1">
              <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2">
                <h2 className="text-xl font-extrabold text-white">
                  {result.passed ? "Victory! Quiz Conquered" : "Defeat! Try Again"}
                </h2>
                <span
                  className={`text-[10px] font-mono font-bold uppercase px-2.5 py-0.5 rounded border ${
                    result.passed
                      ? "text-success-emerald bg-success-emerald/10 border-success-emerald/20"
                      : "text-red-400 bg-red-400/10 border-red-400/20"
                  }`}
                >
                  {result.passed ? "PASSED" : "FAILED"}
                </span>
              </div>

              <p className="text-xs text-muted-foreground">
                Time Taken: {Math.floor(result.time_taken / 60)}m {result.time_taken % 60}s | Attempt #{result.attempt_number}
              </p>

              <div className="flex items-center justify-center sm:justify-start gap-2 text-xs font-bold text-xp-gold">
                <Zap className="w-4 h-4 fill-xp-gold" /> Total XP Earned: +{result.xp_earned} XP
              </div>
            </div>
          </div>

          {/* Performance Summary Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-4 rounded-2xl border border-success-emerald/20 bg-success-emerald/5 space-y-1">
              <span className="text-[10px] font-mono text-success-emerald uppercase font-bold">Correct</span>
              <p className="text-base font-extrabold text-success-emerald font-mono">{result.correct_count}</p>
            </div>

            <div className="p-4 rounded-2xl border border-red-500/20 bg-red-500/5 space-y-1">
              <span className="text-[10px] font-mono text-red-400 uppercase font-bold">Incorrect</span>
              <p className="text-base font-extrabold text-red-400 font-mono">{result.incorrect_count}</p>
            </div>

            <div className="p-4 rounded-2xl border border-card-border/60 bg-[#030303]/40 space-y-1">
              <span className="text-[10px] font-mono text-muted-foreground uppercase font-bold">Skipped</span>
              <p className="text-base font-extrabold text-muted-foreground font-mono">{result.skipped_count}</p>
            </div>

            <div className="p-4 rounded-2xl border border-xp-gold/20 bg-xp-gold/5 space-y-1">
              <span className="text-[10px] font-mono text-xp-gold uppercase font-bold">Bonus XP</span>
              <p className="text-base font-extrabold text-xp-gold font-mono">+{result.bonus_xp} XP</p>
            </div>
          </div>

          {/* XP Breakdown Card */}
          <div className="p-5 rounded-2xl border border-card-border/60 bg-[#030303]/40 space-y-3">
            <h3 className="text-xs font-mono font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-xp-gold" /> XP & Bonus Breakdown
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
              <div className="flex justify-between p-2.5 rounded-xl border border-card-border/40 bg-[#07070a]">
                <span className="text-muted-foreground">Base Completion:</span>
                <span className="font-mono text-white font-bold">+50 XP</span>
              </div>
              <div className="flex justify-between p-2.5 rounded-xl border border-card-border/40 bg-[#07070a]">
                <span className="text-muted-foreground">Correct Answers:</span>
                <span className="font-mono text-white font-bold">+{result.correct_count * 5} XP</span>
              </div>
              {result.perfect_bonus && (
                <div className="flex justify-between p-2.5 rounded-xl border border-xp-gold/30 bg-xp-gold/10">
                  <span className="text-xp-gold font-bold">Perfect Score:</span>
                  <span className="font-mono text-xp-gold font-extrabold">+100 XP</span>
                </div>
              )}
              {result.speed_bonus && (
                <div className="flex justify-between p-2.5 rounded-xl border border-info-cyan/30 bg-info-cyan/10">
                  <span className="text-info-cyan font-bold">Speedrun Bonus:</span>
                  <span className="font-mono text-info-cyan font-extrabold">+50 XP</span>
                </div>
              )}
              {result.first_attempt_bonus && (
                <div className="flex justify-between p-2.5 rounded-xl border border-primary/30 bg-primary/10">
                  <span className="text-primary font-bold">First Try Bonus:</span>
                  <span className="font-mono text-primary font-extrabold">+75 XP</span>
                </div>
              )}
            </div>
          </div>

          {/* Question Explanations Accordion */}
          <div className="space-y-4">
            <h3 className="text-sm font-mono font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-primary" /> Detailed Explanations
            </h3>

            <div className="space-y-3">
              {result.questions_review.map((qRev, idx) => (
                <div
                  key={qRev.id}
                  className={`p-5 rounded-2xl border space-y-3 ${
                    qRev.is_correct
                      ? "border-success-emerald/30 bg-success-emerald/5"
                      : qRev.is_skipped
                      ? "border-card-border bg-[#030303]/40"
                      : "border-red-500/30 bg-red-500/5"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="space-y-1">
                      <span className="text-[10px] font-mono font-bold uppercase text-muted-foreground">
                        Question {idx + 1} • {qRev.concept || "Concept"}
                      </span>
                      <h4 className="text-sm font-bold text-white">{qRev.question}</h4>
                    </div>

                    <span
                      className={`text-[10px] font-mono font-bold uppercase px-2.5 py-1 rounded shrink-0 border ${
                        qRev.is_correct
                          ? "text-success-emerald bg-success-emerald/10 border-success-emerald/30"
                          : qRev.is_skipped
                          ? "text-muted-foreground bg-muted border-card-border"
                          : "text-red-400 bg-red-400/10 border-red-400/30"
                      }`}
                    >
                      {qRev.is_correct ? "CORRECT" : qRev.is_skipped ? "SKIPPED" : "INCORRECT"}
                    </span>
                  </div>

                  {/* Explanation text */}
                  {qRev.explanation && (
                    <div className="p-3 rounded-xl border border-card-border/50 bg-[#030303]/60 text-xs text-muted-foreground space-y-1 font-mono">
                      <span className="text-white font-bold block uppercase tracking-wider text-[10px]">
                        Explanation:
                      </span>
                      <p>{qRev.explanation}</p>
                    </div>
                  )}

                  {/* Why other options are wrong */}
                  {qRev.option_explanations && qRev.option_explanations.length > 0 && (
                    <div className="space-y-1.5 pt-1">
                      <span className="text-[10px] font-mono font-bold text-muted-foreground uppercase tracking-wider block">
                        Option Analysis:
                      </span>
                      <div className="space-y-1 text-xs font-mono">
                        {qRev.options.map((opt, oIdx) => {
                          const exp = qRev.option_explanations?.[oIdx];
                          const isCorrectOpt = qRev.correct_answer.includes(oIdx);
                          if (!exp) return null;

                          return (
                            <div
                              key={oIdx}
                              className={`p-2.5 rounded-lg border text-[11px] ${
                                isCorrectOpt
                                  ? "border-success-emerald/20 bg-success-emerald/10 text-success-emerald font-semibold"
                                  : "border-card-border/30 bg-[#07070a] text-muted-foreground"
                              }`}
                            >
                              <span className="font-bold mr-1">Option {String.fromCharCode(65 + oIdx)}:</span>
                              {exp}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Action Footer */}
          <div className="flex flex-col sm:flex-row gap-4 pt-4 border-t border-card-border/60">
            <button
              onClick={startQuiz}
              className="flex-1 py-3.5 rounded-xl bg-primary hover:bg-primary/90 text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 cursor-pointer transition-all"
            >
              <RotateCcw className="w-4 h-4" /> Retry Quiz Battle
            </button>

            <Link
              href={`/roadmap/${topicId}`}
              className="flex-1 py-3.5 rounded-xl border border-card-border hover:bg-white/[0.02] text-white font-bold text-xs uppercase tracking-wider text-center cursor-pointer transition-all"
            >
              Back to Topic Page
            </Link>
          </div>
        </motion.div>
      )}
    </div>
  );
}
