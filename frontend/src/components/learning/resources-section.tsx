"use client";

import { Video, FileText, BookOpen, ExternalLink, Bookmark, BookmarkCheck, User, Clock, Layers } from "lucide-react";
import { motion } from "framer-motion";

export interface LearningResource {
  id: number;
  node_id: string;
  title: string;
  type: string; // 'Video', 'Article', 'Documentation'
  author?: string;
  duration?: string;
  difficulty?: string;
  url: string;
  order_index: number;
  is_bookmarked?: boolean;
}

interface ResourcesSectionProps {
  resources: LearningResource[];
  onToggleBookmarkResource: (resourceId: number) => void;
}

export function ResourcesSection({ resources, onToggleBookmarkResource }: ResourcesSectionProps) {
  const getResourceIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "video":
        return <Video className="w-4 h-4 text-red-500" />;
      case "article":
        return <FileText className="w-4 h-4 text-info-cyan" />;
      case "documentation":
        return <BookOpen className="w-4 h-4 text-xp-gold" />;
      default:
        return <Layers className="w-4 h-4 text-primary" />;
    }
  };

  const getDifficultyColor = (diff?: string) => {
    if (!diff) return "text-muted-foreground bg-muted";
    switch (diff.toLowerCase()) {
      case "easy":
        return "text-success-emerald bg-success-emerald/10 border-success-emerald/20";
      case "medium":
        return "text-yellow-500 bg-yellow-500/10 border-yellow-500/20";
      case "hard":
        return "text-primary bg-primary/10 border-primary/20";
      default:
        return "text-muted-foreground bg-muted";
    }
  };

  return (
    <motion.div
      id="resources"
      className="border border-card-border rounded-3xl p-6 lg:p-8 glass-card space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      <div className="flex justify-between items-center border-b border-card-border/60 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Video className="w-5 h-5 text-red-500" /> Learning Resources
          </h2>
          <p className="text-xs text-muted-foreground mt-1">
            Curated DB-backed videos, articles, and official documentation to master this concept.
          </p>
        </div>
        <span className="text-xs font-mono font-bold text-muted-foreground px-2.5 py-1 rounded bg-muted border border-card-border">
          {resources.length} AVAILABLE
        </span>
      </div>

      {resources.length === 0 ? (
        <div className="text-center py-8 text-xs text-muted-foreground">
          No resources currently available for this topic.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {resources.map((res) => (
            <div
              key={res.id}
              className="p-5 rounded-2xl border border-card-border bg-[#030303]/50 hover:border-primary/40 transition-all duration-300 flex flex-col justify-between gap-4 group"
            >
              <div className="space-y-3">
                <div className="flex justify-between items-start gap-2">
                  <div className="flex items-center gap-2">
                    <span className="p-2 rounded-xl bg-zinc-950 border border-card-border/60">
                      {getResourceIcon(res.type)}
                    </span>
                    <span className="text-[10px] font-bold uppercase tracking-wider font-mono text-muted-foreground">
                      {res.type}
                    </span>
                  </div>

                  <button
                    onClick={() => onToggleBookmarkResource(res.id)}
                    title={res.is_bookmarked ? "Remove Bookmark" : "Bookmark Resource"}
                    className={`p-2 rounded-xl border text-xs transition-all cursor-pointer ${
                      res.is_bookmarked
                        ? "bg-xp-gold/10 border-xp-gold/30 text-xp-gold"
                        : "border-card-border text-muted-foreground hover:text-white hover:bg-white/[0.04]"
                    }`}
                  >
                    {res.is_bookmarked ? (
                      <BookmarkCheck className="w-4 h-4 fill-xp-gold" />
                    ) : (
                      <Bookmark className="w-4 h-4" />
                    )}
                  </button>
                </div>

                <h3 className="text-sm font-bold text-white group-hover:text-primary transition-colors leading-snug">
                  {res.title}
                </h3>

                <div className="flex flex-wrap items-center gap-3 text-[11px] text-muted-foreground pt-1">
                  {res.author && (
                    <span className="flex items-center gap-1">
                      <User className="w-3 h-3 text-zinc-500" /> {res.author}
                    </span>
                  )}
                  {res.duration && (
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3 text-zinc-500" /> {res.duration}
                    </span>
                  )}
                  {res.difficulty && (
                    <span className={`text-[9px] font-extrabold uppercase px-2 py-0.5 rounded border font-mono ${getDifficultyColor(res.difficulty)}`}>
                      {res.difficulty}
                    </span>
                  )}
                </div>
              </div>

              <a
                href={res.url}
                target="_blank"
                rel="noreferrer"
                className="w-full py-2.5 rounded-xl border border-card-border bg-zinc-950 hover:bg-primary/10 hover:border-primary/40 text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all cursor-pointer"
              >
                <span>Open Resource</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
