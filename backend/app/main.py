from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .database import init_db
from .routes import websocket_router, sessions_router
from contextlib import asynccontextmanager
from .database import init_db, dispose_engine, check_db_connection


settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Starting application...")
    init_db()
    
    if check_db_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application...")
    dispose_engine()
    print("✅ Connection pool disposed")

app = FastAPI(
    title="Real-Time Transcription API",
    description="CPU-based real-time speech-to-text service using Vosk",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(websocket_router, tags=["websocket"])
app.include_router(sessions_router, tags=["sessions"])

@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Real-Time Transcription API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
