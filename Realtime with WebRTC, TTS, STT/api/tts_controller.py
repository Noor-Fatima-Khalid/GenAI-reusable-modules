import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..realtime.session_manager import session_manager
from ..realtime.tts.elevenlabs_stream import elevenlabs_pcm_stream

router = APIRouter()


class SpeakRequest(BaseModel):
    session_id: str
    text: str


@router.post("/tts/speak")
async def speak(req: SpeakRequest):
    """
    Standalone TTS endpoint.

    Usage for testing:
    1) First create WebRTC session via /webrtc/offer
    2) Then call this endpoint with the SAME session_id
    3) Audio will be streamed to browser via WebRTC
    """

    session_id = req.session_id.strip()
    text = req.text.strip()

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    if not text:
        raise HTTPException(status_code=400, detail="text is empty")

    # Get existing WebRTC session
    sess = await session_manager.get(session_id)
    if not sess or sess.closed:
        raise HTTPException(
            status_code=404,
            detail="WebRTC session not found. Call /webrtc/offer first."
        )

    print(f"[TTS] Session: {session_id}")
    print(f"[TTS] Text: {text}")

    async def _stream_into_queue():
        try:
            async for pcm_chunk in elevenlabs_pcm_stream(text):
                try:
                    sess.tts_queue.put_nowait(pcm_chunk)
                except asyncio.QueueFull:
                    pass

            # IMPORTANT: add 500ms silence so last words are not cut
            silence = b"\x00\x00" * int(22050 * 0.5)  # 0.5 sec at 22050
            try:
                sess.tts_queue.put_nowait(silence)
            except asyncio.QueueFull:
                pass

            print(f"[TTS] Completed for session {session_id}")

        except Exception as e:
            print("❌ TTS stream error:", e)

    # Run streaming in background (non-blocking)
    asyncio.create_task(_stream_into_queue())

    return {
        "ok": True,
        "session_id": session_id,
        "message": "TTS streaming started"
    }
