#!/usr/bin/env python3
"""Generate flat graphic icons (NOT photos) for catalog steps."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "images"
W, H = 800, 450

THEMES = {
    "cat_main": ("Основна оптика", "#0B1F3A", "#3D9BE9", "◉"),
    "cat_ptf": ("ПТФ", "#1A1028", "#C084FC", "▣"),
    "led": ("LED", "#0A1628", "#22D3EE", "◆"),
    "biled": ("Bi-LED", "#0A1628", "#38BDF8", "◈"),
    "laser": ("Лазерні", "#140A1E", "#E879F9", "✦"),
    "xenon": ("Ксенон", "#0F172A", "#FBBF24", "◎"),
    "ptf_led": ("LED ПТФ", "#1A1028", "#A78BFA", "▣"),
    "ptf_xen": ("Ксенон ПТФ", "#1A1028", "#F59E0B", "▣"),
    "aozoom": ("Aozoom", "#111827", "#60A5FA", "AZ"),
    "sanvi": ("Sanvi", "#111827", "#34D399", "SV"),
    "brand": ("Марка авто", "#0F172A", "#94A3B8", "M"),
    "model": ("Модель", "#0F172A", "#94A3B8", "▢"),
    "year": ("Рік", "#0F172A", "#94A3B8", "Y"),
    "side_l": ("Ліва", "#0B1220", "#38BDF8", "◀"),
    "side_r": ("Права", "#0B1220", "#38BDF8", "▶"),
    "side_pair": ("Пара", "#0B1220", "#22C55E", "◀▶"),
    "order": ("Замовлення", "#052E16", "#4ADE80", "✓"),
    "home": ("Меню", "#0F172A", "#E2E8F0", "⌂"),
    "default": ("Каталог", "#0F172A", "#64748B", "•"),
}


def font(size: int):
    for p in (
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def make(key, title, bg, accent, mark):
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2 - 20
    for r, w in ((160, 10), (120, 6), (80, 4)):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=accent, width=w)
    d.ellipse((cx - 28, cy - 28, cx + 28, cy + 28), fill=accent)
    d.rectangle((0, 0, W, 8), fill=accent)
    d.rectangle((0, H - 8, W, H), fill=accent)
    f1, f2 = font(48), font(28)
    d.rounded_rectangle((40, 40, 140, 100), radius=16, fill=accent)
    bbox = d.textbbox((0, 0), mark, font=f2)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((90 - tw / 2, 70 - th / 2), mark, fill=bg, font=f2)
    bbox = d.textbbox((0, 0), title, font=f1)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) / 2, H - 90), title, fill="#F8FAFC", font=f1)
    d.text((40, H - 40), "DEMO - grafika - bez foto", fill="#64748B", font=font(18))
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / f"{key}.png", "PNG")


if __name__ == "__main__":
    for k, (title, bg, accent, mark) in THEMES.items():
        make(k, title, bg, accent, mark)
    print(f"OK: {len(THEMES)} images -> {OUT}")