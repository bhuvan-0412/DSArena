import React from "react";
import Link from "next/link";
import { ChevronRight, Home, Compass } from "lucide-react";

interface BreadcrumbItem {
  label: string;
  href?: string;
  type?: "home" | "roadmap" | "step" | "section" | "lesson";
}

interface RoadmapBreadcrumbsProps {
  stepTitle?: string | null;
  sectionTitle?: string | null;
  lessonTitle?: string | null;
  className?: string;
}

export function RoadmapBreadcrumbs({
  stepTitle,
  sectionTitle,
  lessonTitle,
  className = "",
}: RoadmapBreadcrumbsProps) {
  const items: BreadcrumbItem[] = [
    { label: "Home", href: "/", type: "home" },
    { label: "Roadmap", href: "/roadmap", type: "roadmap" },
  ];

  if (stepTitle) {
    items.push({ label: stepTitle, href: "/roadmap", type: "step" });
  }

  if (sectionTitle) {
    items.push({ label: sectionTitle, type: "section" });
  }

  if (lessonTitle) {
    items.push({ label: lessonTitle, type: "lesson" });
  }

  return (
    <nav aria-label="Breadcrumb" className={`flex items-center flex-wrap gap-1.5 text-xs text-slate-400 font-medium ${className}`}>
      {items.map((item, idx) => {
        const isLast = idx === items.length - 1;

        return (
          <React.Fragment key={idx}>
            {idx > 0 && <ChevronRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />}

            {isLast ? (
              <span className="text-cyan-400 font-semibold truncate max-w-[220px] sm:max-w-[320px]" title={item.label}>
                {item.label}
              </span>
            ) : item.href ? (
              <Link
                href={item.href}
                className="hover:text-white flex items-center space-x-1 text-slate-400 transition-colors truncate"
              >
                {item.type === "home" && <Home className="w-3.5 h-3.5 text-slate-400 shrink-0" />}
                {item.type === "roadmap" && <Compass className="w-3.5 h-3.5 text-cyan-400 shrink-0" />}
                <span>{item.label}</span>
              </Link>
            ) : (
              <span className="text-slate-400 truncate max-w-[180px] sm:max-w-[240px]" title={item.label}>
                {item.label}
              </span>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
}
