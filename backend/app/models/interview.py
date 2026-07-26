import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class CareerGoal(Base):
    __tablename__ = "career_goals"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, default="Briefcase")

    user_goals = relationship("UserCareerGoal", back_populates="goal", cascade="all, delete-orphan")

class UserCareerGoal(Base):
    __tablename__ = "user_career_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal_id = Column(Integer, ForeignKey("career_goals.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="career_goals")
    goal = relationship("CareerGoal", back_populates="user_goals")

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    logo_url = Column(String, nullable=True)
    difficulty = Column(String, default="Medium") # 'Hard', 'Medium', 'Easy'
    interview_rounds = Column(JSON, nullable=True) # e.g. ["Online Assessment", "Technical Round 1", "Technical Round 2", "Bar Raiser"]
    high_frequency_topics = Column(JSON, nullable=True) # List of topic IDs e.g. ['topic_3_2_1', 'topic_2_1_2']
    recommended_problem_count = Column(Integer, default=45)
    expected_prep_days = Column(Integer, default=30)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    topics = relationship("CompanyTopic", back_populates="company", cascade="all, delete-orphan")
    user_companies = relationship("UserCompany", back_populates="company", cascade="all, delete-orphan")

class CompanyTopic(Base):
    __tablename__ = "company_topics"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(String, ForeignKey("roadmap_nodes.id", ondelete="CASCADE"), nullable=False)
    weight = Column(Integer, default=5) # 1 to 10 priority weight

    company = relationship("Company", back_populates="topics")

class UserCompany(Base):
    __tablename__ = "user_companies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    selected_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="target_companies")
    company = relationship("Company", back_populates="user_companies")

class InterviewReadiness(Base):
    __tablename__ = "interview_readiness"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    overall_score = Column(Integer, default=0) # 0 to 100
    company_scores = Column(JSON, default=dict) # e.g. {"amazon": 75, "google": 60}
    confidence_level = Column(String, default="Getting Started") # 'Interview Ready', 'On Track', 'Needs Reinforcement', 'Getting Started'
    topic_coverage_score = Column(Integer, default=0)
    problem_completion_score = Column(Integer, default=0)
    quiz_accuracy_score = Column(Integer, default=0)
    revision_completion_score = Column(Integer, default=0)
    suggestions = Column(JSON, default=list) # List of advice strings
    calculated_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="interview_readiness")

class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, default="Trophy")
    xp_reward = Column(Integer, default=250)
    badge_name = Column(String, nullable=False)

    user_milestones = relationship("UserMilestone", back_populates="milestone", cascade="all, delete-orphan")

class UserMilestone(Base):
    __tablename__ = "user_milestones"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    milestone_id = Column(Integer, ForeignKey("milestones.id", ondelete="CASCADE"), nullable=False)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="milestones")
    milestone = relationship("Milestone", back_populates="user_milestones")
