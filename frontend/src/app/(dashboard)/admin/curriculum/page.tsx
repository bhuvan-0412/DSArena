"use client";

// Prevent static generation — this page is authenticated and requires live backend data
export const dynamic = "force-dynamic";

import React, { useState, useEffect, useMemo } from "react";
import {
  Layers,
  FolderTree,
  BookOpen,
  FileCode,
  Video,
  Percent,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Search,
  Filter,
  Download,
  ChevronRight,
  ChevronDown,
  ExternalLink,
  Play,
  ArrowLeft,
  ArrowRight,
  RefreshCw,
  Info,
  Clock,
  Tag,
  ShieldCheck
} from "lucide-react";
import { BACKEND_URL } from "@/lib/api-config";


interface SummaryData {
  total_steps: number;
  total_sections: number;
  total_topics: number;
  total_lessons: number;
  total_videos: number;
  video_coverage_pct: number;
  curriculum_version: string;
  last_import_date: string;
  validation_status: "PASS" | "FAIL";
  passed_lessons_count: number;
  failed_lessons_count: number;
}

interface TreeNode {
  id: string;
  title: string;
  slug: string;
  type: "step" | "section" | "topic" | "lesson" | "problem";
  order_index: number;
  youtube_video_id?: string;
  youtube_url?: string;
  thumbnail_url?: string;
  children: TreeNode[];
  validation_status: "PASS" | "FAIL";
  failed_checks_count: number;
}

interface ValidationCheck {
  key: string;
  name: string;
  passed: boolean;
  details?: string;
}

interface ParentAncestor {
  id: string;
  title: string;
  type: string;
}

interface LessonNavigationItem {
  id: string;
  title: string;
  slug: string;
}

interface LessonDetail {
  id: string;
  title: string;
  slug: string;
  type: string;
  parent_id?: string;
  parent_hierarchy: ParentAncestor[];
  order_index: number;
  estimated_duration: number;
  youtube_url?: string;
  video_id?: string;
  thumbnail?: string;
  embedded_video_url?: string;
  prev_lesson?: LessonNavigationItem;
  next_lesson?: LessonNavigationItem;
  metadata_completeness: number;
  validation_status: "PASS" | "FAIL";
  validation_checks: ValidationCheck[];
}

export default function CurriculumVerificationDashboard() {
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [tree, setTree] = useState<TreeNode[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedLesson, setSelectedLesson] = useState<LessonDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingLesson, setLoadingLesson] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Expanded nodes map
  const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>({});

  // Search & Filter state
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedStepFilter, setSelectedStepFilter] = useState("ALL");
  const [selectedSectionFilter, setSelectedSectionFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [issueFilter, setIssueFilter] = useState("ALL");

  // Fetch initial summary & tree data
  useEffect(() => {
    fetchDashboardData();
  }, []);

  async function fetchDashboardData() {
    try {
      setLoading(true);
      setError(null);
      
      const [sumRes, treeRes] = await Promise.all([
        fetch(`${BACKEND_URL}/admin/curriculum/summary`),
        fetch(`${BACKEND_URL}/admin/curriculum/tree`)
      ]);

      if (!sumRes.ok || !treeRes.ok) {
        throw new Error("Failed to load curriculum data from backend");
      }

      const sumData: SummaryData = await sumRes.json();
      const treeData: TreeNode[] = await treeRes.json();

      setSummary(sumData);
      setTree(treeData);

      // Auto-expand first Step and Section for convenient viewing
      if (treeData.length > 0) {
        const initialExpand: Record<string, boolean> = {};
        treeData.forEach((step) => {
          initialExpand[step.id] = true;
          if (step.children && step.children.length > 0) {
            initialExpand[step.children[0].id] = true;
          }
        });
        setExpandedNodes(initialExpand);

        // Auto-select first lesson in Step 1
        const firstStep = treeData[0];
        if (firstStep && firstStep.children && firstStep.children[0]) {
          const firstSec = firstStep.children[0];
          if (firstSec.children && firstSec.children[0]) {
            const firstTopic = firstSec.children[0];
            setSelectedNodeId(firstTopic.id);
            fetchLessonDetail(firstTopic.id);
          }
        }
      }
    } catch (err: unknown) {
      console.error("Dashboard load error:", err);
      setError(err instanceof Error ? err.message : "Could not connect to backend server at http://127.0.0.1:8000");
    } finally {
      setLoading(false);
    }
  }

  async function fetchLessonDetail(id: string) {
    try {
      setLoadingLesson(true);
      const res = await fetch(`${BACKEND_URL}/admin/curriculum/lesson/${id}`);
      if (res.ok) {
        const data: LessonDetail = await res.json();
        setSelectedLesson(data);
      } else {
        setSelectedLesson(null);
      }
    } catch (err) {
      console.error("Lesson detail error:", err);
      setSelectedLesson(null);
    } finally {
      setLoadingLesson(false);
    }
  }

  function handleSelectNode(node: TreeNode) {
    setSelectedNodeId(node.id);
    fetchLessonDetail(node.id);
  }

  function toggleNodeExpand(id: string, e: React.MouseEvent) {
    e.stopPropagation();
    setExpandedNodes((prev) => ({
      ...prev,
      [id]: !prev[id]
    }));
  }

  function expandAll() {
    const allIds: Record<string, boolean> = {};
    function traverse(nodes: TreeNode[]) {
      nodes.forEach((n) => {
        allIds[n.id] = true;
        if (n.children && n.children.length > 0) {
          traverse(n.children);
        }
      });
    }
    traverse(tree);
    setExpandedNodes(allIds);
  }

  function collapseAll() {
    setExpandedNodes({});
  }

  function handleExport(format: "markdown" | "json" | "csv") {
    window.open(`${BACKEND_URL}/admin/curriculum/export?format=${format}`, "_blank");
  }

  // Filtered Tree Computation
  const filteredTree = useMemo(() => {
    if (!searchQuery && selectedStepFilter === "ALL" && selectedSectionFilter === "ALL" && statusFilter === "ALL" && issueFilter === "ALL") {
      return tree;
    }

    const query = searchQuery.toLowerCase().trim();

    function filterNode(node: TreeNode): TreeNode | null {
      // Check Step filter
      if (node.type === "step" && selectedStepFilter !== "ALL" && node.id !== selectedStepFilter) {
        return null;
      }
      // Check Section filter
      if (node.type === "section" && selectedSectionFilter !== "ALL" && node.id !== selectedSectionFilter) {
        return null;
      }

      // Filter children first
      const matchingChildren: TreeNode[] = [];
      if (node.children) {
        node.children.forEach((c) => {
          const fc = filterNode(c);
          if (fc) matchingChildren.push(fc);
        });
      }

      // Check self match
      const selfTitleMatch = query ? node.title.toLowerCase().includes(query) || node.slug.toLowerCase().includes(query) || node.id.toLowerCase().includes(query) : true;
      const selfStatusMatch = statusFilter === "ALL" ? true : node.validation_status === statusFilter;
      
      let selfIssueMatch = true;
      if (issueFilter === "MISSING_VIDEO") {
        selfIssueMatch = (node.type === "topic" || node.type === "lesson" || node.type === "problem") && !node.youtube_video_id;
      } else if (issueFilter === "MISSING_THUMB") {
        selfIssueMatch = Boolean(node.youtube_video_id && !node.thumbnail_url);
      } else if (issueFilter === "FAILED_VAL") {
        selfIssueMatch = node.validation_status === "FAIL";
      }

      const selfMatches = selfTitleMatch && selfStatusMatch && selfIssueMatch;

      if (selfMatches || matchingChildren.length > 0) {
        return {
          ...node,
          children: matchingChildren
        };
      }

      return null;
    }

    return tree.map(filterNode).filter(Boolean) as TreeNode[];
  }, [tree, searchQuery, selectedStepFilter, selectedSectionFilter, statusFilter, issueFilter]);

  // Section options based on selected step
  const sectionOptions = useMemo(() => {
    if (selectedStepFilter === "ALL") {
      return tree.flatMap((s) => s.children || []);
    }
    const step = tree.find((s) => s.id === selectedStepFilter);
    return step ? step.children || [] : [];
  }, [tree, selectedStepFilter]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[600px] space-y-4">
        <RefreshCw className="w-10 h-10 text-cyan-400 animate-spin" />
        <p className="text-slate-400 font-medium text-sm">Building Curriculum Tree & Running Audit Suite...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-rose-950/40 border border-rose-800/80 rounded-xl p-8 max-w-2xl mx-auto my-12 text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-rose-400 mx-auto" />
        <h2 className="text-xl font-bold text-white">Curriculum Verification Connection Error</h2>
        <p className="text-slate-300 text-sm">{error}</p>
        <button
          onClick={fetchDashboardData}
          className="inline-flex items-center space-x-2 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white font-semibold rounded-lg text-sm transition-all"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Retry Connection</span>
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 1. OVERVIEW SUMMARY CARDS */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-9 gap-3">
        {/* Total Steps */}
        <div className="bg-slate-900/90 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Steps</span>
            <Layers className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-extrabold text-white tracking-tight">{summary?.total_steps}</div>
          <span className="text-[10px] text-slate-500 font-medium">Curriculum Steps</span>
        </div>

        {/* Total Sections */}
        <div className="bg-slate-900/90 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Sections</span>
            <FolderTree className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-extrabold text-white tracking-tight">{summary?.total_sections}</div>
          <span className="text-[10px] text-slate-500 font-medium">Sub-Sections</span>
        </div>

        {/* Total Topics */}
        <div className="bg-slate-900/90 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Topics</span>
            <BookOpen className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-extrabold text-white tracking-tight">{summary?.total_topics}</div>
          <span className="text-[10px] text-slate-500 font-medium">Core Modules</span>
        </div>

        {/* Total Lessons */}
        <div className="bg-slate-900/90 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Lessons</span>
            <FileCode className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-extrabold text-white tracking-tight">{summary?.total_lessons}</div>
          <span className="text-[10px] text-slate-500 font-medium">Total Lesson Nodes</span>
        </div>

        {/* Total Videos */}
        <div className="bg-slate-900/90 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Videos</span>
            <Video className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-extrabold text-white tracking-tight">{summary?.total_videos}</div>
          <span className="text-[10px] text-slate-500 font-medium">Linked Videos</span>
        </div>

        {/* Video Coverage % */}
        <div className="bg-slate-900/90 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Coverage</span>
            <Percent className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-extrabold text-cyan-400 tracking-tight">{summary?.video_coverage_pct}%</div>
          <span className="text-[10px] text-slate-500 font-medium">Video Completeness</span>
        </div>

        {/* Version */}
        <div className="bg-slate-900/90 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Version</span>
            <Tag className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-sm font-bold text-white truncate" title={summary?.curriculum_version}>
            {summary?.curriculum_version}
          </div>
          <span className="text-[10px] text-slate-500 font-medium">Excel Catalog</span>
        </div>

        {/* Last Import Date */}
        <div className="bg-slate-900/90 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between shadow-md">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Imported</span>
            <Calendar className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-xs font-bold text-white truncate" title={summary?.last_import_date}>
            {summary?.last_import_date}
          </div>
          <span className="text-[10px] text-slate-500 font-medium">Last Sync</span>
        </div>

        {/* Validation Status */}
        <div
          className={`border rounded-xl p-3.5 flex flex-col justify-between shadow-md ${
            summary?.validation_status === "PASS"
              ? "bg-emerald-950/40 border-emerald-800/80 text-emerald-300"
              : "bg-amber-950/40 border-amber-800/80 text-amber-300"
          }`}
        >
          <div className="flex items-center justify-between mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Audit Health</span>
            {summary?.validation_status === "PASS" ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-amber-400" />
            )}
          </div>
          <div className="flex items-baseline space-x-1.5">
            <span className="text-xl font-extrabold tracking-tight">
              {summary?.validation_status === "PASS" ? "HEALTHY" : "NEEDS REVIEW"}
            </span>
          </div>
          <span className="text-[10px] font-medium opacity-80">
            {summary?.passed_lessons_count} Passed / {summary?.failed_lessons_count} Issues
          </span>
        </div>
      </div>

      {/* 2. SEARCH, FILTER & EXPORT CONTROL BAR */}
      <div className="bg-slate-900/80 border border-slate-800/80 rounded-xl p-4 flex flex-col lg:flex-row lg:items-center justify-between gap-4 shadow-lg">
        {/* Search & Filters */}
        <div className="flex flex-wrap items-center gap-3 flex-1">
          {/* Search Input */}
          <div className="relative flex-1 min-w-[240px]">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search steps, sections, topics, lessons by title or slug..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-all"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 text-xs font-bold"
              >
                ×
              </button>
            )}
          </div>

          {/* Filter: Step */}
          <select
            value={selectedStepFilter}
            onChange={(e) => {
              setSelectedStepFilter(e.target.value);
              setSelectedSectionFilter("ALL");
            }}
            className="bg-slate-950 border border-slate-800 text-slate-300 rounded-lg text-xs px-3 py-2 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Steps (18 Steps)</option>
            {tree.map((step) => (
              <option key={step.id} value={step.id}>
                {step.title}
              </option>
            ))}
          </select>

          {/* Filter: Section */}
          <select
            value={selectedSectionFilter}
            onChange={(e) => setSelectedSectionFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-slate-300 rounded-lg text-xs px-3 py-2 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Sections</option>
            {sectionOptions.map((sec) => (
              <option key={sec.id} value={sec.id}>
                {sec.title}
              </option>
            ))}
          </select>

          {/* Filter: Status */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-slate-300 rounded-lg text-xs px-3 py-2 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Validation Statuses</option>
            <option value="PASS">✓ Passed Validation Only</option>
            <option value="FAIL">✗ Failed Validation Only</option>
          </select>

          {/* Filter: Specific Issues */}
          <select
            value={issueFilter}
            onChange={(e) => setIssueFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-slate-300 rounded-lg text-xs px-3 py-2 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Specific Issues</option>
            <option value="MISSING_VIDEO">Missing Video</option>
            <option value="MISSING_THUMB">Missing Thumbnail</option>
            <option value="FAILED_VAL">Validation Failures</option>
          </select>
        </div>

        {/* Exports Dropdown & Buttons */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => handleExport("markdown")}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 text-xs font-semibold transition-all"
            title="Download Audit Report in Markdown format"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" />
            <span>Audit Report (.md)</span>
          </button>

          <button
            onClick={() => handleExport("json")}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 text-xs font-semibold transition-all"
            title="Download Validation Suite Report in JSON format"
          >
            <Download className="w-3.5 h-3.5 text-emerald-400" />
            <span>Validation (.json)</span>
          </button>

          <button
            onClick={() => handleExport("csv")}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold transition-all shadow-md shadow-cyan-600/20"
            title="Export all lessons to CSV spreadsheet"
          >
            <Download className="w-3.5 h-3.5 text-white" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* 3. MAIN SPLIT WORKSPACE: TREE VIEW + LESSON INSPECTOR */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* LEFT COLUMN: INTERACTIVE TREE VIEW (5 Columns) */}
        <div className="lg:col-span-5 bg-slate-900/80 border border-slate-800/80 rounded-xl flex flex-col h-[760px] shadow-xl overflow-hidden">
          {/* Tree Header */}
          <div className="px-4 py-3 border-b border-slate-800/80 flex items-center justify-between bg-slate-950/60">
            <div className="flex items-center space-x-2">
              <FolderTree className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-white tracking-tight">Curriculum Hierarchy Tree</h3>
            </div>
            <div className="flex items-center space-x-2 text-xs">
              <button
                onClick={expandAll}
                className="px-2 py-1 bg-slate-950 border border-slate-800 rounded text-slate-400 hover:text-white text-[11px]"
              >
                Expand All
              </button>
              <button
                onClick={collapseAll}
                className="px-2 py-1 bg-slate-950 border border-slate-800 rounded text-slate-400 hover:text-white text-[11px]"
              >
                Collapse All
              </button>
            </div>
          </div>

          {/* Tree Scroll Container */}
          <div className="flex-1 overflow-y-auto p-3 space-y-1 text-xs">
            {filteredTree.length === 0 ? (
              <div className="p-8 text-center text-slate-500 space-y-2">
                <Info className="w-8 h-8 mx-auto text-slate-600" />
                <p>No curriculum nodes match the selected filters.</p>
              </div>
            ) : (
              filteredTree.map((node) => (
                <TreeNodeItem
                  key={node.id}
                  node={node}
                  selectedNodeId={selectedNodeId}
                  expandedNodes={expandedNodes}
                  onSelect={handleSelectNode}
                  onToggleExpand={toggleNodeExpand}
                  level={0}
                />
              ))
            )}
          </div>
        </div>

        {/* RIGHT COLUMN: LESSON DETAILS & VALIDATION INSPECTOR (7 Columns) */}
        <div className="lg:col-span-7 bg-slate-900/80 border border-slate-800/80 rounded-xl h-[760px] flex flex-col shadow-xl overflow-hidden">
          {loadingLesson ? (
            <div className="flex-1 flex flex-col items-center justify-center space-y-3">
              <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
              <p className="text-xs text-slate-400 font-medium">Loading Lesson Details & Video Preview...</p>
            </div>
          ) : selectedLesson ? (
            <div className="flex-1 overflow-y-auto p-5 space-y-6">
              {/* Header & Hierarchy Breadcrumb */}
              <div className="border-b border-slate-800/80 pb-4 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono text-[10px] uppercase font-bold">
                      {selectedLesson.type}
                    </span>
                    <span className="font-mono text-xs text-slate-400">ID: {selectedLesson.id}</span>
                  </div>

                  <div className="flex items-center space-x-2">
                    {selectedLesson.validation_status === "PASS" ? (
                      <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-xs">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>PASSED AUDIT</span>
                      </span>
                    ) : (
                      <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-rose-500/10 border border-rose-500/30 text-rose-400 font-bold text-xs">
                        <XCircle className="w-3.5 h-3.5" />
                        <span>ISSUES DETECTED</span>
                      </span>
                    )}
                  </div>
                </div>

                <h2 className="text-xl font-extrabold text-white tracking-tight leading-snug">
                  {selectedLesson.title}
                </h2>

                {/* Parent Hierarchy Breadcrumb */}
                <div className="flex items-center flex-wrap gap-1.5 text-xs text-slate-400 font-medium">
                  {selectedLesson.parent_hierarchy.map((ancestor, idx) => (
                    <React.Fragment key={ancestor.id}>
                      <span className="hover:text-slate-200">{ancestor.title}</span>
                      {idx < selectedLesson.parent_hierarchy.length - 1 && (
                        <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>

              {/* Prev / Next Navigation Buttons & Quick Stats */}
              <div className="grid grid-cols-2 gap-3">
                {selectedLesson.prev_lesson ? (
                  <button
                    onClick={() => handleSelectNode({ id: selectedLesson.prev_lesson!.id } as TreeNode)}
                    className="flex items-center space-x-2 p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-left hover:border-slate-700 transition-all text-xs group"
                  >
                    <ArrowLeft className="w-4 h-4 text-cyan-400 group-hover:-translate-x-0.5 transition-transform" />
                    <div className="truncate">
                      <div className="text-[10px] text-slate-500 uppercase font-semibold">Previous Lesson</div>
                      <div className="text-slate-200 font-semibold truncate">{selectedLesson.prev_lesson.title}</div>
                    </div>
                  </button>
                ) : (
                  <div className="p-2.5 rounded-lg bg-slate-950/40 border border-slate-900 text-slate-600 text-xs flex items-center space-x-2 opacity-50">
                    <ArrowLeft className="w-4 h-4" />
                    <span>First Lesson in Roadmap</span>
                  </div>
                )}

                {selectedLesson.next_lesson ? (
                  <button
                    onClick={() => handleSelectNode({ id: selectedLesson.next_lesson!.id } as TreeNode)}
                    className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-right hover:border-slate-700 transition-all text-xs group"
                  >
                    <div className="truncate">
                      <div className="text-[10px] text-slate-500 uppercase font-semibold">Next Lesson</div>
                      <div className="text-slate-200 font-semibold truncate">{selectedLesson.next_lesson.title}</div>
                    </div>
                    <ArrowRight className="w-4 h-4 text-cyan-400 group-hover:translate-x-0.5 transition-transform ml-2" />
                  </button>
                ) : (
                  <div className="p-2.5 rounded-lg bg-slate-950/40 border border-slate-900 text-slate-600 text-xs flex items-center justify-end space-x-2 opacity-50">
                    <span>Last Lesson in Roadmap</span>
                    <ArrowRight className="w-4 h-4" />
                  </div>
                )}
              </div>

              {/* Lesson Metadata Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80 text-xs">
                <div>
                  <span className="text-slate-500 block text-[10px] font-semibold uppercase">Order Index</span>
                  <span className="text-slate-200 font-bold">#{selectedLesson.order_index}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] font-semibold uppercase">Duration</span>
                  <span className="text-slate-200 font-bold">{selectedLesson.estimated_duration} mins</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] font-semibold uppercase">Video ID</span>
                  <span className="text-cyan-400 font-mono font-bold truncate block" title={selectedLesson.video_id}>
                    {selectedLesson.video_id || "N/A"}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] font-semibold uppercase">Completeness</span>
                  <div className="flex items-center space-x-2 mt-0.5">
                    <div className="flex-1 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-cyan-500 h-full rounded-full transition-all"
                        style={{ width: `${selectedLesson.metadata_completeness}%` }}
                      />
                    </div>
                    <span className="text-slate-200 font-bold text-[11px]">{selectedLesson.metadata_completeness}%</span>
                  </div>
                </div>
              </div>

              {/* Video Player & YouTube Link */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-200 flex items-center space-x-1.5">
                    <Video className="w-4 h-4 text-rose-400" />
                    <span>Embedded YouTube Video Preview</span>
                  </span>
                  {selectedLesson.youtube_url && (
                    <a
                      href={selectedLesson.youtube_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 font-semibold text-[11px]"
                    >
                      <span>Open YouTube</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>

                {selectedLesson.video_id ? (
                  <div className="aspect-video w-full rounded-xl bg-black border border-slate-800 overflow-hidden shadow-2xl relative">
                    <iframe
                      src={`https://www.youtube-nocookie.com/embed/${selectedLesson.video_id}`}
                      title={selectedLesson.title}
                      className="w-full h-full border-0"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                    />
                  </div>
                ) : (
                  <div className="aspect-video w-full rounded-xl bg-slate-950 border border-dashed border-slate-800 flex flex-col items-center justify-center text-slate-500 space-y-2">
                    <AlertTriangle className="w-8 h-8 text-amber-500" />
                    <p className="text-xs font-semibold">No YouTube video URL associated with this lesson</p>
                  </div>
                )}
              </div>

              {/* Automated Validation Checklist */}
              <div className="space-y-3 pt-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                    <ShieldCheck className="w-4 h-4 text-cyan-400" />
                    <span>Automated Health & Integrity Checks</span>
                  </h3>
                  <span className="text-xs text-slate-400">
                    {selectedLesson.validation_checks.filter((c) => c.passed).length} / {selectedLesson.validation_checks.length} Passed
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  {selectedLesson.validation_checks.map((check) => (
                    <div
                      key={check.key}
                      className={`p-2.5 rounded-lg border flex items-start space-x-2.5 transition-all ${
                        check.passed
                          ? "bg-slate-950/60 border-slate-800/80 text-slate-300"
                          : "bg-rose-950/30 border-rose-800/80 text-rose-200"
                      }`}
                    >
                      {check.passed ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      ) : (
                        <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                      )}
                      <div className="flex-1">
                        <div className="font-semibold text-slate-200 flex items-center justify-between">
                          <span>{check.name}</span>
                          <span
                            className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                              check.passed
                                ? "bg-emerald-500/10 text-emerald-400"
                                : "bg-rose-500/20 text-rose-300"
                            }`}
                          >
                            {check.passed ? "PASS" : "FAIL"}
                          </span>
                        </div>
                        {check.details && (
                          <p className="text-[11px] text-rose-300/80 mt-1 font-mono">{check.details}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-slate-500 space-y-3">
              <BookOpen className="w-12 h-12 text-slate-700" />
              <h3 className="text-base font-bold text-slate-400">No Lesson Selected</h3>
              <p className="text-xs max-w-sm">
                Select any step, section, or topic node from the curriculum tree on the left to inspect its complete metadata, video stream, and health checklist.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// TREE NODE ITEM RECURSIVE COMPONENT
interface TreeNodeItemProps {
  node: TreeNode;
  selectedNodeId: string | null;
  expandedNodes: Record<string, boolean>;
  onSelect: (node: TreeNode) => void;
  onToggleExpand: (id: string, e: React.MouseEvent) => void;
  level: number;
}

function TreeNodeItem({
  node,
  selectedNodeId,
  expandedNodes,
  onSelect,
  onToggleExpand,
  level
}: TreeNodeItemProps) {
  const isExpanded = expandedNodes[node.id];
  const isSelected = selectedNodeId === node.id;
  const hasChildren = node.children && node.children.length > 0;

  // Node type styling badge
  const typeBadges = {
    step: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
    section: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
    topic: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    lesson: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    problem: "bg-purple-500/10 text-purple-400 border-purple-500/20"
  };

  return (
    <div className="select-none">
      <div
        onClick={() => onSelect(node)}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        className={`flex items-center justify-between py-1.5 pr-2 rounded-lg cursor-pointer transition-colors text-xs ${
          isSelected
            ? "bg-cyan-500/20 border border-cyan-500/40 text-cyan-100 font-semibold"
            : "hover:bg-slate-800/60 text-slate-300"
        }`}
      >
        <div className="flex items-center space-x-2 truncate">
          {hasChildren ? (
            <button
              onClick={(e) => onToggleExpand(node.id, e)}
              className="p-0.5 text-slate-500 hover:text-slate-300 rounded"
            >
              {isExpanded ? (
                <ChevronDown className="w-3.5 h-3.5" />
              ) : (
                <ChevronRight className="w-3.5 h-3.5" />
              )}
            </button>
          ) : (
            <div className="w-3.5 h-3.5" />
          )}

          <span
            className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold uppercase border ${
              typeBadges[node.type] || typeBadges.lesson
            }`}
          >
            {node.type}
          </span>

          <span className="truncate">{node.title}</span>
        </div>

        <div className="flex items-center space-x-1.5 shrink-0 ml-2">
          {node.youtube_video_id && (
            <span title="YouTube video attached">
              <Video className="w-3 h-3 text-rose-400" />
            </span>
          )}

          {node.validation_status === "PASS" ? (
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          ) : (
            <span
              className="px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-400 font-bold text-[9px]"
              title={`${node.failed_checks_count} failed checks`}
            >
              {node.failed_checks_count} FAIL
            </span>
          )}
        </div>
      </div>

      {hasChildren && isExpanded && (
        <div className="space-y-0.5">
          {node.children.map((child) => (
            <TreeNodeItem
              key={child.id}
              node={child}
              selectedNodeId={selectedNodeId}
              expandedNodes={expandedNodes}
              onSelect={onSelect}
              onToggleExpand={onToggleExpand}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}
