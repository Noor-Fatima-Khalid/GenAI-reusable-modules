from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
import asyncio
from .webrtc import stream_audio
from .deepgram import run_deepgram

async def offer(request):
    params = await request.json()
    pc = RTCPeerConnection()
    audio_queue = asyncio.Queue()

    @pc.on("track")
    def on_track(track):
        if track.kind == "audio":
            asyncio.create_task(stream_audio(track, audio_queue))

    asyncio.create_task(run_deepgram(audio_queue))

    await pc.setRemoteDescription(RTCSessionDescription(params["sdp"], params["type"]))
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })
