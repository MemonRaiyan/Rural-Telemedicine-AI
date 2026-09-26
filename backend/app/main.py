import os
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.app.database.database import init_db
from backend.app.database.seed_data import seed_database
from backend.app.api.routes import api_router
from backend.app.websocket.consultation_ws import handle_consultation_websocket

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database and ensure seed data is available
    init_db()
    seed_database()
    yield

app = FastAPI(
    title="GramCare AI — Rural Telemedicine AI Platform",
    description="Academic Engineering Project II — Rural Healthcare Telemedicine Platform with ABDM Sandbox & Clinical AI",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware for local and network testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "static")
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include API Router
app.include_router(api_router, prefix="/api")

# WebSocket for Real-time Teleconsultation & Chat
@app.websocket("/ws/consultation/{consultation_id}")
async def websocket_consultation_endpoint(websocket: WebSocket, consultation_id: str):
    await handle_consultation_websocket(websocket, consultation_id)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "GramCare AI Platform",
        "version": "2.0.0",
        "abdm_environment": "ABDM Sandbox Ready",
        "database": "SQLite / WAL Mode Active",
        "academic_project": "B.Tech Engineering Project II"
    }

@app.get("/")
async def get_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>GramCare AI</h1><p>Static index.html not found.</p>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
