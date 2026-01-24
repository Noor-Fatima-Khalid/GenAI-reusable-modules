import asyncio
import json
import os
from aiohttp import web
import aiohttp_cors
from aiortc import RTCPeerConnection, MediaStreamTrack, RTCSessionDescription
import websockets
from dotenv import load_dotenv
import numpy as np
from av.audio.resampler import AudioResampler

# =========================
# ENV
# =========================
load_dotenv()
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
if not DEEPGRAM_API_KEY:
    raise RuntimeError("❌ DEEPGRAM_API_KEY not found")

print("### ENV LOADED ###")

# =========================
# CONFIG
# =========================
SRC_SAMPLE_RATE = 48000
TARGET_SAMPLE_RATE = 16000

DEEPGRAM_WS_URL = (
    "wss://api.deepgram.com/v1/listen"
    "?encoding=linear16"
    "&sample_rate=16000"
    "&channels=1"
    "&interim_results=true"
    "&punctuate=true"
)

# =========================
# DEEPGRAM
# =========================
async def deepgram_stt(audio_queue):
    try:
        async with websockets.connect(
            DEEPGRAM_WS_URL,
            additional_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"},
            open_timeout=10,       # give 10 seconds to complete handshake
            ping_interval=20,
        ) as ws:
            print("🟢 Connected to Deepgram")

            async def send_audio():
                # frames_sent = 0
                while True:
                    chunk = await audio_queue.get()
                    if chunk is None:
                        break
                    try:
                        await ws.send(chunk)
                        # frames_sent += 1
                        # if frames_sent % 100 == 0:  # log every 100 sends
                        #     print(f"📤 Sent {frames_sent} audio chunks")
                    except websockets.exceptions.ConnectionClosed:
                        break

            async def receive():
                async for msg in ws:
                    data = json.loads(msg)
                    if "channel" in data:
                        alt = data["channel"]["alternatives"][0]
                        text = alt.get("transcript", "")
                        if text:
                            if data.get("is_final"):
                                print("🟢 FINAL:", text)
                            else:
                                # optional partials, comment out to reduce spam
                                # print("⚪ PARTIAL:", text)
                                pass

            sender = asyncio.create_task(send_audio())
            receiver = asyncio.create_task(receive())

            done, pending = await asyncio.wait(
                [sender, receiver],
                return_when=asyncio.FIRST_COMPLETED
            )

            for task in pending:
                task.cancel()

            print("🔚 Deepgram session closed cleanly")

    except Exception as e:
        print("❌ Deepgram fatal error:", e)

# =========================
# WEBRTC
# =========================
async def stream_audio(track, queue):
    print("🎧 Initializing AV resampler (48k → 16k)")

    resampler = AudioResampler(
        format="s16",
        layout="mono",
        rate=16000
    )

    # frame_counter = 0
    try:
        while True:
            frame = await track.recv()
            for resampled in resampler.resample(frame):
                pcm = resampled.to_ndarray()
                if pcm.ndim > 1:
                    pcm = pcm[0]
                await queue.put(pcm.tobytes())
            # frame_counter += 1
            # if frame_counter % 100 == 0:  # log every 100 frames (~1 sec)
            #     print("🎧 Audio frames flowing...")

    except Exception:
        print("🎤 Audio track ended")
    finally:
        await queue.put(None)  # THIS STOPS DEEPGRAM CLEANLY


async def offer(request):
    print("### /offer hit ###")
    params = await request.json()
    pc = RTCPeerConnection()
    audio_queue = asyncio.Queue()

    @pc.on("track")
    def on_track(track):
        print("🎤 Track received:", track.kind)
        if track.kind == "audio":
            asyncio.create_task(stream_audio(track, audio_queue))

    asyncio.create_task(deepgram_stt(audio_queue))

    await pc.setRemoteDescription(
        RTCSessionDescription(params["sdp"], params["type"])
    )
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })

# =========================
# APP + CORS
# =========================
app = web.Application()

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

cors.add(app.router.add_post("/offer", offer))

# =========================
# RUN
# =========================
if __name__ == "__main__":
    print("🚀 Server running at http://localhost:8080")
    web.run_app(app, port=8080)
