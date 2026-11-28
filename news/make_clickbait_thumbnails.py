"""Create 1280x720 NeonMan-style clickbait thumbnails with bold text for all 7 episodes."""
from __future__ import annotations

import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT_DIR = Path(__file__).resolve().parent.parent
NEWS_DIR = Path(__file__).resolve().parent
BUILD_ROOT = NEWS_DIR / "build_episodes"
THUMB_DIR = NEWS_DIR / "thumbnails"
THUMB_DIR.mkdir(parents=True, exist_ok=True)

EP04_AI_THUMB = Path(r"C:\Users\ravih\.gemini\antigravity-cli\brain\5275fa44-0420-475e-9b54-8d5153fed182\ep_04_thumb_1795806035884.jpg")

THUMBS: list[dict] = [
    {
        "id": "ep_01_ind_pak_clash",
        "out": "ep_01_thumb.jpg",
        "left": "img_00.jpg",
        "right": "img_03.jpg",
        "top_text": "3X IND vs PAK?!",
        "bottom_text": "HARBHAJAN ANGRY!",
        "badge": "2027 WC",
        "accent": (255, 50, 50),
    },
    {
        "id": "ep_02_pak_asiacup_3in1",
        "out": "ep_02_thumb.jpg",
        "left": "img_00.jpg",
        "right": "img_05.jpg",
        "top_text": "BABAR IGNORES!",
        "bottom_text": "233 THRILLER!",
        "badge": "ASIA CUP",
        "accent": (255, 190, 0),
    },
    {
        "id": "ep_03_bilateral_tilak_2in1",
        "out": "ep_03_thumb.jpg",
        "left": "img_00.jpg",
        "right": "img_04.jpg",
        "top_text": "IND-PAK SERIES?!",
        "bottom_text": "BIG MISTAKE!",
        "badge": "EXPOSED",
        "accent": (255, 60, 40),
    },
    {
        "id": "ep_05_mi_rohit_bumrah_2in1",
        "out": "ep_05_thumb.jpg",
        "left": "img_04.jpg",
        "right": "img_00.jpg",
        "top_text": "ROHIT CAPTAIN!",
        "bottom_text": "BUMRAH REJECTS?!",
        "badge": "IPL 2027",
        "accent": (0, 175, 255),
    },
    {
        "id": "ep_06_ipl_psl_bcci_3in1",
        "out": "ep_06_thumb.jpg",
        "left": "img_06.jpg",
        "right": "img_09.jpg",
        "top_text": "IPL vs PSL CLASH!",
        "bottom_text": "12 TEAMS REJECTED!",
        "badge": "BCCI BIG NO",
        "accent": (255, 65, 35),
    },
    {
        "id": "ep_07_ind_nz_bumrah_3in1",
        "out": "ep_07_thumb.jpg",
        "left": "img_03.jpg",
        "right": "img_00.jpg",
        "top_text": "GAMBHIR SLAMMED!",
        "bottom_text": "SIRAJ OUT?!",
        "badge": "IND vs NZ",
        "accent": (255, 50, 50),
    },
]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for fp in (
        r"C:\Windows\Fonts\impact.ttf",
        r"C:\Windows\Fonts\seguibl.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
    ):
        if Path(fp).exists():
            return ImageFont.truetype(fp, size=size)
    return ImageFont.load_default()


def _fit_cover(img: Image.Image, w: int, h: int) -> Image.Image:
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    x0 = (nw - w) // 2
    y0 = max(0, (nh - h) // 3)
    return resized.crop((x0, y0, x0 + w, y0 + h))


def _draw_outlined_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    stroke: int = 8,
) -> None:
    x, y = xy
    # Hard drop shadow
    draw.text((x + 5, y + 6), text, font=font, fill=(0, 0, 0), anchor="mm")
    draw.text(
        (x, y),
        text,
        font=font,
        fill=fill,
        anchor="mm",
        stroke_width=stroke,
        stroke_fill=(10, 10, 14),
    )


def build_thumbnail(cfg: dict) -> Path:
    img_dir = BUILD_ROOT / cfg["id"] / "imgs"
    left_p = img_dir / cfg["left"]
    right_p = img_dir / cfg["right"]
    if not left_p.exists():
        left_p = sorted(img_dir.glob("img_*"))[0]
    if not right_p.exists():
        right_p = sorted(img_dir.glob("img_*"))[1]

    W, H = 1280, 720
    left_im = _fit_cover(Image.open(left_p).convert("RGB"), W // 2, H)
    right_im = _fit_cover(Image.open(right_p).convert("RGB"), W // 2, H)

    canvas = Image.new("RGB", (W, H))
    canvas.paste(left_im, (0, 0))
    canvas.paste(right_im, (W // 2, 0))

    # Boost contrast & color punch for YouTube clickbait look
    canvas = ImageEnhance.Contrast(canvas).enhance(1.22)
    canvas = ImageEnhance.Color(canvas).enhance(1.30)

    # Dark top/bottom gradient bars for ultra-readable text
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(180):
        alpha = int(205 * (1 - y / 180))
        od.line([(0, y), (W, y)], fill=(8, 10, 18, alpha))
    for y in range(H - 200, H):
        alpha = int(225 * ((y - (H - 200)) / 200))
        od.line([(0, y), (W, y)], fill=(8, 10, 18, alpha))

    # Diagonal glowing split divider
    ac = cfg["accent"]
    od.line([(W // 2 - 22, 0), (W // 2 + 22, H)], fill=(*ac, 230), width=14)
    od.line([(W // 2 - 22, 0), (W // 2 + 22, H)], fill=(255, 255, 255, 240), width=4)

    # Outer clickbait border
    od.rectangle([4, 4, W - 5, H - 5], outline=(*ac, 245), width=9)

    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(canvas)

    # Top & bottom giant clickbait text
    font_big = _load_font(102)
    font_sub = _load_font(94)
    font_badge = _load_font(42)

    _draw_outlined_text(draw, (W // 2, 78), cfg["top_text"], font_big, (255, 224, 30), stroke=9)
    _draw_outlined_text(draw, (W // 2, H - 82), cfg["bottom_text"], font_sub, (255, 255, 255), stroke=9)

    # Center-right pill badge
    badge_txt = cfg["badge"]
    bbox = draw.textbbox((0, 0), badge_txt, font=font_badge)
    bw = bbox[2] - bbox[0] + 44
    bh = bbox[3] - bbox[1] + 26
    bx0 = (W - bw) // 2
    by0 = (H - bh) // 2
    draw.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh], radius=16, fill=ac, outline=(255, 255, 255), width=4)
    draw.text((W // 2, H // 2 - 2), badge_txt, font=font_badge, fill=(255, 255, 255), anchor="mm")

    out_p = THUMB_DIR / cfg["out"]
    canvas.save(out_p, quality=95)
    return out_p


def main() -> None:
    if EP04_AI_THUMB.exists():
        im4 = Image.open(EP04_AI_THUMB).convert("RGB").resize((1280, 720), Image.Resampling.LANCZOS)
        out4 = THUMB_DIR / "ep_04_thumb.jpg"
        im4.save(out4, quality=95)
        print(f"Saved AI thumbnail -> {out4.name}")
    for cfg in THUMBS:
        p = build_thumbnail(cfg)
        print(f"Saved clickbait thumbnail -> {p.name}")


if __name__ == "__main__":
    main()
