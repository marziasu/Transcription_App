from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.sql import func
from ..database import Base
import uuid

class TranscriptionSession(Base):
    __tablename__ = "transcription_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    transcript = Column(Text, nullable=False, default="")
    word_count = Column(Integer, nullable=False, default=0)
    duration = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    session_metadata = Column(Text, nullable=True)  # ✅ 'metadata' থেকে 'session_metadata' তে rename
    
    def __repr__(self):
        return f"<TranscriptionSession(id={self.id}, word_count={self.word_count})>"