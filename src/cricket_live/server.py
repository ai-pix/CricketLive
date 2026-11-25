"""FastAPI + WebSocket server for the live cricket broadcast overlay."""

from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .models import ScoreboardState
from .sources import get_source_mode, run_cricapi_poller, run_playwright_reader, run_simulator

UI_DIR = Path(__file__).resolve().parents[2] / "ui"


class ConnectionManager:
    def __init__(self) -> None:
        self.active: set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self.active.discard(ws)

    async def broadcast(self, state: ScoreboardState) -> None:
        payload = state.model_dump_json()
        stale: list[WebSocket] = []
        for ws in list(self.active):
            try:
                await ws.send_text(payload)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self.disconnect(ws)


state = ScoreboardState()
manager = ConnectionManager()


async def broadcast_state(new_state: ScoreboardState) -> None:
    await manager.broadcast(new_state)


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

    try:
        yield
    finally:
        task.cancel()


app = FastAPI(title="Cricket Live Scoreboard", lifespan=lifespan)


@app.get("/api/state")
async def get_state() -> JSONResponse:
    return JSONResponse(state.model_dump())


@app.post("/api/state")
async def update_state(new_state: ScoreboardState) -> JSONResponse:
    global state
    state = new_state
    await manager.broadcast(state)
    return JSONResponse(state.model_dump())


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
