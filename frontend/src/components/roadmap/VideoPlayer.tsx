"use client";

import { useState } from "react";
import { Play, VideoOff, Loader2, Video } from "lucide-react";

interface VideoPlayerProps {
  youtubeUrl?: string | null;
  videoId?: string | null;
  thumbnailUrl?: string | null;
  title: string;
  source?: string | null;
}

export function extractYoutubeId(url?: string | null): string | null {
  if (!url) return null;
  
  const shortMatch = url.match(/youtu\.be\/([a-zA-Z0-9_-]{11})/);
  if (shortMatch) return shortMatch[1];
  
  const watchMatch = url.match(/[?&]v=([a-zA-Z0-9_-]{11})/);
  if (watchMatch) return watchMatch[1];
  
  const embedMatch = url.match(/youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/);
  if (embedMatch) return embedMatch[1];
  
  console.warn("[VideoPlayer] Failed to extract YouTube video ID from URL:", url);
  return null;
}

export function VideoPlayer({ youtubeUrl, videoId, thumbnailUrl, title, source = "TakeUForward" }: VideoPlayerProps) {
  const [loading, setLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  const activeVideoId = videoId || extractYoutubeId(youtubeUrl);
  const embedUrl = activeVideoId ? `https://www.youtube-nocookie.com/embed/${activeVideoId}?autoplay=0&rel=0&modestbranding=1` : null;

  // Developer Debug Logs
  console.log("[Developer Debug] Roadmap node title:", title);
  console.log("[Developer Debug] youtube_url received:", youtubeUrl);
  console.log("[Developer Debug] Extracted video ID:", activeVideoId);
  console.log("[Developer Debug] Final embed URL:", embedUrl);

  if (!embedUrl || hasError) {
    return (
      <div className="w-full aspect-video rounded-2xl bg-zinc-950/80 border border-zinc-800 flex flex-col items-center justify-center p-6 text-center space-y-3 shadow-2xl">
        <div className="p-4 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-500">
          <VideoOff className="w-8 h-8" />
        </div>
        <div>
          <h4 className="text-sm font-bold text-zinc-300">No Video Assigned</h4>
          <p className="text-xs text-muted-foreground max-w-md mt-1">
            No video has been assigned to this roadmap node.
          </p>
        </div>
        {youtubeUrl && (
          <a
            href={youtubeUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs font-mono text-primary hover:underline pt-2"
          >
            <Play className="w-3 h-3 fill-primary" />
            <span>Open Link in YouTube</span>
          </a>
        )}
      </div>
    );
  }

  return (
    <div className="relative w-full aspect-video rounded-2xl overflow-hidden bg-black border border-card-border shadow-2xl group">
      {/* Source Badge */}
      <div className="absolute top-3 right-3 z-20 pointer-events-none opacity-80 group-hover:opacity-100 transition-opacity">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-950/80 border border-red-500/30 text-red-400 font-mono text-[10px] uppercase font-bold backdrop-blur-md shadow-lg">
          <Video className="w-3.5 h-3.5 text-red-500" />
          <span>{source || "TakeUForward"}</span>
        </div>
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 z-10 bg-zinc-950 flex flex-col items-center justify-center gap-3">
          {thumbnailUrl ? (
            <div 
              className="absolute inset-0 bg-cover bg-center opacity-30 blur-sm"
              style={{ backgroundImage: `url(${thumbnailUrl})` }}
            />
          ) : null}
          <div className="relative z-20 flex flex-col items-center gap-2">
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
            <span className="text-xs font-mono text-muted-foreground uppercase tracking-widest">LOADING VIDEO PLAYER...</span>
          </div>
        </div>
      )}

      {/* Embedded Iframe */}
      <iframe
        src={embedUrl}
        title={title}
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowFullScreen
        onLoad={() => setLoading(false)}
        onError={() => setHasError(true)}
        className="w-full h-full border-0 rounded-2xl"
      />
    </div>
  );
}
