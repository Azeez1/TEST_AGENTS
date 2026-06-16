"""Week 14 carousel v3 — Office Floor Plan / Architectural Blueprint.
Fixes: leak markers at actual seams, no compass overlap, centered room
labels, clean leak index table below plan.
9 slides at 1080x1350 portrait.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import img2pdf
import math

OUT_DIR = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\social_media")
TMP_DIR = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\week14_slides_v3")
TMP_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1350
MARGIN = 60

WARM_WHITE   = (250, 248, 244)
GRID_FAINT   = (228, 228, 234)
WALL_INK     = (22, 22, 28)
LINE_MID     = (140, 142, 152)
LINE_FADED   = (185, 188, 196)
TEXT_INK     = (32, 32, 38)
TEXT_SOFT    = (110, 112, 124)
DRAFT_BLUE   = (38, 78, 138)
LEAK_RED     = (212, 50, 40)
LEAK_RED_DIM = (215, 175, 170)
LEAK_BG      = (252, 232, 228)
ROOM_TINT    = (244, 246, 250)

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


def make_canvas():
    img = Image.new("RGB", (W, H), WARM_WHITE)
    draw = ImageDraw.Draw(img)
    for x in range(0, W, 30):
        draw.line([(x, 0), (x, H)], fill=GRID_FAINT, width=1)
    for y in range(0, H, 30):
        draw.line([(0, y), (W, y)], fill=GRID_FAINT, width=1)
    return img


def draw_dashed_line(draw, x1, y1, x2, y2, fill, width=1, dash=8, gap=5):
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        return
    ux, uy = dx / length, dy / length
    pos = 0
    while pos < length:
        seg_end = min(pos + dash, length)
        sx = x1 + ux * pos
        sy = y1 + uy * pos
        ex = x1 + ux * seg_end
        ey = y1 + uy * seg_end
        draw.line([(sx, sy), (ex, ey)], fill=fill, width=width)
        pos += dash + gap


def draw_dashed_circle(draw, cx, cy, r, color, width=2, dash_count=14):
    arc_each = 360 / dash_count
    arc_on = arc_each * 0.55
    for i in range(dash_count):
        start = i * arc_each
        end = start + arc_on
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=start, end=end, fill=color, width=width)


def draw_masthead(draw, sheet_label):
    draw.line([(MARGIN, 55), (W - MARGIN, 55)], fill=WALL_INK, width=2)
    f = mono(13, bold=True)
    draw.text((MARGIN, 70), "PROJECT: MARGIN RECOVERY  /  CLIENT: THE OPERATOR  /  ISSUE 014",
              fill=TEXT_INK, font=f)
    bbox = draw.textbbox((0, 0), sheet_label, font=f)
    tw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - tw, 70), sheet_label, fill=TEXT_INK, font=f)
    draw.line([(MARGIN, 95), (W - MARGIN, 95)], fill=WALL_INK, width=1)


def draw_footer(draw, sheet_num, total=9):
    block_y = H - 75
    draw.line([(MARGIN, block_y), (W - MARGIN, block_y)], fill=WALL_INK, width=2)
    draw.line([(MARGIN, block_y + 4), (W - MARGIN, block_y + 4)], fill=WALL_INK, width=1)
    f = mono(12, bold=True)
    draw.text((MARGIN, block_y + 18), "DUX MACHINA  /  ARCHITECTURE OF OPERATIONS", fill=TEXT_INK, font=f)
    sheet_str = f"SHEET {sheet_num:02d} OF {total:02d}"
    bbox = draw.textbbox((0, 0), sheet_str, font=f)
    sw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - sw, block_y + 18), sheet_str, fill=TEXT_INK, font=f)
    f2 = mono(11)
    draw.text((MARGIN, block_y + 40), "SCALE: NTS    DRAWN: OPERATOR'S DESK    DATE: 2026-06-15",
              fill=TEXT_SOFT, font=f2)


def draw_compass_rose(draw, cx, cy, size=24):
    draw.ellipse([cx - size, cy - size, cx + size, cy + size], outline=WALL_INK, width=2)
    n_pts = [(cx, cy - size + 3), (cx - size * 0.25, cy), (cx + size * 0.25, cy)]
    draw.polygon(n_pts, fill=WALL_INK)
    s_pts = [(cx, cy + size - 3), (cx - size * 0.25, cy), (cx + size * 0.25, cy)]
    draw.polygon(s_pts, outline=WALL_INK, width=2)
    f = mono(10, bold=True)
    bbox = draw.textbbox((0, 0), "N", font=f)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, cy - size - 18), "N", fill=WALL_INK, font=f)


def draw_scale_bar(draw, x, y, scale=1.0):
    seg_w = int(20 * scale)
    for i in range(4):
        fill = WALL_INK if i % 2 == 0 else WARM_WHITE
        draw.rectangle([x + i * seg_w, y, x + (i + 1) * seg_w, y + 7],
                       outline=WALL_INK, fill=fill, width=1)
    f = mono(9, bold=True)
    for i, label in enumerate(["0", "10", "20", "30", "40"]):
        draw.text((x + i * seg_w - 3, y + 10), label, fill=TEXT_INK, font=f)
    draw.text((x, y - 16), "SCALE (FT)", fill=TEXT_SOFT, font=f)


def draw_furniture(draw, x0, y0, x1, y1, count_x=2, count_y=2, desk_color=LINE_MID):
    """Draw simple desk rectangles in a 2x2 pattern inside a room, with chairs."""
    rw = (x1 - x0)
    rh = (y1 - y0)
    # Leave room for label at top center (extra padding top, sublabel pushed deeper too)
    pad_top = 100
    pad = 20
    avail_w = rw - pad * 2
    avail_h = rh - pad_top - pad
    cell_w = avail_w / count_x
    cell_h = avail_h / count_y
    desk_w = int(cell_w * 0.50)
    desk_h = int(cell_h * 0.30)
    for i in range(count_x):
        for j in range(count_y):
            dx = x0 + pad + int(i * cell_w + (cell_w - desk_w) / 2)
            dy = y0 + pad_top + int(j * cell_h + (cell_h - desk_h) / 2)
            draw.rectangle([dx, dy, dx + desk_w, dy + desk_h],
                           outline=desk_color, width=1)
            # Chair circle next to desk
            chair_r = 4
            cx = dx + desk_w + 6
            cy = dy + desk_h // 2
            draw.ellipse([cx - chair_r, cy - chair_r, cx + chair_r, cy + chair_r],
                         outline=desk_color, width=1)


def draw_room(draw, x0, y0, x1, y1, label, sublabel=None, desk_pattern=(2, 2),
              door_side=None, door_pos=0.5):
    """Draw a room: thick wall outline + optional door + centered top label + furniture."""
    wall_w = 5
    door_w = 28
    # Walls
    # Top
    if door_side == "top":
        gap_x = x0 + (x1 - x0) * door_pos
        draw.line([(x0, y0), (gap_x - door_w // 2, y0)], fill=WALL_INK, width=wall_w)
        draw.line([(gap_x + door_w // 2, y0), (x1, y0)], fill=WALL_INK, width=wall_w)
    else:
        draw.line([(x0, y0), (x1, y0)], fill=WALL_INK, width=wall_w)
    # Bottom
    if door_side == "bottom":
        gap_x = x0 + (x1 - x0) * door_pos
        draw.line([(x0, y1), (gap_x - door_w // 2, y1)], fill=WALL_INK, width=wall_w)
        draw.line([(gap_x + door_w // 2, y1), (x1, y1)], fill=WALL_INK, width=wall_w)
    else:
        draw.line([(x0, y1), (x1, y1)], fill=WALL_INK, width=wall_w)
    # Left
    if door_side == "left":
        gap_y = y0 + (y1 - y0) * door_pos
        draw.line([(x0, y0), (x0, gap_y - door_w // 2)], fill=WALL_INK, width=wall_w)
        draw.line([(x0, gap_y + door_w // 2), (x0, y1)], fill=WALL_INK, width=wall_w)
    else:
        draw.line([(x0, y0), (x0, y1)], fill=WALL_INK, width=wall_w)
    # Right
    if door_side == "right":
        gap_y = y0 + (y1 - y0) * door_pos
        draw.line([(x1, y0), (x1, gap_y - door_w // 2)], fill=WALL_INK, width=wall_w)
        draw.line([(x1, gap_y + door_w // 2), (x1, y1)], fill=WALL_INK, width=wall_w)
    else:
        draw.line([(x1, y0), (x1, y1)], fill=WALL_INK, width=wall_w)

    # CENTERED room label — pushed deep enough into room to clear leak markers at top seam
    f_label = big_shoulders(18)
    bbox = draw.textbbox((0, 0), label, font=f_label)
    tw = bbox[2] - bbox[0]
    room_cx = (x0 + x1) // 2
    draw.text((room_cx - tw // 2, y0 + 50), label, fill=TEXT_INK, font=f_label)
    if sublabel:
        f_sub = mono(10)
        bbox = draw.textbbox((0, 0), sublabel, font=f_sub)
        sw = bbox[2] - bbox[0]
        draw.text((room_cx - sw // 2, y0 + 76), sublabel, fill=TEXT_SOFT, font=f_sub)

    # Furniture
    if desk_pattern:
        draw_furniture(draw, x0, y0, x1, y1, *desk_pattern)


# Floor plan geometry
PLAN_X0_DEFAULT = 110
PLAN_Y0_DEFAULT = 280
PLAN_W_DEFAULT = 860
PLAN_H_DEFAULT = 700

ROOMS = [
    (0, 0, "MARKETING",        "lead gen"),
    (1, 0, "SALES",            "pipeline"),
    (2, 0, "OPERATIONS",       "delivery"),
    (0, 1, "CUSTOMER SUCCESS", "retention"),
    (1, 1, "FOUNDER'S OFFICE", "decisions"),
    (2, 1, "FINANCE",          "books"),
]

# Each leak: (number, dollar, category, seam_position_key)
# seam_position_key:
#   ("v", col_seam, row_idx) — vertical seam at column boundary, in a specific row
#   ("h", col_idx, row_seam) — horizontal seam at row boundary, in a specific column
LEAKS = [
    ("01", "$200-400K", "CAC LEAK",            ("h", 0, 1)),  # MKTG ↔ CS horizontal seam, column 0
    ("02", "$300-500K", "PRICING POSITION",    ("v", 2, 1)),  # SALES ↔ OPS? no — SALES ↔ FINANCE vertical seam between col 1 and col 2 in row 1
    ("03", "$100-300K", "DECISION LATENCY",    ("h", 1, 1)),  # SALES ↔ FOUNDER horizontal seam, column 1
    ("04", "$200-300K", "DUPLICATE SYSTEMS",   ("v", 1, 0)),  # MKTG ↔ SALES vertical seam, row 0
    ("05", "$300-400K", "HANDOFF FIDELITY",    ("h", 2, 1)),  # OPS ↔ FINANCE horizontal seam, column 2
]


def leak_position(plan_x0, plan_y0, plan_w, plan_h, seam_key):
    """Compute pixel position for a leak seam_key tuple."""
    rw = plan_w / 3
    rh = plan_h / 2
    kind = seam_key[0]
    if kind == "h":
        # horizontal seam at row boundary, mid of column
        col_idx = seam_key[1]
        row_seam = seam_key[2]
        cx = plan_x0 + (col_idx + 0.5) * rw
        cy = plan_y0 + row_seam * rh
    elif kind == "v":
        # vertical seam at column boundary, mid of row
        col_seam = seam_key[1]
        row_idx = seam_key[2]
        cx = plan_x0 + col_seam * rw
        cy = plan_y0 + (row_idx + 0.5) * rh
    return int(cx), int(cy)


def draw_leak_marker(draw, cx, cy, leak_num, dim=False):
    """Compact leak marker: dashed outer ring + solid inner ring with number."""
    color = LEAK_RED_DIM if dim else LEAK_RED
    # Halo (only for active leak)
    if not dim:
        for r in [30, 28, 26]:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=LEAK_BG)
    # Outer dashed circle
    draw_dashed_circle(draw, cx, cy, 22, color, width=2, dash_count=12)
    # Inner solid circle
    draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], outline=color, width=2, fill=WARM_WHITE)
    # Leak number
    f_num = mono(12, bold=True)
    bbox = draw.textbbox((0, 0), leak_num, font=f_num)
    nw = bbox[2] - bbox[0]
    nh = bbox[3] - bbox[1]
    draw.text((cx - nw // 2, cy - nh // 2 - 4), leak_num, fill=color, font=f_num)


def draw_floor_plan(img, draw, plan_x0=PLAN_X0_DEFAULT, plan_y0=PLAN_Y0_DEFAULT,
                    plan_w=PLAN_W_DEFAULT, plan_h=PLAN_H_DEFAULT, highlight_leak=None,
                    show_furniture=True):
    """Draw the 6-room floor plan with leak markers."""
    rw = plan_w / 3
    rh = plan_h / 2
    # Background tint
    draw.rectangle([(plan_x0, plan_y0), (plan_x0 + plan_w, plan_y0 + plan_h)],
                   fill=ROOM_TINT)
    # Draw rooms
    for col, row, label, sublabel in ROOMS:
        x0 = int(plan_x0 + col * rw)
        y0 = int(plan_y0 + row * rh)
        x1 = int(plan_x0 + (col + 1) * rw)
        y1 = int(plan_y0 + (row + 1) * rh)
        draw_room(draw, x0, y0, x1, y1, label, sublabel,
                  desk_pattern=(2, 2) if show_furniture else None)
    # Draw leak markers (active first, dimmed others on top would be wrong — draw dimmed first)
    if highlight_leak is not None:
        # Draw dimmed first
        for i, leak in enumerate(LEAKS):
            if i != highlight_leak:
                cx, cy = leak_position(plan_x0, plan_y0, plan_w, plan_h, leak[3])
                draw_leak_marker(draw, cx, cy, leak[0], dim=True)
        # Then active on top
        i = highlight_leak
        cx, cy = leak_position(plan_x0, plan_y0, plan_w, plan_h, LEAKS[i][3])
        draw_leak_marker(draw, cx, cy, LEAKS[i][0], dim=False)
    else:
        for leak in LEAKS:
            cx, cy = leak_position(plan_x0, plan_y0, plan_w, plan_h, leak[3])
            draw_leak_marker(draw, cx, cy, leak[0], dim=False)


def wrap_lines(draw, text, font_obj, max_width):
    words = text.split()
    lines, cur = [], []
    for w in words:
        test = " ".join(cur + [w])
        bbox = draw.textbbox((0, 0), test, font=font_obj)
        if bbox[2] - bbox[0] <= max_width:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def draw_wrapped(draw, x, y, text, font_obj, max_width, line_height, color=TEXT_INK):
    for i, line in enumerate(wrap_lines(draw, text, font_obj, max_width)):
        draw.text((x, y + i * line_height), line, fill=color, font=font_obj)


# ────────────────────────────────────────────────────────────────────
# SLIDE 1 — COVER (no compass overlap)
# ────────────────────────────────────────────────────────────────────
def slide_1():
    img = make_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "SHEET 01 / COVER")

    # Eyebrow
    f_eyebrow = mono(13, bold=True)
    draw.text((MARGIN, 145), "FLOOR PLAN —", fill=DRAFT_BLUE, font=f_eyebrow)

    # Big serif title
    f_title = plex_serif(82, bold=True)
    draw.text((MARGIN, 180), "Where your", fill=TEXT_INK, font=f_title)
    draw.text((MARGIN, 270), "margin", fill=TEXT_INK, font=f_title)
    draw.text((MARGIN, 360), "actually", fill=TEXT_INK, font=f_title)
    draw.text((MARGIN, 450), "lives.", fill=LEAK_RED, font=f_title)

    # Subtitle
    f_sub = work(20)
    draw.text((MARGIN, 580), "5 leaks. 6 rooms. Most operators are losing 12-18%", fill=TEXT_SOFT, font=f_sub)
    draw.text((MARGIN, 608), "of revenue through the seams between them.", fill=TEXT_SOFT, font=f_sub)

    # Mini preview floor plan with leaks at proper seams
    mini_x0, mini_y0 = MARGIN + 20, 700
    mini_w, mini_h = W - 2 * (MARGIN + 20), 280
    mini_rw = mini_w / 3
    mini_rh = mini_h / 2
    # Background tint
    draw.rectangle([(mini_x0, mini_y0), (mini_x0 + mini_w, mini_y0 + mini_h)], fill=ROOM_TINT)
    # Room boxes
    for c in range(3):
        for r in range(2):
            rx0 = int(mini_x0 + c * mini_rw)
            ry0 = int(mini_y0 + r * mini_rh)
            rx1 = int(mini_x0 + (c + 1) * mini_rw)
            ry1 = int(mini_y0 + (r + 1) * mini_rh)
            draw.rectangle([rx0, ry0, rx1, ry1], outline=WALL_INK, width=4)
    # Leak markers at actual seams (3 vertical + 2 horizontal)
    leak_mini_positions = [
        # Horizontal seams (across row boundary) — at column midpoints
        (mini_x0 + 0.5 * mini_rw, mini_y0 + 1 * mini_rh),  # MKTG↔CS
        (mini_x0 + 1.5 * mini_rw, mini_y0 + 1 * mini_rh),  # SALES↔FNDR
        (mini_x0 + 2.5 * mini_rw, mini_y0 + 1 * mini_rh),  # OPS↔FINANCE
        # Vertical seams — at row midpoints
        (mini_x0 + 1 * mini_rw, mini_y0 + 0.5 * mini_rh),  # MKTG↔SALES
        (mini_x0 + 2 * mini_rw, mini_y0 + 1.5 * mini_rh),  # FNDR↔FINANCE
    ]
    for (lx, ly) in leak_mini_positions:
        lx, ly = int(lx), int(ly)
        draw.ellipse([lx - 16, ly - 16, lx + 16, ly + 16], fill=WARM_WHITE)
        draw.ellipse([lx - 13, ly - 13, lx + 13, ly + 13], fill=LEAK_RED)

    # Title block bottom — no compass on cover
    f_block = mono(11, bold=True)
    block_y = 1060
    draw.text((MARGIN, block_y),       "DRAWING:    OFFICE FLOOR PLAN, OPERATIONAL", fill=TEXT_INK, font=f_block)
    draw.text((MARGIN, block_y + 20),  "SUBJECT:    THE 5 SEAMS", fill=TEXT_INK, font=f_block)
    draw.text((MARGIN, block_y + 40),  "AUTHORITY:  OPERATOR'S DESK / DUX MACHINA", fill=TEXT_INK, font=f_block)
    draw.text((MARGIN, block_y + 60),  "DRAWING NO: DM-014-MON-01", fill=TEXT_INK, font=f_block)

    draw_footer(draw, 1)
    return img


# ────────────────────────────────────────────────────────────────────
# SLIDE 2 — THE PIERCE
# ────────────────────────────────────────────────────────────────────
def slide_2():
    img = make_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "SHEET 02 / FINDING")

    f_eyebrow = mono(13, bold=True)
    draw.text((MARGIN, 145), "FINDING —", fill=DRAFT_BLUE, font=f_eyebrow)

    f_lead = plex_serif(54, bold=True)
    y = 195
    for line, color in [("The waste", TEXT_INK), ("is not theft.", TEXT_INK), ("It is structural.", LEAK_RED)]:
        draw.text((MARGIN, y), line, fill=color, font=f_lead)
        y += 70

    # Two-department diagram
    y = 530
    box_w = (W - MARGIN * 2 - 100) // 2
    box_h = 200
    # Left box (DEPT A)
    draw.rectangle([MARGIN, y, MARGIN + box_w, y + box_h], outline=WALL_INK, width=5)
    f_box = big_shoulders(28)
    text = "DEPT A"
    bbox = draw.textbbox((0, 0), text, font=f_box)
    tw = bbox[2] - bbox[0]
    draw.text((MARGIN + (box_w - tw) // 2, y + 75), text, fill=TEXT_INK, font=f_box)
    f_sm = mono(13)
    text2 = "owns its work"
    bbox = draw.textbbox((0, 0), text2, font=f_sm)
    tw = bbox[2] - bbox[0]
    draw.text((MARGIN + (box_w - tw) // 2, y + 120), text2, fill=TEXT_SOFT, font=f_sm)
    # Right box (DEPT B)
    rx = MARGIN + box_w + 100
    draw.rectangle([rx, y, rx + box_w, y + box_h], outline=WALL_INK, width=5)
    text = "DEPT B"
    bbox = draw.textbbox((0, 0), text, font=f_box)
    tw = bbox[2] - bbox[0]
    draw.text((rx + (box_w - tw) // 2, y + 75), text, fill=TEXT_INK, font=f_box)
    text2 = "owns its work"
    bbox = draw.textbbox((0, 0), text2, font=f_sm)
    tw = bbox[2] - bbox[0]
    draw.text((rx + (box_w - tw) // 2, y + 120), text2, fill=TEXT_SOFT, font=f_sm)
    # Leak between boxes
    seam_cx = MARGIN + box_w + 50
    seam_cy = y + box_h // 2
    for r in [38, 35, 32]:
        draw.ellipse([seam_cx - r, seam_cy - r, seam_cx + r, seam_cy + r], fill=LEAK_BG)
    draw_dashed_circle(draw, seam_cx, seam_cy, 28, LEAK_RED, width=3, dash_count=14)
    draw.ellipse([seam_cx - 18, seam_cy - 18, seam_cx + 18, seam_cy + 18], fill=LEAK_RED)
    # Label
    f_leak_lbl = mono(11, bold=True)
    text = "LEAK"
    bbox = draw.textbbox((0, 0), text, font=f_leak_lbl)
    tw = bbox[2] - bbox[0]
    draw.text((seam_cx - tw // 2, seam_cy + 50), text, fill=LEAK_RED, font=f_leak_lbl)

    # Caption
    f_cap = work(20)
    cap = ("Every leak in your business lives in the seam between two "
           "departments that each think the other owns the fix.")
    draw_wrapped(draw, MARGIN, 880, cap, f_cap, W - MARGIN * 2, 30, color=TEXT_INK)

    draw_footer(draw, 2)
    return img


# ────────────────────────────────────────────────────────────────────
# SLIDE 3 — HERO FLOOR PLAN (all leaks)
# ────────────────────────────────────────────────────────────────────
def slide_3():
    img = make_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "SHEET 03 / PLAN VIEW")

    # Title
    f_eyebrow = mono(13, bold=True)
    draw.text((MARGIN, 120), "OFFICE FLOOR PLAN  /  OPERATIONAL", fill=DRAFT_BLUE, font=f_eyebrow)
    f_title = plex_serif(36, bold=True)
    draw.text((MARGIN, 150), "5 leak points marked at the seams.", fill=TEXT_INK, font=f_title)

    # Compass rose — outside plan, top-right of title row (safely separated)
    draw_compass_rose(draw, W - 90, 145, size=24)

    # Floor plan (smaller to leave room for leak index)
    plan_x0, plan_y0 = 110, 230
    plan_w, plan_h = 860, 600
    draw_floor_plan(img, draw, plan_x0, plan_y0, plan_w, plan_h, highlight_leak=None)

    # Scale bar under plan, left
    draw_scale_bar(draw, plan_x0, plan_y0 + plan_h + 22)

    # LEAK INDEX table under the plan
    table_y = plan_y0 + plan_h + 80
    draw.line([(MARGIN, table_y - 6), (W - MARGIN, table_y - 6)], fill=WALL_INK, width=2)
    f_th = mono(12, bold=True)
    draw.text((MARGIN, table_y + 4), "#", fill=DRAFT_BLUE, font=f_th)
    draw.text((MARGIN + 60, table_y + 4), "CATEGORY", fill=DRAFT_BLUE, font=f_th)
    draw.text((W - MARGIN - 180, table_y + 4), "EST. LEAK / YR", fill=DRAFT_BLUE, font=f_th)
    draw.line([(MARGIN, table_y + 28), (W - MARGIN, table_y + 28)], fill=WALL_INK, width=1)

    # Rows
    row_h = 32
    f_no = mono(13, bold=True)
    f_cat = work(15, bold=True)
    f_dollar = mono(15, bold=True)
    for i, (num, dollar, cat, _) in enumerate(LEAKS):
        ry = table_y + 38 + i * row_h
        draw.text((MARGIN, ry), num, fill=LEAK_RED, font=f_no)
        draw.text((MARGIN + 60, ry), cat, fill=TEXT_INK, font=f_cat)
        bbox = draw.textbbox((0, 0), dollar, font=f_dollar)
        dw = bbox[2] - bbox[0]
        draw.text((W - MARGIN - dw, ry), dollar, fill=TEXT_INK, font=f_dollar)

    # Total row
    tot_y = table_y + 38 + 5 * row_h
    draw.line([(MARGIN, tot_y), (W - MARGIN, tot_y)], fill=WALL_INK, width=1)
    f_tot = mono(14, bold=True)
    draw.text((MARGIN + 60, tot_y + 8), "TOTAL ANNUAL LEAK", fill=TEXT_INK, font=f_tot)
    tot_text = "$1.2-1.8M"
    bbox = draw.textbbox((0, 0), tot_text, font=f_tot)
    tw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - tw, tot_y + 8), tot_text, fill=LEAK_RED, font=f_tot)

    draw_footer(draw, 3)
    return img


# ────────────────────────────────────────────────────────────────────
# SLIDES 4-8 — FOCUSED LEAK SLIDES
# ────────────────────────────────────────────────────────────────────
def make_leak_slide(slide_num, leak_idx, body_text):
    img = make_canvas()
    draw = ImageDraw.Draw(img)
    leak = LEAKS[leak_idx]
    num, dollar, category, _ = leak
    draw_masthead(draw, f"SHEET {slide_num:02d} / LEAK {num}")

    # Eyebrow
    f_eyebrow = mono(13, bold=True)
    draw.text((MARGIN, 120), f"LEAK {num}  /  {category}", fill=LEAK_RED, font=f_eyebrow)
    # Amount
    f_amount = plex_serif(56, bold=True)
    draw.text((MARGIN, 152), dollar, fill=TEXT_INK, font=f_amount)
    f_per = work(15)
    draw.text((MARGIN, 222), "per year. on a 10M revenue company.", fill=TEXT_SOFT, font=f_per)

    # Floor plan (smaller)
    plan_x0, plan_y0 = 110, 280
    plan_w, plan_h = 860, 500
    draw_floor_plan(img, draw, plan_x0, plan_y0, plan_w, plan_h,
                    highlight_leak=leak_idx, show_furniture=True)

    # Mechanism body
    body_y = 830
    draw.line([(MARGIN, body_y - 10), (W - MARGIN, body_y - 10)], fill=WALL_INK, width=1)
    f_lbl = mono(13, bold=True)
    draw.text((MARGIN, body_y), "THE MECHANISM —", fill=LEAK_RED, font=f_lbl)
    f_body = work(20)
    draw_wrapped(draw, MARGIN, body_y + 30, body_text, f_body, W - MARGIN * 2, 30, color=TEXT_INK)

    # Mini index at bottom showing which leak is being focused
    legend_y = H - 130
    f_leg = mono(11)
    draw.text((MARGIN, legend_y), "INDEX:", fill=TEXT_SOFT, font=f_leg)
    spacing = (W - MARGIN * 2 - 80) // 5
    for i, lk in enumerate(LEAKS):
        x = MARGIN + 80 + i * spacing
        color = LEAK_RED if i == leak_idx else LEAK_RED_DIM
        # mini dot
        draw.ellipse([x, legend_y, x + 14, legend_y + 14], fill=color)
        draw.text((x + 22, legend_y), lk[0], fill=color, font=f_leg)

    draw_footer(draw, slide_num)
    return img


def slide_4():
    return make_leak_slide(
        4, 0,
        "CFO sees acquisition cost in one P&L and churn in another. Never runs them together. The actual cost per kept customer is 2-3x the reported number.",
    )

def slide_5():
    return make_leak_slide(
        5, 1,
        "Price set 3 years ago based on competitors. Buyers paying without negotiation = the floor moved up. Each closed deal at the old price is a transfer from your company to the buyer.",
    )

def slide_6():
    return make_leak_slide(
        6, 2,
        "Authorization queues stack up on the founder's desk. Work behind them stalls. Each day of stall has a dollar cost. Paused work IS the leak.",
    )

def slide_7():
    return make_leak_slide(
        7, 3,
        "Marketing has a CRM. Sales has another. CS uses a third. Data does not sync. Licenses overlap. Nobody owns consolidation because each department defends its own tool.",
    )

def slide_8():
    return make_leak_slide(
        8, 4,
        "Sales hands customer to onboarding without context. Onboarding hands the relationship to CS without contract terms. Every handoff is a chance for the customer to feel like they are starting over.",
    )


# ────────────────────────────────────────────────────────────────────
# SLIDE 9 — TOTAL + QUESTION CLOSE
# ────────────────────────────────────────────────────────────────────
def slide_9():
    img = make_canvas()
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, "SHEET 09 / TOTAL")

    f_eyebrow = mono(13, bold=True)
    draw.text((MARGIN, 145), "AGGREGATE / 10M REVENUE COMPANY", fill=DRAFT_BLUE, font=f_eyebrow)

    # Massive total
    f_total = plex_serif(190, bold=True)
    draw.text((MARGIN, 190), "$1.2-1.8M", fill=LEAK_RED, font=f_total)
    f_per = work(24)
    draw.text((MARGIN, 405), "walking out the door inside a year.", fill=TEXT_INK, font=f_per)
    draw.text((MARGIN, 439), "nobody is fighting for it.", fill=TEXT_SOFT, font=f_per)

    fix_y = 560
    draw.line([(MARGIN, fix_y), (W - MARGIN, fix_y)], fill=WALL_INK, width=2)
    f_fix_lbl = mono(13, bold=True)
    draw.text((MARGIN, fix_y + 20), "THE FIX —", fill=DRAFT_BLUE, font=f_fix_lbl)
    f_fix = plex_serif(30, bold=True)
    draw.text((MARGIN, fix_y + 50), "Don't fix symptoms.", fill=TEXT_INK, font=f_fix)
    draw.text((MARGIN, fix_y + 92), "Fix the seams.", fill=LEAK_RED, font=f_fix)
    f_fix_sub = work(19)
    draw.text((MARGIN, fix_y + 152), "Name an owner for each category. Give them authority", fill=TEXT_SOFT, font=f_fix_sub)
    draw.text((MARGIN, fix_y + 178), "to redesign the handoff.", fill=TEXT_SOFT, font=f_fix_sub)

    q_y = 880
    draw.line([(MARGIN, q_y), (W - MARGIN, q_y)], fill=LEAK_RED, width=2)
    f_q_lbl = mono(13, bold=True)
    draw.text((MARGIN, q_y + 20), "FOR THE OPERATOR —", fill=LEAK_RED, font=f_q_lbl)
    f_q = plex_serif(30, bold=True)
    q_text = "What is the dollar value of one seam between two departments in your company right now that nobody owns?"
    draw_wrapped(draw, MARGIN, q_y + 56, q_text, f_q, W - MARGIN * 2, 42, color=TEXT_INK)

    draw_footer(draw, 9)
    return img


# ────────────────────────────────────────────────────────────────────
# BUILD
# ────────────────────────────────────────────────────────────────────
def main():
    slides = [
        ("slide_01_cover", slide_1()),
        ("slide_02_finding", slide_2()),
        ("slide_03_hero_plan", slide_3()),
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
