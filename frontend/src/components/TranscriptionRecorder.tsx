'use client';

import { useState, useRef, useEffect } from 'react';
import { Mic, Square } from 'lucide-react';

interface TranscriptionResult { 
  type: 'session_id' | 'partial' | 'final' | 'error'; 
  text?: string; 
  id?: string; 
  session_complete?: boolean;
}

export default function TranscriptionRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [partialText, setPartialText] = useState('');
  const [finalTranscript, setFinalTranscript] = useState<string[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [wordCount, setWordCount] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [audioChunksSent, setAudioChunksSent] = useState(0);
  
  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  
  const handleMessage = (event: MessageEvent) => {
    try {
      const result: TranscriptionResult = JSON.parse(event.data);
      console.log('📨 Received:', result);
      
      if (result.type === 'session_id' && result.id) {
        setSessionId(result.id);
        console.log('✅ Session ID:', result.id);
      } else if (result.type === 'partial' && result.text) {
        setPartialText(result.text);
        console.log('💬 Partial:', result.text);
      } else if (result.type === 'final' && result.text) {
        setFinalTranscript(prev => [...prev, result.text!]);
        setPartialText('');
        console.log('✅ Final:', result.text);
      } else if (result.type === 'error') {
        setError(result.text || 'An error occurred');
        console.error('❌ Error:', result.text);
      }
    } catch (err) {
      console.error('Error parsing message:', err);
    }
  };
  
  const startRecording = async () => {
    try {
      setError(null);
      setFinalTranscript([]);
      setPartialText('');
      setWordCount(0);
      setAudioChunksSent(0);
      
      console.log('🎤 Requesting microphone access...');
      
      // Get microphone stream
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        } 
      });
      
      streamRef.current = stream;
      console.log('✅ Microphone access granted');
      
      // Connect WebSocket
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/transcribe';
      console.log('🔌 Connecting to:', wsUrl);
      
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      
      ws.onopen = () => {
        console.log('✅ WebSocket connected');
      };
      
      ws.onmessage = handleMessage;
      
      ws.onerror = (err) => {
        console.error('❌ WebSocket error:', err);
        setError('WebSocket connection error');
      };
      
      ws.onclose = () => {
        console.log('🔌 WebSocket closed');
      };
      
      // Wait for WebSocket to connect
      await new Promise((resolve, reject) => {
        ws.addEventListener('open', resolve);
        ws.addEventListener('error', reject);
      });
      
      // ✅ Create AudioContext for RAW PCM audio
      const audioContext = new AudioContext({ sampleRate: 16000 });
      audioContextRef.current = audioContext;
      
      const source = audioContext.createMediaStreamSource(stream);
      
      // Create processor to get raw audio samples
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;
      
      processor.onaudioprocess = (e) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
        
        // Get raw audio samples as Float32Array
        const audioData = e.inputBuffer.getChannelData(0);
        
        // Convert Float32 (-1.0 to 1.0) to Int16 PCM
        const int16Array = new Int16Array(audioData.length);
        for (let i = 0; i < audioData.length; i++) {
          const s = Math.max(-1, Math.min(1, audioData[i]));
          int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        
        // Send raw PCM data
        wsRef.current.send(int16Array.buffer);
        setAudioChunksSent(prev => prev + 1);
        
        if (audioChunksSent % 10 === 0) {
          console.log(`🎵 Sent ${audioChunksSent} audio chunks`);
        }
      };
      
      // Connect audio nodes
      source.connect(processor);
      processor.connect(audioContext.destination);
      
      setIsRecording(true);
      console.log('✅ Recording started with PCM audio');
      
    } catch (err) {
      console.error('❌ Error starting recording:', err);
      setError('Failed to start recording. Please check microphone permissions.');
    }
  };
  
  const stopRecording = () => {
    console.log('🛑 Stopping recording...');
    
    // Stop audio processing first
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }
    
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => {
        track.stop();
        console.log('🔇 Audio track stopped');
      });
      streamRef.current = null;
    }

    // ✅ Send end signal and wait for server response before closing
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      console.log('📤 Sending end signal...');
      
      // Set up one-time listener for final result
      const handleFinalMessage = (event: MessageEvent) => {
        try {
          const result: TranscriptionResult = JSON.parse(event.data);
          console.log('📨 Final message received:', result);
          
          if (result.session_complete) {
            console.log('✅ Session complete, closing WebSocket');
            // Now safe to close
            if (wsRef.current) {
              wsRef.current.close();
              wsRef.current = null;
            }
          }
        } catch (err) {
          console.error('Error parsing final message:', err);
        }
      };
      
      // Listen for session complete message
      wsRef.current.addEventListener('message', handleFinalMessage);
      
      // Send end signal
      wsRef.current.send(JSON.stringify({ action: "end_audio" }));
      
      // Fallback: force close after 3 seconds if no response
      setTimeout(() => {
        if (wsRef.current) {
          console.log('⏰ Timeout - force closing WebSocket');
          wsRef.current.close();
          wsRef.current = null;
        }
      }, 3000);
    }

    setIsRecording(false);
    console.log('✅ Recording stopped');
  };
  
  useEffect(() => {
    const allText = [...finalTranscript, partialText].join(' ');
    const words = allText.trim().split(/\s+/).filter(w => w.length > 0);
    setWordCount(words.length);
  }, [finalTranscript, partialText]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Force cleanup on unmount
      if (processorRef.current) {
        processorRef.current.disconnect();
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ action: "end_audio" }));
        setTimeout(() => wsRef.current?.close(), 500);
      }
    };
  }, []);
  
  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          Real-Time Transcription
        </h1>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <div className="flex items-center gap-4 mb-6">
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
              isRecording
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : 'bg-blue-500 hover:bg-blue-600 text-white'
            }`}
          >
            {isRecording ? (
              <>
                <Square size={20} />
                Stop Recording
              </>
            ) : (
              <>
                <Mic size={20} />
                Start Recording
              </>
            )}
          </button>
          
          {isRecording && (
            <div className="flex items-center gap-2 text-red-500">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
              <span className="font-semibold">Recording...</span>
            </div>
          )}
        </div>
        
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-100 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Session ID</p>
            <p className="font-mono text-xs">{sessionId || 'Not started'}</p>
          </div>
          <div className="bg-gray-100 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Word Count</p>
            <p className="text-2xl font-bold">{wordCount}</p>
          </div>
          <div className="bg-gray-100 p-4 rounded-lg">
            <p className="text-sm text-gray-600">Audio Chunks</p>
            <p className="text-2xl font-bold">{audioChunksSent}</p>
          </div>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-6 min-h-[300px]">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">Transcript</h3>
          
          <div className="space-y-2">
            {finalTranscript.map((text, index) => (
              <p key={index} className="text-gray-800">
                {text}
              </p>
            ))}
            
            {partialText && (
              <p className="text-gray-500 italic">
                {partialText}
              </p>
            )}
            
            {!isRecording && finalTranscript.length === 0 && !partialText && (
              <p className="text-gray-400 text-center py-8">
                Click "Start Recording" to begin transcription
              </p>
            )}
          </div>
        </div>
        
        {/* Debug Info */}
        <div className="mt-4 p-4 bg-gray-100 rounded text-xs font-mono">
          <p>🔍 Debug Info:</p>
          <p>- Recording: {isRecording ? 'Yes' : 'No'}</p>
          <p>- Session: {sessionId || 'None'}</p>
          <p>- Chunks sent: {audioChunksSent}</p>
          <p>- WebSocket: {wsRef.current?.readyState === WebSocket.OPEN ? 'Connected' : 'Disconnected'}</p>
        </div>
      </div>
    </div>
  );
}