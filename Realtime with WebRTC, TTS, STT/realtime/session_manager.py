import asyncio
from dataclasses import dataclass
from typing import Dict, Optional

from aiortc import RTCPeerConnection


@dataclass
class LiveSession:
    session_id: str
    pc: RTCPeerConnection
    stt_queue: asyncio.Queue
    tts_queue: asyncio.Queue
    closed: bool = False

    # flags to prevent duplicates
    deepgram_started: bool = False
    track_handler_added: bool = False


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, LiveSession] = {}
        self._lock = asyncio.Lock()

    async def create_or_get(self, *, session_id: str, pc_factory) -> LiveSession:
        async with self._lock:
            sess = self._sessions.get(session_id)
            if sess and not sess.closed:
                return sess

            pc = pc_factory()
            sess = LiveSession(
                session_id=session_id,
                pc=pc,
                stt_queue=asyncio.Queue(maxsize=400),
                tts_queue=asyncio.Queue(maxsize=800),
                closed=False,
            )
            self._sessions[session_id] = sess
            return sess

    async def get(self, session_id: str) -> Optional[LiveSession]:
        async with self._lock:
            return self._sessions.get(session_id)

    async def close(self, session_id: str) -> bool:
        async with self._lock:
            sess = self._sessions.get(session_id)
            if not sess or sess.closed:
                return False
            sess.closed = True

        try:
            await sess.pc.close()
        except Exception:
            pass

        # unblock outbound track
        try:
            sess.tts_queue.put_nowait(None)
        except Exception:
            pass

        return True


session_manager = SessionManager()