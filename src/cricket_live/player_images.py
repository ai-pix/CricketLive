"""Scrape, cache locally, and store real player headshot portraits in SQLite."""

from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Any

import httpx
from playwright.async_api import Page, async_playwright

from .db import normalize_player_key, upsert_player_image

PLAYERS_ASSET_DIR = Path(__file__).resolve().parents[2] / "ui" / "assets" / "players"


def _slugify(name: str) -> str:
    clean = normalize_player_key(name).lower().replace(" ", "_")
    return re.sub(r"[^a-z0-9_]+", "", clean) or "player"


async def extract_and_cache_player_images(
    page: Page,
    team_hint: str = "",
    client: httpx.AsyncClient | None = None,
) -> list[dict[str, str]]:
    """Extract all player headshot <img> elements on the current CREX page, save locally, and record in DB."""
    raw_items: list[dict[str, str]] = await page.evaluate(
        """() => {
            const out = [];
            for (const im of document.querySelectorAll('img')) {
                const src = im.currentSrc || im.src || im.getAttribute('data-src') || '';
                if (!src || !src.includes('/players/') || src.includes('/jersey/')) continue;
                let alt = (im.alt || '').trim();
                alt = alt.replace(/\\s*jersy$/i, '').replace(/\\s*jersey$/i, '').trim();
                if (!alt) {
                    const card = im.closest('a, tr, li, .player-card, .playing-xi-card, div');
                    const txt = (card?.innerText || '').trim().split(/\\n+/)[0]?.trim() || '';
                    if (txt && txt.length <= 36) alt = txt;
                }
                if (alt && !/^team\\s|^crex|^logo/i.test(alt)) {
                    out.push({ name: alt, url: src.split('?')[0] });
                }
            }
            return out;
        }"""
    )

    if not raw_items:
        return []

    PLAYERS_ASSET_DIR.mkdir(parents=True, exist_ok=True)
    own_client = client is None
    if own_client:
        client = httpx.AsyncClient(
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CricketLive/1.0"},
            follow_redirects=True,
            timeout=12.0,
        )

    saved: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    try:
        for item in raw_items:
            name = item["name"].strip()
            url = item["url"].strip()
            if not name or not url:
                continue
            code = url.rsplit("/", 1)[-1].split(".")[0]
            # Prefer human-readable name slug; store local file once per unique CREX player code
            # If the same CREX player code has both "T Varma" and "Tilak Varma", both keys point to the saved file
            file_slug = _slugify(name)
            code_file = next(PLAYERS_ASSET_DIR.glob(f"*__{code}.*"), None)
            if code_file and code_file.exists():
                local_path = f"/assets/players/{code_file.name}"
                upsert_player_image(name, local_path, image_url=url, team=team_hint)
                saved.append({"name": name, "local_path": local_path, "url": url})
                continue

            if url in seen_urls:
                continue
            seen_urls.add(url)

            try:
                resp = await client.get(url)
                if resp.status_code == 200 and len(resp.content) > 1500:
                    ext = ".webp" if ".webp" in url.lower() else (".jpg" if ".jpg" in url.lower() else ".png")
                    fname = f"{file_slug}__{code}{ext}"
                    dest = PLAYERS_ASSET_DIR / fname
                    dest.write_bytes(resp.content)
                    local_path = f"/assets/players/{fname}"
                    upsert_player_image(name, local_path, image_url=url, team=team_hint)
                    saved.append({"name": name, "local_path": local_path, "url": url})
            except Exception as exc:
                print(f"[player_images] download err {name} ({url}): {exc}")
    finally:
        if own_client and client is not None:
            await client.aclose()

    return saved


async def scrape_crex_match_player_images(url: str) -> dict[str, Any]:
    """Visit Live, Match info (both team Playing XI tabs), and Scorecard (both innings) to cache all player photos."""
    results: list[dict[str, str]] = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        async with httpx.AsyncClient(
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CricketLive/1.0"},
            follow_redirects=True,
            timeout=12.0,
        ) as client:
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=35000)
                await asyncio.sleep(3.0)
                results.extend(await extract_and_cache_player_images(page, client=client))

                # Match Info tab -> click all team buttons near Playing XI / Squad
                info_tab = page.locator("text=Match info").first
                if await info_tab.count() > 0:
                    await info_tab.click(timeout=5000)
                    await asyncio.sleep(2.2)
                    results.extend(await extract_and_cache_player_images(page, client=client))

                    # Find Playing XI / Squad team pills (e.g. IND-A, SL-A) and click each
                    team_btns = await page.evaluate(
                        """() => {
                            const h = Array.from(document.querySelectorAll('*')).find(el =>
                                /Playing XI|Squad/i.test((el.textContent || '').trim()) && (el.textContent || '').trim().length < 25
                            );
                            if (!h) return [];
                            const btns = [];
                            let cur = h.parentElement;
                            for (let step = 0; step < 3 && cur; step++, cur = cur.parentElement) {
                                for (const b of cur.querySelectorAll('button, div, span')) {
                                    const t = (b.innerText || '').trim();
                                    if (t && t.length <= 12 && /^[A-Z0-9\\-]{2,10}$/.test(t) && !btns.includes(t)) {
                                        btns.push(t);
                                    }
                                }
                            }
                            return btns.slice(0, 4);
                        }"""
                    )
                    for tcode in team_btns:
                        loc = page.locator(
                            f"xpath=//*[contains(text(),'Playing XI') or contains(text(),'Squad')]/following::*[normalize-space(text())='{tcode}']"
                        ).first
                        if await loc.count() > 0:
                            try:
                                await loc.scroll_into_view_if_needed()
                                await loc.click(timeout=3000, force=True)
                                await asyncio.sleep(1.5)
                                results.extend(await extract_and_cache_player_images(page, team_hint=tcode, client=client))
                            except Exception:
                                pass

                # Scorecard tab -> click each innings tab
                sc_tab = page.locator("text=Scorecard").first
                if await sc_tab.count() > 0:
                    await sc_tab.click(timeout=5000)
                    await asyncio.sleep(2.2)
                    results.extend(await extract_and_cache_player_images(page, client=client))
                    inn_tabs = await page.evaluate(
                        """() => {
                            const out = [];
                            for (const el of document.querySelectorAll('div, button, a, span, li')) {
                                const t = (el.innerText || '').trim();
                                if (t.length > 0 && t.length < 36 && /^[A-Z0-9\\-]+[\\s\\n]+\\d+-\\d+/i.test(t)) {
                                    out.push(t.split(/\\s+/)[0]);
                                }
                            }
                            return Array.from(new Set(out));
                        }"""
                    )
                    for tcode in inn_tabs:
                        try:
                            await page.evaluate(
                                """(code) => {
                                    const rx = new RegExp('^' + code + '[\\\\s\\\\n]+\\\\d+-\\\\d+', 'i');
                                    const hits = Array.from(document.querySelectorAll('div, button, a, span, li')).filter(el => {
                                        const t = (el.innerText || '').trim();
                                        return t.length > 0 && t.length < 36 && rx.test(t);
                                    });
                                    if (hits.length) hits[hits.length - 1].click();
                                }""",
                                tcode,
                            )
                            await asyncio.sleep(1.8)
                            results.extend(await extract_and_cache_player_images(page, team_hint=tcode, client=client))
                        except Exception:
                            pass
            finally:
                await browser.close()

    unique_players = {r["name"]: r["local_path"] for r in results}
    return {"count": len(unique_players), "players": unique_players}


if __name__ == "__main__":
    import sys
    target_url = sys.argv[1] if len(sys.argv) > 1 else "https://crex.com/cricket-live-score/ind-a-vs-sl-a-1st-semi-final-mens-asia-cup-rising-stars-2026-match-updates-1514"
    res = asyncio.run(scrape_crex_match_player_images(target_url))
    print("Scraped players:", res["count"])
    for k, v in sorted(res["players"].items()):
        print(" ", k, "->", v)
