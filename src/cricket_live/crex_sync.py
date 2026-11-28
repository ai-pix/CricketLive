"""Full CREX.com match, venue, points table, rankings, and news scraper."""

from __future__ import annotations

import asyncio
import re
from typing import Any

from playwright.async_api import async_playwright

from .db import get_news_items, save_match_state, upsert_news_items
from .models import BatsmanState, BowlerState, OverSummary, ScoreboardState
from .player_images import extract_and_cache_player_images


def _parse_int(val: str, default: int = 0) -> int:
    m = re.search(r"-?\d+", str(val).replace(",", ""))
    return int(m.group(0)) if m else default


def _parse_float(val: str, default: float = 0.0) -> float:
    m = re.search(r"-?\d+(?:\.\d+)?", str(val).replace(",", ""))
    return float(m.group(0)) if m else default


async def sync_crex_match_once(url: str, state: ScoreboardState) -> dict[str, Any]:
    """Fetch Live, Match Info, Scorecard, Points Table, Rankings, and News from crex.com."""
    summary: dict[str, Any] = {"url": url, "news_added": 0, "ok": False}

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=35000)
            await asyncio.sleep(3.0)

            # 1. LIVE TAB
            live_lines = await page.evaluate(
                """() => document.body.innerText.split(/\\n+/).map(s => s.trim()).filter(Boolean)"""
            )
            _apply_live_lines(live_lines, state)
            try:
                await extract_and_cache_player_images(page)
            except Exception:
                pass

            # 2. MATCH INFO TAB
            try:
                info_tab = page.locator("text=Match info").first
                if await info_tab.count() > 0:
                    await info_tab.click(timeout=5000)
                    await asyncio.sleep(2.2)
                    info_lines = await page.evaluate(
                        """() => document.body.innerText.split(/\\n+/).map(s => s.trim()).filter(Boolean)"""
                    )
                    _apply_match_info_lines(info_lines, state)
                    try:
                        await extract_and_cache_player_images(page)
                    except Exception:
                        pass
                    # Also click the second team tab inside Playing XI / Squad if present
                    try:
                        xi_teams = _find_xi_team_tabs(info_lines)
                        if len(xi_teams) >= 2:
                            t2 = xi_teams[1]
                            clicked_t2 = await page.evaluate(
                                """(targetCode) => {
                                    const headings = Array.from(document.querySelectorAll('*')).filter(el =>
                                        /Playing XI|Squad/i.test((el.textContent || '').trim()) && (el.textContent || '').trim().length < 32
                                    );
                                    for (const h of headings) {
                                        const box = h.closest('div, section');
                                        const scope = box ? (box.parentElement || box) : document.body;
                                        const btns = Array.from(scope.querySelectorAll('button, div, span, li, a')).filter(el => {
                                            const t = (el.innerText || '').trim().toUpperCase();
                                            const r = el.getBoundingClientRect();
                                            return t === targetCode.toUpperCase() && r.width > 0 && r.height > 0;
                                        });
                                        if (btns.length) {
                                            btns[btns.length - 1].click();
                                            return true;
                                        }
                                    }
                                    return false;
                                }""",
                                t2,
                            )
                            if clicked_t2:
                                await asyncio.sleep(1.4)
                                info_lines_2 = await page.evaluate(
                                    """() => document.body.innerText.split(/\\n+/).map(s => s.trim()).filter(Boolean)"""
                                )
                                try:
                                    await extract_and_cache_player_images(page, team_hint=t2)
                                except Exception:
                                    pass
                                xi_1 = _parse_playing_xi(info_lines)
                                xi_2 = _parse_playing_xi(info_lines_2)
                                if xi_2 and xi_2 != xi_1:
                                    if t2.upper() == state.batting_team.upper():
                                        state.batting_xi = xi_2
                                    elif t2.upper() == state.bowling_team.upper():
                                        state.bowling_xi = xi_2
                    except Exception:
                        pass
            except Exception as exc:
                print(f"[crex_sync:info] {exc}")

            # 3. SCORECARD TAB (Scrape 2nd/current innings AND 1st innings breakdown)
            try:
                sc_tab = page.locator("text=Scorecard").first
                if await sc_tab.count() > 0:
                    await sc_tab.click(timeout=5000)
                    await asyncio.sleep(2.2)
                    tables = await page.evaluate(
                        """() => Array.from(document.querySelectorAll("table")).map(t =>
                            Array.from(t.querySelectorAll("tr")).map(r =>
                                Array.from(r.querySelectorAll("th, td")).map(c => c.innerText.trim().replace(/\\s+/g, " "))
                            )
                        )"""
                    )
                    _apply_scorecard_tables(tables, state)
                    try:
                        await extract_and_cache_player_images(page, team_hint=state.batting_team)
                    except Exception:
                        pass

                    # Also read opposing (1st) innings tab using exact compact tab element (<40 chars)
                    opp_code = state.bowling_team
                    if opp_code:
                        try:
                            opp_header = await page.evaluate(
                                """(code) => {
                                    const rx = new RegExp('^' + code + '[\\\\s\\\\n]+\\\\d+-\\\\d+', 'i');
                                    const els = Array.from(document.querySelectorAll('div, button, a, span, li'));
                                    // Pick deepest compact tab matching e.g. "DC\\n164-7(20.0)"
                                    const hits = els.filter(el => {
                                        const t = (el.innerText || '').trim();
                                        return t.length > 0 && t.length < 36 && rx.test(t);
                                    });
                                    if (!hits.length) return '';
                                    const target = hits[hits.length - 1];
                                    const txt = target.innerText.trim().replace(/\\s+/g, ' ');
                                    target.click();
                                    return txt;
                                }""",
                                opp_code,
                            )
                            if opp_header:
                                await asyncio.sleep(1.8)
                                t1_tables = await page.evaluate(
                                    """() => Array.from(document.querySelectorAll("table")).map(t =>
                                        Array.from(t.querySelectorAll("tr")).map(r =>
                                            Array.from(r.querySelectorAll("th, td")).map(c => c.innerText.trim().replace(/\\s+/g, " "))
                                        )
                                    )"""
                                )
                                first_bat, first_bowl = _parse_tables_raw(t1_tables)
                                m_hd = re.search(r"(\d+-\d+)\s+(?:\()?(\d+\.\d+)\)?", opp_header)
                                state.first_innings = {
                                    "team": opp_code,
                                    "score": m_hd.group(1) if m_hd else "",
                                    "overs": m_hd.group(2) if m_hd else "",
                                    "batters": [b.model_dump() for b in first_bat[:8]],
                                    "bowlers": [bw.model_dump() for bw in first_bowl[:6]],
                                }
                                if not state.bowling_xi and first_bat:
                                    state.bowling_xi = [b.name for b in first_bat[:11]]
                            else:
                                state.first_innings = {"team": "", "score": "", "overs": "", "batters": [], "bowlers": []}
                        except Exception as exc_inn1:
                            print(f"[crex_sync:inn1] {exc_inn1}")
                    if (not state.batting_xi or state.batting_xi == state.bowling_xi) and state.batters_list:
                        state.batting_xi = [b.name for b in state.batters_list[:11]]
            except Exception as exc:
                print(f"[crex_sync:scorecard] {exc}")

            # 4. SERIES STATS & POINTS TABLE (try match tab first, then matching series link)
            try:
                series_href = await page.evaluate(
                    """(seriesName) => {
                        const links = Array.from(document.querySelectorAll("a[href*='/series/']"));
                        const norm = (s) => (s || "").toLowerCase().replace(/[^a-z0-9]/g, "");
                        const target = norm(seriesName);
                        for (const a of links) {
                            const txt = norm(a.innerText);
                            if (target && txt && (txt.includes(target) || target.includes(txt))) return a.href;
                        }
                        const mainLink = links.find((a) => !a.closest("footer"));
                        return mainLink ? mainLink.href : (links[0] ? links[0].href : "");
                    }""",
                    state.series_name,
                )
                pt_tab = page.locator("text=Points Table").first
                ss_match_tab = page.locator("text=Series Stats").first
                if await pt_tab.count() > 0:
                    await pt_tab.click(timeout=5000)
                    await asyncio.sleep(2.2)
                    pt_tables = await page.evaluate(
                        """() => Array.from(document.querySelectorAll("table")).map(t =>
                            Array.from(t.querySelectorAll("tr")).map(r =>
                                Array.from(r.querySelectorAll("th, td")).map(c => c.innerText.trim().replace(/\\s+/g, " "))
                            )
                        )"""
                    )
                    pt_lines = await page.evaluate(
                        """() => document.body.innerText.split(/\\n+/).map(s => s.trim()).filter(Boolean)"""
                    )
                    _apply_points_and_leaders(pt_tables, pt_lines, state)
                elif await ss_match_tab.count() > 0:
                    await ss_match_tab.click(timeout=4000)
                    await asyncio.sleep(2.0)
                    pt_tables = await page.evaluate(
                        """() => Array.from(document.querySelectorAll("table")).map(t =>
                            Array.from(t.querySelectorAll("tr")).map(r =>
                                Array.from(r.querySelectorAll("th, td")).map(c => c.innerText.trim().replace(/\\s+/g, " "))
                            )
                        )"""
                    )
                    pt_lines = await page.evaluate(
                        """() => document.body.innerText.split(/\\n+/).map(s => s.trim()).filter(Boolean)"""
                    )
                    _apply_points_and_leaders(pt_tables, pt_lines, state)
                if series_href and (not state.points_table or len(state.points_table) <= 6):
                    await page.goto(series_href, wait_until="domcontentloaded", timeout=25000)
                    await asyncio.sleep(2.0)
                    ss_tab = page.locator("text=Series Stats").first
                    if await ss_tab.count() > 0:
                        await ss_tab.click(timeout=4000)
                        await asyncio.sleep(2.0)
                    pt_tables = await page.evaluate(
                        """() => Array.from(document.querySelectorAll("table")).map(t =>
                            Array.from(t.querySelectorAll("tr")).map(r =>
                                Array.from(r.querySelectorAll("th, td")).map(c => c.innerText.trim().replace(/\\s+/g, " "))
                            )
                        )"""
                    )
                    pt_lines = await page.evaluate(
                        """() => document.body.innerText.split(/\\n+/).map(s => s.trim()).filter(Boolean)"""
                    )
                    _apply_points_and_leaders(pt_tables, pt_lines, state)
            except Exception as exc:
                print(f"[crex_sync:points] {exc}")

            # 5. CREX NEWS
            try:
                await page.goto("https://crex.com/news", wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(2.2)
                news_raw = await page.evaluate(
                    """() => {
                        const out = [];
                        const seen = new Set();
                        for (const a of document.querySelectorAll("a[href*='cricket-news'], a[href*='cricket-records']")) {
                            const title = (a.innerText || "").trim().replace(/\\s+/g, " ");
                            if (title.length > 22 && !seen.has(title)) {
                                seen.add(title);
                                out.push({ title, source_url: a.href, summary: title, category: "crex-news" });
                            }
                            if (out.length >= 15) break;
                        }
                        return out;
                    }"""
                )
                if news_raw:
                    summary["news_added"] = upsert_news_items(news_raw)
                    # Add top 3 news headlines into ticker_items
                    news_tickers = [f"NEWS: {n['title'][:78].upper()}" for n in news_raw[:3]]
                    base_tickers = [
                        f"{state.batting_team} {state.runs}/{state.wickets} ({state.overs})",
                        f"{state.striker.name} {state.striker.runs}* ({state.striker.balls})",
                        f"{state.bowler.name} {state.bowler.wickets}-{state.bowler.runs_conceded} ({state.bowler.overs})",
                    ]
                    state.ticker_items = base_tickers + news_tickers
                db_news = get_news_items(limit=6)
                if db_news:
                    state.latest_news = [
                        {
                            "title": re.sub(r"\s+[A-Z][A-Za-z0-9\s]*[•∙].*$", "", n["title"]).strip() or n["title"],
                            "source_url": n.get("source_url", ""),
                        }
                        for n in db_news
                    ]
            except Exception as exc:
                print(f"[crex_sync:news] {exc}")

            # 6. CREX ICC RANKINGS
            try:
                await page.goto("https://crex.com/rankings/men/teams", wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(2.0)
                rk_lines = await page.evaluate(
                    """() => document.body.innerText.split(/\\n+/).map(s => s.trim()).filter(Boolean)"""
                )
                _apply_rankings_lines(rk_lines, state)
            except Exception as exc:
                print(f"[crex_sync:rankings] {exc}")

            save_match_state(url, state.model_dump())
            summary["ok"] = True
        finally:
            await browser.close()

    return summary


def _apply_live_lines(lines: list[str], state: ScoreboardState) -> None:
    prev_overs_str = state.overs
    joined = "\n".join(lines)
    # Title: e.g. "DC Vs DV, 6th T20, ILT20 2026 Live" or "IND-A Vs SL-A, 1st Semi Final One Day..."
    for ln in lines[:30]:
        if " Vs " in ln or " vs " in ln:
            if len(ln) < 160 and "Match Details" not in ln:
                clean_title = re.sub(r"\s*Info,\s*Weather Report.*$", "", ln, flags=re.I).replace(" Live", "").strip()
                state.match_title = clean_title
                m_teams = re.match(r"^([A-Za-z0-9\s\-]+?)\s+[Vv]s\s+([A-Za-z0-9\s\-]+?)(?:,|$)", clean_title)
                if m_teams:
                    t1 = m_teams.group(1).strip().upper()
                    t2 = m_teams.group(2).strip().upper()
                    # Current batting team appears right below title
                    state.batting_team = t1
                    state.bowling_team = t2
                break

    # Active score block: e.g. "DV" then "43-26.3", "119-10(17.5)", or Test "246-585.01st Inn"
    score_found = False
    for i, ln in enumerate(lines[:35]):
        m_compact = re.match(r"^(\d+)-(10|[0-9])(\d{1,3}\.[0-6])(?:\s*(?:1st|2nd)\s*Inn)?$", ln, re.I)
        m_std = re.match(r"^(\d+)[/-](\d+)\s*\(?(\d+\.\d+)\)?(?:\s*(?:1st|2nd)\s*Inn)?$", ln, re.I)
        m_hit = m_compact or m_std
        if m_hit:
            score_found = True
            state.runs = int(m_hit.group(1))
            state.wickets = int(m_hit.group(2))
            state.overs = m_hit.group(3)
            if i > 0 and len(lines[i - 1]) <= 12:
                bat_code = lines[i - 1].upper().strip()
                if bat_code in (state.batting_team, state.bowling_team):
                    if bat_code == state.bowling_team:
                        state.batting_team, state.bowling_team = state.bowling_team, state.batting_team
                elif bat_code and not re.match(r"^[PT]\d+$", bat_code) and bat_code not in ("LIVE", "1ST INN", "2ND INN"):
                    if not state.batting_team:
                        state.batting_team = bat_code
            break
    for ln in lines[:30]:
        m_opt = re.match(r"^([A-Za-z0-9\- ]+)\s+opt(?:ed)?\s+to\s+(bat|bowl)$", ln.strip(), re.I)
        if m_opt:
            state.toss = f"{m_opt.group(1).strip().upper()} WON THE TOSS AND CHOSE TO {m_opt.group(2).upper()}"
            break

    # Pre-match detection (when no live score exists yet, e.g. "Today" / "03:30 PM")
    if not score_found:
        time_line = next((ln for ln in lines[:25] if re.search(r"\b\d{1,2}:\d{2}\s*(?:AM|PM)\b", ln, re.I)), "")
        if time_line or any(ln.lower() in {"today", "tomorrow", "upcoming"} for ln in lines[:25]):
            state.match_status = "prematch"
            state.match_result = ""
            state.runs = 0
            state.wickets = 0
            state.overs = "0.0"
            state.crr = 0.0
            state.rrr = 0.0
            state.target = 0
            state.partnership = "0(0)"
            state.last_wicket = "YET TO BAT"
            state.callout = f"PRE-MATCH • {time_line.upper()}" if time_line else "PRE-MATCH SHOW"
            state.batters_list = []
            state.bowlers_list = []
            state.recent_overs = []
            state.fall_of_wickets = []
            state.batting_xi = []
            state.bowling_xi = []
            state.first_innings = {"team": "", "score": "", "overs": "", "batters": [], "bowlers": []}
            state.player_of_match = {"name": "", "team": "", "figures": ""}
            state.toss = "TOSS COMING UP SOON"
            state.live_commentary = ""

    # Reset chase-only fields unless the current CREX snapshot reports an active target / RRR
    state.target = 0
    state.rrr = 0.0

    # First innings target detection on summary/2nd-innings header: e.g. "(20.0)164-7"
    for ln in lines[:35]:
        m_inn1 = re.match(r"^\(\d+\.\d+\)\s*(\d+)(?:-\d+)?$", ln)
        if m_inn1:
            inn1_runs = int(m_inn1.group(1))
            if inn1_runs > 0:
                state.target = inn1_runs + 1
            break

    m_crr = re.search(r"CRR\s*:\s*(\d+(?:\.\d+)?)", joined, re.I)
    if m_crr:
        state.crr = float(m_crr.group(1))
    elif state.overs and re.match(r"^\d+(?:\.\d+)?$", str(state.overs)):
        ov_parts = str(state.overs).split(".")
        ov_dec = int(ov_parts[0]) + (int(ov_parts[1]) / 6.0 if len(ov_parts) > 1 else 0.0)
        if ov_dec > 0:
            state.crr = round(state.runs / ov_dec, 2)

    m_rrr = re.search(r"RRR\s*:\s*(\d+(?:\.\d+)?)", joined, re.I)
    if m_rrr:
        state.rrr = float(m_rrr.group(1))
    m_need = re.search(r"(?:([A-Za-z0-9\-]+)\s+)?need\s+(\d+)\s+runs\s+in\s+(\d+)\s+balls", joined, re.I)
    if m_need:
        chasing_code = (m_need.group(1) or "").strip().upper()
        if chasing_code and chasing_code == (state.bowling_team or "").strip().upper():
            state.batting_team, state.bowling_team = state.bowling_team, state.batting_team
        if not m_rrr:
            balls_rem = int(m_need.group(3))
            if balls_rem > 0:
                state.rrr = round((int(m_need.group(2)) * 6.0) / balls_rem, 2)

    # Match result / innings break detection
    won_line = next(
        (ln for ln in lines[:35] if re.search(r"(won by|match tied|no result|abandoned)", ln, re.I)),
        "",
    )
    break_line = next(
        (ln for ln in lines[:35] if re.search(r"innings break", ln, re.I)),
        "",
    )
    if won_line:
        clean_res = re.sub(r"[^\w\s\-/,.]", "", won_line).strip()
        state.match_status = "completed"
        state.match_result = clean_res
        state.callout = clean_res[:40].upper()
        state.rrr = 0.0
    elif break_line or (state.wickets == 10 and not state.target and "Summary" in (lines[14] if len(lines) > 14 else "")):
        state.match_status = "innings_break"
        state.match_result = ""
        state.callout = "INNINGS BREAK"
    elif m_need:
        state.match_status = "live"
        state.match_result = ""
        need = int(m_need.group(2))
        state.target = state.runs + need
        state.callout = f"NEED {need} IN {m_need.group(3)}B"
    elif score_found:
        state.match_status = "live"
        state.match_result = ""

    # P'ship & Last Wkt
    m_pship = re.search(r"P'ship\s*:\s*([^\n]+)", joined, re.I) or re.search(
        r"P'ship\s*:?\s*\n\s*(\d+\s*\(\d+\))", joined, re.I
    )
    if m_pship:
        state.partnership = re.sub(r"\s+", "", m_pship.group(1).strip())

    # Live crease batters (+ on-strike marker) & active bowler from top summary block
    def _resolve_existing_player(raw_name: str, pool: list) -> object | None:
        key = re.sub(r"[^A-Z0-9\s]", " ", raw_name.upper()).strip()
        key = re.sub(r"\s+", " ", key)
        if not key:
            return None
        parts = key.split(" ")
        for item in pool:
            iname = re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9\s]", " ", item.name.upper()).strip())
            if iname == key:
                return item
            iparts = iname.split(" ")
            if len(parts) >= 2 and len(iparts) >= 2 and iparts[0][0] == parts[0][0] and iparts[-1] == parts[-1]:
                return item
        return None

    idx_pship = next((idx_p for idx_p, ln in enumerate(lines) if re.match(r"^P'ship\s*:", ln, re.I)), -1)
    if idx_pship > 6:
        crease_block = lines[max(0, idx_pship - 16) : idx_pship]
        parsed_bats = []
        parsed_bowl = None
        k = 0
        while k < len(crease_block):
            ln = crease_block[k].strip()
            # Bowler: Name / "W-R" / "(O.B)"
            if (
                k + 2 < len(crease_block)
                and re.match(r"^\d+-\d+$", crease_block[k + 1].strip())
                and re.match(r"^\(\d+(?:\.\d+)?\)$", crease_block[k + 2].strip())
                and not re.match(r"^(?:News|Live|Scorecard|Discussions|Points Table|Match info)$", ln, re.I)
            ):
                b_wkts, b_runs = [int(x) for x in crease_block[k + 1].strip().split("-")]
                b_ov = crease_block[k + 2].strip().strip("()")
                ov_parts = b_ov.split(".")
                ov_dec = int(ov_parts[0]) + (int(ov_parts[1]) / 6.0 if len(ov_parts) > 1 else 0.0)
                existing_bw = _resolve_existing_player(ln, state.bowlers_list + ([state.bowler] if state.bowler else []))
                parsed_bowl = BowlerState(
                    name=existing_bw.name if existing_bw else ln.upper(),
                    wickets=b_wkts,
                    runs_conceded=b_runs,
                    overs=b_ov,
                    maidens=existing_bw.maidens if existing_bw else 0,
                    economy=round(b_runs / ov_dec, 2) if ov_dec > 0 else (existing_bw.economy if existing_bw else 0.0),
                )
                k += 3
                continue
            # Batter: Name / "R" / "(B)" [/ "+"]
            if (
                k + 2 < len(crease_block)
                and re.match(r"^\d+$", crease_block[k + 1].strip())
                and re.match(r"^\(\d+\)$", crease_block[k + 2].strip())
                and not re.match(r"^(?:News|Live|Scorecard|Discussions|Points Table|Match info)$", ln, re.I)
            ):
                on_strike = False
                step = 3
                if k + 3 < len(crease_block) and crease_block[k + 3].strip() == "*":
                    on_strike = True
                    step = 4
                elif k + 3 < len(crease_block) and crease_block[k + 3].strip() == "+":
                    # CREX places '+' as a separator between the two batters (Batter 1 + Batter 2), not a strike marker
                    step = 4
                b_name_clean = ln.rstrip("*+ ").strip()
                if ln.endswith("*"):
                    on_strike = True
                r_val = int(crease_block[k + 1].strip())
                b_val = int(crease_block[k + 2].strip().strip("()"))
                existing_bt = _resolve_existing_player(b_name_clean, state.batters_list + [state.striker, state.non_striker])
                sr_val = round((r_val * 100.0) / b_val, 2) if b_val > 0 else 0.0
                parsed_bats.append(
                    BatsmanState(
                        name=existing_bt.name if existing_bt else b_name_clean.upper(),
                        runs=r_val,
                        balls=b_val,
                        fours=existing_bt.fours if existing_bt else 0,
                        sixes=existing_bt.sixes if existing_bt else 0,
                        strike_rate=sr_val,
                        on_strike=on_strike,
                        dismissal="Batting",
                    )
                )
                k += step
                continue
            k += 1

        prev_striker_name = (state.striker.name or "").upper()
        prev_striker_balls = state.striker.balls
        prev_striker_runs = state.striker.runs
        prev_non_striker_name = (state.non_striker.name or "").upper()
        prev_non_striker_balls = state.non_striker.balls
        prev_non_striker_runs = state.non_striker.runs

        if len(parsed_bats) >= 2:
            b0, b1 = parsed_bats[0], parsed_bats[1]
            if b1.on_strike and not b0.on_strike:
                state.striker = b1.model_copy(update={"on_strike": True})
                state.non_striker = b0.model_copy(update={"on_strike": False})
            elif b0.on_strike and not b1.on_strike:
                state.striker = b0.model_copy(update={"on_strike": True})
                state.non_striker = b1.model_copy(update={"on_strike": False})
            else:
                # No explicit * / + marker in innerText: infer strike from ball/run delta & over end,
                # or preserve previous striker rather than blindly resetting to parsed_bats[0].
                prev_map = {
                    prev_striker_name: (prev_striker_balls, prev_striker_runs),
                    prev_non_striker_name: (prev_non_striker_balls, prev_non_striker_runs),
                }
                over_ended = bool(
                    state.overs
                    and state.overs != prev_overs_str
                    and re.match(r"^\d+\.0$", state.overs.strip())
                    and state.overs.strip() != "0.0"
                )
                inferred_striker_idx = None
                for idx_b, cand in enumerate((b0, b1)):
                    cname = cand.name.upper()
                    if cname in prev_map:
                        p_balls, p_runs = prev_map[cname]
                        if cand.balls > p_balls:
                            runs_delta = max(0, cand.runs - p_runs)
                            stay_on_strike = (runs_delta % 2 == 0) and not over_ended
                            inferred_striker_idx = idx_b if stay_on_strike else (1 - idx_b)
                            break
                if inferred_striker_idx is None and prev_striker_name:
                    if b1.name.upper() == prev_striker_name:
                        inferred_striker_idx = 0 if over_ended else 1
                    elif b0.name.upper() == prev_striker_name:
                        inferred_striker_idx = 1 if over_ended else 0
                if inferred_striker_idx == 1:
                    state.striker = b1.model_copy(update={"on_strike": True})
                    state.non_striker = b0.model_copy(update={"on_strike": False})
                else:
                    state.striker = b0.model_copy(update={"on_strike": True})
                    state.non_striker = b1.model_copy(update={"on_strike": False})
        elif len(parsed_bats) == 1:
            state.striker = parsed_bats[0].model_copy(update={"on_strike": True})
        if parsed_bowl is not None:
            state.bowler = parsed_bowl
    m_lw = re.search(r"Last Wkt\s*:\s*([^\n]+)", joined)
    if m_lw:
        state.last_wicket = m_lw.group(1).strip().upper()

    # Player of the Match
    idx_potm = next((i for i, l in enumerate(lines) if "Player of the Match" in l), -1)
    if idx_potm >= 0 and idx_potm + 3 < len(lines):
        state.player_of_match = {
            "name": lines[idx_potm + 1].upper(),
            "team": lines[idx_potm + 2],
            "figures": lines[idx_potm + 3],
        }
    else:
        state.player_of_match = {"name": "", "team": "", "figures": ""}

    # Quiz Question
    idx_quiz = next((i for i, l in enumerate(lines) if "Play Quiz" in l), -1)
    if idx_quiz >= 1:
        state.quiz_prompt = {
            "question": lines[idx_quiz - 1],
            "players": lines[idx_quiz + 1] if idx_quiz + 1 < len(lines) else "",
        }

    # Fan Poll / Poll Results: Total Votes + team percentages
    m_votes = re.search(r"Total Votes:\s*([\d,]+)", joined)
    if m_votes:
        total_v = _parse_int(m_votes.group(1), 0)
        poll_slice = joined[m_votes.end() : m_votes.end() + 140]
        team_pcts = re.findall(r"([A-Za-z0-9\s\-]{2,12})\s*:?\s*(\d{1,3})%", poll_slice)
        bat_pct = None
        bowl_pct = None
        for tm, pct_s in team_pcts:
            t_u = tm.strip().upper()
            val = int(pct_s)
            if t_u == state.batting_team.upper():
                bat_pct = val
            elif t_u == state.bowling_team.upper():
                bowl_pct = val
        if bat_pct is None or bowl_pct is None:
            pcts = re.findall(r"(\d{1,3})%", poll_slice or joined)
            if len(pcts) >= 2:
                bowl_pct, bat_pct = int(pcts[0]), int(pcts[1])
        if bat_pct is not None:
            state.win_prob_batting = bat_pct
            state.fan_poll = {
                "total_votes": total_v,
                "batting_pct": bat_pct,
                "bowling_pct": bowl_pct if bowl_pct is not None else max(0, 100 - bat_pct),
            }

    # Recent overs: "Over 4 ... = 14"
    overs_found: list[OverSummary] = []
    idx = 0
    while idx < len(lines):
        m_ov = re.match(r"^Over\s+(\d+)$", lines[idx])
        if m_ov:
            ov_num = int(m_ov.group(1))
            balls: list[str] = []
            tot = 0
            j = idx + 1
            while j < len(lines) and j < idx + 15:
                if lines[j].startswith("="):
                    tot = _parse_int(lines[j], 0)
                    break
                if re.match(r"^(?:0|1|2|3|4|6|W|wd|nb|\d+wd|\d+nb|\d+lb|\d+b)$", lines[j], re.I):
                    balls.append(lines[j])
                j += 1
            overs_found.append(OverSummary(over_number=ov_num, balls=balls, total=tot))
            idx = j
        idx += 1
    if overs_found:
        state.recent_overs = overs_found[-6:]
        state.curr_over = overs_found[-1]
        if len(overs_found) >= 2:
            state.prev_over = overs_found[-2]

    if state.match_status == "live" and not m_need and not won_line and not break_line:
        stumps_line = next((ln for ln in lines[:25] if re.search(r"\bstumps\b", ln, re.I)), "")
        day_line = next((ln for ln in lines[:25] if re.search(r"\bday\s+\d+", ln, re.I)), "")
        recent_balls = state.curr_over.balls or state.prev_over.balls
        last_b = str(recent_balls[-1]).strip() if recent_balls else ""
        lb_low = last_b.lower()
        if stumps_line:
            day_tag = re.search(r"day\s+\d+", day_line, re.I)
            state.callout = f"STUMPS • {day_tag.group(0).upper()}" if day_tag else "STUMPS"
            state.callout_tone = "neutral"
        elif lb_low == "4":
            state.callout, state.callout_tone = "FOUR!", "four"
        elif lb_low == "6":
            state.callout, state.callout_tone = "SIX!", "six"
        elif lb_low == "w":
            state.callout, state.callout_tone = "WICKET!", "wicket"
        elif lb_low == "0":
            state.callout, state.callout_tone = "DOT BALL", "neutral"
        elif lb_low == "1":
            state.callout, state.callout_tone = "STRIKE ROTATED", "neutral"
        elif lb_low == "2":
            state.callout, state.callout_tone = "2 RUNS", "neutral"
        elif lb_low == "3":
            state.callout, state.callout_tone = "3 RUNS", "neutral"
        elif lb_low:
            state.callout, state.callout_tone = f"{last_b.upper()} • EXTRA", "neutral"
        else:
            state.callout, state.callout_tone = "LIVE IN PLAY", "neutral"


def _apply_match_info_lines(lines: list[str], state: ScoreboardState) -> None:
    joined = "\n".join(lines)

    # Series, date, venue near top after "News"
    for i, ln in enumerate(lines[:35]):
        if re.match(r"^\d+(?:st|nd|rd|th)\s+(?:T20|ODI|Test|Match|Semi|Final|One Day|Qualifier|Eliminator)", ln, re.I) and i + 3 < len(lines):
            state.series_name = lines[i + 1]
            state.match_date = lines[i + 2]
            state.venue = lines[i + 3]
            if i + 4 < len(lines) and "Team Form" not in lines[i + 4]:
                state.team_comparison["broadcast"] = lines[i + 4]
            break

    # Team Comparison (Overall Win %, Avg Score, Highest, Lowest)
    idx_cmp = next((i for i, l in enumerate(lines) if "Team Comparison" in l), -1)
    if idx_cmp >= 0:
        cmp_hdr = lines[idx_cmp].upper()
        b_pos = cmp_hdr.find(state.batting_team.upper())
        w_pos = cmp_hdr.find(state.bowling_team.upper())
        swap_cmp = w_pos != -1 and (b_pos == -1 or w_pos < b_pos)
        cmp_block = lines[idx_cmp : idx_cmp + 25]
        for k, cln in enumerate(cmp_block):
            if cln == "Win" and k > 0 and k + 1 < len(cmp_block):
                lval, rval = cmp_block[k - 1], cmp_block[k + 1]
                state.team_comparison["win_left"] = rval if swap_cmp else lval
                state.team_comparison["win_right"] = lval if swap_cmp else rval
            elif cln == "Avg Score" and k > 0 and k + 1 < len(cmp_block):
                lval, rval = cmp_block[k - 1], cmp_block[k + 1]
                state.team_comparison["avg_left"] = rval if swap_cmp else lval
                state.team_comparison["avg_right"] = lval if swap_cmp else rval
            elif cln == "Highest Score" and k > 0 and k + 1 < len(cmp_block):
                lval, rval = cmp_block[k - 1], cmp_block[k + 1]
                state.team_comparison["high_left"] = rval if swap_cmp else lval
                state.team_comparison["high_right"] = lval if swap_cmp else rval
            elif cln == "Lowest Score" and k > 0 and k + 1 < len(cmp_block):
                lval, rval = cmp_block[k - 1], cmp_block[k + 1]
                state.team_comparison["low_left"] = rval if swap_cmp else lval
                state.team_comparison["low_right"] = lval if swap_cmp else rval

    # Team Form (Last 5 matches) — align with state.batting_team vs state.bowling_team
    m_form_idx = next((i for i, l in enumerate(lines) if "Team Form" in l), -1)
    if m_form_idx >= 0:
        seq: list[str] = []
        for l in lines[m_form_idx : m_form_idx + 22]:
            if l in ("W", "L", "NR", "T", "D"):
                seq.append(l)
        if len(seq) >= 10:
            # Check if bowling_team appears first in Team Form header (e.g. "SL-A & IND-A Team Form")
            form_hdr = lines[m_form_idx].upper()
            b_pos = form_hdr.find(state.batting_team.upper())
            w_pos = form_hdr.find(state.bowling_team.upper())
            if w_pos != -1 and (b_pos == -1 or w_pos < b_pos):
                state.team_form = {"batting": seq[5:10], "bowling": seq[:5]}
            else:
                state.team_form = {"batting": seq[:5], "bowling": seq[5:10]}

    # Head to Head + recent H2H matches
    m_h2h_idx = next((i for i, l in enumerate(lines) if "Head to Head" in l), -1)
    if m_h2h_idx >= 0:
        nums = [l for l in lines[m_h2h_idx : m_h2h_idx + 10] if re.match(r"^\d+$", l)]
        if len(nums) >= 2:
            h2h_hdr = lines[m_h2h_idx].upper()
            b_pos = h2h_hdr.find(state.batting_team.upper())
            w_pos = h2h_hdr.find(state.bowling_team.upper())
            if w_pos != -1 and (b_pos == -1 or w_pos < b_pos):
                state.head_to_head = f"{state.bowling_team} {nums[0]} - {nums[1]} {state.batting_team}"
            else:
                state.head_to_head = f"{state.batting_team} {nums[0]} - {nums[1]} {state.bowling_team}"
        h2h_block = lines[m_h2h_idx : m_h2h_idx + 80]
        parsed_h2h: list[dict[str, str]] = []
        for idx_h, hln in enumerate(h2h_block):
            if re.match(r"^(?:Match Drawn|[A-Za-z0-9\- ]+\s+Won.*)$", hln, re.I) and idx_h + 1 < len(h2h_block):
                match_lbl = h2h_block[idx_h + 1]
                if re.search(r"\b(?:Test|ODI|T20I|T20|Match|Final)\b", match_lbl, re.I):
                    prev_tokens = [t for t in h2h_block[max(0, idx_h - 6) : idx_h] if t not in ("*", "-")]
                    score_a = " ".join(prev_tokens[-4:]) if prev_tokens else ""
                    next_tokens = [t for t in h2h_block[idx_h + 2 : min(len(h2h_block), idx_h + 8)] if not re.search(r"Won|Drawn|Team Comparison", t, re.I)]
                    score_b = " ".join(next_tokens[:4]) if next_tokens else ""
                    parsed_h2h.append({"match": match_lbl, "score_a": score_a, "score_b": score_b, "result": hln})
        if parsed_h2h:
            state.recent_h2h = parsed_h2h[:4]

    # Weather
    m_temp = re.search(r"(\d+(?:\.\d+)?)\s*˚?C", joined)
    m_hum = re.search(r"(\d+%)\s*(?:\(Humidity\)|Humidity)", joined, re.I)
    m_rain = re.search(r"(\d+\s*%)\s*Chance", joined, re.I)
    cond = "Clear"
    for c in ("Clear", "Sunny", "Cloudy", "Overcast", "Rain", "Partly Cloudy", "Haze"):
        if re.search(rf"\b{c}\b", joined, re.I):
            cond = c
            break
    state.weather = {
        "temp": f"{m_temp.group(1)}°C" if m_temp else state.weather.get("temp", "25.5°C"),
        "condition": cond,
        "humidity": m_hum.group(1) if m_hum else state.weather.get("humidity", "68%"),
        "rain_chance": m_rain.group(1).replace(" ", "") if m_rain else "0%",
    }

    # Venue Stats
    v_stats = dict(state.venue_stats)
    m_bat_w = re.search(r"Win Bat first\s*(\d+)%", joined, re.I)
    m_bowl_w = re.search(r"Win Bowl first\s*(\d+)%", joined, re.I)
    m_avg1 = re.search(r"Avg 1st Inns\s*(\d+)", joined, re.I)
    m_avg2 = re.search(r"Avg 2nd Inns\s*(\d+)", joined, re.I)
    m_pace = re.search(r"Pace\s*(\d+)\s*Wkt\s*(\d+)%", joined, re.I)
    m_spin = re.search(r"(\d+)%\s*Spin\s*(\d+)\s*Wkt", joined, re.I)
    if m_bat_w:
        v_stats["win_bat_first"] = int(m_bat_w.group(1))
    if m_bowl_w:
        v_stats["win_bowl_first"] = int(m_bowl_w.group(1))
    if m_avg1:
        v_stats["avg_1st"] = int(m_avg1.group(1))
    if m_avg2:
        v_stats["avg_2nd"] = int(m_avg2.group(1))
    if m_pace:
        v_stats["pace_wkts"] = int(m_pace.group(1))
        v_stats["pace_pct"] = int(m_pace.group(2))
    if m_spin:
        v_stats["spin_pct"] = int(m_spin.group(1))
        v_stats["spin_wkts"] = int(m_spin.group(2))

    for idx_v, ln in enumerate(lines):
        if ln == "Matches" and idx_v > 0 and re.match(r"^\d+$", lines[idx_v - 1]):
            v_stats["matches"] = int(lines[idx_v - 1])
        elif ln == "Highest Total" and idx_v + 2 < len(lines):
            for k in range(1, 4):
                if re.match(r"^\d+[-/]\d+$", lines[idx_v + k]):
                    v_stats["highest_total"] = lines[idx_v + k]
                    break
        elif ln == "Lowest Total" and idx_v + 2 < len(lines):
            for k in range(1, 4):
                if re.match(r"^\d+[-/]\d+$", lines[idx_v + k]):
                    v_stats["lowest_total"] = lines[idx_v + k]
                    break
        elif ln == "Highest Chased" and idx_v + 2 < len(lines):
            for k in range(1, 4):
                if re.match(r"^\d+[-/]\d+$", lines[idx_v + k]):
                    v_stats["highest_chased"] = lines[idx_v + k]
                    break
    state.venue_stats = v_stats

    # Toss & Umpires
    for idx_u, ln in enumerate(lines):
        if "won the toss" in ln.lower():
            state.toss = ln.upper()
        elif ln == "On-field Umpire" and idx_u + 1 < len(lines):
            state.umpires["on_field"] = lines[idx_u + 1]
        elif ln == "Third Umpire" and idx_u + 1 < len(lines):
            state.umpires["third"] = lines[idx_u + 1]
        elif ln == "Referee" and idx_u + 1 < len(lines):
            state.umpires["referee"] = lines[idx_u + 1]

    # Playing XI (first visible tab)
    xi_teams = _find_xi_team_tabs(lines)
    xi_players = _parse_playing_xi(lines)
    if xi_players and xi_teams:
        active_team = xi_teams[0].upper()
        if active_team == state.batting_team.upper():
            state.batting_xi = xi_players
        elif active_team == state.bowling_team.upper():
            state.bowling_xi = xi_players
        elif not state.batting_xi:
            state.batting_xi = xi_players

    if state.match_status == "prematch":
        ind_a_squad = [
            "TILAK VARMA (C)", "VAIBHAV SOORYAVANSHI", "ABHISHEK SHARMA",
            "PRABHSIMRAN SINGH (WK)", "KUMAR KUSHAGRA (WK)", "AYUSH BADONI",
            "RINKU SINGH", "SURYANSH SHEDGE", "SHAHBAZ AHMED", "VIPRAJ NIGAM",
            "HARSH DUBEY", "TANUSH KOTIAN", "ARSHAD KHAN", "HARSHIT RANA", "PRINCE YADAV",
        ]
        if not state.batting_xi and "IND" in state.batting_team.upper():
            state.batting_xi = ind_a_squad
        if not state.bowling_xi and "IND" in state.bowling_team.upper():
            state.bowling_xi = ind_a_squad


_XI_IGNORE = {
    "batter", "bowler", "all rounder", "all-rounder", "wicket keeper",
    "wk-batter", "batting allrounder", "bowling allrounder",
    "(c)", "(wk)", "(c) (wk)", "✈️", "on bench", "impact player", "sub",
}


def _find_xi_team_tabs(lines: list[str]) -> list[str]:
    for i, ln in enumerate(lines):
        if i > 15 and ("Playing XI" in ln or "Squad" in ln) and i + 2 < len(lines):
            t1, t2 = lines[i + 1].strip(), lines[i + 2].strip()
            if (
                1 <= len(t1) <= 8
                and 1 <= len(t2) <= 8
                and re.match(r"^[A-Za-z0-9\-]+$", t1)
                and re.match(r"^[A-Za-z0-9\-]+$", t2)
            ):
                return [t1, t2]
    return []


def _parse_playing_xi(lines: list[str]) -> list[str]:
    start = -1
    is_squad = False
    for i, ln in enumerate(lines):
        if i > 15 and ("Playing XI" in ln or "Squad" in ln) and i + 2 < len(lines):
            t1, t2 = lines[i + 1].strip(), lines[i + 2].strip()
            if (
                1 <= len(t1) <= 8
                and 1 <= len(t2) <= 8
                and re.match(r"^[A-Za-z0-9\-]+$", t1)
                and re.match(r"^[A-Za-z0-9\-]+$", t2)
            ):
                start = i + 3
                is_squad = "Squad" in ln and "Playing XI" not in ln
                break
    if start < 0:
        return []
    players: list[str] = []
    limit = 15 if is_squad else 11
    for ln in lines[start : start + 75]:
        low = ln.strip().lower()
        if low in {"on bench", "hot picks", "tournaments", "teams"}:
            break
        if low in {"(c)", "(wk)", "(c) (wk)"}:
            tag = ln.strip().upper()
            if players and tag not in players[-1]:
                players[-1] = f"{players[-1]} {tag}"
            continue
        if low in _XI_IGNORE or low.startswith("(") or "✈" in ln:
            continue
        if len(ln.strip()) >= 2:
            players.append(ln.strip().upper())
        if len(players) == limit:
            break
    return players


def _parse_tables_raw(
    tables: list[list[list[str]]],
) -> tuple[list[BatsmanState], list[BowlerState]]:
    batters: list[BatsmanState] = []
    bowlers: list[BowlerState] = []
    for tbl in tables:
        if not tbl or len(tbl) < 2:
            continue
        hdr = [h.lower() for h in tbl[0]]
        if "batter" in hdr and "sr" in hdr:
            for row in tbl[1:]:
                if len(row) < 6:
                    continue
                raw = row[0]
                m_dis = re.match(r"^(.+?)\s+((?:c |b |lbw |run out|st |batting|not out).*)$", raw, re.I)
                name = (m_dis.group(1) if m_dis else raw).replace("IMPACT", "").replace("(WK)", "").replace("(C)", "").strip().upper()
                dis = m_dis.group(2).strip() if m_dis else "batting"
                batters.append(
                    BatsmanState(
                        name=name,
                        runs=_parse_int(row[1]),
                        balls=_parse_int(row[2]),
                        fours=_parse_int(row[3]),
                        sixes=_parse_int(row[4]),
                        strike_rate=_parse_float(row[5]),
                        on_strike=False,
                        dismissal=dis,
                    )
                )
        elif "bowler" in hdr and "er" in hdr:
            for row in tbl[1:]:
                if len(row) < 6:
                    continue
                name = row[0].replace("IMPACT", "").strip().upper()
                bowlers.append(
                    BowlerState(
                        name=name,
                        overs=row[1],
                        maidens=_parse_int(row[2]),
                        runs_conceded=_parse_int(row[3]),
                        wickets=_parse_int(row[4]),
                        economy=_parse_float(row[5]),
                    )
                )
    return (batters, bowlers)


def _apply_scorecard_tables(tables: list[list[list[str]]], state: ScoreboardState) -> None:
    batters, bowlers = _parse_tables_raw(tables)
    fows: list[str] = []

    for tbl in tables:
        if not tbl or len(tbl) < 2:
            continue
        hdr = [h.lower() for h in tbl[0]]
        if "batter" in hdr and "score" in hdr and "overs" in hdr:
            for row in tbl[1:]:
                if len(row) >= 3:
                    fows.append(f"{row[0].replace('IMPACT', '').strip().upper()} • {row[1]} ({row[2]})")

    if batters:
        state.batters_list = batters
        active = [b for b in batters if "batting" in b.dismissal.lower() or "not out" in b.dismissal.lower()]
        if len(active) >= 2:
            curr_striker_name = (state.striker.name or "").upper()
            if curr_striker_name and active[1].name.upper() == curr_striker_name:
                state.striker = active[1].model_copy(update={"on_strike": True})
                state.non_striker = active[0].model_copy(update={"on_strike": False})
            else:
                state.striker = active[0].model_copy(update={"on_strike": True})
                state.non_striker = active[1].model_copy(update={"on_strike": False})
        elif len(active) == 1:
            state.striker = active[0].model_copy(update={"on_strike": True})
    if bowlers:
        state.bowlers_list = bowlers
        curr_bw = (state.bowler.name or "").upper()
        matched_bw = next((bw for bw in bowlers if curr_bw and bw.name.upper() == curr_bw), None)
        state.bowler = (matched_bw or bowlers[-1]).model_copy(deep=True)
    if fows:
        state.fall_of_wickets = fows


def _apply_points_and_leaders(
    tables: list[list[list[str]]], lines: list[str], state: ScoreboardState
) -> None:
    for tbl in tables:
        if not tbl or len(tbl) < 2:
            continue
        hdr = [h.lower() for h in tbl[0]]
        if "team" in hdr and "nrr" in hdr and "pts" in hdr:
            pt_rows = []
            for row in tbl[1:]:
                if len(row) >= 7:
                    pt_rows.append(
                        {
                            "team": row[0].upper(),
                            "p": _parse_int(row[1]),
                            "w": _parse_int(row[2]),
                            "l": _parse_int(row[3]),
                            "nr": _parse_int(row[4]),
                            "nrr": row[5],
                            "pts": _parse_int(row[6]),
                        }
                    )
            if pt_rows:
                state.points_table = pt_rows
            break
        if "team" in hdr and ("pct %" in hdr or "pct" in hdr) and "pts" in hdr:
            pt_rows = []
            for row in tbl[1:]:
                if len(row) >= 8:
                    pt_rows.append(
                        {
                            "team": row[0].upper(),
                            "p": _parse_int(row[2]),
                            "w": _parse_int(row[3]),
                            "l": _parse_int(row[4]),
                            "nr": _parse_int(row[5]),
                            "nrr": f"{row[7]}%",
                            "pts": _parse_int(row[6]),
                        }
                    )
            if pt_rows:
                state.points_table = pt_rows
            break

    leaders: list[dict[str, str | int]] = []
    for cat in ("Most Runs", "Most Wickets", "Most Sixes", "Best Strike Rate"):
        idx = next((i for i, l in enumerate(lines) if l == cat), -1)
        if idx >= 0 and idx + 3 < len(lines):
            raw_val = lines[idx + 3]
            unit = lines[idx + 4] if idx + 4 < len(lines) and lines[idx + 4] in ("Runs", "Wickets", "Sixes", "SR") else ""
            val = f"{raw_val} {unit}".strip() if unit else (f"{raw_val} SR" if cat == "Best Strike Rate" and "SR" not in raw_val else raw_val)
            leaders.append(
                {
                    "category": cat.upper(),
                    "player": lines[idx + 1].upper(),
                    "team": lines[idx + 2].upper(),
                    "value": val,
                }
            )
    if leaders:
        state.series_leaders = leaders


def _apply_rankings_lines(lines: list[str], state: ScoreboardState) -> None:
    # Extract ODI top teams from crex.com/rankings/men/teams
    odi_teams = []
    idx_odi = next((i for i, l in enumerate(lines) if l == "ODI"), -1)
    if idx_odi >= 0 and idx_odi + 3 < len(lines):
        # First team right under ODI
        odi_teams.append({"rank": 1, "team": lines[idx_odi + 1], "rating": _parse_int(lines[idx_odi + 3], 116)})
        i = idx_odi + 4
        while i + 2 < len(lines) and len(odi_teams) < 6:
            if re.match(r"^\d+$", lines[i]) and int(lines[i]) == len(odi_teams) + 1:
                odi_teams.append({"rank": int(lines[i]), "team": lines[i + 1], "rating": _parse_int(lines[i + 2], 100)})
                i += 3
            else:
                i += 1
    if odi_teams:
        rk = dict(state.icc_rankings)
        rk["odi_teams"] = odi_teams
        state.icc_rankings = rk


async def run_crex_live_watcher(url: str, state: ScoreboardState, on_update) -> None:
    """Keep persistent CREX Live + Scorecard tabs open for 2s full-scorecard & ball-by-ball updates."""
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        scorecard_page = await browser.new_page(viewport={"width": 1440, "height": 900})
        try:
            await asyncio.gather(
                page.goto(url, wait_until="domcontentloaded", timeout=35000),
                scorecard_page.goto(url, wait_until="domcontentloaded", timeout=35000),
            )
            await asyncio.sleep(2.5)
            # Switch CREX commentary to Hindi if the language button is present
            try:
                hindi_btn = page.locator("text=हिन्दी").first
                if await hindi_btn.count() > 0:
                    await hindi_btn.click(timeout=3000)
                    await asyncio.sleep(1.5)
            except Exception:
                pass
            # Open the Scorecard tab on the dedicated scorecard_page
            try:
                sc_tab = scorecard_page.locator("text=Scorecard").first
                if await sc_tab.count() > 0:
                    await sc_tab.click(timeout=5000)
                    await asyncio.sleep(1.5)
            except Exception:
                pass
            needs_full = not state.first_innings.get("score") or not state.latest_news
            last_full_sync = 0.0 if needs_full else asyncio.get_running_loop().time()

            while True:
                snap, sc_tables = await asyncio.gather(
                    page.evaluate(
                        """() => {
                            const lines = document.body.innerText.split(/\\n+/).map(s => s.trim()).filter(Boolean);
                            let comm = "";
                            const cards = Array.from(document.querySelectorAll(".cm-b-roundcard"));
                            for (const c of cards.slice(0, 6)) {
                                const t = (c.innerText || "").trim().replace(/\\s+/g, " ");
                                if (/^\\d+\\.\\d+\\s+/.test(t) && /[\\u0900-\\u097F]/.test(t) && t.length > 22) {
                                    comm = t;
                                    break;
                                }
                            }
                            if (!comm) {
                                for (const c of cards.slice(0, 4)) {
                                    const t = (c.innerText || "").trim().replace(/\\s+/g, " ");
                                    if (/^\\d+\\.\\d+\\s+/.test(t) && t.length > 28) {
                                        comm = t;
                                        break;
                                    }
                                }
                            }
                            if (!comm) {
                                const c2 = document.querySelector(".cm-b-comment-c2");
                                if (c2) comm = (c2.innerText || "").trim().replace(/\\s+/g, " ");
                            }
                            return { lines, comm };
                        }"""
                    ),
                    scorecard_page.evaluate(
                        """() => Array.from(document.querySelectorAll("table")).map(t =>
                            Array.from(t.querySelectorAll("tr")).map(r =>
                                Array.from(r.querySelectorAll("th, td")).map(c => c.innerText.trim().replace(/\\s+/g, " "))
                            )
                        )"""
                    ),
                )
                prev_sig = (
                    state.runs,
                    state.wickets,
                    state.overs,
                    state.partnership,
                    state.crr,
                    state.rrr,
                    state.target,
                    state.striker.name,
                    state.striker.runs,
                    state.striker.balls,
                    state.non_striker.name,
                    state.non_striker.runs,
                    state.non_striker.balls,
                    state.bowler.name,
                    state.bowler.wickets,
                    state.bowler.runs_conceded,
                    state.bowler.overs,
                    state.live_commentary,
                    state.match_status,
                    state.batting_team,
                    state.callout,
                    tuple((b.name, b.runs, b.balls, b.fours, b.sixes, b.dismissal) for b in state.batters_list),
                    tuple((bw.name, bw.overs, bw.runs_conceded, bw.wickets) for bw in state.bowlers_list),
                    len(state.fall_of_wickets),
                )
                _apply_live_lines(snap.get("lines") or [], state)
                if snap.get("comm"):
                    state.live_commentary = snap["comm"]
                if sc_tables:
                    _apply_scorecard_tables(sc_tables, state)
                curr_sig = (
                    state.runs,
                    state.wickets,
                    state.overs,
                    state.partnership,
                    state.crr,
                    state.rrr,
                    state.target,
                    state.striker.name,
                    state.striker.runs,
                    state.striker.balls,
                    state.non_striker.name,
                    state.non_striker.runs,
                    state.non_striker.balls,
                    state.bowler.name,
                    state.bowler.wickets,
                    state.bowler.runs_conceded,
                    state.bowler.overs,
                    state.live_commentary,
                    state.match_status,
                    state.batting_team,
                    state.callout,
                    tuple((b.name, b.runs, b.balls, b.fours, b.sixes, b.dismissal) for b in state.batters_list),
                    tuple((bw.name, bw.overs, bw.runs_conceded, bw.wickets) for bw in state.bowlers_list),
                    len(state.fall_of_wickets),
                )

                if curr_sig != prev_sig:
                    save_match_state(url, state.model_dump())
                    await on_update(state)

                now = asyncio.get_running_loop().time()
                if last_full_sync == 0.0 and now > 0:
                    last_full_sync = now
                    try:
                        pre_team = state.batting_team
                        pre_runs = state.runs
                        pre_wkts = state.wickets
                        pre_overs = state.overs
                        pre_comm = state.live_commentary

                        def _ov_t(ov: str) -> tuple[int, int]:
                            pts = str(ov or "0.0").split(".")
                            try:
                                return (int(pts[0] or 0), int(pts[1] or 0) if len(pts) > 1 else 0)
                            except Exception:
                                return (0, 0)

                        await sync_crex_match_once(url, state)
                        if state.batting_team == pre_team and (
                            _ov_t(state.overs) < _ov_t(pre_overs)
                            or state.runs < pre_runs
                            or state.wickets < pre_wkts
                        ):
                            state.runs = pre_runs
                            state.wickets = pre_wkts
                            state.overs = pre_overs
                            if pre_comm:
                                state.live_commentary = pre_comm
                        await on_update(state)
                    except Exception as exc:
                        print(f"[crex_watcher:full] {exc}")

                await asyncio.sleep(1.0)
        finally:
            await browser.close()
