"""Week 12 carousel — Founder's Bulletin newspaper-propaganda aesthetic.
10 slides at 1080x1350 portrait. Decision Velocity Audit edition.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import img2pdf
import random

OUT_DIR = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\social_media")
TMP_DIR = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\week12_slides")
TMP_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1350
MARGIN = 90

# Founder's Bulletin palette — aged newsprint + propaganda crimson
PAPER       = (242, 232, 208)   # #F2E8D0 warm cream
PAPER_DK    = (228, 216, 188)   # #E4D8BC slight shadow for layered paper
INK         = (26, 20, 16)      # #1A1410 warm black ink
INK_SOFT    = (74, 60, 48)      # #4A3C30 muted ink for secondary
CRIMSON     = (164, 35, 28)     # #A4231C propaganda red
CRIMSON_DK  = (122, 24, 20)     # darker crimson for shadow
SEPIA       = (110, 92, 66)     # #6E5C42 aged accent
NEWSPRINT   = (200, 188, 162)   # subtle texture color

FONTS = Path(r"C:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS\.claude\skills\canvas-design\canvas-fonts")

def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)

# Font aliases
def big_shoulders(size, bold=True):
    return font("BigShoulders-Bold.ttf" if bold else "BigShoulders-Regular.ttf", size)
def plex_serif(size, bold=False):
    return font("IBMPlexSerif-Bold.ttf" if bold else "IBMPlexSerif-Regular.ttf", size)
def work(size, bold=False):
    return font("WorkSans-Bold.ttf" if bold else "WorkSans-Regular.ttf", size)
def mono(size, bold=False):
    return font("JetBrainsMono-Bold.ttf" if bold else "JetBrainsMono-Regular.ttf", size)
def crimson_italic(size):
    return font("CrimsonPro-Italic.ttf", size)
def gloock(size):
    return font("Gloock-Regular.ttf", size)  # display serif for huge numbers
def stencil_display(size):
    # Erica One is bold, propaganda-feeling display sans
    return font("EricaOne-Regular.ttf", size)


def make_paper_canvas():
    """Aged paper background with subtle noise texture."""
    img = Image.new("RGB", (W, H), PAPER)
    # Noise speckle for newsprint feel
    px = img.load()
    random.seed(42)
    for _ in range(W * H // 50):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        # Random darker speckles
        darken = random.randint(0, 25)
        r, g, b = px[x, y]
        px[x, y] = (max(0, r - darken), max(0, g - darken), max(0, b - darken))
    # Subtle vignette via edge shadow
    draw = ImageDraw.Draw(img, "RGBA")
    for i in range(20):
        alpha = int(8 - i * 0.3)
        if alpha > 0:
            draw.rectangle([i, i, W - i, H - i], outline=(80, 60, 40, alpha), width=1)
    return img

def draw_double_rule(draw, y, x_start=MARGIN, x_end=W - MARGIN, color=INK, gap=8, weight=3):
    draw.line([(x_start, y), (x_end, y)], fill=color, width=weight)
    draw.line([(x_start, y + gap), (x_end, y + gap)], fill=color, width=1)

def draw_triple_rule(draw, y, x_start=MARGIN, x_end=W - MARGIN, color=INK):
    draw.line([(x_start, y), (x_end, y)], fill=color, width=2)
    draw.line([(x_start, y + 5), (x_end, y + 5)], fill=color, width=1)
    draw.line([(x_start, y + 10), (x_end, y + 10)], fill=color, width=2)

def text_center(draw, y, text, font_obj, color=INK):
    bbox = draw.textbbox((0, 0), text, font=font_obj)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, fill=color, font=font_obj)

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

def draw_wrapped(draw, x, y, text, font_obj, max_width, line_height, color=INK, center=False):
    lines = wrap_text(draw, text, font_obj, max_width)
    for i, line in enumerate(lines):
        if center:
            bbox = draw.textbbox((0, 0), line, font=font_obj)
            lw = bbox[2] - bbox[0]
            draw.text((x + (max_width - lw) // 2, y + i * line_height), line, fill=color, font=font_obj)
        else:
            draw.text((x, y + i * line_height), line, fill=color, font=font_obj)
    return y + len(lines) * line_height

def draw_masthead(draw, vol_text, date_text):
    """Top masthead: BULLETIN nameplate + vol/date row."""
    # Top thick rule
    draw.rectangle([(MARGIN, 50), (W - MARGIN, 56)], fill=INK)
    # Bulletin title — BIG SHOULDERS condensed bold
    f_mast = big_shoulders(58)
    text_center(draw, 70, "THE FOUNDER'S BULLETIN", f_mast, color=INK)
    # Subhead italics
    f_sub = crimson_italic(20)
    text_center(draw, 138, "an operator's dispatch — published by Dux Machina", f_sub, color=INK_SOFT)
    # Vol/date row
    f_meta = mono(15, bold=True)
    draw.text((MARGIN, 175), vol_text, fill=INK, font=f_meta)
    bbox = draw.textbbox((0, 0), date_text, font=f_meta)
    tw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - tw, 175), date_text, fill=INK, font=f_meta)
    # Double rule under masthead
    draw_double_rule(draw, 200)

def draw_footer(draw, page_num, total=10):
    # Bottom double rule
    draw_double_rule(draw, H - 80)
    f_foot = mono(13)
    draw.text((MARGIN, H - 55), "DUX MACHINA · OPERATOR'S DESK", fill=INK_SOFT, font=f_foot)
    page_str = f"PG. {page_num} / {total}"
    bbox = draw.textbbox((0, 0), page_str, font=f_foot)
    pw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - pw, H - 55), page_str, fill=INK_SOFT, font=f_foot)

def draw_stamp(draw, x, y, text, font_obj, fill=CRIMSON, padding=14):
    """Boxed propaganda-style stamp."""
    bbox = draw.textbbox((0, 0), text, font=font_obj)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    box = [x, y, x + tw + padding * 2, y + th + padding * 2]
    draw.rectangle(box, fill=fill)
    draw.text((x + padding, y + padding - 4), text, fill=PAPER, font=font_obj)
    return box

def draw_halftone_band(img, y, h, density=0.18):
    """Halftone-like speckle band — propaganda newsprint accent."""
    draw = ImageDraw.Draw(img)
    random.seed(y)
    for _ in range(int(W * h * density)):
        x = random.randint(MARGIN, W - MARGIN)
        py = random.randint(y, y + h - 1)
        r = random.choice([1, 1, 2, 2, 3])
        draw.ellipse([x, py, x + r, py + r], fill=INK)

def draw_pointing_finger(draw, x, y, size=60, color=CRIMSON):
    """Stylized propaganda pointing-hand glyph using shapes."""
    # Hand bar (palm)
    draw.rectangle([x, y + size * 0.35, x + size * 0.55, y + size * 0.75], fill=color)
    # Index finger pointing right
    draw.polygon([
        (x + size * 0.55, y + size * 0.42),
        (x + size, y + size * 0.5),
        (x + size * 0.55, y + size * 0.58),
    ], fill=color)
    # Cuff stripes
    draw.rectangle([x, y + size * 0.78, x + size * 0.55, y + size * 0.82], fill=color)
    draw.rectangle([x, y + size * 0.85, x + size * 0.55, y + size * 0.89], fill=color)

# ────────────────────────────────────────────────────────────────────
# SLIDE 1 — FRONT PAGE / MASTHEAD COVER
# ────────────────────────────────────────────────────────────────────
def slide_1():
    img = make_paper_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "VOL. XII   ·   NO. 01", "MONDAY · JUNE 1, 2026")

    # Edition stamp
    f_stamp = work(18, bold=True)
    draw_stamp(draw, MARGIN, 240, "SPECIAL EDITION", f_stamp)

    # Edition title — small caps
    f_kicker = work(22, bold=True)
    draw.text((MARGIN, 320), "THE DECISION VELOCITY EDITION", fill=INK, font=f_kicker)

    # Mega serif feature headline
    f_headline = plex_serif(82, bold=True)
    y = 370
    lines = [
        "The bottleneck",
        "on your desk",
        "is costing",
        "$340,000",
        "a week.",
    ]
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=f_headline)
        lw = bbox[2] - bbox[0]
        # Highlight the dollar amount in crimson
        color = CRIMSON if "$340" in line else INK
        draw.text((MARGIN, y), line, fill=color, font=f_headline)
        y += 92

    # Standfirst / deck
    f_deck = crimson_italic(26)
    deck = "Across the founders we audit, the same pattern surfaces every Monday. Inside: the audit that clears the queue."
    draw_wrapped(draw, MARGIN, y + 30, deck, f_deck, W - MARGIN * 2, 36, color=INK_SOFT)

    # Halftone band above footer
    draw_halftone_band(img, H - 180, 60, density=0.25)

    # "READ INSIDE" callout, bottom-right
    f_inside = work(18, bold=True)
    draw_stamp(draw, W - MARGIN - 200, H - 165, "READ INSIDE  ▶", f_inside)

    draw_footer(draw, 1)
    return img

# ────────────────────────────────────────────────────────────────────
# SLIDE 2 — DISPATCH NO. 1 / Opening stat
# ────────────────────────────────────────────────────────────────────
def slide_2():
    img = make_paper_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "VOL. XII   ·   NO. 01", "DISPATCH NO. 1")

    # Section label
    f_section = mono(16, bold=True)
    draw.text((MARGIN, 240), "── THE PATTERN ──", fill=CRIMSON, font=f_section)

    # Headline
    f_hl = plex_serif(64, bold=True)
    y = 280
    for line in ["15 to 25 decisions", "on your desk."]:
        draw.text((MARGIN, y), line, fill=INK, font=f_hl)
        y += 76

    # Body
    f_body = work(24)
    body = ("Across the founders we audit, the same pattern surfaces every "
            "Monday morning. The desk is loaded. The week has not started.")
    y = draw_wrapped(draw, MARGIN, y + 30, body, f_body, W - MARGIN * 2, 36, color=INK)

    # Big stat panel: wait time — sized to fill the lower half of the slide with breathing room
    panel_y = y + 90
    panel_h = 540
    draw.rectangle([(MARGIN, panel_y), (W - MARGIN, panel_y + panel_h)], outline=INK, width=3)
    # Crimson tag — sits INSIDE the panel, top-left corner (clean interior label)
    f_tag = mono(14, bold=True)
    tag_inset = 14
    tag_h = 38
    tag_w = 250
    draw.rectangle(
        [(MARGIN + tag_inset, panel_y + tag_inset),
         (MARGIN + tag_inset + tag_w, panel_y + tag_inset + tag_h)],
        fill=CRIMSON,
    )
    draw.text(
        (MARGIN + tag_inset + 16, panel_y + tag_inset + 10),
        "AVERAGE WAIT TIME",
        fill=PAPER,
        font=f_tag,
    )
    # Hairline separator under the tag area
    draw.line(
        [(MARGIN + 14, panel_y + tag_inset + tag_h + 24),
         (W - MARGIN - 14, panel_y + tag_inset + tag_h + 24)],
        fill=SEPIA,
        width=1,
    )
    # Giant number — visually centered in the panel body
    f_num = gloock(260)
    text_center(draw, panel_y + 140, "7-10", f_num, color=INK)
    # Hairline separator above the label
    draw.line(
        [(MARGIN + 14, panel_y + panel_h - 95),
         (W - MARGIN - 14, panel_y + panel_h - 95)],
        fill=SEPIA,
        width=1,
    )
    # Label at the bottom — generous bottom margin
    f_unit = work(24, bold=True)
    text_center(draw, panel_y + panel_h - 70, "DAYS PER DECISION", f_unit, color=INK_SOFT)

    draw_footer(draw, 2)
    return img

# ────────────────────────────────────────────────────────────────────
# SLIDE 3 — THE MATH NOBODY RUNS / 140 person-days
# ────────────────────────────────────────────────────────────────────
def slide_3():
    img = make_paper_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "VOL. XII   ·   NO. 01", "DISPATCH NO. 2")

    f_section = mono(16, bold=True)
    draw.text((MARGIN, 240), "── BY THE NUMBERS ──", fill=CRIMSON, font=f_section)

    f_hl = plex_serif(60, bold=True)
    draw.text((MARGIN, 280), "The math nobody runs.", fill=INK, font=f_hl)

    # Equation row
    eq_y = 400
    f_eq = mono(36, bold=True)
    text_center(draw, eq_y, "20  ×  7 DAYS  =", f_eq, color=INK)

    # MASSIVE 140 number
    f_giant = gloock(280)
    text_center(draw, eq_y + 70, "140", f_giant, color=CRIMSON)

    f_under = work(26, bold=True)
    text_center(draw, eq_y + 380, "PERSON-DAYS OF AUTHORIZATION", f_under, color=INK)
    text_center(draw, eq_y + 416, "WAITING FOR A YES OR A NO.", f_under, color=INK)

    # Halftone band
    draw_halftone_band(img, H - 230, 60, density=0.22)

    # Caption
    f_cap = crimson_italic(20)
    text_center(draw, H - 145, "Before anyone in the building can act.", f_cap, color=INK_SOFT)

    draw_footer(draw, 3)
    return img

# ────────────────────────────────────────────────────────────────────
# SLIDE 4 — CONSEQUENCE / Pull quote
# ────────────────────────────────────────────────────────────────────
def slide_4():
    img = make_paper_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "VOL. XII   ·   NO. 01", "DISPATCH NO. 3")

    f_section = mono(16, bold=True)
    draw.text((MARGIN, 240), "── THE CONSEQUENCE ──", fill=CRIMSON, font=f_section)

    # Pull quote — big italic serif
    f_quote_open = gloock(220)
    draw.text((MARGIN - 10, 270), "“", fill=CRIMSON, font=f_quote_open)

    f_pull = plex_serif(54, bold=False)
    y = 420
    pull_lines = [
        "When",
        "authorization",
        "stops,",
        "work stops.",
    ]
    for line in pull_lines:
        # Last line bold
        f_use = plex_serif(54, bold=True) if line == "work stops." else f_pull
        color = CRIMSON if line == "work stops." else INK
        draw.text((MARGIN + 30, y), line, fill=color, font=f_use)
        y += 70

    # Body
    f_body = work(22)
    body = ("The team learns this within a quarter. They stop asking. They route "
            "around the founder. The decisions that get made anyway are usually the "
            "wrong ones, because the people closest to the problem did not have "
            "authority to fix it.")
    draw_wrapped(draw, MARGIN, y + 60, body, f_body, W - MARGIN * 2, 34, color=INK)

    draw_footer(draw, 4)
    return img

# ────────────────────────────────────────────────────────────────────
# SLIDE 5 — THREE BUCKETS / Field guide
# ────────────────────────────────────────────────────────────────────
def slide_5():
    img = make_paper_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "VOL. XII   ·   NO. 01", "FIELD GUIDE")

    # Section banner
    draw.rectangle([(MARGIN, 230), (W - MARGIN, 290)], fill=INK)
    f_banner = big_shoulders(46)
    text_center(draw, 238, "THE AUDIT · THREE BUCKETS", f_banner, color=PAPER)

    # Three labeled columns / rows
    f_num = gloock(110)
    f_label = big_shoulders(54)
    f_desc = work(22)

    row_y = 340
    for i, (num, label, desc) in enumerate([
        ("I", "REVERSIBLE", "Recoverable inside 30 days. Delegate completely."),
        ("II", "IRREVERSIBLE", "Structural cost. Founder owns with a 48-hour clock."),
        ("III", "INFORMATIONAL", "Not a decision. Hand it back: 'you decide.'"),
    ]):
        # Numeral
        draw.text((MARGIN, row_y - 10), num, fill=CRIMSON, font=f_num)
        # Label
        draw.text((MARGIN + 170, row_y + 10), label, fill=INK, font=f_label)
        # Description
        draw_wrapped(draw, MARGIN + 170, row_y + 75, desc, f_desc,
                     W - MARGIN * 2 - 170, 32, color=INK_SOFT)
        # Divider
        if i < 2:
            draw.line([(MARGIN, row_y + 175), (W - MARGIN, row_y + 175)], fill=SEPIA, width=1)
        row_y += 200

    draw_footer(draw, 5)
    return img

# ────────────────────────────────────────────────────────────────────
# SLIDE 6 — REVERSIBLE detail
# ────────────────────────────────────────────────────────────────────
def slide_6():
    img = make_paper_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "VOL. XII   ·   NO. 01", "BUCKET I")

    # Roman numeral huge
    f_roman = gloock(280)
    draw.text((MARGIN, 230), "I", fill=CRIMSON, font=f_roman)

    # Label
    f_label = big_shoulders(96)
    draw.text((MARGIN + 200, 280), "REVERSIBLE", fill=INK, font=f_label)

    # Definition
    f_def = plex_serif(28, bold=False)
    y = draw_wrapped(draw, MARGIN, 560,
                     "Cost of being wrong is recoverable inside 30 days.",
                     f_def, W - MARGIN * 2, 42, color=INK_SOFT)

    # Default action stamp
    f_stamp = work(22, bold=True)
    draw_stamp(draw, MARGIN, y + 50, "DEFAULT  ▶  DELEGATE COMPLETELY", f_stamp)

    # Note
    f_note = crimson_italic(22)
    note = "The founder should not be the bottleneck on any reversible decision."
    draw_wrapped(draw, MARGIN, y + 160, note, f_note, W - MARGIN * 2, 32, color=INK)

    # Halftone band
    draw_halftone_band(img, H - 220, 50, density=0.18)

    draw_footer(draw, 6)
    return img

# ────────────────────────────────────────────────────────────────────
# SLIDE 7 — IRREVERSIBLE detail
# ────────────────────────────────────────────────────────────────────
def slide_7():
    img = make_paper_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "VOL. XII   ·   NO. 01", "BUCKET II")

    f_roman = gloock(280)
    draw.text((MARGIN, 230), "II", fill=CRIMSON, font=f_roman)

    f_label = big_shoulders(86)
    draw.text((MARGIN + 280, 290), "IRREVERSIBLE", fill=INK, font=f_label)

    f_def = plex_serif(28, bold=False)
    y = draw_wrapped(draw, MARGIN, 560,
                     "Cost of being wrong is structural or expensive to undo.",
                     f_def, W - MARGIN * 2, 42, color=INK_SOFT)

    f_stamp = work(22, bold=True)
    draw_stamp(draw, MARGIN, y + 50, "DEFAULT  ▶  FOUNDER OWNS · 48-HOUR CLOCK", f_stamp)

    f_note = crimson_italic(22)
    note = "Past 48 hours, the founder has already cost the company more than the decision itself is worth."
    draw_wrapped(draw, MARGIN, y + 160, note, f_note, W - MARGIN * 2, 32, color=INK)

    draw_halftone_band(img, H - 220, 50, density=0.18)
    draw_footer(draw, 7)
    return img

# ────────────────────────────────────────────────────────────────────
# SLIDE 8 — INFORMATIONAL detail
# ────────────────────────────────────────────────────────────────────
def slide_8():
    img = make_paper_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "VOL. XII   ·   NO. 01", "BUCKET III")

    f_roman = gloock(280)
    draw.text((MARGIN, 230), "III", fill=CRIMSON, font=f_roman)

    f_label = big_shoulders(72)
    draw.text((MARGIN + 360, 305), "INFORMATIONAL", fill=INK, font=f_label)

    f_def = plex_serif(28, bold=False)
    y = draw_wrapped(draw, MARGIN, 560,
                     "Not actually a decision. Someone wants a thumbs-up because they are nervous.",
                     f_def, W - MARGIN * 2, 42, color=INK_SOFT)

    f_stamp = work(22, bold=True)
    draw_stamp(draw, MARGIN, y + 80, "DEFAULT  ▶  HAND IT BACK · 'YOU DECIDE'", f_stamp)

    f_note = crimson_italic(22)
    note = "Reassurance is not a decision. Train the team to bring you fewer of these."
    draw_wrapped(draw, MARGIN, y + 190, note, f_note, W - MARGIN * 2, 32, color=INK)

    draw_halftone_band(img, H - 220, 50, density=0.18)
    draw_footer(draw, 8)
    return img

# ────────────────────────────────────────────────────────────────────
# SLIDE 9 — THE 70% FINDING / Full stat poster
# ────────────────────────────────────────────────────────────────────
def slide_9():
    img = make_paper_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "VOL. XII   ·   NO. 01", "THE FINDING")

    f_section = mono(16, bold=True)
    text_center(draw, 240, "── AFTER THE AUDIT ──", f_section, color=CRIMSON)

    # MASSIVE 70%
    f_giant = gloock(420)
    text_center(draw, 290, "70%", f_giant, color=CRIMSON)

    # Subheading
    f_sub = big_shoulders(58)
    text_center(draw, 770, "OF YOUR QUEUE", f_sub, color=INK)
    text_center(draw, 830, "NEVER NEEDED YOU.", f_sub, color=INK)

    # Body
    f_body = work(22)
    body = ("Reversible. Or informational. You were the bottleneck on work "
            "that never required your input in the first place.")
    draw_wrapped(draw, MARGIN, 920, body, f_body, W - MARGIN * 2, 32, color=INK_SOFT, center=True)

    # Triple rule
    draw_triple_rule(draw, 1060)

    # Closing italic
    f_close = crimson_italic(22)
    text_center(draw, 1090, "The fastest companies clear the desk every 48 hours.", f_close, color=INK)

    draw_footer(draw, 9)
    return img

# ────────────────────────────────────────────────────────────────────
# SLIDE 10 — EDITORIAL / QUESTION CLOSE
# ────────────────────────────────────────────────────────────────────
def slide_10():
    img = make_paper_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "VOL. XII   ·   NO. 01", "EDITORIAL")

    # Pointing finger
    draw_pointing_finger(draw, MARGIN, 240, size=72, color=CRIMSON)

    # Section
    f_section = big_shoulders(38)
    draw.text((MARGIN + 110, 260), "A QUESTION FOR THE DESK.", fill=INK, font=f_section)

    # The question — large serif italic
    f_q = plex_serif(42, bold=True)
    question = (
        "How many decisions are sitting on your desk right now that your team "
        "would have resolved on Tuesday if you had moved on Monday?"
    )
    draw_wrapped(draw, MARGIN, 380, question, f_q, W - MARGIN * 2, 56, color=INK)

    # Halftone band
    draw_halftone_band(img, 900, 70, density=0.22)

    # Sign-off
    f_signoff = crimson_italic(26)
    text_center(draw, 1020, "Count them before the week starts.", f_signoff, color=INK_SOFT)

    # Triple rule
    draw_triple_rule(draw, 1100)

    # Publisher line
    f_pub = work(18, bold=True)
    text_center(draw, 1140, "PUBLISHED BY DUX MACHINA — STRATEGY THAT BUILDS.", f_pub, color=INK)
    f_url = mono(14)
    text_center(draw, 1175, "duxmachina.com", f_url, color=INK_SOFT)

    draw_footer(draw, 10)
    return img

# ────────────────────────────────────────────────────────────────────
# BUILD
# ────────────────────────────────────────────────────────────────────
def main():
    slides = [
        ("slide_01_cover", slide_1()),
        ("slide_02_pattern", slide_2()),
        ("slide_03_math", slide_3()),
        ("slide_04_consequence", slide_4()),
        ("slide_05_threebuckets", slide_5()),
        ("slide_06_reversible", slide_6()),
        ("slide_07_irreversible", slide_7()),
        ("slide_08_informational", slide_8()),
        ("slide_09_seventy", slide_9()),
        ("slide_10_question", slide_10()),
    ]

    paths = []
    for name, img in slides:
        p = TMP_DIR / f"{name}.png"
        img.save(p, "PNG")
        paths.append(p)
        print(f"saved {p.name}  ({p.stat().st_size // 1024} KB)")

    # Assemble PDF
    pdf_path = OUT_DIR / "week12_monday_carousel.pdf"
    with open(pdf_path, "wb") as f:
        f.write(img2pdf.convert([str(p) for p in paths]))
    print(f"\nPDF: {pdf_path}  ({pdf_path.stat().st_size // 1024} KB, {len(paths)} slides)")

if __name__ == "__main__":
    main()
