// src/components/SessionList.tsx
'use client';

import { useEffect, useState } from 'react';
import { Clock, FileText, Trash2, RefreshCw } from 'lucide-react';
import { ApiService, Session } from '../services/api';

export default function SessionList() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedSession, setSelectedSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    fetchSessions();
  }, []);
  
  const fetchSessions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await ApiService.getAllSessions();
      setSessions(data);
    } catch (err) {
      setError('Failed to load sessions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this session?')) {
      return;
    }
    
    try {
      await ApiService.deleteSession(id);
      setSessions(sessions.filter(s => s.id !== id));
      if (selectedSession?.id === id) {
        setSelectedSession(null);
      }
    } catch (err) {
      alert('Failed to delete session');
      console.error(err);
    }
  };
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return 'Invalid date';
    }
    return date.toLocaleString();
  };
  
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };
  
  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading sessions...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-bold text-gray-800">
            Transcription History
          </h2>
          <button
            onClick={fetchSessions}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <RefreshCw size={18} />
            Refresh
          </button>
        </div>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        {sessions.length === 0 ? (
          <div className="text-center py-12">
            <FileText size={48} className="mx-auto text-gray-300 mb-4" />
            <p className="text-gray-500 text-lg">No transcription sessions yet</p>
            <p className="text-gray-400 text-sm mt-2">
              Start recording to create your first session
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Sessions List */}
            <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  onClick={() => setSelectedSession(session)}
                  className={`border rounded-lg p-4 cursor-pointer transition-all hover:shadow-md ${
                    selectedSession?.id === session.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-2">
                      <FileText size={20} className="text-blue-500" />
                      <span className="font-mono text-sm text-gray-600">
                        {session.id.slice(0, 8)}...
                      </span>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(session.id);
                      }}
                      className="text-red-500 hover:text-red-700 transition-colors"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                  
                  <div className="space-y-1 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <Clock size={14} />
                      <span>{formatDate(session.created_at)}</span>
                    </div>
                    <div className="flex gap-4">
                      <span>Words: {session.word_count}</span>
                      <span>Duration: {formatDuration(session.duration)}</span>
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-700 mt-2 line-clamp-2">
                    {session.transcript || 'No transcript available'}
                  </p>
                </div>
              ))}
            </div>
            
            {/* Selected Session Details */}
            <div className="border rounded-lg p-6 bg-gray-50 max-h-[600px] overflow-y-auto">
              {selectedSession ? (
                <>
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">
                    Transcript Details
                  </h3>
                  
                  <div className="space-y-3 mb-6">
                    <div>
                      <p className="text-sm text-gray-600">Session ID</p>
                      <p className="font-mono text-sm">{selectedSession.id}</p>
                    </div>
                    
                    <div>
                      <p className="text-sm text-gray-600">Created</p>
                      <p className="text-sm">{formatDate(selectedSession.created_at)}</p>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-600">Words</p>
                        <p className="text-2xl font-bold text-blue-600">
                          {selectedSession.word_count}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Duration</p>
                        <p className="text-2xl font-bold text-blue-600">
                          {formatDuration(selectedSession.duration)}
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <p className="text-sm text-gray-600 mb-2">Full Transcript</p>
                    <div className="bg-white rounded-lg p-4 border">
                      <p className="text-gray-800 whitespace-pre-wrap">
                        {selectedSession.transcript || 'No transcript available'}
                      </p>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => handleDelete(selectedSession.id)}
                    className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                  >
                    <Trash2 size={18} />
                    Delete Session
                  </button>
                </>
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-500">
                    Select a session to view details
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}