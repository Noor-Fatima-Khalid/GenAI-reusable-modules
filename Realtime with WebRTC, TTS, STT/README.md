## TTS Streaming Architecture (Resampling + Timing)

### Overview
The system streams ElevenLabs TTS audio to the browser over WebRTC.  
To ensure correct speed, pitch, and smooth playback, audio must be resampled and delivered at precise real-time intervals.

---

### End-to-End Flow

Text  
→ ElevenLabs WebSocket  
→ PCM Audio (24 kHz, int16, mono)  
→ Backend Queue  
→ Resample **24 kHz → 48 kHz**  
→ Fixed-size framing (20 ms)  
→ WebRTC (aiortc)  
→ Browser Audio Playback

---

### Why Resampling?

| Source | Rate |
|---|---|
| ElevenLabs (multilingual v2) | 24,000 Hz |
| WebRTC required rate | 48,000 Hz |

If 24 kHz audio is sent as 48 kHz:
- Playback becomes **2× faster**
- Voice becomes **high-pitched/shrill**

**Solution:** Resample all incoming audio from **24 kHz → 48 kHz** before sending.

---

### Frame Timing (Real-Time Requirement)

WebRTC expects audio in fixed intervals:

- 48,000 samples/sec  
- 20 ms per frame  
- **960 samples per frame**

The audio track:
- Sends exactly **960 samples every 20 ms**
- Uses an internal clock
- Fills with silence if buffer is temporarily empty

This prevents:
- Audio cutting
- Speed changes
- Jitter or gaps

---

### Buffering Strategy

ElevenLabs sends variable-sized chunks.

Backend:
1. Accumulates chunks into a buffer
2. Resamples to 48 kHz
3. Emits fixed 960-sample frames at steady intervals

---

### Component Responsibilities

| Component | Role |
|---|---|
| ElevenLabs | Generate PCM audio (24 kHz) |
| TTS Route | Push chunks to session queue |
| QueueAudioTrack | Resample, buffer, pace frames |
| aiortc | WebRTC transport |
| Browser | Playback |

---

### Key Rules

- Always match **actual sample rate** with declared rate
- WebRTC audio must be **time-paced**, not chunk-driven
- Resample once, then stream at a fixed clock
- Use silence to handle temporary queue gaps

---

### Summary

ElevenLabs audio (24 kHz) is resampled to WebRTC’s native 48 kHz and streamed as precisely timed 20 ms frames (960 samples) to ensure correct speed, natural pitch, and stable real-time playback.
