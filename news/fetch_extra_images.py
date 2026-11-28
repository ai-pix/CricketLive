"""Fetch targeted, accurate match & cricketer action photos via Bing Images + live news pages."""
import asyncio
import json
from pathlib import Path
from urllib.parse import quote
import httpx
from playwright.async_api import async_playwright

OUT_DIR = Path("news/build_02/extra_candidates")
OUT_DIR.mkdir(parents=True, exist_ok=True)

QUERIES = [
    ("shahbaz", "Shahbaz Ahmed India cricketer batting action"),
    ("tilak", "Tilak Varma India cricket jersey batting fifty"),
    ("rinku", "Rinku Singh India A vs Sri Lanka A batting"),
    ("ind_sl_a", "India A vs Sri Lanka A Asia Cup Rising Stars 2026 Doha"),
    ("doha_stadium", "West End Park International Cricket Stadium Doha cricket match"),
    ("kotian", "Tanush Kotian cricketer batting"),
]


async def main():
    # First refresh news so we catch any new IND-A vs SL-A 317/8 innings-break articles
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        try:
            r = await client.post("http://127.0.0.1:8000/api/news/refresh")
            print("News refresh status:", r.status_code)
        except Exception as exc:
            print("News refresh skip:", exc)

    items = json.loads(Path("news/latest_news.json").read_text(encoding="utf-8")).get("items", [])
    article_candidates = []
    for it in items:
        t = (it.get("title") or "").lower()
        if any(k in t for k in ("ind-a", "ind a", "india a", "sri lanka a", "sl-a", "sooryavanshi", "abhishek", "rinku", "tilak", "shahbaz")):
            if it.get("image_url"):
                article_candidates.append(("article_img", it["image_url"]))
            if it.get("source_url"):
                article_candidates.append(("article_page", it["source_url"]))

    collected: list[tuple[str, str]] = []
    for tag, url in article_candidates:
        if tag == "article_img":
            collected.append(("rss", url))

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        # Scrape remaining IND-A vs SL-A articles beyond the first 6
        pages = [u for tag, u in article_candidates if tag == "article_page"]
        for u in pages[4:11]:
            try:
                await page.goto(u, wait_until="domcontentloaded", timeout=18000)
                await asyncio.sleep(2.0)
                urls = await page.evaluate(
                    """() => {
                        const out = [];
                        const og = document.querySelector('meta[property="og:image"]')?.content;
                        if (og) out.push(og);
                        for (const im of document.querySelectorAll('article img, main img, figure img')) {
                            const s = im.currentSrc || im.src || im.getAttribute('data-src') || '';
                            if (s.startsWith('http') && !/logo|icon|avatar|svg|gif|pixel|badge|ad/i.test(s) && (im.naturalWidth >= 450 || im.width >= 450)) {
                                out.push(s);
                            }
                        }
                        return out;
                    }"""
                )
                print(f"Article {page.url[:60]} -> {len(urls)} imgs")
                for img_u in urls[:4]:
                    collected.append(("art", img_u))
            except Exception as exc:
                print(f"Article skip {u[:40]}: {exc}")

        # Targeted Bing Image searches (high-res cricket photos, skip tiny thumbnails)
        for label, query in QUERIES:
            try:
                search_url = f"https://www.bing.com/images/search?q={quote(query)}&qft=+filterui:imagesize-large+filterui:aspect-wide"
                await page.goto(search_url, wait_until="domcontentloaded", timeout=18000)
                await asyncio.sleep(1.5)
                murls = await page.evaluate(
                    """() => {
                        const out = [];
                        for (const a of document.querySelectorAll('a.iusc')) {
                            try {
                                const m = JSON.parse(a.getAttribute('m') || '{}');
                                if (m.murl && m.murl.startsWith('http')) out.push(m.murl);
                            } catch {}
                        }
                        return out.slice(0, 6);
                    }"""
                )
                print(f"Bing [{label}] -> {len(murls)} hits")
                for mu in murls[:3]:
                    collected.append((label, mu))
            except Exception as exc:
                print(f"Bing err [{label}]: {exc}")

        await browser.close()

    # Download unique images that aren't already tiny or logos
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"}
    seen = set()
    idx = 0
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=15) as c:
        for label, u in collected:
            if u in seen or any(bad in u.lower() for bad in ("dafabet", "1xbet", "logo", "favicon", "crex.live/assets")):
                continue
            seen.add(u)
            try:
                resp = await c.get(u)
                ct = (resp.headers.get("content-type") or "").lower()
                if resp.status_code == 200 and "image" in ct and len(resp.content) > 25000:
                    ext = ".png" if "png" in ct else ".jpg"
                    p = OUT_DIR / f"extra_{idx:02d}_{label}{ext}"
                    p.write_bytes(resp.content)
                    print(f"SAVED {p.name} ({len(resp.content)//1024} KB) <- {u[:75]}")
                    idx += 1
                    if idx >= 18:
                        break
            except Exception:
                pass


if __name__ == "__main__":
    asyncio.run(main())
