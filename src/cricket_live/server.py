"""FastAPI + WebSocket server for the live cricket broadcast overlay."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from .audio_pipeline import CommentaryPipeline
from .commentary import (
    CommentaryTurn,
    get_mp3_duration_sec,
    seed_default_stories,
    synthesize_fish_audio,
)
from .crex_sync import run_crex_live_watcher, sync_crex_match_once
from .db import (
    DB_PATH,
    get_all_player_images,
    get_news_items,
    init_db,
    list_player_images_rows,
    load_latest_match_state,
    log_ball_event,
    save_match_state,
)
from .demo_script import build_demo_seed_state, prepare_demo_audio, run_demo_showcase
from .models import ScoreboardState
from .sources import get_source_mode, run_cricapi_poller, run_playwright_reader, run_simulator

load_dotenv()

UI_DIR = Path(__file__).resolve().parents[2] / "ui"
UI_V2_DIR = Path(__file__).resolve().parents[2] / "ui_v2"
ROOT_DIR = Path(__file__).resolve().parents[2]
NEWS_DIR = ROOT_DIR / "news"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from news.fetcher import fetch_all_cricket_news, load_cached_news


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
source_task: asyncio.Task | None = None


async def _speak_and_broadcast(turns: list[CommentaryTurn]) -> float:
    global clip_counter, last_commentary_at
    last_commentary_at = time.monotonic()
    total_sec = 0.0
    for speaker, text in turns:
        audio_bytes = await synthesize_fish_audio(text, speaker=speaker)
        audio_url = None
        if audio_bytes:
            total_sec += await get_mp3_duration_sec(audio_bytes) + 0.45
            clip_counter += 1
            commentary_clips[clip_counter] = audio_bytes
            if len(commentary_clips) > 40:
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
    return total_sec


def _register_clip(audio_bytes: bytes) -> str:
    global clip_counter
    clip_counter += 1
    commentary_clips[clip_counter] = audio_bytes
    if len(commentary_clips) > 80:
        oldest = next(iter(commentary_clips))
        commentary_clips.pop(oldest, None)
    return f"/api/commentary/audio/{clip_counter}"


async def _broadcast_json(payload: dict) -> None:
    await manager.broadcast_text(json.dumps(payload))


commentary_engine = CommentaryPipeline(
    get_state=lambda: state,
    has_clients=lambda: bool(manager.active),
    is_demo_running=lambda: bool(demo_task and not demo_task.done()),
    broadcast_json=_broadcast_json,
    register_clip=_register_clip,
)


async def _emit_commentary(prev: ScoreboardState | None, curr: ScoreboardState) -> None:
    commentary_engine.notify_ball_event(prev, curr)


async def _filler_loop(interval: float = 22.0) -> None:
    await commentary_engine.run()


MILESTONE_LABELS = {
    50: "HALF CENTURY!",
    100: "CENTURY!",
    150: "150 RUNS!",
    200: "DOUBLE CENTURY!",
    250: "250 RUNS!",
    300: "TRIPLE CENTURY!",
}


async def _check_and_emit_milestones(prev: ScoreboardState | None, curr: ScoreboardState) -> None:
    if prev is None:
        return
    prev_map = {b.name: b.runs for b in (prev.striker, prev.non_striker)}
    for batter in (curr.striker, curr.non_striker):
        old_runs = prev_map.get(batter.name)
        if old_runs is None:
            continue
        for m, label in MILESTONE_LABELS.items():
            if old_runs < m <= batter.runs:
                await manager.broadcast_text(
                    json.dumps(
                        {
                            "type": "milestone",
                            "player": batter.name,
                            "runs": batter.runs,
                            "balls": batter.balls,
                            "fours": batter.fours,
                            "sixes": batter.sixes,
                            "strike_rate": batter.strike_rate,
                            "milestone": m,
                            "label": label,
                            "team": curr.batting_team,
                        }
                    )
                )
                hindi_name = batter.name.title()
                commentary_engine.queue_milestone_turn(
                    f"शानदार मील का पत्थर! {hindi_name} ने {m} रन पूरे कर लिए हैं — लाजवाब पारी, पूरा स्टेडियम तालियाँ बजा रहा है!"
                )
                break


def _has_toss_result(toss_text: str) -> bool:
    t = (toss_text or "").upper()
    return any(k in t for k in ("WON THE TOSS", "CHOSE", "ELECTED", "OPTED"))


async def _auto_switch_on_transition(prev: ScoreboardState | None, curr: ScoreboardState) -> None:
    """Keep broadcast locked on the main Scoreboard (/) without auto-switching to other pages."""
    return


_last_fx_sig: tuple[int, int, str, str] | None = None


async def _check_and_emit_event_fx(prev: ScoreboardState | None, curr: ScoreboardState) -> None:
    global _last_fx_sig
    if prev is None:
        return
    if prev.runs == curr.runs and prev.wickets == curr.wickets and prev.overs == curr.overs and prev.callout_tone == curr.callout_tone:
        return

    score_diff = curr.runs - prev.runs
    wicket_fell = curr.wickets > prev.wickets
    overs_changed = curr.overs != prev.overs
    last_ball = (curr.curr_over.balls[-1].upper() if curr.curr_over.balls else "")
    tone = (curr.callout_tone or "").lower()

    event = ""
    subtitle = ""
    if wicket_fell or (overs_changed and (last_ball == "W" or tone == "wicket")):
        event = "WICKET"
        subtitle = f"{curr.bowler.name} • {curr.runs}/{curr.wickets}"
    elif score_diff >= 6 or (overs_changed and (last_ball == "6" or tone == "six")):
        event = "SIX"
        subtitle = f"{curr.striker.name} • {curr.runs}/{curr.wickets}"
    elif score_diff == 4 or (overs_changed and (last_ball == "4" or tone == "four")):
        event = "FOUR"
        subtitle = f"{curr.striker.name} • {curr.runs}/{curr.wickets}"

    if not event:
        return
    sig = (curr.runs, curr.wickets, curr.overs, event)
    if sig == _last_fx_sig:
        return
    _last_fx_sig = sig
    await manager.broadcast_text(json.dumps({"type": "event_fx", "event": event, "subtitle": subtitle}))


async def _delayed_ui_sync(snapshot_prev: ScoreboardState | None, snapshot_curr: ScoreboardState) -> None:
    """Delay UI state & FX broadcast until the live ball's voice audio starts (max 3.5s safety cap)."""
    commentary_engine._ball_audio_synced.clear()
    try:
        await asyncio.wait_for(commentary_engine._ball_audio_synced.wait(), timeout=3.5)
    except asyncio.TimeoutError:
        pass
    await manager.broadcast(snapshot_curr)
    await _check_and_emit_event_fx(snapshot_prev, snapshot_curr)
    await _check_and_emit_milestones(snapshot_prev, snapshot_curr)


async def broadcast_state(new_state: ScoreboardState) -> None:
    global prev_state
    snapshot_prev = prev_state
    snapshot_curr = new_state.model_copy(deep=True)
    prev_state = snapshot_curr
    if snapshot_prev is None or (
        snapshot_prev.runs != snapshot_curr.runs
        or snapshot_prev.wickets != snapshot_curr.wickets
        or snapshot_prev.overs != snapshot_curr.overs
    ):
        log_ball_event(
            active_match_url or "local",
            snapshot_curr.overs,
            snapshot_curr.runs,
            snapshot_curr.wickets,
            snapshot_curr.callout,
            snapshot_curr.live_commentary,
        )
    asyncio.create_task(_auto_switch_on_transition(snapshot_prev, snapshot_curr))
    await _emit_commentary(snapshot_prev, snapshot_curr)

    is_ball_change = bool(
        snapshot_prev is not None
        and (
            snapshot_prev.runs != snapshot_curr.runs
            or snapshot_prev.wickets != snapshot_curr.wickets
            or snapshot_prev.overs != snapshot_curr.overs
        )
    )
    voice_sync_active = (not commentary_engine.paused) and bool(manager.active)
    if voice_sync_active and is_ball_change:
        asyncio.create_task(_delayed_ui_sync(snapshot_prev, snapshot_curr))
    else:
        await manager.broadcast(new_state)
        asyncio.create_task(_check_and_emit_event_fx(snapshot_prev, snapshot_curr))
        asyncio.create_task(_check_and_emit_milestones(snapshot_prev, snapshot_curr))

    if (
        snapshot_prev is not None
        and _has_toss_result(snapshot_curr.toss)
        and not _has_toss_result(snapshot_prev.toss)
    ):
        asyncio.create_task(
            broadcast_control({"type": "toss_trigger", "toss": snapshot_curr.toss})
        )


active_match_url: str = ""


async def _run_crex_live_loop(url: str, interval_sec: float = 20.0) -> None:
    while True:
        try:
            await run_crex_live_watcher(url, state, broadcast_state)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            print(f"[crex_live_loop] error: {exc}")
            await asyncio.sleep(5.0)


async def _news_refresh_loop(interval_sec: float = 600.0) -> None:
    while True:
        try:
            q = f"{state.batting_team} {state.bowling_team}".strip()
            terms = [state.batting_team, state.bowling_team, state.series_name, "semi final", "live", "win", "wickets"]
            payload = await fetch_all_cricket_news(match_query=q, focus_terms=terms, max_items=50)
            if payload.get("items"):
                state.latest_news = [
                    {
                        "title": it["title"],
                        "summary": it.get("summary", ""),
                        "source": it.get("source", "NEWS"),
                        "source_url": it.get("source_url", ""),
                    }
                    for it in payload["items"][:12]
                ]
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            print(f"[news_loop] error: {exc}")
        await asyncio.sleep(interval_sec)


@asynccontextmanager
async def lifespan(_: FastAPI):
    global source_task, active_match_url
    init_db()
    seed_default_stories()
    mode = get_source_mode()
    crex_url = os.getenv("CREX_LIVE_URL", "").strip()
    cached_state = load_latest_match_state(crex_url or None)
    if cached_state:
        try:
            loaded = ScoreboardState.model_validate(cached_state)
            for field_name in loaded.model_fields:
                setattr(state, field_name, getattr(loaded, field_name))
        except Exception:
            pass

    if crex_url:
        active_match_url = crex_url
        source_task = asyncio.create_task(_run_crex_live_loop(crex_url))
    elif mode == "cricapi":
        source_task = asyncio.create_task(
            run_cricapi_poller(
                state,
                broadcast_state,
                api_key=os.environ["CRICAPI_KEY"],
                match_id=os.getenv("CRICAPI_MATCH_ID"),
            )
        )
    elif mode == "playwright":
        source_task = asyncio.create_task(
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
        source_task = asyncio.create_task(run_simulator(state, broadcast_state))

    filler_interval = float(os.getenv("FILLER_INTERVAL_SEC", "22"))
    filler_task = asyncio.create_task(_filler_loop(interval=filler_interval))
    news_task = asyncio.create_task(_news_refresh_loop(interval_sec=600.0))

    try:
        yield
    finally:
        if source_task:
            source_task.cancel()
        filler_task.cancel()
        news_task.cancel()


app = FastAPI(title="Cricket Live Scoreboard", lifespan=lifespan)


@app.middleware("http")
async def _no_cache_ui_middleware(request, call_next):
    resp = await call_next(request)
    path = request.url.path.lower()
    if path in ("/", "/v1", "/v1/", "/v2", "/v2/") or path.endswith((".html", ".js", ".css")):
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return resp


@app.get("/api/state")
async def get_state() -> JSONResponse:
    return JSONResponse(state.model_dump())


@app.get("/api/stories")
async def get_stories_and_news() -> JSONResponse:
    from .db import get_all_stories, get_news_items

    return JSONResponse({"stories": get_all_stories(), "news": get_news_items()})


demo_task: asyncio.Task | None = None


async def broadcast_control(payload: dict) -> None:
    await manager.broadcast_text(json.dumps(payload))


async def broadcast_state_only(new_state: ScoreboardState) -> None:
    global prev_state
    prev_state = new_state.model_copy(deep=True)
    await manager.broadcast(new_state)


@app.post("/api/demo/prepare")
async def prepare_demo() -> JSONResponse:
    cached = await prepare_demo_audio()
    return JSONResponse({"status": "ready", "clips": cached})


@app.post("/api/demo/seed")
async def seed_demo_state() -> JSONResponse:
    if source_task and not source_task.done():
        source_task.cancel()
    seed = build_demo_seed_state()
    for field_name in seed.model_fields:
        setattr(state, field_name, getattr(seed, field_name))
    await broadcast_state_only(state)
    return JSONResponse({"status": "seeded"})


@app.post("/api/broadcast/start")
async def start_live_broadcast() -> JSONResponse:
    """Start the actual live/prematch broadcast using the currently configured match state."""
    global demo_task
    if demo_task and not demo_task.done():
        demo_task.cancel()
        demo_task = None
    status = (state.match_status or "live").lower()
    start_slide = "/"
    await broadcast_state_only(state)
    await broadcast_control({"type": "slide", "url": start_slide})
    return JSONResponse({"status": "live_started", "slide": start_slide, "match_status": status})


@app.post("/api/demo/start")
async def start_demo_showcase() -> JSONResponse:
    global demo_task
    if source_task and not source_task.done():
        source_task.cancel()
    if demo_task and not demo_task.done():
        demo_task.cancel()
    demo_task = asyncio.create_task(
        run_demo_showcase(
            state,
            broadcast_state_only,
            broadcast_control,
            _speak_and_broadcast,
        )
    )
    return JSONResponse({"status": "started"})


@app.post("/api/source/crex")
async def connect_crex_live(body: dict[str, str]) -> JSONResponse:
    global source_task, active_match_url
    url = (body.get("url") or "").strip()
    if not url or "crex.com" not in url:
        raise HTTPException(status_code=400, detail="Valid crex.com URL required")
    if source_task and not source_task.done():
        source_task.cancel()
    if demo_task and not demo_task.done():
        demo_task.cancel()
    if url != active_match_url:
        fresh = ScoreboardState()
        for field_name in fresh.model_fields:
            setattr(state, field_name, getattr(fresh, field_name))
    active_match_url = url
    summary = await sync_crex_match_once(url, state)
    await broadcast_state_only(state)
    source_task = asyncio.create_task(_run_crex_live_loop(url))
    return JSONResponse({"status": "live", "summary": summary, "state_title": state.match_title, "score": f"{state.batting_team} {state.runs}/{state.wickets} ({state.overs})"})


@app.get("/api/news")
async def api_news() -> JSONResponse:
    cached = load_cached_news()
    return JSONResponse(
        {
            "items": cached.get("items", []),
            "sources": cached.get("sources", {}),
            "fetched_at": cached.get("fetched_at", ""),
            "news": get_news_items(limit=30),
        }
    )


@app.post("/api/news/refresh")
async def api_news_refresh() -> JSONResponse:
    q = f"{state.batting_team} {state.bowling_team}".strip()
    terms = [state.batting_team, state.bowling_team, state.series_name, "semi final", "live", "win", "wickets"]
    payload = await fetch_all_cricket_news(match_query=q, focus_terms=terms, max_items=50)
    if payload.get("items"):
        state.latest_news = [
            {
                "title": it["title"],
                "summary": it.get("summary", ""),
                "source": it.get("source", "NEWS"),
                "source_url": it.get("source_url", ""),
            }
            for it in payload["items"][:12]
        ]
        await broadcast_state_only(state)
    return JSONResponse(payload)


@app.get("/api/player-images")
async def api_player_images() -> JSONResponse:
    return JSONResponse({"images": get_all_player_images(), "players": list_player_images_rows()})


@app.get("/api/db/summary")
async def api_db_summary() -> JSONResponse:
    import sqlite3

    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        counts = {
            t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t in ("matches", "ball_events", "news_items", "commentary_stories")
        }
    return JSONResponse({"db_path": str(DB_PATH), "counts": counts})


@app.post("/api/state")
async def update_state(new_state: ScoreboardState) -> JSONResponse:
    global state
    state = new_state
    await broadcast_state(state)
    return JSONResponse(state.model_dump())


@app.post("/api/toss")
async def update_toss(body: dict[str, object]) -> JSONResponse:
    """Update the live toss result, persist to DB, broadcast to all overlays, and optionally show /toss.html."""
    toss_text = str(body.get("toss") or "").strip()
    winner = str(body.get("winner") or "").strip().upper()
    decision = str(body.get("decision") or "").strip().upper()
    if not toss_text:
        if not winner or decision not in ("BAT", "BOWL"):
            raise HTTPException(status_code=400, detail="Provide 'toss' text or 'winner' + 'decision' ('BAT'|'BOWL')")
        toss_text = f"{winner} WON THE TOSS AND ELECTED TO {decision} FIRST"
    state.toss = toss_text.upper()
    state.callout = state.toss[:34]
    save_match_state(active_match_url or "ind-a-vs-sl-a-semi-final", state.model_dump())
    await broadcast_state_only(state)
    await broadcast_control(
        {
            "type": "toss_trigger",
            "winner": winner,
            "decision": decision,
            "toss": state.toss,
        }
    )
    if body.get("show_slide", True):
        await broadcast_control({"type": "slide", "url": "/toss.html", "priority": True})
    return JSONResponse({"status": "updated", "toss": state.toss})


@app.post("/api/control")
async def remote_control(body: dict[str, object]) -> JSONResponse:
    """Broadcast remote slide switch or FX trigger from OBS Dock / control.html to director.html."""
    action = str(body.get("action") or "").strip().lower()
    if action == "slide":
        url = str(body.get("url") or "/").strip()
        await broadcast_control({"type": "slide", "url": url, "priority": True})
        return JSONResponse({"status": "ok", "action": "slide", "url": url})
    if action == "fx":
        event = str(body.get("event") or "FOUR").strip().upper()
        detail = str(body.get("detail") or "").strip()
        await broadcast_control({"type": "fx", "event": event, "detail": detail})
        return JSONResponse({"status": "ok", "action": "fx", "event": event})
    if action == "crowd_toggle":
        await broadcast_control({"type": "crowd_toggle"})
        return JSONResponse({"status": "ok", "action": "crowd_toggle"})
    if action == "toss":
        await broadcast_control(
            {
                "type": "toss_trigger",
                "winner": str(body.get("winner") or "").strip().upper(),
                "decision": str(body.get("decision") or "").strip().upper(),
                "toss": str(body.get("toss") or state.toss or "").strip().upper(),
            }
        )
        return JSONResponse({"status": "ok", "action": "toss"})
    if action == "toss_close":
        await broadcast_control({"type": "toss_close"})
        return JSONResponse({"status": "ok", "action": "toss_close"})
    if action in ("prematch", "pitch", "weather", "scorecard", "modal_close"):
        await broadcast_control({"type": f"v2_{action}", "enabled": body.get("enabled")})
        return JSONResponse({"status": "ok", "action": action})
    raise HTTPException(status_code=400, detail="Unsupported action")


@app.get("/api/commentary/audio/{clip_id}")
async def get_commentary_audio(clip_id: int) -> Response:
    audio = commentary_clips.get(clip_id)
    if audio is None:
        raise HTTPException(status_code=404, detail="Clip not found")
    return Response(content=audio, media_type="audio/mpeg")


@app.post("/api/commentary/stop")
async def stop_commentary() -> JSONResponse:
    commentary_engine.pause()
    await manager.broadcast_text(json.dumps({"type": "commentary_interrupt"}))
    return JSONResponse({"status": "stopped"})


@app.post("/api/commentary/start")
async def start_commentary() -> JSONResponse:
    commentary_engine.resume()
    return JSONResponse({"status": "started"})


@app.get("/api/commentary/status")
async def commentary_status() -> JSONResponse:
    return JSONResponse(commentary_engine.get_status())


@app.post("/api/commentary/prewarm")
async def prewarm_commentary(max_items: int = 8) -> JSONResponse:
    warmed = await commentary_engine.prewarm_assets(max_items=max_items)
    return JSONResponse({"status": "warmed", "clips": warmed})


@app.get("/api/commentary/voice")
async def get_active_voice() -> JSONResponse:
    return JSONResponse(
        {
            "host_reference_id": os.getenv("FISH_REFERENCE_ID", ""),
            "expert_reference_id": os.getenv("FISH_EXPERT_REFERENCE_ID", ""),
        }
    )


@app.post("/api/commentary/voice")
async def set_host_voice(body: dict[str, str]) -> JSONResponse:
    ref_id = (body.get("reference_id") or "").strip()
    if not ref_id:
        raise HTTPException(status_code=400, detail="Missing 'reference_id'")
    os.environ["FISH_REFERENCE_ID"] = ref_id
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()
        out = [
            f"FISH_REFERENCE_ID={ref_id}" if l.startswith("FISH_REFERENCE_ID=") else l
            for l in lines
        ]
        if not any(l.startswith("FISH_REFERENCE_ID=") for l in out):
            out.append(f"FISH_REFERENCE_ID={ref_id}")
        env_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return JSONResponse({"status": "updated", "host_reference_id": ref_id})


@app.post("/api/commentary/speak")
async def speak_commentary(body: dict[str, str]) -> JSONResponse:
    global clip_counter
    text = (body.get("text") or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Missing 'text'")
    audio_bytes = await synthesize_fish_audio(text, speaker="expert")
    audio_url = None
    if audio_bytes:
        clip_counter += 1
        commentary_clips[clip_counter] = audio_bytes
        audio_url = f"/api/commentary/audio/{clip_counter}"
    await manager.broadcast_text(
        json.dumps({"type": "commentary", "speaker": "expert", "text": text, "audio_url": audio_url})
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


class LayeredStaticFiles(StaticFiles):
    """Serve static files from ordered directories so UI v2 overrides UI v1 while sharing assets/slides."""

    def __init__(self, directories: list[Path], **kwargs: object) -> None:
        layer_dirs = [d for d in directories if d.exists()]
        primary = layer_dirs[0] if layer_dirs else directories[0]
        super().__init__(directory=str(primary), **kwargs)
        self.all_directories = [str(d) for d in layer_dirs]


def _ui_v2_entry_path() -> Path:
    for candidate in (UI_V2_DIR / "broadcast.html", UI_V2_DIR / "index.html", UI_DIR / "index.html"):
        if candidate.exists():
            return candidate
    raise HTTPException(status_code=404, detail="UI entry page not found")


def _redirect_with_query(request: Request, target_path: str) -> RedirectResponse:
    target = target_path + (f"?{request.url.query}" if request.url.query else "")
    return RedirectResponse(url=target, status_code=307)


@app.get("/")
async def ui_root() -> FileResponse:
    return FileResponse(_ui_v2_entry_path())


@app.get("/v2")
async def ui_v2_redirect(request: Request) -> RedirectResponse:
    return _redirect_with_query(request, "/v2/")


@app.get("/v2/")
async def ui_v2_root() -> FileResponse:
    return FileResponse(_ui_v2_entry_path())


@app.get("/v1")
async def ui_v1_redirect(request: Request) -> RedirectResponse:
    return _redirect_with_query(request, "/v1/")


if NEWS_DIR.exists():
    app.mount("/news-portal", StaticFiles(directory=str(NEWS_DIR), html=True), name="news-portal")
if UI_V2_DIR.exists():
    app.mount("/v2", LayeredStaticFiles([UI_V2_DIR, UI_DIR], html=True), name="ui-v2")
app.mount("/v1", StaticFiles(directory=str(UI_DIR), html=True), name="ui-v1")
app.mount("/", LayeredStaticFiles([UI_V2_DIR, UI_DIR], html=True), name="ui")
