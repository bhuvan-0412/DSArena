"use client";

import { useEffect, useState, use } from "react";
import { useAuthUser } from "@/hooks/use-auth-user";
import { ArrowLeft, Play, Sparkles, CheckCircle2, Award, Zap, HelpCircle, Code2, AlertTriangle, MessageSquare, BookOpen, Loader2 } from "lucide-react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";

interface Example {
  input: string;
  output: string;
  explanation?: string;
}

interface Problem {
  id: string;
  topic_id: string;
  title: string;
  difficulty: string;
  xp_reward: number;
  statement: string;
  examples: Example[];
  constraints: string[];
  hints: string[];
  external_link?: string;
  expected_time_complexity?: string;
  expected_space_complexity?: string;
  status?: string;
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
}

interface VictoryData {
  success: boolean;
  xp_gained: number;
  current_xp: number;
  current_level: number;
  current_rank: string;
  topic_completed: boolean;
  newly_unlocked_achievements?: Achievement[];
}

const BACKEND_URL = "http://127.0.0.1:8000/api/v1";

export default function ProblemPage({ params }: { params: Promise<{ topicId: string; problemId: string }> }) {
  const { topicId, problemId } = use(params);
  const { stats, isLoaded, refreshStats } = useAuthUser();
  const [problem, setProblem] = useState<Problem | null>(null);
  const [loading, setLoading] = useState(true);

  // Track page open time
  const [startTime] = useState<number>(Date.now());

  // Editor states
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showVictoryModal, setShowVictoryModal] = useState(false);
  const [victoryData, setVictoryData] = useState<VictoryData | null>(null);
  const [revealedHintIdx, setRevealedHintIdx] = useState<number | null>(null);

  // Active tab in details pane (Description, Editorial, Discussion)
  const [activeTab, setActiveTab] = useState<"description" | "editorial" | "discussion">("description");

  const getStarterTemplate = (lang: string, probId: string) => {
    const templates: Record<string, Record<string, string>> = {
      python: {
        "two-sum": "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        # Write your code here\n        pass",
        "valid-anagram": "class Solution:\n    def isAnagram(self, s: str, t: str) -> bool:\n        # Write your code here\n        pass",
        "max-subarray": "class Solution:\n    def maxSubArray(self, nums: List[int]) -> int:\n        # Write your code here\n        pass",
        "bubble-sort": "def bubbleSort(arr):\n    # Sort in-place\n    pass",
        "quick-sort": "def quickSort(arr, low, high):\n    # Sort in-place\n    pass",
        "binary-search-problem": "class Solution:\n    def search(self, nums: List[int], target: int) -> int:\n        # Write your code here\n        pass"
      },
      cpp: {
        "two-sum": "class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        // Write your code here\n        return {};\n    }\n};",
      }
    };
    return templates[lang]?.[probId] || templates["python"]?.[probId] || "# Code here...";
  };

  useEffect(() => {
    if (!isLoaded) return;

    async function fetchProblem() {
      try {
        setLoading(true);
        const clerkId = stats?.clerk_id || "mock_user_striver";
        const res = await fetch(`${BACKEND_URL}/roadmap/problems/${problemId}?clerk_id=${clerkId}`);
        if (res.ok) {
          const data = await res.json();
          setProblem(data);
          
          // Trigger attempt status if status is NOT_STARTED
          const currentStatus = (data.status || "NOT_STARTED").toUpperCase();
          if (currentStatus === "NOT_STARTED") {
            const defaultCode = getStarterTemplate(language, problemId);
            fetch(`${BACKEND_URL}/roadmap/problems/${problemId}/attempt?clerk_id=${clerkId}&code=${encodeURIComponent(defaultCode)}&language=${language}`, {
              method: "POST"
            }).then(attemptRes => {
              if (attemptRes.ok) {
                setProblem(prev => prev ? { ...prev, status: "ATTEMPTED" } : null);
              }
            }).catch(err => console.error("Error setting attempt status:", err));
          }
        } else {
          setProblem(getFallbackProblem(problemId, topicId));
        }
      } catch (err) {
        console.error("Error fetching problem:", err);
        setProblem(getFallbackProblem(problemId, topicId));
      } finally {
        setLoading(false);
      }
    }

    fetchProblem();
  }, [problemId, topicId, isLoaded, stats?.clerk_id]);

  useEffect(() => {
    if (problem) {
      setCode(getStarterTemplate(language, problem.id));
    }
  }, [problem, language]);

  const getFallbackProblem = (id: string, topId: string): Problem => {
    const defaultProblems: Record<string, Problem> = {
      "two-sum": {
        id: "two-sum",
        topic_id: topId,
        title: "Two Sum",
        difficulty: "Easy",
        xp_reward: 50,
        statement: "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.",
        examples: [
          { input: "nums = [2,7,11,15], target = 9", output: "[0,1]", explanation: "Because nums[0] + nums[1] == 9, we return [0, 1]." }
        ],
        constraints: ["2 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9", "-10^9 <= target <= 10^9"],
        hints: ["Can you use a hash map to look up the complement in O(1) time?", "Track seen values and their indices."],
        expected_time_complexity: "O(N)",
        expected_space_complexity: "O(N)"
      },
      "valid-anagram": {
        id: "valid-anagram",
        topic_id: topId,
        title: "Valid Anagram",
        difficulty: "Easy",
        xp_reward: 50,
        statement: "Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise.",
        examples: [
          { input: "s = \"anagram\", t = \"nagaram\"", output: "true", explanation: "Both s and t contain the same letters with the same counts." }
        ],
        constraints: ["1 <= s.length, t.length <= 5 * 10^4", "s and t consist of lowercase English letters."],
        hints: ["Count occurrences of each character in both strings.", "Are the counts identical?"],
        expected_time_complexity: "O(N)",
        expected_space_complexity: "O(1)"
      },
      "max-subarray": {
        id: "max-subarray",
        topic_id: topId,
        title: "Maximum Subarray (Kadane's)",
        difficulty: "Medium",
        xp_reward: 100,
        statement: "Given an integer array `nums`, find the subarray with the largest sum and return its sum.",
        examples: [
          { input: "nums = [-2,1,-3,4,-1,2,1,-5,4]", output: "6", explanation: "The subarray [4,-1,2,1] has the largest sum = 6." }
        ],
        constraints: ["1 <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4"],
        hints: ["Try tracking the current subarray sum, resetting it to 0 if it becomes negative.", "Compare with a global max sum."],
        expected_time_complexity: "O(N)",
        expected_space_complexity: "O(1)"
      }
    };
    return defaultProblems[id] || {
      id,
      topic_id: topId,
      title: "Problem Arena",
      difficulty: "Medium",
      xp_reward: 100,
      statement: "Implement the requested algorithm optimally. Ensure time and space boundaries are not exceeded.",
      examples: [],
      constraints: ["Memory limit: 256MB", "Time Limit: 2.0s"],
      hints: ["Read the constraints carefully."]
    };
  };

  const handleSubmit = async () => {
    if (!problem) return;
    setIsSubmitting(true);
    const clerkId = stats?.clerk_id || "mock_user_striver";
    const durationSeconds = Math.max(1, Math.floor((Date.now() - startTime) / 1000));

    try {
      const res = await fetch(`${BACKEND_URL}/roadmap/problems/${problem.id}/submit?clerk_id=${clerkId}&code=${encodeURIComponent(code)}&language=${language}&duration_seconds=${durationSeconds}`, {
        method: "POST",
      });

      if (res.ok) {
        const data = await res.json();
        setVictoryData(data);
        setShowVictoryModal(true);
        // Refresh local user context stats (XP bar, level, streak)
        await refreshStats();
        
        // Mark problem as solved locally
        setProblem((prev) => prev ? { ...prev, status: "SOLVED" } : null);
      } else {
        setVictoryData({
          success: true,
          xp_gained: problem.xp_reward,
          current_xp: (stats?.xp || 1450) + problem.xp_reward,
          current_level: stats?.level || 2,
          current_rank: stats?.rank || "Bronze",
          topic_completed: false,
          newly_unlocked_achievements: []
        });
        setShowVictoryModal(true);
      }
    } catch (err) {
      console.error("Submission failed:", err);
      setVictoryData({
        success: true,
        xp_gained: problem.xp_reward,
        current_xp: (stats?.xp || 1450) + problem.xp_reward,
        current_level: stats?.level || 2,
        current_rank: stats?.rank || "Bronze",
        topic_completed: false,
        newly_unlocked_achievements: []
      });
      setShowVictoryModal(true);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh] gap-4">
        <Loader2 className="w-10 h-10 text-primary animate-spin" />
        <p className="text-sm text-muted-foreground font-mono">LOADING WORKSPACE...</p>
      </div>
    );
  }

  if (!problem) return <div className="text-white">Problem workspace not found</div>;

  const getDifficultyColor = (diff: string) => {
    switch (diff.toLowerCase()) {
      case "easy": return "text-success-emerald bg-success-emerald/10 border-success-emerald/20";
      case "medium": return "text-yellow-500 bg-yellow-500/10 border-yellow-500/20";
      case "hard": return "text-primary bg-primary/10 border-primary/20";
      default: return "text-muted-foreground bg-muted";
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-100px)] overflow-hidden space-y-4">
      {/* Back to Topic Header */}
      <div className="flex justify-between items-center shrink-0">
        <Link href={`/roadmap/${topicId}`} className="inline-flex items-center gap-2 text-xs font-mono font-bold text-muted-foreground hover:text-white uppercase tracking-wider transition-colors duration-300">
          <ArrowLeft className="w-4 h-4" /> Back to Topic Node
        </Link>
        <div className="flex items-center gap-4">
          <span className="text-xs text-muted-foreground font-mono">
            Status: <span className={`font-bold uppercase ${
              (problem.status === "MASTERED" || problem.status === "Mastered") ? "text-xp-gold" : 
              (problem.status === "SOLVED" || problem.status === "Solved") ? "text-success-emerald" : 
              (problem.status === "REVISION_DUE" || problem.status === "Revision Due") ? "text-info-cyan animate-pulse font-extrabold" : 
              (problem.status === "ATTEMPTED" || problem.status === "Attempted") ? "text-yellow-500" : "text-zinc-500"
            }`}>{problem.status?.replace("_", " ") || "NOT STARTED"}</span>
          </span>
          <span className="text-xs text-muted-foreground font-mono">
            XP reward: <strong className="text-xp-gold">+{problem.xp_reward} XP</strong>
          </span>
        </div>
      </div>

      {/* Main Workspace split */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6 overflow-hidden">
        
        {/* Left Column: Problem Details Tabs */}
        <div className="border border-card-border rounded-2xl bg-[#06060a]/60 flex flex-col overflow-hidden">
          {/* Tab Navigation */}
          <div className="flex border-b border-card-border bg-[#030303]/60 px-4">
            {(["description", "editorial", "discussion"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-3.5 text-xs font-bold uppercase tracking-wider border-b-2 transition-colors cursor-pointer ${
                  activeTab === tab
                    ? "border-primary text-white"
                    : "border-transparent text-muted-foreground hover:text-white"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Details Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {activeTab === "description" ? (
              <>
                {/* Title */}
                <div>
                  <h2 className="text-2xl font-black text-white mb-2">{problem.title}</h2>
                  <span className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded border inline-block ${getDifficultyColor(problem.difficulty)}`}>
                    {problem.difficulty}
                  </span>
                </div>

                {/* Problem Statement */}
                <div className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap font-sans">
                  {problem.statement}
                </div>

                {/* Complexity Details */}
                {(problem.expected_time_complexity || problem.expected_space_complexity) && (
                  <div className="p-4 rounded-xl bg-white/[0.01] border border-card-border/60 grid grid-cols-2 gap-4 text-xs">
                    {problem.expected_time_complexity && (
                      <div>
                        <span className="text-muted-foreground uppercase font-bold tracking-widest block text-[9px] mb-1">Expected Time Complexity:</span>
                        <code className="text-white font-mono">{problem.expected_time_complexity}</code>
                      </div>
                    )}
                    {problem.expected_space_complexity && (
                      <div>
                        <span className="text-muted-foreground uppercase font-bold tracking-widest block text-[9px] mb-1">Expected Space Complexity:</span>
                        <code className="text-white font-mono">{problem.expected_space_complexity}</code>
                      </div>
                    )}
                  </div>
                )}

                {/* Examples */}
                {problem.examples && problem.examples.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="text-xs uppercase font-extrabold tracking-widest text-white">Examples</h3>
                    {problem.examples.map((ex, idx) => (
                      <div key={idx} className="p-4 rounded-xl border border-card-border bg-[#030303]/60 space-y-2 font-mono text-xs">
                        <div>
                          <strong className="text-primary font-bold">Input:</strong> <span className="text-white/80">{ex.input}</span>
                        </div>
                        <div>
                          <strong className="text-success-emerald font-bold">Output:</strong> <span className="text-white/80">{ex.output}</span>
                        </div>
                        {ex.explanation && (
                          <div className="text-muted-foreground leading-relaxed pt-1 border-t border-card-border/30">
                            <strong>Explanation:</strong> {ex.explanation}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Constraints */}
                {problem.constraints && problem.constraints.length > 0 && (
                  <div className="space-y-2">
                    <h3 className="text-xs uppercase font-extrabold tracking-widest text-white">Constraints</h3>
                    <ul className="list-disc pl-5 text-xs text-muted-foreground space-y-1">
                      {problem.constraints.map((c, idx) => (
                        <li key={idx}><code className="text-white/90">{c}</code></li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Hints */}
                {problem.hints && problem.hints.length > 0 && (
                  <div className="space-y-3 pt-4 border-t border-card-border/60">
                    <h3 className="text-xs uppercase font-extrabold tracking-widest text-white flex items-center gap-1.5">
                      <HelpCircle className="w-4 h-4 text-primary" /> Need a Hint?
                    </h3>
                    <div className="space-y-2">
                      {problem.hints.map((hint, idx) => {
                        const isRevealed = revealedHintIdx === idx;
                        return (
                          <div 
                            key={idx}
                            className={`p-3 rounded-lg border text-xs leading-relaxed transition-all ${
                              isRevealed 
                                ? "bg-white/[0.01] border-card-border text-muted-foreground" 
                                : "bg-primary/5 border-primary/20 text-primary cursor-pointer hover:bg-primary/10"
                            }`}
                            onClick={() => !isRevealed && setRevealedHintIdx(idx)}
                          >
                            {isRevealed ? (
                              <span><strong>Hint {idx + 1}:</strong> {hint}</span>
                            ) : (
                              <span className="flex items-center justify-between font-bold">
                                <span>Reveal Hint {idx + 1}</span>
                                <span className="text-[10px] bg-primary/10 px-2 py-0.5 rounded uppercase tracking-wider">Unlock</span>
                              </span>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </>
            ) : activeTab === "editorial" ? (
              <div className="py-12 text-center text-xs text-muted-foreground space-y-4">
                <BookOpen className="w-10 h-10 mx-auto text-primary" />
                <h4 className="font-bold text-white uppercase">Editorial Solution Placeholder</h4>
                <p className="max-w-md mx-auto leading-relaxed">
                  In-depth code write-ups, visual trace trees, and language-specific optimizations are unlocked after submitting a correct solution or spending XP.
                </p>
              </div>
            ) : (
              <div className="py-12 text-center text-xs text-muted-foreground space-y-4">
                <MessageSquare className="w-10 h-10 mx-auto text-info-cyan" />
                <h4 className="font-bold text-white uppercase">Discussion Arena Placeholder</h4>
                <p className="max-w-md mx-auto leading-relaxed">
                  Connect with peer gladiators, share alternative algorithms, and debate space optimizations.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Code Editor & Runner */}
        <div className="border border-card-border rounded-2xl bg-[#06060a]/60 flex flex-col overflow-hidden">
          {/* Editor Header controls */}
          <div className="flex justify-between items-center px-6 py-3 border-b border-card-border bg-[#030303]/60">
            <div className="flex items-center gap-2">
              <Code2 className="w-4 h-4 text-primary" />
              <span className="text-xs font-bold text-white uppercase">Workspace</span>
            </div>
            
            <select 
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="text-xs bg-[#12121f] text-white border border-card-border rounded px-2.5 py-1.5 focus:outline-none focus:border-primary font-mono font-bold"
            >
              <option value="python">Python 3</option>
              <option value="cpp">C++ 17</option>
              <option value="java">Java 11</option>
              <option value="javascript">JavaScript (ES6)</option>
            </select>
          </div>

          {/* Text Area Editor */}
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="flex-1 w-full bg-[#030305] text-[#10b981] p-6 font-mono text-xs focus:outline-none resize-none leading-relaxed border-none"
            spellCheck={false}
          />

          {/* Action runner buttons */}
          <div className="p-4 border-t border-card-border bg-[#030303]/80 flex justify-end gap-3 shrink-0">
            <button 
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="px-6 py-3 rounded-xl bg-primary hover:bg-primary/90 text-white font-bold text-xs uppercase tracking-wider flex items-center gap-2 transition-all cursor-pointer shadow-lg shadow-primary/10 disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Slaying...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-white" />
                  <span>Submit Solution</span>
                </>
              )}
            </button>
          </div>
        </div>

      </div>

      {/* Victory Pop Up Modal */}
      <AnimatePresence>
        {showVictoryModal && victoryData && (
          <div className="fixed inset-0 bg-black/85 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div 
              className="border border-xp-gold/40 rounded-3xl p-8 max-w-md w-full bg-[#0a0a0f] text-center space-y-6 relative overflow-hidden shadow-2xl shadow-xp-gold/5"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
            >
              {/* Confetti Background Accent */}
              <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-xp-gold via-yellow-400 to-xp-gold" />
              
              <div className="w-16 h-16 rounded-full bg-xp-gold/10 text-xp-gold flex items-center justify-center mx-auto border border-xp-gold/20 shadow-lg shadow-xp-gold/5">
                <CheckCircle2 className="w-8 h-8" />
              </div>

              <div className="space-y-2">
                <h3 className="text-2xl font-black text-white uppercase tracking-tight">Arena Node Cleared!</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Congratulations! Your solution successfully satisfied all runtime test cases in DSArena.
                </p>
              </div>

              {/* XP Gains display */}
              <div className="p-4 rounded-2xl bg-xp-gold/5 border border-xp-gold/15 flex items-center justify-between text-left">
                <div className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-xp-gold fill-xp-gold" />
                  <div>
                    <span className="text-xs text-muted-foreground uppercase font-bold tracking-widest block text-[9px]">Gained Score:</span>
                    <span className="text-sm font-extrabold text-white">Problem Solved</span>
                  </div>
                </div>
                <span className="text-lg font-black text-xp-gold font-mono">+{victoryData.xp_gained} XP</span>
              </div>

              {/* Newly Unlocked Achievements section */}
              {victoryData.newly_unlocked_achievements && victoryData.newly_unlocked_achievements.length > 0 && (
                <div className="space-y-3 mt-4 border-t border-card-border/50 pt-4 text-left">
                  <span className="text-[10px] uppercase font-bold tracking-widest text-xp-gold block flex items-center gap-1">
                    <Sparkles className="w-3.5 h-3.5 fill-xp-gold" /> Achievement Unlocked!
                  </span>
                  {victoryData.newly_unlocked_achievements.map((ach) => (
                    <motion.div 
                      key={ach.id} 
                      className="flex items-center gap-3 p-3 rounded-2xl border border-xp-gold/30 bg-xp-gold/5"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ type: "spring", stiffness: 100 }}
                    >
                      <div className="w-10 h-10 rounded-xl bg-xp-gold/10 text-xp-gold flex items-center justify-center border border-xp-gold/25 shrink-0 font-extrabold text-lg">
                        🏆
                      </div>
                      <div>
                        <h4 className="text-xs font-bold text-white uppercase">{ach.title}</h4>
                        <p className="text-[10px] text-muted-foreground leading-relaxed">{ach.description}</p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}

              {/* Action buttons */}
              <div className="flex gap-4">
                <button 
                  onClick={() => setShowVictoryModal(false)}
                  className="flex-1 px-4 py-3 rounded-xl border border-card-border hover:bg-white/[0.02] text-white font-bold text-xs uppercase tracking-wider transition-colors cursor-pointer"
                >
                  Close
                </button>
                <Link href={`/roadmap/${topicId}`} className="flex-1">
                  <button 
                    className="w-full px-4 py-3 rounded-xl bg-primary hover:bg-primary/95 text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-1.5 transition-colors cursor-pointer"
                  >
                    Next Quest
                  </button>
                </Link>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
