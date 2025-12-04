import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..utils.websocket_manager import manager
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws/transcribe")
async def websocket_transcribe_endpoint(
    websocket: WebSocket,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time audio transcription
    
    Flow:
    1. Accept WebSocket connection
    2. Generate and send session ID
    3. Receive audio chunks
    4. Process with Vosk STT
    5. Send partial/final results
    6. Save to database on disconnect
    """
    session_id = str(uuid.uuid4())
    logger.info(f"New WebSocket connection - Session ID: {session_id}")
    
    await manager.connect(websocket, session_id)
    
    try:
        # Send session ID to client
        await websocket.send_json({
            "type": "session_id",
            "id": session_id
        })
        logger.info(f"Session ID sent to client: {session_id}")
        
        # Handle transcription
        await manager.handle_transcription(websocket, session_id, db)
        
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected - Session ID: {session_id}")
        await manager.disconnect(session_id, db)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        await manager.disconnect(session_id, db)
