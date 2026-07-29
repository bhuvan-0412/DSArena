"use client";

import React, { useEffect, useState, useRef } from "react";
import { MarkdownEditor } from "./MarkdownEditor";
import { FileText, Save, Sparkles } from "lucide-react";
import { BACKEND_URL } from "@/lib/api-config";

interface NotesPanelProps {
  nodeId: string;
  clerkId: string;
  initialContent?: string;
  onNoteUpdated?: (newContent: string) => void;
}



export function NotesPanel({
  nodeId,
  clerkId,
  initialContent = "",
  onNoteUpdated,
}: NotesPanelProps) {
  const [content, setContent] = useState(initialContent);
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [lastSavedContent, setLastSavedContent] = useState(initialContent);
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Sync initial content
  useEffect(() => {
    setContent(initialContent);
    setLastSavedContent(initialContent);
  }, [initialContent]);

  // Handle auto-save with 1.5s idle debounce
  const handleContentChange = (newVal: string) => {
    setContent(newVal);
    setSaveStatus("saving");

    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current);
    }

    autoSaveTimerRef.current = setTimeout(() => {
      saveNoteToBackend(newVal);
    }, 1500);
  };

  const saveNoteToBackend = async (noteText: string) => {
    try {
      setSaveStatus("saving");
      const res = await fetch(
        `${BACKEND_URL}/roadmap/nodes/${nodeId}/notes?clerk_id=${clerkId}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content: noteText }),
        }
      );

      if (res.ok) {
        setSaveStatus("saved");
        setLastSavedContent(noteText);
        if (onNoteUpdated) onNoteUpdated(noteText);

        setTimeout(() => {
          setSaveStatus((prev) => (prev === "saved" ? "idle" : prev));
        }, 3000);
      } else {
        setSaveStatus("error");
      }
    } catch (err) {
      console.error("Error auto-saving note:", err);
      setSaveStatus("error");
    }
  };

  const handleDeleteNote = async () => {
    if (!window.confirm("Are you sure you want to delete your lesson notes?")) return;

    try {
      setSaveStatus("saving");
      const res = await fetch(
        `${BACKEND_URL}/roadmap/nodes/${nodeId}/notes?clerk_id=${clerkId}`,
        { method: "DELETE" }
      );

      if (res.ok) {
        setContent("");
        setLastSavedContent("");
        setSaveStatus("saved");
        if (onNoteUpdated) onNoteUpdated("");
      }
    } catch (err) {
      console.error("Error deleting note:", err);
      setSaveStatus("error");
    }
  };

  const handleManualSave = () => {
    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current);
    }
    saveNoteToBackend(content);
  };

  return (
    <div className="space-y-4">
      {/* Header Info */}
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-white flex items-center gap-1.5">
              <span>MY PRIVATE LESSON NOTES</span>
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            </h4>
            <p className="text-[11px] text-zinc-400">Auto-saved to your personal profile</p>
          </div>
        </div>

        <button
          onClick={handleManualSave}
          disabled={saveStatus === "saving" || content === lastSavedContent}
          className="px-3 py-1.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-300 font-bold text-xs flex items-center gap-1.5 transition-all disabled:opacity-50"
        >
          <Save className="w-3.5 h-3.5 text-cyan-400" />
          <span>Save Now</span>
        </button>
      </div>

      {/* Editor Container */}
      <MarkdownEditor
        value={content}
        onChange={handleContentChange}
        onDeleteNote={content ? handleDeleteNote : undefined}
        saveStatus={saveStatus}
      />
    </div>
  );
}
