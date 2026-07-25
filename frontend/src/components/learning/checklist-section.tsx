"use client";

import { CheckSquare, Video, FileText, Lightbulb, Award, Code2, CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";

export interface LearningChecklistData {
  watched_video: boolean;
  read_notes: boolean;
  understood_concepts: boolean;
  completed_quiz: boolean;
  solved_problems: boolean;
  updated_at?: string | null;
}

interface ChecklistSectionProps {
  checklist: LearningChecklistData;
  onToggleChecklist: (key: keyof LearningChecklistData) => void;
}

export function ChecklistSection({ checklist, onToggleChecklist }: ChecklistSectionProps) {
  const items = [
    {
      key: "watched_video" as keyof LearningChecklistData,
      label: "Watched Video",
      description: "Watched the concept masterclass or video breakdown",
      icon: Video,
      color: "text-red-500 bg-red-500/10 border-red-500/20",
    },
    {
      key: "read_notes" as keyof LearningChecklistData,
      label: "Read Notes",
      description: "Read through takeaway notes, articles, and documentation",
      icon: FileText,
      color: "text-info-cyan bg-info-cyan/10 border-info-cyan/20",
    },
    {
      key: "understood_concepts" as keyof LearningChecklistData,
      label: "Understood Concepts",
      description: "Grasped time/space complexities and edge case pitfalls",
      icon: Lightbulb,
      color: "text-xp-gold bg-xp-gold/10 border-xp-gold/20",
    },
    {
      key: "completed_quiz" as keyof LearningChecklistData,
      label: "Completed Quiz",
      description: "Tested active recall by completing the interactive quiz",
      icon: Award,
      color: "text-purple-400 bg-purple-500/10 border-purple-500/20",
    },
    {
      key: "solved_problems" as keyof LearningChecklistData,
      label: "Solved Problems",
      description: "Solved the required coding problems associated with this topic",
      icon: Code2,
      color: "text-success-emerald bg-success-emerald/10 border-success-emerald/20",
    },
  ];

  const completedCount = items.filter((item) => !!checklist[item.key]).length;
  const progressPct = Math.round((completedCount / 5.0) * 100);

  return (
    <motion.div
      id="checklist"
      className="border border-card-border rounded-3xl p-6 lg:p-8 glass-card space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
    >
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 border-b border-card-border/60 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-success-emerald" /> Topic Learning Checklist
          </h2>
          <p className="text-xs text-muted-foreground mt-1">
            Complete all 5 mastery milestones to finish this roadmap node.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs font-mono font-bold text-success-emerald bg-success-emerald/10 border border-success-emerald/20 px-3 py-1.5 rounded-xl">
            {completedCount} / 5 MILESTONES ({progressPct}%)
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-2.5 bg-zinc-950 rounded-full overflow-hidden border border-card-border/40">
        <div
          className="h-full bg-success-emerald transition-all duration-500"
          style={{ width: `${progressPct}%` }}
        />
      </div>

      {/* Checklist Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {items.map((item) => {
          const Icon = item.icon;
          const isChecked = !!checklist[item.key];

          return (
            <button
              key={item.key}
              onClick={() => onToggleChecklist(item.key)}
              className={`p-4 rounded-2xl border text-left flex items-start gap-3.5 transition-all duration-200 cursor-pointer ${
                isChecked
                  ? "bg-success-emerald/10 border-success-emerald/40 text-white shadow-md shadow-success-emerald/5"
                  : "bg-[#030303]/40 border-card-border hover:border-card-border/80 text-muted-foreground"
              }`}
            >
              <div
                className={`w-6 h-6 rounded-lg border shrink-0 flex items-center justify-center transition-all ${
                  isChecked ? "bg-success-emerald border-success-emerald text-black font-bold" : "border-zinc-700 bg-zinc-950"
                }`}
              >
                {isChecked && <CheckCircle2 className="w-4 h-4 text-black stroke-[3]" />}
              </div>

              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className={`p-1.5 rounded-lg border text-xs ${item.color}`}>
                    <Icon className="w-3.5 h-3.5" />
                  </span>
                  <span className={`text-xs font-bold ${isChecked ? "text-white line-through opacity-80" : "text-white"}`}>
                    {item.label}
                  </span>
                </div>
                <p className="text-[11px] text-muted-foreground leading-relaxed">{item.description}</p>
              </div>
            </button>
          );
        })}
      </div>
    </motion.div>
  );
}
