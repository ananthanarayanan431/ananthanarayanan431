"""Generate a neofetch-style profile card PNG from the GitHub avatar.

Run once (not wired into CI): python3 scripts/generate_neofetch.py
Writes assets/neofetch.png, which the README embeds directly.
"""

import io
import subprocess

from PIL import Image, ImageDraw, ImageFont

USERNAME = "ananthanarayanan431"
AVATAR_URL = f"https://github.com/{USERNAME}.png?size=460"
OUT_PATH = "assets/neofetch.png"
FONT_PATH = "/System/Library/Fonts/Menlo.ttc"

BG = (17, 20, 28)
TITLEBAR = (22, 25, 37)
ACCENT = (74, 157, 255)  # matches the #4A9DFF accent used elsewhere in the README
TEXT = (200, 211, 245)
MUTED = (86, 95, 137)
DOT_RED, DOT_YEL, DOT_GRN = (255, 95, 86), (255, 189, 46), (39, 201, 63)
PALETTE = [
    (15, 32, 39), (32, 58, 67), (44, 83, 100), (74, 157, 255),
    (86, 95, 137), (200, 211, 245), (39, 201, 63), (255, 189, 46),
]

ASCII_RAMP = " .:-=+*#%@"
ART_COLS, ART_ROWS = 50, 27
CELL_W, CELL_H = 7, 13

CANVAS_W, CANVAS_H = 1100, 560
TITLEBAR_H = 34
MARGIN_X, MARGIN_Y = 40, 60


def fetch_avatar():
    data = subprocess.run(
        ["curl", "-sL", AVATAR_URL], check=True, capture_output=True
    ).stdout
    return Image.open(io.BytesIO(data)).convert("RGB")


def draw_ascii_art(draw, avatar, origin_x, origin_y, font):
    small = avatar.resize((ART_COLS, ART_ROWS), Image.LANCZOS)
    pixels = small.load()
    for y in range(ART_ROWS):
        for x in range(ART_COLS):
            r, g, b = pixels[x, y]
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            idx = min(len(ASCII_RAMP) - 1, int(lum * (len(ASCII_RAMP) - 1) * 1.15))
            ch = ASCII_RAMP[idx]
            if ch != " ":
                draw.text((origin_x + x * CELL_W, origin_y + y * CELL_H), ch, font=font, fill=(r, g, b))


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
    for i, color in enumerate([DOT_RED, DOT_YEL, DOT_GRN]):
        cx = 20 + i * 22
        draw.ellipse([cx - 6, TITLEBAR_H // 2 - 6, cx + 6, TITLEBAR_H // 2 + 6], fill=color)
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
        ("Connect", "LinkedIn / GitHub / Medium / X"),
    ]
    for label, value in rows:
        if label:
            draw_stat_line(draw, mono, text_x, y, label, value)
        y += 24

    y += 6
    for i, color in enumerate(PALETTE):
        sx = text_x + i * 26
        draw.rectangle([sx, y, sx + 20, y + 20], fill=color)

    img.save(OUT_PATH)
    print(f"wrote {OUT_PATH} ({CANVAS_W}x{CANVAS_H})")


if __name__ == "__main__":
    main()
