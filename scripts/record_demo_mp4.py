"""Record the full scripted broadcast demo (1280x720 video + non-overlapping synced Hindi audio) to MP4."""

from __future__ import annotations

import asyncio
import json
import subprocess
import tempfile
import time
from pathlib import Path

import httpx
import websockets
from playwright.async_api import async_playwright

from cricket_live.commentary import _find_ffmpeg

ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_MP4 = ROOT_DIR / "cricket_live_demo.mp4"
SERVER_URL = "http://127.0.0.1:8000"


def get_audio_duration_ms(ffmpeg: str, path: Path) -> int:
    """Measure exact audio clip duration in milliseconds using ffmpeg stderr."""
    proc = subprocess.run(
        [ffmpeg, "-i", str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    for line in proc.stderr.splitlines():
        if "Duration:" in line:
            t_str = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = t_str.split(":")
            return int((int(h) * 3600 + int(m) * 60 + float(s)) * 1000)
    return 4000


async def main() -> None:
    ffmpeg = _find_ffmpeg()
    if not ffmpeg:
        raise RuntimeError("FFmpeg not found")

    # Seed IND vs AUS and pre-synthesize all 28 Hindi clips BEFORE recording so there is zero silence gap!
    print("[prepare] Pre-synthesizing all 28 Hindi commentary clips...")
    async with httpx.AsyncClient(timeout=240.0) as client:
        await client.post(f"{SERVER_URL}/api/demo/seed")
        prep = await client.post(f"{SERVER_URL}/api/demo/prepare")
        print("[prepare]", prep.json())

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        video_dir = tmp / "video"
        audio_dir = tmp / "audio"
        video_dir.mkdir()
        audio_dir.mkdir()

        audio_events: list[tuple[int, Path]] = []
        recording_active = False
        demo_done_event = asyncio.Event()
        start_time = time.monotonic()
        cursor_ms = 0

        async def listen_audio(stop_event: asyncio.Event) -> None:
            nonlocal cursor_ms
            idx = 0
            async with websockets.connect("ws://127.0.0.1:8000/ws") as ws:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    while not stop_event.is_set():
                        try:
                            raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        except asyncio.TimeoutError:
                            continue
                        if not recording_active:
                            continue
                        msg = json.loads(raw)
                        if msg.get("type") == "demo_done":
                            demo_done_event.set()
                            continue
                        if msg.get("type") == "commentary" and msg.get("audio_url"):
                            arrival_ms = max(0, int((time.monotonic() - start_time) * 1000))
                            resp = await client.get(f"{SERVER_URL}{msg['audio_url']}")
                            if resp.status_code == 200:
                                idx += 1
                                clip_path = audio_dir / f"clip_{idx:03d}.mp3"
                                clip_path.write_bytes(resp.content)
                                dur_ms = get_audio_duration_ms(ffmpeg, clip_path)
                                place_ms = max(arrival_ms, cursor_ms)
                                cursor_ms = place_ms + dur_ms + 420
                                audio_events.append((place_ms, clip_path))
                                print(f"  [audio] {clip_path.name} ({dur_ms}ms) @ {place_ms}ms")

        stop_event = asyncio.Event()
        listener_task = asyncio.create_task(listen_audio(stop_event))

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                record_video_dir=str(video_dir),
                record_video_size={"width": 1280, "height": 720},
            )
            page = await context.new_page()
            await page.goto(f"{SERVER_URL}/director.html?embed=1", wait_until="networkidle")
            await page.wait_for_timeout(1000)

            start_time = time.monotonic()
            recording_active = True
            async with httpx.AsyncClient() as client:
                await client.post(f"{SERVER_URL}/api/demo/start")

            # Wait until demo_script emits demo_done (up to 10 minutes)
            print("[record] Recording full synced 1280x720 broadcast demo...")
            await asyncio.wait_for(demo_done_event.wait(), timeout=600.0)
            await asyncio.sleep(1.5)

            video_path = await page.video.path()
            await context.close()
            await browser.close()

        stop_event.set()
        await listener_task

        print(f"[ffmpeg] Muxing video ({video_path}) + {len(audio_events)} non-overlapping clips...")
        cmd: list[str] = [ffmpeg, "-y", "-i", str(video_path)]
        for _, clip in audio_events:
            cmd.extend(["-i", str(clip)])

        if audio_events:
            filters = []
            mix_inputs = []
            for i, (place_ms, _) in enumerate(audio_events, start=1):
                filters.append(f"[{i}:a]adelay={place_ms}|{place_ms}[a{i}]")
                mix_inputs.append(f"[a{i}]")
            filter_complex = ";".join(filters) + f";{''.join(mix_inputs)}amix=inputs={len(audio_events)}:normalize=0[aout]"
            cmd.extend(
                [
                    "-filter_complex",
                    filter_complex,
                    "-map",
                    "0:v",
                    "-map",
                    "[aout]",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "20",
                    "-pix_fmt",
                    "yuv420p",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                    "-shortest",
                    str(OUTPUT_MP4),
                ]
            )
        else:
            cmd.extend(["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(OUTPUT_MP4)])

        subprocess.run(cmd, check=True)
        print(f"[done] Saved MP4 to: {OUTPUT_MP4} ({OUTPUT_MP4.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    asyncio.run(main())
