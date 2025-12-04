# 🔧 Backend Documentation

Fast API-based backend for real-time speech-to-text transcription using Vosk AI model and PostgreSQL.

## 📂 Project Structure
```
backend/
├── app/
│   ├── models/         # SQLAlchemy database models
│   ├── routes/         # API endpoints (sessions, websocket)
│   ├── schemas/        # Pydantic validation schemas
│   ├── services/       # Business logic (transcription, sessions, audio)
│   └── utils/          # Helper functions
├── models/             # Vosk model (vosk-model-small-en-us-0.15)
├── .env                # Environment configuration
├── config.py           # Settings management
├── database.py         # Database setup
├── main.py             # Application entry point
└── requirements.txt    # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL
- FFmpeg

### Installation

1. **Clone and navigate:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**

Create `.env` file:
```bash
DATABASE_URL=postgresql://username:password@hostname:port/database_name
MODEL_PATH=./models/vosk-model-small-en-us-0.15
cors_origins=["http://localhost:3000"]
HOST=0.0.0.0
PORT=8000
```

5. **Run application:**
```bash
uvicorn main:app --reload  # Development
uvicorn main:app --host 0.0.0.0 --port 8000  # Production
```

## 📡 API Endpoints

### REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sessions` | Get all sessions (supports pagination) |
| GET | `/sessions/{id}` | Get session by ID |
| DELETE | `/sessions/{id}` | Delete session |
| GET | `/docs` | Interactive API documentation |

### WebSocket

**Endpoint:** `ws://localhost:8000/ws/transcribe`

**Usage:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/transcribe');

// Send audio bytes (PCM 16-bit, 16kHz, mono)
ws.send(audioBuffer);

// Receive results
ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  // result: { type: "partial" | "final", text: "..." }
};
```

## 🗄️ Database Schema
```sql
transcription_sessions
├── id (UUID, PK)
├── transcript (TEXT)
├── word_count (INT)
├── duration (FLOAT)
├── session_metadata (JSON)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)
```

## 🔧 Core Components

### Transcription Service
- Real-time speech-to-text using Vosk
- CPU-optimized, offline processing
- Sample rate: 16kHz, 16-bit PCM

### Session Service
- CRUD operations for transcription sessions
- PostgreSQL persistence with SQLAlchemy

### Audio Processing
- FFmpeg-based audio conversion
- Converts any format to Vosk-compatible PCM

## 🐳 Docker

**Build:**
```bash
docker build -t transcription-app-backend .
```

**Run:**
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host/db" \
  -e MODEL_PATH="./models/vosk-model-small-en-us-0.15" \
  transcription-app-backend
```

## ⚙️ Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `MODEL_PATH` | Vosk model directory path | Yes |
| `cors_origins` | Allowed CORS origins (JSON array) | Yes |
| `HOST` | Server host | No (default: 0.0.0.0) |
| `PORT` | Server port | No (default: 8000) |

## 🧪 Testing

**WebSocket test:**
```bash
python test_ws_client.py
```

**Interactive docs:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| FFmpeg not found | Install FFmpeg and add to PATH |
| Model not found | Verify `MODEL_PATH` in `.env` |
| Database connection error | Check `DATABASE_URL` and PostgreSQL status |
| CORS error | Add frontend URL to `cors_origins` |

# ⚡ Async Architecture

This project uses **async/await** everywhere for maximum performance and scalability.

## Key Features

### ✓ FastAPI Async Routes
All endpoints are non-blocking, allowing **thousands of concurrent connections**.

### ✓ Async SQLAlchemy (2.0+)
```python
async_engine = create_async_engine(settings.database_url)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)
```

### ✓ Async WebSocket Streaming
Real-time transcription uses asynchronous receive/send for **smooth audio streaming**.

### ✓ Non-blocking Audio Processing Pipeline
FFmpeg calls run in **async subprocess mode** to avoid blocking the event loop.

### ✓ Exception Handling
Route-level error handling with try-catch blocks for robust error management.

**Benefits:**
- ⚡ Faster response time
- 📈 High throughput
- 🚀 Better performance under real-time load
- 🛡️ Graceful error handling

## 📖 Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Vosk API](https://alphacephei.com/vosk/models)
- [Project Repository](https://github.com/marziasu/Transcription_App)

---

For issues, visit [GitHub Issues](https://github.com/marziasu/Transcription_App/issues)
