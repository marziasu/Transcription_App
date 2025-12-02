import asyncio
import websockets
import sys
import os
import json
from app.services.read_audio import read_audio_as_bytes

async def send_audio(file_path, ws_url="ws://127.0.0.1:8000/ws/transcribe"):
    """Send audio file to WebSocket server for transcription"""
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ Connected to WebSocket!")

            # Receive initial session ID
            initial_msg = await websocket.recv()
            session_data = json.loads(initial_msg)
            session_id = session_data.get('id', 'unknown')
            print(f"📝 Session ID: {session_id}\n")

            # Read audio file as bytes
            print(f"📁 Reading audio file: {file_path}")
            audio_bytes = read_audio_as_bytes(file_path)
            print(f"📊 Audio size: {len(audio_bytes)} bytes\n")

            # Send audio in chunks
            chunk_size = 4000
            total_chunks = (len(audio_bytes) + chunk_size - 1) // chunk_size
            
            print(f"📤 Sending {total_chunks} audio chunks...")
            for i in range(0, len(audio_bytes), chunk_size):
                chunk = audio_bytes[i:i+chunk_size]
                await websocket.send(chunk)
                
                # Show progress every 10 chunks
                chunk_num = i // chunk_size + 1
                if chunk_num % 10 == 0:
                    print(f"   Sent chunk {chunk_num}/{total_chunks}")

            print("✅ All audio sent")
            print("🔚 Sending end-of-audio signal...\n")

            # Send JSON end signal (more reliable than binary)
            await asyncio.sleep(0.2)  # Wait for last chunk to process
            await websocket.send(json.dumps({"action": "end_audio"}))
            print("✅ End signal sent!")
            await asyncio.sleep(0.1)  # Wait for signal to be sent

            # Receive transcription results
            print("=" * 60)
            print("TRANSCRIPTION RESULTS:")
            print("=" * 60)
            print()
            
            final_transcripts = []
            last_partial = ""
            received_count = 0
            MAX_WAIT = 150  # Maximum messages to receive
            
            try:
                while received_count < MAX_WAIT:
                    try:
                        msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        received_count += 1
                    except asyncio.TimeoutError:
                        print("\n⏰ Timeout - no more data received")
                        break
                    
                    data = json.loads(msg)
                    
                    msg_type = data.get('type', 'unknown')
                    text = data.get('text', '').strip()
                    
                    if msg_type == "partial":
                        # Only print if changed and not empty
                        if text and text != last_partial:
                            # Clear line and print partial (overwrites previous)
                            print(f"\r🔄 Listening: {text}", end='', flush=True)
                            last_partial = text
                        elif not text:
                            print(f"⚠️ Empty partial received")  # Debug
                    
                    elif msg_type == "final":
                        # Clear the partial line
                        print("\r" + " " * 100 + "\r", end='')
                        
                        if text:
                            final_transcripts.append(text)
                            print(f"✅ Final: {text}")
                        
                        # Check if session is complete
                        if data.get('session_complete'):
                            print("\n" + "=" * 60)
                            print("SESSION COMPLETE")
                            print("=" * 60)
                            break
                    
                    else:
                        print(f"\n❓ Unknown type: {msg_type}")

            except websockets.exceptions.ConnectionClosedOK:
                print("\n✅ WebSocket closed normally")
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"\n❌ WebSocket closed with error: {e}")
            except Exception as e:
                print(f"\n❌ Error receiving messages: {e}")

            # Print final summary
            if final_transcripts:
                print("\n" + "=" * 60)
                print("COMPLETE TRANSCRIPTION:")
                print("=" * 60)
                complete_text = " ".join(final_transcripts)
                print(complete_text)
                print(f"\n📊 Word count: {len(complete_text.split())}")
                print(f"📊 Character count: {len(complete_text)}")
                print("=" * 60)
            else:
                print("\n⚠️  No transcription received")

    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_ws_client.py <audio_file.wav>")
        print("Example: python test_ws_client.py sample_audio.mp3")
        sys.exit(1)

    audio_file = sys.argv[1]
    
    print("🎤 WebSocket Transcription Client")
    print("=" * 60)
    
    asyncio.run(send_audio(audio_file))