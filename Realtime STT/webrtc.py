from aiortc import MediaStreamTrack
from av.audio.resampler import AudioResampler
import asyncio

async def stream_audio(track: MediaStreamTrack, queue: asyncio.Queue):
    print("🎧 Initializing resampler (48k → 16k)")
    resampler = AudioResampler(format="s16", layout="mono", rate=16000)
    try:
        while True:
            frame = await track.recv()
            for resampled in resampler.resample(frame):
                pcm = resampled.to_ndarray()
                if pcm.ndim > 1:
                    pcm = pcm[0]
                await queue.put(pcm.tobytes())
    except Exception:
        print("🎤 Audio track ended")
    finally:
        await queue.put(None)  # signal Deepgram to stop
