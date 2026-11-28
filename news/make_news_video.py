"""Build a clean ~2-minute Hindi cricket news video using 1 narrator voice and lots of real images."""

from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

load_dotenv(override=True)

from cricket_live.commentary import get_mp3_duration_sec, synthesize_fish_audio  # noqa: E402
from news.fetcher import fetch_all_cricket_news, load_cached_news  # noqa: E402

NEWS_DIR = Path(__file__).resolve().parent
WORK_DIR = NEWS_DIR / "build_01"
IMG_RAW_DIR = WORK_DIR / "raw_imgs"
SLIDE_DIR = WORK_DIR / "slides"
AUDIO_DIR = WORK_DIR / "audio"
VIDEO_OUT_DIR = NEWS_DIR / "videos"
OUTPUT_MP4 = VIDEO_OUT_DIR / "cricket_news_01.mp4"


def _probe_image(path: Path) -> tuple[int, int, str]:
    try:
        res = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height,pix_fmt",
                "-of",
                "json",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        s = (json.loads(res.stdout).get("streams") or [{}])[0]
        return (int(s.get("width", 0)), int(s.get("height", 0)), str(s.get("pix_fmt", "")))
    except Exception:
        return (0, 0, "")


def _normalize_to_1280x720(src: Path, dest: Path, is_cutout: bool = False) -> bool:
    """Convert any photo or transparent cutout cleanly to 1280x720 JPEG without stretching."""
    w, h, pix = _probe_image(src)
    if w < 180 or h < 120:
        return False
    bg = ROOT_DIR / "ui" / "assets" / "stadium_bg.jpg"
    has_alpha = "a" in pix.lower() or is_cutout

    if has_alpha and bg.exists():
        # Composite transparent player cutout nicely on dark blurred stadium background
        filt = (
            "[0:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,"
            "gblur=sigma=8,eq=brightness=-0.18:saturation=0.95[bg];"
            "[1:v]scale=-1:640[fg];"
            "[bg][fg]overlay=(W-w)/2:H-h:format=auto,format=yuv420p"
        )
        cmd = ["ffmpeg", "-y", "-i", str(bg), "-i", str(src), "-filter_complex", filt, "-q:v", "2", str(dest)]
    elif w / max(h, 1) < 1.25:
        # Portrait or square image: blurred self-backdrop + sharp centered foreground (no cropped heads)
        filt = (
            "[0:v]split=2[a][b];"
            "[a]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,"
            "gblur=sigma=18,eq=brightness=-0.22[bg];"
            "[b]scale=-1:720[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p"
        )
        cmd = ["ffmpeg", "-y", "-i", str(src), "-filter_complex", filt, "-q:v", "2", str(dest)]
    else:
        # Landscape photo: clean center crop fill
        filt = "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,format=yuv420p"
        cmd = ["ffmpeg", "-y", "-i", str(src), "-vf", filt, "-q:v", "2", str(dest)]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return dest.exists() and dest.stat().st_size > 8000
    except Exception:
        return False


async def _download_news_images(items: list[dict[str, Any]]) -> dict[str, Path]:
    """Download real article images from news items, upgrading BBC thumbnails to HD where possible."""
    IMG_RAW_DIR.mkdir(parents=True, exist_ok=True)
    SLIDE_DIR.mkdir(parents=True, exist_ok=True)
    downloaded: dict[str, Path] = {}

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CricketLive/1.0"}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=15.0) as client:
        for idx, it in enumerate(items):
            url = (it.get("image_url") or "").strip()
            if not url or url in downloaded:
                continue
            candidates = [url]
            if "ichef.bbci.co.uk" in url and "/240/" in url:
                candidates.insert(0, url.replace("/240/", "/976/"))
            for cand in candidates:
                try:
                    resp = await client.get(cand)
                    if resp.status_code == 200 and len(resp.content) > 8000:
                        raw_p = IMG_RAW_DIR / f"news_{idx:02d}.jpg"
                        raw_p.write_bytes(resp.content)
                        slide_p = SLIDE_DIR / f"news_{idx:02d}.jpg"
                        if _normalize_to_1280x720(raw_p, slide_p):
                            downloaded[url] = slide_p
                            break
                except Exception:
                    continue
    return downloaded


def _prepare_local_slides() -> dict[str, Path]:
    """Prepare clean 1280x720 frames from real local photos (no floating cutout heads)."""
    SLIDE_DIR.mkdir(parents=True, exist_ok=True)
    out: dict[str, Path] = {}
    local_assets = {
        "stadium": (ROOT_DIR / "ui" / "assets" / "stadium_bg.jpg", False),
        "action": (ROOT_DIR / "ui" / "assets" / "cricket_action.jpg", False),
        "batting": (ROOT_DIR / "ui" / "assets" / "batting_hero.jpg", False),
        "bowling": (ROOT_DIR / "ui" / "assets" / "bowling_hero.jpg", False),
        "abhishek": (ROOT_DIR / "ui" / "assets" / "players" / "abhishek_sharma.jpg", False),
        "sooryavanshi": (ROOT_DIR / "ui" / "assets" / "players" / "vaibhav_sooryavanshi.jpg", False),
        "tilak": (ROOT_DIR / "ui" / "assets" / "players" / "tilak_varma.png", False),
        "liyanage": (ROOT_DIR / "ui" / "assets" / "players" / "janith_liyanage.jpg", False),
        "shahbaz": (ROOT_DIR / "ui" / "assets" / "players" / "shahbaz_ahmed.jpg", False),
        "kushagra": (ROOT_DIR / "ui" / "assets" / "players" / "kumar_kushagra.jpg", False),
        "shedge": (ROOT_DIR / "ui" / "assets" / "players" / "suryansh_shedge.png", False),
    }
    for key, (src, is_cutout) in local_assets.items():
        if src.exists():
            dest = SLIDE_DIR / f"local_{key}.jpg"
            if _normalize_to_1280x720(src, dest, is_cutout=is_cutout):
                out[key] = dest
    return out


async def _fetch_live_score_context() -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get("http://127.0.0.1:8000/api/state")
            if r.status_code == 200:
                return r.json()
    except Exception:
        pass
    return {}


async def _generate_hindi_news_beats(
    news_items: list[dict[str, Any]], live_state: dict[str, Any]
) -> list[dict[str, Any]]:
    """Use LLM (or clean structured fallback) to write a 6-beat ~2-minute Hindi news script."""
    score_line = ""
    if live_state:
        score_line = (
            f"{live_state.get('batting_team', 'India A')} {live_state.get('runs', '')}/"
            f"{live_state.get('wickets', '')} in {live_state.get('overs', '')} overs "
            f"(Toss: {live_state.get('toss', '')}, Striker: {live_state.get('striker', {}).get('name', '')})"
        )

    compact_stories = [
        {"idx": i, "source": it.get("source", ""), "title": it.get("title", ""), "summary": it.get("summary", "")[:180]}
        for i, it in enumerate(news_items[:14])
    ]

    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "").strip().rstrip("/")
    model = os.getenv("LLM_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free").strip()

    if api_key and base_url:
        prompt = (
            "Write a crisp, natural ~2-minute Hindi cricket news bulletin (total ~280 to 320 Hindi words, split into 6 beats of ~45-55 words each) "
            "for ONE male news anchor.\n"
            "Rules:\n"
            "1. Pure Devanagari Hindi only (transliterate names like इंडिया ए, श्रीलंका ए, अभिषेक शर्मा, वैभव सूर्यवंशी, तिलक वर्मा, रिंकू सिंह, शुभमन गिल, मुशीर खान, हेगली ओवल).\n"
            "2. NEVER use abbreviations like IND-A or SL-A — always say इंडिया ए and श्रीलंका ए.\n"
            "3. Strictly masculine anchor grammar (बता रहा हूँ, देखते हैं).\n"
            "4. Beat 0 should cover the big India A vs Sri Lanka A Semi-Final + live score; Beats 1-4 cover the other top global & domestic cricket news stories from the JSON; Beat 5 wraps up cleanly.\n"
            "5. Return ONLY a JSON array of 6 objects: [{\"beat\": 0, \"text\": \"...\", \"story_indices\": [0, 1]}].\n\n"
            f"Live IND-A vs SL-A status: {score_line}\n"
            f"Top Stories JSON:\n{json.dumps(compact_stories, ensure_ascii=False)}"
        )
        try:
            async with httpx.AsyncClient(timeout=35.0) as client:
                r = await client.post(
                    f"{base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.65,
                        "max_tokens": 1400,
                        "reasoning": {"effort": "none"},
                    },
                )
                if r.status_code == 200:
                    raw = (r.json().get("choices") or [{}])[0].get("message", {}).get("content", "")
                    s, e = raw.find("["), raw.rfind("]")
                    if s != -1 and e > s:
                        arr = json.loads(raw[s : e + 1])
                        if isinstance(arr, list) and len(arr) >= 5:
                            return [
                                {
                                    "text": str(x.get("text", "")).strip(),
                                    "story_indices": [int(k) for k in (x.get("story_indices") or []) if str(k).isdigit()],
                                }
                                for x in arr
                                if len(str(x.get("text", "")).strip()) > 20
                            ]
        except Exception as exc:
            print(f"[make_news_video] LLM script fallback: {exc}")

    # Grounded deterministic fallback (~290 words across 6 beats)
    runs = live_state.get("runs", 236)
    wkts = live_state.get("wickets", 6)
    ovs = live_state.get("overs", "40.1")
    return [
        {
            "text": f"नमस्कार, क्रिकेट लाइव न्यूज़ बुलेटिन में आपका स्वागत है। आज की सबसे बड़ी खबर एशिया कप राइजिंग स्टार्स के पहले सेमीफाइनल से आ रही है, जहाँ इंडिया ए और श्रीलंका ए के बीच रोमांचक मुकाबला चल रहा है। टॉस जीतकर पहले बल्लेबाज़ी करते हुए इंडिया ए ने तेज़ शुरुआत की, जहाँ वैभव सूर्यवंशी ने चालीस रन बनाए और अभिषेक शर्मा ने शानदार अर्धशतक जड़ा। ताज़ा अपडेट तक इंडिया ए का स्कोर {ovs} ओवर में {runs} रन पर {wkts} विकेट है।",
            "story_indices": [0],
        },
        {
            "text": "दूसरी बड़ी खबर भारत और न्यूज़ीलैंड टेस्ट सीरीज़ से है। वेलिंगटन में मिली निराशा के बाद अब भारतीय टीम क्राइस्टचर्च के हेगली ओवल में होने वाले दूसरे और निर्णायक टेस्ट में जीत के साथ सीरीज़ बराबर करने के इरादे से उतरेगी। हालांकि भारतीय तेज़ गेंदबाज़ी कॉम्बिनेशन को लेकर टीम मैनेजमेंट के सामने अभी भी चुनौतियाँ बनी हुई हैं।",
            "story_indices": [2, 7],
        },
        {
            "text": "इसी बीच भारतीय कप्तान शुभमन गिल का एक बड़ा बयान सुर्खियों में है। गिल ने कहा है कि टेस्ट क्रिकेट में गेंद को चमकाने के लिए फिर से लार यानी सलाइवा के इस्तेमाल की अनुमति मिलनी चाहिए, ताकि तेज़ गेंदबाज़ों को रिवर्स स्विंग में मदद मिल सके। उनके इस बयान पर क्रिकेट जगत में तेज़ बहस छिड़ गई है।",
            "story_indices": [10],
        },
        {
            "text": "घरेलू क्रिकेट की बात करें तो सैयद मुश्ताक अली ट्रॉफी में मुंबई का अजेय अभियान जारी है। मुशीर खान और अंगकृष रघुवंशी की धमाकेदार पारियों के दम पर मुंबई ने उत्तराखंड को छियासी रनों से करारी शिकस्त दी। वहीं एक अन्य रोमांचक मुकाबले में हरियाणा ने जम्मू कश्मीर पर आखिरी ओवर में दो विकेट से शानदार जीत दर्ज की।",
            "story_indices": [5],
        },
        {
            "text": "अंतरराष्ट्रीय और महिला क्रिकेट से भी दिलचस्प खबरें आई हैं। महिला बिग बैश लीग में इंग्लैंड की सारा ग्लेन ने अनोखी 'फ्री बॉल' पर खाली स्टंप उखाड़कर इतिहास रच दिया, जब डिएंड्रा डॉटिन टाइम आउट नियम में फँस गईं। वहीं स्कॉटलैंड ने ज़िम्बाब्वे के खिलाफ दमदार जीत हासिल की और हैम्पशायर ने ऑस्ट्रेलियाई लेग स्पिनर अमांडा जेड वेलिंगटन को अगले सीज़न के लिए साइन किया है।",
            "story_indices": [4, 8, 9, 1],
        },
        {
            "text": "आखिर में बात वायरल खबर की — इंडिया ए के युवा सितारे वैभव सूर्यवंशी की दो सौ चार रनों की विस्फोटक पारी पर आइसलैंड क्रिकेट ने एनवीडिया एआई चिप्स से जुड़ा मज़ेदार पोस्ट शेयर किया जो सोशल मीडिया पर जमकर वायरल हो रहा है। तो ये थीं आज की बड़ी क्रिकेट खबरें, लाइव मैच अपडेट्स के लिए हमारे साथ जुड़े रहें।",
            "story_indices": [11],
        },
    ]


async def build_first_news_video() -> Path:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    VIDEO_OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Fresh internet news + live match state
    live_state = await _fetch_live_score_context()
    news_payload = load_cached_news()
    if not news_payload.get("items"):
        news_payload = await fetch_all_cricket_news(
            match_query="IND-A vs SL-A",
            focus_terms=["ind", "india", "sl", "sri lanka", "semi final", "asia cup", "live", "win"],
            max_items=50,
        )
    items = news_payload.get("items", [])

    # 2. Download real article images + prepare local player/stadium frames (lots of images!)
    downloaded_map = await _download_news_images(items[:35])
    local_slides = _prepare_local_slides()
    news_slides = list(downloaded_map.values())
    print(f"Prepared {len(news_slides)} internet news images + {len(local_slides)} local player/stadium slides")

    # 3. Generate ~2-minute Hindi script & synthesize with single narrator voice
    beats = await _generate_hindi_news_beats(items, live_state)
    audio_clips: list[Path] = []
    durations: list[float] = []
    for idx, beat in enumerate(beats):
        audio_bytes = await synthesize_fish_audio(beat["text"], speaker="host", mood="conversational")
        if not audio_bytes:
            raise RuntimeError(f"Fish Audio synthesis failed for beat {idx}")
        mp3_path = AUDIO_DIR / f"beat_{idx:02d}.mp3"
        mp3_path.write_bytes(audio_bytes)
        dur = await get_mp3_duration_sec(audio_bytes)
        audio_clips.append(mp3_path)
        durations.append(max(4.0, dur + 0.35))
        print(f"  Beat {idx}: {dur:.2f}s | {beat['text'][:60]}...")

    total_audio_dur = sum(durations)
    print(f"Total narration duration: {total_audio_dur:.2f}s across {len(beats)} beats")

    # 4. Merge voiceover clips with clean 0.35s breath gaps into voice_full.mp3
    voice_concat_txt = WORK_DIR / "audio_concat.txt"
    sil_path = AUDIO_DIR / "silence_350ms.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.35", "-b:a", "192k", str(sil_path)],
        capture_output=True,
        check=True,
    )
    lines = []
    for i, clip in enumerate(audio_clips):
        lines.append(f"file '{clip.as_posix()}'")
        if i < len(audio_clips) - 1:
            lines.append(f"file '{sil_path.as_posix()}'")
    voice_concat_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

    full_voice = WORK_DIR / "voice_full.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(voice_concat_txt), "-c:a", "libmp3lame", "-b:a", "192k", str(full_voice)],
        capture_output=True,
        check=True,
    )

    # 5. Build rich image sequence (~4-5s per image, lots of images matching each beat!)
    pool_used: set[Path] = set()
    beat0_candidates = [
        downloaded_map.get(items[0].get("image_url", "")),
        local_slides.get("sooryavanshi"),
        local_slides.get("abhishek"),
        local_slides.get("tilak"),
        local_slides.get("stadium"),
        local_slides.get("action"),
    ]
    extra_pool = [p for p in news_slides if p is not None] + [
        local_slides.get(k) for k in ("shahbaz", "liyanage", "kushagra", "shedge", "batting", "bowling")
    ]
    extra_pool = [p for p in extra_pool if p is not None]

    def pick_slide(preferred: list[Path | None]) -> Path:
        for p in preferred:
            if p and p not in pool_used:
                pool_used.add(p)
                return p
        for p in extra_pool:
            if p not in pool_used:
                pool_used.add(p)
                return p
        # Wrap cleanly if all 25+ images were already shown once
        pool_used.clear()
        return extra_pool[0] if extra_pool else (news_slides[0])

    # Assign 4 images per beat (~24 total image switches across ~2 minutes!)
    timeline: list[tuple[Path, float]] = []
    for b_idx, beat in enumerate(beats):
        beat_dur = durations[b_idx]
        n_imgs = 4 if beat_dur >= 14.0 else 3
        per_img = beat_dur / n_imgs
        pref: list[Path | None] = []
        if b_idx == 0:
            pref.extend(beat0_candidates)
        for si in beat.get("story_indices", []):
            if 0 <= si < len(items):
                pref.append(downloaded_map.get(items[si].get("image_url", "")))
        for _ in range(n_imgs):
            timeline.append((pick_slide(pref), per_img))

    # Build FFmpeg concat file for the image sequence (last entry repeated per concat demuxer spec)
    img_concat_txt = WORK_DIR / "images_concat.txt"
    img_lines = []
    for slide_path, dur in timeline:
        img_lines.append(f"file '{slide_path.as_posix()}'")
        img_lines.append(f"duration {dur:.3f}")
    img_lines.append(f"file '{timeline[-1][0].as_posix()}'")
    img_concat_txt.write_text("\n".join(img_lines) + "\n", encoding="utf-8")

    # 6. Render clean MP4 (minimal editing: crisp images + single narrator voice)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(img_concat_txt),
            "-i",
            str(full_voice),
            "-vf",
            "fps=30,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "19",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(OUTPUT_MP4),
        ],
        capture_output=True,
        check=True,
    )
    print(f"Rendered Video #1 -> {OUTPUT_MP4} ({OUTPUT_MP4.stat().st_size / (1024*1024):.2f} MB, {len(timeline)} images)")
    return OUTPUT_MP4


if __name__ == "__main__":
    asyncio.run(build_first_news_video())
