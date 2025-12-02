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
            "last_send_time": 0,
            "audio_chunks_received": 0  # ✅ Track audio reception
        }
        
        # Send session_id to client
        await websocket.send_json({
            "type": "session_id",
            "id": session_id
        })
        print(f"[{session_id}] ✅ Session initialized and ID sent to client")
    
    async def disconnect(self, session_id: str, db: Session):
        """Handle WebSocket disconnection and save session"""
        print(f"[{session_id}] 🔄 Starting disconnect process...")
        
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        
        if session_id in self.session_data:
            data = self.session_data[session_id]
            duration = time.time() - data["start_time"]
            complete_transcript = " ".join(data["transcript"])
            word_count = len(complete_transcript.split()) if complete_transcript else 0
            
            print(f"[{session_id}] 📊 Session stats:")
            print(f"  - Audio chunks received: {data['audio_chunks_received']}")
            print(f"  - Transcript parts: {len(data['transcript'])}")
            print(f"  - Complete transcript: '{complete_transcript[:200]}'")
            print(f"  - Word count: {word_count}")
            print(f"  - Duration: {duration:.2f}s")
            
            # Save session even if empty
            try:
                session_create = TranscriptionSessionCreate(
                    id=session_id,
                    transcript=complete_transcript or "[No transcript]",
                    word_count=word_count,
                    duration=duration
                )
                
                saved_session = SessionService.create_session(db, session_create)
                print(f"[{session_id}] ✅ Session saved to database with ID: {saved_session.id}")
                
            except Exception as e:
                print(f"[{session_id}] ❌ Error saving session to database: {e}")
                import traceback
                traceback.print_exc()
            
            # Cleanup
            del self.session_data[session_id]
        else:
            print(f"[{session_id}] ⚠️ No session data found for {session_id}")
    
    async def handle_transcription(
        self, 
        websocket: WebSocket, 
        session_id: str, 
        db: Session
    ):
        """Handle real-time transcription with detailed logging"""  
        recognizer = self.transcription_service.create_recognizer()
        print(f"[{session_id}] 🎤 Recognizer created, waiting for audio...")
        TIMEOUT = 30

        try:
            while True:
                try:
                    message = await asyncio.wait_for(
                        websocket.receive(),
                        timeout=TIMEOUT
                    )
                    
                    # ✅ DEBUG: Log every message received
                    msg_type = message.get("type", "unknown")
                    has_bytes = "bytes" in message and message["bytes"]
                    has_text = "text" in message and message["text"]
                    
                    if has_bytes:
                        audio_size = len(message["bytes"])
                        print(f"[{session_id}] 🎵 Received {audio_size} bytes of audio")
                    
                    if has_text:
                        print(f"[{session_id}] 📝 Received text: {message['text'][:100]}")
                    
                    # Handle binary audio data
                    if has_bytes:
                        audio_data = message["bytes"]
                        self.session_data[session_id]["audio_chunks_received"] += 1
                        
                        # Check for END signal
                        if audio_data == b"__END__":
                            print(f"[{session_id}] 🛑 Binary END signal")
                            await self._send_final_result(websocket, session_id, recognizer, db)
                            break
                        
                        # Process audio
                        print(f"[{session_id}] 🔄 Processing audio chunk #{self.session_data[session_id]['audio_chunks_received']}")
                        await self._process_audio(websocket, session_id, recognizer, audio_data)
                    
                    # Handle text/JSON commands
                    elif has_text:
                        text_data = message["text"]
                        try:
                            data = json.loads(text_data)
                            if data.get("action") == "end_audio":
                                print(f"[{session_id}] 🛑 JSON END signal")
                                await self._send_final_result(websocket, session_id, recognizer, db)
                                break
                        except json.JSONDecodeError:
                            print(f"[{session_id}] ⚠️ Invalid JSON received")
                    
                    # Handle disconnect
                    elif msg_type == "websocket.disconnect":
                        print(f"[{session_id}] 🔌 Disconnect signal")
                        break
                
                except asyncio.TimeoutError:
                    print(f"[{session_id}] ⏰ Timeout after {TIMEOUT}s")
                    await self._send_final_result(websocket, session_id, recognizer, db)
                    break

        except WebSocketDisconnect:
            print(f"[{session_id}] 🔌 WebSocket disconnected")
            try:
                final_text = self.transcription_service.get_final_result(recognizer)
                if final_text and final_text.strip():
                    self.session_data[session_id]["transcript"].append(final_text)
                    print(f"[{session_id}] 📝 Final text on disconnect: {final_text}")
            except Exception as e:
                print(f"[{session_id}] ⚠️ Error getting final text: {e}")
            
            await self.disconnect(session_id, db)
        
        except Exception as e:
            print(f"[{session_id}] ❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            await self.disconnect(session_id, db)
    
    async def _send_final_result(self, websocket: WebSocket, session_id: str, recognizer, db: Session):
        """Send final result and save session"""
        print(f"[{session_id}] 📋 Finalizing transcription...")
        
        try:
            # Get any remaining transcription
            final_text = self.transcription_service.get_final_result(recognizer)
            print(f"[{session_id}] 📄 Final text from recognizer: '{final_text}'")
            
            if final_text and final_text.strip():
                self.session_data[session_id]["transcript"].append(final_text)
            
            # Get complete transcript
            complete = " ".join(self.session_data[session_id]["transcript"])
            print(f"[{session_id}] 📜 Complete transcript: '{complete}'")
            
            # ✅ CRITICAL: Save to database BEFORE sending response
            try:
                data = self.session_data[session_id]
                duration = time.time() - data["start_time"]
                word_count = len(complete.split()) if complete else 0
                
                session_create = TranscriptionSessionCreate(
                    id=session_id,
                    transcript=complete or "[No transcript]",
                    word_count=word_count,
                    duration=duration
                )
                
                saved = SessionService.create_session(db, session_create)
                print(f"[{session_id}] ✅ Session saved to database with ID: {saved.id}")
                print(f"[{session_id}]    - Transcript: '{complete[:100]}'")
                print(f"[{session_id}]    - Words: {word_count}, Duration: {duration:.2f}s")
                
            except Exception as db_error:
                print(f"[{session_id}] ❌ Database save error: {db_error}")
                import traceback
                traceback.print_exc()
            
            # Send response to client with session_complete flag
            response = {
                "type": "final",
                "text": final_text if final_text else "",
                "session_complete": True,
                "complete_transcript": complete,
                "word_count": word_count
            }
            
            await websocket.send_json(response)
            print(f"[{session_id}] ✅ Final result sent to client with session_complete=True")
            
            # Cleanup session data
            if session_id in self.session_data:
                del self.session_data[session_id]
            if session_id in self.active_connections:
                del self.active_connections[session_id]
                
        except Exception as e:
            print(f"[{session_id}] ❌ Error in _send_final_result: {e}")
            import traceback
            traceback.print_exc()
    
    async def _process_audio(self, websocket: WebSocket, session_id: str, recognizer, audio_data: bytes):
        """Process audio chunk - MAIN TRANSCRIPTION LOGIC"""
        try:
            print(f"[{session_id}] 🔍 Calling transcription service...")
            
            # ✅ CRITICAL: Check if transcription service is working
            result = self.transcription_service.process_audio_chunk(recognizer, audio_data)
            
            print(f"[{session_id}] 📊 Result from service: {result}")
            
            if not result:
                print(f"[{session_id}] ⚠️ No result from transcription service!")
                return
            
            current_time = time.time()
            session_data = self.session_data[session_id]

            if result["type"] == "partial":
                current_text = result.get("text", "").strip()
                print(f"[{session_id}] 💬 Partial result: '{current_text}'")
                
                if current_text:
                    last_partial = session_data["last_partial"]
                    
                    if current_text != last_partial:
                        session_data["last_partial"] = current_text
                        session_data["last_send_time"] = current_time
                        
                        await websocket.send_json({
                            "type": "partial",
                            "text": current_text
                        })
                        print(f"[{session_id}] ✅ Sent partial to client: '{current_text[:100]}'")
            
            elif result["type"] == "final":
                final_text = result.get("text", "").strip()
                print(f"[{session_id}] ✅ Final result: '{final_text}'")
                
                if final_text:
                    session_data["transcript"].append(final_text)
                    session_data["last_partial"] = ""
                    session_data["last_send_time"] = current_time
                    
                    await websocket.send_json({
                        "type": "final",
                        "text": final_text
                    })
                    print(f"[{session_id}] ✅ Sent final to client")
            
            elif result["type"] == "error":
                error_msg = result.get("text", "Unknown error")
                print(f"[{session_id}] ❌ Transcription error: {error_msg}")
                await websocket.send_json({
                    "type": "error",
                    "text": error_msg
                })
                    
        except Exception as e:
            print(f"[{session_id}] ❌ Error in _process_audio: {e}")
            import traceback
            traceback.print_exc()
            
            # Send error to client
            try:
                await websocket.send_json({
                    "type": "error",
                    "text": f"Processing error: {str(e)}"
                })
            except:
                pass


# Global instance
manager = ConnectionManager()