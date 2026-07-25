"use client";

import { useState } from "react";
import { Lightbulb, ChevronDown, ChevronUp, CheckCircle, AlertTriangle, Sparkles, Clock, ShieldCheck } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export interface KeyConceptItem {
  id: number;
  node_id: string;
  title: string;
  summary: string;
  key_points?: string[];
  complexity_notes?: string;
  common_mistakes?: string[];
  best_practices?: string[];
  order_index: number;
}

interface KeyConceptsSectionProps {
  keyConcepts: KeyConceptItem[];
}

export function KeyConceptsSection({ keyConcepts }: KeyConceptsSectionProps) {
  const [expandedId, setExpandedId] = useState<number | null>(keyConcepts.length > 0 ? keyConcepts[0].id : null);

  const toggleExpand = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <motion.div
      id="key-concepts"
      className="border border-card-border rounded-3xl p-6 lg:p-8 glass-card space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <div className="flex justify-between items-center border-b border-card-border/60 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-xp-gold" /> Key Concepts & Pitfalls
          </h2>
          <p className="text-xs text-muted-foreground mt-1">
            Deepen your mental models with core concepts, complexity rules, and common interview mistakes.
          </p>
        </div>
      </div>

      {keyConcepts.length === 0 ? (
        <div className="text-center py-8 text-xs text-muted-foreground">
          No key concepts defined for this topic.
        </div>
      ) : (
        <div className="space-y-4">
          {keyConcepts.map((kc) => {
            const isExpanded = expandedId === kc.id;
            return (
              <div
                key={kc.id}
                className={`border rounded-2xl overflow-hidden transition-all duration-300 ${
                  isExpanded ? "border-xp-gold/30 bg-[#05050a]/80 shadow-lg shadow-xp-gold/[0.02]" : "border-card-border bg-[#030303]/40"
                }`}
              >
                {/* Accordion Header */}
                <button
                  onClick={() => toggleExpand(kc.id)}
                  className="w-full p-5 text-left flex justify-between items-center gap-4 cursor-pointer hover:bg-white/[0.02] transition-colors"
                >
                  <div className="space-y-1">
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-xp-gold" /> {kc.title}
                    </h3>
                    <p className="text-xs text-muted-foreground line-clamp-1">
                      {kc.summary}
                    </p>
                  </div>
                  <span className="p-2 rounded-xl border border-card-border/60 bg-zinc-950 text-muted-foreground shrink-0">
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </span>
                </button>

                {/* Accordion Content */}
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.25 }}
                      className="border-t border-card-border/50 p-5 space-y-5 text-xs"
                    >
                      {/* Summary Box */}
                      <div className="p-4 rounded-xl border border-xp-gold/20 bg-xp-gold/5 text-muted-foreground leading-relaxed">
                        <span className="text-[10px] uppercase font-bold tracking-widest text-xp-gold block mb-1">
                          Core Summary:
                        </span>
                        {kc.summary}
                      </div>

                      {/* Key Points */}
                      {kc.key_points && kc.key_points.length > 0 && (
                        <div className="space-y-2">
                          <span className="text-[10px] uppercase font-bold tracking-widest text-white flex items-center gap-1.5">
                            <CheckCircle className="w-3.5 h-3.5 text-success-emerald" /> Key Takeaways
                          </span>
                          <ul className="space-y-1.5 text-muted-foreground pl-5 list-disc">
                            {kc.key_points.map((pt, idx) => (
                              <li key={idx}>{pt}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Complexity Notes */}
                      {kc.complexity_notes && (
                        <div className="p-4 rounded-xl border border-card-border bg-zinc-950/80 space-y-1 font-mono text-xs">
                          <span className="text-[9px] uppercase font-bold tracking-widest text-info-cyan block flex items-center gap-1">
                            <Clock className="w-3 h-3" /> Complexity Notes
                          </span>
                          <p className="text-zinc-300 whitespace-pre-line">{kc.complexity_notes}</p>
                        </div>
                      )}

                      {/* Common Mistakes & Best Practices Grid */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {kc.common_mistakes && kc.common_mistakes.length > 0 && (
                          <div className="p-4 rounded-xl border border-red-500/20 bg-red-500/5 space-y-2">
                            <span className="text-[10px] uppercase font-bold tracking-widest text-red-500 flex items-center gap-1.5">
                              <AlertTriangle className="w-3.5 h-3.5" /> Common Pitfalls
                            </span>
                            <ul className="space-y-1.5 text-muted-foreground pl-4 list-disc">
                              {kc.common_mistakes.map((m, idx) => (
                                <li key={idx}>{m}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {kc.best_practices && kc.best_practices.length > 0 && (
                          <div className="p-4 rounded-xl border border-success-emerald/20 bg-success-emerald/5 space-y-2">
                            <span className="text-[10px] uppercase font-bold tracking-widest text-success-emerald flex items-center gap-1.5">
                              <ShieldCheck className="w-3.5 h-3.5" /> Best Practices
                            </span>
                            <ul className="space-y-1.5 text-muted-foreground pl-4 list-disc">
                              {kc.best_practices.map((bp, idx) => (
                                <li key={idx}>{bp}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            );
          })}
        </div>
      )}
    </motion.div>
  );
}
