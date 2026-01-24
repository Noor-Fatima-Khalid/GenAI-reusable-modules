import asyncio
import json
import websockets
import os
from dotenv import load_dotenv

load_dotenv()
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
DEEPGRAM_WS_URL = (
    "wss://api.deepgram.com/v1/listen"
    "?encoding=linear16"
    "&sample_rate=16000"
    "&channels=1"
    "&interim_results=true"
    "&punctuate=true"
)

async def run_deepgram(audio_queue):
    try:
        async with websockets.connect(
            DEEPGRAM_WS_URL,
            additional_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"},
            open_timeout=10,
            ping_interval=20
        ) as ws:
            print("🟢 Connected to Deepgram")

            async def send_audio():
                while True:
                    chunk = await audio_queue.get()
                    if chunk is None:
                        break
                    try:
                        await ws.send(chunk)
                    except websockets.exceptions.ConnectionClosed:
                        break

            async def receive():
                async for msg in ws:
                    data = json.loads(msg)
                    if "channel" in data:
                        alt = data["channel"]["alternatives"][0]
                        text = alt.get("transcript", "")
                        if text and data.get("is_final"):
                            print("🟢 FINAL:", text)

            sender = asyncio.create_task(send_audio())
            receiver = asyncio.create_task(receive())

            done, pending = await asyncio.wait(
                [sender, receiver],
                return_when=asyncio.FIRST_COMPLETED
            )

            for task in pending:
                task.cancel()
            print("🔚 Deepgram session closed")

    except Exception as e:
        print("❌ Deepgram error:", e)
