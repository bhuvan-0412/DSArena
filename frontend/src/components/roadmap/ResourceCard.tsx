"use client";

import React from "react";
import { BookOpen, FileText, ExternalLink, Code2, Tv, FileCode, Layers, ShieldCheck } from "lucide-react";

export interface ResourceItem {
  id: number;
  node_id: string;
  title: string;
  description?: string | null;
  type: string; // 'Documentation' | 'Articles' | 'Reference Notes' | 'PDFs' | 'Cheat Sheets' | 'GitHub' | 'YouTube'
  url: string;
}

interface ResourceCardProps {
  resources?: ResourceItem[] | null;
}

export function ResourceCard({ resources }: ResourceCardProps) {
  if (!resources || resources.length === 0) {
    return (
      <div className="p-8 rounded-2xl border border-zinc-800 bg-zinc-950/90 text-center space-y-3 shadow-xl">
        <BookOpen className="w-8 h-8 text-zinc-600 mx-auto" />
        <h4 className="text-sm font-bold text-white uppercase">No Resources Linked Yet</h4>
        <p className="text-xs text-zinc-400 max-w-sm mx-auto">
          Supplementary reading materials, documentation, and GitHub repositories will appear here.
        </p>
      </div>
    );
  }

  const getResourceIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "github":
        return <Code2 className="w-4 h-4 text-purple-400" />;
      case "youtube":
      case "video":
        return <Tv className="w-4 h-4 text-rose-400" />;
      case "pdf":
      case "pdfs":
        return <FileText className="w-4 h-4 text-amber-400" />;
      case "cheat sheets":
      case "reference notes":
        return <FileCode className="w-4 h-4 text-cyan-400" />;
      case "documentation":
        return <ShieldCheck className="w-4 h-4 text-emerald-400" />;
      case "articles":
      default:
        return <BookOpen className="w-4 h-4 text-teal-400" />;
    }
  };

  const getBadgeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "github":
        return "bg-purple-500/10 text-purple-400 border-purple-500/30";
      case "youtube":
      case "video":
        return "bg-rose-500/10 text-rose-400 border-rose-500/30";
      case "pdf":
      case "pdfs":
        return "bg-amber-500/10 text-amber-400 border-amber-500/30";
      case "cheat sheets":
      case "reference notes":
        return "bg-cyan-500/10 text-cyan-400 border-cyan-500/30";
      case "documentation":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
      case "articles":
      default:
        return "bg-teal-500/10 text-teal-400 border-teal-500/30";
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-white">
            CURATED LEARNING RESOURCES
          </h4>
        </div>
        <span className="text-[11px] font-mono text-zinc-400">{resources.length} Available</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {resources.map((item) => (
          <a
            key={item.id}
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="group p-4 rounded-2xl border border-zinc-800 bg-zinc-950/90 hover:bg-zinc-900/60 hover:border-zinc-700 transition-all flex flex-col justify-between space-y-3 shadow-xl transform hover:-translate-y-0.5"
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between gap-2">
                <span
                  className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-[11px] font-mono font-bold uppercase ${getBadgeColor(
                    item.type
                  )}`}
                >
                  {getResourceIcon(item.type)}
                  <span>{item.type}</span>
                </span>
                <ExternalLink className="w-3.5 h-3.5 text-zinc-500 group-hover:text-cyan-400 transition-colors shrink-0" />
              </div>

              <h5 className="text-sm font-bold text-white group-hover:text-cyan-300 transition-colors leading-snug">
                {item.title}
              </h5>

              {item.description && (
                <p className="text-xs text-zinc-400 leading-relaxed line-clamp-2">
                  {item.description}
                </p>
              )}
            </div>

            <div className="pt-2 border-t border-zinc-800/60 flex items-center justify-between text-[11px] text-zinc-500 font-mono">
              <span className="truncate max-w-[200px]">{item.url}</span>
              <span className="text-cyan-400 font-bold group-hover:underline">Open Link $\rightarrow$</span>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
