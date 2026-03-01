from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.webrtc_controller import router as webrtc_router
from .api.tts_controller import router as tts_router

app = FastAPI(title="Standalone STT + TTS")

# Allow browser requests (important for WebRTC testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # for testing only (standalone)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webrtc_router)
app.include_router(tts_router)


@app.get("/")
async def root():
    return {"status": "running"}
