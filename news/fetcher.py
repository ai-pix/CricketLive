"""Fetch latest cricket match news across multiple live internet RSS feeds."""

from __future__ import annotations

import asyncio
import email.utils
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import httpx

NEWS_DIR = Path(__file__).resolve().parent
ROOT_DIR = NEWS_DIR.parent
CACHE_JSON_PATH = NEWS_DIR / "latest_news.json"

DEFAULT_FEEDS: list[tuple[str, str]] = [
    ("ESPNcricinfo", "https://www.espncricinfo.com/rss/content/story/feeds/0.xml"),
    ("BBC Sport", "https://feeds.bbci.co.uk/sport/cricket/rss.xml"),
    ("NDTV Cricket", "https://feeds.feedburner.com/ndtvsports-cricket"),
    ("TOI Cricket", "https://timesofindia.indiatimes.com/rssfeeds/54829575.cms"),
    (
        "Cricket Wire",
        "https://news.google.com/rss/search?q=cricket+match+OR+live+score+OR+semi+final+when:2d&hl=en-IN&gl=IN&ceid=IN:en",
    ),
]


def _clean_html(raw: str) -> str:
    txt = html.unescape(raw or "")
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def _clean_title(raw: str, source_name: str) -> tuple[str, str]:
    title = _clean_html(raw)
    # Google News titles often end with " - Publisher Name"
    if source_name in ("Cricket Wire", "Match Wire") and " - " in title:
        head, pub = title.rsplit(" - ", 1)
        if 2 <= len(pub.strip()) <= 45:
            return (head.strip(), pub.strip())
    return (title, source_name)


def _parse_pub_ts(pub_date: str) -> float:
    if not pub_date:
        return 0.0
    try:
        dt = email.utils.parsedate_to_datetime(pub_date)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except Exception:
        return 0.0


def _extract_image(item_el: ET.Element) -> str:
    for child in item_el:
        tag = child.tag.lower()
        if tag.endswith("content") or tag.endswith("thumbnail") or tag == "enclosure":
            url = (child.attrib.get("url") or "").strip()
            if url.startswith("http"):
                return url
    desc = item_el.findtext("description") or ""
    m = re.search(r'<img[^>]+src=["\'](https?://[^"\']+)["\']', desc, flags=re.I)
    return m.group(1) if m else ""


def _parse_rss_xml(xml_text: str, source_name: str, limit: int = 25) -> list[dict[str, Any]]:
    root = ET.fromstring(xml_text)
    items: list[dict[str, Any]] = []
    for item_el in root.findall(".//item")[:limit]:
        raw_title = item_el.findtext("title") or ""
        title, resolved_source = _clean_title(raw_title, source_name)
        if not title:
            continue
        source_el = item_el.find("source")
        if source_el is not None and (source_el.text or "").strip():
            resolved_source = source_el.text.strip()

        raw_desc = item_el.findtext("description") or ""
        summary = _clean_html(raw_desc)
        # Avoid repeating headline verbatim in Google News summaries
        if summary.lower().startswith(title[:40].lower()):
            summary = summary[len(title) :].lstrip(" -–—:.")
        summary = summary[:240]

        link = (item_el.findtext("link") or "").strip()
        pub_raw = (item_el.findtext("pubDate") or "").strip()
        pub_ts = _parse_pub_ts(pub_raw)
        items.append(
            {
                "title": title,
                "summary": summary or f"Latest match report via {resolved_source}.",
                "source": resolved_source,
                "source_url": link,
                "image_url": _extract_image(item_el),
                "published": pub_raw,
                "published_ts": pub_ts,
                "category": "match_news",
            }
        )
    return items


async def _fetch_feed(
    client: httpx.AsyncClient, source_name: str, url: str
) -> tuple[str, list[dict[str, Any]]]:
    try:
        resp = await client.get(url)
        if resp.status_code != 200:
            return (source_name, [])
        return (source_name, _parse_rss_xml(resp.text, source_name))
    except Exception as exc:
        print(f"[news.fetcher] {source_name} err: {exc}")
        return (source_name, [])


def _dedupe_and_rank(
    items: list[dict[str, Any]], focus_terms: list[str] | None = None
) -> list[dict[str, Any]]:
    terms = [t.lower() for t in (focus_terms or []) if t and len(t) >= 2]
    seen_keys: set[str] = set()
    unique: list[dict[str, Any]] = []
    for it in items:
        norm = re.sub(r"[^a-z0-9]+", "", it["title"].lower())[:52]
        if not norm or norm in seen_keys:
            continue
        seen_keys.add(norm)
        hay = f"{it['title']} {it['summary']}".lower()
        if any(spam in hay for spam in ("dream11", "fantasy", "my11circle", "prediction", "live streaming", "telecast")):
            continue
        boost = sum(1 for t in terms if t in hay)
        it["_rank"] = (boost, it.get("published_ts", 0.0))
        unique.append(it)

    unique.sort(key=lambda x: x["_rank"], reverse=True)
    for it in unique:
        it.pop("_rank", None)
    return unique


def _sync_to_db(items: list[dict[str, Any]]) -> int:
    src_dir = str(ROOT_DIR / "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    try:
        from cricket_live.db import upsert_news_items

        db_rows = [
            {
                "title": it["title"],
                "summary": f"[{it['source']}] {it['summary']}",
                "source_url": it.get("source_url", ""),
                "category": it.get("source", "cricket"),
            }
            for it in items[:40]
        ]
        return upsert_news_items(db_rows)
    except Exception as exc:
        print(f"[news.fetcher] db sync skip: {exc}")
        return 0


async def fetch_all_cricket_news(
    match_query: str = "",
    focus_terms: list[str] | None = None,
    max_items: int = 50,
    save_to_db: bool = True,
) -> dict[str, Any]:
    """Fetch latest cricket news across multiple internet feeds, cache JSON in news/, and sync DB."""
    feeds = list(DEFAULT_FEEDS)
    if match_query.strip():
        q_url = (
            "https://news.google.com/rss/search?q="
            + quote_plus(f"{match_query.strip()} cricket when:2d")
            + "&hl=en-IN&gl=IN&ceid=IN:en"
        )
        feeds.insert(0, ("Match Wire", q_url))

    headers = {"User-Agent": "CricketLiveNewsBot/1.0 (+https://localhost)"}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=12.0) as client:
        results = await asyncio.gather(*(_fetch_feed(client, n, u) for n, u in feeds))

    all_items: list[dict[str, Any]] = []
    sources_ok: dict[str, int] = {}
    for source_name, batch in results:
        if batch:
            sources_ok[source_name] = len(batch)
            all_items.extend(batch)

    ranked = _dedupe_and_rank(all_items, focus_terms=focus_terms)[:max_items]
    db_added = _sync_to_db(ranked) if (save_to_db and ranked) else 0

    payload: dict[str, Any] = {
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": sources_ok,
        "total": len(ranked),
        "db_added": db_added,
        "items": ranked,
    }
    NEWS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def load_cached_news() -> dict[str, Any]:
    if CACHE_JSON_PATH.exists():
        try:
            return json.loads(CACHE_JSON_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"fetched_at": "", "sources": {}, "total": 0, "items": []}


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]).strip()
    res = asyncio.run(
        fetch_all_cricket_news(
            match_query=q,
            focus_terms=["ind", "india", "sl", "sri lanka", "semi final", "asia cup", "live", "win", "wickets"],
        )
    )
    print(f"Fetched {res['total']} articles from {res['sources']} (DB added: {res['db_added']})")
    for idx, item in enumerate(res["items"][:8], 1):
        print(f"  {idx}. [{item['source']}] {item['title']}")
