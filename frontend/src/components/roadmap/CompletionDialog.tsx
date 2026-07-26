"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Trophy, ChevronRight, CheckCircle2, X } from "lucide-react";

interface CompletionDialogProps {
  isOpen: boolean;
  onClose: () => void;
  nodeTitle: string;
  xpReward?: number;
  nextNodeId?: string | null;
  onGoToNextNode?: () => void;
}

export function CompletionDialog({
  isOpen,
  onClose,
  nodeTitle,
  xpReward = 50,
  nextNodeId,
  onGoToNextNode,
}: CompletionDialogProps) {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="glass-card max-w-md w-full p-6 rounded-3xl border border-card-border shadow-2xl relative space-y-6 text-center"
        >
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-1.5 rounded-full bg-zinc-900 text-zinc-400 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>

          {/* Trophy Badge */}
          <div className="mx-auto w-16 h-16 rounded-full bg-gradient-to-tr from-xp-gold to-yellow-300 p-0.5 shadow-[0_0_20px_rgba(234,179,8,0.5)]">
            <div className="w-full h-full rounded-full bg-zinc-950 flex items-center justify-center">
              <Trophy className="w-8 h-8 text-xp-gold animate-bounce" />
            </div>
          </div>

          <div className="space-y-2">
            <span className="text-xs font-mono uppercase font-bold text-success-emerald tracking-widest flex items-center justify-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>NODE COMPLETED!</span>
            </span>
            <h3 className="text-2xl font-black text-white">{nodeTitle}</h3>
            <p className="text-xs text-muted-foreground">
              Great job! You have completed this video lesson and earned{" "}
              <span className="text-xp-gold font-bold">+{xpReward} XP</span>.
            </p>
          </div>

          {/* Actions */}
          <div className="space-y-3 pt-2">
            {nextNodeId && onGoToNextNode ? (
              <button
                onClick={() => {
                  onClose();
                  onGoToNextNode();
                }}
                className="w-full py-3 rounded-xl bg-primary hover:bg-primary/90 text-white font-bold text-sm uppercase tracking-wider flex items-center justify-center gap-2 shadow-lg shadow-primary/20 transition-all"
              >
                <span>Go To Next Node</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
              <div className="p-3 rounded-xl bg-success-emerald/10 border border-success-emerald/30 text-success-emerald font-bold text-xs">
                🎉 Congratulations! You completed this section.
              </div>
            )}

            <button
              onClick={onClose}
              className="w-full py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-300 font-bold text-xs uppercase tracking-wider border border-zinc-800 transition-colors"
            >
              Stay on Page
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
