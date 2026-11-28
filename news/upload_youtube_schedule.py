"""Upload and schedule grouped cricket news videos + clickbait thumbnails via YouTube Data API v3.

Requires:
  news/client_secret.json  (Google Cloud OAuth 2.0 Desktop App client secret with YouTube Data API v3 enabled)

Usage:
  .venv\\Scripts\\python.exe news\\upload_youtube_schedule.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

ROOT_DIR = Path(__file__).resolve().parent.parent
NEWS_DIR = Path(__file__).resolve().parent
VIDEOS_DIR = NEWS_DIR / "videos"
THUMB_DIR = NEWS_DIR / "thumbnails"
CLIENT_SECRET = NEWS_DIR / "client_secret.json"
TOKEN_FILE = NEWS_DIR / "youtube_token.json"
STATE_FILE = NEWS_DIR / "youtube_uploaded.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

if str(NEWS_DIR) not in sys.path:
    sys.path.insert(0, str(NEWS_DIR))

from make_grouped_news_videos import EPISODES  # noqa: E402

THUMB_MAP = {
    "ep_01_ind_pak_clash": "ep_01_thumb.jpg",
    "ep_02_pak_asiacup_3in1": "ep_02_thumb.jpg",
    "ep_03_bilateral_tilak_2in1": "ep_03_thumb.jpg",
    "ep_04_vaibhav_standalone": "ep_04_thumb.jpg",
    "ep_05_mi_rohit_bumrah_2in1": "ep_05_thumb.jpg",
    "ep_06_ipl_psl_bcci_3in1": "ep_06_thumb.jpg",
    "ep_07_ind_nz_bumrah_3in1": "ep_07_thumb.jpg",
}


def get_youtube_service():
    if not CLIENT_SECRET.exists():
        raise FileNotFoundError(
            f"Missing OAuth client secret: {CLIENT_SECRET}\n"
            "Download your OAuth 2.0 Desktop App JSON from Google Cloud Console "
            "(with YouTube Data API v3 enabled) and save it as news/client_secret.json."
        )
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=creds)


def main() -> None:
    youtube = get_youtube_service()
    ch_resp = youtube.channels().list(part="snippet", mine=True).execute()
    ch_items = ch_resp.get("items") or []
    if not ch_items:
        raise RuntimeError("No YouTube channel found for the authorized Google account.")
    ch = ch_items[0]
    print(f"Authorized YouTube Channel: {ch['snippet']['title']} (ID: {ch['id']})")
    uploaded: dict[str, str] = json.loads(STATE_FILE.read_text(encoding="utf-8")) if STATE_FILE.exists() else {}

    ist = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(ist)
    # Start at the next whole hour + 1h buffer, spaced 2 hours apart
    first_slot = (now_ist.replace(minute=0, second=0, microsecond=0) + timedelta(hours=2))

    for idx, ep in enumerate(EPISODES):
        eid = ep["id"]
        if eid in uploaded:
            print(f"[{eid}] Already uploaded -> https://youtu.be/{uploaded[eid]}")
            continue

        video_path = VIDEOS_DIR / f"{eid}.mp4"
        thumb_path = THUMB_DIR / THUMB_MAP[eid]
        if not video_path.exists():
            print(f"[{eid}] Missing video {video_path}, skipping.")
            continue

        publish_at = (first_slot + timedelta(hours=2 * idx)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        desc_lines = [ep["title"], "", "Cricket News Bulletin (Hinglish):", ""]
        for _, _, h_line in ep["beats"]:
            desc_lines.append(f"• {h_line}")
        desc_lines.append("\n#CricketNews #INDvsPAK #IPL2027 #TeamIndia #CricketUpdates")
        description = "\n".join(desc_lines)[:4900]

        body = {
            "snippet": {
                "title": ep["title"][:100],
                "description": description,
                "tags": ["cricket news", "indian cricket", "ipl 2027", "ind vs pak", "cricket highlights", "hindi cricket news"],
                "categoryId": "17",  # Sports
                "defaultLanguage": "hi",
            },
            "status": {
                "privacyStatus": "private",
                "publishAt": publish_at,
                "selfDeclaredMadeForKids": False,
            },
        }

        print(f"[{eid}] Uploading {video_path.name} scheduled for {publish_at} ...")
        try:
            req = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=MediaFileUpload(str(video_path), chunksize=8 * 1024 * 1024, resumable=True),
            )
            resp = None
            while resp is None:
                status, resp = req.next_chunk()
                if status:
                    print(f"  progress: {int(status.progress() * 100)}%")
            vid = resp["id"]
            print(f"  Uploaded video ID: {vid}")

            if thumb_path.exists():
                youtube.thumbnails().set(
                    videoId=vid,
                    media_body=MediaFileUpload(str(thumb_path)),
                ).execute()
                print(f"  Set clickbait thumbnail: {thumb_path.name}")

            uploaded[eid] = vid
            STATE_FILE.write_text(json.dumps(uploaded, indent=2), encoding="utf-8")
        except HttpError as e:
            print(f"  YouTube API error for {eid}: {e}")
            break


if __name__ == "__main__":
    main()
