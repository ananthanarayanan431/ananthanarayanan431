"""Generate a neofetch-style profile card PNG from the GitHub avatar.

Run once (not wired into CI): python3 scripts/generate_neofetch.py
Requires: pip install rembg onnxruntime (used to cut the subject out of its background)
Writes assets/neofetch.png, which the README embeds directly.
"""

import io
import subprocess

from PIL import Image, ImageDraw, ImageFont
from rembg import remove

USERNAME = "ananthanarayanan431"
AVATAR_URL = f"https://github.com/{USERNAME}.png?size=460"
OUT_PATH = "assets/neofetch.png"
FONT_PATH = "/System/Library/Fonts/Menlo.ttc"

# Strictly grayscale palette - no hue anywhere in the image.
BG = (10, 10, 10)
TITLEBAR = (24, 24, 24)
ACCENT = (245, 245, 245)
TEXT = (170, 170, 170)
MUTED = (75, 75, 75)
DOT = (90, 90, 90)

ASCII_RAMP = " .:-=+*#%@"
ART_COLS, ART_ROWS = 50, 27
CELL_W, CELL_H = 7, 13

CANVAS_W, CANVAS_H = 1100, 620
TITLEBAR_H = 34
MARGIN_X, MARGIN_Y = 40, 60


def fetch_avatar():
    data = subprocess.run(
        ["curl", "-sL", AVATAR_URL], check=True, capture_output=True
    ).stdout
    photo = Image.open(io.BytesIO(data)).convert("RGB")
    return remove(photo)  # RGBA, background made transparent


def draw_ascii_art(draw, avatar, origin_x, origin_y, font):
    small = avatar.resize((ART_COLS, ART_ROWS), Image.LANCZOS)
    pixels = small.load()
    for y in range(ART_ROWS):
        for x in range(ART_COLS):
            r, g, b, a = pixels[x, y]
            if a < 128:
                continue  # background was removed - leave this cell blank
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            idx = min(len(ASCII_RAMP) - 1, int(lum * (len(ASCII_RAMP) - 1) * 1.15))
            ch = ASCII_RAMP[idx]
            if ch != " ":
                # brighter pixels render as lighter gray, matching the source contrast
                shade = int(60 + lum * 195)
                draw.text((origin_x + x * CELL_W, origin_y + y * CELL_H), ch, font=font, fill=(shade, shade, shade))


def draw_stat_line(draw, mono, x, y, label, value, dot_target_px=205):
    draw.text((x, y), label, font=mono, fill=ACCENT)
    label_w = draw.textlength(label, font=mono)
    dot_w = draw.textlength(".", font=mono)
    dots_needed = max(1, int((dot_target_px - label_w) / dot_w))
    draw.text((x + label_w, y), " " + "." * dots_needed + " ", font=mono, fill=MUTED)
    value_x = x + dot_target_px + dot_w * 2
    draw.text((value_x, y), value, font=mono, fill=TEXT)


def main():
    avatar = fetch_avatar()
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, CANVAS_W, TITLEBAR_H], fill=TITLEBAR)
    for i in range(3):
        cx = 20 + i * 22
        draw.ellipse([cx - 6, TITLEBAR_H // 2 - 6, cx + 6, TITLEBAR_H // 2 + 6], outline=DOT, width=2)
    title_font = ImageFont.truetype(FONT_PATH, 14)
    draw.text((CANVAS_W // 2, TITLEBAR_H // 2), f"anantha@{USERNAME}: ~", font=title_font, fill=MUTED, anchor="mm")

    art_font = ImageFont.truetype(FONT_PATH, 12)
    draw_ascii_art(draw, avatar, MARGIN_X, MARGIN_Y, art_font)

    mono = ImageFont.truetype(FONT_PATH, 13)
    mono_header = ImageFont.truetype(FONT_PATH, 16)

    text_x = MARGIN_X + ART_COLS * CELL_W + 50
    y = MARGIN_Y

    draw.text((text_x, y), f"anantha@{USERNAME}", font=mono_header, fill=ACCENT)
    y += 26
    draw.text((text_x, y), "-" * 30, font=mono, fill=MUTED)
    y += 30

    rows = [
        ("OS", "Linux / macOS"),
        ("Role", "GenAI / Agent Engineer"),
        ("Host", "Agent Drops"),
        ("Editor", "VS Code"),
        ("", ""),
        ("Languages.Programming", "Python, TypeScript, JavaScript, Java, C++, C"),
        ("Languages.Frameworks", "LangChain, LangGraph, FastAPI, React"),
        ("Languages.Real", "English"),
        ("", ""),
        ("Currently", "market-research-agent"),
        ("Exploring", "MCP, A2A interoperability"),
        ("", ""),
        ("Public Repos", "79"),
        ("Top Starred", "Langchain-Projects-LLM (100+)"),
        ("", ""),
        ("Email", "ananthanaryanan431@gmail.com"),
        ("GitHub", "ananthanarayanan431"),
        ("LinkedIn", "rananthanarayananofficial"),
        ("Instagram", "anantha.narayanan_"),
        ("X", "@AnanthaNara2810"),
    ]
    for label, value in rows:
        if label:
            draw_stat_line(draw, mono, text_x, y, label, value)
        y += 24

    img.save(OUT_PATH)
    print(f"wrote {OUT_PATH} ({CANVAS_W}x{CANVAS_H})")


if __name__ == "__main__":
    main()
