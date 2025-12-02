from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..services.session_service import SessionService
from ..schemas.session import TranscriptionSessionResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.get("", response_model=List[TranscriptionSessionResponse])
async def get_all_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Retrieve all transcription sessions
    
    Query Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100)
    
    Returns:
    - List of transcription sessions ordered by creation date (newest first)
    """
    sessions = SessionService.get_all_sessions(db, skip=skip, limit=limit)
    return sessions

@router.get("/{session_id}", response_model=TranscriptionSessionResponse)
async def get_session_by_id(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific transcription session by ID
    
    Path Parameters:
    - session_id: UUID of the session
    
    Returns:
    - Transcription session details including full transcript
    
    Raises:
    - 404: Session not found
    """
    session = SessionService.get_session_by_id(db, session_id)
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session with id '{session_id}' not found"
        )
    
    return session

@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a transcription session
    
    Path Parameters:
    - session_id: UUID of the session
    
    Returns:
    - Success message
    
    Raises:
    - 404: Session not found
    """
    deleted = SessionService.delete_session(db, session_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Session with id '{session_id}' not found"
        )
    
    return {"message": "Session deleted successfully", "session_id": session_id}
