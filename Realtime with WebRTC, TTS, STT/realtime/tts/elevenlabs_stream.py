# ElevenLabs websocket streaming (pcm_22050)

import os
import json
import base64
import websockets

from ...core.config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID


async def elevenlabs_pcm_stream(text: str):
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY not set")

    url = (
        f"wss://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream-input"
        f"?model_id=eleven_multilingual_v2"
        f"&output_format=pcm_24000"
    )
    headers = {"xi-api-key": ELEVENLABS_API_KEY}

    async with websockets.connect(url, additional_headers=headers) as ws:
        # Send text
        await ws.send(json.dumps({
            "text": text,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }))
        await ws.send(json.dumps({"text": ""}))

        # 🔧 BUFFER FIX
        buffer = b""
        MIN_CHUNK_SIZE = 12000  # ~270ms audio

        async for msg in ws:
            data = json.loads(msg)

            if "audio" in data and data["audio"]:
                audio_bytes = base64.b64decode(data["audio"])
                buffer += audio_bytes

                # Yield only when enough audio accumulated
                if len(buffer) >= MIN_CHUNK_SIZE:
                    yield buffer
                    buffer = b""

            if data.get("isFinal"):
                break

        # Flush remaining audio
        if buffer:
            yield buffer