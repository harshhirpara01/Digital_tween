from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    profession = Column(String(200), nullable=False)
    otp_code = Column(String(16), nullable=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    logs = relationship("BehaviorLog", back_populates="user", cascade="all, delete-orphan")


class BehaviorLog(Base):
    __tablename__ = "behavior_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    log_date = Column(Date, nullable=False)
    log_hour = Column(Integer, nullable=False)
    activity = Column(String(200), nullable=False)
    mood = Column(String(120), nullable=False)
    energy_level = Column(Integer, nullable=False)
    study_hour = Column(Float, nullable=False)
    work_hour = Column(Float, nullable=False)
    mobile_usage_hour = Column(Float, nullable=False)
    sleep_hours = Column(Float, nullable=False)
    social_intreaction_minutes = Column(Integer, nullable=False)
    is_weekend = Column(Boolean, nullable=False, default=False)
    productivy_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="logs")
