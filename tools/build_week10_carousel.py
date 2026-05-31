"""Midnight Atelier carousel — 10 slides at 1080x1350 portrait. Founder Bottleneck Audit."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import img2pdf

OUT_DIR = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\social_media")
TMP_DIR = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\week10_slides")
TMP_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1350
MARGIN = 110

# Midnight Atelier palette
BG = (15, 26, 46)            # deep midnight navy #0F1A2E
GRID = (26, 37, 56)           # slightly lighter navy for subtle grid
INK = (240, 233, 221)         # warm bone ivory #F0E9DD
INK_SOFT = (184, 176, 163)    # muted bone for secondary
COPPER = (201, 125, 88)       # warm copper #C97D58
GRAY = (110, 118, 130)        # cool gray for page numbers

FONTS = Path(r"C:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS\.claude\skills\canvas-design\canvas-fonts")

def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)

def place_motif(target_img, motif_filename, position, size):
    """Apply alpha extraction + copper recolor + place on target image."""
    from PIL import ImageOps
    motif_path = Path(rf"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\images\{motif_filename}")
    if not motif_path.exists():
        return
    src = Image.open(motif_path).convert("RGB")
    gray = ImageOps.grayscale(src)
    alpha = ImageOps.invert(gray)
    alpha = alpha.point(lambda v: 0 if v < 40 else min(255, int(v * 1.3)))
    copper_layer = Image.new("RGBA", src.size, COPPER + (255,))
    copper_layer.putalpha(alpha)
    motif = copper_layer.resize(size, Image.LANCZOS)
    target_img.paste(motif, position, motif)

def make_canvas():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    # Subtle grid: faint horizontal lines every 60px, verticals every 90
    for y in range(0, H, 60):
        draw.line([(0, y), (W, y)], fill=GRID, width=1)
    for x in range(0, W, 90):
        draw.line([(x, 0), (x, H)], fill=GRID, width=1)
    # Top + bottom hairlines (copper) — codex frame
    draw.line([(MARGIN, 80), (W - MARGIN, 80)], fill=COPPER, width=2)
    draw.line([(MARGIN, H - 80), (W - MARGIN, H - 80)], fill=COPPER, width=2)
    return img, draw

def draw_meta(draw, slide_num, label_top="MIDNIGHT ATELIER"):
    f_meta = font("InstrumentSans-Regular.ttf", 16)
    draw.text((MARGIN, 50), label_top, fill=COPPER, font=f_meta)
    page_str = f"{slide_num}/10"
    f_page = font("IBMPlexMono-Regular.ttf", 18)
    bbox = draw.textbbox((0, 0), page_str, font=f_page)
    pw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - pw, H - 60), page_str, fill=GRAY, font=f_page)
    f_mark = font("IBMPlexMono-Regular.ttf", 14)
    draw.text((MARGIN, H - 58), "DUX MACHINA / OPERATOR'S MANUAL", fill=GRAY, font=f_mark)

def wrap_text(draw, text, font_obj, max_width):
    words = text.split()
    lines, current = [], []
    for word in words:
        test = " ".join(current + [word])
        bbox = draw.textbbox((0, 0), test, font=font_obj)
        if bbox[2] - bbox[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines

# ============= SLIDE 1: COVER =============
def slide_1():
    img, draw = make_canvas()
    place_motif(img, "week10_motif_test_labyrinth.png", ((W - 340) // 2, 820), (340, 340))
    draw_meta(draw, 1)
    f_eye = font("IBMPlexMono-Regular.ttf", 18)
    draw.text((MARGIN, 200), "I.   THE FOUNDER AUDIT", fill=COPPER, font=f_eye)

    f_h = font("InstrumentSerif-Regular.ttf", 72)
    headline = [
        "Most founders hire",
        "to escape a problem",
        "they ARE."
    ]
    y = 320
    for line in headline:
        if "ARE" in line:
            parts = line.split("ARE")
            x = MARGIN
            draw.text((x, y), parts[0], fill=INK, font=f_h)
            x += draw.textbbox((0, 0), parts[0], font=f_h)[2]
            draw.text((x, y), "ARE", fill=COPPER, font=f_h)
            x += draw.textbbox((0, 0), "ARE", font=f_h)[2]
            draw.text((x, y), parts[1], fill=INK, font=f_h)
        else:
            draw.text((MARGIN, y), line, fill=INK, font=f_h)
        y += 90

    f_sub = font("InstrumentSerif-Italic.ttf" if (FONTS / "InstrumentSerif-Italic.ttf").exists() else "CrimsonPro-Italic.ttf", 32)
    draw.text((MARGIN, 700), "Here is how we audit it", fill=INK_SOFT, font=f_sub)
    draw.text((MARGIN, 740), "before the next hire.", fill=INK_SOFT, font=f_sub)

    f_label = font("InstrumentSans-Regular.ttf", 18)
    draw.text((MARGIN, 1180), "FIELD NOTE NO. 10", fill=COPPER, font=f_label)
    draw.text((MARGIN, 1210), "Cross-industry systems consultancy", fill=INK_SOFT, font=f_label)
    img.save(TMP_DIR / "slide_01.png")

# ============= SLIDE 2: THE PATTERN =============
def slide_2():
    img, draw = make_canvas()
    place_motif(img, "week10_motif_hourglass.png", (720, 460), (280, 380))
    draw_meta(draw, 2)
    f_eye = font("IBMPlexMono-Regular.ttf", 18)
    draw.text((MARGIN, 200), "II.  THE PATTERN", fill=COPPER, font=f_eye)
    f_t = font("InstrumentSerif-Regular.ttf", 64)
    draw.text((MARGIN, 270), "Six months", fill=INK, font=f_t)
    draw.text((MARGIN, 340), "after the hire.", fill=INK, font=f_t)

    f_b = font("InstrumentSans-Regular.ttf", 30)
    lines = [
        "The calendar is still full.",
        "The fires are still burning.",
        "The founder wonders if they",
        "hired the wrong person.",
    ]
    y = 540
    for line in lines:
        draw.text((MARGIN, y), line, fill=INK, font=f_b)
        y += 50

    draw.line([(MARGIN, 800), (W - MARGIN, 800)], fill=COPPER, width=1)

    f_em = font("InstrumentSerif-Italic.ttf" if (FONTS / "InstrumentSerif-Italic.ttf").exists() else "CrimsonPro-Italic.ttf", 38)
    draw.text((MARGIN, 870), "The hire is rarely", fill=INK, font=f_em)
    draw.text((MARGIN, 920), "the problem.", fill=COPPER, font=f_em)
    img.save(TMP_DIR / "slide_02.png")

# ============= SYMPTOM SLIDES (3-7) =============
def symptom_slide(slide_num, roman, title, body_lines):
    img, draw = make_canvas()
    draw_meta(draw, slide_num)
    # Big roman numeral as the visual anchor
    f_roman = font("InstrumentSerif-Regular.ttf", 220)
    bbox = draw.textbbox((0, 0), roman, font=f_roman)
    rw = bbox[2] - bbox[0]
    draw.text((MARGIN, 180), roman, fill=COPPER, font=f_roman)

    # Section label below roman
    f_eye = font("IBMPlexMono-Regular.ttf", 16)
    draw.text((MARGIN, 460), f"SYMPTOM {slide_num - 2}", fill=INK_SOFT, font=f_eye)

    # Title
    f_t = font("InstrumentSerif-Regular.ttf", 56)
    draw.text((MARGIN, 510), title, fill=INK, font=f_t)

    # Body
    f_b = font("InstrumentSans-Regular.ttf", 28)
    y = 690
    for line in body_lines:
        wrapped = wrap_text(draw, line, f_b, W - 2 * MARGIN)
        for w_line in wrapped:
            draw.text((MARGIN, y), w_line, fill=INK, font=f_b)
            y += 42
        y += 16
    img.save(TMP_DIR / f"slide_{slide_num:02d}.png")

def slide_3():
    symptom_slide(3, "I.", "The approval bottleneck.", [
        "Every decision over a few thousand dollars routes back to you.",
        "The team has stopped trying without checking.",
        "Velocity collapses. Ownership disappears.",
    ])

def slide_4():
    symptom_slide(4, "II.", "The only seller.", [
        "Enterprise deals close on your calendar.",
        "Customers ask for you by name.",
        "The operator has become the product.",
    ])

def slide_5():
    symptom_slide(5, "III.", "The repetitive author.", [
        "Same intro, fourteenth vendor.",
        "Same pitch, twenty-second investor.",
        "Same email, eighteen versions deep.",
        "Every one is a system that should exist.",
    ])

def slide_6():
    symptom_slide(6, "IV.", "The only answer.", [
        "Customer support lands on your desk.",
        "Technical questions land on your desk.",
        "Operational fires land on your desk.",
        "Three systems, one human being.",
    ])

def slide_7():
    symptom_slide(7, "V.", "The deciding voice.", [
        "Every meeting waits for your weigh-in.",
        "Consensus without you is provisional.",
        "Decisions stall in your calendar.",
    ])

# ============= SLIDE 8: THE REFRAME =============
def slide_8():
    img, draw = make_canvas()
    place_motif(img, "week10_motif_gears.png", ((W - 420) // 2, 950), (420, 220))
    draw_meta(draw, 8)
    f_eye = font("IBMPlexMono-Regular.ttf", 18)
    draw.text((MARGIN, 200), "VIII. THE REFRAME", fill=COPPER, font=f_eye)

    f_h = font("InstrumentSerif-Regular.ttf", 72)
    draw.text((MARGIN, 320), "The fix is rarely", fill=INK, font=f_h)
    draw.text((MARGIN, 405), "a hire.", fill=COPPER, font=f_h)

    draw.line([(MARGIN, 560), (W - MARGIN, 560)], fill=COPPER, width=1)

    f_step_n = font("IBMPlexMono-Regular.ttf", 18)
    f_step = font("InstrumentSerif-Regular.ttf", 36)
    steps = [
        "Map which one you do.",
        "Build the system that absorbs it.",
        "Then hand the system to a person.",
    ]
    y = 650
    for i, step in enumerate(steps):
        draw.text((MARGIN, y + 8), f"0{i+1}", fill=COPPER, font=f_step_n)
        draw.text((MARGIN + 70, y), step, fill=INK, font=f_step)
        y += 90
    img.save(TMP_DIR / "slide_08.png")

# ============= SLIDE 9: CROSS-INDUSTRY =============
def slide_9():
    img, draw = make_canvas()
    place_motif(img, "week10_motif_network.png", (700, 440), (300, 300))
    draw_meta(draw, 9)
    f_eye = font("IBMPlexMono-Regular.ttf", 18)
    draw.text((MARGIN, 200), "IX.  THE ARCHITECTURE TRAVELS", fill=COPPER, font=f_eye)
    f_t = font("InstrumentSerif-Regular.ttf", 56)
    draw.text((MARGIN, 270), "Same audit applies to:", fill=INK, font=f_t)

    items = [
        "Founder-led services firms",
        "Growth-stage SaaS",
        "Multi-location operators",
        "Family-owned manufacturers",
        "Anyone who built it themselves",
    ]
    f_n = font("IBMPlexMono-Regular.ttf", 18)
    f_b = font("InstrumentSerif-Regular.ttf", 32)
    y = 510
    for i, item in enumerate(items):
        draw.text((MARGIN, y + 8), f"0{i+1}", fill=COPPER, font=f_n)
        draw.text((MARGIN + 70, y), item, fill=INK, font=f_b)
        y += 80
    img.save(TMP_DIR / "slide_09.png")

# ============= SLIDE 10: CLOSE =============
def slide_10():
    img, draw = make_canvas()
    place_motif(img, "week10_motif_door.png", (700, 280), (280, 380))
    draw_meta(draw, 10)
    f_eye = font("IBMPlexMono-Regular.ttf", 18)
    draw.text((MARGIN, 200), "X.   THE INVITATION", fill=COPPER, font=f_eye)

    f_h = font("InstrumentSerif-Regular.ttf", 56)
    draw.text((MARGIN, 320), "If three or more", fill=INK, font=f_h)
    draw.text((MARGIN, 390), "ring true,", fill=INK, font=f_h)

    f_em = font("InstrumentSerif-Italic.ttf" if (FONTS / "InstrumentSerif-Italic.ttf").exists() else "CrimsonPro-Italic.ttf", 50)
    draw.text((MARGIN, 540), "the next hire is not", fill=INK_SOFT, font=f_em)
    draw.text((MARGIN, 605), "your problem.", fill=INK_SOFT, font=f_em)
    f_em2 = font("InstrumentSerif-Regular.ttf", 56)
    draw.text((MARGIN, 700), "You are.", fill=COPPER, font=f_em2)

    draw.line([(MARGIN, 880), (W - MARGIN, 880)], fill=COPPER, width=1)
    draw.line([(MARGIN, 1100), (W - MARGIN, 1100)], fill=COPPER, width=1)

    f_cta_eye = font("IBMPlexMono-Regular.ttf", 16)
    draw.text((MARGIN, 920), "DIRECT CORRESPONDENCE", fill=COPPER, font=f_cta_eye)
    f_cta = font("InstrumentSerif-Italic.ttf" if (FONTS / "InstrumentSerif-Italic.ttf").exists() else "CrimsonPro-Italic.ttf", 30)
    cta = [
        "Send a message if you want",
        "to see what this audit looks like",
        "for your specific stack.",
    ]
    y = 960
    for line in cta:
        draw.text((MARGIN, y), line, fill=INK, font=f_cta)
        y += 42
    img.save(TMP_DIR / "slide_10.png")

# Build all
for fn in [slide_1, slide_2, slide_3, slide_4, slide_5, slide_6, slide_7, slide_8, slide_9, slide_10]:
    fn()
    print(f"  {fn.__name__} done")

# Combine into PDF
slides = sorted(TMP_DIR.glob("slide_*.png"))
pdf_path = OUT_DIR / "week10_monday_carousel.pdf"
with open(pdf_path, "wb") as f:
    f.write(img2pdf.convert([str(s) for s in slides]))
print(f"\nPDF: {pdf_path}")
print(f"Size: {pdf_path.stat().st_size / 1024:.1f} KB")
print(f"Slides: {len(slides)}")
