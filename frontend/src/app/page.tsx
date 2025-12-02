'use client';

import { useState } from 'react';
import TranscriptionRecorder from '../components/TranscriptionRecorder';
import SessionList from '../components/SessionList';


export default function Home() {
  const [activeTab, setActiveTab] = useState<'recorder' | 'history'>('recorder');

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🎤 Real-Time Transcription
          </h1>
          <p className="text-gray-600">
            CPU-based speech-to-text
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-6">
          <div className="bg-white rounded-lg shadow-md p-1 inline-flex">
            <button
              onClick={() => setActiveTab('recorder')}
              className={`px-6 py-2 rounded-md font-semibold transition-all ${
                activeTab === 'recorder'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Record
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`px-6 py-2 rounded-md font-semibold transition-all ${
                activeTab === 'history'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              History
            </button>
          </div>
        </div>

        {/* Content */}
        <div>
          {activeTab === 'recorder' ? (
            <TranscriptionRecorder />
          ) : (
            <SessionList />
          )}
        </div>

        {/* Footer */}
        <footer className="text-center mt-12 text-gray-500 text-sm">
          <p>enjoy your transcription experience!</p>
        </footer>
      </div>
    </main>
  );
}