"""Broadcast-grade, phase-aware Hindi Commentary Director with anti-repetition memory."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass

from .db import get_all_stories, get_news_items, pick_next_story
from .llm_director import generate_llm_segment, is_llm_configured
from .models import ScoreboardState

# Turn tuple: (speaker: "host" | "expert", text: str, tag: str)
DirectedTurn = tuple[str, str, str]


class NoRepeatDeck:
    """Shuffled non-repeating deck across namespaces so lines never repeat back-to-back."""

    def __init__(self) -> None:
        self._pools: dict[str, list[int]] = {}
        self._last: dict[str, int] = {}

    def pick(self, namespace: str, items: list) -> object:
        if not items:
            return None
        if len(items) == 1:
            return items[0]
        deck = self._pools.get(namespace)
        if not deck or any(i >= len(items) for i in deck):
            deck = list(range(len(items)))
            random.shuffle(deck)
            last_idx = self._last.get(namespace)
            if last_idx is not None and deck[0] == last_idx and len(deck) > 1:
                deck[0], deck[-1] = deck[-1], deck[0]
            self._pools[namespace] = deck
        idx = deck.pop(0)
        self._last[namespace] = idx
        return items[idx]


@dataclass
class MatchContext:
    overs_float: float
    phase: str  # "powerplay" | "middle" | "death"
    is_chase: bool
    runs_needed: int
    balls_remaining: int
    chase_pressure: str  # "none" | "comfortable" | "tight" | "crunch"
    over_completed: bool
    striker_near_50: bool
    striker_near_100: bool


def _parse_overs(ov: str) -> float:
    try:
        parts = str(ov or "0.0").split(".")
        completed = int(parts[0] or 0)
        balls = int(parts[1] or 0) if len(parts) > 1 else 0
        return completed + min(balls, 6) / 6.0
    except Exception:
        return 0.0


def analyze_context(prev: ScoreboardState | None, curr: ScoreboardState) -> MatchContext:
    ov_f = _parse_overs(curr.overs)
    max_ov = 20 if (curr.target <= 260 and ov_f <= 20.5) else 50
    if ov_f < 6.0:
        phase = "powerplay"
    elif (max_ov == 20 and ov_f < 15.0) or (max_ov == 50 and ov_f < 38.0):
        phase = "middle"
    else:
        phase = "death"

    is_chase = bool(curr.target and curr.target > 0)
    runs_needed = max(0, (curr.target or 0) - curr.runs) if is_chase else 0
    total_balls = max_ov * 6
    bowled_balls = int(ov_f) * 6 + round((ov_f - int(ov_f)) * 6)
    balls_rem = max(0, total_balls - bowled_balls)

    pressure = "none"
    if is_chase:
        if curr.rrr >= curr.crr + 2.5 or (balls_rem <= 24 and runs_needed > balls_rem):
            pressure = "crunch"
        elif curr.rrr > curr.crr + 0.5:
            pressure = "tight"
        else:
            pressure = "comfortable"

    over_completed = False
    if prev is not None and prev.overs != curr.overs:
        over_completed = str(curr.overs).endswith(".0") or (
            curr.prev_over.over_number > prev.prev_over.over_number
        )

    sr = curr.striker.runs
    return MatchContext(
        overs_float=ov_f,
        phase=phase,
        is_chase=is_chase,
        runs_needed=runs_needed,
        balls_remaining=balls_rem,
        chase_pressure=pressure,
        over_completed=over_completed,
        striker_near_50=42 <= sr < 50,
        striker_near_100=90 <= sr < 100,
    )


def extract_crex_ball(raw: str) -> tuple[str, str]:
    """Return (ball_id e.g. '12.4', clean Hindi description)."""
    txt = (raw or "").strip()
    m = re.match(r"^(\d+\.\d+)\s+(.+)$", txt)
    if not m:
        return ("", txt[:260])
    ball_id = m.group(1)
    body = m.group(2).strip()
    # Strip trailing duplicate/noise tags if any
    body = re.sub(r"\s+(?:OUT|4s/6s|Wkt\s*#\d+).*$", "", body).strip()
    return (ball_id, body[:260])


# ---------------------------------------------------------------------------
# Rules, Science & Craft Library (Multi-sentence Expert deep-dives)
# ---------------------------------------------------------------------------
RULES_AND_CRAFT_LIBRARY: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "impact_player_tactics",
        [
            ("host", "टी20 लीग्स में इम्पैक्ट प्लेयर नियम ने टीमों की बल्लेबाज़ी गहराई को पूरी तरह बदल दिया है। पहले जहाँ छठे विकेट के बाद टीम संभलकर खेलती थी, अब नंबर आठ तक बड़े हिटर दिखते हैं।"),
            ("expert", "बिल्कुल सही कहा! इसका सीधा असर गेंदबाज़ों की रणनीति पर पड़ा है। पहले कप्तान सोचते थे कि दो विकेट लेकर मिडल ऑर्डर पर दबाव बना देंगे, लेकिन अब इम्पैक्ट सब आने से पार स्कोर ही पंद्रह से बीस रन ऊपर खिसक गया है। ऐसे में गेंदबाज़ों के पास डिफेंस करने की जगह हर ओवर में विकेट लेने की तलाश ही सबसे बड़ा हथियार बचती है।"),
        ],
    ),
    (
        "dew_and_magnus_physics",
        [
            ("host", "शाम के मैचों में जैसे-जैसे फ्लडलाइट्स चमकती हैं, मैदान पर ओस यानी ड्यू की चर्चा हर ड्रेसिंग रूम में शुरू हो जाती है।"),
            ("expert", "देखो इसके पीछे सीधा सा साइंस है। जब आउटफील्ड पर ओस जमती है, तो गेंद की सिलाई यानी सीम पर हल्की नमी आ जाती है। इससे स्पिनरों की उंगलियों की ग्रिप फिसलती है और तेज़ गेंदबाज़ों का यॉर्कर थोड़ा स्किड होकर सीधे बल्ले के बीच में आता है! इसलिए दूसरी पारी में बल्लेबाज़ी ज़्यादातर आसान हो जाती है।"),
            ("host", "यानी गेंदबाज़ बार-बार तौलिए से गेंद सुखाते नज़र आते हैं, लेकिन बल्लेबाज़ के चेहरे पर मुस्कान आ जाती है!"),
        ],
    ),
    (
        "cutter_vs_yorker_death",
        [
            ("host", "डेथ ओवर्स में आजकल रफ्तार से ज़्यादा वेरिएशन देखने को मिलती है — कोई वाइड यॉर्कर डाल रहा है तो कोई ऑफ-कटर।"),
            ("expert", "सही बात है। आज के बैटर बैट स्पीड से एक सौ चालीस की सीधी गेंद को आसानी से स्टैंड्स में भेज देते हैं। इसलिए स्मार्ट बॉलर सीम को हल्का तिरछा पकड़कर उंगलियां गेंद के साइड में चलाता है — जिसे हम कटर कहते हैं। पिच पर टप्पा खाने के बाद गेंद थोड़ा रुककर आती है और बल्लेबाज़ शॉट पहले पूरा कर बैठता है, नतीजा हवा में ऊँचा कैच!"),
        ],
    ),
    (
        "powerplay_vs_middle_field",
        [
            ("host", "पावरप्ले के बाद जब पांच फील्डर बाहर जाते हैं, तो गेम की पूरी चाल एकदम से बदल जाती है।"),
            ("expert", "जी हाँ! शुरुआती छह ओवरों में तीस गज के दायरे में नौ खिलाड़ी होने की वजह से बल्लेबाज़ ऊपर से मारने का रिस्क लेता है। लेकिन सातवें ओवर से बाउंड्री पर पांच फील्डर फैलते ही चौका निकालना कठिन हो जाता है, और पूरा खेल स्ट्राइक रोटेट करने तथा बड़े पॉकेट्स ढूंढने पर आ जाता है। यहीं पर डॉट बॉल्स का प्रेशर विकेट दिलाता है।"),
            ("host", "बिल्कुल, और जो जोड़ी बीच के ओवरों में बिना रिस्क लिए आठ के करीब रनरेट चला ले, वो मैच आधी जीत वहीं तय कर देती है।"),
        ],
    ),
    (
        "boundary_relay_catches",
        [
            ("host", "क्रिकेट में पहले जो शॉट बिना सोचे छह रन माने जाते थे, आजकल बाउंड्री रोप पर फील्डर उन्हें भी कैच में बदल रहे हैं।"),
            ("expert", "रिले कैचिंग ने खेल का स्तर ही बदल दिया है! नियम साफ कहता है कि हवा में उछलकर गेंद पकड़ते समय खिलाड़ी का पहला संपर्क बाउंड्री के अंदर से होना चाहिए और रोप को छूने से पहले गेंद हाथ से छूट जानी चाहिए। खिलाड़ियों की एथलेटिक फिटनेस और आपसी तालमेल ने आज बल्लेबाज़ों की सांसें अटका रखी हैं।"),
        ],
    ),
    (
        "anchor_vs_intent_paradox",
        [
            ("host", "टी20 क्रिकेट में हमेशा एक बहस चलती है — क्या टीम को एक एंकर बल्लेबाज़ चाहिए जो सोलहवें ओवर तक टिके, या सभी को पहले बॉल से ही अटैक करना चाहिए?"),
            ("expert", "इसका जवाब पिच तय करती है भाई! अगर स्कोर दो सौ दस का बन रहा हो, तो धीमी पारी टीम को हरा सकती है। लेकिन जब गेंद रुककर आ रही हो और पावरप्ले में तीन विकेट गिर जाएं, तो एक शांत एंकर दूसरे छोर से पूरी पारी को बांधकर रखता है ताकि बाकी बल्लेबाज़ खुलकर खेल सकें।"),
        ],
    ),
    (
        "bowler_captain_angle",
        [
            ("host", "जब किसी सेट बल्लेबाज़ को रोकना हो, तो गेंदबाज़ के साथ-साथ कप्तान की फील्ड सेटिंग भी आधी गेंदबाज़ी करती है।"),
            ("expert", "बिल्कुल! अगर आप लेग-स्टंप के बाहर फील्डर सजाकर वाइड ऑफ़ यॉर्कर डालोगे, तो बल्लेबाज़ को ताकत अपनी तरफ से पैदा करनी पड़ेगी। कप्तान का काम बस इतना होता है कि वो गेंदबाज़ के प्लान के मुताबिक कम से कम सात फील्डर एक ही तरफ लॉक कर दे — इसे ही असली क्रिकेट की बिसात कहते हैं!"),
        ],
    ),
]


# ---------------------------------------------------------------------------
# Live On-The-Spot Ball Delivery Script
# ---------------------------------------------------------------------------
def build_live_ball_turns(
    prev: ScoreboardState | None,
    curr: ScoreboardState,
    deck: NoRepeatDeck,
    last_spoken_ball_id: str = "",
) -> tuple[list[DirectedTurn], str]:
    """Generate immediate, non-repetitive live ball call + analytical follow-up."""
    if prev is None:
        return ([], last_spoken_ball_id)

    ctx = analyze_context(prev, curr)
    striker = curr.striker.name.title()
    non_striker = curr.non_striker.name.title()
    bowler = curr.bowler.name.title()
    team = _spoken_team(curr.batting_team, "बल्लेबाज़ी टीम")
    score_diff = curr.runs - prev.runs
    wicket_fell = curr.wickets > prev.wickets
    overs_changed = curr.overs != prev.overs
    last_ball = curr.curr_over.balls[-1].upper() if curr.curr_over.balls else ""

    ball_id, crex_hindi = extract_crex_ball(curr.live_commentary)
    fresh_crex = bool(crex_hindi and (not ball_id or ball_id != last_spoken_ball_id))

    # 1. WICKET — Accordion escalation + multi-sentence Expert tactical analysis
    if wicket_fell or (overs_changed and last_ball == "W"):
        if fresh_crex:
            call_line = f"बड़ा झटका! {crex_hindi} स्कोर अब {team} का {curr.runs} पर {curr.wickets}।"
        else:
            call_line = deck.pick(
                "wicket_host",
                [
                    f"आउट! ज़बरदस्त सफलता {bowler} को! {team} ने अपना बड़ा विकेट गंवा दिया है, स्कोर {curr.runs} पर {curr.wickets}।",
                    f"विकेट गिरता हुआ! {bowler} की सटीक लाइन ने बल्लेबाज़ को छका दिया — {team} अब {curr.overs} ओवर में {curr.runs} पर {curr.wickets}।",
                    f"कमाल की गेंद और पवेलियन लौटना होगा! {bowler} ने साझेदारी तोड़ दी है, {team} {curr.runs} पर {curr.wickets}।",
                ],
            )
        expert_line = deck.pick(
            "wicket_expert",
            [
                f"अरे भाई, यही दबाव की जीत है! {bowler} पिछले कुछ गेंदों से लगातार लाइन बदलकर बल्लेबाज़ को फंसाने की कोशिश कर रहे थे, और इस बार सीधा जाल में फंस गए। अब नए बल्लेबाज़ पर तुरंत सेट होने का भारी दबाव रहेगा।",
                f"क्या सटीक लेंथ पकड़ी {bowler} ने! टी20 में जब आप बल्लेबाज़ के आर्क से थोड़ा दूर या रफ्तार बदलकर डालते हैं, तो शॉट कंट्रोल करना नामुमकिन हो जाता है। ड्रेसिंग रूम में इस वक्त हलचल तेज़ होगी।",
                f"यह विकेट पूरे मैच का मोमेंटम मोड़ सकता है! {team} ने {curr.wickets} विकेट गंवा दिए हैं, अब क्रीज़ पर मौजूद जोड़ी को पहले कुछ गेंदें संभलकर खेलनी होंगी ताकि पारी दोबारा पटरी पर आ सके।",
            ],
        )
        turns: list[DirectedTurn] = [
            ("host", call_line, "live_wicket"),
            ("expert", expert_line, "live_wicket_analysis"),
        ]
        if ctx.over_completed:
            turns.append(
                (
                    "host",
                    f"और इसी के साथ ओवर भी समाप्त — {curr.prev_over.over_number} ओवर में आए सिर्फ {curr.prev_over.total} रन।",
                    "over_recap",
                )
            )
        return (turns, ball_id or last_spoken_ball_id)

    # 2. SIX — Crowd escalation + dynamic reaction
    if score_diff >= 6 or (overs_changed and last_ball == "6"):
        if fresh_crex:
            call_line = f"गगनचुंबी छक्का! {crex_hindi} {team} पहुँचा {curr.runs} पर {curr.wickets}!"
        else:
            call_line = deck.pick(
                "six_host",
                [
                    f"छक्का! {striker} का करारा प्रहार और गेंद सीधा दर्शकों के बीच जा गिरी! {team} {curr.runs} पर {curr.wickets}।",
                    f"क्या ज़ोरदार हिट {striker} के बल्ले से! {bowler} की गेंद को मैदान के पार भेज दिया — पूरे छह रन!",
                    f"सीधा स्टैंड्स में! {striker} ने खुलकर हाथ खोले हैं और पूरे स्टेडियम में शोर गूंज उठा है!",
                ],
            )
        expert_line = deck.pick(
            "six_expert",
            [
                f"ओहोहो, बल्ले से आवाज़ सुनी? एकदम बीचों-बीच कनेक्ट हुई गेंद! जब {striker} इतनी जल्दी लेंथ पढ़ लेते हैं, तो गेंदबाज़ के लिए कोई भी बाउंड्री बड़ी नहीं बचती।",
                f"शानदार बैट स्विंग! गेंद थोड़ा स्लॉट में मिली और {striker} ने फ्रंट फुट क्लियर करके सीधा लॉफ्ट कर दिया — यही आधुनिक पावर-हिटिंग की पहचान है।",
                f"इस छक्के ने {bowler} की पूरी लय हिला दी है! अब अगले दो गेंदों पर कप्तान को फील्डिंग बदलने पर मजबूर होना पड़ेगा।",
            ],
        )
        return ([("host", call_line, "live_six"), ("expert", expert_line, "live_six_analysis")], ball_id or last_spoken_ball_id)

    # 3. FOUR — Sharp boundary call + technical praise
    if score_diff == 4 or (overs_changed and last_ball == "4"):
        if fresh_crex:
            call_line = f"कमाल का चौका! {crex_hindi} स्कोर {curr.runs} पर {curr.wickets}।"
        else:
            call_line = deck.pick(
                "four_host",
                [
                    f"चौका! {striker} ने फील्डरों के बीच से शानदार गैप निकाला — चार रन और स्कोर {curr.runs} पर {curr.wickets}।",
                    f"बेहतरीन टाइमिंग! {striker} के बल्ले से क्लासिक शॉट, गेंद गोली की रफ्तार से सीमा रेखा के पार!",
                    f"चार रन {striker} के खाते में! {bowler} की गेंद पर ज़ोर से नहीं बल्कि नज़ाकत से शॉट जड़ा!",
                ],
            )
        expert_line = deck.pick(
            "four_expert",
            [
                f"वाह, इसे कहते हैं शुद्ध टाइमिंग! फील्डर हिल भी नहीं पाए — जब बल्लेबाज़ क्रीज़ पर संतुलन में होता है तो गैप अपने आप खुलते जाते हैं।",
                f"बहुत बढ़िया शॉट चयन! {striker} ने हवा में रिस्क लेने के बजाय ज़मीन के रास्ते चौका बटोरा, और इससे स्कोरबोर्ड को अच्छी गति मिली।",
            ],
        )
        return ([("host", call_line, "live_four"), ("expert", expert_line, "live_four_analysis")], ball_id or last_spoken_ball_id)

    # 4. OVER COMPLETED — Dedicated Over-Break Recap & Tactical Shift
    if ctx.over_completed:
        ov_num = curr.prev_over.over_number
        ov_runs = curr.prev_over.total
        recap_intro = (
            f"{crex_hindi} और इसी के साथ ओवर नंबर {ov_num} पूरा हुआ!"
            if fresh_crex
            else f"ओवर नंबर {ov_num} समाप्त — इस ओवर से आए {ov_runs} रन।"
        )
        chase_note = (
            f" लक्ष्य से अब {ctx.runs_needed} रन दूर है {team}, ज़रूरी रन रेट {curr.rrr:.2f} का है।"
            if ctx.is_chase
            else f" वर्तमान रन रेट {curr.crr:.2f} पर चल रहा है।"
        )
        host_recap = f"{recap_intro} {team} का स्कोर {curr.runs} पर {curr.wickets}।{chase_note}"
        expert_shift = deck.pick(
            "over_break_expert",
            [
                f"देखो {ov_runs} रन का यह ओवर बहुत अहम रहा। {bowler} ने अभी तक {curr.bowler.overs} ओवर में {curr.bowler.wickets} विकेट लेकर जो दबाव बनाया है, अब दूसरे छोर से आने वाले गेंदबाज़ को उसका फायदा उठाना होगा। {striker} और {non_striker} के बीच {curr.partnership} की साझेदारी क्रीज़ पर टिकी हुई है।",
                f"एक दिलचस्प मोड़ पर खड़ा है मुकाबला। पिच अब थोड़ा दोहरी गति दिखा रही है, इसलिए आने वाले ओवर में जो भी तेज़ या स्पिन गेंदबाज़ आएगा, उसे कटर और लेंथ में लगातार बदलाव करना पड़ेगा। वरना {striker} जैसे बल्लेबाज़ आखिरी ओवरों में बहुत खतरनाक साबित होते हैं।",
                f"बिल्कुल संतुलित ओवर रहा। {team} जानती है कि हाथ में अभी {10 - curr.wickets} विकेट बाकी हैं, इसलिए अगले दो ओवरों में कम से कम एक बाउंड्री प्रति ओवर निकालनी ज़रूरी होगी ताकि रन गति नीचे न गिरे।",
            ],
        )
        return ([("host", host_recap, "over_break"), ("expert", expert_shift, "over_break_tactics")], ball_id or last_spoken_ball_id)

    # 5. ROUTINE BALL / CREX LIVE DESCRIPTION (Concise natural call, alternating speaker subtly)
    if fresh_crex:
        # Let Host call most deliveries, occasionally let Expert chime in on quiet dots/singles
        speaker = "host" if score_diff > 0 or random.random() < 0.72 else "expert"
        return ([(speaker, crex_hindi, "live_crex_ball")], ball_id or last_spoken_ball_id)

    if score_diff > 0:
        line = deck.pick(
            "single_host",
            [
                f"{striker} ने हल्के हाथों से धकेलकर {score_diff} रन दौड़ लिए, स्कोर {curr.runs} पर {curr.wickets}।",
                f"अच्छी रनिंग बिटवीन द विकेट्स — {score_diff} रन के साथ {team} {curr.overs} ओवर में {curr.runs} पर {curr.wickets}।",
                f"गैप में खेलकर तेज़ी से स्ट्राइक रोटेट किया {striker} ने, {score_diff} रन और जुड़े खाते में।",
                f"समझदारी भरी बल्लेबाज़ी, बिना कोई बड़ा रिस्क लिए {score_diff} रन चुरा लिए हैं।",
            ],
        )
        return ([("host", line, "live_run")], last_spoken_ball_id)

    if overs_changed:
        line = deck.pick(
            "dot_call",
            [
                f"{bowler} की कसी हुई गेंद, कोई रन नहीं। {team} {curr.runs} पर {curr.wickets}।",
                f"सीधा फील्डर के हाथ में शॉट, {striker} रन नहीं निकाल पाए।",
                f"बेहतरीन नियंत्रण {bowler} का, डॉट बॉल के साथ दबाव बढ़ाते हुए।",
                f"ऑफ स्टंप के पास सटीक गेंद, {striker} ने सम्मान देकर रोक दिया।",
            ],
        )
        return ([("host", line, "live_dot")], last_spoken_ball_id)

    return ([], last_spoken_ball_id)


# ---------------------------------------------------------------------------
# Continuous Between-Ball Conversational Segment Generator
# ---------------------------------------------------------------------------
def curr_wkts(state: ScoreboardState) -> int:
    return min(10, max(0, int(state.wickets or 0)))


SLIDE_SPOTLIGHT_SHOWCASE: list[tuple[str, str, str]] = [
    ("/report.html", "match_report", "Post-Match Report Banner, Both Innings Comparison, Player of the Match & Turning Points"),
    ("/story.html", "crex_news", "Studio Match Talks, Cricket Stories, News Headlines & Live Caption Board"),
    ("/audience.html", "form_h2h_poll", "Audience Zone: Fan Poll Verdict (Votes Split), Trivia Quiz & Viewer Debate Question"),
    ("/match.html", "match_summary", "Match Overview, Win Probability & Result Banner"),
    ("/leaders.html", "matchup", "Top Match Performers Leaderboard (Leading Batters & Bowlers)"),
    ("/player.html", "matchup", "Player Spotlight Card (Star Batter & Key Bowler)"),
    ("/batting.html", "matchup", "Full Batting Scorecard (Runs, Balls, 4s, 6s, Strike Rates, Dismissals)"),
    ("/bowling.html", "over_break_tactics", "Full Bowling Figures (Overs, Maidens, Runs, Wickets, Economy)"),
    ("/overs.html", "overs_fow", "Over-by-Over Ball Progression & Fall of Wickets"),
    ("/partnership.html", "situation", "Batting Partnerships & Wicket Timeline"),
    ("/milestone.html", "milestone", "50 / 100 / 150 / 200 Milestone Watch & Top Scorers"),
    ("/runrate.html", "runrate", "Boundaries Analytics (4s vs 6s Runs & Scoring Rate)"),
    ("/projected.html", "situation", "Projected Score Run-Rate Matrix & Live Fan Poll"),
    ("/pitch.html", "pitch_weather", "Pitch Report, Weather Conditions, Pace vs Spin Split & Toss"),
    ("/form.html", "form_h2h_poll", "Last-5 Match Form Streaks, Comparison & Recent H2H Results"),
    ("/points.html", "points_series", "Tournament Points Table (Standings, NRR, Pts) & Series Key Stats"),
    ("/rankings.html", "icc_rankings", "ICC Men's ODI & T20I Team Rankings & Top Ranked Players"),
    ("/versus.html", "form_h2h_poll", "Team vs Team Showdown Graphic & Head-to-Head"),
    ("/info.html", "crex_news", "Match Venue, Series Info, Weather & Latest Cricket News"),
    ("/break.html", "db_story", "Studio Break Screen & Dressing Room Cricket Stories"),
    ("/news.html", "crex_news", "Live Cricket Newsroom & Breaking Headlines Discussion"),
    ("/other_matches.html", "points_series", "Around The Grounds: Other Tournament Matches & Standings"),
    ("/stories_hub.html", "db_story", "Dressing Room Chronicles & Bite-Sized Cricket Stories"),
    ("/experience.html", "rules_craft", "Expert Dugout: Captain's Field Radar & Tactical Match Craft"),
    ("/stats_deep.html", "situation", "Deep Stats Lab: Phase-by-Phase Scoring & Pace vs Spin Analytics"),
]

PREMATCH_SLIDE_SHOWCASE: list[tuple[str, str, str]] = [
    ("/prematch.html", "form_h2h_poll", "Pre-Match Show Hub, Match Countdown, Form & Talking Points"),
    ("/toss.html", "pitch_weather", "Toss Center: Coin Toss Status, Venue Toss Bias & Captains at the Middle"),
    ("/key_battles.html", "matchup", "Key Player Battles: Sooryavanshi vs Samarakoon, Tilak vs Viyaskanth, Rinku vs Sahan"),
    ("/road_to_semi.html", "points_series", "Road to the Semi-Final: IND-A Firepower vs Unbeaten SL-A Group A Toppers"),
    ("/players_to_watch.html", "matchup", "Players to Watch: X-Factor Spotlight Across Both Semi-Final Squads"),
    ("/predictions.html", "form_h2h_poll", "Match Predictions: Win Probability, Live Fan Poll & Matchday Broadcast Schedule"),
    ("/comparison.html", "form_h2h_poll", "Team Radar: Win%, Avg Score, Highest Total & Key Players to Watch"),
    ("/pitch.html", "pitch_weather", "Doha Pitch Report, Weather Conditions & 50/50 Pace vs Spin Split"),
    ("/playing11.html", "matchup", "Official Squads & Probable Playing XI Lineups"),
    ("/form.html", "form_h2h_poll", "Last-5 Match Form Streaks & Head-to-Head Rivalry"),
    ("/points.html", "points_series", "Asia Cup Rising Stars 2026 Points Table & Net Run Rate"),
    ("/news.html", "crex_news", "Live Cricket Newsroom & Breaking Tournament Headlines"),
    ("/other_matches.html", "points_series", "Around The Grounds: Recent Tournament Results & Standings"),
    ("/stories_hub.html", "db_story", "Dressing Room Small Stories & Iconic Cricket Moments"),
    ("/experience.html", "rules_craft", "Expert Dugout: Knockout Field Radar & Tactical Craft"),
    ("/stats_deep.html", "pitch_weather", "Deep Stats Lab: Phase Run Rates & Venue Scoring Averages"),
    ("/audience.html", "form_h2h_poll", "Audience Zone: Live Fan Poll & Debate"),
    ("/versus.html", "form_h2h_poll", "Matchday Showdown Poster: IND-A vs SL-A"),
]


def _has_toss_result(toss_text: str) -> bool:
    t = (toss_text or "").upper()
    return any(k in t for k in ("WON THE TOSS", "CHOSE", "ELECTED", "OPTED"))


def pick_spotlight_slide(tag: str, state: ScoreboardState, deck: NoRepeatDeck) -> str:
    """Locked to Scoreboard (/) — no automatic slide switching away from Scorecard."""
    return "/"


def _choose_phase_topic(state: ScoreboardState, deck: NoRepeatDeck) -> str:
    ctx = analyze_context(None, state)
    topics = ["situation", "matchup", "pitch_weather", "points_series", "form_h2h_poll", "crex_news", "db_story", "rules_craft", "crex_news", "db_story"]
    if ctx.chase_pressure == "crunch" or ctx.phase == "death":
        weighted = ["situation", "matchup", "pitch_weather", "crex_news", "points_series", "rules_craft", "db_story"]
    elif ctx.phase == "powerplay":
        weighted = ["matchup", "pitch_weather", "form_h2h_poll", "crex_news", "rules_craft", "db_story"]
    else:
        weighted = topics
    return str(deck.pick("segment_topic", weighted))


async def build_next_segment_async(
    state: ScoreboardState,
    deck: NoRepeatDeck,
    recent_lines: list[str] | None = None,
) -> tuple[list[DirectedTurn], str]:
    """Generate next segment + matching spotlight slide URL using Nemotron Ultra when configured."""
    is_prematch = state.match_status == "prematch"
    is_break_or_done = state.match_status in ("innings_break", "completed")
    slide_meta: dict[str, str] | None = None

    if is_prematch:
        topic = _choose_phase_topic(state, deck)
        spotlight_url = "/"
        slide_meta = {"url": "/", "description": "Live Scoreboard & Scorecard"}
    elif is_break_or_done:
        topic = _choose_phase_topic(state, deck)
        spotlight_url = "/"
        slide_meta = {"url": "/", "description": "Live Scoreboard & Scorecard"}
    else:
        topic = _choose_phase_topic(state, deck)
        spotlight_url = "/"
        slide_meta = {"url": "/", "description": "Live Scoreboard & Scorecard"}

    if is_llm_configured():
        news_item = None
        story_item = None
        if topic in ("crex_news",) or (is_break_or_done and topic == "info"):
            news_list = get_news_items(limit=20)
            if news_list:
                news_item = deck.pick("crex_news", news_list)
        elif topic == "db_story":
            all_st = get_all_stories()
            series_low = (state.series_name or "").lower()
            stories = [
                s for s in all_st
                if (s.get("match_context") or "general") == "general"
                or ((s.get("match_context") or "").lower() in series_low)
            ] or [s for s in all_st if (s.get("match_context") or "general") == "general"]
            if stories:
                story_item = deck.pick("db_story", stories)

        llm_turns = await generate_llm_segment(
            state=state,
            topic_hint=topic,
            recent_lines=recent_lines or [],
            news_cursor_item=news_item,
            story_item=story_item,
            slide_on_screen=slide_meta,
            timeout_sec=40.0 if (is_break_or_done or is_prematch) else 25.0,
        )
        if llm_turns:
            return (llm_turns, spotlight_url)

    # Deterministic fallback mapped to core 8 topics
    fallback_topic = {
        "match_report": "matchup",
        "match_summary": "situation",
        "overs_fow": "situation",
        "milestone": "matchup",
        "runrate": "situation",
        "icc_rankings": "points_series",
        "over_break_tactics": "matchup",
    }.get(topic, topic)
    turns = build_next_segment(state, deck, forced_topic=fallback_topic)
    return (turns, spotlight_url)


_HINDI_TEAM_NAMES: dict[str, str] = {
    "IND-A": "इंडिया ए",
    "SL-A": "श्रीलंका ए",
    "IND": "इंडिया",
    "SL": "श्रीलंका",
    "BAN-A": "बांग्लादेश ए",
    "PAK-A": "पाकिस्तान ए",
    "AFG-A": "अफ़ग़ानिस्तान ए",
}


def _spoken_team(code: str, default: str = "टीम") -> str:
    key = (code or "").strip().upper()
    return _HINDI_TEAM_NAMES.get(key, code or default)


def _spoken_form(items: list[str] | None) -> str:
    mapping = {"W": "जीत", "L": "हार", "T": "टाई", "NR": "बेनतीजा", "D": "ड्रॉ"}
    return ", ".join(mapping.get(str(x).strip().upper(), str(x)) for x in (items or []))


def build_next_segment(
    state: ScoreboardState, deck: NoRepeatDeck, forced_topic: str | None = None
) -> list[DirectedTurn]:
    """Generate a cohesive, natural 2-to-4-turn conversation segment with varied turn lengths."""
    ctx = analyze_context(None, state)
    team = _spoken_team(state.batting_team, "टीम")
    bowl_team = _spoken_team(state.bowling_team, "गेंदबाज़ी टीम")
    striker = state.striker.name.title()
    non_striker = state.non_striker.name.title()
    bowler = state.bowler.name.title()
    venue = state.venue or "स्टेडियम"

    topic = forced_topic or _choose_phase_topic(state, deck)

    # 1. MATCH SITUATION & MILESTONE / CHASE WATCH (3 non-repeating angles)
    if topic == "situation":
        if ctx.striker_near_50:
            return [
                ("host", f"नज़रें इस वक्त {striker} पर टिकी हैं जो {state.striker.runs} रन बनाकर अपने अर्धशतक से सिर्फ {50 - state.striker.runs} रन दूर खड़े हैं।", "seg_situation"),
                ("expert", f"सही कहा! जब बल्लेबाज़ चालीस के पार पहुँचता है, तो दो चीज़ें काम आती हैं — एक तो रिस्क न लेना, और दूसरा गैप्स में सिंगल निकालकर मील के पत्थर तक शांत मन से पहुँचना। {striker} ने अभी तक {state.striker.fours} चौके और {state.striker.sixes} छक्के लगाए हैं, जो बताता है कि गेंद बल्ले पर बढ़िया आ रही है।", "seg_situation"),
                ("host", f"और टीम को भी उनकी इस पारी की सख्त ज़रूरत है क्योंकि {team} अभी {state.overs} ओवर में {state.runs} पर {state.wickets} है।", "seg_situation"),
            ]
        angle = deck.pick("situation_angle", ["chase_math", "wicket_depth", "projected_window"])
        if ctx.is_chase and angle == "chase_math":
            return [
                ("host", f"समीकरण पर नज़र डालें तो {team} को अभी जीत के लिए {ctx.balls_remaining} गेंदों में {ctx.runs_needed} रन की ज़रूरत है।", "seg_situation"),
                ("expert", f"देखो वर्तमान रन रेट {state.crr:.2f} है जबकि रिक्वायर्ड रन रेट {state.rrr:.2f} तक पहुँच चुका है। ऐसे चेज़ में सबसे ज़रूरी होता है कि पार्टनरशिप टूटे नहीं और हर ओवर में कम से कम एक बाउंड्री आती रहे। अभी {striker} और {non_striker} के बीच {state.partnership} की साझेदारी चल रही है — अगर यह जोड़ी चार ओवर और टिक गई तो मुकाबला पूरा पलट सकता है।", "seg_situation"),
                ("host", f"बिल्कुल, वहीं {bowl_team} चाहेगी कि किसी तरह एक और विकेट चटकाकर नए बल्लेबाज़ों को क्रीज़ पर लाया जाए।", "seg_situation"),
            ]
        if angle == "wicket_depth":
            return [
                ("expert", f"क्रिकेट के स्कोरकार्ड में अभी {team} का स्कोर {state.runs} पर {state.wickets} दिख रहा है। हाथ में अभी {10 - curr_wkts(state)} विकेट बाकी हैं, जिसका सीधा मतलब है कि बल्लेबाज़ अगले तीन ओवर में गियर बदल सकते हैं।", "seg_situation"),
                ("host", f"बिल्कुल! खासकर {striker} और {non_striker} की {state.partnership} वाली साझेदारी इस पूरी पारी की रीढ़ बन चुकी है।", "seg_situation"),
            ]
        rem_ov = max(0.0, (20.0 if ctx.overs_float <= 20.5 else 50.0) - ctx.overs_float)
        proj_curr = round(state.runs + rem_ov * state.crr)
        proj_plus = round(state.runs + rem_ov * (state.crr + 1.5))
        return [
            ("host", f"प्रोजेक्टेड स्कोर मैट्रिक्स देखें तो अगर {team} इसी {state.crr:.2f} के रन रेट से चलती रही, तो स्कोर करीब {proj_curr} तक जाएगा, लेकिन डेढ़ रन रेट बढ़ने पर {proj_plus} भी मुमकिन है।", "seg_situation"),
            ("expert", f"और यही पंद्रह से बीस रन का अंतर आखिरी ओवर में जीत और हार के बीच की रेखा बन जाता है। इसलिए {bowl_team} इस समय डॉट बॉल प्रतिशत बढ़ाने पर पूरा जोर लगा रही है।", "seg_situation"),
        ]

    # 2. BATTER vs BOWLER MATCHUP & LEADERS (3 non-repeating angles)
    if topic == "matchup":
        angle = deck.pick("matchup_angle", ["crex_duel", "innings_leaders", "boundary_ratio"])
        if angle == "innings_leaders":
            top_bat = max(state.batters_list, key=lambda b: b.runs, default=None)
            top_bowl = max(state.bowlers_list, key=lambda bw: (bw.wickets, -bw.runs_conceded), default=None)
            t_bat = f"{top_bat.name.title()} ({top_bat.runs} रन)" if top_bat else striker
            t_bowl = f"{top_bowl.name.title()} ({top_bowl.wickets} विकेट)" if top_bowl else bowler
            return [
                ("host", f"आज के स्कोरकार्ड के टॉप परफ़ॉर्मर्स देखें तो बल्लेबाज़ी में {t_bat} और गेंदबाज़ी में {t_bowl} ने सबसे गहरी छाप छोड़ी है।", "seg_matchup"),
                ("expert", "जब दो खिलाड़ी पूरे दिन के सर्वश्रेष्ठ फॉर्म में हों और मैच के अहम चरण में सामने आते हैं, तो पूरा मैच उन्हीं के इर्द-गिर्द घूमने लगता है। बाकी साथियों का काम बस स्ट्राइक रोटेट कर उन्हें ज़्यादा से ज़्यादा गेंदें देना होता है।", "seg_matchup"),
            ]
        if angle == "boundary_ratio":
            bnd_runs = state.striker.fours * 4 + state.striker.sixes * 6
            return [
                ("expert", f"{striker} की पारी का विश्लेषण करें तो उनके {state.striker.runs} रनों में से {bnd_runs} रन सिर्फ चौकों और छक्कों से आए हैं। यानी बाउंड्री के साथ-साथ वे सिंगल और डबल भी लगातार निकाल रहे हैं, जो किसी भी गेंदबाज़ की लाइन बिगाड़ने के लिए काफी होता है।", "seg_matchup"),
                ("host", f"दूसरे छोर पर {non_striker} भी {state.non_striker.runs} रन बनाकर बढ़िया साथ निभा रहे हैं।", "seg_matchup"),
            ]
        return [
            ("host", f"क्रीज़ पर इस समय बेहद दिलचस्प टक्कर चल रही है — {striker} ({state.striker.runs} रन, स्ट्राइक रेट {state.striker.strike_rate:.1f}) के सामने गेंदबाज़ी पर {bowler}।", "seg_matchup"),
            ("expert", f"{bowler} ने {state.bowler.overs} ओवर में {state.bowler.runs_conceded} रन देकर {state.bowler.wickets} विकेट निकाले हैं, इकॉनमी सिर्फ {state.bowler.economy:.2f} की रही है। यही छोटा-सा द्वंद्व तय करेगा कि अगले तीन ओवरों में किसका पलड़ा भारी रहता है।", "seg_matchup"),
        ]

    # 3. CREX PITCH, WEATHER & PACE vs SPIN (3 non-repeating angles)
    if topic == "pitch_weather":
        vs = state.venue_stats or {}
        w = state.weather or {}
        angle = deck.pick("pitch_angle", ["pace_spin", "weather_dew", "venue_par"])
        if angle == "weather_dew":
            raw_temp = str(w.get("temp") or "").strip()
            safe_temp = "25°C" if not raw_temp or raw_temp.startswith("0") else raw_temp
            return [
                ("host", f"{venue} में मौसम बिल्कुल साफ है — तापमान {safe_temp} और ह्यूमिडिटी {w.get('humidity', '68%')} के करीब दर्ज की गई है।", "seg_pitch"),
                ("expert", "नमी जब सत्तर प्रतिशत के आसपास पहुँचती है, तो रात के मुकाबले में ओस पड़ने की संभावना बढ़ जाती है। इससे स्विंग धीरे-धीरे कम होती है और गेंद बैट पर थोड़ा फिसलकर आती है, जिसका सीधा फायदा दूसरी पारी के बल्लेबाज़ों को मिलता है।", "seg_pitch"),
            ]
        if angle == "venue_par":
            return [
                ("host", f"{venue} के ऐतिहासिक आंकड़ों में पहली पारी का औसत स्कोर {vs.get('avg_1st', 165)} और दूसरी पारी का औसत {vs.get('avg_2nd', 150)} रहा है।", "seg_pitch"),
                ("expert", f"यहाँ अब तक खेले गए {vs.get('matches', 45)} मुकाबलों में हाईएस्ट चेज़ {vs.get('highest_chased', '193/5')} रहा है। यानी बड़े लक्ष्य का पीछा करना मुश्किल ज़रूर है, पर नामुमकिन नहीं — बशर्ते पावरप्ले के बाद विकेट बचाकर रखे जाएं।", "seg_pitch"),
            ]
        return [
            ("expert", f"इस मैदान पर पिछले दस मैचों का बॉलिंग ब्रेकडाउन देखें तो तेज़ गेंदबाज़ों ने {vs.get('pace_wkts', 84)} विकेट यानी {vs.get('pace_pct', 59)} प्रतिशत शिकार किए हैं, जबकि स्पिनरों को {vs.get('spin_wkts', 58)} विकेट ({vs.get('spin_pct', 41)} प्रतिशत) मिले हैं।", "seg_pitch"),
            ("host", f"और टॉस भी बड़ा रोल निभाता है क्योंकि यहाँ पहले गेंदबाज़ी करने वाली टीम {vs.get('win_bowl_first', 52)} प्रतिशत मैच जीत चुकी है।", "seg_pitch"),
        ]

    # 4. CREX POINTS TABLE, SERIES LEADERS & ICC RANKINGS (3 non-repeating angles)
    if topic == "points_series":
        pt = state.points_table or []
        sl = state.series_leaders or []
        rk = state.icc_rankings or {}
        angle = deck.pick("points_angle", ["standings", "series_caps", "icc_ladder"])
        if angle == "icc_ladder":
            odi_top = ", ".join(f"#{x.get('rank')} {x.get('team')} ({x.get('rating')})" for x in rk.get("odi_teams", [])[:3])
            t20_top = ", ".join(f"#{x.get('rank')} {x.get('team')} ({x.get('rating')})" for x in rk.get("t20_teams", [])[:3])
            return [
                ("host", f"अंतरराष्ट्रीय क्रिकेट की आईसीसी रैंकिंग पर नज़र डालें तो वनडे में {odi_top or 'IND शीर्ष पर'} और टी20 में {t20_top or 'ENG और IND'} के बीच जबरदस्त होड़ चल रही है।", "seg_points"),
                ("expert", "दिलचस्प बात यह है कि अब फ्रेंचाइज़ी लीग्स में चमकने वाले खिलाड़ी सीधे नेशनल टीम में जगह बना रहे हैं, जिससे अंतरराष्ट्रीय रैंकिंग में शीर्ष चार टीमों का अंतर बेहद कम रह गया है।", "seg_points"),
            ]
        if angle == "series_caps":
            leader_txt = ", ".join(f"{x.get('category', '')}: {x.get('player', '').title()} ({x.get('value', '')})" for x in sl[:3])
            return [
                ("host", f"टूर्नामेंट के प्रमुख स्टैट्स लीडर्स की सूची में इस वक्त {leader_txt or f'{striker} सबसे आगे'} छाए हुए हैं।", "seg_points"),
                ("expert", "जब लीडरबोर्ड के टॉप बल्लेबाज़ और सबसे ज़्यादा छक्के लगाने वाले खिलाड़ी लय में हों, तो विपक्षी गेंदबाज़ उनके खिलाफ खास डेटा प्लान तैयार करके मैदान में उतरते हैं।", "seg_points"),
            ]
        top_teams = ", ".join(f"{r.get('team', '')} ({r.get('pts', 0)} अंक)" for r in pt[:3])
        return [
            ("expert", f"टूर्नामेंट के पॉइंट्स टेबल की दौड़ अभी से रोमांचक हो चली है। शीर्ष पर {top_teams or team} के बीच कड़ा मुकाबला दिख रहा है, और ऐसे में सिर्फ जीत नहीं बल्कि नेट रन रेट भी आखिरी हफ़्ते में सेमीफाइनल का टिकट तय करता है।", "seg_points"),
            ("host", "बिल्कुल ठीक कहा! हर एक ओवर में बचाया गया चार-पांच रन महीने के अंत में बहुत बड़ी बढ़त दिलाता है।", "seg_points"),
        ]

    # 5. CREX FORM, H2H & FAN POLL (3 non-repeating angles)
    if topic == "form_h2h_poll":
        tf = state.team_form or {}
        fp = state.fan_poll or {}
        h2h = state.recent_h2h or []
        angle = deck.pick("form_angle", ["streak", "h2h_recap", "fan_poll"])
        if angle == "fan_poll":
            return [
                ("host", f"लाइव फैन पोल पर अभी तक {fp.get('total_votes', 207850):,} से अधिक क्रिकेट प्रेमी अपनी भविष्यवाणी दर्ज कर चुके हैं!", "seg_form"),
                ("expert", f"पोल में {team} को {fp.get('batting_pct', 50)} प्रतिशत और {bowl_team} को {fp.get('bowling_pct', 50)} प्रतिशत समर्थन मिला है। लेकिन एक अच्छा ओवर या एक कैच इस पूरे पोल का मीटर उलट सकता है।", "seg_form"),
            ]
        if angle == "h2h_recap" and h2h:
            last_h2h = h2h[0]
            return [
                ("host", f"इन दोनों टीमों के पिछले आमने-सामने रिकॉर्ड हमेशा कांटे के रहे हैं — पिछली भिड़ंत में {last_h2h.get('match', '')} के दौरान {last_h2h.get('result', '')} हुआ था।", "seg_form"),
                ("expert", "पुरानी राइवलरी जब भी मैदान पर उतरती है, तो खिलाड़ी सामान्य से दस प्रतिशत अतिरिक्त जोश दिखाते हैं और छोटे मोमेंट्स बड़े बन जाते हैं।", "seg_form"),
            ]
        bat_form = _spoken_form(tf.get("batting", ["W", "L"])[-5:])
        bowl_form = _spoken_form(tf.get("bowling", ["W", "W"])[-5:])
        return [
            ("host", f"पिछले पांच मुकाबलों की फॉर्म पर नज़र डालें तो {team} का सफर {bat_form} और {bowl_team} का {bowl_form} रहा है।", "seg_form"),
            ("expert", "मोमेंटम बहुत तेज़ी से बदलता है — लगातार जीत के बाद ड्रेसिंग रूम में निडरता आती है, जबकि हार के बाद कप्तान बेसिक्स पर लौटने की सलाह देते हैं।", "seg_form"),
        ]

    # 6. CREX NEWS DESK (Zero-repeat)
    if topic == "crex_news":
        news_list = get_news_items(limit=20)
        if news_list:
            picked = deck.pick("crex_news", news_list)
            raw_title = picked["title"]
            # Strip CREX author/timestamp suffix like "KAUSHIK∙ 4 HRS AGO"
            headline = re.sub(r"\s+[A-Z][A-Za-z\s]*[•∙]\s*\d+\s+(?:HRS?|MINS?|DAYS?|WEEKS?)\s+AGO.*$", "", raw_title).strip()
            headline = headline or raw_title
            bridge = deck.pick(
                "news_bridge",
                [
                    f"क्रिकेट जगत में इस वक्त हर तरफ इस खबर की चर्चा है — {headline}. आज के दौर में खिलाड़ी एक तरफ लीग क्रिकेट खेलते हैं और साथ ही इंटरनेशनल रिकॉर्ड्स पर भी नज़र बनाए रखते हैं। ऐसी उपलब्धियां युवा खिलाड़ियों को भी प्रेरित करती हैं कि हर मैच को पूरी गंभीरता से लें।",
                    f"जी हाँ, {headline} — यह अपडेट बताती है कि आधुनिक क्रिकेट कितनी तेज़ी से बदल रहा है। चाहे रिकॉर्ड्स टूटने की बात हो या टीम सिलेक्शन की रणनीति, हर टूर्नामेंट अगले बड़े इवेंट की तैयारी बन चुका है।",
                    f"बिल्कुल, जब ऐसी बड़ी खबरें सामने आती हैं — जैसे {headline} — तो ड्रेसिंग रूम के माहौल और फैंस की उम्मीदों दोनों में नया रोमांच जुड़ जाता है।",
                ],
            )
            outro = deck.pick(
                "news_outro",
                [
                    f"वाकई बड़ी खबर है! चलिए इसी ऊर्जा के साथ वापस {venue} की पिच पर लौटते हैं जहाँ {striker} क्रीज़ पर डटे हुए हैं।",
                    f"बिल्कुल सही विश्लेषण! खैर अब निगाहें फिर से मैदान पर — {bowler} अपने अगले ओवर की तैयारी कर रहे हैं।",
                    f"जी हाँ, क्रिकेट की दुनिया लगातार घूम रही है — और उधर {team} की नज़रें अगले कुछ ओवरों में स्कोर तेज़ी से बढ़ाने पर हैं।",
                    f"बहुत बढ़िया अपडेट थी यह! चलिए अब क्रीज़ के एक्शन पर वापस आते हैं जहाँ {striker} और {non_striker} मौजूद हैं।",
                ],
            )
            return [
                ("host", f"मैच के बीच क्रिकेट न्यूज़ डेस्क से एक अहम अपडेट भी आ रही है — {headline}।", "seg_news"),
                ("expert", bridge, "seg_news"),
                ("host", outro, "seg_news"),
            ]

    # 7. DB STORYTELLING (Varied narrator & multi-sentence delivery)
    if topic == "db_story":
        raw_stories = get_all_stories()
        series_low = (state.series_name or "").lower()
        all_stories = [
            s for s in raw_stories
            if (s.get("match_context") or "general") == "general"
            or ((s.get("match_context") or "").lower() in series_low)
        ] or [s for s in raw_stories if (s.get("match_context") or "general") == "general"]
        if all_stories:
            st = deck.pick("db_story", all_stories)
            opener = deck.pick(
                "story_opener",
                [
                    f"यार {venue} की इस फ्लडलाइट्स और भीड़ को देखकर मुझे एक कमाल का किस्सा याद आ रहा है...",
                    "सुनिए ज़रा... मैं आपको क्रिकेट की एक ऐसी मज़ेदार बात बताता हूँ जो बहुत कम लोग जानते होंगे!",
                    "वैसे इस मुकाबले के बीच मुझे ड्रेसिंग रूम का एक शानदार किस्सा याद आ गया...",
                ],
            )
            # Alternate between extended Expert storytelling, multi-turn, and Host lead
            if random.random() < 0.5:
                s_outro = deck.pick(
                    "story_outro",
                    [
                        f"हाहा, यही तो इस खेल को बाकी खेलों से अलग बनाता है! खैर नज़रें फिर से {bowler} पर जो अगले ओवर के लिए तैयार हैं।",
                        f"क्या कमाल का किस्सा था! अब देखते हैं क्रीज़ पर {striker} यहाँ से कैसी पारी खेलते हैं।",
                        f"बिल्कुल लाजवाब बात कही आपने! खैर मैदान पर मुकाबला फिर गरमाता जा रहा है।",
                    ],
                )
                return [
                    ("host", opener, "seg_story"),
                    ("expert", f"{st['host_line']} और मज़े की बात यह है कि {st['expert_line']}", "seg_story"),
                    ("host", s_outro, "seg_story"),
                ]
            return [
                ("host", st["host_line"], "seg_story"),
                ("expert", st["expert_line"], "seg_story"),
            ]

    # 8. RULES, BIOMECHANICS & CRAFT DEEP-DIVE
    rule_id, rule_turns = deck.pick("rules_craft", RULES_AND_CRAFT_LIBRARY)
    return [(spk, txt, f"seg_rule:{rule_id}") for spk, txt in rule_turns]
