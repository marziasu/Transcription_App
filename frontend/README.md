# Frontend Documentation

Modern Next.js web application for real-time audio transcription with WebSocket streaming and session management.

## 📂 Project Structure
```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx           # Home page
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles
│   ├── components/
│   │   ├── TranscriptionRecorder.tsx  # Real-time recording UI
│   │   └── SessionList.tsx            # Session history browser
│   ├── services/
│   │   └── api.ts             # REST API client
│   └── lib/
│       └── websocket.ts       # WebSocket wrapper
├── .env.local                 # Environment variables
├── Dockerfile                 # Docker configuration
├── next.config.js             # Next.js config
├── tailwind.config.js         # Tailwind CSS config
└── package.json               # Dependencies
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm 9+
- Modern browser with microphone access

### Installation

1. **Clone and navigate:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Configure environment:**

Create `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/transcribe
PORT=3000
```

4. **Run application:**
```bash
npm run dev              # Development
npm run build && npm start  # Production
```

## 📡 API Integration

### REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sessions` | Fetch all transcription sessions |
| GET | `/sessions/{id}` | Fetch specific session |
| DELETE | `/sessions/{id}` | Delete session |

### WebSocket

**Endpoint:** `ws://localhost:8000/ws/transcribe`

**Protocol:**
```javascript
// Send audio (PCM 16-bit, 16kHz, mono)
ws.send(audioBuffer);

// Receive transcription results
ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  // { type: "session_id" | "partial" | "final", text: "..." }
};
```

## 🎨 Key Components

### TranscriptionRecorder
- Real-time audio capture and streaming
- WebSocket connection management
- Live transcript display (partial + final)
- Word count tracking
- Recording controls

### SessionList
- Browse all transcription sessions
- Detailed transcript viewer
- Session deletion with confirmation
- Real-time statistics (word count, duration)

## 🔧 Technical Details

### API Service (`services/api.ts`)
- **HTTP Client:** Native `fetch` API
- **Base URL:** Configured via `NEXT_PUBLIC_API_URL`
- **Endpoints:**
  - `GET /sessions` - Fetch all sessions
  - `GET /sessions/:id` - Fetch specific session
  - `DELETE /sessions/:id` - Delete session
- **Error Handling:** Built-in try-catch with error messages

### State Management
- **Approach:** Local React state using `useState` hooks
- **No global state library** (Context API, Redux, Zustand not used)
- **Session state** managed in `SessionList` component
- **Recording state** managed in `TranscriptionRecorder` component

### Audio Processing
- **API:** Web Audio API + ScriptProcessorNode
- **Format:** Raw PCM (16-bit signed integer)
- **Sample Rate:** 16,000 Hz (16kHz)
- **Channels:** Mono (1 channel)
- **Processing:** Real-time audio chunks (4096 samples)
- **Features:** Echo cancellation, noise suppression enabled

### WebSocket Implementation
- **Client:** Native WebSocket API
- **Wrapper:** Custom `TranscriptionWebSocket` class in `lib/websocket.ts`
- **Message Types:**
  - `session_id` - Initial session assignment
  - `partial` - Interim transcription results
  - `final` - Complete transcription segments
  - `error` - Error messages

### Additional Features
- ✅ Real-time partial transcription display
- ✅ Final transcription aggregation
- ✅ Word count tracking
- ✅ Audio chunk monitoring
- ✅ Session history browsing
- ✅ Session deletion with confirmation

  
## 🐳 Docker

**Build:**
```bash
docker build -t transcription-app-frontend .
```

**Run:**
```bash
docker run -p 3000:3000 \
  -e PORT=3000
  -e NEXT_PUBLIC_API_URL=http://backend:8000 \
  -e NEXT_PUBLIC_WS_URL=ws://backend:8000/ws/transcribe \
  transcription-app-frontend
```

## ⚙️ Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend REST API endpoint | Yes |
| `NEXT_PUBLIC_WS_URL` | WebSocket transcription endpoint | Yes |
| `PORT` | Frontend server port | No (default: 3000) |

## 🧪 Available Scripts
```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Microphone not working | Grant permissions, use HTTPS/localhost |
| WebSocket connection failed | Check backend URL and CORS settings |
| Build errors | Clear cache: `rm -rf .next node_modules && npm install` |
| Audio not streaming | Verify PCM format (16-bit, 16kHz, mono) |

## 📚 Tech Stack

- **Framework:** Next.js 14.0.4
- **UI Library:** React 18.2.0
- **Language:** TypeScript 5.3.3
- **Styling:** Tailwind CSS 3.4.18
- **Icons:** Lucide React 0.294.0
- **Audio:** Web Audio API + WebSocket

## 📖 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Project Repository](https://github.com/marziasu/Transcription_App)

---

For issues, visit [GitHub Issues](https://github.com/marziasu/Transcription_App/issues)
