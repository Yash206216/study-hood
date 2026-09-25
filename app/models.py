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
    twelfth_percentage = Column(String(10), nullable=True)
    message = Column(Text, nullable=True)
    consent_given = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
