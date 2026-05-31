"""Builder's Codex carousel — 8 slides at 1080x1350 portrait, output as PDF."""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import img2pdf

OUT_DIR = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\social_media")
TMP_DIR = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\week9_slides")
TMP_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1350
MARGIN = 110

# Builder's Codex palette
BG = (245, 241, 232)        # aged cream
GRID = (228, 222, 210)      # faint grid line
INK = (26, 26, 26)           # charcoal
INK_SOFT = (60, 60, 60)
GOLD = (201, 169, 97)        # champagne
GRAY = (160, 156, 148)       # page numbers, secondary

FONTS = Path(r"C:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS\.claude\skills\canvas-design\canvas-fonts")

def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)

# Pre-load font sizes used across slides
def make_canvas():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    # Subtle grid — very faint horizontal lines every 60px
    for y in range(0, H, 60):
        draw.line([(0, y), (W, y)], fill=GRID, width=1)
    # Verticals every 90px
    for x in range(0, W, 90):
        draw.line([(x, 0), (x, H)], fill=GRID, width=1)
    # Top hairline + bottom hairline (gold) — the codex frame
    draw.line([(MARGIN, 80), (W - MARGIN, 80)], fill=GOLD, width=2)
    draw.line([(MARGIN, H - 80), (W - MARGIN, H - 80)], fill=GOLD, width=2)
    return img, draw

def draw_meta(draw, slide_num, label_top="BUILDER'S CODEX"):
    # Top label small caps, gold
    f_meta = font("InstrumentSans-Regular.ttf", 16)
    draw.text((MARGIN, 50), label_top, fill=GOLD, font=f_meta)
    # Page number bottom right
    page_str = f"{slide_num}/8"
    f_page = font("IBMPlexMono-Regular.ttf", 18)
    bbox = draw.textbbox((0, 0), page_str, font=f_page)
    pw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - pw, H - 60), page_str, fill=GRAY, font=f_page)
    # Bottom-left small mark
    f_mark = font("IBMPlexMono-Regular.ttf", 14)
    draw.text((MARGIN, H - 58), "DUX MACHINA / OPERATOR'S MANUAL", fill=GRAY, font=f_mark)

def wrap_text(draw, text, font_obj, max_width):
    words = text.split()
    lines = []
    current = []
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

def text_height(draw, text, font_obj):
    bbox = draw.textbbox((0, 0), text, font=font_obj)
    return bbox[3] - bbox[1]

# ============= SLIDE 1: COVER =============
def slide_1():
    img, draw = make_canvas()
    draw_meta(draw, 1)
    # Eyebrow
    f_eye = font("IBMPlexMono-Regular.ttf", 18)
    draw.text((MARGIN, 200), "I.   ON LEVERAGE", fill=GOLD, font=f_eye)

    # Headline (multi-line, serif)
    f_h = font("InstrumentSerif-Regular.ttf", 78)
    headline_lines = [
        "We cut a 4-hour edit",
        "and a $3K agency",
        "dependency to",
        "30 minutes."
    ]
    y = 320
    for line in headline_lines:
        if "$3K" in line:
            # Render with $3K in gold
            parts = line.split("$3K")
            x = MARGIN
            draw.text((x, y), parts[0], fill=INK, font=f_h)
            x += draw.textbbox((0, 0), parts[0], font=f_h)[2]
            draw.text((x, y), "$3K", fill=GOLD, font=f_h)
            x += draw.textbbox((0, 0), "$3K", font=f_h)[2]
            draw.text((x, y), parts[1], fill=INK, font=f_h)
        elif "30 minutes" in line:
            parts = line.split("30 minutes")
            x = MARGIN
            draw.text((x, y), parts[0], fill=INK, font=f_h)
            x += draw.textbbox((0, 0), parts[0], font=f_h)[2]
            draw.text((x, y), "30 minutes", fill=GOLD, font=f_h)
            x += draw.textbbox((0, 0), "30 minutes", font=f_h)[2]
            draw.text((x, y), parts[1], fill=INK, font=f_h)
        else:
            draw.text((MARGIN, y), line, fill=INK, font=f_h)
        y += 96

    # Italic subhead
    f_sub = font("InstrumentSerif-Italic.ttf" if (FONTS / "InstrumentSerif-Italic.ttf").exists() else "LibreBaskerville-Regular.ttf", 32)
    draw.text((MARGIN, 770), "Here is the system.", fill=INK_SOFT, font=f_sub)

    # Author/label far below
    f_label = font("InstrumentSans-Regular.ttf", 18)
    draw.text((MARGIN, 1180), "FIELD NOTE NO. 09", fill=GOLD, font=f_label)
    draw.text((MARGIN, 1210), "Cross-industry systems consultancy", fill=INK_SOFT, font=f_label)

    img.save(TMP_DIR / "slide_01.png")
    print("Slide 1 done")

# ============= SLIDE 2: THE OLD WAY =============
def slide_2():
    img, draw = make_canvas()
    draw_meta(draw, 2)
    f_eye = font("IBMPlexMono-Regular.ttf", 18)
    draw.text((MARGIN, 200), "II.  THE DEFAULT STACK", fill=GOLD, font=f_eye)
    # Title
    f_t = font("InstrumentSerif-Regular.ttf", 64)
    draw.text((MARGIN, 270), "Old way to ship", fill=INK, font=f_t)
    draw.text((MARGIN, 340), "one video.", fill=INK, font=f_t)

    # List items
    f_label = font("IBMPlexMono-Regular.ttf", 18)
    f_body = font("InstrumentSans-Regular.ttf", 30)
    items = [
        ("01", "1 hour record"),
        ("02", "2 hours transcribe"),
        ("03", "4 hours edit and revisions"),
        ("04", "2 to 3 weeks agency turnaround"),
        ("05", "Or $3,000 outsourced"),
    ]
    y = 510
    for label, text in items:
        draw.text((MARGIN, y + 8), label, fill=GOLD, font=f_label)
        if "$3,000" in text:
            parts = text.split("$3,000")
            x = MARGIN + 70
            draw.text((x, y), parts[0], fill=INK, font=f_body)
            x += draw.textbbox((0, 0), parts[0], font=f_body)[2]
            draw.text((x, y), "$3,000", fill=GOLD, font=f_body)
            x += draw.textbbox((0, 0), "$3,000", font=f_body)[2]
            draw.text((x, y), parts[1], fill=INK, font=f_body)
        else:
            draw.text((MARGIN + 70, y), text, fill=INK, font=f_body)
        y += 60
    # Divider
    draw.line([(MARGIN, y + 30), (W - MARGIN, y + 30)], fill=INK, width=1)
    y += 70
    # Total
    f_total_label = font("IBMPlexMono-Regular.ttf", 16)
    draw.text((MARGIN, y), "TOTAL", fill=GOLD, font=f_total_label)
    f_total = font("InstrumentSerif-Regular.ttf", 48)
    draw.text((MARGIN, y + 30), "8+ hours, or $3K per asset.", fill=INK, font=f_total)

    img.save(TMP_DIR / "slide_02.png")
    print("Slide 2 done")

# ============= SLIDE 3: WHY IT FAILS =============
def slide_3():
    img, draw = make_canvas()
    draw_meta(draw, 3)
    f_eye = font("IBMPlexMono-Regular.ttf", 18)
    draw.text((MARGIN, 200), "III. THE STRUCTURAL FAULT", fill=GOLD, font=f_eye)
    f_t = font("InstrumentSerif-Regular.ttf", 60)
    draw.text((MARGIN, 270), "Why the default", fill=INK, font=f_t)
    draw.text((MARGIN, 335), "stack actually fails.", fill=INK, font=f_t)

    # 3 numbered observations
    f_num = font("InstrumentSerif-Regular.ttf", 38)
    f_body = font("InstrumentSans-Regular.ttf", 26)
    observations = [
        ("i.", "Every revision restarts the cycle."),
        ("ii.", "Your voice flattens through the editor's filter."),
        ("iii.", "By the time the asset ships, the moment is gone."),
    ]
    y = 510
    for num, obs in observations:
        draw.text((MARGIN, y), num, fill=GOLD, font=f_num)
        wrapped = wrap_text(draw, obs, f_body, W - 2 * MARGIN - 90)
        oy = y + 8
        for line in wrapped:
            draw.text((MARGIN + 70, oy), line, fill=INK, font=f_body)
            oy += 38
        y += max(80, oy - y + 30)

    # Bottom emphasis (italic serif)
    f_em = font("InstrumentSerif-Italic.ttf" if (FONTS / "InstrumentSerif-Italic.ttf").exists() else "CrimsonPro-Italic.ttf", 36)
    em_lines = [
        "This is not a content problem.",
        "It is a coordination problem.",
    ]
    by = 1100
    for line in em_lines:
        draw.text((MARGIN, by), line, fill=INK, font=f_em)
        by += 50

    img.save(TMP_DIR / "slide_03.png")
    print("Slide 3 done")

# ============= SLIDE 4: WHAT WE BUILT =============
def slide_4():
    img, draw = make_canvas()
    draw_meta(draw, 4)
    f_eye = font("IBMPlexMono-Regular.ttf", 18)
    draw.text((MARGIN, 200), "IV.  THE PIPELINE", fill=GOLD, font=f_eye)
    f_t = font("InstrumentSerif-Regular.ttf", 64)
    draw.text((MARGIN, 270), "What we built.", fill=INK, font=f_t)

    # Pipeline as a vertical sequence of steps with thin gold connectors
    steps = [
        "Recording",
        "Automated transcription",
        "Filler detection",
        "Audio cleanup",
        "Avatar layer",
        "Compositor",
        "Published episode",
    ]
    f_step_num = font("IBMPlexMono-Regular.ttf", 18)
    f_step = font("InstrumentSerif-Regular.ttf", 32)
    y = 470
    for i, step in enumerate(steps):
        # Number column
        draw.text((MARGIN, y + 6), f"0{i+1}", fill=GOLD, font=f_step_num)
        # Step name
        draw.text((MARGIN + 70, y), step, fill=INK, font=f_step)
        # Connector line on left margin
        if i < len(steps) - 1:
            draw.line([(MARGIN + 14, y + 40), (MARGIN + 14, y + 78)], fill=GOLD, width=1)
        y += 78

    # Bottom emphasis
    f_em = font("InstrumentSerif-Italic.ttf" if (FONTS / "InstrumentSerif-Italic.ttf").exists() else "CrimsonPro-Italic.ttf", 32)
    draw.text((MARGIN, 1180), "One pipeline.", fill=INK, font=f_em)
    draw.text((MARGIN, 1220), "No human in the middle.", fill=INK_SOFT, font=f_em)

    img.save(TMP_DIR / "slide_04.png")
    print("Slide 4 done")

# ============= SLIDE 5: THE MATH =============
def slide_5():
    img, draw = make_canvas()
    draw_meta(draw, 5)
    f_eye = font("IBMPlexMono-Regular.ttf", 18)
    draw.text((MARGIN, 200), "V.   THE LEDGER", fill=GOLD, font=f_eye)
    f_t = font("InstrumentSerif-Regular.ttf", 64)
    draw.text((MARGIN, 270), "The math from", fill=INK, font=f_t)
    draw.text((MARGIN, 335), "one episode.", fill=INK, font=f_t)

    # Stat block
    stats = [
        ("Raw recording", "18:25"),
        ("Auto-detected cuts", "358"),
        ("Dead air + filler removed", "5:14"),
        ("Reduction from source", "26%"),
        ("Final episode", "13:11"),
        ("Hands-on time", "30 min"),
    ]
    f_label = font("InstrumentSans-Regular.ttf", 22)
    f_value = font("IBMPlexMono-Regular.ttf", 44)
    y = 500
    for label, value in stats:
        draw.text((MARGIN, y + 14), label, fill=INK_SOFT, font=f_label)
        # right-align value
        bbox = draw.textbbox((0, 0), value, font=f_value)
        vw = bbox[2] - bbox[0]
        draw.text((W - MARGIN - vw, y), value, fill=GOLD, font=f_value)
        # divider
        draw.line([(MARGIN, y + 70), (W - MARGIN, y + 70)], fill=GRID, width=1)
        y += 95

    img.save(TMP_DIR / "slide_05.png")
    print("Slide 5 done")

# ============= SLIDE 6: CROSS-INDUSTRY =============
def slide_6():
    img, draw = make_canvas()
    draw_meta(draw, 6)
    f_eye = font("IBMPlexMono-Regular.ttf", 18)
    draw.text((MARGIN, 200), "VI.  THE ARCHITECTURE TRAVELS", fill=GOLD, font=f_eye)
    f_t = font("InstrumentSerif-Regular.ttf", 56)
    draw.text((MARGIN, 270), "The same architecture", fill=INK, font=f_t)
    draw.text((MARGIN, 332), "works for:", fill=INK, font=f_t)

    items = [
        "Sales demo videos",
        "Investor updates for portfolio companies",
        "Internal training assets",
        "Customer success walk-throughs",
        "Onboarding for new hires",
    ]
    f_n = font("IBMPlexMono-Regular.ttf", 18)
    f_b = font("InstrumentSerif-Regular.ttf", 34)
    y = 510
    for i, item in enumerate(items):
        draw.text((MARGIN, y + 8), f"0{i+1}", fill=GOLD, font=f_n)
        wrapped = wrap_text(draw, item, f_b, W - 2 * MARGIN - 90)
        oy = y
        for line in wrapped:
            draw.text((MARGIN + 70, oy), line, fill=INK, font=f_b)
            oy += 44
        y += max(75, oy - y + 30)

    img.save(TMP_DIR / "slide_06.png")
    print("Slide 6 done")

# ============= SLIDE 7: THE BIGGER IDEA =============
def slide_7():
    img, draw = make_canvas()
    draw_meta(draw, 7)
    f_eye = font("IBMPlexMono-Regular.ttf", 18)
    draw.text((MARGIN, 200), "VII. THE PRINCIPLE", fill=GOLD, font=f_eye)

    # Centered serif statement
    f_h1 = font("InstrumentSerif-Regular.ttf", 64)
    line1 = "You do not need to hire"
    line2 = "to scale content."
    f_h2 = font("InstrumentSerif-Italic.ttf" if (FONTS / "InstrumentSerif-Italic.ttf").exists() else "CrimsonPro-Italic.ttf", 50)
    line3 = "You need the system"
    line4 = "the hires cannot replace."

    def cx_text(text, fnt, y, color):
        bbox = draw.textbbox((0, 0), text, font=fnt)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) / 2, y), text, fill=color, font=fnt)

    cx_text(line1, f_h1, 540, INK)
    cx_text(line2, f_h1, 620, INK)
    # Decorative gold mark between halves
    draw.line([(W//2 - 50, 740), (W//2 + 50, 740)], fill=GOLD, width=2)
    cx_text(line3, f_h2, 800, INK_SOFT)
    cx_text(line4, f_h2, 870, INK_SOFT)

    img.save(TMP_DIR / "slide_07.png")
    print("Slide 7 done")

# ============= SLIDE 8: CLOSE =============
def slide_8():
    img, draw = make_canvas()
    draw_meta(draw, 8)
    f_eye = font("IBMPlexMono-Regular.ttf", 18)
    draw.text((MARGIN, 200), "VIII. THE INVITATION", fill=GOLD, font=f_eye)
    f_t = font("InstrumentSerif-Regular.ttf", 56)
    draw.text((MARGIN, 270), "If you are paying", fill=INK, font=f_t)
    line = "$3K to $15K per video."
    # Render with gold
    parts = line.split("$3K to $15K")
    x, y = MARGIN, 332
    f_t2 = font("InstrumentSerif-Regular.ttf", 56)
    if len(parts) == 2:
        draw.text((x, y), parts[0], fill=INK, font=f_t2)
        x += draw.textbbox((0, 0), parts[0], font=f_t2)[2]
        draw.text((x, y), "$3K to $15K", fill=GOLD, font=f_t2)
        x += draw.textbbox((0, 0), "$3K to $15K", font=f_t2)[2]
        draw.text((x, y), parts[1], fill=INK, font=f_t2)
    else:
        draw.text((MARGIN, y), line, fill=INK, font=f_t2)

    # Body
    f_body = font("InstrumentSans-Regular.ttf", 28)
    body_lines = [
        "And waiting two weeks per turnaround,",
        "the math is begging for a redesign.",
    ]
    y = 480
    for line in body_lines:
        draw.text((MARGIN, y), line, fill=INK_SOFT, font=f_body)
        y += 42

    # CTA in gold, centered, framed by hairlines
    draw.line([(MARGIN, 880), (W - MARGIN, 880)], fill=GOLD, width=1)
    draw.line([(MARGIN, 1100), (W - MARGIN, 1100)], fill=GOLD, width=1)

    f_cta_eye = font("IBMPlexMono-Regular.ttf", 16)
    draw.text((MARGIN, 920), "DIRECT CORRESPONDENCE", fill=GOLD, font=f_cta_eye)
    f_cta = font("InstrumentSerif-Italic.ttf" if (FONTS / "InstrumentSerif-Italic.ttf").exists() else "CrimsonPro-Italic.ttf", 32)
    cta_lines = [
        "Send a message if you want to see",
        "how this would apply to your team's",
        "content workflow.",
    ]
    y = 960
    for line in cta_lines:
        draw.text((MARGIN, y), line, fill=INK, font=f_cta)
        y += 44

    img.save(TMP_DIR / "slide_08.png")
    print("Slide 8 done")

# ============= BUILD ALL + COMBINE =============
slide_1()
slide_2()
slide_3()
slide_4()
slide_5()
slide_6()
slide_7()
slide_8()

# Combine into single PDF
slides = sorted(TMP_DIR.glob("slide_*.png"))
pdf_path = OUT_DIR / "week9_monday_carousel.pdf"
with open(pdf_path, "wb") as f:
    f.write(img2pdf.convert([str(s) for s in slides]))

print(f"\nPDF: {pdf_path}")
print(f"Size: {pdf_path.stat().st_size / 1024:.1f} KB")
print(f"Slides: {len(slides)}")
