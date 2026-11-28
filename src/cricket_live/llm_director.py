"""Async OpenAI-compatible AI Dialogue Director using Numes AI (Nemotron 3 Ultra)."""

from __future__ import annotations

import json
import os
import re

from dotenv import load_dotenv
import httpx

from .db import get_all_stories, get_news_items, get_recent_ball_events
from .models import ScoreboardState

load_dotenv()

DirectedTurn = tuple[str, str, str]

_TEAM_FULL_NAMES: dict[str, str] = {
    "IND-A": "India A (इंडिया ए)",
    "SL-A": "Sri Lanka A (श्रीलंका ए)",
    "IND": "India (इंडिया)",
    "SL": "Sri Lanka (श्रीलंका)",
    "BAN-A": "Bangladesh A (बांग्लादेश ए)",
    "BAN": "Bangladesh (बांग्लादेश)",
    "PAK-A": "Pakistan A (पाकिस्तान ए)",
    "PAK": "Pakistan (पाकिस्तान)",
    "AFG-A": "Afghanistan A (अफ़ग़ानिस्तान ए)",
    "AFG": "Afghanistan (अफ़ग़ानिस्तान)",
    "AUS": "Australia (ऑस्ट्रेलिया)",
    "ENG": "England (इंग्लैंड)",
    "NZ": "New Zealand (न्यूज़ीलैंड)",
    "SA": "South Africa (दक्षिण अफ्रीका)",
    "WI": "West Indies (वेस्ट इंडीज़)",
    "UAE": "United Arab Emirates (यूएई)",
    "HK": "Hong Kong (हांगकांग)",
}


def expand_team_name(code: str) -> str:
    """Convert short team codes like IND-A / SL-A into full spoken names."""
    key = (code or "").strip().upper()
    return _TEAM_FULL_NAMES.get(key, code)


def expand_form_list(items: list[str] | None) -> list[str]:
    """Convert W/L form codes into full Win/Loss words."""
    mapping = {"W": "Win (जीत)", "L": "Loss (हार)", "T": "Tie", "NR": "No Result", "D": "Draw"}
    return [mapping.get(str(x).strip().upper(), str(x)) for x in (items or [])]


_SYSTEM_PROMPT = """You are the sole, lead Hindi cricket commentator ("expert") on a high-energy live broadcast (Star Sports Hindi / IPL style).

PERSONA:
- "expert": An electrifying, sharp, passionate MALE Indian cricket commentator and analyst using strictly masculine Hindi verbs/grammar ("मैं देख रहा हूँ", "मैं मानता हूँ", "बता रहा हूँ") — NEVER feminine verbs like "बताती हूँ", "कहती हूँ", "देख रही हूँ".
- You carry the ENTIRE broadcast solo with seamless continuity, excitement, match urgency, tactical insight, pitch physics, and crisp storytelling.

STRICT RULES:
1. OUTPUT FORMAT: Return ONLY a valid JSON array of 1 to 3 objects: [{"speaker": "expert", "text": "..."}]. Every object MUST have "speaker": "expert". No markdown fences, no commentary outside JSON.
2. NATURAL SPOKEN HINDI (DEVANAGARI ONLY): Write vivid, high-energy, conversational broadcast Hindi in pure Devanagari (transliterate English cricket terms/names like इंडिया ए, श्रीलंका ए, हेटमायर, चमीरा, नूर अहमद, पावरप्ले, नेट रन रेट). ALWAYS speak full team names like "इंडिया ए" / "भारत ए" and "श्रीलंका ए" (NEVER abbreviations like "आईएनडी-ए" or "एसएल-ए"), and ALWAYS say "जीत" or "हार" instead of "W" or "L". Use natural spoken rhythm ("अरे वाह!", "देखिए...", "कमाल!", commas, "...") instead of stiff bookish prose. Never mix Arabic/Urdu characters or raw English abbreviations.
3. CONSISTENT SOLO FLOW: Keep sentences flowing smoothly from one thought to the next as one continuous commentator — no host/co-host handoffs, no "जैसा आपने कहा", no "continue what you were saying", and no mid-match greetings like "नमस्कार दोस्तों".
4. CREX COMMENTARY REFINEMENT: Whenever live_feed_commentary (from CREX) is provided, refine and elevate those exact ball/ground insights into exciting, natural spoken Hindi broadcast commentary rather than reading raw text robotically.
5. ZERO HALLUCINATION & NO REPETITION: Use ONLY numbers, scores, wickets, overs, player stats, team names, and news facts explicitly present in the provided JSON context. Never reuse openings/phrasings from recent_spoken_lines_avoid_repeating."""


def is_llm_configured() -> bool:
    return bool(os.getenv("LLM_API_KEY", "").strip() and os.getenv("LLM_BASE_URL", "").strip())


def _extract_json_array(raw: str) -> list[dict] | None:
    txt = (raw or "").strip()
    if txt.startswith("```"):
        txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt, flags=re.S).strip()
    start = txt.find("[")
    end = txt.rfind("]")
    if start == -1 or end <= start:
        return None
    try:
        parsed = json.loads(txt[start : end + 1])
        return parsed if isinstance(parsed, list) else None
    except Exception:
        return None


async def generate_llm_segment(
    state: ScoreboardState,
    topic_hint: str,
    recent_lines: list[str],
    news_cursor_item: dict | None = None,
    story_item: dict | None = None,
    slide_on_screen: dict[str, str] | None = None,
    timeout_sec: float = 16.0,
) -> list[DirectedTurn] | None:
    """Call Numes AI / OpenAI-compatible endpoint to generate a cohesive Hindi segment."""
    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "").strip().rstrip("/")
    model = os.getenv("LLM_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free").strip()
    if not api_key or not base_url:
        return None

    is_break_or_done = state.match_status in ("innings_break", "completed")
    effective_timeout = max(timeout_sec, 40.0) if is_break_or_done else max(timeout_sec, 25.0)

    recent_balls = get_recent_ball_events(limit=6)
    bat_full = expand_team_name(state.batting_team)
    bowl_full = expand_team_name(state.bowling_team)
    raw_form = state.team_form or {}
    expanded_form = {
        bat_full: expand_form_list(raw_form.get("batting")),
        bowl_full: expand_form_list(raw_form.get("bowling")),
    }
    compact_ctx: dict[str, object] = {
        "topic_focus": topic_hint,
        "match_status": state.match_status,
        "match_result": state.match_result,
        "match": f"{bat_full} vs {bowl_full} — {state.match_title}",
        "series": state.series_name,
        "venue": state.venue,
        "toss": state.toss,
        "teams": {"batting_team": bat_full, "bowling_team": bowl_full},
        "score": f"{bat_full} {state.runs}/{state.wickets} in {state.overs} ov (vs {bowl_full})",
        "crr": state.crr,
        "rrr": state.rrr,
        "target": state.target,
        "partnership": state.partnership,
        "striker": f"{state.striker.name} {state.striker.runs}({state.striker.balls}) 4s:{state.striker.fours} 6s:{state.striker.sixes} SR:{state.striker.strike_rate}",
        "non_striker": f"{state.non_striker.name} {state.non_striker.runs}({state.non_striker.balls})",
        "bowler": f"{state.bowler.name} {state.bowler.overs}-{state.bowler.maidens}-{state.bowler.runs_conceded}-{state.bowler.wickets} ER:{state.bowler.economy}",
        "top_batters": [f"{b.name} {b.runs}({b.balls}) {b.dismissal}" for b in state.batters_list[:5]],
        "top_bowlers": [f"{bw.name} {bw.wickets}/{bw.runs_conceded} ({bw.overs})" for bw in state.bowlers_list[:5]],
        "fall_of_wickets": state.fall_of_wickets[:6],
        "weather": state.weather,
        "venue_stats": state.venue_stats,
        "fan_poll": state.fan_poll,
        "team_form": expanded_form,
        "head_to_head": state.head_to_head,
        "points_table": state.points_table[:4],
        "series_leaders": state.series_leaders[:4],
        "icc_rankings": state.icc_rankings,
        "player_of_match": state.player_of_match,
        "first_innings": {
            "team": state.first_innings.get("team", ""),
            "score": state.first_innings.get("score", ""),
            "overs": state.first_innings.get("overs", ""),
            "top_batters": state.first_innings.get("batters", [])[:4],
        },
        "quiz_prompt": state.quiz_prompt,
        "recent_balls": [f"{b['overs']} -> {b['runs']}/{b['wickets']} ({b['callout']})" for b in recent_balls[:4]],
        "recent_spoken_lines_avoid_repeating": recent_lines[-6:],
    }
    if state.live_commentary:
        compact_ctx["live_feed_commentary"] = state.live_commentary[:900]
    if slide_on_screen:
        compact_ctx["graphic_slide_currently_on_screen"] = slide_on_screen
    if news_cursor_item:
        raw_title = news_cursor_item.get("title", "")
        clean_title = re.sub(r"\s+[A-Z][A-Za-z0-9\s]*[•∙].*$", "", raw_title).strip()
        compact_ctx["external_cricket_news_to_translate_in_hindi"] = clean_title or raw_title
    if story_item:
        compact_ctx["story_seed_to_retell_naturally"] = f"{story_item.get('host_line', '')} {story_item.get('expert_line', '')}"

    stage_note = (
        f" The match/innings is {state.match_status} ({state.match_result or 'break'}). Analyze the full graphic shown in graphic_slide_currently_on_screen in deep conversational Hindi."
        if is_break_or_done
        else " Connect naturally to graphic_slide_currently_on_screen while live play continues."
    )
    if state.live_commentary:
        stage_note += " Speak directly from live_feed_commentary (live pitch report / ground updates / ball-by-ball commentary) and weave those exact insights into your Hindi dialogue."
    user_prompt = (
        f"Generate the next conversational commentary segment focused on '{topic_hint}'.{stage_note}\n"
        f"Context JSON:\n{json.dumps(compact_ctx, ensure_ascii=False)}"
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.75,
        "max_tokens": 1200 if is_break_or_done else 800,
        "reasoning": {"effort": "none"},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    attempts = 2 if is_break_or_done else 1
    for attempt in range(attempts):
        try:
            async with httpx.AsyncClient(timeout=effective_timeout) as client:
                resp = await client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
                if resp.status_code != 200:
                    print(f"[llm_director] HTTP {resp.status_code} (try {attempt+1}): {resp.text[:180]}")
                    continue
                data = resp.json()
                choices = data.get("choices") or []
                if not choices:
                    print(f"[llm_director] empty choices (try {attempt+1})")
                    continue
                content = (choices[0].get("message") or {}).get("content") or ""
                arr = _extract_json_array(content)
                if not arr:
                    print(f"[llm_director] bad_json (try {attempt+1}): {content[:160]}")
                    continue

                turns: list[DirectedTurn] = []
                for item in arr:
                    if not isinstance(item, dict):
                        continue
                    txt = str(item.get("text", "")).strip()
                    if len(txt) < 12:
                        continue
                    if any("\u0600" <= ch <= "\u06ff" for ch in txt):
                        continue
                    turns.append(("expert", txt, f"ai:{topic_hint}"))
                if len(turns) >= 1:
                    return turns
                print(f"[llm_director] too_few_turns ({len(turns)}, try {attempt+1}): {content[:140]}")
        except Exception as exc:
            print(f"[llm_director] error (try {attempt+1}): {type(exc).__name__}: {exc}")
    return None


async def generate_live_ball_llm_turns(
    prev: ScoreboardState | None,
    curr: ScoreboardState,
    crex_text: str,
    recent_lines: list[str],
    tag: str = "live_crex_ball",
    timeout_sec: float = 2.2,
) -> list[DirectedTurn] | None:
    """Pass live CREX ball commentary + match state through the LLM so the solo Expert refines and delivers it."""
    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "").strip().rstrip("/")
    model = os.getenv("LLM_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free").strip()
    if not api_key or not base_url:
        return None

    bat_full = expand_team_name(curr.batting_team)
    bowl_full = expand_team_name(curr.bowling_team)
    runs_delta = (curr.runs - prev.runs) if prev else 0
    wicket_fell = bool(prev and curr.wickets > prev.wickets)
    ball_ctx = {
        "score": f"{bat_full} {curr.runs}/{curr.wickets} ({curr.overs} ov) vs {bowl_full}",
        "runs_on_ball": runs_delta,
        "wicket_fell": wicket_fell,
        "striker": f"{curr.striker.name} {curr.striker.runs}({curr.striker.balls})",
        "non_striker": f"{curr.non_striker.name} {curr.non_striker.runs}({curr.non_striker.balls})",
        "bowler": f"{curr.bowler.name} {curr.bowler.wickets}/{curr.bowler.runs_conceded} ({curr.bowler.overs})",
        "crr": curr.crr,
        "rrr": curr.rrr,
        "target": curr.target,
        "crex_live_commentary": (crex_text or curr.live_commentary or "")[:700],
        "recent_spoken_lines_avoid_repeating": recent_lines[-4:],
    }
    user_prompt = (
        "Refine the CREX live ball commentary below into 1 or 2 punchy, exciting, natural solo Expert Hindi commentary turns "
        "(pure Devanagari, high broadcast energy, no repetition). Return ONLY JSON array [{\"speaker\":\"expert\",\"text\":\"...\"}].\n"
        f"Ball Context JSON:\n{json.dumps(ball_ctx, ensure_ascii=False)}"
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.72,
        "max_tokens": 350,
        "reasoning": {"effort": "none"},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=timeout_sec) as client:
            resp = await client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
            if resp.status_code != 200:
                print(f"[llm_director:ball] HTTP {resp.status_code}: {resp.text[:160]}")
                return None
            data = resp.json()
            choices = data.get("choices") or []
            if not choices:
                return None
            content = (choices[0].get("message") or {}).get("content") or ""
            arr = _extract_json_array(content)
            if not arr:
                return None
            turns: list[DirectedTurn] = []
            for item in arr:
                if not isinstance(item, dict):
                    continue
                txt = str(item.get("text", "")).strip()
                if len(txt) < 10 or any("\u0600" <= ch <= "\u06ff" for ch in txt):
                    continue
                turns.append(("expert", txt, tag))
            return turns if turns else None
    except Exception as exc:
        print(f"[llm_director:ball] error: {type(exc).__name__}: {exc}")
        return None
