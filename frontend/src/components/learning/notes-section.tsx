"use client";

import { useState, useEffect, useRef } from "react";
import { Edit3, Save, CheckCircle2, Clock, Bold, Italic, List, Code, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

interface NotesSectionProps {
  initialContent: string;
  updatedAt: string | null;
  onSaveNotes: (content: string) => Promise<void>;
}

export function NotesSection({ initialContent, updatedAt, onSaveNotes }: NotesSectionProps) {
  const [content, setContent] = useState(initialContent);
  const [saving, setSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<string | null>(updatedAt);
  const [saveStatus, setSaveStatus] = useState<"SAVED" | "SAVING" | "UNSAVED">("SAVED");

  const saveTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    setContent(initialContent);
    setLastSaved(updatedAt);
  }, [initialContent, updatedAt]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setContent(val);
    setSaveStatus("UNSAVED");

    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    // Auto-save after 1.5 seconds of inactivity
    saveTimeoutRef.current = setTimeout(() => {
      triggerSave(val);
    }, 1500);
  };

  const triggerSave = async (valToSave: string) => {
    setSaving(true);
    setSaveStatus("SAVING");
    try {
      await onSaveNotes(valToSave);
      setSaveStatus("SAVED");
      setLastSaved(new Date().toISOString());
    } catch (err) {
      console.error("Auto save notes failed:", err);
      setSaveStatus("UNSAVED");
    } finally {
      setSaving(false);
    }
  };

  const insertFormatting = (prefix: string, suffix: string = "") => {
    const textarea = document.getElementById("personal-notes-editor") as HTMLTextAreaElement;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selected = content.substring(start, end) || "text";
    const replacement = `${prefix}${selected}${suffix}`;

    const newContent = content.substring(0, start) + replacement + content.substring(end);
    setContent(newContent);
    setSaveStatus("UNSAVED");

    if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
    saveTimeoutRef.current = setTimeout(() => {
      triggerSave(newContent);
    }, 1500);
  };

  return (
    <motion.div
      id="notes"
      className="border border-card-border rounded-3xl p-6 lg:p-8 glass-card space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
    >
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 border-b border-card-border/60 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Edit3 className="w-5 h-5 text-info-cyan" /> Personal Concept Notes
          </h2>
          <p className="text-xs text-muted-foreground mt-1">
            Write markdown notes, edge cases, or code snippets. Notes automatically save per user.
          </p>
        </div>

        {/* Auto-save Status Indicator */}
        <div className="flex items-center gap-3">
          {saveStatus === "SAVING" ? (
            <span className="text-xs font-mono text-xp-gold flex items-center gap-1.5 bg-xp-gold/10 border border-xp-gold/20 px-3 py-1.5 rounded-xl">
              <Loader2 className="w-3.5 h-3.5 animate-spin" /> Auto-saving...
            </span>
          ) : saveStatus === "SAVED" ? (
            <span className="text-xs font-mono text-success-emerald flex items-center gap-1.5 bg-success-emerald/10 border border-success-emerald/20 px-3 py-1.5 rounded-xl">
              <CheckCircle2 className="w-3.5 h-3.5" /> All Changes Saved
            </span>
          ) : (
            <span className="text-xs font-mono text-yellow-500 flex items-center gap-1.5 bg-yellow-500/10 border border-yellow-500/20 px-3 py-1.5 rounded-xl">
              <Clock className="w-3.5 h-3.5" /> Unsaved Changes
            </span>
          )}

          <button
            onClick={() => triggerSave(content)}
            disabled={saving}
            className="px-4 py-2 rounded-xl bg-primary hover:bg-primary/90 text-white font-bold text-xs uppercase tracking-wider flex items-center gap-1.5 transition-all cursor-pointer shadow-md shadow-primary/20 disabled:opacity-50"
          >
            <Save className="w-3.5 h-3.5" /> Save Now
          </button>
        </div>
      </div>

      {/* Formatting Toolbar */}
      <div className="flex flex-wrap items-center gap-1.5 p-2 rounded-xl border border-card-border/60 bg-[#030305]/60 text-xs">
        <button
          onClick={() => insertFormatting("**", "**")}
          title="Bold"
          className="p-2 rounded-lg hover:bg-white/[0.06] text-muted-foreground hover:text-white cursor-pointer"
        >
          <Bold className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={() => insertFormatting("*", "*")}
          title="Italic"
          className="p-2 rounded-lg hover:bg-white/[0.06] text-muted-foreground hover:text-white cursor-pointer"
        >
          <Italic className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={() => insertFormatting("\n- ")}
          title="Bullet List"
          className="p-2 rounded-lg hover:bg-white/[0.06] text-muted-foreground hover:text-white cursor-pointer"
        >
          <List className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={() => insertFormatting("`", "`")}
          title="Inline Code"
          className="p-2 rounded-lg hover:bg-white/[0.06] text-muted-foreground hover:text-white cursor-pointer"
        >
          <Code className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={() => insertFormatting("\n```python\n", "\n```\n")}
          title="Code Block"
          className="p-2 rounded-lg hover:bg-white/[0.06] text-muted-foreground hover:text-white font-mono text-[10px] font-bold uppercase cursor-pointer"
        >
          [CodeBlock]
        </button>
        <span className="text-[10px] font-mono text-zinc-500 ml-auto pr-2">Markdown Supported</span>
      </div>

      {/* Textarea Editor */}
      <div className="relative">
        <textarea
          id="personal-notes-editor"
          value={content}
          onChange={handleChange}
          placeholder="# My Personal Notes\n- Key trick for Two Sum: Use hash map complement...\n- Remember to handle 0 or negative numbers..."
          className="w-full min-h-[200px] p-4 rounded-2xl border border-card-border bg-[#020204] text-white font-mono text-xs leading-relaxed focus:outline-none focus:border-info-cyan/60 transition-colors resize-y"
        />
      </div>

      {lastSaved && (
        <div className="text-[10px] font-mono text-muted-foreground flex items-center gap-1 justify-end">
          <Clock className="w-3 h-3 text-zinc-500" />
          <span>Last edited: {new Date(lastSaved).toLocaleString()}</span>
        </div>
      )}
    </motion.div>
  );
}
