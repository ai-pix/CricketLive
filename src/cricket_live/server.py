"""FastAPI + WebSocket server for the live cricket broadcast overlay."""

from __future__ import annotations

import asyncio
import json
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from .commentary import (
    CommentaryTurn,
    generate_commentary_turns,
    generate_filler_dialogue,
    synthesize_fish_audio,
)
from .models import ScoreboardState
from .sources import get_source_mode, run_cricapi_poller, run_playwright_reader, run_simulator

load_dotenv()

UI_DIR = Path(__file__).resolve().parents[2] / "ui"


class ConnectionManager:
    def __init__(self) -> None:
        self.active: set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self.active.discard(ws)

    async def broadcast_text(self, payload: str) -> None:
        stale: list[WebSocket] = []
        for ws in list(self.active):
            try:
                await ws.send_text(payload)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self.disconnect(ws)

    async def broadcast(self, state: ScoreboardState) -> None:
        await self.broadcast_text(state.model_dump_json())


state = ScoreboardState()
prev_state: ScoreboardState | None = None
manager = ConnectionManager()
commentary_clips: dict[int, bytes] = {}
clip_counter = 0
last_commentary_at = time.monotonic()
filler_index = 0


async def _speak_and_broadcast(turns: list[CommentaryTurn]) -> None:
    global clip_counter, last_commentary_at
    last_commentary_at = time.monotonic()
    for speaker, text in turns:
        audio_bytes = await synthesize_fish_audio(text, speaker=speaker)
        audio_url = None
        if audio_bytes:
            clip_counter += 1
            commentary_clips[clip_counter] = audio_bytes
            if len(commentary_clips) > 20:
                oldest = next(iter(commentary_clips))
                commentary_clips.pop(oldest, None)
            audio_url = f"/api/commentary/audio/{clip_counter}"
        await manager.broadcast_text(
            json.dumps(
                {
                    "type": "commentary",
                    "speaker": speaker,
                    "text": text,
                    "audio_url": audio_url,
                }
            )
        )


async def _emit_commentary(prev: ScoreboardState | None, curr: ScoreboardState) -> None:
    turns = generate_commentary_turns(prev, curr)
    if turns:
        await _speak_and_broadcast(turns)


async def _filler_loop(interval: float = 22.0) -> None:
    global filler_index
    while True:
        await asyncio.sleep(5.0)
        if not manager.active:
            continue
        if time.monotonic() - last_commentary_at >= interval:
            turns = generate_filler_dialogue(state, filler_index)
            filler_index += 1
            await _speak_and_broadcast(turns)


async def broadcast_state(new_state: ScoreboardState) -> None:
    global prev_state
    snapshot_prev = prev_state
    snapshot_curr = new_state.model_copy(deep=True)
    prev_state = snapshot_curr
    await manager.broadcast(new_state)
    asyncio.create_task(_emit_commentary(snapshot_prev, snapshot_curr))


@asynccontextmanager
async def lifespan(_: FastAPI):
    mode = get_source_mode()
    if mode == "cricapi":
        task = asyncio.create_task(
            run_cricapi_poller(
                state,
                broadcast_state,
                api_key=os.environ["CRICAPI_KEY"],
                match_id=os.getenv("CRICAPI_MATCH_ID"),
            )
        )
    elif mode == "playwright":
        task = asyncio.create_task(
            run_playwright_reader(
                state,
                broadcast_state,
                url=os.environ["SCRAPE_URL"],
                score_selector=os.getenv("SCRAPE_SCORE_SELECTOR", os.getenv("SCRAPE_SELECTOR", "[data-score]")),
                overs_selector=os.getenv("SCRAPE_OVERS_SELECTOR", "[data-overs]"),
                status_selector=os.getenv("SCRAPE_STATUS_SELECTOR", "[data-status]"),
                balls_selector=os.getenv("SCRAPE_BALLS_SELECTOR", "[data-balls]"),
                team_selector=os.getenv("SCRAPE_TEAM_SELECTOR", ""),
                crr_selector=os.getenv("SCRAPE_CRR_SELECTOR", ""),
            )
        )
    else:
        task = asyncio.create_task(run_simulator(state, broadcast_state))

    filler_interval = float(os.getenv("FILLER_INTERVAL_SEC", "22"))
    filler_task = asyncio.create_task(_filler_loop(interval=filler_interval))

    try:
        yield
    finally:
        task.cancel()
        filler_task.cancel()


app = FastAPI(title="Cricket Live Scoreboard", lifespan=lifespan)


@app.get("/api/state")
async def get_state() -> JSONResponse:
    return JSONResponse(state.model_dump())


@app.post("/api/state")
async def update_state(new_state: ScoreboardState) -> JSONResponse:
    global state
    state = new_state
    await broadcast_state(state)
    return JSONResponse(state.model_dump())


@app.get("/api/commentary/audio/{clip_id}")
async def get_commentary_audio(clip_id: int) -> Response:
    audio = commentary_clips.get(clip_id)
    if audio is None:
        raise HTTPException(status_code=404, detail="Clip not found")
    return Response(content=audio, media_type="audio/mpeg")


@app.post("/api/commentary/speak")
async def speak_commentary(body: dict[str, str]) -> JSONResponse:
    global clip_counter
    text = (body.get("text") or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Missing 'text'")
    audio_bytes = await synthesize_fish_audio(text)
    audio_url = None
    if audio_bytes:
        clip_counter += 1
        commentary_clips[clip_counter] = audio_bytes
        audio_url = f"/api/commentary/audio/{clip_counter}"
    await manager.broadcast_text(
        json.dumps({"type": "commentary", "text": text, "audio_url": audio_url})
    )
    return JSONResponse({"text": text, "audio_url": audio_url})


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await manager.connect(ws)
    try:
        await ws.send_text(state.model_dump_json())
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)


app.mount("/", StaticFiles(directory=str(UI_DIR), html=True), name="ui")
