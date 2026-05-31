"""Week 11 Monday — Medical Diagnostic Imaging style.
Pure black, sterile white text, cool cyan accent, monospace clinical aesthetic."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\social_media\week11_mon_image.png")
MOTIF = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\images\week11_motif_xray_building.png")

W, H = 1080, 1350
MARGIN = 80

# Medical Diagnostic palette — completely different from Midnight Atelier
BG = (8, 10, 14)              # near-pure black, slight cool tint
INK = (235, 240, 245)         # sterile white with cool tint
INK_SOFT = (140, 155, 170)    # muted gray-blue
CYAN = (122, 200, 220)        # x-ray glow cyan
CYAN_DIM = (60, 100, 120)     # dim cyan for hairlines
SIGNAL = (200, 220, 230)      # data white

FONTS = Path(r"C:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS\.claude\skills\canvas-design\canvas-fonts")

def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# Subtle scanlines — very faint, like a CRT/medical display
for y in range(0, H, 3):
    draw.line([(0, y), (W, y)], fill=(12, 14, 18), width=1)

# Top + bottom hairlines in cyan
draw.line([(MARGIN, 60), (W - MARGIN, 60)], fill=CYAN_DIM, width=1)
draw.line([(MARGIN, H - 60), (W - MARGIN, H - 60)], fill=CYAN_DIM, width=1)

# Header bar — clinical metadata
f_mono_small = font("JetBrainsMono-Regular.ttf", 14)
f_mono_med = font("JetBrainsMono-Regular.ttf", 16)

# Top-left: file identifier
draw.text((MARGIN, 80), "FILE / 0011", fill=CYAN, font=f_mono_med)
# Top-right: timestamp/classification
case_id = "OPS-DIAGNOSTIC-2026-05-18"
bbox = draw.textbbox((0, 0), case_id, font=f_mono_small)
draw.text((W - MARGIN - (bbox[2] - bbox[0]), 84), case_id, fill=INK_SOFT, font=f_mono_small)

# Subtitle line
draw.text((MARGIN, 110), "PRESENTING_SYMPTOMS / UNDERLYING_SYSTEMS", fill=INK_SOFT, font=f_mono_small)

# Divider after header
draw.line([(MARGIN, 145), (W - MARGIN, 145)], fill=CYAN_DIM, width=1)

# Hero headline — using JetBrainsMono Bold for clinical hard-hitting feel
f_h = font("JetBrainsMono-Bold.ttf", 38)
headline_lines = [
    "MOST OPERATORS",
    "MISDIAGNOSE WHAT IS",
    "ACTUALLY BROKEN.",
]
y = 190
for line in headline_lines:
    draw.text((MARGIN, y), line, fill=INK, font=f_h)
    y += 52

# Place X-ray motif (it's already black bg with white lines — use directly)
src = Image.open(MOTIF).convert("RGB")
motif = src.resize((420, 420), Image.LANCZOS)
img.paste(motif, ((W - 420) // 2, 370))

# Caption under motif
f_cap = font("JetBrainsMono-Regular.ttf", 13)
caption = "FIG. 01 / OPERATIONAL CROSS-SECTION / X-RAY VIEW"
bbox = draw.textbbox((0, 0), caption, font=f_cap)
draw.text(((W - (bbox[2] - bbox[0])) // 2, 805), caption, fill=INK_SOFT, font=f_cap)

# Divider before pairs
draw.line([(MARGIN, 850), (W - MARGIN, 850)], fill=CYAN_DIM, width=1)

# Pairs table header
draw.text((MARGIN, 870), "PRESENTING", fill=CYAN, font=f_mono_small)
draw.text((W // 2 + 20, 870), "UNDERLYING", fill=CYAN, font=f_mono_small)

# 4 paired rows in clinical chart format
f_pair = font("JetBrainsMono-Regular.ttf", 17)
pairs = [
    ('"Sales is slow."',           "lead routing / follow-up cadence"),
    ('"Team is overwhelmed."',     "meeting cost / approval bottleneck"),
    ('"Marketing isn\'t working."', "retention / existing-lead math"),
    ('"Customer churn is rising."', "post-sale handoff / first 90 days"),
]
y = 905
for left, right in pairs:
    # Symptom in dim white
    draw.text((MARGIN, y), left, fill=SIGNAL, font=f_pair)
    # Arrow in cyan
    draw.text((W // 2 - 10, y), "->", fill=CYAN, font=f_pair)
    # System in white
    draw.text((W // 2 + 20, y), right, fill=INK, font=f_pair)
    y += 38

# Divider before close
draw.line([(MARGIN, 1090), (W - MARGIN, 1090)], fill=CYAN_DIM, width=1)

# Closing reframe — sterile diagnostic
f_close_label = font("JetBrainsMono-Regular.ttf", 14)
draw.text((MARGIN, 1110), "DIAGNOSTIC NOTE", fill=CYAN, font=f_close_label)
f_close = font("JetBrainsMono-Regular.ttf", 22)
draw.text((MARGIN, 1145), "The symptom is visible.", fill=INK_SOFT, font=f_close)
draw.text((MARGIN, 1180), "The system that produced it is not.", fill=INK, font=f_close)

# Footer mark
f_footer = font("JetBrainsMono-Regular.ttf", 12)
draw.text((MARGIN, H - 40), "DUX MACHINA / DIAGNOSTIC IMAGING", fill=INK_SOFT, font=f_footer)

img.save(OUT)
print(f"Saved: {OUT}")
print(f"Size: {OUT.stat().st_size / 1024:.1f} KB")
