from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TranscriptionSessionBase(BaseModel):
    transcript: str
    word_count: int
    duration: float
    session_metadata: Optional[str] = None  # ✅ এখানেও rename

class TranscriptionSessionCreate(TranscriptionSessionBase):
    id: str

class TranscriptionSessionResponse(TranscriptionSessionBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class WebSocketMessage(BaseModel):
    type: str  # "session_id", "partial", "final", "error"
    text: Optional[str] = None
    id: Optional[str] = None
    word_count: Optional[int] = None