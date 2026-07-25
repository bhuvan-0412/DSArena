from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime

# Problems
class ProblemBase(BaseModel):
    id: str
    title: str
    difficulty: str
    xp_reward: int
    statement: str
    examples: Optional[List[Any]] = None
    constraints: Optional[List[str]] = None
    hints: Optional[List[str]] = None
    external_link: Optional[str] = None
    expected_time_complexity: Optional[str] = None
    expected_space_complexity: Optional[str] = None

class ProblemCreate(ProblemBase):
    topic_id: str

class ProblemResponse(ProblemBase):
    topic_id: str
    status: Optional[str] = "NOT_STARTED"
    revision_due_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Topics / Concepts
class TopicBase(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    order: int
    xp_reward: int = 200

class TopicCreate(TopicBase):
    pass

class TopicResponse(TopicBase):
    problems: List[ProblemResponse] = []
    problems_solved: Optional[int] = 0
    quiz_completed: Optional[bool] = False
    video_watched: Optional[bool] = False
    notes_read: Optional[bool] = False
    boss_battle_completed: Optional[bool] = False
    boss_battle_locked: Optional[bool] = True
    mastery_percentage: Optional[int] = 0
    estimated_completion: Optional[str] = "0 mins"
    quiz_best_score: Optional[int] = None

    class Config:
        from_attributes = True

# New Hierarchical Node Schema
class RoadmapNodeResponse(BaseModel):
    id: str
    parent_id: Optional[str] = None
    title: str
    slug: str
    description: Optional[str] = None
    type: str  # 'step', 'section', 'subsection', 'topic', 'problem'
    order_index: int
    estimated_time: Optional[int] = None
    xp_reward: int = 0
    difficulty: Optional[str] = None
    
    # Progress/status fields computed dynamically for the user
    is_completed: bool = False
    is_locked: bool = False
    progress_percentage: int = 0
    problems_solved: int = 0
    total_problems: int = 0
    quiz_completed: bool = False
    quiz_best_score: Optional[int] = None
    revision_due_count: int = 0
    
    children: List['RoadmapNodeResponse'] = []

    class Config:
        from_attributes = True

# Sprint 2.4 Learning Content Engine Schemas
class LearningResourceResponse(BaseModel):
    id: int
    node_id: str
    title: str
    type: str  # 'Video', 'Article', 'Documentation'
    author: Optional[str] = None
    duration: Optional[str] = None
    difficulty: Optional[str] = None
    url: str
    order_index: int = 1
    is_bookmarked: bool = False

    class Config:
        from_attributes = True

class KeyConceptResponse(BaseModel):
    id: int
    node_id: str
    title: str
    summary: str
    key_points: Optional[List[str]] = None
    complexity_notes: Optional[str] = None
    common_mistakes: Optional[List[str]] = None
    best_practices: Optional[List[str]] = None
    order_index: int = 1

    class Config:
        from_attributes = True

class ConceptNoteRequest(BaseModel):
    content: str

class ConceptNoteResponse(BaseModel):
    id: int
    node_id: str
    content: str
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BookmarkToggleRequest(BaseModel):
    target_type: str  # 'concept', 'problem', 'resource'
    target_id: str

class BookmarkItem(BaseModel):
    id: int
    target_type: str
    target_id: str
    title: str
    description: Optional[str] = None
    difficulty: Optional[str] = None
    created_at: Optional[datetime] = None

class UserBookmarksResponse(BaseModel):
    concepts: List[BookmarkItem] = []
    problems: List[BookmarkItem] = []
    resources: List[BookmarkItem] = []

class LearningChecklistRequest(BaseModel):
    watched_video: Optional[bool] = None
    read_notes: Optional[bool] = None
    understood_concepts: Optional[bool] = None
    completed_quiz: Optional[bool] = None
    solved_problems: Optional[bool] = None

class LearningChecklistResponse(BaseModel):
    watched_video: bool = False
    read_notes: bool = False
    understood_concepts: bool = False
    completed_quiz: bool = False
    solved_problems: bool = False
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True



# Sprint 2.5 Interactive Quiz Engine Schemas
class QuizStartResponse(BaseModel):
    id: int
    topic_id: str
    title: str
    description: Optional[str] = None
    difficulty: str
    estimated_time: int
    xp_reward: int = 50
    pass_mark: int = 70
    question_count: int = 0
    best_score: Optional[int] = None
    attempt_count: int = 0

class QuizQuestionResponse(BaseModel):
    id: int
    question: str
    type: str  # MCQ, MULTIPLE_SELECT, TRUE_FALSE, ARRANGE_ORDER, MATCH_FOLLOWING, FILL_BLANK
    options: List[str]
    difficulty: str
    order_index: int
    tags: Optional[List[str]] = None
    concept: Optional[str] = None
    expected_time_seconds: Optional[int] = 60
    hints: Optional[List[str]] = None

class QuizSubmitRequest(BaseModel):
    time_taken: int  # total duration in seconds
    answers: Dict[str, List[int]]  # question_id string -> selected option indices
    flagged_questions: Optional[List[int]] = []
    skipped_questions: Optional[List[int]] = []

class QuizQuestionReview(BaseModel):
    id: int
    question: str
    type: str
    options: List[str]
    user_answer: List[int]
    correct_answer: List[int]
    is_correct: bool
    is_skipped: bool
    explanation: Optional[str] = None
    option_explanations: Optional[List[str]] = None
    concept: Optional[str] = None
    tags: Optional[List[str]] = None

class QuizResultResponse(BaseModel):
    attempt_id: int
    score: int  # Percentage (0-100)
    passed: bool
    correct_count: int
    incorrect_count: int
    skipped_count: int
    time_taken: int  # in seconds
    xp_earned: int
    bonus_xp: int
    perfect_bonus: bool
    speed_bonus: bool
    first_attempt_bonus: bool
    attempt_number: int
    questions_review: List[QuizQuestionReview] = []
    newly_unlocked_achievements: List[Any] = []

class QuizAttemptHistoryItem(BaseModel):
    id: int
    score: int
    time_taken: int
    attempt_number: int
    xp_earned: int = 0
    completed_at: Optional[datetime] = None


