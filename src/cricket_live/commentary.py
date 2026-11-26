"""Dynamic two-person Hindi cricket commentary (Host + Expert) with FFmpeg audio polish."""

from __future__ import annotations

import asyncio
import hashlib
import os
import random
import shutil
from pathlib import Path

from dotenv import load_dotenv
import httpx

load_dotenv(override=True)

from .db import get_news_items, pick_next_story, seed_commentary_stories
from .models import ScoreboardState

TTS_CACHE_DIR = Path(__file__).resolve().parents[2] / "cache" / "tts"

PREWRITTEN_STORIES: list[tuple[str, str, str, str]] = [
    (
        "dubai_dew",
        "दुबई इंटरनेशनल स्टेडियम में जैसे-जैसे रात बढ़ती है, ओस यानी ड्यू का असर दिखने लगता है।",
        "बिल्कुल सही! दुबई में चेज़ करने वाली टीम को दूसरी पारी में 58 प्रतिशत मैचों में जीत मिली है, क्योंकि गीली गेंद से स्पिनरों को ग्रिप नहीं मिलता!",
        "ilt20",
    ),
    (
        "dubai_ring_of_fire",
        "अच्छा एक दिलचस्प बात दुबई स्टेडियम की — यहाँ फ्लडलाइट्स टावर पर नहीं बल्कि पूरी छत पर रिंग ऑफ फायर की तरह लगी हैं!",
        "जी हाँ! इससे मैदान पर खिलाड़ियों की परछाई बहुत कम बनती है और हाई कैच पकड़ना थोड़ा अलग अनुभव होता है!",
        "ilt20",
    ),
    (
        "noor_ahmad",
        "नूर अहमद की कलाई की स्पिन इस पिच पर बल्लेबाज़ों को लगातार परेशान कर रही है।",
        "उनकी गुगली और तेज़ रॉन्ग-वन को पढ़ना टी20 में बहुत मुश्किल है, खासकर जब रन रेट नौ के ऊपर जा रहा हो!",
        "ilt20",
    ),
    (
        "mustafizur_cutter",
        "मुस्तफिज़ुर रहमान जब गेंदबाज़ी पर आते हैं, तो उनकी स्लोअर कटर का जवाब किसी के पास नहीं होता।",
        "डेथ ओवर्स में फज़ का एंगल और चेंज ऑफ पेस दुबई की पिच पर सबसे बड़ा हथियार है!",
        "ilt20",
    ),
    (
        "stoinis_allrounder",
        "मार्कस स्टोइनिस को देखो — बैटिंग हो या बॉलिंग, हर डिपार्टमेंट में मैच का रुख पलटने का दम रखते हैं।",
        "और टी20 लीग्स में ऐसे पावर-हिटर ऑलराउंडर का होना किसी भी कप्तान के लिए सोने पर सुहागा होता है!",
        "ilt20",
    ),
    (
        "ilt20_points_battle",
        "आईएलटी20 के पॉइंट्स टेबल पर नज़र डालें तो हर एक जीत और नेट रन रेट बहुत मायने रखता है।",
        "बिल्कुल! टॉप चार में जगह बनाने के लिए टीमें आखिरी गेंद तक नेट रन रेट बचाने की कोशिश करती हैं!",
        "ilt20",
    ),
    (
        "pace_vs_spin_dubai",
        "आंकड़े बताते हैं कि दुबई में पिछले दस मैचों में तेज़ गेंदबाज़ों ने 59 प्रतिशत और स्पिनरों ने 41 प्रतिशत विकेट निकाले हैं।",
        "मतलब नई गेंद से पेसर्स को स्विंग मिलता है और बीच के ओवरों में स्पिनर्स गेम कंट्रोल करते हैं!",
        "ilt20",
    ),
    (
        "sehwag_story",
        "अच्छा एक बात बताओ यार... जब मैदान पर इतना प्रेशर होता है, तो बैट्समैन खुद को शांत कैसे रखते हैं?",
        "हाहा, मुझे वीरेंद्र सहवाग का किस्सा याद आ गया! 300 रन की पारी खेलते वक्त भी वो क्रीज़ पर किशोर कुमार के गाने गुनगुनाते रहते थे!",
        "general",
    ),
    (
        "dhoni_helicopter",
        "लास्ट ओवर्स में बड़े शॉट्स देखकर हमेशा महेंद्र सिंह धोनी के हेलीकॉप्टर शॉट की याद आ जाती है।",
        "और मज़ेदार बात ये है कि धोनी ने वो शॉट रांची में टेनिस बॉल क्रिकेट खेलते हुए अपने दोस्त संतोष लाल से सीखा था!",
        "general",
    ),
    (
        "sachin_200",
        "वनडे क्रिकेट में पहले दोहरे शतक का ज़िक्र आज भी हर फैन के चेहरे पर मुस्कान ले आता है।",
        "2010 में ग्वालियर में सचिन तेंदुलकर ने 200 नॉट आउट बनाकर इतिहास रच दिया था — पूरा स्टेडियम झूम उठा था!",
        "general",
    ),
    (
        "keeper_chatter",
        "स्टंप माइक पर विकेटकीपर की बातें सुनने में भी बड़ा मज़ा आता है न!",
        "अरे बिल्कुल! कीपर का आधा काम कैच पकड़ना है और बाकी आधा काम बल्लेबाज़ के दिमाग में हल्का सा शक पैदा करना!",
        "general",
    ),
    (
        "dressing_room_ritual",
        "ड्रेसिंग रूम में खिलाड़ियों के अपने-अपने लकी चार्म और टोटके बड़े मज़ेदार होते हैं।",
        "कोई बायाँ पैड पहले बांधता है, तो कोई अपनी लकी जर्सी या बैटिंग ग्लव्स पूरी सीरीज़ नहीं बदलता!",
        "general",
    ),
    (
        "super_over_thrill",
        "टी20 क्रिकेट में जब भी मैच आखिरी ओवर तक जाता है, फैंस की धड़कनें तेज़ हो जाती हैं।",
        "और अगर सुपर ओवर हो जाए, तो मानो पूरा स्टेडियम एक सांस में सिमट जाता है — छह गेंदों में पूरी मेहनत का फैसला!",
        "general",
    ),
    (
        "yorker_art",
        "डेथ ओवर्स में यॉर्कर डालना आज भी क्रिकेट की सबसे मुश्किल कला मानी जाती है।",
        "एक इंच आगे गिरी तो फुलटॉस और एक इंच पीछे तो स्लॉट में छक्का! इसलिए बूम-बूम बुमराह और मलिंगा जैसे बॉलर्स इतने खास होते हैं।",
        "general",
    ),
    (
        "boundary_fielding",
        "आजकल बाउंड्री रोप पर फील्डिंग का स्तर इतना ऊँचा हो गया है कि पक्के छक्के भी कैच में बदल जाते हैं।",
        "बिल्कुल! हवा में छलांग लगाकर गेंद को अंदर फेंकना अब टी20 क्रिकेट की सबसे बड़ी हाईलाइट बन चुका है।",
        "general",
    ),
    (
        "captaincy_chess",
        "कप्तान के लिए सबसे कठिन पल वो होता है जब सेट बल्लेबाज़ को रोकने के लिए फील्ड बदलनी हो।",
        "सही कहा! एक एक्सट्रा कवर ऊपर बुलाओ या लॉन्ग-ऑन डीप रखो — हर एक कदम गेंदबाज़ के प्लान से जुड़ा होता है।",
        "general",
    ),
    (
        "slower_bouncer",
        "आज के तेज़ गेंदबाज़ सिर्फ रफ्तार पर नहीं बल्कि धीमे बाउंसर पर भी खूब विकेट निकालते हैं।",
        "जब बल्लेबाज़ 145 की रफ्तार का इंतज़ार कर रहा हो और गेंद 115 की आए, तो शॉट की टाइमिंग पूरी तरह बिगड़ जाती है!",
        "general",
    ),
    (
        "crowd_energy",
        "स्टेडियम में दर्शकों का शोर जब गूंजता है, तो खिलाड़ियों में अलग ही जोश आ जाता है।",
        "सही बात है! खासकर जब होम टीम या पसंदीदा बल्लेबाज़ बाउंड्री लगाए, तो पूरा माहौल बिजली जैसा हो जाता है।",
        "general",
    ),
    (
        "ilt20_star_power",
        "आईएलटी20 की सबसे खास बात ये है कि दुनिया भर के टॉप टी20 विशेषज्ञ एक ही लीग में भिड़ते हैं।",
        "जी हाँ! वेस्टइंडीज के पावर-हिटर्स से लेकर अफ़ग़ान स्पिनर्स और इंग्लिश स्ट्रोक-मेकर्स तक — हर मैच हाई-वोल्टेज होता है!",
        "ilt20",
    ),
    (
        "debut_nerves",
        "जब कोई युवा खिलाड़ी बड़े मंच पर पहली बार बल्लेबाज़ी करने आता है, तो पहली दस गेंदें सबसे अहम होती हैं।",
        "बिल्कुल! एक बार पहला चौका लग जाए, तो सारा नर्वसनेस गायब हो जाता है और नेचुरल गेम बाहर आता है।",
        "general",
    ),
]


def seed_default_stories() -> int:
    """Persist pre-written commentary stories into SQLite for reuse."""
    return seed_commentary_stories(PREWRITTEN_STORIES)

FISH_TTS_URL = "https://api.fish.audio/v1/tts"

CommentaryTurn = tuple[str, str]  # (speaker: "host" | "expert", text)

_recent_filler_ids: list[int] = []
_tts_cache: dict[tuple[str, str], bytes] = {}


def _find_ffmpeg() -> str | None:
    """Locate ffmpeg on PATH or inside Playwright's local browser cache."""
    on_path = shutil.which("ffmpeg")
    if on_path:
        return on_path
    local_app = os.getenv("LOCALAPPDATA", "")
    if local_app:
        pw_dir = Path(local_app) / "ms-playwright"
        if pw_dir.exists():
            matches = sorted(pw_dir.glob("ffmpeg-*/ffmpeg*.exe"))
            if matches:
                return str(matches[-1])
    return None


async def get_mp3_duration_sec(mp3_bytes: bytes) -> float:
    """Measure exact MP3 duration in seconds using FFmpeg."""
    ffmpeg = _find_ffmpeg()
    if not ffmpeg or not mp3_bytes:
        return 3.5
    proc = await asyncio.create_subprocess_exec(
        ffmpeg, "-f", "mp3", "-i", "pipe:0", "-f", "null", "-",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate(input=mp3_bytes)
    text = stderr.decode("utf-8", "ignore")
    last_time = 0.0
    for line in text.splitlines():
        if "time=" in line:
            part = line.split("time=")[-1].split()[0].strip()
            try:
                h, m, s = part.split(":")
                last_time = int(h) * 3600 + int(m) * 60 + float(s)
            except Exception:
                pass
    return last_time if last_time > 0.2 else 3.5


async def polish_audio_mp3(raw_bytes: bytes, speaker: str = "host", input_format: str = "wav") -> bytes:
    """Clean lossless WAV/MP3 speech: denoise fuzz, remove boxiness, boost vocal clarity, and encode crisp 192k MP3."""
    ffmpeg = _find_ffmpeg()
    if not ffmpeg or not raw_bytes:
        return raw_bytes

    if speaker == "expert":
        # Clean, grounded male studio analyst EQ + gentle denoise
        timbre = (
            "highpass=f=85,"
            "afftdn=nf=-28,"
            "equalizer=f=300:t=o:w=1.2:g=-1.2,"
            "equalizer=f=2800:t=o:w=1.4:g=2.4,"
            "treble=g=1.4:f=8000,"
            "acompressor=threshold=-17dB:ratio=1.9:attack=15:release=130,"
        )
    else:
        # Crystal-clear, lively, zero-fuzz broadcast filter for Cheerful RJ Female Host
        timbre = (
            "highpass=f=100,"
            "afftdn=nf=-26,"
            "equalizer=f=320:t=o:w=1.2:g=-1.8,"
            "equalizer=f=3400:t=o:w=1.4:g=2.8,"
            "treble=g=2.2:f=7500,"
            "acompressor=threshold=-16dB:ratio=1.8:attack=15:release=120,"
        )

    af_chain = (
        f"{timbre}"
        "apad=pad_dur=0.22,"
        "afade=t=in:st=0:d=0.03,"
        "areverse,afade=t=in:st=0:d=0.12,areverse,"
        "loudnorm=I=-16:TP=-1.5:LRA=8"
    )
    proc = await asyncio.create_subprocess_exec(
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        input_format,
        "-i",
        "pipe:0",
        "-af",
        af_chain,
        "-c:a",
        "libmp3lame",
        "-b:a",
        "192k",
        "-f",
        "mp3",
        "pipe:1",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate(input=raw_bytes)
    if proc.returncode == 0 and stdout:
        return stdout
    return raw_bytes


def _clean_crex_comm(raw: str) -> str:
    """Clean ball prefix from CREX commentary string for natural TTS reading."""
    txt = (raw or "").strip()
    parts = txt.split(" ", 1)
    if len(parts) == 2 and any(c.isdigit() for c in parts[0]):
        txt = parts[1].strip()
    # Strip trailing standalone 1-char tokens like 'W', '4', '6', '1', '0' right after bowler-batter header
    return txt[:260]


def generate_commentary_turns(
    prev: ScoreboardState | None, curr: ScoreboardState
) -> list[CommentaryTurn]:
    """Generate varied Host + Expert Hindi commentary turns when the match state advances."""
    if prev is None:
        return []

    striker = curr.striker.name.title()
    bowler = curr.bowler.name.title()
    team = curr.batting_team
    score_diff = curr.runs - prev.runs
    wicket_fell = curr.wickets > prev.wickets
    overs_changed = curr.overs != prev.overs
    last_ball = curr.curr_over.balls[-1].upper() if curr.curr_over.balls else ""

    if wicket_fell or (overs_changed and last_ball == "W"):
        if curr.live_commentary and curr.live_commentary != prev.live_commentary:
            clean_crex = _clean_crex_comm(curr.live_commentary)
            if clean_crex:
                expert_lines = [
                    f"अरे भाई! यही तो खूबसूरती है इस खेल की! {bowler} ने जाल बिछाया और बल्लेबाज़ सीधा फंस गए!",
                    f"क्या गेंद थी यार! एकदम सटीक लाइन और लेंथ... ड्रेसिंग रूम में इस वक्त सन्नाटा छा गया होगा!",
                ]
                return [("host", clean_crex), ("expert", random.choice(expert_lines))]
        host_lines = [
            f"आउट! बड़ा झटका! {bowler} ने शानदार गेंद पर विकेट चटकाया। {team} {curr.runs} पर {curr.wickets}।",
            f"और ये विकेट गिरता हुआ! {bowler} की सटीक गेंद ने कमाल कर दिया। स्कोर {curr.runs} पर {curr.wickets}।",
            f"कमाल की बॉलिंग! {bowler} को मिली बड़ी सफलता, पवेलियन लौटना होगा बल्लेबाज़ को!",
        ]
        expert_lines = [
            f"अरे भाई! यही तो खूबसूरती है इस खेल की! {bowler} ने जाल बिछाया और बल्लेबाज़ सीधा फंस गए!",
            f"क्या गेंद थी यार! एकदम सटीक लाइन और लेंथ... ड्रेसिंग रूम में इस वक्त सन्नाटा छा गया होगा!",
            f"बिलकुल सही समय पर ब्रेकथ्रू मिला है — यहाँ से मैच का मोमेंटम बदल सकता है!",
        ]
        return [("host", random.choice(host_lines)), ("expert", random.choice(expert_lines))]

    if score_diff >= 6 or (overs_changed and last_ball == "6"):
        if curr.live_commentary and curr.live_commentary != prev.live_commentary:
            clean_crex = _clean_crex_comm(curr.live_commentary)
            if clean_crex:
                return [("host", clean_crex), ("expert", f"ओहोहो! ज़बरदस्त बैट स्विंग {striker} का, सीधा दर्शकों के बीच!")]
        host_lines = [
            f"छक्का! {striker} का ज़ोरदार प्रहार, गेंद सीधा दर्शकों के बीच! {team} {curr.runs} पर {curr.wickets}।",
            f"गगनचुंबी छक्का! {striker} ने {bowler} की गेंद को मैदान के बाहर पहुंचा दिया!",
            f"कमाल का शॉट! छह रन {striker} के खाते में, पूरा स्टेडियम झूम उठा है!",
        ]
        expert_lines = [
            f"ओहोहो! आवाज़ सुनी बल्ले की? प्योर टाइमिंग भाई, स्टैंड्स में बैठे दर्शक भी खड़े हो गए!",
            f"क्या बात है! बॉलर सोच ही रहे थे कि कहाँ डालूँ, और {striker} ने गेंद को हवाई यात्रा पर भेज दिया!",
            f"ज़बरदस्त बैट स्विंग! इस तरह के छक्के गेंदबाज़ का हौसला तोड़ देते हैं!",
        ]
        return [("host", random.choice(host_lines)), ("expert", random.choice(expert_lines))]

    if score_diff == 4 or (overs_changed and last_ball == "4"):
        if curr.live_commentary and curr.live_commentary != prev.live_commentary:
            clean_crex = _clean_crex_comm(curr.live_commentary)
            if clean_crex:
                return [("host", clean_crex), ("expert", f"वाह! इसे कहते हैं नज़ाकत और टाइमिंग — लाजवाब चौका {striker}!")]
        host_lines = [
            f"शानदार चौका! {striker} ने बेहतरीन गैप निकाला। स्कोर अब {curr.runs} पर {curr.wickets}।",
            f"चार रन! {striker} के बल्ले से क्लासिक शॉट, फील्डर के पास कोई मौका नहीं।",
            f"बेहतरीन बाउंड्री! {striker} ने {bowler} की गेंद को सीमा रेखा के पार भेजा!",
        ]
        expert_lines = [
            f"वाह! इसे कहते हैं नज़ाकत! ताकत कम और टाइमिंग ज़्यादा — लाजवाब शॉट {striker}!",
            f"बिलकुल टेक्स्टबुक शॉट था ये! जब बल्लेबाज़ लय में हो, तो ऐसी बाउंड्री अपने आप आती है!",
            f"फील्डिंग के हिसाब से बिल्कुल सही जगह शॉट खेला — चार रन पक्के थे!",
        ]
        return [("host", random.choice(host_lines)), ("expert", random.choice(expert_lines))]

    if curr.live_commentary and curr.live_commentary != prev.live_commentary:
        parts = curr.live_commentary.split(" ", 1)
        clean_line = (
            parts[1].strip()
            if len(parts) == 2 and any(c.isdigit() for c in parts[0])
            else curr.live_commentary.strip()
        )
        if clean_line:
            return [("host", clean_line)]

    if score_diff > 0:
        host_lines = [
            f"{striker} ने {bowler} की गेंद को हल्के हाथों से खेलकर {score_diff} रन चुराया। स्कोर {curr.runs} पर {curr.wickets}।",
            f"अच्छी रनिंग बिटवीन द विकेट्स, {score_diff} रन के साथ {team} {curr.runs} पर {curr.wickets}।",
            f"गैप में धकेला और तेज़ी से {score_diff} रन पूरे किए — स्कोरबोर्ड लगातार चलता हुआ।",
            f"चतुराई से स्ट्राइक रोटेट किया {striker} ने, {score_diff} रन जुड़े {team} के खाते में।",
            f"बढ़िया क्रिकेट! बिना रिस्क लिए {score_diff} रन बटोरे, अब स्कोर {curr.runs} पर {curr.wickets}।",
        ]
        return [("host", random.choice(host_lines))]

    if overs_changed:
        dot_lines = [
            f"{bowler} की कसी हुई गेंद, कोई रन नहीं। {team} {curr.runs} पर {curr.wickets}।",
            f"अच्छा डिफेंस {striker} का, {bowler} दबाव बनाए हुए हैं।",
            f"डॉट बॉल! {bowler} ने बिल्कुल सटीक लेंथ पकड़ी है, स्कोर {curr.runs} पर {curr.wickets}।",
            f"बीट हुए बल्लेबाज़! शानदार गेंद {bowler} की, कोई रन नहीं मिला।",
            f"सीधा फील्डर के हाथ में शॉट, {striker} को रन चुराने का मौका नहीं मिला।",
            f"बहुत कसी हुई ओवर चल रही है, {bowler} बल्लेबाज़ों को बांधे हुए हैं।",
        ]
        return [("host", random.choice(dot_lines))]

    return []


def generate_filler_dialogue(curr: ScoreboardState, _index: int = 0) -> list[CommentaryTurn]:
    """Pick a fresh, non-repeating conversational story/banter/fact between Host and Expert."""
    striker = curr.striker.name.title()
    non_striker = curr.non_striker.name.title()
    bowler = curr.bowler.name.title()
    team = curr.batting_team
    bowl_team = curr.bowling_team

    # Situation-aware mood line
    if curr.wickets >= 5:
        situation_note = f"{team} ने {curr.wickets} विकेट गंवा दिए हैं, अब साझेदारी बहुत ज़रूरी है।"
    elif curr.crr >= 5.5:
        situation_note = f"रन रेट {curr.crr:.2f} का है, बल्लेबाज़ पूरी तरह हावी दिख रहे हैं!"
    else:
        situation_note = f"स्कोर {curr.overs} ओवर में {curr.runs} पर {curr.wickets} है और मुकाबला बराबरी का चल रहा है।"

    pool: list[list[CommentaryTurn]] = [
        # 1. Situation + Strategy
        [
            ("host", f"हम्म... तो अगर स्कोर पर नज़र डालें, {situation_note} मतलब... गेम अभी खुला हुआ है, है न?"),
            ("expert", f"बिल्कुल भाई! क्रिकेट में अगले आधे घंटे का खेल हमेशा निर्णायक होता है। अगर {striker} और {non_striker} टिके रहे, तो {bowl_team} की मुश्किलें बढ़ेंगी!"),
        ],
        # 2. Sehwag Kishore Kumar Story
        [
            ("host", "अच्छा एक बात बताओ यार... जब मैदान पर इतना प्रेशर होता है, तो बैट्समैन खुद को शांत कैसे रखते हैं?"),
            ("expert", "हाहा, मुझे वीरेंद्र सहवाग का किस्सा याद आ गया! 300 रन की पारी खेलते वक्त भी वो क्रीज़ पर किशोर कुमार के गाने गुनगुनाते रहते थे! बॉलर बेचारा पसीने में और वीरू भाई गाने के मूड में!"),
        ],
        # 3. High-altitude / Pitch Physics Fact
        [
            ("host", f"देखो... अभी {bowler} लगातार तेज़ पेस से डाल रहे हैं, और बॉल बैट पर बड़ी तेज़ी से आ रही है।"),
            ("expert", "जी हाँ! और एक दिलचस्प साइंस फैक्ट बताऊँ — ऊँचाई वाले मैदानों पर हवा थोड़ी पतली होती है, तो गेंद स्विंग कम और ट्रैवल दस प्रतिशत ज़्यादा करती है! मतलब हल्का सा भी कनेक्शन हुआ तो सीधा बाउंड्री!"),
        ],
        # 4. Dhoni Helicopter Shot Origin
        [
            ("host", f"हम्म, {striker} अभी {curr.striker.runs} रन पर खेल रहे हैं... लग रहा है बड़े शॉट की फिराक में हैं!"),
            ("expert", "वैसे बड़े शॉट से याद आया — महेंद्र सिंह धोनी का हेलीकॉप्टर शॉट उन्होंने टेनिस बॉल क्रिकेट में अपने दोस्त संतोष लाल से सीखा था! गली क्रिकेट की तकनीक इंटरनेशनल क्रिकेट की पहचान बन गई!"),
        ],
        # 5. Funny Lucky Charm / Dressing Room Story
        [
            ("host", "अच्छा ये तो मानना पड़ेगा... ड्रेसिंग रूम में प्लेयर्स के अजीब टोटके भी बड़े मज़ेदार होते हैं, सही कहा न?"),
            ("expert", "अरे पूछो मत! कई खिलाड़ी तो जब तक शतक या अर्धशतक चलता है, अपने बैटिंग ग्लव्स या सीट तक नहीं बदलते! कोई बायाँ पैड पहले बांधता है तो कोई चाय का कप एक ही कोने में रखता है!"),
        ],
        # 6. Bowler Mind Games
        [
            ("host", f"सुनो... {bowler} ने अभी तक {curr.bowler.overs} ओवर में {curr.bowler.runs_conceded} रन देकर {curr.bowler.wickets} विकेट लिए हैं। क्या प्लान चल रहा होगा दिमाग में?"),
            ("expert", f"देखो, तेज़ गेंदबाज़ हमेशा दो ओवर आगे की सोचता है। पहले दो आउटस्विंगर दिखाकर बल्लेबाज़ को बाहर खींचो, और फिर अचानक एक तेज़ इनस्विंगर या यॉर्कर! यही असली शतरंज है!"),
        ],
        # 7. Tea/Chai & Audience Connection
        [
            ("host", "हम्म, जितने भी दोस्त लाइव जुड़े हैं... आप लोग किस शहर से मैच देख रहे हो, चैट में बताओ ज़रा!"),
            ("expert", "और भाई हाथ में गरमा-गरम चाय हो और सामने लाइव क्रिकेट, इससे बेहतर शाम क्या हो सकती है! वीडियो को लाइक और सब्सक्राइब ज़रूर कर दें ताकि हर गेंद पर आवाज़ गूंजती रहे!"),
        ],
        # 8. Sachin 200* Gwalior Fact
        [
            ("host", f"अच्छा {striker} और {non_striker} के बीच पार्टनरशिप धीरे-धीरे जम रही है... यही टेस्ट और वनडे का मज़ा है!"),
            ("expert", "बिल्कुल! वैसे एक मज़ेदार रिकॉर्ड याद है? 2010 में ग्वालियर में सचिन तेंदुलकर ने जब वनडे इतिहास का पहला दोहरा शतक जड़ा था, तो आखिरी ओवरों में वो इतने थक गए थे कि दौड़ने से ज़्यादा बाउंड्री में डील कर रहे थे!"),
        ],
        # 9. Wicketkeeper Chatter
        [
            ("host", "हाहा, वैसे स्टंप माइक पर विकेटकीपर की बातें सुनने में भी बड़ा मज़ा आता है न!"),
            ("expert", "अरे बिल्कुल! कीपर का आधा काम कैच पकड़ना है और बाकी आधा काम बल्लेबाज़ का ध्यान भटकाना! 'अरे ये तो स्विंग हो रही है भाई' — बस इतना बोलकर बल्लेबाज़ के दिमाग में कीड़ा छोड़ देते हैं!"),
        ],
        # 10. Prediction Prompt
        [
            ("host", f"अच्छा क्या लगता है... अगले पाँच ओवर में {team} कितने रन जोड़ पाएगी?"),
            ("expert", f"मेरा अनुमान है कम से कम 25 से 30 रन! लेकिन अगर {bowler} ने एक और विकेट निकाल लिया, तो सारा गेम पलट जाएगा। दर्शक अपनी राय कमेंट में लिखें!"),
        ],
    ]

    if index % 3 == 1:
        news_list = get_news_items(limit=10)
        if news_list:
            item = news_list[(index // 3) % len(news_list)]
            headline = item["title"]
            return [
                ("host", f"अच्छा इसी बीच क्रिकेट जगत से एक ताज़ा खबर आ रही है — {headline}"),
                ("expert", "बिल्कुल भाई! सीज़न में हर अपडेट टीमों की रणनीति पर सीधा असर डालता है। अब वापस मैदान पर नज़र डालते हैं!"),
            ]

    db_story = pick_next_story(match_context="ilt20" if "ILT20" in (curr.series_name or "").upper() else None)
    if db_story and index % 2 == 0:
        return [("host", db_story[0]), ("expert", db_story[1])]

    available = [i for i in range(len(pool)) if i not in _recent_filler_ids]
    if not available:
        _recent_filler_ids.clear()
        available = list(range(len(pool)))

    chosen = random.choice(available)
    _recent_filler_ids.append(chosen)
    if len(_recent_filler_ids) > 6:
        _recent_filler_ids.pop(0)

    return pool[chosen]


def _format_spoken_prosody(text: str, speaker: str, mood: str) -> str:
    """Shape lively, interested conversational Hindi delivery with crisp pauses for Fish Audio S2.1-Pro."""
    out = text.strip()
    if not out:
        return out
    # Crisp conversational comma pauses (avoid heavy '...' everywhere which causes sleepy/flat cadence)
    out = out.replace(" — ", ", ").replace(" —", ",").replace("—", ", ")
    if speaker == "host":
        # Keep female Host upbeat, bright, and genuinely engaged
        if mood == "excited" and not out.startswith("[excited]"):
            out = f"[excited] {out}"
        elif mood == "conversational" and not out.startswith("["):
            out = f"[cheerful] {out}"
    elif mood == "excited" and not out.startswith("[excited]"):
        out = f"[excited] {out}"
    return out


async def synthesize_fish_audio(
    text: str, speaker: str = "host", mood: str = "conversational"
) -> bytes | None:
    """Synthesize lossless WAV from Fish Audio TTS, denoise/clarify with FFmpeg, and cache 192k MP3."""
    api_key = os.getenv("FISH_API_KEY", "").strip()
    clean_text = text.strip()
    if not api_key or not clean_text:
        return None

    spoken_text = _format_spoken_prosody(clean_text, speaker, mood)
    cache_key = (speaker, f"{mood}|{spoken_text}")
    if cache_key in _tts_cache:
        return _tts_cache[cache_key]

    if speaker == "expert":
        reference_id = os.getenv("FISH_EXPERT_REFERENCE_ID", "").strip() or os.getenv("FISH_REFERENCE_ID", "").strip()
        prosody_speed = 1.07 if mood == "excited" else 1.01
    else:
        reference_id = os.getenv("FISH_REFERENCE_ID", "").strip()
        if mood == "excited":
            prosody_speed = 1.08
        elif mood == "calm":
            prosody_speed = 1.01
        else:
            # Grounded, authoritative studio anchor speed (matching checkpoint)
            prosody_speed = 1.03

    model_name = os.getenv("FISH_MODEL", "s2.1-pro-free")
    digest = hashlib.sha256(
        f"v5|{speaker}|{mood}|{prosody_speed}|{reference_id}|{model_name}|{spoken_text}".encode("utf-8")
    ).hexdigest()[:24]
    TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    disk_path = TTS_CACHE_DIR / f"{speaker}_{digest}.mp3"
    if disk_path.exists():
        data = disk_path.read_bytes()
        if data:
            _tts_cache[cache_key] = data
            return data

    payload: dict[str, object] = {
        "text": spoken_text,
        "format": "wav",
        "sample_rate": 44100,
        "prosody": {"speed": prosody_speed, "volume": 0.0},
    }
    if reference_id:
        payload["reference_id"] = reference_id

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "model": model_name,
    }

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(FISH_TTS_URL, json=payload, headers=headers)
            resp.raise_for_status()
            polished = await polish_audio_mp3(resp.content, speaker=speaker, input_format="wav")
            _tts_cache[cache_key] = polished
            try:
                disk_path.write_bytes(polished)
            except Exception:
                pass
            return polished
    except Exception as exc:
        print(f"[fish-audio:{speaker}] TTS error: {exc}")
        return None
