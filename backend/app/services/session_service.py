from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.session import TranscriptionSession
from ..schemas.session import TranscriptionSessionCreate

class SessionService:
    """Service for managing transcription sessions"""
    
    @staticmethod
    def create_session(
        db: Session, 
        session_data: TranscriptionSessionCreate
    ) -> TranscriptionSession:
        db_session = TranscriptionSession(
            id=session_data.id,
            transcript=session_data.transcript,
            word_count=session_data.word_count,
            duration=session_data.duration,
            session_metadata=session_data.session_metadata
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session
    
    @staticmethod
    def get_all_sessions(
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[TranscriptionSession]:
        return db.query(TranscriptionSession)\
            .order_by(TranscriptionSession.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_session_by_id(
        db: Session, 
        session_id: str
    ) -> Optional[TranscriptionSession]:
        return db.query(TranscriptionSession)\
            .filter(TranscriptionSession.id == session_id)\
            .first()
    
    @staticmethod
    def delete_session(db: Session, session_id: str) -> bool:
        session = SessionService.get_session_by_id(db, session_id)
        if session:
            db.delete(session)
            db.commit()
            return True
        return False
    

