"use client";

import React, { useState } from "react";
import { Bold, Italic, Code, List, Heading, Eye, Edit3, Trash2 } from "lucide-react";

interface MarkdownEditorProps {
  value: string;
  onChange: (newValue: string) => void;
  onDeleteNote?: () => void;
  saveStatus?: "idle" | "saving" | "saved" | "error";
  readOnly?: boolean;
}

export function MarkdownEditor({
  value,
  onChange,
  onDeleteNote,
  saveStatus = "idle",
  readOnly = false,
}: MarkdownEditorProps) {
  const [isPreview, setIsPreview] = useState(false);

  const insertFormatting = (prefix: string, suffix: string = "") => {
    if (readOnly) return;
    const textarea = document.getElementById("lesson-markdown-textarea") as HTMLTextAreaElement;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = value.substring(start, end);
    const replacement = `${prefix}${selectedText || "text"}${suffix}`;
    const newValue = value.substring(0, start) + replacement + value.substring(end);

    onChange(newValue);

    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start + prefix.length, start + prefix.length + (selectedText.length || 4));
    }, 0);
  };

  // Basic client markdown preview renderer helper
  const renderSimpleMarkdown = (text: string) => {
    if (!text.trim()) return <p className="text-zinc-500 italic text-xs">No notes written yet. Start typing below...</p>;

    const lines = text.split("\n");
    return lines.map((line, idx) => {
      if (line.startsWith("### ")) {
        return <h4 key={idx} className="text-sm font-bold text-cyan-300 mt-2 mb-1">{line.replace("### ", "")}</h4>;
      }
      if (line.startsWith("## ")) {
        return <h3 key={idx} className="text-base font-bold text-cyan-400 mt-3 mb-1">{line.replace("## ", "")}</h3>;
      }
      if (line.startsWith("# ")) {
        return <h2 key={idx} className="text-lg font-black text-white mt-4 mb-2">{line.replace("# ", "")}</h2>;
      }
      if (line.startsWith("- ") || line.startsWith("* ")) {
        return (
          <li key={idx} className="ml-4 list-disc text-xs text-zinc-300 my-0.5">
            {line.substring(2)}
          </li>
        );
      }
      if (line.startsWith("```")) {
        return <pre key={idx} className="p-3 bg-zinc-900 rounded-lg text-xs font-mono text-cyan-300 my-2 overflow-x-auto border border-zinc-800">{line.replace(/```[a-z]*/g, "")}</pre>;
      }
      if (!line.trim()) return <div key={idx} className="h-2" />;

      return <p key={idx} className="text-xs text-zinc-300 leading-relaxed my-1">{line}</p>;
    });
  };

  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-950/90 overflow-hidden shadow-xl space-y-0">
      {/* Editor Toolbar */}
      <div className="p-3 bg-zinc-900/60 border-b border-zinc-800 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => insertFormatting("**", "**")}
            title="Bold"
            className="p-1.5 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors text-xs"
          >
            <Bold className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={() => insertFormatting("*", "*")}
            title="Italic"
            className="p-1.5 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors text-xs"
          >
            <Italic className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={() => insertFormatting("### ")}
            title="Heading"
            className="p-1.5 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors text-xs"
          >
            <Heading className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={() => insertFormatting("- ")}
            title="Bullet List"
            className="p-1.5 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors text-xs"
          >
            <List className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={() => insertFormatting("```python\n", "\n```")}
            title="Code Block"
            className="p-1.5 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors text-xs"
          >
            <Code className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Save Status & View Mode */}
        <div className="flex items-center gap-3">
          {saveStatus === "saving" && (
            <span className="text-[11px] font-mono text-amber-400 flex items-center gap-1.5 animate-pulse">
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
              <span>Saving...</span>
            </span>
          )}
          {saveStatus === "saved" && (
            <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
              <span>✓ Saved</span>
            </span>
          )}

          <div className="flex items-center gap-1 bg-zinc-900 p-1 rounded-xl border border-zinc-800">
            <button
              type="button"
              onClick={() => setIsPreview(false)}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                !isPreview ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30" : "text-zinc-400 hover:text-white"
              }`}
            >
              <Edit3 className="w-3 h-3" />
              <span>Edit</span>
            </button>

            <button
              type="button"
              onClick={() => setIsPreview(true)}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                isPreview ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30" : "text-zinc-400 hover:text-white"
              }`}
            >
              <Eye className="w-3 h-3" />
              <span>Preview</span>
            </button>
          </div>

          {onDeleteNote && (
            <button
              type="button"
              onClick={onDeleteNote}
              title="Delete Note"
              className="p-1.5 rounded-lg hover:bg-rose-500/20 text-zinc-500 hover:text-rose-400 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Editor Body */}
      <div className="p-4 min-h-[220px]">
        {isPreview ? (
          <div className="prose prose-invert max-w-none text-xs font-sans leading-relaxed">
            {renderSimpleMarkdown(value)}
          </div>
        ) : (
          <textarea
            id="lesson-markdown-textarea"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            disabled={readOnly}
            placeholder="Write your lesson notes in Markdown here... (e.g. ## Key Invariant, ```cpp code```, - point 1)"
            className="w-full min-h-[220px] bg-transparent text-xs text-zinc-200 placeholder:text-zinc-600 font-mono leading-relaxed focus:outline-none resize-y"
          />
        )}
      </div>
    </div>
  );
}
