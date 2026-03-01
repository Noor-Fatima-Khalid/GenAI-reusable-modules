import asyncio

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from aiortc import RTCPeerConnection, RTCSessionDescription

from ..realtime.session_manager import session_manager
from ..STT.webrtc_handler import stream_audio
from ..STT.deepgram_client import run_deepgram
from ..realtime.tts.tts_track import QueueAudioTrack

router = APIRouter()


class OfferRequest(BaseModel):
    session_id: str  # use Node interview_id here
    sdp: str
    type: str


@router.post("/webrtc/offer")
async def webrtc_offer(body: OfferRequest):
    session_id = body.session_id.strip()
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    def pc_factory():
        return RTCPeerConnection()

    sess = await session_manager.create_or_get(session_id=session_id, pc_factory=pc_factory)
    pc = sess.pc

    # 1) Add outbound TTS track ONCE
    if not any(s.track and s.track.kind == "audio" for s in pc.getSenders()):
        pc.addTrack(QueueAudioTrack(sess.tts_queue))

    # 2) Add inbound track handler ONCE
    if not sess.track_handler_added:

        @pc.on("track")
        def on_track(track):
            if track.kind == "audio":
                print("🎤 Starting audio stream")
                asyncio.create_task(stream_audio(track, sess.stt_queue))

        sess.track_handler_added = True

    # 3) Start Deepgram ONCE
    if not sess.deepgram_started:
        sess.deepgram_started = True
        asyncio.create_task(run_deepgram(sess.stt_queue, sess.session_id))

    # 4) WebRTC answer
    await pc.setRemoteDescription(RTCSessionDescription(body.sdp, body.type))
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}