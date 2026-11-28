"""Create a focused <2 minute single-story cricket news video with zoom/pan & slide edits.

Story: IND-A vs SL-A, 1st Semi-Final, Asia Cup Rising Stars 2026 (West End Park, Doha).
Outputs:
  - D:/Python Projects/Cricket Live/news/videos/cricket_news_02.mp4
"""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
NEWS_DIR = Path(__file__).resolve().parent
BUILD_DIR = NEWS_DIR / "build_02"
NORM_DIR = BUILD_DIR / "norm_frames"
CLIP_DIR = BUILD_DIR / "clips"
AUDIO_DIR = BUILD_DIR / "audio"
VIDEO_OUT = NEWS_DIR / "videos" / "cricket_news_02.mp4"

for d in (BUILD_DIR, NORM_DIR, CLIP_DIR, AUDIO_DIR, VIDEO_OUT.parent):
    d.mkdir(parents=True, exist_ok=True)

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from cricket_live.commentary import get_mp3_duration_sec, synthesize_fish_audio  # noqa: E402

load_dotenv(ROOT_DIR / ".env", override=True)

FPS = 30
TRANSITION_SEC = 0.45
PAUSE_BETWEEN_BEATS_SEC = 0.28


def _run(cmd: list[str], desc: str = "command") -> subprocess.CompletedProcess[str]:
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        raise RuntimeError(f"{desc} failed (exit {res.returncode}):\n{res.stderr[-1500:]}")
    return res


def _probe_image(path: Path) -> tuple[int, int, str]:
    res = _run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,codec_name",
            "-of",
            "json",
            str(path),
        ],
        f"ffprobe {path.name}",
    )
    info = json.loads(res.stdout or "{}").get("streams", [{}])[0]
    return int(info.get("width", 0)), int(info.get("height", 0)), str(info.get("codec_name", ""))


def _probe_duration(path: Path) -> float:
    res = _run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        f"ffprobe duration {path.name}",
    )
    return float((res.stdout or "0").strip() or 0.0)


def _normalize_to_1280x720(src: Path, dest: Path) -> None:
    """Convert any JPG/PNG/WEBP image into crisp 1280x720 JPEG without clipping faces."""
    w, h, codec = _probe_image(src)
    aspect = (w / h) if (w and h) else 1.777
    print(f"  norm {src.name} ({w}x{h} {codec}, ar={aspect:.2f}) -> {dest.name}")
    if aspect < 1.25:
        # Portrait/square framing: blurred mirror backdrop + crisp centered foreground
        vf = (
            "[0:v]split=2[bg][fg];"
            "[bg]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,boxblur=22:3[bg2];"
            "[fg]scale=-2:700:force_original_aspect_ratio=decrease[fg2];"
            "[bg2][fg2]overlay=(W-w)/2:(H-h)/2,format=yuvj420p"
        )
        _run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-filter_complex", vf, "-q:v", "2", str(dest)], f"norm {src.name}")
    else:
        # Landscape: fill 1280x720 with gentle top-bias crop so player heads never clip
        vf = (
            "scale=1280:720:force_original_aspect_ratio=increase,"
            "crop=1280:720:(iw-1280)/2:min(ih-720\\,(ih-720)*0.18),format=yuvj420p"
        )
        _run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf", vf, "-q:v", "2", str(dest)], f"norm {src.name}")


async def _fetch_live_state() -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get("http://127.0.0.1:8000/api/state")
            if resp.status_code == 200:
                return resp.json()
    except Exception as exc:
        print(f"Live state fallback ({exc})")
    return {}


def _build_story_beats(state: dict[str, Any]) -> list[dict[str, Any]]:
    """5 focused pure-Devanagari Hindi beats strictly for IND-A vs SL-A Semi-Final 1 (< 95s)."""
    # Reflect live match score dynamically if it changed post-1st innings
    batting_team = str(state.get("batting_team") or "IND-A")
    runs = int(state.get("runs") or 317)
    wickets = int(state.get("wickets") or 8)
    overs = str(state.get("overs") or "50.0")
    match_status = str(state.get("match_status") or "innings_break")
    print(f"Live context: {batting_team} {runs}/{wickets} ({overs}) status={match_status}")

    # Default verified innings-break script (~195 Devanagari words -> ~75-85s)
    beats = [
        {
            "id": "intro_vaibhav",
            "text": (
                "नमस्कार, मैं आपको एशिया कप राइजिंग स्टार्स दो हज़ार छब्बीस के पहले सेमीफ़ाइनल की बड़ी खबर बता रहा हूँ। "
                "दोहा में इंडिया ए ने श्रीलंका ए के खिलाफ पचास ओवर में तीन सौ सत्रह रन का विशाल स्कोर खड़ा किया। "
                "ओपनर वैभव सूर्यवंशी ने सत्ताईस गेंदों में चार चौकों और तीन छक्कों से चालीस रन की तेज़ शुरुआत दिलाई।"
            ),
            "shots": [
                {"img": "news/build_02/extra_candidates/extra_03_art.jpg", "motion": "zoom_out_center", "xfade": "slideleft"},
                {"img": "news/build_02/candidates/cand_08.png", "motion": "zoom_in_top", "xfade": "smoothleft"},
                {"img": "news/build_02/candidates/cand_06.jpg", "motion": "zoom_in_center", "xfade": "slideright"},
                {"img": "news/build_02/candidates/cand_01.jpg", "motion": "pan_left_to_right", "xfade": "wipeleft"},
            ],
        },
        {
            "id": "abhishek_tilak",
            "text": (
                "वैभव के बाद अभिषेक शर्मा ने मोर्चे को संभाला और तरेसठ गेंदों में ग्यारह चौकों व एक छक्के की मदद से शानदार अठहत्तर रन जड़े। "
                "कप्तान तिलक वर्मा ने भी छियासठ गेंदों में तिरपन रन की सधी हुई अर्धशतकीय पारी खेलकर स्कोर बोर्ड को तेज़ी से आगे बढ़ाया।"
            ),
            "shots": [
                {"img": "news/build_02/candidates/cand_04.jpg", "motion": "zoom_in_center", "xfade": "slideleft"},
                {"img": "news/build_02/candidates/cand_05.jpg", "motion": "zoom_out_center", "xfade": "smoothright"},
                {"img": "news/build_02/extra_candidates/extra_04_art.jpg", "motion": "zoom_in_top", "xfade": "slideleft"},
            ],
        },
        {
            "id": "rinku_drama",
            "text": (
                "लेकिन सैंतीसवें ओवर में मैदान पर बड़ा ड्रामा देखने को मिला, जब बारह रन पर खेल रहे रिंकू सिंह को अंपायर ने एलबीडब्ल्यू आउट दे दिया। "
                "फैसले से रिंकू बेहद नाराज़ दिखे, और देखते ही देखते इंडिया ए दो सौ पैंतीस रन पर छह विकेट गंवाकर दबाव में आ गया।"
            ),
            "shots": [
                {"img": "news/build_01/raw_imgs/news_00.jpg", "motion": "zoom_in_fast", "xfade": "slideup"},
                {"img": "news/build_02/candidates/cand_00.jpg", "motion": "pan_right_to_left", "xfade": "smoothleft"},
            ],
        },
        {
            "id": "shahbaz_rescue",
            "text": (
                "मुश्किल हालात में शाहबाज़ अहमद टीम के संकटमोचक बने और अड़तालीस गेंदों में चार गगनचुंबी छक्कों के साथ नाबाद चौवन रनों की मैच पलटने वाली पारी खेली। "
                "तनुष कोटियन के अट्ठाईस और आखिरी ओवर में हर्ष दुबे के तेज़ रनों ने टीम को तीन सौ सत्रह तक पहुँचा दिया।"
            ),
            "shots": [
                {"img": "news/build_02/extra_candidates/extra_08_shahbaz.jpg", "motion": "zoom_in_top", "xfade": "slideleft"},
                {"img": "news/build_02/extra_candidates/extra_09_shahbaz.jpg", "motion": "pan_left_to_right", "xfade": "wiperight"},
                {"img": "news/build_02/extra_candidates/extra_10_shahbaz.jpg", "motion": "zoom_in_center", "xfade": "smoothleft"},
            ],
        },
        {
            "id": "outro_target",
            "text": (
                "अब फाइनल में जगह पक्की करने के लिए श्रीलंका ए के सामने तीन सौ अठारह रनों की कड़ी चुनौती है। "
                "देखना दिलचस्प होगा कि भारतीय गेंदबाज़ इस लक्ष्य का बचाव कैसे करते हैं। बने रहिए हमारे साथ!"
            ),
            "shots": [
                {"img": "news/build_02/extra_candidates/extra_05_art.jpg", "motion": "zoom_in_top", "xfade": "slideright"},
                {"img": "news/build_02/extra_candidates/extra_06_art.jpg", "motion": "zoom_out_center", "xfade": None},
            ],
        },
    ]

    # If SL-A 2nd innings is actually underway live while script runs, dynamically mention chase update in outro
    if batting_team == "SL-A" and runs > 0:
        beats[-1]["text"] = (
            f"तीन सौ अठारह रन के लक्ष्य का पीछा करते हुए श्रीलंका ए का स्कोर फिलहाल {wickets} विकेट पर {runs} रन है। "
            "सेमीफ़ाइनल का रोमांच अपने चरम पर है, बने रहिए हमारे साथ!"
        )
    elif str(state.get("match_result") or "").strip():
        beats[-1]["text"] = (
            "रोमांचक पहले सेमीफ़ाइनल में इस बड़े स्कोर ने मुकाबले की दिशा तय की। "
            "क्रिकेट की ऐसी ही तेज़ और सटीक खबरों के लिए बने रहिए हमारे साथ!"
        )

    return beats


def _build_zoompan_expr(motion: str, n_frames: int) -> str:
    d = max(1, n_frames - 1)
    if motion == "zoom_in_center":
        z = f"1.02+0.16*on/{d}"
        x = "(iw-iw/zoom)*0.5"
        y = "(ih-ih/zoom)*0.5"
    elif motion == "zoom_in_top":
        z = f"1.02+0.16*on/{d}"
        x = "(iw-iw/zoom)*0.5"
        y = "(ih-ih/zoom)*0.16"
    elif motion == "zoom_in_fast":
        z = f"1.00+0.24*on/{d}"
        x = "(iw-iw/zoom)*0.48"
        y = "(ih-ih/zoom)*0.24"
    elif motion == "zoom_out_center":
        z = f"1.18-0.16*on/{d}"
        x = "(iw-iw/zoom)*0.5"
        y = "(ih-ih/zoom)*0.28"
    elif motion == "pan_left_to_right":
        z = "1.14"
        x = f"(iw-iw/zoom)*(on/{d})"
        y = "(ih-ih/zoom)*0.25"
    elif motion == "pan_right_to_left":
        z = "1.14"
        x = f"(iw-iw/zoom)*(1-on/{d})"
        y = "(ih-ih/zoom)*0.25"
    else:
        z = f"1.02+0.14*on/{d}"
        x = "(iw-iw/zoom)*0.5"
        y = "(ih-ih/zoom)*0.3"
    return f"scale=2560:1440,zoompan=z='{z}':x='{x}':y='{y}':d={n_frames}:s=1280x720:fps={FPS},format=yuv420p"


async def main() -> None:
    state = await _fetch_live_state()
    beats = _build_story_beats(state)

    # 1. Synthesize Fish Audio TTS per beat cleanly
    beat_audio_paths: list[Path] = []
    beat_durations: list[float] = []

    for idx, beat in enumerate(beats):
        mp3_path = AUDIO_DIR / f"beat_{idx:02d}.mp3"
        print(f"Synthesizing beat {idx+1}/{len(beats)} [{beat['id']}]...")
        audio_bytes = await synthesize_fish_audio(beat["text"], speaker="host", mood="conversational")
        if not audio_bytes:
            raise RuntimeError(f"Fish Audio returned empty audio for beat {beat['id']}")
        mp3_path.write_bytes(audio_bytes)
        dur = _probe_duration(mp3_path)
        if dur <= 0.5:
            dur = await get_mp3_duration_sec(audio_bytes)
        beat_audio_paths.append(mp3_path)
        beat_durations.append(dur)
        print(f"  beat_{idx:02d}.mp3 -> {dur:.2f}s ({len(beat['text'].split())} words)")

    # Concatenate beats + exact 0.28s silences via decoded filter_complex (no muxer sample-rate mismatch)
    voice_full = BUILD_DIR / "voice_full.mp3"
    audio_cmd: list[str] = ["ffmpeg", "-y", "-v", "error"]
    for p in beat_audio_paths:
        audio_cmd.extend(["-i", str(p)])
    n_beats = len(beat_audio_paths)
    af_parts: list[str] = []
    concat_inputs: list[str] = []
    for idx in range(n_beats):
        af_parts.append(f"[{idx}:a]aresample=48000,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=mono[a{idx}]")
        concat_inputs.append(f"[a{idx}]")
        if idx < n_beats - 1:
            af_parts.append(
                f"anullsrc=r=48000:cl=mono:d={PAUSE_BETWEEN_BEATS_SEC:.3f}[s{idx}]"
            )
            concat_inputs.append(f"[s{idx}]")
    n_segments = 2 * n_beats - 1
    af_parts.append(
        f"{''.join(concat_inputs)}concat=n={n_segments}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=9[aout]"
    )
    af_script = AUDIO_DIR / "audio_concat.ffscript"
    af_script.write_text(";\n".join(af_parts), encoding="utf-8")
    audio_cmd.extend(
        [
            "-filter_complex_script",
            str(af_script),
            "-map",
            "[aout]",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(voice_full),
        ]
    )
    _run(audio_cmd, "concat audio beats via filter_complex")

    expected_audio_dur = sum(beat_durations) + (n_beats - 1) * PAUSE_BETWEEN_BEATS_SEC
    total_audio_dur = _probe_duration(voice_full)
    print(f"\nTotal voiceover duration: {total_audio_dur:.2f}s (expected ~{expected_audio_dur:.2f}s, target < 120s)")
    if abs(total_audio_dur - expected_audio_dur) > 1.0:
        raise RuntimeError(f"Audio concat drift detected: got {total_audio_dur:.2f}s vs expected {expected_audio_dur:.2f}s")
    if total_audio_dur >= 118.0:
        raise RuntimeError(f"Voiceover too long ({total_audio_dur:.2f}s >= 118s)! Trim beats.")

    # 2. Build flat shot schedule synced to exact beat windows
    shots: list[dict[str, Any]] = []
    for idx, beat in enumerate(beats):
        # Include the pause after non-final beats inside the beat's visual slot
        slot_total = beat_durations[idx] + (PAUSE_BETWEEN_BEATS_SEC if idx < len(beats) - 1 else 0.35)
        n_shots = len(beat["shots"])
        each_slot = slot_total / n_shots
        for s in beat["shots"]:
            shots.append({
                "src": ROOT_DIR / s["img"],
                "motion": s["motion"],
                "xfade": s["xfade"],
                "slot_dur": each_slot,
            })

    # Match exact total timeline to voice_full duration (+0.35s clean tail fade-out)
    target_video_dur = total_audio_dur + 0.35
    sum_slots = sum(s["slot_dur"] for s in shots)
    scale_factor = target_video_dur / sum_slots
    for s in shots:
        s["slot_dur"] *= scale_factor

    # 3. Normalize images & render individual zoompan clips
    norm_paths: list[Path] = []
    clip_paths: list[Path] = []
    clip_durs: list[float] = []

    print(f"\nRendering {len(shots)} zoomed/panned clips...")
    for idx, shot in enumerate(shots):
        src_img: Path = shot["src"]
        if not src_img.exists():
            raise FileNotFoundError(f"Missing verified shot image: {src_img}")
        norm_p = NORM_DIR / f"frame_{idx:02d}.jpg"
        _normalize_to_1280x720(src_img, norm_p)
        norm_paths.append(norm_p)

        has_next = idx < len(shots) - 1
        # Extend clip duration by TRANSITION_SEC for all except final clip so xfade keeps slot alignment exact
        clip_target_sec = shot["slot_dur"] + (TRANSITION_SEC if has_next else 0.0)
        n_frames = max(30, round(clip_target_sec * FPS))
        actual_sec = n_frames / FPS
        clip_p = CLIP_DIR / f"clip_{idx:02d}.mp4"
        vf = _build_zoompan_expr(shot["motion"], n_frames)
        _run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-i",
                str(norm_p),
                "-vf",
                vf,
                "-frames:v",
                str(n_frames),
                "-r",
                str(FPS),
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "18",
                "-pix_fmt",
                "yuv420p",
                str(clip_p),
            ],
            f"render zoompan clip_{idx:02d}",
        )
        clip_paths.append(clip_p)
        clip_durs.append(actual_sec)
        print(f"  clip_{idx:02d}.mp4: {shot['motion']:<18} {n_frames}f ({actual_sec:.2f}s) next_xfade={shot['xfade']}")

    # 4. Chain clips sequentially with sliding/wipe xfade transitions + clean fade in/out
    filter_parts: list[str] = []
    prev_label = "[0:v]"
    running_dur = clip_durs[0]
    for idx in range(len(clip_paths) - 1):
        trans = shots[idx]["xfade"] or "slideleft"
        offset = max(0.2, running_dur - TRANSITION_SEC)
        out_label = f"[v{idx:02d}]" if idx < len(clip_paths) - 2 else "[vjoined]"
        filter_parts.append(
            f"{prev_label}[{idx+1}:v]xfade=transition={trans}:duration={TRANSITION_SEC:.3f}:offset={offset:.3f}{out_label}"
        )
        prev_label = out_label
        running_dur = offset + clip_durs[idx + 1]

    fade_out_start = max(1.0, running_dur - 0.50)
    filter_parts.append(
        f"[vjoined]fade=t=in:st=0:d=0.30,fade=t=out:st={fade_out_start:.3f}:d=0.50,format=yuv420p[vfinal]"
    )

    ffscript = BUILD_DIR / "xfade.ffscript"
    ffscript.write_text(";\n".join(filter_parts), encoding="utf-8")

    cmd: list[str] = ["ffmpeg", "-y", "-v", "error"]
    for cp in clip_paths:
        cmd.extend(["-i", str(cp)])
    audio_idx = len(clip_paths)
    cmd.extend(["-i", str(voice_full)])
    cmd.extend(
        [
            "-filter_complex_script",
            str(ffscript),
            "-map",
            "[vfinal]",
            "-map",
            f"{audio_idx}:a",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(VIDEO_OUT),
        ]
    )
    print(f"\nStitching final video ({running_dur:.2f}s projected) -> {VIDEO_OUT}...")
    _run(cmd, "stitch final xfade video")

    final_dur = _probe_duration(VIDEO_OUT)
    size_mb = VIDEO_OUT.stat().st_size / (1024 * 1024)
    print(f"\nDONE! Rendered {VIDEO_OUT} | Duration: {final_dur:.2f}s | Size: {size_mb:.2f} MB")


if __name__ == "__main__":
    asyncio.run(main())
