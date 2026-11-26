"""Live cricket data sources: official API poller, Playwright page reader, and simulator."""

from __future__ import annotations

import asyncio
import os
import random
import re
from typing import Awaitable, Callable

import httpx

from .models import BatsmanState, BowlerState, OverSummary, ScoreboardState

StateCallback = Callable[[ScoreboardState], Awaitable[None]]


async def run_simulator(state: ScoreboardState, on_update: StateCallback, interval: float = 4.0) -> None:
    """Emit realistic ball-by-ball updates for testing the live overlay."""
    outcomes = [
        ("0", 0, "DOT BALL", "neutral"),
        ("1", 1, "STRIKE ROTATED", "neutral"),
        ("2", 2, "2 RUNS", "neutral"),
        ("4", 4, "FOUR!", "four"),
        ("6", 6, "SIX!", "six"),
        ("W", 0, "WICKET!", "wicket"),
    ]
    weights = [30, 30, 12, 14, 8, 6]

    while True:
        await asyncio.sleep(interval)
        if state.match_status == "prematch":
            continue
        ball_label, runs_scored, callout, tone = random.choices(outcomes, weights=weights, k=1)[0]

        state.runs += runs_scored
        if ball_label == "W":
            state.wickets = min(10, state.wickets + 1)
            state.bowler.wickets += 1
            state.last_wicket = f"{state.striker.name} • {state.striker.runs}({state.striker.balls + 1})"
            state.striker.runs = 0
            state.striker.balls = 0
            state.striker.fours = 0
            state.striker.sixes = 0
            state.striker.strike_rate = 0.0
        else:
            state.striker.runs += runs_scored
            state.striker.balls += 1
            if runs_scored == 4:
                state.striker.fours += 1
            elif runs_scored == 6:
                state.striker.sixes += 1
            if state.striker.balls > 0:
                state.striker.strike_rate = round((state.striker.runs / state.striker.balls) * 100, 2)

        state.bowler.runs_conceded += runs_scored

        # Advance over & ball tracker
        ov_num, ball_num = (int(x) for x in state.overs.split("."))
        ball_num += 1
        if ball_num >= 6:
            ov_num += 1
            ball_num = 0
        state.overs = f"{ov_num}.{ball_num}"

        if len(state.curr_over.balls) >= 6:
            state.prev_over = state.curr_over.model_copy(deep=True)
            state.curr_over.over_number += 1
            state.curr_over.balls = []
            state.curr_over.total = 0

        state.curr_over.balls.append(ball_label)
        state.curr_over.total += runs_scored

        if runs_scored % 2 == 1:
            state.striker, state.non_striker = state.non_striker, state.striker
            state.striker.on_strike = True
            state.non_striker.on_strike = False

        total_overs = ov_num + (ball_num / 6)
        if total_overs > 0:
            state.crr = round(state.runs / total_overs, 2)

        state.callout = callout
        state.callout_tone = tone
        await on_update(state)


async def run_cricapi_poller(
    state: ScoreboardState,
    on_update: StateCallback,
    api_key: str,
    match_id: str | None = None,
    interval: float = 30.0,
) -> None:
    """Poll CricketData.org (CricAPI) free/developer JSON API."""
    url = f"https://api.cricapi.com/v1/currentMatches?apikey={api_key}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        while True:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                payload = resp.json()
                if payload.get("status") == "success":
                    matches = payload.get("data", [])
                    target = None
                    if match_id:
                        target = next((m for m in matches if m.get("id") == match_id), None)
                    elif matches:
                        target = matches[0]

                    if target:
                        teams = target.get("teams", [])
                        if len(teams) >= 2:
                            state.batting_team = str(teams[0]).upper()
                            state.bowling_team = str(teams[1]).upper()
                        scores = target.get("score", [])
                        if scores:
                            latest = scores[-1]
                            state.runs = int(latest.get("r", state.runs))
                            state.wickets = int(latest.get("w", state.wickets))
                            state.overs = str(latest.get("o", state.overs))
                        status_text = target.get("status", "")
                        if status_text:
                            state.callout = status_text[:28].upper()
                            state.callout_tone = "neutral"
                        await on_update(state)
            except Exception as exc:
                print(f"[cricapi] poll error: {exc}")
            await asyncio.sleep(interval)


async def run_playwright_reader(
    state: ScoreboardState,
    on_update: StateCallback,
    url: str,
    score_selector: str = "[data-score]",
    overs_selector: str = "[data-overs]",
    status_selector: str = "[data-status]",
    balls_selector: str = "[data-balls]",
    team_selector: str = "",
    crr_selector: str = "",
    poll_interval: float = 1.5,
) -> None:
    """Keep a single Playwright page open and watch live DOM updates without reloading."""
    from playwright.async_api import async_playwright

    selectors = {
        "score": score_selector,
        "overs": overs_selector,
        "status": status_selector,
        "balls": balls_selector,
        "team": team_selector,
        "crr": crr_selector,
    }

    last_snapshot: dict[str, str] = {}
    update_queue: asyncio.Queue[dict[str, str]] = asyncio.Queue()

    async def extract_snapshot(page) -> dict[str, str]:
        return await page.evaluate(
            """(sel) => {
                const read = (q) => {
                    const el = q ? document.querySelector(q) : null;
                    return el ? el.innerText.trim() : "";
                };
                const readList = (q) => {
                    if (!q) return "";
                    const els = Array.from(document.querySelectorAll(q));
                    return els.map((e) => e.innerText.trim()).filter(Boolean).join("|");
                };
                return {
                    score: read(sel.score),
                    overs: read(sel.overs),
                    status: read(sel.status),
                    balls: readList(sel.balls),
                    team: read(sel.team),
                    crr: read(sel.crr),
                    title: read("h1.name-wrapper"),
                    players: Array.from(document.querySelectorAll(".batsmen-career-wrapper"))
                        .map((e) => e.innerText.trim().replace(/\\s+/g, " "))
                        .join("||"),
                    overs_slides: Array.from(document.querySelectorAll(".overs-slide"))
                        .slice(-8)
                        .map((e) => e.innerText.trim().replace(/\\s+/g, " "))
                        .join("||"),
                    last_wkt: read("[class*='last-w'], [class*='wicket']"),
                    pship: read("[class*='partner']"),
                    commentary: (() => {
                        const cards = Array.from(document.querySelectorAll(".cm-b-roundcard"));
                        for (const c of cards) {
                            const t = (c.innerText || "").trim().replace(/\\s+/g, " ");
                            if (t.length > 28) return t;
                        }
                        return "";
                    })(),
                };
            }""",
            selectors,
        )

    def apply_snapshot(snap: dict[str, str]) -> bool:
        nonlocal last_snapshot
        if snap == last_snapshot:
            return False
        last_snapshot = snap

        changed = False
        team_text = snap.get("team", "")
        if team_text:
            state.batting_team = team_text.splitlines()[0].strip().upper()
            changed = True

        title_text = snap.get("title", "")
        if title_text:
            state.match_title = title_text
            m_teams = re.match(r"^\s*([A-Za-z0-9\- ]+?)\s+Vs\s+([A-Za-z0-9\- ]+?)(?:,|$)", title_text, re.I)
            if m_teams:
                t1, t2 = m_teams.group(1).strip().upper(), m_teams.group(2).strip().upper()
                state.bowling_team = t2 if state.batting_team == t1 else t1
                changed = True

        score_text = snap.get("score", "")
        sep = "/" if "/" in score_text else ("-" if "-" in score_text else "")
        if sep:
            runs_str, wkts_str = score_text.split(sep, 1)
            runs_digits = "".join(c for c in runs_str if c.isdigit())
            wkts_digits = "".join(c for c in wkts_str if c.isdigit())
            if runs_digits:
                state.runs = int(runs_digits)
                changed = True
            if wkts_digits:
                state.wickets = int(wkts_digits)
                changed = True

        overs_text = snap.get("overs", "")
        if overs_text:
            state.overs = overs_text.replace("OVERS:", "").strip()
            changed = True

        crr_text = snap.get("crr", "")
        if crr_text:
            try:
                state.crr = float(crr_text.replace("CRR", "").replace(":", "").strip())
                changed = True
            except ValueError:
                pass

        status_text = snap.get("status", "")
        if status_text:
            upper = status_text.upper()
            state.callout = upper[:28]
            if "SIX" in upper or upper == "6":
                state.callout_tone = "six"
            elif "FOUR" in upper or upper == "4":
                state.callout_tone = "four"
            elif "WICKET" in upper or "OUT" in upper or upper == "W":
                state.callout_tone = "wicket"
            else:
                state.callout_tone = "neutral"
            changed = True

        balls_raw = snap.get("balls", "")
        if balls_raw:
            balls = [b for b in balls_raw.split("|") if b][:6]
            if balls:
                state.curr_over.balls = balls
                state.curr_over.total = sum(int(b) for b in balls if b.isdigit())
                changed = True

        players_raw = snap.get("players", "")
        if players_raw:
            cards = [c.strip() for c in players_raw.split("||") if c.strip()]
            bat_cards = []
            for card in cards:
                m_bat = re.match(
                    r"^(.+?)\s*(\d+)\s*\((\d+)\).*?4s:\s*(\d+)\s*6s:\s*(\d+)\s*SR:\s*([\d.]+)",
                    card,
                )
                if m_bat:
                    bat_cards.append(m_bat)
                    continue
                m_bowl = re.match(
                    r"^(.+?)\s*(\d+)-(\d+)\s*\(([\d.]+)\).*?Econ:\s*([\d.]+)",
                    card,
                )
                if m_bowl:
                    state.bowler.name = m_bowl.group(1).strip().upper()
                    state.bowler.wickets = int(m_bowl.group(2))
                    state.bowler.runs_conceded = int(m_bowl.group(3))
                    state.bowler.overs = m_bowl.group(4)
                    state.bowler.economy = float(m_bowl.group(5))
                    changed = True

            if len(bat_cards) >= 1:
                b0 = bat_cards[0]
                state.non_striker.name = b0.group(1).strip().upper()
                state.non_striker.runs = int(b0.group(2))
                state.non_striker.balls = int(b0.group(3))
                state.non_striker.fours = int(b0.group(4))
                state.non_striker.sixes = int(b0.group(5))
                state.non_striker.strike_rate = float(b0.group(6))
                changed = True
            if len(bat_cards) >= 2:
                b1 = bat_cards[1]
                state.striker.name = b1.group(1).strip().upper()
                state.striker.runs = int(b1.group(2))
                state.striker.balls = int(b1.group(3))
                state.striker.fours = int(b1.group(4))
                state.striker.sixes = int(b1.group(5))
                state.striker.strike_rate = float(b1.group(6))
                changed = True

        slides_raw = snap.get("overs_slides", "")
        if slides_raw:
            parsed_overs: list[OverSummary] = []
            for slide in slides_raw.split("||"):
                m_ov = re.match(r"Over\s+(\d+)\s+(.*?)\s*=\s*(\d+)", slide.strip())
                if m_ov:
                    ov_num = int(m_ov.group(1))
                    ov_balls = [tok for tok in m_ov.group(2).split() if tok]
                    ov_total = int(m_ov.group(3))
                    parsed_overs.append(
                        OverSummary(over_number=ov_num, balls=ov_balls, total=ov_total)
                    )
            if parsed_overs:
                state.recent_overs = parsed_overs[-8:]
            if len(parsed_overs) == 1:
                state.curr_over = parsed_overs[0]
                changed = True
            elif len(parsed_overs) >= 2:
                state.prev_over = parsed_overs[-2]
                state.curr_over = parsed_overs[-1]
                changed = True

        last_wkt_text = snap.get("last_wkt", "")
        if last_wkt_text and "last wkt" in last_wkt_text.lower():
            cleaned_wkt = re.sub(r"^last\s*wkt\s*:\s*", "", last_wkt_text, flags=re.I).strip()
            if cleaned_wkt and cleaned_wkt != state.last_wicket:
                state.last_wicket = cleaned_wkt
                fow_entry = f"{state.wickets}-{state.runs} ({cleaned_wkt})"
                if fow_entry not in state.fall_of_wickets:
                    state.fall_of_wickets.append(fow_entry)
                changed = True

        pship_text = snap.get("pship", "")
        if pship_text and "(" in pship_text and len(pship_text) < 30:
            state.partnership = pship_text
            changed = True

        # Keep live batters_list & bowlers_list up to date for Slide 1 & Slide 2
        for active_bat in (state.striker, state.non_striker):
            existing = next((b for b in state.batters_list if b.name == active_bat.name), None)
            if existing:
                existing.runs = active_bat.runs
                existing.balls = active_bat.balls
                existing.fours = active_bat.fours
                existing.sixes = active_bat.sixes
                existing.strike_rate = active_bat.strike_rate
                existing.on_strike = active_bat.on_strike
            else:
                state.batters_list.append(active_bat.model_copy(deep=True))

        existing_bowl = next((bw for bw in state.bowlers_list if bw.name == state.bowler.name), None)
        if existing_bowl:
            existing_bowl.wickets = state.bowler.wickets
            existing_bowl.runs_conceded = state.bowler.runs_conceded
            existing_bowl.overs = state.bowler.overs
            existing_bowl.economy = state.bowler.economy
        else:
            state.bowlers_list.append(state.bowler.model_copy(deep=True))

        # Simple momentum-based win probability estimate
        base = 50 + int((state.crr - 3.5) * 6) - (state.wickets * 4)
        state.win_prob_batting = max(12, min(88, base))

        comm_text = snap.get("commentary", "")
        if comm_text and comm_text != state.live_commentary:
            state.live_commentary = comm_text
            changed = True

        return changed

    async def sync_scorecard_tab(sc_page) -> bool:
        """Read full batting, bowling, and FOW tables from the crex.com /match-scorecard tab."""
        tables = await sc_page.evaluate(
            """() => {
                return Array.from(document.querySelectorAll("table")).map(t =>
                    Array.from(t.querySelectorAll("tr")).map(r =>
                        Array.from(r.querySelectorAll("th, td")).map(c => c.innerText.trim().replace(/\\s+/g, " "))
                    )
                );
            }"""
        )
        if not tables:
            return False

        updated = False
        for tbl in tables:
            if not tbl or len(tbl) < 2:
                continue
            headers = [h.lower() for h in tbl[0]]
            if "batter" in headers and "sr" in headers:
                parsed_bat: list[BatsmanState] = []
                for row in tbl[1:]:
                    if len(row) < 6:
                        continue
                    raw_name = row[0]
                    # Split "Tanzid Hasan c Rickelton b Mulder" if dismissal is present
                    m_dis = re.match(r"^(.+?)\s+((?:c |b |lbw |run out|st |not out).*)$", raw_name, re.I)
                    if m_dis:
                        b_name = m_dis.group(1).strip().upper()
                        b_dis = m_dis.group(2).strip()
                    else:
                        b_name = raw_name.strip().upper()
                        b_dis = "batting"
                    try:
                        parsed_bat.append(
                            BatsmanState(
                                name=b_name,
                                runs=int(row[1]),
                                balls=int(row[2]),
                                fours=int(row[3]),
                                sixes=int(row[4]),
                                strike_rate=float(row[5]),
                                on_strike=(b_name == state.striker.name),
                                dismissal=b_dis,
                            )
                        )
                    except ValueError:
                        continue
                if parsed_bat:
                    state.batters_list = parsed_bat
                    state.batting_xi = [b.name for b in parsed_bat]
                    updated = True

            elif "bowler" in headers and ("er" in headers or "econ" in headers):
                parsed_bowl: list[BowlerState] = []
                for row in tbl[1:]:
                    if len(row) < 6:
                        continue
                    try:
                        parsed_bowl.append(
                            BowlerState(
                                name=row[0].strip().upper(),
                                overs=row[1].strip(),
                                maidens=int(row[2]),
                                runs_conceded=int(row[3]),
                                wickets=int(row[4]),
                                economy=float(row[5]),
                            )
                        )
                    except ValueError:
                        continue
                if parsed_bowl:
                    state.bowlers_list = parsed_bowl
                    state.bowling_xi = [bw.name for bw in parsed_bowl]
                    updated = True

            elif "batter" in headers and "score" in headers and "overs" in headers:
                parsed_fow = [
                    f"{row[1]} • {row[0]} ({row[2]})"
                    for row in tbl[1:]
                    if len(row) >= 3
                ]
                if parsed_fow:
                    state.fall_of_wickets = parsed_fow
                    updated = True

        return updated

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        sc_page = None
        if "crex.com" in url:
            sc_page = await browser.new_page()

        async def on_dom_mutation(snap: dict[str, str]) -> None:
            await update_queue.put(snap)

        await page.expose_function("pyOnDomMutation", on_dom_mutation)

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Switch crex.com commentary to Hindi if the language button is present
            try:
                hindi_btn = page.locator("text=हिन्दी").first
                if await hindi_btn.count() > 0:
                    await hindi_btn.click(timeout=2500)
            except Exception:
                pass

            # Watch live DOM mutations in-place so the page never needs to reload
            await page.evaluate(
                """(sel) => {
                    let timer = null;
                    const read = (q) => {
                        const el = q ? document.querySelector(q) : null;
                        return el ? el.innerText.trim() : "";
                    };
                    const readList = (q) => {
                        if (!q) return "";
                        return Array.from(document.querySelectorAll(q))
                            .map((e) => e.innerText.trim())
                            .filter(Boolean)
                            .join("|");
                    };
                    const emit = () => {
                        window.pyOnDomMutation({
                            score: read(sel.score),
                            overs: read(sel.overs),
                            status: read(sel.status),
                            balls: readList(sel.balls),
                            team: read(sel.team),
                            crr: read(sel.crr),
                            title: read("h1.name-wrapper"),
                            players: Array.from(document.querySelectorAll(".batsmen-career-wrapper"))
                                .map((e) => e.innerText.trim().replace(/\\s+/g, " "))
                                .join("||"),
                            overs_slides: Array.from(document.querySelectorAll(".overs-slide"))
                                .slice(-8)
                                .map((e) => e.innerText.trim().replace(/\\s+/g, " "))
                                .join("||"),
                            last_wkt: read("[class*='last-w'], [class*='wicket']"),
                            pship: read("[class*='partner']"),
                            commentary: (() => {
                                const cards = Array.from(document.querySelectorAll(".cm-b-roundcard"));
                                for (const c of cards) {
                                    const t = (c.innerText || "").trim().replace(/\\s+/g, " ");
                                    if (t.length > 28) return t;
                                }
                                return "";
                            })(),
                        });
                    };
                    const observer = new MutationObserver(() => {
                        clearTimeout(timer);
                        timer = setTimeout(emit, 120);
                    });
                    observer.observe(document.body, {
                        childList: true,
                        subtree: true,
                        characterData: true,
                    });
                }""",
                selectors,
            )

            # Initial snapshot
            initial = await extract_snapshot(page)
            if apply_snapshot(initial):
                await on_update(state)

            if sc_page is not None:
                base_url = url.rstrip("/").removesuffix("/match-scorecard").removesuffix("/match-details")
                try:
                    await sc_page.goto(f"{base_url}/match-details", wait_until="domcontentloaded", timeout=30000)
                    await asyncio.sleep(1.5)
                    details = await sc_page.evaluate(
                        """() => {
                            const lines = document.body.innerText.split(/\\n+/).map(s => s.trim()).filter(Boolean);
                            const idx = lines.findIndex(l => /News/i.test(l));
                            const slice = idx >= 0 ? lines.slice(idx + 1, idx + 8) : [];
                            return { slice };
                        }"""
                    )
                    sl = details.get("slice", [])
                    if len(sl) >= 4 and not any("theme" in s.lower() or "language" in s.lower() for s in sl[:4]):
                        state.series_name = sl[1]
                        state.match_date = sl[2]
                        state.venue = sl[3]
                except Exception as exc:
                    print(f"[playwright:details] init error: {exc}")

                sc_url = f"{base_url}/match-scorecard"
                try:
                    await sc_page.goto(sc_url, wait_until="domcontentloaded", timeout=30000)
                    await asyncio.sleep(2.0)
                    if await sync_scorecard_tab(sc_page):
                        await on_update(state)
                    # Also grab bowling team's full 11 from their innings tab if available
                    if len(state.bowling_xi) < 11 and state.bowling_team:
                        try:
                            opp_btn = sc_page.locator(f"button:has-text('{state.bowling_team}')").first
                            if await opp_btn.count() > 0:
                                await opp_btn.click(timeout=3000)
                                await asyncio.sleep(1.5)
                                opp_names = await sc_page.evaluate(
                                    """() => {
                                        const tbl = document.querySelector("table");
                                        if (!tbl) return [];
                                        return Array.from(tbl.querySelectorAll("tr")).slice(1).map(r => {
                                            const c = r.querySelector("td");
                                            return c ? c.innerText.trim().split(/\\s+(?:c |b |lbw |run out|st |not out)/i)[0].trim().toUpperCase() : "";
                                        }).filter(Boolean);
                                    }"""
                                )
                                if opp_names:
                                    state.bowling_xi = opp_names[:11]
                                    await on_update(state)
                                # Switch back to latest innings tab
                                btns = sc_page.locator("button:has-text('Innings')")
                                if await btns.count() > 0:
                                    await btns.last.click(timeout=3000)
                                    await asyncio.sleep(1.0)
                        except Exception:
                            pass
                except Exception as exc:
                    print(f"[playwright:scorecard] init error: {exc}")

            last_sc_sync = asyncio.get_running_loop().time()

            while True:
                try:
                    snap = await asyncio.wait_for(update_queue.get(), timeout=poll_interval)
                except asyncio.TimeoutError:
                    snap = await extract_snapshot(page)

                changed_now = apply_snapshot(snap)
                now = asyncio.get_running_loop().time()
                if sc_page is not None and (changed_now or now - last_sc_sync >= 12.0):
                    last_sc_sync = now
                    try:
                        if await sync_scorecard_tab(sc_page):
                            changed_now = True
                    except Exception:
                        pass

                if changed_now:
                    await on_update(state)
        finally:
            await browser.close()


def get_source_mode() -> str:
    """Determine active data source from environment variables."""
    if os.getenv("CRICAPI_KEY"):
        return "cricapi"
    if os.getenv("SCRAPE_URL"):
        return "playwright"
    return "simulator"
