from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict
import time
import asyncio
import json
from ..services.transcription_service import TranscriptionService
from ..services.session_service import SessionService
from ..schemas.session import TranscriptionSessionCreate
from ..config import get_settings

settings = get_settings()

class ConnectionManager:
    """Manager for WebSocket connections and transcription sessions"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.transcription_service = TranscriptionService(settings.model_path)
        self.session_data: Dict[str, dict] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept WebSocket connection and initialize session"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.session_data[session_id] = {
            "transcript": [],
            "start_time": time.time(),
            "last_partial": "",
            "last_send_time": 0
        }
    
    async def disconnect(self, session_id: str, db: Session):
        """Handle WebSocket disconnection and save session"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        
        if session_id in self.session_data:
            data = self.session_data[session_id]
            duration = time.time() - data["start_time"]
            complete_transcript = " ".join(data["transcript"])
            word_count = len(complete_transcript.split()) if complete_transcript else 0
            
            session_create = TranscriptionSessionCreate(
                id=session_id,
                transcript=complete_transcript,
                word_count=word_count,
                duration=duration
            )
            
            SessionService.create_session(db, session_create)
            del self.session_data[session_id]
    
    async def handle_transcription(
        self, 
        websocket: WebSocket, 
        session_id: str, 
        db: Session
    ):
        """
        Robust handler that supports:
        1. Binary audio data
        2. Text end signals (JSON)
        3. Timeout protection
        """  
        recognizer = self.transcription_service.create_recognizer()
        THROTTLE_DELAY = 0.3
        TIMEOUT = 30  # seconds

        try:
            while True:
                try:
                    # Try to receive with timeout
                    message = await asyncio.wait_for(
                        websocket.receive(),
                        timeout=TIMEOUT
                    )
                    
                    print(f"[{session_id}] Message: {message}")
                    
                    # Safely get message type and data
                    msg_type = message.get("type", "")
                    
                    # Handle binary data (audio chunks)
                    if "bytes" in message and message["bytes"]:
                        audio_data = message["bytes"]
                        
                        # Check for binary end signal
                        if audio_data == b"__END__":
                            print(f"[{session_id}] ✅ Received binary END signal")
                            await self._send_final_result(websocket, session_id, recognizer)
                            break
                        
                        # Process normal audio
                        await self._process_audio(websocket, session_id, recognizer, audio_data)
                    
                    # Handle text data (JSON commands)
                    elif "text" in message and message["text"]:
                        text_data = message["text"]
                        print(f"[{session_id}] Received text: {text_data}")
                        
                        try:
                            data = json.loads(text_data)
                            if data.get("action") == "end_audio":
                                print(f"[{session_id}] ✅ Received JSON END signal")
                                await self._send_final_result(websocket, session_id, recognizer)
                                break
                        except json.JSONDecodeError as e:
                            print(f"[{session_id}] ⚠️ Invalid JSON: {text_data}, Error: {e}")
                    
                    # Handle disconnect
                    elif msg_type == "websocket.disconnect":
                        print(f"[{session_id}] Disconnect message received")
                        break
                    
                    else:
                        print(f"[{session_id}] ⚠️ Unknown message format: {message}")
                
                except asyncio.TimeoutError:
                    print(f"[{session_id}] ⏰ Timeout - no data for {TIMEOUT}s, ending session")
                    await self._send_final_result(websocket, session_id, recognizer)
                    break
                except Exception as inner_e:
                    print(f"[{session_id}] ❌ Inner loop error: {inner_e}")
                    import traceback
                    traceback.print_exc()
                    # Continue to next iteration
                    continue

        except WebSocketDisconnect:
            print(f"[{session_id}] 🔌 Client disconnected")
            try:
                final_text = self.transcription_service.get_final_result(recognizer)
                if final_text and final_text.strip():
                    self.session_data[session_id]["transcript"].append(final_text)
            except:
                pass
            await self.disconnect(session_id, db)
        
        except Exception as e:
            print(f"[{session_id}] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await self.disconnect(session_id, db)
    
    async def _send_final_result(self, websocket: WebSocket, session_id: str, recognizer):
        """Helper to send final result"""
        print(f"[{session_id}] 📝 Getting final result...")
        final_text = self.transcription_service.get_final_result(recognizer)
        
        print(f"[{session_id}] Final text: '{final_text}'")
        
        if final_text and final_text.strip():
            self.session_data[session_id]["transcript"].append(final_text)
            response = {
                "type": "final",
                "text": final_text,
                "session_complete": True
            }
            print(f"[{session_id}] 📤 Sending final result: {response}")
            await websocket.send_json(response)
            print(f"[{session_id}] ✅ Final result sent!")
        else:
            response = {
                "type": "final",
                "text": "",
                "session_complete": True
            }
            print(f"[{session_id}] 📤 Sending empty final")
            await websocket.send_json(response)
    
    async def _process_audio(self, websocket: WebSocket, session_id: str, recognizer, audio_data: bytes):
        """Helper to process audio chunk"""
        result = self.transcription_service.process_audio_chunk(recognizer, audio_data)
        current_time = time.time()
        session_data = self.session_data[session_id]

        if result["type"] == "partial":
            current_text = result["text"].strip()
            last_partial = session_data["last_partial"]
            last_send = session_data["last_send_time"]
            
            if current_text and current_text != last_partial:
                # Calculate word difference
                current_words = current_text.split()
                last_words = last_partial.split() if last_partial else []
                word_diff = len(current_words) - len(last_words)
                time_diff = current_time - last_send
                
                # Send if significant change or enough time passed
                should_send = (word_diff >= 2) or (time_diff >= 1.0)
                
                if should_send:
                    session_data["last_partial"] = current_text
                    session_data["last_send_time"] = current_time
                    await websocket.send_json({
                        "type": "partial",
                        "text": current_text
                    })
                    # print(f"[{session_id}] Partial: ...{current_text[-50:]}")
        
        elif result["type"] == "final":
            final_text = result["text"].strip()
            if final_text:
                session_data["transcript"].append(final_text)
                session_data["last_partial"] = ""
                session_data["last_send_time"] = current_time
                
                await websocket.send_json({
                    "type": "final",
                    "text": final_text
                })
                print(f"[{session_id}] Final chunk: {final_text}")


# Global instance
manager = ConnectionManager()