"""Week 14 carousel — Auditor's Worksheet / Green Ledger Book aesthetic.
9 slides at 1080x1350 portrait. The 5-Category Operational Waste Map.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import img2pdf
import random

OUT_DIR = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\social_media")
TMP_DIR = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\week14_slides")
TMP_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1350
MARGIN = 80

# Auditor's Worksheet palette — green ledger paper + accountant ink + audit red
LEDGER_CREAM  = (244, 238, 218)   # base ledger paper
LEDGER_GREEN_LT = (216, 230, 198) # banded row green
LEDGER_GREEN_RULE = (128, 158, 102) # column/row rule lines
INK           = (24, 20, 16)       # accountant black ink
INK_SOFT      = (74, 60, 48)
AUDIT_RED     = (170, 30, 24)     # red pen audit annotation
AUDIT_RED_DK  = (122, 22, 18)
SEPIA         = (110, 92, 66)     # faded aged accent
RULE_RED      = (164, 80, 70)     # red column ruling
PAPER_SHADOW  = (180, 165, 130)

FONTS = Path(r"C:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS\.claude\skills\canvas-design\canvas-fonts")

def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)

def plex_serif(size, bold=False):
    return font("IBMPlexSerif-Bold.ttf" if bold else "IBMPlexSerif-Regular.ttf", size)
def work(size, bold=False):
    return font("WorkSans-Bold.ttf" if bold else "WorkSans-Regular.ttf", size)
def mono(size, bold=False):
    return font("JetBrainsMono-Bold.ttf" if bold else "JetBrainsMono-Regular.ttf", size)
def big_shoulders(size):
    return font("BigShoulders-Bold.ttf", size)
def crimson_italic(size):
    return font("CrimsonPro-Italic.ttf", size)
def gloock(size):
    return font("Gloock-Regular.ttf", size)


def make_ledger_canvas():
    """Pale green columnar ledger paper with horizontal banded rows + faint vertical rules."""
    img = Image.new("RGB", (W, H), LEDGER_CREAM)
    draw = ImageDraw.Draw(img)
    # Alternating row bands every 40px starting from y=140 (under the masthead)
    band_h = 40
    y = 140
    band_count = 0
    while y < H - 80:
        if band_count % 2 == 0:
            draw.rectangle([(0, y), (W, y + band_h)], fill=LEDGER_GREEN_LT)
        y += band_h
        band_count += 1
    # Horizontal rule lines (every 40px)
    y = 140
    while y < H - 80:
        draw.line([(MARGIN, y), (W - MARGIN, y)], fill=LEDGER_GREEN_RULE, width=1)
        y += band_h
    # Vertical red column rule (right side — like an accounting amount column)
    col_x = W - MARGIN - 200
    draw.line([(col_x, 140), (col_x, H - 80)], fill=RULE_RED, width=1)
    # Slight inner edge tint to look like aged paper
    px = img.load()
    random.seed(141)
    for _ in range(W * H // 70):
        x = random.randint(0, W - 1)
        y_n = random.randint(0, H - 1)
        darken = random.randint(0, 20)
        r, g, b = px[x, y_n]
        px[x, y_n] = (max(0, r - darken), max(0, g - darken), max(0, b - darken))
    # Edge shadow vignette
    overlay = ImageDraw.Draw(img, "RGBA")
    for i in range(18):
        a = max(0, 8 - int(i * 0.4))
        overlay.rectangle([i, i, W - i, H - i], outline=(80, 60, 40, a), width=1)
    return img


def draw_masthead(draw, slide_label):
    """Top auditor's worksheet header strip."""
    # Top thick rule
    draw.rectangle([(MARGIN, 50), (W - MARGIN, 55)], fill=INK)
    # Title
    f_title = big_shoulders(38)
    draw.text((MARGIN, 65), "MARGIN RECOVERY AUDIT", fill=INK, font=f_title)
    f_sub = crimson_italic(18)
    draw.text((MARGIN, 110), "an operator's worksheet", fill=AUDIT_RED, font=f_sub)
    # Right side: slide label + date
    f_meta = mono(14, bold=True)
    bbox = draw.textbbox((0, 0), slide_label, font=f_meta)
    tw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - tw, 65), slide_label, fill=INK, font=f_meta)
    date_str = "WEEK OF JUN 15, 2026"
    bbox = draw.textbbox((0, 0), date_str, font=f_meta)
    tw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - tw, 95), date_str, fill=INK_SOFT, font=f_meta)
    # Lower double rule
    draw.line([(MARGIN, 134), (W - MARGIN, 134)], fill=INK, width=2)
    draw.line([(MARGIN, 138), (W - MARGIN, 138)], fill=INK, width=1)


def draw_footer(draw, page_num, total=9):
    draw.line([(MARGIN, H - 70), (W - MARGIN, H - 70)], fill=INK, width=1)
    f_foot = mono(13, bold=True)
    draw.text((MARGIN, H - 50), "DUX MACHINA / AUDIT DESK", fill=INK, font=f_foot)
    page_str = f"PG. {page_num:02d}/{total:02d}"
    bbox = draw.textbbox((0, 0), page_str, font=f_foot)
    pw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - pw, H - 50), page_str, fill=INK, font=f_foot)


def paste_rotated_stamp(target_img, x, y, text, font_obj, color=AUDIT_RED, padding_x=20, padding_y=10, angle=-7, border_w=4):
    """Red rubber-stamp callout (rotated)."""
    tmp = Image.new("RGB", (10, 10))
    bbox = ImageDraw.Draw(tmp).textbbox((0, 0), text, font=font_obj)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    w_box = tw + padding_x * 2
    h_box = th + padding_y * 2 + 4
    stamp_img = Image.new("RGBA", (w_box + 24, h_box + 24), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp_img)
    sd.rectangle([12, 12, 12 + w_box, 12 + h_box], outline=color + (255,), width=border_w)
    sd.rectangle([12 + border_w + 3, 12 + border_w + 3, 12 + w_box - border_w - 3, 12 + h_box - border_w - 3],
                 outline=color + (255,), width=1)
    sd.text((12 + padding_x, 12 + padding_y), text, fill=color + (255,), font=font_obj)
    stamp_img = stamp_img.rotate(angle, resample=Image.BICUBIC, expand=True)
    target_img.paste(stamp_img, (x, y), stamp_img)


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


def draw_wrapped(draw, x, y, text, font_obj, max_width, line_height, color=INK):
    lines = wrap_text(draw, text, font_obj, max_width)
    for i, line in enumerate(lines):
        draw.text((x, y + i * line_height), line, fill=color, font=font_obj)
    return y + len(lines) * line_height


def text_center(draw, y, text, font_obj, color=INK):
    bbox = draw.textbbox((0, 0), text, font=font_obj)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, fill=color, font=font_obj)


def draw_strikethrough_line(draw, x, y, w, color=AUDIT_RED, thickness=3):
    """Hand-drawn audit strikethrough."""
    draw.line([(x, y), (x + w, y)], fill=color, width=thickness)


def draw_category_row(img, draw, row_y, roman, label, amount_pct, amount_dollar):
    """Standard ledger row for a waste category."""
    f_roman = gloock(72)
    f_label = big_shoulders(36)
    f_pct = mono(28, bold=True)
    f_dollar = mono(22, bold=True)
    # Roman numeral in red
    draw.text((MARGIN + 10, row_y), roman, fill=AUDIT_RED, font=f_roman)
    # Label
    draw.text((MARGIN + 140, row_y + 12), label, fill=INK, font=f_label)
    # Right column: % of revenue
    pct_text = amount_pct
    bbox = draw.textbbox((0, 0), pct_text, font=f_pct)
    pw = bbox[2] - bbox[0]
    col_right = W - MARGIN - 20
    draw.text((col_right - pw, row_y + 12), pct_text, fill=AUDIT_RED, font=f_pct)
    # Dollar amount in smaller print under
    dollar_text = amount_dollar
    bbox = draw.textbbox((0, 0), dollar_text, font=f_dollar)
    pw = bbox[2] - bbox[0]
    draw.text((col_right - pw, row_y + 50), dollar_text, fill=INK_SOFT, font=f_dollar)


# ────────────────────────────────────────────────────────────────────
# SLIDE 1 — COVER PAGE
# ────────────────────────────────────────────────────────────────────
def slide_1():
    img = make_ledger_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "WORKSHEET No. 014")

    # FILE No. block (top-left under masthead)
    f_file = mono(15, bold=True)
    draw.text((MARGIN, 165), "FILE No.    014 / 2026-06", fill=INK, font=f_file)
    draw.text((MARGIN, 195), "AUDITOR     OPERATOR'S DESK", fill=INK, font=f_file)
    draw.text((MARGIN, 225), "SUBJECT     OPERATIONAL WASTE", fill=INK, font=f_file)

    # Big title
    f_title = plex_serif(74, bold=True)
    y = 320
    title_lines = ["Your business", "is leaking", "12-18%"]
    for line in title_lines:
        color = AUDIT_RED if "12-18" in line else INK
        draw.text((MARGIN, y), line, fill=color, font=f_title)
        y += 88

    # Subtitle
    f_sub = crimson_italic(28)
    y += 30
    draw.text((MARGIN, y), "of revenue. through 5 categories.", fill=INK_SOFT, font=f_sub)
    f_sub2 = crimson_italic(28)
    draw.text((MARGIN, y + 38), "nobody on the team is tracking.", fill=INK_SOFT, font=f_sub2)

    # FOUND IN ERROR stamp top right
    paste_rotated_stamp(img, W - 380, 175, "MARGIN LEAK", big_shoulders(38),
                        color=AUDIT_RED, padding_x=22, padding_y=10, angle=-8)
    paste_rotated_stamp(img, W - 380, 285, "CONFIRMED", big_shoulders(28),
                        color=AUDIT_RED, padding_x=18, padding_y=8, angle=5)

    # Cross-industry signal box at bottom
    f_evidence = mono(14, bold=True)
    draw.text((MARGIN, 1130), "EVIDENCE SAMPLE — CROSS-INDUSTRY", fill=AUDIT_RED, font=f_evidence)
    f_industries = mono(15)
    inds = "SaaS / Pro Services / Manufacturing / Agencies / Healthcare"
    draw.text((MARGIN, 1160), inds, fill=INK, font=f_industries)

    draw_footer(draw, 1)
    return img


# ────────────────────────────────────────────────────────────────────
# SLIDE 2 — THE FINDING / WHY IT LEAKS
# ────────────────────────────────────────────────────────────────────
def slide_2():
    img = make_ledger_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "ENTRY 02 — THE FINDING")

    # Section label
    f_section = mono(14, bold=True)
    draw.text((MARGIN, 170), "── PRELIMINARY FINDING ──", fill=AUDIT_RED, font=f_section)

    # Big serif pierce
    f_hl = plex_serif(54, bold=True)
    y = 220
    lines = [
        "The waste is",
        "not theft.",
    ]
    for line in lines:
        draw.text((MARGIN, y), line, fill=INK, font=f_hl)
        y += 66

    # Crimson italic counter
    f_counter = crimson_italic(40)
    y += 30
    counter_lines = [
        "It is structural.",
        "It lives in the seams",
        "between departments.",
    ]
    for line in counter_lines:
        draw.text((MARGIN, y), line, fill=AUDIT_RED, font=f_counter)
        y += 52

    # Body explanation
    f_body = work(20)
    y += 30
    body = ("Marketing blames sales. Sales blames operations. Operations blames "
            "the product. Each leak lives just inside the edge of somebody "
            "else's accountability. Which is why none of them get fixed.")
    draw_wrapped(draw, MARGIN, y, body, f_body, W - MARGIN * 2, 32, color=INK)

    # FOUND stamp top right
    paste_rotated_stamp(img, W - 320, 175, "ROOT CAUSE", big_shoulders(30),
                        color=AUDIT_RED, padding_x=18, padding_y=8, angle=-6)

    draw_footer(draw, 2)
    return img


# ────────────────────────────────────────────────────────────────────
# SLIDE 3 — THE FIVE CATEGORIES (ledger overview)
# ────────────────────────────────────────────────────────────────────
def slide_3():
    img = make_ledger_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "ENTRY 03 — INDEX")

    # Section banner
    draw.rectangle([(MARGIN, 165), (W - MARGIN, 230)], fill=INK)
    f_banner = big_shoulders(42)
    text_center(draw, 175, "FIVE CATEGORIES OF HIDDEN WASTE", f_banner, color=LEDGER_CREAM)

    # Column header row
    f_col = mono(14, bold=True)
    draw.text((MARGIN + 10, 252), "#", fill=AUDIT_RED, font=f_col)
    draw.text((MARGIN + 140, 252), "CATEGORY", fill=AUDIT_RED, font=f_col)
    draw.text((W - MARGIN - 240, 252), "% OF REVENUE", fill=AUDIT_RED, font=f_col)
    draw.line([(MARGIN, 280), (W - MARGIN, 280)], fill=INK, width=2)

    # Five rows
    categories = [
        ("I",   "CUSTOMER ACQUISITION LEAK",   "2-4%"),
        ("II",  "PRICING POSITION LEAK",       "3-5%"),
        ("III", "DECISION LATENCY LEAK",       "1-3%"),
        ("IV",  "DUPLICATE-SYSTEM LEAK",       "2-3%"),
        ("V",   "DEPARTMENT HANDOFF LEAK",     "3-4%"),
    ]
    row_y = 305
    row_h = 140
    f_roman = gloock(64)
    f_cat = big_shoulders(28)
    f_pct = mono(34, bold=True)
    for cat in categories:
        draw.text((MARGIN + 10, row_y), cat[0], fill=AUDIT_RED, font=f_roman)
        draw.text((MARGIN + 140, row_y + 20), cat[1], fill=INK, font=f_cat)
        pct = cat[2]
        bbox = draw.textbbox((0, 0), pct, font=f_pct)
        pw = bbox[2] - bbox[0]
        draw.text((W - MARGIN - pw - 20, row_y + 18), pct, fill=AUDIT_RED, font=f_pct)
        draw.line([(MARGIN, row_y + row_h - 20), (W - MARGIN, row_y + row_h - 20)],
                  fill=LEDGER_GREEN_RULE, width=1)
        row_y += row_h

    # Total tally row
    total_y = row_y - 10
    f_total_label = big_shoulders(36)
    draw.text((MARGIN + 140, total_y + 10), "TOTAL LEAK", fill=INK, font=f_total_label)
    f_total_val = mono(48, bold=True)
    total_str = "12-18%"
    bbox = draw.textbbox((0, 0), total_str, font=f_total_val)
    pw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - pw - 20, total_y), total_str, fill=AUDIT_RED, font=f_total_val)

    draw_footer(draw, 3)
    return img


# ────────────────────────────────────────────────────────────────────
# SLIDE 4 — CATEGORY I: CAC LEAK
# ────────────────────────────────────────────────────────────────────
def slide_4():
    img = make_ledger_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "CATEGORY I")

    # Roman numeral huge
    f_roman = gloock(280)
    draw.text((MARGIN, 165), "I", fill=AUDIT_RED, font=f_roman)

    # Label
    f_label = big_shoulders(58)
    draw.text((MARGIN + 200, 225), "ACQUISITION COST LEAK", fill=INK, font=f_label)
    f_sub = crimson_italic(24)
    draw.text((MARGIN + 200, 285), "paying to acquire customers the system cannot retain.", fill=INK_SOFT, font=f_sub)

    # The mechanism
    f_lbl = mono(15, bold=True)
    draw.text((MARGIN, 510), "THE MECHANISM", fill=AUDIT_RED, font=f_lbl)
    f_body = work(22)
    body = ("CFO sees acquisition cost in one P&L and churn in another. "
            "Never runs them together. The actual cost per kept customer "
            "is 2-3x the reported number.")
    draw_wrapped(draw, MARGIN, 545, body, f_body, W - MARGIN * 2, 34, color=INK)

    # Dollar callout
    draw.line([(MARGIN, 760), (W - MARGIN, 760)], fill=INK, width=2)
    draw.line([(MARGIN, 765), (W - MARGIN, 765)], fill=INK, width=1)
    f_amount_lbl = mono(16, bold=True)
    draw.text((MARGIN, 790), "TYPICAL LEAK / 10M REVENUE COMPANY", fill=INK_SOFT, font=f_amount_lbl)
    f_amount = gloock(140)
    draw.text((MARGIN, 825), "$200-400K", fill=AUDIT_RED, font=f_amount)
    f_unit = work(20)
    draw.text((MARGIN, 990), "per year, walking out the door.", fill=INK_SOFT, font=f_unit)

    # Stamp
    paste_rotated_stamp(img, W - 320, 175, "FOUND", big_shoulders(40),
                        color=AUDIT_RED, padding_x=24, padding_y=10, angle=-6)

    draw_footer(draw, 4)
    return img


# ────────────────────────────────────────────────────────────────────
# SLIDE 5 — CATEGORY II: PRICING POSITION
# ────────────────────────────────────────────────────────────────────
def slide_5():
    img = make_ledger_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "CATEGORY II")

    f_roman = gloock(280)
    draw.text((MARGIN, 165), "II", fill=AUDIT_RED, font=f_roman)

    f_label = big_shoulders(58)
    draw.text((MARGIN + 290, 225), "PRICING POSITION LEAK", fill=INK, font=f_label)
    f_sub = crimson_italic(24)
    draw.text((MARGIN + 290, 285), "the floor moved. the seller did not.", fill=INK_SOFT, font=f_sub)

    f_lbl = mono(15, bold=True)
    draw.text((MARGIN, 510), "THE MECHANISM", fill=AUDIT_RED, font=f_lbl)
    f_body = work(22)
    body = ("Price set 3 years ago based on competitor pricing. Buyers paying "
            "without negotiation = the floor has moved up. Each closed deal "
            "at the old price is a transfer from your company to the buyer.")
    draw_wrapped(draw, MARGIN, 545, body, f_body, W - MARGIN * 2, 34, color=INK)

    draw.line([(MARGIN, 760), (W - MARGIN, 760)], fill=INK, width=2)
    draw.line([(MARGIN, 765), (W - MARGIN, 765)], fill=INK, width=1)
    f_amount_lbl = mono(16, bold=True)
    draw.text((MARGIN, 790), "TYPICAL LEAK / 10M REVENUE COMPANY", fill=INK_SOFT, font=f_amount_lbl)
    f_amount = gloock(140)
    draw.text((MARGIN, 825), "$300-500K", fill=AUDIT_RED, font=f_amount)
    f_unit = work(20)
    draw.text((MARGIN, 990), "in unclaimed margin per year.", fill=INK_SOFT, font=f_unit)

    paste_rotated_stamp(img, W - 320, 175, "FOUND", big_shoulders(40),
                        color=AUDIT_RED, padding_x=24, padding_y=10, angle=4)

    draw_footer(draw, 5)
    return img


# ────────────────────────────────────────────────────────────────────
# SLIDE 6 — CATEGORY III: DECISION LATENCY
# ────────────────────────────────────────────────────────────────────
def slide_6():
    img = make_ledger_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "CATEGORY III")

    f_roman = gloock(280)
    draw.text((MARGIN, 165), "III", fill=AUDIT_RED, font=f_roman)

    f_label = big_shoulders(54)
    draw.text((MARGIN + 380, 225), "DECISION LATENCY", fill=INK, font=f_label)
    f_sub = crimson_italic(24)
    draw.text((MARGIN + 380, 280), "authorization queues. paused work. real dollars.", fill=INK_SOFT, font=f_sub)

    f_lbl = mono(15, bold=True)
    draw.text((MARGIN, 510), "THE MECHANISM", fill=AUDIT_RED, font=f_lbl)
    f_body = work(22)
    body = ("Decisions stack up on the founder's desk. Work behind them stalls. "
            "Each day of stall has a dollar cost. The cost does not appear on "
            "a P&L because the work was paused, not lost. But paused work IS "
            "the leak.")
    draw_wrapped(draw, MARGIN, 545, body, f_body, W - MARGIN * 2, 34, color=INK)

    draw.line([(MARGIN, 760), (W - MARGIN, 760)], fill=INK, width=2)
    draw.line([(MARGIN, 765), (W - MARGIN, 765)], fill=INK, width=1)
    f_amount_lbl = mono(16, bold=True)
    draw.text((MARGIN, 790), "TYPICAL LEAK / 10M REVENUE COMPANY", fill=INK_SOFT, font=f_amount_lbl)
    f_amount = gloock(140)
    draw.text((MARGIN, 825), "$100-300K", fill=AUDIT_RED, font=f_amount)
    f_unit = work(20)
    draw.text((MARGIN, 990), "in stalled team output per year.", fill=INK_SOFT, font=f_unit)

    paste_rotated_stamp(img, W - 320, 175, "FOUND", big_shoulders(40),
                        color=AUDIT_RED, padding_x=24, padding_y=10, angle=-5)

    draw_footer(draw, 6)
    return img


# ────────────────────────────────────────────────────────────────────
# SLIDE 7 — CATEGORY IV: DUPLICATE SYSTEMS
# ────────────────────────────────────────────────────────────────────
def slide_7():
    img = make_ledger_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "CATEGORY IV")

    f_roman = gloock(280)
    draw.text((MARGIN, 165), "IV", fill=AUDIT_RED, font=f_roman)

    f_label = big_shoulders(50)
    draw.text((MARGIN + 330, 225), "DUPLICATE SYSTEMS", fill=INK, font=f_label)
    f_sub = crimson_italic(24)
    draw.text((MARGIN + 330, 280), "three tools doing one job. data does not sync.", fill=INK_SOFT, font=f_sub)

    f_lbl = mono(15, bold=True)
    draw.text((MARGIN, 510), "THE MECHANISM", fill=AUDIT_RED, font=f_lbl)
    f_body = work(22)
    body = ("Marketing has a CRM. Sales has another. Customer success uses a "
            "third. Data does not sync. Licenses overlap. Nobody owns "
            "consolidation because each department defends its own tool. "
            "The duplication is invisible until somebody audits the stack.")
    draw_wrapped(draw, MARGIN, 545, body, f_body, W - MARGIN * 2, 34, color=INK)

    draw.line([(MARGIN, 760), (W - MARGIN, 760)], fill=INK, width=2)
    draw.line([(MARGIN, 765), (W - MARGIN, 765)], fill=INK, width=1)
    f_amount_lbl = mono(16, bold=True)
    draw.text((MARGIN, 790), "TYPICAL LEAK / 10M REVENUE COMPANY", fill=INK_SOFT, font=f_amount_lbl)
    f_amount = gloock(140)
    draw.text((MARGIN, 825), "$200-300K", fill=AUDIT_RED, font=f_amount)
    f_unit = work(20)
    draw.text((MARGIN, 990), "in overlap + license + sync cost per year.", fill=INK_SOFT, font=f_unit)

    paste_rotated_stamp(img, W - 320, 175, "FOUND", big_shoulders(40),
                        color=AUDIT_RED, padding_x=24, padding_y=10, angle=6)

    draw_footer(draw, 7)
    return img


# ────────────────────────────────────────────────────────────────────
# SLIDE 8 — CATEGORY V: HANDOFF LEAK
# ────────────────────────────────────────────────────────────────────
def slide_8():
    img = make_ledger_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "CATEGORY V")

    f_roman = gloock(280)
    draw.text((MARGIN, 165), "V", fill=AUDIT_RED, font=f_roman)

    f_label = big_shoulders(58)
    draw.text((MARGIN + 220, 225), "HANDOFF FIDELITY LEAK", fill=INK, font=f_label)
    f_sub = crimson_italic(24)
    draw.text((MARGIN + 220, 285), "work loses fidelity at every department boundary.", fill=INK_SOFT, font=f_sub)

    f_lbl = mono(15, bold=True)
    draw.text((MARGIN, 510), "THE MECHANISM", fill=AUDIT_RED, font=f_lbl)
    f_body = work(22)
    body = ("Sales hands customer to onboarding without context. Onboarding "
            "hands the relationship to customer success without contract "
            "terms. Every handoff is a chance for the customer to feel like "
            "they are starting over with a new vendor.")
    draw_wrapped(draw, MARGIN, 545, body, f_body, W - MARGIN * 2, 34, color=INK)

    draw.line([(MARGIN, 760), (W - MARGIN, 760)], fill=INK, width=2)
    draw.line([(MARGIN, 765), (W - MARGIN, 765)], fill=INK, width=1)
    f_amount_lbl = mono(16, bold=True)
    draw.text((MARGIN, 790), "TYPICAL LEAK / 10M REVENUE COMPANY", fill=INK_SOFT, font=f_amount_lbl)
    f_amount = gloock(140)
    draw.text((MARGIN, 825), "$300-400K", fill=AUDIT_RED, font=f_amount)
    f_unit = work(20)
    draw.text((MARGIN, 990), "in churn + rework cost per year.", fill=INK_SOFT, font=f_unit)

    paste_rotated_stamp(img, W - 320, 175, "FOUND", big_shoulders(40),
                        color=AUDIT_RED, padding_x=24, padding_y=10, angle=-7)

    draw_footer(draw, 8)
    return img


# ────────────────────────────────────────────────────────────────────
# SLIDE 9 — TOTAL + QUESTION CLOSE
# ────────────────────────────────────────────────────────────────────
def slide_9():
    img = make_ledger_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "AUDIT TOTAL")

    # AUDIT COMPLETE stamp
    paste_rotated_stamp(img, MARGIN, 170, "AUDIT COMPLETE", big_shoulders(38),
                        color=AUDIT_RED, padding_x=22, padding_y=10, angle=-4)

    # Big total
    f_total_lbl = mono(18, bold=True)
    draw.text((MARGIN, 320), "AGGREGATE LEAK / 10M REVENUE COMPANY", fill=INK, font=f_total_lbl)
    f_total = gloock(200)
    draw.text((MARGIN, 360), "$1.2-1.8M", fill=AUDIT_RED, font=f_total)
    f_total_unit = crimson_italic(28)
    draw.text((MARGIN, 580), "walking out the door inside a year.", fill=INK_SOFT, font=f_total_unit)

    # The fix
    draw.line([(MARGIN, 660), (W - MARGIN, 660)], fill=INK, width=2)
    draw.line([(MARGIN, 665), (W - MARGIN, 665)], fill=INK, width=1)
    f_fix_lbl = mono(16, bold=True)
    draw.text((MARGIN, 690), "THE FIX", fill=AUDIT_RED, font=f_fix_lbl)
    f_fix = work(22)
    fix_text = ("Don't fix symptoms. Fix seams. Name an owner for each category. "
                "Give that owner authority to redesign the handoff.")
    draw_wrapped(draw, MARGIN, 725, fix_text, f_fix, W - MARGIN * 2, 34, color=INK)

    # Question close
    draw.line([(MARGIN, 880), (W - MARGIN, 880)], fill=AUDIT_RED, width=2)
    f_q_lbl = mono(15, bold=True)
    draw.text((MARGIN, 905), "FOR THE OPERATOR'S DESK", fill=AUDIT_RED, font=f_q_lbl)
    f_q = plex_serif(28, bold=True)
    q_text = ("What is the dollar value of one seam between two "
              "departments in your company right now that nobody owns?")
    draw_wrapped(draw, MARGIN, 940, q_text, f_q, W - MARGIN * 2, 40, color=INK)

    # Sign-off
    f_signoff = crimson_italic(20)
    text_center(draw, H - 130, "filed by the auditor's desk.", f_signoff, color=INK_SOFT)
    f_pub = work(14, bold=True)
    text_center(draw, H - 100, "DUX MACHINA  /  STRATEGY THAT BUILDS.", f_pub, color=INK)

    draw_footer(draw, 9)
    return img


# ────────────────────────────────────────────────────────────────────
# BUILD
# ────────────────────────────────────────────────────────────────────
def main():
    slides = [
        ("slide_01_cover", slide_1()),
        ("slide_02_finding", slide_2()),
        ("slide_03_index", slide_3()),
        ("slide_04_cac", slide_4()),
        ("slide_05_pricing", slide_5()),
        ("slide_06_latency", slide_6()),
        ("slide_07_duplicate", slide_7()),
        ("slide_08_handoff", slide_8()),
        ("slide_09_total", slide_9()),
    ]
    paths = []
    for name, img in slides:
        p = TMP_DIR / f"{name}.png"
        img.save(p, "PNG")
        paths.append(p)
        print(f"saved {p.name}  ({p.stat().st_size // 1024} KB)")
    pdf_path = OUT_DIR / "week14_monday_carousel.pdf"
    with open(pdf_path, "wb") as f:
        f.write(img2pdf.convert([str(p) for p in paths]))
    print(f"\nPDF: {pdf_path}  ({pdf_path.stat().st_size // 1024} KB, {len(paths)} slides)")


if __name__ == "__main__":
    main()
