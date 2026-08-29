import asyncio
import json
from typing import Set
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

router = APIRouter()

class EventNotifier:
    def __init__(self):
        self._subscribers: Set[asyncio.Queue] = set()

    async def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self._subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        self._subscribers.discard(q)

    async def broadcast(self, event_type: str, data: dict):
        message = json.dumps({"event": event_type, "data": data})
        for q in list(self._subscribers):
            try:
                await q.put(message)
            except Exception:
                self._subscribers.discard(q)

notifier = EventNotifier()

@router.get("/stream")
async def events_stream(request: Request):
    """Server-Sent Events endpoint for real-time queue & task updates."""
    queue = await notifier.subscribe()

    async def event_generator():
        try:
            # Send initial ping
            yield "data: {\"event\": \"connected\"}\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=20.0)
                    yield f"data: {data}\n\n"
                except asyncio.TimeoutError:
                    # Keep-alive heartbeat comment
                    yield ": keep-alive\n\n"
        finally:
            notifier.unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
