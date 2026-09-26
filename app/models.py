from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from app.database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False)
    city = Column(String(100), nullable=False)
    course_interested = Column(String(200), nullable=False)
    preferred_college = Column(String(200), nullable=False)
    intake_year = Column(String(10), nullable=True)
    source_college = Column(String(150), nullable=True)  # which college-page link they applied through
    twelfth_percentage = Column(String(10), nullable=True)
    message = Column(Text, nullable=True)
    consent_given = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class College(Base):
    __tablename__ = "colleges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(120), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    city = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    courses_offered = Column(Text, nullable=True)  # comma-separated, kept simple for v1
    website = Column(String(300), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
