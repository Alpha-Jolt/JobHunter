from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from core.db import Base

class ScraperPreferences(Base):
    __tablename__ = "scraper_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    preferences = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ScraperAuditLog(Base):
    __tablename__ = "scraper_audit_log"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    request_id = Column(String, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    audit_hash = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
