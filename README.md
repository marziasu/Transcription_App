# 🎙️ Real-Time Transcription Application

A high-performance, CPU-based real-time speech-to-text web application. This project leverages **FastAPI** for a robust backend and **Next.js** for a responsive frontend. It features live audio streaming via WebSockets, real-time transcription using the Vosk model, and persistent session management using PostgreSQL (hosted on Render).

## 🔗 Live Demo

Experience the application live:

- **Frontend:** [https://transcription-app-frontend-latest.onrender.com](https://transcription-app-frontend-latest.onrender.com)
- **Backend API:** [https://transcription-app-backend-latest.onrender.com/docs](https://transcription-app-backend-latest.onrender.com/docs)

## ✨ Features

- **Real-Time Transcription:** Low-latency speech-to-text conversion using the Vosk offline model
- **WebSocket Streaming:** Seamless audio data transfer between client and server
- **Session Management:** Save and retrieve past transcription sessions
- **Persistent Storage:** Data is securely stored using PostgreSQL (managed by Render)
- **Dockerized:** Fully containerized for easy deployment

## 📸 Application Preview

<div align="center">
  <img src="./assets/screenshots/transcription-historoy.png" alt="Session History" width="700" />
  <p><em>Transcription History Dashboard</em></p>

   <img src="./assets/screenshots/realtime-transcription.png" alt="Real-Time Transcription" width="700" />
  <p><em>Real-Time Transcription Interface</em></p>
</div>


## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Next.js, React, Tailwind CSS |
| **Backend** | FastAPI, Python, WebSockets |
| **AI Model** | Vosk (Small English Model) |
| **Database** | PostgreSQL (Hosted on Render) |
| **DevOps** | Docker, Docker Compose, Render |

## 📂 Repository Structure
```bash
transcription-app/
├── backend/              # FastAPI backend application
├── frontend/             # Next.js frontend application
├── docker-compose.yml    # Docker orchestration
└── README.md            # Project documentation
```

For specific details on implementation, refer to the component READMEs:
- [Backend Documentation](./backend/README.md)
- [Frontend Documentation](./frontend/README.md)

## 🚀 Quick Start (Docker Compose)

The easiest way to run the full stack locally is via Docker Compose.

1. **Clone the repository:**
```bash
git clone https://github.com/marziasu/Transcription_App.git
cd Transcription_App
```

2. **Set up environment variables:**

Create a `.env` file in the **backend directory**:
```bash
cd backend
```
```bash
DATABASE_URL=postgresql://username:password@hostname/db_name
MODEL_PATH=./models/vosk-model-small-en-us-0.15
cors_origins=["http://localhost:3000"]
HOST=0.0.0.0
PORT=8000
```

Create a `.env.local` file in the **frontend directory**:
```bash
cd frontend
```
```bash
PORT=3000
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/transcribe
```
```bash
cd ..
```

> **Note:** Replace the `DATABASE_URL` with your actual PostgreSQL connection string.

3. **Start the services:**
```bash
docker-compose up --build
```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/docs

## 🐳 Running via Docker Hub

If you prefer to pull the pre-built images directly from Docker Hub, use the commands below.

### 1. Run Backend

> **Note:** You must provide your PostgreSQL connection string.
```bash
docker pull marzias/transcription-app-backend:latest

docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://username:password@hostname/db_name" \
  -e MODEL_PATH="./models/vosk-model-small-en-us-0.15" \
  marzias/transcription-app-backend:latest
```

### 2. Run Frontend

> **Note:** Ensure the backend URL matches where your backend is running.
```bash
docker pull marzias/transcription-app-frontend:latest

docker run -p 3000:3000 \
  -e PORT=3000 \
  -e NEXT_PUBLIC_API_URL="https://transcription-app-backend-latest.onrender.com" \
  -e NEXT_PUBLIC_WS_URL="wss://transcription-app-backend-latest.onrender.com/ws/transcribe" \
  marzias/transcription-app-frontend:latest
```

## 💻 Manual Setup (Local Development)

If you wish to run the code without Docker, follow these steps.

### Prerequisites

- Node.js & npm
- Python 3.9+
- PostgreSQL Database (Local or Cloud)

### 1. Backend Setup

Navigate to the backend directory:
```bash
cd backend
```

Create a `.env` file:
```bash
DATABASE_URL=postgresql://username:password@dpg-.../db_name
MODEL_PATH=./models/vosk-model-small-en-us-0.15
cors_origins=["http://localhost:3000"]
HOST=0.0.0.0
PORT=8000
```

Install dependencies and run:
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

> **Note:** Ensure the Vosk model is downloaded and placed in the `models/` directory.

### 2. Frontend Setup

Navigate to the frontend directory:
```bash
cd ../frontend
```

Create a `.env.local` file:
```bash
PORT=3000
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/transcribe
```

Install dependencies and run:
```bash
npm install
npm run dev
```

## ⚙️ Environment Variables

### Backend (`.env`)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (Recommended: Render PostgreSQL) |
| `MODEL_PATH` | Path to the Vosk speech model directory |
| `cors_origins` | List of allowed origins (e.g., `["http://localhost:3000"]`) |

### Frontend (`.env.local`)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | HTTP URL for the Backend API |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL for the Backend API |
| `PORT` | Port for the Next.js server (Default: 3000) |

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/marziasu/Transcription_App/issues).

## 👤 Author

**Marzia**

- GitHub: [@marziasu](https://github.com/marziasu)

---

⭐️ If you found this project helpful, please consider giving it a star!
