"""Screen-accurate scripted broadcast demo showcasing all 12 pages, 4/6/W stingers, and Hindi Host + Expert."""

from __future__ import annotations

import asyncio
from typing import Awaitable, Callable

from .commentary import CommentaryTurn, synthesize_fish_audio
from .models import BatsmanState, BowlerState, OverSummary, ScoreboardState

ControlCallback = Callable[[dict], Awaitable[None]]
StateCallback = Callable[[ScoreboardState], Awaitable[None]]
SpeakCallback = Callable[[list[CommentaryTurn]], Awaitable[float]]


def _calc_econ(runs: int, overs_str: str) -> float:
    ov, ball = (int(x) for x in overs_str.split("."))
    total_ov = ov + (ball / 6.0)
    return round(runs / total_ov, 2) if total_ov > 0 else 0.0


def build_demo_seed_state() -> ScoreboardState:
    """Create a rich, internally consistent IND vs AUS match state."""
    batters = [
        BatsmanState(name="ROHIT SHARMA", runs=48, balls=31, fours=6, sixes=2, strike_rate=154.84, dismissal="c Inglis b Starc"),
        BatsmanState(name="SHUBMAN GILL", runs=22, balls=19, fours=3, sixes=0, strike_rate=115.79, dismissal="b Hazlewood"),
        BatsmanState(name="VIRAT KOHLI", runs=64, balls=42, fours=7, sixes=2, strike_rate=152.38, on_strike=True, dismissal="batting"),
        BatsmanState(name="SURYAKUMAR YADAV", runs=31, balls=16, fours=3, sixes=2, strike_rate=193.75, on_strike=False, dismissal="batting"),
        BatsmanState(name="HARDIK PANDYA", runs=0, balls=0, fours=0, sixes=0, strike_rate=0.0, dismissal="yet to bat"),
        BatsmanState(name="RISHABH PANT", runs=0, balls=0, fours=0, sixes=0, strike_rate=0.0, dismissal="yet to bat"),
        BatsmanState(name="RAVINDRA JADEJA", runs=0, balls=0, fours=0, sixes=0, strike_rate=0.0, dismissal="yet to bat"),
        BatsmanState(name="AXAR PATEL", runs=0, balls=0, fours=0, sixes=0, strike_rate=0.0, dismissal="yet to bat"),
        BatsmanState(name="KULDEEP YADAV", runs=0, balls=0, fours=0, sixes=0, strike_rate=0.0, dismissal="yet to bat"),
        BatsmanState(name="JASPRIT BUMRAH", runs=0, balls=0, fours=0, sixes=0, strike_rate=0.0, dismissal="yet to bat"),
        BatsmanState(name="ARSHDEEP SINGH", runs=0, balls=0, fours=0, sixes=0, strike_rate=0.0, dismissal="yet to bat"),
    ]
    bowlers = [
        BowlerState(name="MITCHELL STARC", overs="3.2", maidens=0, runs_conceded=34, wickets=1, economy=10.20),
        BowlerState(name="JOSH HAZLEWOOD", overs="4.0", maidens=0, runs_conceded=29, wickets=1, economy=7.25),
        BowlerState(name="PAT CUMMINS", overs="3.0", maidens=0, runs_conceded=31, wickets=0, economy=10.33),
        BowlerState(name="ADAM ZAMPA", overs="4.0", maidens=0, runs_conceded=36, wickets=0, economy=9.00),
        BowlerState(name="GLENN MAXWELL", overs="2.0", maidens=0, runs_conceded=22, wickets=0, economy=11.00),
    ]
    recent_overs = [
        OverSummary(over_number=12, balls=["1", "4", "0", "1", "2", "1"], total=9),
        OverSummary(over_number=13, balls=["1", "0", "6", "1", "1", "4"], total=13),
        OverSummary(over_number=14, balls=["2", "1", "0", "4", "1", "2"], total=10),
        OverSummary(over_number=15, balls=["1", "6", "1", "0", "4", "1"], total=13),
        OverSummary(over_number=16, balls=["4", "1", "2", "1", "6", "0"], total=14),
        OverSummary(over_number=17, balls=["1", "0"], total=1),
    ]
    return ScoreboardState(
        batting_team="IND",
        bowling_team="AUS",
        runs=169,
        wickets=2,
        overs="16.2",
        partnership="68(33)",
        crr=10.35,
        last_5_ov="63/0",
        callout="STRIKE ROTATED",
        callout_tone="neutral",
        prev_over=recent_overs[-2],
        curr_over=recent_overs[-1],
        striker=batters[2],
        non_striker=batters[3],
        bowler=bowlers[0],
        last_wicket="SHUBMAN GILL • 22(19)",
        match_title="IND vs AUS, 3rd T20I • Wankhede Stadium, Mumbai",
        venue="Wankhede Stadium, Mumbai",
        series_name="IND vs AUS T20I Series 2026",
        match_date="LIVE • NIGHT T20I",
        head_to_head="IND 19 - 11 AUS",
        win_prob_batting=64,
        recent_overs=recent_overs,
        batters_list=batters,
        bowlers_list=bowlers,
        fall_of_wickets=["68-1 • ROHIT SHARMA (7.4)", "101-2 • SHUBMAN GILL (11.1)"],
        batting_xi=[b.name for b in batters],
        bowling_xi=[
            "TRAVIS HEAD", "MITCHELL MARSH", "JOSH INGLIS", "GLENN MAXWELL",
            "MARCUS STOINIS", "TIM DAVID", "MATTHEW WADE", "PAT CUMMINS",
            "MITCHELL STARC", "ADAM ZAMPA", "JOSH HAZLEWOOD",
        ],
    )


DEMO_LINES: list[CommentaryTurn] = [
    ("host", "नमस्कार दोस्तों! वानखेड़े स्टेडियम मुंबई में भारत और ऑस्ट्रेलिया के बीच टी-ट्वेंटी सीरीज़ का महा-मुकाबला है!"),
    ("expert", "अरे भाई! स्क्रीन पर इंडिया वर्सेस ऑस्ट्रेलिया का फेस-ऑफ देखिए, दोनों टीमें पूरी ताकत के साथ तैयार हैं!"),
    ("host", "मैच इन्फो पर नज़र डालें तो वानखेड़े स्टेडियम मुंबई में आज नाइट टी-ट्वेंटी है, और हेड टू हेड में भारत उन्नीस-ग्यारह से आगे है।"),
    ("expert", "बिल्कुल! उन्नीस-ग्यारह का रिकॉर्ड भारत के पक्ष में ज़रूर है, लेकिन ऑस्ट्रेलिया कभी भी बड़ा पलटवार कर सकता है!"),
    ("host", "दोनों टीमों की प्लेइंग इलेवन आपकी स्क्रीन पर है — भारत में रोहित, गिल, कोहली और सूर्या के साथ हार्दिक, पंत और बुमराह शामिल हैं।"),
    ("expert", "और ऑस्ट्रेलिया की प्लेइंग इलेवन भी कम नहीं — हेड, मार्श, मैक्सवेल, कमिंस, स्टार्क, ज़म्पा और हेज़लवुड सब मैदान में हैं!"),
    ("host", "सिंगल के साथ स्ट्राइक रोटेट! अब सूर्यकुमार यादव बाईं ओर स्ट्राइक पर आ गए हैं, स्कोर एक सौ सत्तर पर दो।"),
    ("host", "चौका! सूर्यकुमार यादव का शानदार फ्लिक, भारत का स्कोर एक सौ चौहत्तर पर दो!"),
    ("expert", "ओहोहो! क्या टाइमिंग थी भाई! स्टार्क की तेज़ गेंद पर चार रन, सूर्या अब पैंतीस रन पर पहुँच गए हैं!"),
    ("host", "प्लेयर स्पॉटलाइट में देखिए सूर्यकुमार यादव — सत्रह गेंदों में पैंतीस रन, चार चौके, दो छक्के और दो सौ पाँच का स्ट्राइक रेट!"),
    ("expert", "जी हाँ, दो सौ पाँच से ऊपर का स्ट्राइक रेट टी-ट्वेंटी में गेंदबाज़ों के लिए सबसे बड़ा सिरदर्द है!"),
    ("host", "पार्टनरशिप ट्रैकर पर देखें तो सूर्यकुमार पैंतीस और विराट कोहली पैंसठ रन बनाकर खेल रहे हैं, कुल साझेदारी तिहत्तर रन की!"),
    ("expert", "सिर्फ पैंतीस गेंदों में तिहत्तर रन! एक तरफ कोहली का क्लास, दूसरी तरफ सूर्या की तेज़ी!"),
    ("host", "छक्का!! गगनचुंबी छक्का! भारत का स्कोर एक सौ अस्सी पर दो विकेट, सूर्यकुमार इकतालीस पर!"),
    ("expert", "अरे वाह! अठारह गेंदों में इकतालीस रन, पूरा वानखेड़े झूम उठा है!"),
    ("host", "ओवर प्रोग्रेशन चार्ट देखिए — तेरहवें ओवर में तेरह, पंद्रहवें में तेरह और सोलहवें ओवर में चौदह रन बने हैं!"),
    ("expert", "बिल्कुल! और फॉल ऑफ विकेट्स देखें तो सिर्फ दो विकेट गिरे — पहला अड़सठ पर रोहित शर्मा और दूसरा एक सौ एक पर शुभमन गिल!"),
    ("host", "गेंदबाज़ी आंकड़ों में जोश हेज़लवुड ने चार ओवर में सिर्फ उनतीस रन देकर एक विकेट लिया है, इकोनॉमी सात दशमलव दो पाँच।"),
    ("expert", "वहीं मिचेल स्टार्क तीन दशमलव पाँच ओवर में पैंतालीस रन दे चुके हैं और ज़म्पा को भी चार ओवर में छत्तीस रन पड़े हैं!"),
    ("host", "आउट!! बड़ा झटका! मिचेल स्टार्क ने सूर्यकुमार यादव को इकतालीस के स्कोर पर आउट किया! भारत एक सौ अस्सी पर तीन विकेट।"),
    ("expert", "और अब हार्दिक पांड्या स्ट्राइक पर आ चुके हैं! स्टार्क ने अपना दूसरा विकेट लेकर ऑस्ट्रेलिया को वापसी दिलाई!"),
    ("host", "पूरा बैटिंग स्कोरकार्ड आपकी स्क्रीन पर — विराट कोहली पैंसठ पर नाबाद हैं, रोहित ने अड़तालीस और सूर्या ने इकतालीस रन बनाए।"),
    ("expert", "नीचे हार्दिक पांड्या, ऋषभ पंत और जडेजा अभी बाकी हैं, यानी आखिरी तीन ओवरों में बड़ा स्कोर तय है!"),
    ("host", "टॉप परफॉर्मर्स में बल्लेबाज़ी में नंबर एक विराट कोहली पैंसठ रन के साथ, और नंबर दो पर रोहित शर्मा अड़तालीस रन पर।"),
    ("expert", "और गेंदबाज़ी में मिचेल स्टार्क दो विकेट लेकर नंबर एक पर हैं, जबकि हेज़लवुड एक विकेट के साथ दूसरे नंबर पर!"),
    ("host", "मैच सेंटर और विन प्रोबेबिलिटी देखें तो करंट रन रेट दस दशमलव पाँच नौ है, और भारत बासठ प्रतिशत से आगे चल रहा है।"),
    ("expert", "ऑस्ट्रेलिया अभी भी अड़तीस प्रतिशत मुकाबले में बना हुआ है — आखिरी तीन ओवर बेहद रोमांचक होंगे!"),
    ("host", "सत्रह ओवर पूरे, भारत का स्कोर एक सौ अस्सी पर तीन विकेट। छोटा सा ड्रिंक्स ब्रेक है, बने रहिए हमारे साथ!"),
]


async def prepare_demo_audio() -> int:
    """Pre-synthesize all demo TTS clips into cache so playback has 0ms synthesis delay."""
    count = 0
    for speaker, text in DEMO_LINES:
        if await synthesize_fish_audio(text, speaker=speaker):
            count += 1
    return count


async def run_demo_showcase(
    state: ScoreboardState,
    on_state: StateCallback,
    on_control: ControlCallback,
    on_speak: SpeakCallback,
) -> None:
    """Run a screen-accurate broadcast demo across all 12 pages with synced Hindi commentary."""
    seed = build_demo_seed_state()
    for field_name in seed.model_fields:
        setattr(state, field_name, getattr(seed, field_name))
    await on_state(state)

    async def step(
        slide: str | None,
        turns: list[CommentaryTurn],
        extra_hold: float = 0.45,
        fx_event: str | None = None,
        fx_sub: str = "",
    ) -> None:
        if slide:
            await on_control({"type": "slide", "url": slide})
            await asyncio.sleep(0.55)
        if fx_event:
            await on_control({"type": "event_fx", "event": fx_event, "subtitle": fx_sub})
        spoken_sec = 0.0
        if turns:
            spoken_sec = await on_speak(turns)
        await asyncio.sleep(max(extra_hold, spoken_sec + extra_hold))

    # 1. Pre-Match Versus Poster (shows: IND vs AUS, Wankhede Stadium, Series 2026)
    await step(
        "/versus.html",
        [
            ("host", "नमस्कार दोस्तों! वानखेड़े स्टेडियम मुंबई में भारत और ऑस्ट्रेलिया के बीच टी-ट्वेंटी सीरीज़ का महा-मुकाबला है!"),
            ("expert", "अरे भाई! स्क्रीन पर इंडिया वर्सेस ऑस्ट्रेलिया का फेस-ऑफ देखिए, दोनों टीमें पूरी ताकत के साथ तैयार हैं!"),
        ],
    )

    # 2. Match Info & Venue (shows: Series 2026, Wankhede Stadium Mumbai, Night T20I, Head-to-Head IND 19 - 11 AUS)
    await step(
        "/info.html",
        [
            ("host", "मैच इन्फो पर नज़र डालें तो वानखेड़े स्टेडियम मुंबई में आज नाइट टी-ट्वेंटी है, और हेड टू हेड में भारत उन्नीस-ग्यारह से आगे है।"),
            ("expert", "बिल्कुल! उन्नीस-ग्यारह का रिकॉर्ड भारत के पक्ष में ज़रूर है, लेकिन ऑस्ट्रेलिया कभी भी बड़ा पलटवार कर सकता है!"),
        ],
    )

    # 3. Playing XI (shows: IND 11 batters & AUS 11 players)
    await step(
        "/playing11.html",
        [
            ("host", "दोनों टीमों की प्लेइंग इलेवन आपकी स्क्रीन पर है — भारत में रोहित, गिल, कोहली और सूर्या के साथ हार्दिक, पंत और बुमराह शामिल हैं।"),
            ("expert", "और ऑस्ट्रेलिया की प्लेइंग इलेवन भी कम नहीं — हेड, मार्श, मैक्सवेल, कमिंस, स्टार्क, ज़म्पा और हेज़लवुड सब मैदान में हैं!"),
        ],
    )

    # 4. Main Scoreboard -> 16.3 Single (Strike Rotated) -> 16.4 FOUR!
    await step("/", [], extra_hold=1.5)
    state.runs += 1
    state.overs = "16.3"
    state.partnership = "69(34)"
    state.crr = round(state.runs / 16.5, 2)
    state.striker.runs += 1
    state.striker.balls += 1
    state.striker.strike_rate = round((state.striker.runs / state.striker.balls) * 100, 2)
    state.bowler.runs_conceded += 1
    state.bowler.overs = "3.3"
    state.bowler.economy = _calc_econ(state.bowler.runs_conceded, state.bowler.overs)
    state.curr_over.balls.append("1")
    state.curr_over.total += 1
    state.striker, state.non_striker = state.non_striker, state.striker
    state.striker.on_strike = True
    state.non_striker.on_strike = False
    state.callout = "STRIKE ROTATED"
    state.callout_tone = "neutral"
    await on_state(state)
    await step(
        None,
        [("host", "सिंगल के साथ स्ट्राइक रोटेट! अब सूर्यकुमार यादव बाईं ओर स्ट्राइक पर आ गए हैं, स्कोर एक सौ सत्तर पर दो।")],
    )

    state.runs += 4
    state.overs = "16.4"
    state.partnership = "73(35)"
    state.crr = round(state.runs / 16.67, 2)
    state.striker.runs += 4
    state.striker.balls += 1
    state.striker.fours += 1
    state.striker.strike_rate = round((state.striker.runs / state.striker.balls) * 100, 2)
    state.bowler.runs_conceded += 4
    state.bowler.overs = "3.4"
    state.bowler.economy = _calc_econ(state.bowler.runs_conceded, state.bowler.overs)
    state.curr_over.balls.append("4")
    state.curr_over.total += 4
    state.callout = "FOUR!"
    state.callout_tone = "four"
    state.win_prob_batting = 68
    await on_state(state)
    await step(
        None,
        [
            ("host", "चौका! सूर्यकुमार यादव का शानदार फ्लिक, भारत का स्कोर एक सौ चौहत्तर पर दो!"),
            ("expert", "ओहोहो! क्या टाइमिंग थी भाई! स्टार्क की तेज़ गेंद पर चार रन, सूर्या अब पैंतीस रन पर पहुँच गए हैं!"),
        ],
        fx_event="FOUR",
        fx_sub="SURYAKUMAR YADAV • WRISTY FLICK",
    )

    # 5. Player Spotlight (shows: SURYAKUMAR YADAV 35 (17), 4s: 4, 6s: 2, SR: 205.88)
    await step(
        "/player.html",
        [
            ("host", "प्लेयर स्पॉटलाइट में देखिए सूर्यकुमार यादव — सत्रह गेंदों में पैंतीस रन, चार चौके, दो छक्के और दो सौ पाँच का स्ट्राइक रेट!"),
            ("expert", "जी हाँ, दो सौ पाँच से ऊपर का स्ट्राइक रेट टी-ट्वेंटी में गेंदबाज़ों के लिए सबसे बड़ा सिरदर्द है!"),
        ],
    )

    # 6. Partnership Tracker (shows: SURYAKUMAR YADAV 35(17) vs VIRAT KOHLI 65(43), Partnership 73(35))
    await step(
        "/partnership.html",
        [
            ("host", "पार्टनरशिप ट्रैकर पर देखें तो सूर्यकुमार पैंतीस और विराट कोहली पैंसठ रन बनाकर खेल रहे हैं, कुल साझेदारी तिहत्तर रन की!"),
            ("expert", "सिर्फ पैंतीस गेंदों में तिहत्तर रन! एक तरफ कोहली का क्लास, दूसरी तरफ सूर्या की तेज़ी!"),
        ],
    )

    # 7. Back to Main Scoreboard -> 16.5 SIX!
    await step("/", [], extra_hold=1.5)
    state.runs += 6
    state.overs = "16.5"
    state.partnership = "79(36)"
    state.crr = round(state.runs / 16.83, 2)
    state.striker.runs += 6
    state.striker.balls += 1
    state.striker.sixes += 1
    state.striker.strike_rate = round((state.striker.runs / state.striker.balls) * 100, 2)
    state.bowler.runs_conceded += 6
    state.bowler.overs = "3.5"
    state.bowler.economy = _calc_econ(state.bowler.runs_conceded, state.bowler.overs)
    state.curr_over.balls.append("6")
    state.curr_over.total += 6
    state.callout = "SIX!"
    state.callout_tone = "six"
    state.win_prob_batting = 74
    await on_state(state)
    await step(
        None,
        [
            ("host", "छक्का!! गगनचुंबी छक्का! भारत का स्कोर एक सौ अस्सी पर दो विकेट, सूर्यकुमार इकतालीस पर!"),
            ("expert", "अरे वाह! अठारह गेंदों में इकतालीस रन, पूरा वानखेड़े झूम उठा है!"),
        ],
        fx_event="SIX",
        fx_sub="SURYAKUMAR YADAV • 94m MAXIMUM",
    )

    # 8. Over Progression & FOW (shows: OV 12..17 bars, FOW: 68-1 Rohit, 101-2 Gill)
    await step(
        "/overs.html",
        [
            ("host", "ओवर प्रोग्रेशन चार्ट देखिए — तेरहवें ओवर में तेरह, पंद्रहवें में तेरह और सोलहवें ओवर में चौदह रन बने हैं!"),
            ("expert", "और फॉल ऑफ विकेट्स देखें तो सिर्फ दो विकेट गिरे — पहला अड़सठ पर रोहित शर्मा और दूसरा एक सौ एक पर शुभमन गिल!"),
        ],
    )

    # 9. Bowling Figures (shows: Starc 3.5-0-45-1, Hazlewood 4.0-0-29-1, Cummins 3.0-0-31-0, Zampa 4.0-0-36-0, Maxwell 2.0-0-22-0)
    await step(
        "/bowling.html",
        [
            ("host", "गेंदबाज़ी आंकड़ों में जोश हेज़लवुड ने चार ओवर में सिर्फ उनतीस रन देकर एक विकेट लिया है, इकोनॉमी सात दशमलव दो पाँच।"),
            ("expert", "वहीं मिचेल स्टार्क तीन दशमलव पाँच ओवर में पैंतालीस रन दे चुके हैं और ज़म्पा को भी चार ओवर में छत्तीस रन पड़े हैं!"),
        ],
    )

    # 10. Back to Main Scoreboard -> 16.6 WICKET!
    await step("/", [], extra_hold=1.5)
    state.wickets += 1
    state.overs = "16.6"
    state.partnership = "0(0)"
    state.crr = round(state.runs / 17.0, 2)
    state.bowler.wickets += 1
    state.bowler.overs = "4.0"
    state.bowler.economy = _calc_econ(state.bowler.runs_conceded, state.bowler.overs)
    state.curr_over.balls.append("W")
    state.last_wicket = f"{state.striker.name} • {state.striker.runs}({state.striker.balls + 1})"
    state.fall_of_wickets.append(f"{state.runs}-{state.wickets} • {state.striker.name} (16.6)")
    state.batters_list[3].balls += 1
    state.batters_list[3].strike_rate = round((state.batters_list[3].runs / state.batters_list[3].balls) * 100, 2)
    state.batters_list[3].dismissal = "c Marsh b Starc"
    state.batters_list[3].on_strike = False
    state.batters_list[4].on_strike = True
    state.batters_list[4].dismissal = "batting"
    state.striker = state.batters_list[4]
    state.callout = "WICKET!"
    state.callout_tone = "wicket"
    state.win_prob_batting = 62
    await on_state(state)
    await step(
        None,
        [
            ("host", "आउट!! बड़ा झटका! मिचेल स्टार्क ने सूर्यकुमार यादव को इकतालीस के स्कोर पर आउट किया! भारत एक सौ अस्सी पर तीन विकेट।"),
            ("expert", "और अब हार्दिक पांड्या स्ट्राइक पर आ चुके हैं! स्टार्क ने अपना दूसरा विकेट लेकर ऑस्ट्रेलिया को वापसी दिलाई!"),
        ],
        fx_event="WICKET",
        fx_sub="SURYAKUMAR c MARSH b STARC • 41(19)",
    )

    # 11. Full Batting Scorecard (shows: Rohit 48, Gill 22, Kohli 65*, Suryakumar 41, Hardik 0*)
    await step(
        "/batting.html",
        [
            ("host", "पूरा बैटिंग स्कोरकार्ड आपकी स्क्रीन पर — विराट कोहली पैंसठ पर नाबाद हैं, रोहित ने अड़तालीस और सूर्या ने इकतालीस रन बनाए।"),
            ("expert", "नीचे हार्दिक पांड्या, ऋषभ पंत और जडेजा अभी बाकी हैं, यानी आखिरी तीन ओवरों में बड़ा स्कोर तय है!"),
        ],
    )

    # 12. Top Performers (shows: #1 Kohli 65(43), #2 Rohit 48(31), #1 Starc 2-45(4.0), #2 Hazlewood 1-29(4.0))
    await step(
        "/leaders.html",
        [
            ("host", "टॉप परफॉर्मर्स में बल्लेबाज़ी में नंबर एक विराट कोहली पैंसठ रन के साथ, और नंबर दो पर रोहित शर्मा अड़तालीस रन पर।"),
            ("expert", "और गेंदबाज़ी में मिचेल स्टार्क दो विकेट लेकर नंबर एक पर हैं, जबकि हेज़लवुड एक विकेट के साथ दूसरे नंबर पर!"),
        ],
    )

    # 13. Win Probability & Match Center (shows: CRR 10.59, IND 62% vs AUS 38%, Last Wkt Suryakumar 41(19))
    await step(
        "/match.html",
        [
            ("host", "मैच सेंटर और विन प्रोबेबिलिटी देखें तो करंट रन रेट दस दशमलव पाँच नौ है, और भारत बासठ प्रतिशत से आगे चल रहा है।"),
            ("expert", "ऑस्ट्रेलिया अभी भी अड़तीस प्रतिशत मुकाबले में बना हुआ है — आखिरी तीन ओवर बेहद रोमांचक होंगे!"),
        ],
    )

    # 14. Break Screen (shows: IND 180/3 (16.6 ov) • DRINKS BREAK)
    state.callout = "DRINKS BREAK"
    state.callout_tone = "neutral"
    await on_state(state)
    await step(
        "/break.html",
        [("host", "सत्रह ओवर पूरे, भारत का स्कोर एक सौ अस्सी पर तीन विकेट। छोटा सा ड्रिंक्स ब्रेक है, बने रहिए हमारे साथ!")],
        extra_hold=1.5,
    )
    await on_control({"type": "demo_done"})
