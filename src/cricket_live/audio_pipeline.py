"""Streaming Producer-Consumer Commentary Audio Pipeline with lookahead synthesis."""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Awaitable, Callable

from .commentary import get_mp3_duration_sec, synthesize_fish_audio
from .commentary_director import (
    RULES_AND_CRAFT_LIBRARY,
    DirectedTurn,
    NoRepeatDeck,
    build_live_ball_turns,
    build_live_ball_turns_async,
    build_next_segment,
    build_next_segment_async,
)
from .db import get_all_stories
from .llm_director import is_llm_configured
from .models import ScoreboardState

LOG_PATH = Path(__file__).resolve().parents[2] / "logs" / "commentary.log"


def _log_line(tag: str, msg: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] [{tag}] {msg}\n"
    try:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass
    print(line, end="")


class CommentaryPipeline:
    """Continuous, non-repetitive broadcast pipeline with lookahead pre-synthesis and instant live preemption."""

    def __init__(
        self,
        get_state: Callable[[], ScoreboardState],
        has_clients: Callable[[], bool],
        is_demo_running: Callable[[], bool],
        broadcast_json: Callable[[dict], Awaitable[None]],
        register_clip: Callable[[bytes], str],
    ) -> None:
        self._get_state = get_state
        self._has_clients = has_clients
        self._is_demo_running = is_demo_running
        self._broadcast_json = broadcast_json
        self._register_clip = register_clip

        self.deck = NoRepeatDeck()
        self.paused = False

        self._priority_events: list[tuple[ScoreboardState | None, ScoreboardState]] = []
        self._priority_turns: list[DirectedTurn] = []
        self._major_interrupt_pending = False
        self._ball_audio_synced = asyncio.Event()
        self._active_turns: list[DirectedTurn] = []
        self._interrupt_event = asyncio.Event()
        self._last_spoken_ball_id = ""
        self._last_crex_raw = ""
        self._seen_crex_raws: set[str] = set()

        self._recent_transcript: list[dict] = []
        self._total_spoken = 0
        self._ai_segments = 0
        self._fallback_segments = 0
        self._current_tag = "idle"
        self._current_speaker = "none"
        self._current_slide = "/"

    def queue_milestone_turn(self, text: str) -> None:
        """Queue a milestone call through the single Expert pipeline without overlapping."""
        if self.paused or not text:
            return
        self._priority_turns.append(("expert", text, "live_milestone"))
        self._major_interrupt_pending = True
        self._interrupt_event.set()

    def pause(self) -> None:
        self.paused = True
        self._priority_events.clear()
        self._priority_turns.clear()
        self._major_interrupt_pending = False
        self._active_turns.clear()
        self._interrupt_event.set()
        self._current_tag = "paused"
        _log_line("ENGINE", "Commentary paused")

    def resume(self) -> None:
        self.paused = False
        self._interrupt_event.clear()
        self._current_tag = "active"
        _log_line("ENGINE", "Commentary resumed")

    def get_status(self) -> dict:
        return {
            "paused": self.paused,
            "llm_enabled": is_llm_configured(),
            "match_status": self._get_state().match_status,
            "current_slide": self._current_slide,
            "ai_segments": self._ai_segments,
            "fallback_segments": self._fallback_segments,
            "current_tag": self._current_tag,
            "current_speaker": self._current_speaker,
            "queued_turns": len(self._active_turns),
            "pending_events": len(self._priority_events),
            "total_spoken": self._total_spoken,
            "recent_lines": self._recent_transcript[-12:],
        }

    def notify_ball_event(self, prev: ScoreboardState | None, curr: ScoreboardState) -> None:
        """Immediately preempt ongoing studio chatter when live match action updates."""
        if prev is None or self.paused:
            return
        if prev.match_status == "completed" and curr.match_status == "completed":
            if curr.live_commentary:
                self._last_crex_raw = curr.live_commentary
                self._seen_crex_raws.add(curr.live_commentary)
            return
        new_crex = bool(
            curr.live_commentary
            and curr.live_commentary != self._last_crex_raw
            and curr.live_commentary not in self._seen_crex_raws
        )
        changed = (
            prev.runs != curr.runs
            or prev.wickets != curr.wickets
            or prev.overs != curr.overs
            or new_crex
        )
        if not changed:
            return
        # Ignore stale backward snapshots from CREX (e.g. 21/1 (3.2) -> 20/1 (3.1)) within the same innings
        if prev.batting_team == curr.batting_team:
            def _ov_tuple(ov: str) -> tuple[int, int]:
                parts = str(ov or "0.0").split(".")
                try:
                    return (int(parts[0] or 0), int(parts[1] or 0) if len(parts) > 1 else 0)
                except Exception:
                    return (0, 0)
            if _ov_tuple(curr.overs) < _ov_tuple(prev.overs) or curr.runs < prev.runs or curr.wickets < prev.wickets:
                return
        if curr.live_commentary:
            self._last_crex_raw = curr.live_commentary
            self._seen_crex_raws.add(curr.live_commentary)
            if len(self._seen_crex_raws) > 60:
                self._seen_crex_raws.clear()
        _log_line(
            "BALL_EVENT",
            f"{prev.runs}/{prev.wickets} ({prev.overs}) -> {curr.runs}/{curr.wickets} ({curr.overs}) crex={new_crex}",
        )
        # Keep only the latest pending ball event so rapid dot balls don't pile up
        if self._priority_events:
            first_prev, _ = self._priority_events[0]
            self._priority_events = [(first_prev, curr)]
        else:
            self._priority_events.append((prev, curr))

        last_ball = (curr.curr_over.balls[-1].upper() if curr.curr_over.balls else "")
        is_major_event = (
            curr.wickets > prev.wickets
            or (curr.runs - prev.runs) >= 4
            or last_ball in ("4", "6", "W")
        )
        if is_major_event:
            self._major_interrupt_pending = True
            self._interrupt_event.set()

    async def _synthesize_turn(self, turn: DirectedTurn) -> tuple[str | None, float]:
        speaker, text, tag = turn
        speaker = "expert"
        if tag in ("live_wicket", "live_wicket_analysis", "live_six", "live_six_analysis", "live_four", "live_four_analysis"):
            mood = "excited"
        elif tag in ("live_dot", "live_run", "live_crex_ball"):
            mood = "calm"
        else:
            mood = "conversational"
        audio_bytes = await synthesize_fish_audio(text, speaker=speaker, mood=mood)
        if audio_bytes:
            url = self._register_clip(audio_bytes)
            dur = await get_mp3_duration_sec(audio_bytes)
            return (url, dur)
        return (None, max(3.2, len(text) * 0.055))

    async def _deliver_turn(
        self,
        turn: DirectedTurn,
        prepared: tuple[str | None, float] | None = None,
        lookahead_turn: DirectedTurn | None = None,
        *,
        interruptible: bool = True,
        slide_url: str | None = None,
        sync_state: ScoreboardState | None = None,
    ) -> tuple[bool, asyncio.Task | None]:
        """Broadcast slide (synced to speech start) + turn audio, and prefetch next turn concurrently."""
        _, text, tag = turn
        speaker = "expert"
        audio_url, dur = prepared if prepared is not None else await self._synthesize_turn((speaker, text, tag))
        if self.paused:
            return (False, None)

        if slide_url:
            await self._switch_slide_if_needed(slide_url)

        self._current_tag = tag
        self._current_speaker = speaker
        self._total_spoken += 1
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "speaker": speaker,
            "tag": tag,
            "text": text,
            "audio_url": audio_url,
            "duration_sec": round(dur, 2),
        }
        self._recent_transcript.append(entry)
        if len(self._recent_transcript) > 40:
            self._recent_transcript.pop(0)
        _log_line(f"SPEAK:{speaker.upper()}:{tag}", text)

        payload: dict[str, object] = {
            "type": "commentary",
            "speaker": speaker,
            "text": text,
            "tag": tag,
            "audio_url": audio_url,
            "slide_url": slide_url or "",
        }
        if sync_state is not None:
            payload["state"] = sync_state.model_dump()
        await self._broadcast_json(payload)
        if sync_state is not None:
            self._ball_audio_synced.set()

        next_task: asyncio.Task | None = None
        if lookahead_turn is not None:
            next_task = asyncio.create_task(self._synthesize_turn(lookahead_turn))

        wait_sec = max(0.25, dur - 0.25)
        if not interruptible:
            await asyncio.sleep(wait_sec)
            return (True, next_task)

        try:
            await asyncio.wait_for(self._interrupt_event.wait(), timeout=wait_sec)
            return (False, None)
        except asyncio.TimeoutError:
            return (True, next_task)

    async def prewarm_assets(self, max_items: int = 8) -> int:
        """Pre-synthesize static rules and DB stories into disk TTS cache."""
        warmed = 0
        for _, turns in RULES_AND_CRAFT_LIBRARY[:3]:
            if warmed >= max_items * 2:
                break
            for _, txt in turns:
                await synthesize_fish_audio(txt, speaker="expert")
                warmed += 1
        _log_line("PREWARM", f"Pre-generated {warmed} cached commentary clips")
        return warmed

    async def _switch_slide_if_needed(self, url: str) -> None:
        # Locked to Scoreboard only — no automatic transitions to other slides
        target = "/"
        if target != self._current_slide:
            self._current_slide = target
            _log_line("SLIDE_LIMELIGHT", target)
            await self._broadcast_json({"type": "slide", "url": target})

    async def run(self) -> None:
        """Continuous lookahead producer-consumer broadcast loop with Nemotron AI + Auto Slide Limelight."""
        prepared_next: tuple[str | None, float] | None = None
        ai_seg_task: asyncio.Task | None = None
        next_slide_for_queue: str | None = None

        def _spawn_ai_prefetch() -> asyncio.Task:
            recent_texts = [r["text"] for r in self._recent_transcript[-8:]]
            return asyncio.create_task(
                build_next_segment_async(self._get_state(), self.deck, recent_texts)
            )

        while True:
            try:
                if self.paused or not self._has_clients() or self._is_demo_running():
                    prepared_next = None
                    if ai_seg_task and not ai_seg_task.done():
                        ai_seg_task.cancel()
                        ai_seg_task = None
                    await asyncio.sleep(1.0)
                    continue

                # 1. Priority milestone or live ball events
                if self._priority_turns or self._priority_events:
                    self._interrupt_event.clear()
                    is_hard_interrupt = self._major_interrupt_pending
                    self._major_interrupt_pending = False
                    prepared_next = None
                    self._active_turns.clear()
                    next_slide_for_queue = None
                    if ai_seg_task and not ai_seg_task.done():
                        ai_seg_task.cancel()
                    ai_seg_task = None

                    if is_hard_interrupt:
                        await self._broadcast_json({"type": "commentary_interrupt"})

                    if self._priority_turns:
                        turns = [self._priority_turns.pop(0)]
                        curr_sync = None
                    else:
                        prev, curr = self._priority_events.pop(0)
                        while self._priority_events:
                            _, curr = self._priority_events.pop(0)

                        turns, new_ball_id = await build_live_ball_turns_async(
                            prev,
                            curr,
                            self.deck,
                            self._last_spoken_ball_id,
                            [r["text"] for r in self._recent_transcript[-6:]],
                        )
                        if self._priority_events:
                            while self._priority_events:
                                _, curr = self._priority_events.pop(0)
                            turns, new_ball_id = await build_live_ball_turns_async(
                                prev,
                                curr,
                                self.deck,
                                self._last_spoken_ball_id,
                                [r["text"] for r in self._recent_transcript[-6:]],
                            )
                        if new_ball_id:
                            self._last_spoken_ball_id = new_ball_id
                        curr_sync = curr

                    if self.paused:
                        continue

                    if turns:
                        # Stay locked on Scoreboard (/) during live play and over breaks
                        await self._switch_slide_if_needed("/")
                        for idx, t in enumerate(turns):
                            look = turns[idx + 1] if idx + 1 < len(turns) else None
                            is_major_call = t[2] in ("live_wicket", "live_six", "live_four")
                            completed, nt = await self._deliver_turn(
                                t,
                                prepared=prepared_next,
                                lookahead_turn=look,
                                interruptible=not is_major_call,
                                sync_state=curr_sync if idx == 0 else None,
                            )
                            if not completed:
                                prepared_next = None
                                break
                            prepared_next = await nt if nt is not None else None
                    prepared_next = None
                    continue

                # 2. Load next segment (using Nemotron directly during prematch/break/completed, or prefetched live)
                if not self._active_turns:
                    self._interrupt_event.clear()
                    st = self._get_state()
                    is_non_live = st.match_status in ("prematch", "innings_break", "completed")

                    if ai_seg_task is not None:
                        try:
                            seg, _ = await ai_seg_task
                        except Exception:
                            seg = build_next_segment(st, self.deck)
                        spotlight_url = "/"
                        ai_seg_task = None
                    elif is_non_live and is_llm_configured():
                        # Latency doesn't matter during prematch / break / match complete: let Nemotron write every word
                        recent_texts = [r["text"] for r in self._recent_transcript[-8:]]
                        seg, _ = await build_next_segment_async(st, self.deck, recent_texts)
                        spotlight_url = "/"
                    else:
                        # Instant 0ms bootstrap segment on first live play turn while Nemotron warms up for segment 2
                        seg = build_next_segment(st, self.deck)
                        spotlight_url = "/"

                    if seg and seg[0][2].startswith("ai:"):
                        self._ai_segments += 1
                    else:
                        self._fallback_segments += 1
                    self._active_turns = list(seg)
                    next_slide_for_queue = spotlight_url

                # Kick off Nemotron AI prefetch in background while current segment plays!
                if ai_seg_task is None and len(self._active_turns) <= 3:
                    ai_seg_task = _spawn_ai_prefetch()

                # 3. Speak current turn while pre-synthesizing next turn concurrently
                if self._active_turns:
                    current_turn = self._active_turns.pop(0)
                    slide_to_show = next_slide_for_queue
                    next_slide_for_queue = None

                    if not self._active_turns and ai_seg_task is not None and ai_seg_task.done():
                        try:
                            seg, next_url = ai_seg_task.result()
                            ai_seg_task = None
                            if seg and seg[0][2].startswith("ai:"):
                                self._ai_segments += 1
                            else:
                                self._fallback_segments += 1
                            self._active_turns.extend(seg)
                            next_slide_for_queue = next_url
                        except Exception:
                            ai_seg_task = None

                    lookahead = self._active_turns[0] if self._active_turns else None
                    completed, next_task = await self._deliver_turn(
                        current_turn,
                        prepared=prepared_next,
                        lookahead_turn=lookahead,
                        interruptible=True,
                        slide_url=slide_to_show,
                    )
                    if not completed:
                        prepared_next = None
                        continue
                    prepared_next = await next_task if next_task is not None else None

            except asyncio.CancelledError:
                raise
            except Exception as exc:
                _log_line("ENGINE_ERR", str(exc))
                prepared_next = None
                await asyncio.sleep(1.5)
