import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, ForeignKey("roadmap_nodes.id", ondelete="CASCADE"), nullable=False, unique=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String, nullable=False) # Easy, Medium, Hard
    estimated_time = Column(Integer, default=5) # in minutes
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Sprint 2.5 additions
    xp_reward = Column(Integer, default=50)          # Total XP reward shown on start screen
    pass_mark = Column(Integer, default=70)           # Pass requirement percentage
    question_count = Column(Integer, default=0)       # Cached question count

    # Relationships
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan", order_by="QuizQuestion.order_index")
    attempts = relationship("UserQuizAttempt", back_populates="quiz", cascade="all, delete-orphan")
    node = relationship("RoadmapNode", back_populates="quizzes")

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    type = Column(String, nullable=False) # MCQ, MULTIPLE_SELECT, TRUE_FALSE, ARRANGE_ORDER, MATCH_FOLLOWING, FILL_BLANK
    options = Column(JSON, nullable=False) # List of strings e.g. ["A", "B", "C", "D"]
    correct_answer = Column(JSON, nullable=False) # List of indices e.g. [0] or [1, 2]
    explanation = Column(Text, nullable=True)   # General explanation shown after submission
    difficulty = Column(String, nullable=False)
    order_index = Column(Integer, default=0)

    # Sprint 2.5 additions
    tags = Column(JSON, nullable=True)                    # e.g. ["Two Pointers", "Sliding Window"]
    concept = Column(String, nullable=True)               # Primary concept e.g. "Prefix Sum"
    expected_time_seconds = Column(Integer, nullable=True) # Per-question time hint in seconds
    hints = Column(JSON, nullable=True)                   # List of hint strings (future-ready)
    option_explanations = Column(JSON, nullable=True)     # List of per-option "why wrong" strings

    # Relationship
    quiz = relationship("Quiz", back_populates="questions")

class UserQuizAttempt(Base):
    __tablename__ = "user_quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False) # Percentage (0-100)
    time_taken = Column(Integer, nullable=False) # in seconds
    answers = Column(JSON, nullable=False) # JSON object mapping question_id (as str) to list of selected indices e.g. {"1": [0]}
    attempt_number = Column(Integer, default=1)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Sprint 2.5 additions
    xp_earned = Column(Integer, default=0)            # Total XP earned this attempt
    bonus_xp = Column(Integer, default=0)             # Bonus XP breakdown (perfect + speed + first)
    flagged_questions = Column(JSON, nullable=True)   # List of question IDs flagged during quiz
    skipped_questions = Column(JSON, nullable=True)   # List of question IDs skipped

    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    user = relationship("User", back_populates="quiz_attempts")

