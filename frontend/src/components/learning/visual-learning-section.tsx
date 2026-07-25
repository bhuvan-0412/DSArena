"use client";

import { useState } from "react";
import { Play, Layers, GitBranch, Search, Share2, BarChart3, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

export interface VisualPlaceholder {
  id: string;
  title: string;
  type: string;
  description: string;
}

interface VisualLearningSectionProps {
  placeholders: VisualPlaceholder[];
}

export function VisualLearningSection({ placeholders }: VisualLearningSectionProps) {
  const [activeVisualId, setActiveVisualId] = useState<string>(placeholders.length > 0 ? placeholders[0].id : "array_anim");
  const [simStep, setSimStep] = useState<number>(0);

  const getIconForType = (type: string) => {
    switch (type.toLowerCase()) {
      case "array":
        return <Layers className="w-5 h-5 text-primary" />;
      case "linked list":
        return <GitBranch className="w-5 h-5 text-success-emerald" />;
      case "binary search":
        return <Search className="w-5 h-5 text-info-cyan" />;
      case "tree":
        return <Share2 className="w-5 h-5 text-purple-400" />;
      case "graph":
        return <Share2 className="w-5 h-5 text-xp-gold" />;
      case "sorting":
        return <BarChart3 className="w-5 h-5 text-orange-400" />;
      default:
        return <Play className="w-5 h-5 text-primary" />;
    }
  };

  const activeVisual = placeholders.find((p) => p.id === activeVisualId) || placeholders[0];

  return (
    <motion.div
      id="visual-learning"
      className="border border-card-border rounded-3xl p-6 lg:p-8 glass-card space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <div className="flex justify-between items-center border-b border-card-border/60 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Play className="w-5 h-5 text-primary fill-primary" /> Visual Learning Engine
          </h2>
          <p className="text-xs text-muted-foreground mt-1">
            Interactive visualization framework for stepping through data structure pointer operations and algorithm animations.
          </p>
        </div>
      </div>

      {/* Visualizer Selector Tabs */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        {placeholders.map((p) => {
          const isActive = p.id === activeVisualId;
          return (
            <button
              key={p.id}
              onClick={() => {
                setActiveVisualId(p.id);
                setSimStep(0);
              }}
              className={`p-3 rounded-xl border text-xs font-bold transition-all duration-200 cursor-pointer flex flex-col items-center gap-2 text-center ${
                isActive
                  ? "bg-primary/10 border-primary text-white shadow-lg shadow-primary/10"
                  : "border-card-border bg-[#030303]/40 text-muted-foreground hover:text-white hover:border-card-border/80"
              }`}
            >
              {getIconForType(p.type)}
              <span className="text-[11px] leading-tight">{p.type}</span>
            </button>
          );
        })}
      </div>

      {/* Visual Canvas Area */}
      {activeVisual && (
        <div className="border border-card-border rounded-2xl p-6 bg-[#030307]/80 space-y-6 relative overflow-hidden">
          <div className="flex justify-between items-center">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-widest font-mono text-primary block">
                [ANIMATION MODULE]
              </span>
              <h3 className="text-md font-extrabold text-white uppercase tracking-wide">
                {activeVisual.title}
              </h3>
              <p className="text-xs text-muted-foreground mt-0.5">{activeVisual.description}</p>
            </div>

            <span className="text-[10px] font-mono text-success-emerald bg-success-emerald/10 border border-success-emerald/20 px-2.5 py-1 rounded uppercase font-bold">
              Ready for React Component
            </span>
          </div>

          {/* Interactive Mock Canvas Visualizer */}
          <div className="min-h-[220px] rounded-xl border border-card-border/60 bg-[#010103] p-6 flex flex-col items-center justify-center gap-6 relative">
            {/* Visualizer Demo Mockup depending on type */}
            {activeVisual.type === "Array" && (
              <div className="flex flex-wrap items-center justify-center gap-3">
                {[2, 7, 11, 15, 23].map((val, idx) => (
                  <div
                    key={idx}
                    className={`w-16 h-16 rounded-xl border-2 flex flex-col items-center justify-center transition-all duration-300 ${
                      simStep === idx
                        ? "bg-primary/20 border-primary scale-110 shadow-lg shadow-primary/20"
                        : "bg-zinc-950 border-card-border"
                    }`}
                  >
                    <span className="text-[9px] font-mono text-muted-foreground">idx [{idx}]</span>
                    <span className="text-base font-extrabold text-white">{val}</span>
                  </div>
                ))}
              </div>
            )}

            {activeVisual.type === "Linked List" && (
              <div className="flex flex-wrap items-center justify-center gap-2">
                {[10, 20, 30, 40].map((val, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <div
                      className={`px-4 py-3 rounded-xl border-2 flex items-center gap-3 transition-all duration-300 ${
                        simStep === idx ? "bg-success-emerald/20 border-success-emerald scale-105" : "bg-zinc-950 border-card-border"
                      }`}
                    >
                      <span className="text-sm font-bold text-white">{val}</span>
                      <span className="text-[9px] font-mono text-muted-foreground border-l border-card-border pl-2">next -&gt;</span>
                    </div>
                    {idx < 3 && <span className="text-muted-foreground text-xs font-mono">➡</span>}
                  </div>
                ))}
              </div>
            )}

            {activeVisual.type === "Binary Search" && (
              <div className="flex flex-col items-center gap-3">
                <div className="text-xs font-mono text-info-cyan">Target: 23 | Low: 0 | High: 5 | Mid: {simStep + 1}</div>
                <div className="flex items-center gap-2">
                  {[1, 3, 5, 8, 12, 23].map((val, idx) => (
                    <div
                      key={idx}
                      className={`w-12 h-12 rounded-lg border flex items-center justify-center text-xs font-bold ${
                        idx === simStep + 1
                          ? "bg-info-cyan/20 border-info-cyan text-info-cyan scale-110 shadow-md shadow-info-cyan/20"
                          : "bg-zinc-950 border-card-border text-muted-foreground"
                      }`}
                    >
                      {val}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeVisual.type !== "Array" && activeVisual.type !== "Linked List" && activeVisual.type !== "Binary Search" && (
              <div className="flex flex-col items-center gap-2 text-center">
                <Sparkles className="w-8 h-8 text-xp-gold animate-pulse" />
                <span className="text-xs font-mono font-bold text-white">
                  [{activeVisual.title} Active]
                </span>
                <p className="text-[11px] text-muted-foreground max-w-sm">
                  This modular card placeholder connects cleanly with D3.js, Canvas, or Framer Motion visualizer components.
                </p>
              </div>
            )}

            {/* Stepper Controls */}
            <div className="flex items-center gap-3 pt-2">
              <button
                onClick={() => setSimStep((prev) => Math.max(0, prev - 1))}
                className="px-3 py-1.5 rounded-lg border border-card-border bg-zinc-950 text-xs font-mono text-muted-foreground hover:text-white cursor-pointer"
              >
                ◀ Step Prev
              </button>
              <span className="text-xs font-mono text-muted-foreground">Step #{simStep + 1}</span>
              <button
                onClick={() => setSimStep((prev) => (prev + 1) % 4)}
                className="px-3 py-1.5 rounded-lg border border-card-border bg-primary/20 text-xs font-mono text-white hover:bg-primary/30 cursor-pointer"
              >
                Step Next ▶
              </button>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}
