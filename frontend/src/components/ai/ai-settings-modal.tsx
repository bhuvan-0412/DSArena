import React, { useState, useEffect } from "react";
import { Cpu, Thermometer, Sparkles, Check, Settings2, Sliders, X } from "lucide-react";
import { useAuthUser } from "@/hooks/use-auth-user";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

interface AISettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AISettingsModal({ isOpen, onClose }: AISettingsModalProps) {
  const { clerkId } = useAuthUser();
  const [provider, setProvider] = useState<string>("openai");
  const [temperature, setTemperature] = useState<number>(0.7);
  const [style, setStyle] = useState<string>("visual_socratic");
  const [providersList, setProvidersList] = useState<unknown[]>([]);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    if (isOpen && clerkId) {
      fetch(`${BACKEND_URL}/ai/settings?clerk_id=${clerkId}`)
        .then((res) => res.json())
        .then((data) => {
          if (data) {
            setProvider(data.active_provider_name || "openai");
            setTemperature(data.temperature ?? 0.7);
            setStyle(data.preferred_explanation_style || "visual_socratic");
            setProvidersList(data.available_providers || []);
          }
        })
        .catch((err) => console.error("Error fetching AI settings:", err));
    }
  }, [isOpen, clerkId]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${BACKEND_URL}/ai/settings?clerk_id=${clerkId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          provider_name: provider,
          temperature: temperature,
          preferred_explanation_style: style,
        }),
      });
      if (res.ok) {
        setSavedSuccess(true);
        setTimeout(() => {
          setSavedSuccess(false);
          onClose();
        }, 800);
      }
    } catch (e) {
      console.error("Failed to save settings:", e);
    } finally {
      setSaving(false);
    }
  };

  const styleOptions = [
    { id: "visual_socratic", label: "Visual & Socratic", desc: "Step-by-step intuition with visual analogies and guiding questions." },
    { id: "concise_direct", label: "Concise & Direct", desc: "Short, highly focused explanations straight to the point." },
    { id: "deep_dive", label: "Deep-Dive Theoretical", desc: "In-depth proofs, lower-level memory mechanics, and time/space proofs." },
    { id: "interview_strict", label: "Strict FAANG Interviewer", desc: "Simulates an intense technical interviewer testing edge cases and trade-offs." },
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-[#0f172a] text-slate-100 border border-slate-800 max-w-lg w-full shadow-2xl rounded-2xl p-6 relative space-y-4">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
        >
          <X className="w-5 h-5" />
        </button>

        <div>
          <div className="flex items-center gap-2 text-rose-400 font-semibold mb-1">
            <Cpu className="w-5 h-5" />
            <span>AI Coach Preferences</span>
          </div>
          <div className="text-xl font-bold text-white flex items-center justify-between">
            Configure Provider & Behavior
            <span className="border border-rose-500/30 text-rose-400 text-xs px-2 py-0.5 rounded-md bg-rose-500/10">
              Phase 3.1
            </span>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Customize your AI LLM engine, temperature randomness, and explanation style.
          </p>
        </div>

        <div className="space-y-6 my-4">
          {/* AI Provider Selection */}
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 block flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-cyan-400" />
              Active LLM Provider
            </label>
            <div className="grid grid-cols-2 gap-2.5">
              {[
                { id: "openai", name: "OpenAI GPT-4o Mini", badge: "Fast & Accurate" },
                { id: "gemini", name: "Google Gemini 1.5", badge: "Multimodal" },
                { id: "anthropic", name: "Claude 3.5 Sonnet", badge: "Reasoning" },
                { id: "local", name: "Local LLM (Llama 3)", badge: "Privacy / Ollama" },
              ].map((p) => {
                const isSelected = provider === p.id;
                return (
                  <button
                    key={p.id}
                    onClick={() => setProvider(p.id)}
                    className={`p-3 rounded-xl text-left border transition-all flex flex-col justify-between ${
                      isSelected
                        ? "bg-rose-500/10 border-rose-500 text-white shadow-lg shadow-rose-500/10"
                        : "bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700 hover:bg-slate-800/40"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-xs">{p.name}</span>
                      {isSelected && <Check className="w-4 h-4 text-rose-400" />}
                    </div>
                    <span className="text-[10px] text-slate-400 mt-1">{p.badge}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Temperature Slider */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Thermometer className="w-4 h-4 text-amber-400" />
                Temperature (Randomness)
              </label>
              <span className="text-xs font-mono font-bold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-md border border-rose-500/20">
                {temperature}
              </span>
            </div>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-rose-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>0.0 (Precise / Deterministic)</span>
              <span>1.0 (Creative)</span>
            </div>
          </div>

          {/* Explanation Style */}
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 block flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-purple-400" />
              Preferred Explanation Style
            </label>
            <div className="space-y-2">
              {styleOptions.map((opt) => {
                const isSelected = style === opt.id;
                return (
                  <button
                    key={opt.id}
                    onClick={() => setStyle(opt.id)}
                    className={`w-full p-3 rounded-xl text-left border transition-all flex items-start justify-between ${
                      isSelected
                        ? "bg-purple-500/10 border-purple-500 text-white shadow-md shadow-purple-500/10"
                        : "bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700"
                    }`}
                  >
                    <div>
                      <div className="font-semibold text-xs text-slate-200">{opt.label}</div>
                      <div className="text-[11px] text-slate-400 mt-0.5">{opt.desc}</div>
                    </div>
                    {isSelected && <Check className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-slate-800/80">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold rounded-xl border border-slate-800 text-slate-300 hover:bg-slate-800 transition-all"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 text-xs font-semibold rounded-xl bg-rose-600 hover:bg-rose-500 text-white transition-all flex items-center gap-2"
          >
            {savedSuccess ? (
              <>
                <Check className="w-4 h-4" /> Saved!
              </>
            ) : (
              <>
                <Sliders className="w-4 h-4" /> Save Preferences
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
