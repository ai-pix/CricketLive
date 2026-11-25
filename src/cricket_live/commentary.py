"""Dynamic two-person Hindi cricket commentary (Host + Expert) with FFmpeg audio polish."""

from __future__ import annotations

import asyncio
import os
import random
import shutil
from pathlib import Path

import httpx

from .models import ScoreboardState

FISH_TTS_URL = "https://api.fish.audio/v1/tts"

CommentaryTurn = tuple[str, str]  # (speaker: "host" | "expert", text)

_recent_filler_ids: list[int] = []


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


async def polish_audio_mp3(mp3_bytes: bytes, speaker: str = "host") -> bytes:
    """Add speaker-distinct pitch/EQ timbre, soft fades, breath pad, and loudness norm."""
    ffmpeg = _find_ffmpeg()
    if not ffmpeg or not mp3_bytes:
        return mp3_bytes

    if speaker == "expert":
        # Brighter, higher-energy timbre (+4.5% pitch + presence boost @ 2.8kHz)
        timbre = (
            "aresample=44100,"
            "asetrate=44100*1.045,"
            "aresample=44100,"
            "atempo=0.957,"
            "equalizer=f=2800:t=o:w=1.5:g=3.0,"
        )
    else:
        # Warmer, grounded studio-host timbre (-4.5% pitch + low-mid warmth @ 220Hz)
        timbre = (
            "aresample=44100,"
            "asetrate=44100*0.955,"
            "aresample=44100,"
            "atempo=1.047,"
            "equalizer=f=220:t=o:w=1.5:g=2.0,"
        )

    af_chain = (
        f"{timbre}"
        "apad=pad_dur=0.35,"
        "afade=t=in:st=0:d=0.04,"
        "areverse,afade=t=in:st=0:d=0.18,areverse,"
        "loudnorm=I=-16:TP=-1.5:LRA=11"
    )
    proc = await asyncio.create_subprocess_exec(
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "mp3",
        "-i",
        "pipe:0",
        "-af",
        af_chain,
        "-c:a",
        "libmp3lame",
        "-q:a",
        "3",
        "-f",
        "mp3",
        "pipe:1",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate(input=mp3_bytes)
    if proc.returncode == 0 and stdout:
        return stdout
    return mp3_bytes


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

    if wicket_fell or last_ball == "W":
        host_lines = [
            f"आउट! बड़ा झटका! {bowler} ने शानदार गेंद पर विकेट चटकाया। {team} {curr.runs} पर {curr.wickets}।",
            f"और ये विकेट गिरता हुआ! {bowler} की सटीक गेंद ने कमाल कर दिया। स्कोर {curr.runs} पर {curr.wickets}।",
        ]
        expert_lines = [
            f"अरे भाई! यही तो खूबसूरती है इस खेल की! {bowler} ने जाल बिछाया और बल्लेबाज़ सीधा फंस गए!",
            f"क्या गेंद थी यार! एकदम सटीक लाइन और लेंथ... ड्रेसिंग रूम में इस वक्त सन्नाटा छा गया होगा!",
        ]
        return [("host", random.choice(host_lines)), ("expert", random.choice(expert_lines))]

    if last_ball == "6" or score_diff >= 6:
        host_lines = [
            f"छक्का! {striker} का ज़ोरदार प्रहार, गेंद सीधा दर्शकों के बीच! {team} {curr.runs} पर {curr.wickets}।",
            f"गगनचुंबी छक्का! {striker} ने {bowler} की गेंद को मैदान के बाहर पहुंचा दिया!",
        ]
        expert_lines = [
            f"ओहोहो! आवाज़ सुनी बल्ले की? प्योर टाइमिंग भाई, स्टैंड्स में बैठे दर्शक भी खड़े हो गए!",
            f"क्या बात है! बॉलर सोच ही रहे थे कि कहाँ डालूँ, और {striker} ने गेंद को हवाई यात्रा पर भेज दिया!",
        ]
        return [("host", random.choice(host_lines)), ("expert", random.choice(expert_lines))]

    if last_ball == "4" or score_diff == 4:
        host_lines = [
            f"शानदार चौका! {striker} ने बेहतरीन गैप निकाला। स्कोर अब {curr.runs} पर {curr.wickets}।",
            f"चार रन! {striker} के बल्ले से क्लासिक शॉट, फील्डर के पास कोई मौका नहीं।",
        ]
        expert_lines = [
            f"वाह! इसे कहते हैं नज़ाकत! ताकत कम और टाइमिंग ज़्यादा — लाजवाब शॉट {striker}!",
            f"बिलकुल टेक्स्टबुक शॉट था ये! जब बल्लेबाज़ लय में हो, तो ऐसी बाउंड्री अपने आप आती है!",
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
        ]
        return [("host", random.choice(host_lines))]

    if overs_changed:
        dot_lines = [
            f"{bowler} की कसी हुई गेंद, कोई रन नहीं। {team} {curr.runs} पर {curr.wickets}।",
            f"अच्छा डिफेंस {striker} का, {bowler} दबाव बनाए हुए हैं।",
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

    available = [i for i in range(len(pool)) if i not in _recent_filler_ids]
    if not available:
        _recent_filler_ids.clear()
        available = list(range(len(pool)))

    chosen = random.choice(available)
    _recent_filler_ids.append(chosen)
    if len(_recent_filler_ids) > 6:
        _recent_filler_ids.pop(0)

    return pool[chosen]


async def synthesize_fish_audio(text: str, speaker: str = "host") -> bytes | None:
    """Synthesize speech using Fish Audio TTS API and polish with FFmpeg fades/loudness."""
    api_key = os.getenv("FISH_API_KEY", "").strip()
    if not api_key or not text.strip():
        return None

    payload: dict[str, object] = {
        "text": text,
        "format": "mp3",
    }

    if speaker == "expert":
        reference_id = os.getenv("FISH_EXPERT_REFERENCE_ID", "").strip() or os.getenv("FISH_REFERENCE_ID", "").strip()
        payload["prosody"] = {"speed": 1.07}
    else:
        reference_id = os.getenv("FISH_REFERENCE_ID", "").strip()
        payload["prosody"] = {"speed": 1.03}

    if reference_id:
        payload["reference_id"] = reference_id

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "model": os.getenv("FISH_MODEL", "s2.1-pro-free"),
    }

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(FISH_TTS_URL, json=payload, headers=headers)
            resp.raise_for_status()
            return await polish_audio_mp3(resp.content, speaker=speaker)
    except Exception as exc:
        print(f"[fish-audio:{speaker}] TTS error: {exc}")
        return None
