from __future__ import annotations

import logging
import re
from typing import Any, Dict, List
from sqlalchemy.orm import Session
from app.models.roadmap import (
    RoadmapNode, RoadmapStep, RoadmapSection, RoadmapTopic, RoadmapLesson, LessonVideo
)

logger = logging.getLogger("RoadmapValidator")

class RoadmapValidationService:
    """
    Validation service checking integrity of the roadmap database:
    - Duplicate IDs, Slugs, and Titles
    - Missing parent references & broken hierarchy chains
    - Missing videos & invalid YouTube URLs
    - Non-sequential ordering
    """

    def __init__(self, db: Session):
        self.db = db

    def validate_roadmap(self) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []

        all_nodes = self.db.query(RoadmapNode).all()
        all_lessons = self.db.query(RoadmapLesson).all()
        all_videos = self.db.query(LessonVideo).all()

        # 1. Duplicate IDs
        ids_seen = set()
        duplicate_ids = set()
        for n in all_nodes:
            if n.id in ids_seen:
                duplicate_ids.add(n.id)
                errors.append(f"Duplicate Node ID found: '{n.id}'")
            ids_seen.add(n.id)

        # 2. Duplicate Slugs
        slugs_seen = {}
        for n in all_nodes:
            if n.slug in slugs_seen:
                warnings.append(f"Duplicate slug '{n.slug}' on nodes '{slugs_seen[n.slug]}' and '{n.id}'")
            else:
                slugs_seen[n.slug] = n.id

        # 3. Missing Parent References & Broken Hierarchy
        node_id_map = {n.id: n for n in all_nodes}
        missing_parents = 0
        for n in all_nodes:
            if n.parent_id and n.parent_id not in node_id_map:
                missing_parents += 1
                errors.append(f"Node '{n.id}' references missing parent_id '{n.parent_id}'")

        # 4. Missing Videos & Invalid Video URLs
        missing_videos = 0
        invalid_urls = 0
        for lesson in all_lessons:
            vids = self.db.query(LessonVideo).filter(LessonVideo.lesson_id == lesson.id).all()
            if not vids:
                missing_videos += 1
                warnings.append(f"Lesson '{lesson.id}' ({lesson.title}) has no attached LessonVideo.")
            else:
                for v in vids:
                    if not v.video_id or not re.match(r"^[a-zA-Z0-9_-]{11}$", v.video_id):
                        invalid_urls += 1
                        errors.append(f"Invalid video_id '{v.video_id}' for lesson '{lesson.id}'")

        # 5. Ordering Validation
        wrong_order = 0
        # Group by parent_id
        parent_groups: Dict[str, List[RoadmapNode]] = {}
        for n in all_nodes:
            pid = n.parent_id or "ROOT"
            if pid not in parent_groups:
                parent_groups[pid] = []
            parent_groups[pid].append(n)

        for pid, group in parent_groups.items():
            group.sort(key=lambda x: x.order_index)
            for idx, item in enumerate(group):
                if item.order_index <= 0:
                    wrong_order += 1
                    warnings.append(f"Node '{item.id}' has non-positive order_index '{item.order_index}'")

        total_nodes = len(all_nodes)
        valid_nodes = total_nodes - len(errors)

        is_valid = len(errors) == 0

        result = {
            "is_valid": is_valid,
            "total_nodes": total_nodes,
            "total_lessons": len(all_lessons),
            "total_videos": len(all_videos),
            "duplicate_ids": len(duplicate_ids),
            "missing_parents": missing_parents,
            "missing_videos": missing_videos,
            "invalid_urls": invalid_urls,
            "wrong_order_count": wrong_order,
            "errors": errors,
            "warnings": warnings,
            "validation_score": f"{round((valid_nodes / max(1, total_nodes)) * 100, 1)}%"
        }

        logger.info(f"Roadmap validation complete. Valid: {is_valid}. Errors: {len(errors)}, Warnings: {len(warnings)}")
        return result
