# this version is standalone and does not use node backend. To connect it to backend, a webhook will be used.

import os
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "9J08XLaVNO9dwqz7kWR7")

# Where to send transcripts (Node endpoint)
# Example: http://localhost:5000/api/interview/transcript
NODE_TRANSCRIPT_WEBHOOK = os.getenv("NODE_TRANSCRIPT_WEBHOOK", "")

# Optional auth token to include when posting transcripts to Node
NODE_WEBHOOK_TOKEN = os.getenv("NODE_WEBHOOK_TOKEN", "")

SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "22050"))
CHANNELS = int(os.getenv("AUDIO_CHANNELS", "1"))


NODE_TRANSCRIPT_URL = os.getenv("NODE_TRANSCRIPT_URL")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID", "9J08XLaVNO9dwqz7kWR7")
