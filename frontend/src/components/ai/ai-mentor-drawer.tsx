"use client";

import React, { useState, useEffect, useRef } from "react";
import { useAuthUser } from "@/hooks/use-auth-user";
import { BACKEND_URL } from "@/lib/api-config";
import { AISettingsModal } from "./ai-settings-modal";
import {
  Bot, Sparkles, Send, Lightbulb, Code2, Calendar, Mic, Settings,
  ChevronRight, RefreshCw, X, Maximize2, Minimize2, Check, Copy, AlertCircle
} from "lucide-react";



interface MessageItem {
  id?: number;
  role: "user" | "assistant" | "system";
  content: string;
  hint_level?: number;
}

interface AIMentorDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  topicId?: string;
  problemId?: string;
  codeSnippet?: string;
  language?: string;
}

export function AIMentorDrawer({
  isOpen,
  onClose,
  topicId,
  problemId,
  codeSnippet,
  language = "python",
}: AIMentorDrawerProps) {
  const { clerkId } = useAuthUser();
  const [activeMode, setActiveMode] = useState<string>("concept_mentor");
  const [hintLevel, setHintLevel] = useState<number>(1);
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const modes = [
    { id: "concept_mentor", label: "Concept Mentor", icon: Lightbulb, color: "text-amber-400 border-amber-500/30 bg-amber-500/10" },
    { id: "hint_system", label: "Hint System", icon: Sparkles, color: "text-purple-400 border-purple-500/30 bg-purple-500/10" },
    { id: "code_reviewer", label: "Code Reviewer", icon: Code2, color: "text-cyan-400 border-cyan-500/30 bg-cyan-500/10" },
    { id: "study_planner", label: "Study Planner", icon: Calendar, color: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10" },
    { id: "interview_mentor", label: "Interview Coach", icon: Mic, color: "text-rose-400 border-rose-500/30 bg-rose-500/10" },
  ];

  // Auto-scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Load active conversation history when drawer opens or mode changes
  useEffect(() => {
    if (isOpen && clerkId) {
      fetchConversations();
    }
  }, [isOpen, clerkId, activeMode, topicId, problemId]);

  const fetchConversations = async () => {
    try {
      let url = `${BACKEND_URL}/ai/conversations?clerk_id=${clerkId}&mode=${activeMode}`;
      if (topicId) url += `&topic_id=${topicId}`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        if (data && data.length > 0) {
          const activeConv = data[0];
          setConversationId(activeConv.id);
          fetchMessages(activeConv.id);
        } else {
          setConversationId(null);
          setMessages([
            {
              role: "assistant",
              content: getWelcomeMessage(activeMode),
            },
          ]);
        }
      }
    } catch (e) {
      console.error("Error fetching conversations:", e);
    }
  };

  const fetchMessages = async (convId: number) => {
    try {
      const res = await fetch(`${BACKEND_URL}/ai/conversations/${convId}/messages?clerk_id=${clerkId}`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data.length > 0 ? data : [{ role: "assistant", content: getWelcomeMessage(activeMode) }]);
      }
    } catch (e) {
      console.error("Error fetching messages:", e);
    }
  };

  const getWelcomeMessage = (mode: string) => {
    switch (mode) {
      case "hint_system":
        return "### 🧩 AI Hint System\nI will guide you step-by-step without spoiling the full code immediately!\nSelect a **Hint Level (1 to 5)** below or ask a specific question.";
      case "code_reviewer":
        return "### 🔍 AI Code Reviewer\nClick **'Review My Submitted Code'** below or paste a snippet to analyze Time/Space complexity, readability, and optimizations.";
      case "study_planner":
        return "### 📅 Adaptive Study Planner\nI analyze your weak topics, due revisions, and daily missions to build your optimal study plan today!";
      case "interview_mentor":
        return "### 🎙️ Technical Interview Mentor\nWelcome candidate! Ready for a mock interview question on your current topic? Let's test your problem-solving process.";
      default:
        return "### ⚔️ DSArena AI Coach\nWelcome! I am your context-aware DSA coach. Ask me any concept questions, visual intuition, or interview tips!";
    }
  };

  const handleSendMessage = async (customMsg?: string, customHintLevel?: number, actionName?: string) => {
    const textToSend = customMsg || inputMessage;
    if (!textToSend.trim() && !actionName) return;

    const userMessageObj: MessageItem = {
      role: "user",
      content: textToSend,
      hint_level: customHintLevel || (activeMode === "hint_system" ? hintLevel : undefined),
    };

    setMessages((prev) => [...prev, userMessageObj]);
    if (!customMsg) setInputMessage("");
    setLoading(true);

    try {
      if (actionName) {
        const res = await fetch(`${BACKEND_URL}/ai/quick-action?clerk_id=${clerkId}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            action: actionName,
            topic_id: topicId,
            problem_id: problemId,
            code_snippet: codeSnippet,
            language: language,
            hint_level: customHintLevel || hintLevel,
          }),
        });
        if (res.ok) {
          const data = await res.json();
          setConversationId(data.conversation_id);
          setMessages((prev) => [...prev, data.assistant_message]);
        }
      } else {
        const res = await fetch(`${BACKEND_URL}/ai/chat?clerk_id=${clerkId}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            conversation_id: conversationId,
            mode: activeMode,
            topic_id: topicId,
            problem_id: problemId,
            user_message: textToSend,
            hint_level: customHintLevel || (activeMode === "hint_system" ? hintLevel : undefined),
            code_snippet: activeMode === "code_reviewer" ? codeSnippet : undefined,
            language: language,
          }),
        });
        if (res.ok) {
          const data = await res.json();
          setConversationId(data.conversation_id);
          setMessages((prev) => [...prev, data.assistant_message]);
        }
      }
    } catch (e) {
      console.error("Chat error:", e);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "⚠️ **Coach Error**: Unable to reach AI provider. Please check your connection or provider settings.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 1500);
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black/50 backdrop-blur-xs z-40" onClick={onClose} />

      <aside className="fixed top-0 right-0 h-full w-full sm:w-[480px] bg-[#0b132b] text-slate-100 border-l border-slate-800 z-50 flex flex-col shadow-2xl transition-all duration-300">
        {/* Header */}
        <div className="p-4 border-b border-slate-800 bg-[#0f172a]/90 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-rose-600 to-purple-600 flex items-center justify-center shadow-lg shadow-rose-500/20">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-sm text-white">DSArena AI Coach</h3>
                <span className="border border-rose-500/30 text-rose-400 text-[10px] px-1.5 py-0 rounded bg-rose-500/10">
                  Context-Aware
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Personal DSA Coach & Interview Mentor</p>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setIsSettingsOpen(true)}
              className="text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg p-1.5 flex items-center justify-center"
              title="AI Settings"
            >
              <Settings className="w-4 h-4" />
            </button>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg p-1.5 flex items-center justify-center"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Mode Navigation Tabs */}
        <div className="flex items-center gap-1.5 p-2 bg-[#0b132b] border-b border-slate-800 overflow-x-auto no-scrollbar">
          {modes.map((m) => {
            const Icon = m.icon;
            const isActive = activeMode === m.id;
            return (
              <button
                key={m.id}
                onClick={() => setActiveMode(m.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all border ${
                  isActive
                    ? m.color
                    : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {m.label}
              </button>
            );
          })}
        </div>

        {/* Mode Specific Controls (e.g. 5-Level Hint Stepper) */}
        {activeMode === "hint_system" && (
          <div className="p-3 bg-purple-950/20 border-b border-purple-900/30 flex items-center justify-between">
            <span className="text-xs font-semibold text-purple-300 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" /> Hint Stepper:
            </span>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((lvl) => (
                <button
                  key={lvl}
                  onClick={() => {
                    setHintLevel(lvl);
                    handleSendMessage(`Give me Level ${lvl} hint for this problem.`, lvl, "request_hint");
                  }}
                  className={`w-7 h-7 rounded-md text-xs font-bold transition-all border ${
                    hintLevel === lvl
                      ? "bg-purple-600 text-white border-purple-400 shadow-md shadow-purple-500/20"
                      : "bg-slate-900 border-slate-800 text-slate-400 hover:border-purple-800"
                  }`}
                  title={`Level ${lvl} Hint`}
                >
                  L{lvl}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Quick Action Chips */}
        <div className="px-3 py-2 bg-slate-900/50 border-b border-slate-800 flex items-center gap-2 overflow-x-auto no-scrollbar">
          {codeSnippet && (
            <button
              onClick={() => handleSendMessage(undefined, undefined, "review_code")}
              className="text-[11px] font-semibold px-2.5 py-1 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/20 whitespace-nowrap flex items-center gap-1"
            >
              <Code2 className="w-3 h-3" /> Review My Code
            </button>
          )}
          <button
            onClick={() => handleSendMessage(undefined, 1, "request_hint")}
            className="text-[11px] font-semibold px-2.5 py-1 rounded-md bg-purple-500/10 border border-purple-500/30 text-purple-300 hover:bg-purple-500/20 whitespace-nowrap flex items-center gap-1"
          >
            <Sparkles className="w-3 h-3" /> Get Hint
          </button>
          <button
            onClick={() => handleSendMessage("Explain the visual intuition for this topic.", undefined, "explain_concept")}
            className="text-[11px] font-semibold px-2.5 py-1 rounded-md bg-amber-500/10 border border-amber-500/30 text-amber-300 hover:bg-amber-500/20 whitespace-nowrap flex items-center gap-1"
          >
            <Lightbulb className="w-3 h-3" /> Visual Intuition
          </button>
          <button
            onClick={() => handleSendMessage(undefined, undefined, "generate_study_plan")}
            className="text-[11px] font-semibold px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/20 whitespace-nowrap flex items-center gap-1"
          >
            <Calendar className="w-3 h-3" /> Study Plan Today
          </button>
        </div>

        {/* Message Thread */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 font-sans text-sm">
          {messages.map((m, idx) => {
            const isUser = m.role === "user";
            return (
              <div
                key={idx}
                className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}
              >
                {!isUser && (
                  <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-rose-600 to-purple-600 flex items-center justify-center shrink-0 mt-0.5 shadow-md shadow-rose-500/20">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                )}

                <div
                  className={`relative group max-w-[85%] rounded-2xl p-3.5 text-xs leading-relaxed shadow-sm border ${
                    isUser
                      ? "bg-rose-600 text-white border-rose-500 rounded-br-none"
                      : "bg-slate-900/90 text-slate-200 border-slate-800 rounded-bl-none"
                  }`}
                >
                  {/* Copy Button for Assistant Messages */}
                  {!isUser && (
                    <button
                      onClick={() => copyToClipboard(m.content, idx)}
                      className="absolute top-2 right-2 p-1 text-slate-400 hover:text-white rounded opacity-0 group-hover:opacity-100 transition-opacity bg-slate-800/80"
                      title="Copy response"
                    >
                      {copiedIdx === idx ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                  )}

                  {/* Render content */}
                  <div className="whitespace-pre-wrap font-sans text-slate-200 space-y-2">
                    {m.content}
                  </div>

                  {m.hint_level && (
                    <span className="inline-block mt-2 text-[10px] border border-purple-500/40 text-purple-300 px-2 py-0.5 rounded bg-purple-500/10">
                      Hint Level {m.hint_level} / 5
                    </span>
                  )}
                </div>
              </div>
            );
          })}

          {loading && (
            <div className="flex gap-3 justify-start items-center">
              <div className="w-7 h-7 rounded-lg bg-rose-600/30 border border-rose-500/30 flex items-center justify-center shrink-0 animate-pulse">
                <Bot className="w-4 h-4 text-rose-400" />
              </div>
              <div className="bg-slate-900 border border-slate-800 text-slate-400 rounded-2xl rounded-bl-none p-3 text-xs flex items-center gap-2">
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-rose-400" />
                <span>Coach is reflecting on your DSA context...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-3 border-t border-slate-800 bg-[#0f172a]/90">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex gap-2"
          >
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={
                activeMode === "hint_system"
                  ? "Ask for a clue or hint level..."
                  : activeMode === "code_reviewer"
                  ? "Ask for time complexity or optimization tips..."
                  : "Ask your DSA coach anything..."
              }
              className="flex-1 bg-slate-900 border border-slate-800 text-slate-100 placeholder-slate-500 text-xs rounded-xl px-3.5 py-2.5 focus:outline-none focus:border-rose-500/50"
            />
            <button
              type="submit"
              disabled={loading || !inputMessage.trim()}
              className="bg-rose-600 hover:bg-rose-500 text-white rounded-xl w-9 h-9 shrink-0 shadow-lg shadow-rose-600/20 flex items-center justify-center cursor-pointer disabled:opacity-40"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </aside>

      <AISettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
    </>
  );
}
