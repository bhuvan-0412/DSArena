from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, nullable=False, unique=True)

    # Relationships
    sections = relationship("Section", back_populates="campaign", cascade="all, delete-orphan", order_by="Section.order")

class Section(Base):
    __tablename__ = "sections"

    id = Column(String, primary_key=True, index=True)
    campaign_id = Column(String, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="sections")
    subsections = relationship("Subsection", back_populates="section", cascade="all, delete-orphan", order_by="Subsection.order")

class Subsection(Base):
    __tablename__ = "subsections"

    id = Column(String, primary_key=True, index=True)
    section_id = Column(String, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, nullable=False)

    # Relationships
    section = relationship("Section", back_populates="subsections")
    concepts = relationship("Concept", back_populates="subsection", cascade="all, delete-orphan", order_by="Concept.order")
