from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import datetime
import csv
import io
import re

from app.core.database import get_db
from app.models.roadmap import RoadmapNode, RoadmapStep, RoadmapSection, RoadmapTopic, RoadmapLesson, LessonVideo, ImportLog
from app.schemas.admin import (
    CurriculumSummaryResponse, CurriculumTreeNode, LessonDetailResponse,
    ValidationCheck, ParentAncestor, LessonNavigationItem, LessonValidationResult,
    CheckSummaryItem, CurriculumValidationResponse
)

router = APIRouter()

# Validation rule definitions
VALIDATION_RULES = [
    ("missing_title", "Missing Title"),
    ("missing_slug", "Missing Slug"),
    ("missing_parent", "Missing Parent"),
    ("invalid_parent", "Invalid Parent Pointer"),
    ("duplicate_slug", "Duplicate Slug"),
    ("duplicate_title_same_parent", "Duplicate Title Under Same Parent"),
    ("missing_video", "Missing Video"),
    ("invalid_video_id", "Invalid Video ID Format"),
    ("missing_thumbnail", "Missing Video Thumbnail"),
    ("missing_order_index", "Missing Order Index"),
    ("non_sequential_ordering", "Non-Sequential / Duplicate Ordering"),
    ("broken_prev_lesson", "Broken Previous Lesson Link"),
    ("broken_next_lesson", "Broken Next Lesson Link"),
]

def build_curriculum_audit_cache(db: Session):
    """
    Fetch all nodes and compute structural & validation metadata in a single fast pass.
    Avoids N+1 queries.
    """
    all_nodes = db.query(RoadmapNode).all()
    node_map = {n.id: n for n in all_nodes}

    # Group by slug for duplicate detection
    slug_counts = {}
    for n in all_nodes:
        if n.slug:
            slug_counts[n.slug] = slug_counts.get(n.slug, 0) + 1

    # Group by parent for sibling order & duplicate title checks
    children_by_parent = {}
    for n in all_nodes:
        children_by_parent.setdefault(n.parent_id, []).append(n)

    # Sort siblings by order_index
    for pid in children_by_parent:
        children_by_parent[pid].sort(key=lambda x: x.order_index or 0)

    # Identify ordered list of all lessons (topic or problem nodes)
    ordered_lessons = []
    # Hierarchy traversal to get linear ordered lessons
    root_steps = [n for n in all_nodes if n.type == 'step']
    root_steps.sort(key=lambda x: x.order_index or 0)

    def collect_lessons(node):
        if node.type in ('topic', 'problem', 'lesson'):
            ordered_lessons.append(node)
        children = children_by_parent.get(node.id, [])
        for c in children:
            collect_lessons(c)

    for step in root_steps:
        collect_lessons(step)

    lesson_index_map = {node.id: idx for idx, node in enumerate(ordered_lessons)}

    # Validate each node
    node_validations = {}
    for n in all_nodes:
        checks = []

        # 1. Missing Title
        has_title = bool(n.title and n.title.strip())
        checks.append(ValidationCheck(
            key="missing_title",
            name="Missing Title",
            passed=has_title,
            details=None if has_title else "Node title is empty"
        ))

        # 2. Missing Slug
        has_slug = bool(n.slug and n.slug.strip())
        checks.append(ValidationCheck(
            key="missing_slug",
            name="Missing Slug",
            passed=has_slug,
            details=None if has_slug else "Node slug is empty"
        ))

        # 3. Missing Parent
        has_parent = (n.type == 'step') or bool(n.parent_id)
        checks.append(ValidationCheck(
            key="missing_parent",
            name="Missing Parent",
            passed=has_parent,
            details=None if has_parent else f"Non-step node '{n.id}' has no parent_id"
        ))

        # 4. Invalid Parent
        parent_valid = (n.parent_id is None) or (n.parent_id in node_map)
        checks.append(ValidationCheck(
            key="invalid_parent",
            name="Invalid Parent Pointer",
            passed=parent_valid,
            details=None if parent_valid else f"parent_id '{n.parent_id}' does not exist"
        ))

        # 5. Duplicate Slug
        is_unique_slug = slug_counts.get(n.slug, 0) <= 1
        checks.append(ValidationCheck(
            key="duplicate_slug",
            name="Duplicate Slug",
            passed=is_unique_slug,
            details=None if is_unique_slug else f"Slug '{n.slug}' is shared by {slug_counts.get(n.slug)} nodes"
        ))

        # 6. Duplicate Title Under Same Parent
        siblings = children_by_parent.get(n.parent_id, [])
        same_title_count = sum(1 for s in siblings if s.title.strip().lower() == n.title.strip().lower())
        unique_sibling_title = (same_title_count <= 1)
        checks.append(ValidationCheck(
            key="duplicate_title_same_parent",
            name="Duplicate Title Under Same Parent",
            passed=unique_sibling_title,
            details=None if unique_sibling_title else f"Another node with title '{n.title}' exists under parent '{n.parent_id}'"
        ))

        # 7. Missing Video (For topics/lessons)
        if n.type in ('topic', 'problem', 'lesson'):
            has_vid = bool(n.youtube_video_id or n.youtube_url)
            checks.append(ValidationCheck(
                key="missing_video",
                name="Missing Video",
                passed=has_vid,
                details=None if has_vid else f"Lesson '{n.title}' has no associated YouTube video"
            ))
        else:
            checks.append(ValidationCheck(key="missing_video", name="Missing Video", passed=True))

        # 8. Invalid Video ID
        vid = n.youtube_video_id
        if vid:
            valid_vid_fmt = len(vid) == 11 and bool(re.match(r'^[a-zA-Z0-9_-]{11}$', vid))
            checks.append(ValidationCheck(
                key="invalid_video_id",
                name="Invalid Video ID Format",
                passed=valid_vid_fmt,
                details=None if valid_vid_fmt else f"Video ID '{vid}' is invalid (must be 11 standard characters)"
            ))
        else:
            checks.append(ValidationCheck(key="invalid_video_id", name="Invalid Video ID Format", passed=True))

        # 9. Missing Thumbnail
        if vid or n.youtube_url:
            has_thumb = bool(n.thumbnail_url)
            checks.append(ValidationCheck(
                key="missing_thumbnail",
                name="Missing Video Thumbnail",
                passed=has_thumb,
                details=None if has_thumb else "Thumbnail URL is missing"
            ))
        else:
            checks.append(ValidationCheck(key="missing_thumbnail", name="Missing Video Thumbnail", passed=True))

        # 10. Missing Order Index
        has_order = (n.order_index is not None) and (n.order_index >= 1)
        checks.append(ValidationCheck(
            key="missing_order_index",
            name="Missing Order Index",
            passed=has_order,
            details=None if has_order else f"order_index is invalid: {n.order_index}"
        ))

        # 11. Non-Sequential Ordering
        orders = [s.order_index for s in siblings if s.order_index is not None]
        unique_orders = len(orders) == len(set(orders))
        checks.append(ValidationCheck(
            key="non_sequential_ordering",
            name="Non-Sequential / Duplicate Ordering",
            passed=unique_orders,
            details=None if unique_orders else "Duplicate order indices exist among sibling nodes"
        ))

        # 12 & 13. Prev & Next Lesson Integrity
        if n.type in ('topic', 'problem', 'lesson') and n.id in lesson_index_map:
            idx = lesson_index_map[n.id]
            prev_ok = (idx == 0 or ordered_lessons[idx - 1] is not None)
            next_ok = (idx == len(ordered_lessons) - 1 or ordered_lessons[idx + 1] is not None)
            checks.append(ValidationCheck(key="broken_prev_lesson", name="Broken Previous Lesson Link", passed=prev_ok))
            checks.append(ValidationCheck(key="broken_next_lesson", name="Broken Next Lesson Link", passed=next_ok))
        else:
            checks.append(ValidationCheck(key="broken_prev_lesson", name="Broken Previous Lesson Link", passed=True))
            checks.append(ValidationCheck(key="broken_next_lesson", name="Broken Next Lesson Link", passed=True))

        all_passed = all(c.passed for c in checks)
        failed_count = sum(1 for c in checks if not c.passed)
        node_validations[n.id] = {
            "status": "PASS" if all_passed else "FAIL",
            "failed_count": failed_count,
            "checks": checks
        }

    return {
        "all_nodes": all_nodes,
        "node_map": node_map,
        "children_by_parent": children_by_parent,
        "ordered_lessons": ordered_lessons,
        "lesson_index_map": lesson_index_map,
        "node_validations": node_validations
    }

@router.get("/summary", response_model=CurriculumSummaryResponse)
def get_curriculum_summary(db: Session = Depends(get_db)):
    """
    Get overview statistics and health metrics for the curriculum dashboard.
    """
    cache = build_curriculum_audit_cache(db)
    all_nodes = cache["all_nodes"]
    node_validations = cache["node_validations"]

    steps = [n for n in all_nodes if n.type == 'step']
    sections = [n for n in all_nodes if n.type == 'section']
    topics = [n for n in all_nodes if n.type == 'topic']
    lessons = cache["ordered_lessons"]

    videos_count = sum(1 for l in lessons if l.youtube_video_id or l.youtube_url)
    coverage_pct = round((videos_count / len(lessons) * 100.0), 1) if lessons else 0.0

    passed_count = sum(1 for l in lessons if node_validations[l.id]["status"] == "PASS")
    failed_count = len(lessons) - passed_count
    overall_status = "PASS" if failed_count == 0 else "FAIL"

    # Get last import log
    last_log = db.query(ImportLog).order_by(ImportLog.import_date.desc()).first()
    import_date_str = last_log.import_date.strftime("%Y-%m-%d %H:%M UTC") if last_log else datetime.datetime.utcnow().strftime("%Y-%m-%d")
    version_str = f"v{last_log.excel_version}" if last_log and last_log.excel_version else "v1.0 (Striver A2Z)"

    return CurriculumSummaryResponse(
        total_steps=len(steps),
        total_sections=len(sections),
        total_topics=len(topics),
        total_lessons=len(lessons),
        total_videos=videos_count,
        video_coverage_pct=coverage_pct,
        curriculum_version=version_str,
        last_import_date=import_date_str,
        validation_status=overall_status,
        passed_lessons_count=passed_count,
        failed_lessons_count=failed_count
    )

@router.get("/tree", response_model=List[CurriculumTreeNode])
def get_curriculum_tree(db: Session = Depends(get_db)):
    """
    Get the complete curriculum tree (Step -> Section -> Topic -> Lesson) with validation badges.
    """
    cache = build_curriculum_audit_cache(db)
    all_nodes = cache["all_nodes"]
    children_by_parent = cache["children_by_parent"]
    node_validations = cache["node_validations"]

    def build_node(node) -> CurriculumTreeNode:
        val = node_validations[node.id]
        children = children_by_parent.get(node.id, [])
        children_nodes = [build_node(c) for c in children]

        return CurriculumTreeNode(
            id=node.id,
            title=node.title,
            slug=node.slug,
            type=node.type,
            order_index=node.order_index or 1,
            youtube_video_id=node.youtube_video_id,
            youtube_url=node.youtube_url,
            thumbnail_url=node.thumbnail_url,
            children=children_nodes,
            validation_status=val["status"],
            failed_checks_count=val["failed_count"]
        )

    root_steps = [n for n in all_nodes if n.type == 'step']
    root_steps.sort(key=lambda x: x.order_index or 0)
    tree = [build_node(s) for s in root_steps]
    return tree

@router.get("/lesson/{lesson_id}", response_model=LessonDetailResponse)
def get_lesson_detail(lesson_id: str, db: Session = Depends(get_db)):
    """
    Get full details for a single lesson including parent hierarchy, video iframe embed, and validation checklist.
    """
    cache = build_curriculum_audit_cache(db)
    node_map = cache["node_map"]
    node_validations = cache["node_validations"]
    ordered_lessons = cache["ordered_lessons"]
    lesson_index_map = cache["lesson_index_map"]

    if lesson_id not in node_map:
        raise HTTPException(status_code=404, detail=f"Lesson '{lesson_id}' not found")

    node = node_map[lesson_id]

    # Build ancestor hierarchy
    hierarchy = []
    curr = node
    visited = set()
    while curr.parent_id and curr.parent_id in node_map and curr.parent_id not in visited:
        visited.add(curr.parent_id)
        parent = node_map[curr.parent_id]
        hierarchy.append(ParentAncestor(id=parent.id, title=parent.title, type=parent.type))
        curr = parent
    hierarchy.reverse()

    # Prev & Next navigation
    prev_item = None
    next_item = None
    if lesson_id in lesson_index_map:
        idx = lesson_index_map[lesson_id]
        if idx > 0:
            prev_node = ordered_lessons[idx - 1]
            prev_item = LessonNavigationItem(id=prev_node.id, title=prev_node.title, slug=prev_node.slug)
        if idx < len(ordered_lessons) - 1:
            next_node = ordered_lessons[idx + 1]
            next_item = LessonNavigationItem(id=next_node.id, title=next_node.title, slug=next_node.slug)

    # Embedded video URL
    embed_url = f"https://www.youtube.com/embed/{node.youtube_video_id}" if node.youtube_video_id else None

    # Calculate metadata completeness %
    fields = [
        bool(node.title),
        bool(node.slug),
        bool(node.order_index),
        bool(node.youtube_video_id),
        bool(node.youtube_url),
        bool(node.thumbnail_url),
        bool(node.parent_id or node.type == 'step'),
    ]
    completeness_pct = round((sum(fields) / len(fields)) * 100.0, 1)

    val = node_validations[node.id]

    return LessonDetailResponse(
        id=node.id,
        title=node.title,
        slug=node.slug,
        type=node.type,
        parent_id=node.parent_id,
        parent_hierarchy=hierarchy,
        order_index=node.order_index or 1,
        estimated_duration=node.estimated_time or 15,
        youtube_url=node.youtube_url,
        video_id=node.youtube_video_id,
        thumbnail=node.thumbnail_url,
        embedded_video_url=embed_url,
        prev_lesson=prev_item,
        next_lesson=next_item,
        metadata_completeness=completeness_pct,
        validation_status=val["status"],
        validation_checks=val["checks"]
    )

@router.get("/validation", response_model=CurriculumValidationResponse)
def get_curriculum_validation(db: Session = Depends(get_db)):
    """
    Run full automated audit across all lessons and return pass/fail breakdown.
    """
    cache = build_curriculum_audit_cache(db)
    ordered_lessons = cache["ordered_lessons"]
    node_map = cache["node_map"]
    node_validations = cache["node_validations"]

    check_counts = {r[0]: {"name": r[1], "passed": 0, "failed": 0} for r in VALIDATION_RULES}
    failed_results = []

    passed_count = 0
    for l in ordered_lessons:
        val = node_validations[l.id]
        if val["status"] == "PASS":
            passed_count += 1
        
        # Get step & section titles for context
        step_title = None
        sec_title = None
        curr = l
        while curr.parent_id and curr.parent_id in node_map:
            p = node_map[curr.parent_id]
            if p.type == 'section':
                sec_title = p.title
            elif p.type == 'step':
                step_title = p.title
            curr = p

        failed_checks_for_lesson = []
        for c in val["checks"]:
            if c.passed:
                check_counts[c.key]["passed"] += 1
            else:
                check_counts[c.key]["failed"] += 1
                failed_checks_for_lesson.append(c)

        if val["status"] == "FAIL":
            failed_results.append(LessonValidationResult(
                lesson_id=l.id,
                title=l.title,
                slug=l.slug,
                step_title=step_title,
                section_title=sec_title,
                validation_status="FAIL",
                failed_checks=failed_checks_for_lesson
            ))

    total = len(ordered_lessons)
    failed_count = total - passed_count
    overall_status = "PASS" if failed_count == 0 else "FAIL"

    check_breakdown = {
        key: CheckSummaryItem(
            name=val["name"],
            passed_count=val["passed"],
            failed_count=val["failed"]
        ) for key, val in check_counts.items()
    }

    return CurriculumValidationResponse(
        overall_status=overall_status,
        total_lessons_checked=total,
        passed_count=passed_count,
        failed_count=failed_count,
        check_breakdown=check_breakdown,
        failed_lessons=failed_results
    )

@router.get("/export")
def export_curriculum_report(format: str = Query("json", regex="^(markdown|json|csv)$"), db: Session = Depends(get_db)):
    """
    Export the curriculum audit report in Markdown, JSON, or CSV format.
    """
    cache = build_curriculum_audit_cache(db)
    ordered_lessons = cache["ordered_lessons"]
    node_map = cache["node_map"]
    node_validations = cache["node_validations"]

    if format == "json":
        summary = get_curriculum_summary(db).dict()
        validation = get_curriculum_validation(db).dict()
        data = {
            "exported_at": datetime.datetime.utcnow().isoformat(),
            "summary": summary,
            "validation": validation
        }
        return JSONResponse(content=data, headers={
            "Content-Disposition": "attachment; filename=curriculum_validation_report.json"
        })

    elif format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Lesson ID", "Step Title", "Section Title", "Lesson Title", "Slug",
            "Order Index", "Video ID", "YouTube URL", "Duration (mins)", "Validation Status", "Failed Checks Count"
        ])

        for l in ordered_lessons:
            val = node_validations[l.id]
            step_title = ""
            sec_title = ""
            curr = l
            while curr.parent_id and curr.parent_id in node_map:
                p = node_map[curr.parent_id]
                if p.type == 'section':
                    sec_title = p.title
                elif p.type == 'step':
                    step_title = p.title
                curr = p

            writer.writerow([
                l.id,
                step_title,
                sec_title,
                l.title,
                l.slug,
                l.order_index or 1,
                l.youtube_video_id or "",
                l.youtube_url or "",
                l.estimated_time or 15,
                val["status"],
                val["failed_count"]
            ])

        return Response(content=output.getvalue(), media_type="text/csv", headers={
            "Content-Disposition": "attachment; filename=curriculum_lessons_export.csv"
        })

    elif format == "markdown":
        summary = get_curriculum_summary(db)
        validation = get_curriculum_validation(db)
        now_str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        md = f"""# DSArena Curriculum Audit & Verification Report

**Exported Date**: {now_str}  
**Curriculum Version**: {summary.curriculum_version}  
**Overall Validation Status**: **{summary.validation_status}**

---

## 1. Executive Summary

| Metric | Value |
| :--- | :--- |
| **Total Steps** | {summary.total_steps} |
| **Total Sections** | {summary.total_sections} |
| **Total Topics** | {summary.total_topics} |
| **Total Lessons** | {summary.total_lessons} |
| **Total Videos** | {summary.total_videos} |
| **Video Coverage** | {summary.video_coverage_pct}% |
| **Lessons Passed** | {summary.passed_lessons_count} / {summary.total_lessons} |
| **Lessons Failed** | {summary.failed_lessons_count} |

---

## 2. Automated Check Breakdown

| Check Rule | Passed | Failed | Status |
| :--- | :---: | :---: | :---: |
"""

        for rule_key, rule_name in VALIDATION_RULES:
            item = validation.check_breakdown.get(rule_key)
            passed = item.passed_count if item else 0
            failed = item.failed_count if item else 0
            st = "PASS" if failed == 0 else "FAIL"
            md += f"| {rule_name} | {passed} | {failed} | **{st}** |\n"

        md += "\n---\n\n## 3. Failed Lessons Details\n\n"
        if validation.failed_lessons:
            for fl in validation.failed_lessons:
                md += f"### Lesson: `{fl.title}` (`{fl.lesson_id}`)\n"
                md += f"- **Hierarchy**: {fl.step_title or 'N/A'} > {fl.section_title or 'N/A'}\n"
                md += f"- **Failed Checks**:\n"
                for fc in fl.failed_checks:
                    md += f"  - ❌ **{fc.name}**: {fc.details or 'Check failed'}\n"
                md += "\n"
        else:
            md += "🎉 **All automated checks passed cleanly! Zero validation failures found.**\n"

        return Response(content=md, media_type="text/markdown", headers={
            "Content-Disposition": "attachment; filename=curriculum_audit_report.md"
        })
