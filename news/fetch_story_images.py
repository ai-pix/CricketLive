"""Fetch accurate match & player images for the #1 IND-A vs SL-A 1st Semi-Final story."""
import asyncio
import json
import re
from pathlib import Path
from urllib.parse import quote
import httpx
from playwright.async_api import async_playwright

OUT_DIR = Path("news/build_02/candidates")
OUT_DIR.mkdir(parents=True, exist_ok=True)


async def gather():
    items = json.loads(Path("news/latest_news.json").read_text(encoding="utf-8")).get("items", [])
    target_urls = []
    direct_imgs = []
    for it in items:
        t = (it.get("title") or "").lower()
        if any(k in t for k in ("ind-a", "ind a", "sooryavanshi", "abhishek sharma", "rinku singh", "sl-a", "sri lanka a")):
            if it.get("image_url"):
                direct_imgs.append((it["title"][:50], it["image_url"]))
            if it.get("source_url"):
                target_urls.append((it.get("source", ""), it["title"][:50], it["source_url"]))

    print(f"Direct article images: {len(direct_imgs)} | Candidate article pages: {len(target_urls)}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"}
    found_urls: list[tuple[str, str]] = list(direct_imgs)

    # Use Playwright to follow Google News / article pages and collect high-res cricket photos
    async with async_playwright() as pw:
        b = await pw.chromium.launch(headless=True)
        page = await b.new_page(viewport={"width": 1280, "height": 800})
        for src_name, title, url in target_urls[:6]:
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                await asyncio.sleep(2.5)
                imgs = await page.evaluate(
                    """() => {
                        const out = [];
                        const og = document.querySelector('meta[property="og:image"]')?.content;
                        if (og) out.push({src: og, alt: 'og'});
                        for (const im of document.querySelectorAll('img')) {
                            const s = im.currentSrc || im.src || im.getAttribute('data-src') || '';
                            if (!s.startsWith('http')) continue;
                            if (/logo|icon|avatar|svg|gif|pixel|ads|doubleclick|scorecard|badge/i.test(s)) continue;
                            const r = im.getBoundingClientRect();
                            if ((im.naturalWidth >= 400 || r.width >= 350) && (im.naturalHeight >= 220 || r.height >= 200)) {
                                out.push({src: s, alt: (im.alt || '').slice(0, 40)});
                            }
                        }
                        return out;
                    }"""
                )
                print(f"Page [{src_name}] {page.url[:65]} -> {len(imgs)} imgs")
                for im in imgs[:6]:
                    found_urls.append((f"{src_name}:{im['alt']}", im["src"]))
            except Exception as exc:
                print(f"Skip {url[:50]}: {exc}")
        await b.close()

    # Also search Wikimedia Commons for specific match/player real action photos
    async with httpx.AsyncClient(headers={"User-Agent": "CricketLiveBot/1.0"}, follow_redirects=True, timeout=15) as c:
        for q in ["Rinku Singh", "Abhishek Sharma cricketer", "Tilak Varma", "West End Park International Cricket Stadium Doha"]:
            try:
                u = "https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6&gsrsearch=" + quote(q) + "&gsrlimit=3&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json"
                r = await c.get(u)
                if r.status_code == 200 and r.text.strip().startswith("{"):
                    for v in (r.json().get("query", {}).get("pages") or {}).values():
                        ii = (v.get("imageinfo") or [{}])[0]
                        u2 = ii.get("thumburl") or ii.get("url")
                        if u2 and any(e in u2.lower() for e in (".jpg", ".jpeg", ".png")):
                            found_urls.append((f"Wiki:{q}", u2))
            except Exception:
                pass

        # Download unique images
        seen_url = set()
        idx = 0
        for label, u in found_urls:
            if u in seen_url:
                continue
            seen_url.add(u)
            try:
                resp = await c.get(u, headers=headers)
                if resp.status_code == 200 and len(resp.content) > 15000:
                    ext = ".png" if ".png" in u.lower().split("?")[0] else ".jpg"
                    p = OUT_DIR / f"cand_{idx:02d}{ext}"
                    p.write_bytes(resp.content)
                    print(f"SAVED {p.name} ({len(resp.content)//1024} KB) <- {label} | {u[:75]}")
                    idx += 1
            except Exception:
                pass


if __name__ == "__main__":
    asyncio.run(gather())
