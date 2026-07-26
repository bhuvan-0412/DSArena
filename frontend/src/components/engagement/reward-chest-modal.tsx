"use client";

import React, { useState, useEffect } from "react";
import { Package, Sparkles, X, Trophy, Zap, Check } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuthUser } from "@/hooks/use-auth-user";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

interface RewardChestModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function RewardChestModal({ isOpen, onClose }: RewardChestModalProps) {
  const { clerkId } = useAuthUser();
  const [isOpening, setIsOpening] = useState(false);
  const [reward, setReward] = useState<{ xp_granted?: number; unlocked_title?: string; message?: string } | null>(null);

  if (!isOpen) return null;

  const handleOpenChest = async () => {
    setIsOpening(true);
    try {
      const res = await fetch(`${BACKEND_URL}/engagement/open-chest?chest_id=1&clerk_id=${clerkId}`, {
        method: "POST",
      });
      const data = await res.json();
      setTimeout(() => {
        setReward(data);
        setIsOpening(false);
      }, 1200);
    } catch (e) {
      console.error("Error opening chest:", e);
      setIsOpening(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-[#0f172a] text-slate-100 border border-slate-800 max-w-md w-full shadow-2xl rounded-3xl p-8 relative text-center space-y-6">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="space-y-1">
          <span className="text-[10px] font-extrabold uppercase tracking-widest px-2.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
            Mystery Reward Chest
          </span>
          <h2 className="text-2xl font-black text-white tracking-tight">Unlock Your Loot</h2>
        </div>

        {/* Animated Chest Graphic */}
        <div className="py-6 flex flex-col items-center justify-center relative">
          <motion.div
            animate={isOpening ? { scale: [1, 1.2, 0.9, 1.1, 1], rotate: [0, -10, 10, -5, 0] } : {}}
            transition={{ duration: 1 }}
            className="w-28 h-28 rounded-3xl bg-gradient-to-tr from-amber-600 via-amber-400 to-amber-200 border-2 border-amber-300 flex items-center justify-center shadow-2xl shadow-amber-500/20 relative"
          >
            <Package className="w-14 h-14 text-slate-950" />
          </motion.div>
        </div>

        {reward ? (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-3 p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30">
            <div className="flex justify-center items-center gap-1 text-amber-400 font-extrabold text-lg">
              <Sparkles className="w-5 h-5" /> +{reward.xp_granted} XP Granted!
            </div>
            {reward.unlocked_title && (
              <div className="text-xs text-purple-300 font-bold bg-purple-500/10 border border-purple-500/20 py-1.5 px-3 rounded-xl">
                Title Unlocked: &quot;{reward.unlocked_title}&quot;
              </div>
            )}
            <button
              onClick={onClose}
              className="w-full py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold text-xs uppercase transition-all shadow"
            >
              Collect Rewards
            </button>
          </motion.div>
        ) : (
          <button
            onClick={handleOpenChest}
            disabled={isOpening}
            className="w-full py-3 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-extrabold text-xs uppercase tracking-wider shadow-lg shadow-rose-600/20 cursor-pointer disabled:opacity-50 transition-all"
          >
            {isOpening ? "Opening Chest..." : "Open Mystery Chest"}
          </button>
        )}
      </div>
    </div>
  );
}
