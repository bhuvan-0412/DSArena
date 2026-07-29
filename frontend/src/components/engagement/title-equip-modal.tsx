"use client";

import React, { useState, useEffect } from "react";
import { Award, Check, X, Shield, Sparkles } from "lucide-react";
import { useAuthUser } from "@/hooks/use-auth-user";
import { BACKEND_URL } from "@/lib/api-config";


interface TitleItem {
  id: number;
  title_name: string;
  is_equipped: boolean;
}

interface TitleEquipModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function TitleEquipModal({ isOpen, onClose }: TitleEquipModalProps) {
  const { clerkId } = useAuthUser();
  const [titles, setTitles] = useState<TitleItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen && clerkId) {
      fetch(`${BACKEND_URL}/engagement/titles?clerk_id=${clerkId}`)
        .then((res) => res.json())
        .then((data) => setTitles(data || []))
        .catch((err) => console.error("Error fetching titles:", err))
        .finally(() => setLoading(false));
    }
  }, [isOpen, clerkId]);

  const handleEquip = async (titleName: string) => {
    const updated = titles.map((t) => ({ ...t, is_equipped: t.title_name === titleName }));
    setTitles(updated);

    try {
      await fetch(`${BACKEND_URL}/engagement/equip-title?clerk_id=${clerkId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title_name: titleName }),
      });
    } catch (e) {
      console.error("Error equipping title:", e);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-[#0f172a] text-slate-100 border border-slate-800 max-w-md w-full shadow-2xl rounded-3xl p-6 relative space-y-4">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
        >
          <X className="w-5 h-5" />
        </button>

        <div>
          <div className="flex items-center gap-2 text-purple-400 font-semibold mb-1">
            <Award className="w-5 h-5" />
            <span>Profile Customization</span>
          </div>
          <h2 className="text-xl font-extrabold text-white">Equip Profile Title</h2>
          <p className="text-xs text-slate-400 mt-1">
            Unlocked titles are displayed alongside your username across the Arena.
          </p>
        </div>

        <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
          {titles.map((t) => (
            <button
              key={t.id}
              onClick={() => handleEquip(t.title_name)}
              className={`w-full p-3 rounded-2xl border transition-all flex items-center justify-between cursor-pointer ${
                t.is_equipped
                  ? "bg-purple-500/10 border-purple-500 text-white shadow-md shadow-purple-500/10"
                  : "bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700"
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Sparkles className={`w-4 h-4 ${t.is_equipped ? "text-purple-400" : "text-slate-500"}`} />
                <span className="text-xs font-bold">{t.title_name}</span>
              </div>
              {t.is_equipped && <Check className="w-4 h-4 text-purple-400" />}
            </button>
          ))}
        </div>

        <div className="pt-2 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
