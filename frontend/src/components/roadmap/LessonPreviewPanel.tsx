import React from "react";
import Link from "next/link";
import {
  Video,
  Play,
  Clock,
  Zap,
  CheckCircle2,
  Lock,
  ChevronRight,
  Sparkles,
  BookOpen,
  HelpCircle
} from "lucide-react";

export interface PreviewLessonData {
  id: string;
  title: string;
  slug: string;
  description?: string;
  stepTitle?: string;
  sectionTitle?: string;
  duration?: number;
  xpReward?: number;
  difficulty?: string;
  youtubeVideoId?: string;
  youtubeUrl?: string;
  thumbnailUrl?: string;
  isCompleted?: boolean;
  isLocked?: boolean;
  status?: string;
}

interface LessonPreviewPanelProps {
  lesson: PreviewLessonData | null;
  onClose?: () => void;
}

export function LessonPreviewPanel({ lesson }: LessonPreviewPanelProps) {
  if (!lesson) {
    return (
      <div className="sticky top-20 bg-slate-900/80 border border-slate-800/80 rounded-xl p-8 text-center text-slate-500 space-y-3 flex flex-col items-center justify-center min-h-[420px] shadow-xl">
        <div className="w-14 h-14 rounded-full bg-slate-950 border border-slate-800 flex items-center justify-center">
          <BookOpen className="w-6 h-6 text-slate-600" />
        </div>
        <h3 className="text-sm font-bold text-slate-300">Select Any Lesson</h3>
        <p className="text-xs max-w-xs text-slate-500 leading-relaxed">
          Hover or click on any lesson in the curriculum roadmap to preview its video stream, estimated duration, XP rewards, and prerequisites.
        </p>
      </div>
    );
  }

  const getDifficultyBadge = (diff?: string) => {
    if (!diff) return "text-slate-400 bg-slate-900 border-slate-800";
    switch (diff.toLowerCase()) {
      case "easy":
        return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
      case "medium":
        return "text-amber-400 bg-amber-500/10 border-amber-500/20";
      case "hard":
        return "text-rose-400 bg-rose-500/10 border-rose-500/20";
      default:
        return "text-slate-400 bg-slate-900 border-slate-800";
    }
  };

  const videoId = lesson.youtubeVideoId;
  const thumbUrl = lesson.thumbnailUrl || (videoId ? `https://img.youtube.com/vi/${videoId}/hqdefault.jpg` : null);

  return (
    <div className="sticky top-20 bg-slate-900/90 border border-slate-800/80 rounded-xl p-5 space-y-5 shadow-2xl backdrop-blur-md">
      {/* Header Info */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-cyan-400 bg-cyan-500/10 border border-cyan-500/20 px-2 py-0.5 rounded">
            LESSON PREVIEW
          </span>

          <span
            className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded border ${getDifficultyBadge(
              lesson.difficulty
            )}`}
          >
            {lesson.difficulty || "Easy"}
          </span>
        </div>

        <h3 className="text-lg font-extrabold text-white tracking-tight leading-snug">
          {lesson.title}
        </h3>

        {/* Parent Breadcrumb Path */}
        {(lesson.stepTitle || lesson.sectionTitle) && (
          <p className="text-xs text-slate-400 font-medium truncate">
            {lesson.stepTitle} {lesson.sectionTitle && `> ${lesson.sectionTitle}`}
          </p>
        )}
      </div>

      {/* Video Thumbnail Preview */}
      <div className="relative aspect-video w-full rounded-xl bg-slate-950 border border-slate-800 overflow-hidden group shadow-lg">
        {thumbUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={thumbUrl}
            alt={lesson.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center text-slate-600 space-y-2">
            <Video className="w-8 h-8" />
            <span className="text-xs font-semibold">Video Tutorial Available</span>
          </div>
        )}

        <div className="absolute inset-0 bg-slate-950/40 group-hover:bg-slate-950/20 transition-all flex items-center justify-center">
          <div className="w-12 h-12 rounded-full bg-cyan-500/90 text-slate-950 flex items-center justify-center shadow-xl shadow-cyan-500/30 group-hover:scale-110 transition-transform">
            <Play className="w-5 h-5 fill-slate-950 ml-0.5" />
          </div>
        </div>
      </div>

      {/* Description */}
      {lesson.description && (
        <p className="text-xs text-slate-400 leading-relaxed line-clamp-3">
          {lesson.description}
        </p>
      )}

      {/* Metrics Row */}
      <div className="grid grid-cols-3 gap-2 bg-slate-950/60 p-3 rounded-lg border border-slate-800/80 text-xs">
        <div>
          <span className="text-slate-500 block text-[10px] font-semibold uppercase">Duration</span>
          <div className="flex items-center space-x-1 text-slate-200 font-bold mt-0.5">
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            <span>{lesson.duration || 15}m</span>
          </div>
        </div>

        <div>
          <span className="text-slate-500 block text-[10px] font-semibold uppercase">Reward</span>
          <div className="flex items-center space-x-1 text-amber-400 font-bold mt-0.5">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span>+{lesson.xpReward || 50} XP</span>
          </div>
        </div>

        <div>
          <span className="text-slate-500 block text-[10px] font-semibold uppercase">Status</span>
          <div className="flex items-center space-x-1 font-bold mt-0.5">
            {lesson.isCompleted ? (
              <span className="text-emerald-400 flex items-center space-x-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Done</span>
              </span>
            ) : lesson.isLocked ? (
              <span className="text-slate-500 flex items-center space-x-1">
                <Lock className="w-3.5 h-3.5" />
                <span>Locked</span>
              </span>
            ) : (
              <span className="text-cyan-400 flex items-center space-x-1">
                <Play className="w-3 h-3 fill-cyan-400" />
                <span>Ready</span>
              </span>
            )}
          </div>
        </div>
      </div>

      {/* CTA Button */}
      {lesson.isLocked ? (
        <button
          disabled
          className="w-full py-2.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-600 font-bold text-xs uppercase tracking-wider flex items-center justify-center space-x-2 opacity-60 cursor-not-allowed"
        >
          <Lock className="w-4 h-4" />
          <span>Locked Lesson</span>
        </button>
      ) : (
        <Link href={`/roadmap/node/${lesson.id}`} className="block">
          <button className="w-full py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-slate-950 font-extrabold text-xs uppercase tracking-wider flex items-center justify-center space-x-2 shadow-lg shadow-cyan-500/20 transition-all cursor-pointer">
            <Play className="w-4 h-4 fill-slate-950" />
            <span>Start Lesson Video</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </Link>
      )}
    </div>
  );
}
