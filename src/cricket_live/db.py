"""SQLite persistence for live matches, ball events, CREX news, and pre-written commentary stories."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "cricket_live.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init_db() -> None:
    """Create database tables if they do not exist."""
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS matches (
                match_url TEXT PRIMARY KEY,
                match_title TEXT,
                series_name TEXT,
                venue TEXT,
                state_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS ball_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_url TEXT NOT NULL,
                overs TEXT,
                runs INTEGER,
                wickets INTEGER,
                callout TEXT,
                commentary TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS news_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL,
                summary TEXT DEFAULT '',
                source_url TEXT DEFAULT '',
                category TEXT DEFAULT 'cricket',
                fetched_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS commentary_stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                host_line TEXT NOT NULL,
                expert_line TEXT NOT NULL,
                match_context TEXT DEFAULT 'general',
                used_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                UNIQUE(host_line, expert_line)
            );

            CREATE TABLE IF NOT EXISTS player_images (
                player_key TEXT PRIMARY KEY,
                player_name TEXT NOT NULL,
                team TEXT DEFAULT '',
                image_url TEXT NOT NULL,
                local_path TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )


def save_match_state(match_url: str, state_dict: dict) -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO matches (match_url, match_title, series_name, venue, state_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(match_url) DO UPDATE SET
                match_title=excluded.match_title,
                series_name=excluded.series_name,
                venue=excluded.venue,
                state_json=excluded.state_json,
                updated_at=excluded.updated_at
            """,
            (
                match_url,
                state_dict.get("match_title", ""),
                state_dict.get("series_name", ""),
                state_dict.get("venue", ""),
                json.dumps(state_dict, ensure_ascii=False),
                _now_iso(),
            ),
        )


def load_latest_match_state() -> dict | None:
    if not DB_PATH.exists():
        return None
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT state_json FROM matches ORDER BY updated_at DESC LIMIT 1"
        ).fetchone()
        if not row:
            return None
        try:
            return json.loads(row["state_json"])
        except Exception:
            return None


def log_ball_event(
    match_url: str,
    overs: str,
    runs: int,
    wickets: int,
    callout: str,
    commentary: str = "",
) -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO ball_events (match_url, overs, runs, wickets, callout, commentary, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (match_url, overs, runs, wickets, callout, commentary, _now_iso()),
        )


def get_recent_ball_events(limit: int = 8) -> list[dict]:
    if not DB_PATH.exists():
        return []
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT overs, runs, wickets, callout, commentary, created_at FROM ball_events ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def upsert_news_items(items: list[dict[str, str]]) -> int:
    init_db()
    now = _now_iso()
    inserted = 0
    with _connect() as conn:
        for item in items:
            title = (item.get("title") or "").strip()
            if not title:
                continue
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO news_items (title, summary, source_url, category, fetched_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    title,
                    (item.get("summary") or "").strip(),
                    (item.get("source_url") or "").strip(),
                    (item.get("category") or "cricket").strip(),
                    now,
                ),
            )
            inserted += cur.rowcount
    return inserted


def get_news_items(limit: int = 15) -> list[dict[str, str]]:
    if not DB_PATH.exists():
        return []
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT title, summary, source_url, category, fetched_at FROM news_items ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def seed_commentary_stories(stories: list[tuple[str, str, str, str]]) -> int:
    """Insert (category, host_line, expert_line, match_context) stories if not already present."""
    init_db()
    now = _now_iso()
    inserted = 0
    with _connect() as conn:
        for cat, host_line, expert_line, ctx in stories:
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO commentary_stories
                    (category, host_line, expert_line, match_context, used_count, created_at)
                VALUES (?, ?, ?, ?, 0, ?)
                """,
                (cat, host_line.strip(), expert_line.strip(), ctx, now),
            )
            inserted += cur.rowcount
    return inserted


def get_all_stories() -> list[dict]:
    """Return all commentary stories from SQLite."""
    if not DB_PATH.exists():
        return []
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, category, host_line, expert_line, match_context, used_count FROM commentary_stories ORDER BY id"
        ).fetchall()
        return [dict(r) for r in rows]


def pick_next_story(match_context: str | None = None) -> tuple[str, str] | None:
    """Return the least-used (host_line, expert_line) story and increment its used_count."""
    if not DB_PATH.exists():
        return None
    init_db()
    with _connect() as conn:
        if match_context:
            row = conn.execute(
                """
                SELECT id, host_line, expert_line FROM commentary_stories
                WHERE match_context = ? OR match_context = 'general'
                ORDER BY used_count ASC, RANDOM() LIMIT 1
                """,
                (match_context,),
            ).fetchone()
        else:
            row = conn.execute(
                """
                SELECT id, host_line, expert_line FROM commentary_stories
                ORDER BY used_count ASC, RANDOM() LIMIT 1
                """
            ).fetchone()
        if not row:
            return None
        conn.execute(
            "UPDATE commentary_stories SET used_count = used_count + 1 WHERE id = ?",
            (row["id"],),
        )
        return (row["host_line"], row["expert_line"])


def normalize_player_key(name: str) -> str:
    """Normalize a player name by removing captain/keeper tags and extra whitespace."""
    import re
    clean = re.sub(r"\((?:c|wk|vc)\)", "", str(name or ""), flags=re.I)
    clean = re.sub(r"[^A-Za-z0-9\s]", " ", clean)
    return " ".join(clean.upper().split())


def upsert_player_image(
    player_name: str,
    local_path: str,
    image_url: str = "",
    team: str = "",
) -> None:
    key = normalize_player_key(player_name)
    if not key or not local_path:
        return
    init_db()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO player_images (player_key, player_name, team, image_url, local_path, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(player_key) DO UPDATE SET
                player_name=excluded.player_name,
                team=CASE WHEN excluded.team != '' THEN excluded.team ELSE player_images.team END,
                image_url=CASE WHEN excluded.image_url != '' THEN excluded.image_url ELSE player_images.image_url END,
                local_path=excluded.local_path,
                updated_at=excluded.updated_at
            """,
            (key, player_name.strip(), team.strip(), image_url.strip(), local_path.strip(), _now_iso()),
        )


def get_all_player_images() -> dict[str, str]:
    """Return a lookup dict of normalized player keys (plus short initial+last aliases) to local paths."""
    if not DB_PATH.exists():
        return {}
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT player_key, player_name, team, local_path FROM player_images ORDER BY updated_at DESC"
        ).fetchall()
    out: dict[str, str] = {}
    last_counts: dict[str, int] = {}
    for r in rows:
        parts = r["player_key"].split()
        if parts:
            last_counts[parts[-1]] = last_counts.get(parts[-1], 0) + 1
    for r in rows:
        key = r["player_key"]
        path = r["local_path"]
        out[key] = path
        parts = key.split()
        if len(parts) >= 2:
            # Map "T VARMA" <-> "TILAK VARMA" style aliases
            alias = f"{parts[0][0]} {parts[-1]}"
            out.setdefault(alias, path)
            if last_counts.get(parts[-1], 0) == 1 and len(parts[-1]) >= 4:
                out.setdefault(parts[-1], path)
    return out


def list_player_images_rows() -> list[dict]:
    if not DB_PATH.exists():
        return []
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT player_key, player_name, team, image_url, local_path, updated_at FROM player_images ORDER BY team, player_name"
        ).fetchall()
        return [dict(r) for r in rows]
