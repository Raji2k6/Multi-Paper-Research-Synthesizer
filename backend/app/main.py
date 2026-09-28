from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.upload import router as upload_router
from app.api.chat import router as chat_router
from app.api.synthesis import router as synthesis_router


app = FastAPI(
    title="Multi-Paper Research Synthesizer API",
    version="1.0.0",
    description="Backend API for Multi-Paper Research Synthesizer"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React Vite
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(synthesis_router)

@app.get("/")
def root():
    return {
        "message": "Multi-Paper Research Synthesizer API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }