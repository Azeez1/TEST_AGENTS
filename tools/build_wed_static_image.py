"""Wednesday post static image — Midnight Atelier palette. Single composition."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\social_media\week10_wed_image.png")
W, H = 1080, 1350
MARGIN = 110

BG = (15, 26, 46)
GRID = (26, 37, 56)
INK = (240, 233, 221)
INK_SOFT = (184, 176, 163)
COPPER = (201, 125, 88)
GRAY = (110, 118, 130)

FONTS = Path(r"C:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS\.claude\skills\canvas-design\canvas-fonts")

def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# Subtle grid
for y in range(0, H, 60):
    draw.line([(0, y), (W, y)], fill=GRID, width=1)
for x in range(0, W, 90):
    draw.line([(x, 0), (x, H)], fill=GRID, width=1)

# Top + bottom hairlines
draw.line([(MARGIN, 80), (W - MARGIN, 80)], fill=COPPER, width=2)
draw.line([(MARGIN, H - 80), (W - MARGIN, H - 80)], fill=COPPER, width=2)

# Top meta
f_meta = font("InstrumentSans-Regular.ttf", 16)
draw.text((MARGIN, 50), "FIELD NOTE — INDECISION", fill=COPPER, font=f_meta)

# Eyebrow
f_eye = font("IBMPlexMono-Regular.ttf", 18)
draw.text((MARGIN, 170), "VOL. II   |   THE JOLT EFFECT", fill=COPPER, font=f_eye)

# Hero headline — the savable inertia line
f_h = font("InstrumentSerif-Regular.ttf", 78)
headline = [
    "The deal was not",
    "lost to a vendor.",
]
y = 280
for line in headline:
    draw.text((MARGIN, y), line, fill=INK, font=f_h)
    y += 90

# Beat line — italic
f_em = font("InstrumentSerif-Italic.ttf" if (FONTS / "InstrumentSerif-Italic.ttf").exists() else "CrimsonPro-Italic.ttf", 78)
draw.text((MARGIN, 470), "It was lost to inertia.", fill=COPPER, font=f_em)

# Divider
draw.line([(MARGIN, 620), (W - MARGIN, 620)], fill=COPPER, width=1)

# The supporting stat block
f_stat_label = font("IBMPlexMono-Regular.ttf", 16)
draw.text((MARGIN, 670), "THE MATH", fill=COPPER, font=f_stat_label)

# Big 56% in copper
f_big = font("InstrumentSerif-Regular.ttf", 200)
draw.text((MARGIN, 720), "56%", fill=COPPER, font=f_big)

# Supporting text next to / below the big number
f_body = font("InstrumentSans-Regular.ttf", 26)
body_lines = [
    "of B2B 'no decision' losses are buyers",
    "who told the seller they wanted to change,",
    "agreed the status quo was hurting them,",
    "and still could not commit.",
]
y = 740
for line in body_lines:
    draw.text((MARGIN + 340, y), line, fill=INK, font=f_body)
    y += 36

# Bottom hairline before source
draw.line([(MARGIN, 1100), (W - MARGIN, 1100)], fill=COPPER, width=1)

# Source citation
f_src_label = font("IBMPlexMono-Regular.ttf", 14)
draw.text((MARGIN, 1130), "SOURCE", fill=GRAY, font=f_src_label)
f_src = font("InstrumentSans-Regular.ttf", 20)
draw.text((MARGIN, 1160), "Matt Dixon and Ted McKenna, The Jolt Effect (2022).", fill=INK_SOFT, font=f_src)
draw.text((MARGIN, 1190), "2.5 million B2B sales calls analyzed.", fill=INK_SOFT, font=f_src)

# Footer
f_footer = font("IBMPlexMono-Regular.ttf", 14)
draw.text((MARGIN, H - 58), "DUX MACHINA / OPERATOR'S MANUAL", fill=GRAY, font=f_footer)

img.save(OUT)
print(f"Saved: {OUT}")
print(f"Size: {OUT.stat().st_size / 1024:.1f} KB")
