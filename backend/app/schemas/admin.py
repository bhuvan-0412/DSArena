from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class CurriculumSummaryResponse(BaseModel):
    total_steps: int
    total_sections: int
    total_topics: int
    total_lessons: int
    total_videos: int
    video_coverage_pct: float
    curriculum_version: str
    last_import_date: str
    validation_status: str  # "PASS" | "FAIL"
    passed_lessons_count: int
    failed_lessons_count: int

class CurriculumTreeNode(BaseModel):
    id: str
    title: str
    slug: str
    type: str  # "step" | "section" | "topic" | "lesson"
    order_index: int
    youtube_video_id: Optional[str] = None
    youtube_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    children: List["CurriculumTreeNode"] = []
    validation_status: str = "PASS"
    failed_checks_count: int = 0

CurriculumTreeNode.update_forward_refs()

class ValidationCheck(BaseModel):
    key: str
    name: str
    passed: bool
    details: Optional[str] = None

class ParentAncestor(BaseModel):
    id: str
    title: str
    type: str

class LessonNavigationItem(BaseModel):
    id: str
    title: str
    slug: str

class LessonDetailResponse(BaseModel):
    id: str
    title: str
    slug: str
    type: str
    parent_id: Optional[str] = None
    parent_hierarchy: List[ParentAncestor] = []
    order_index: int
    estimated_duration: int
    youtube_url: Optional[str] = None
    video_id: Optional[str] = None
    thumbnail: Optional[str] = None
    embedded_video_url: Optional[str] = None
    prev_lesson: Optional[LessonNavigationItem] = None
    next_lesson: Optional[LessonNavigationItem] = None
    metadata_completeness: float
    validation_status: str  # "PASS" | "FAIL"
    validation_checks: List[ValidationCheck] = []

class LessonValidationResult(BaseModel):
    lesson_id: str
    title: str
    slug: str
    step_title: Optional[str] = None
    section_title: Optional[str] = None
    validation_status: str  # "PASS" | "FAIL"
    failed_checks: List[ValidationCheck] = []

class CheckSummaryItem(BaseModel):
    name: str
    passed_count: int
    failed_count: int

class CurriculumValidationResponse(BaseModel):
    overall_status: str  # "PASS" | "FAIL"
    total_lessons_checked: int
    passed_count: int
    failed_count: int
    check_breakdown: Dict[str, CheckSummaryItem]
    failed_lessons: List[LessonValidationResult]
