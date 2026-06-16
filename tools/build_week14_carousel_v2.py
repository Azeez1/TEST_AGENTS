"""Week 14 carousel v2 — Office Floor Plan / Architectural Blueprint aesthetic.
9 slides at 1080x1350 portrait. Where Your Margin Lives.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import img2pdf
import math

OUT_DIR = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\social_media")
TMP_DIR = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_clips\week14_slides_v2")
TMP_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1350
MARGIN = 60

# Architectural CAD palette — clean, modern, drafting precise
WARM_WHITE   = (250, 248, 244)   # architectural vellum
GRID_FAINT   = (228, 228, 234)   # very faint blueprint grid
WALL_INK     = (22, 22, 28)      # thick wall lines
LINE_MID     = (140, 142, 152)   # interior/furniture lines
LINE_FADED   = (185, 188, 196)   # dimensioning lines
TEXT_INK     = (32, 32, 38)      # text ink
TEXT_SOFT    = (110, 112, 124)   # secondary text
DRAFT_BLUE   = (38, 78, 138)     # blueprint accent blue
LEAK_RED     = (212, 50, 40)     # alert red for leak markers
LEAK_RED_DIM = (210, 165, 160)   # dimmed/inactive leak
LEAK_BG      = (252, 232, 228)   # leak halo/glow background

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
def tektur(size):
    return font("Tektur-Medium.ttf", size)
def national(size, bold=False):
    return font("NationalPark-Bold.ttf" if bold else "NationalPark-Regular.ttf", size)


def make_blueprint_canvas():
    """Warm white with very faint blueprint grid."""
    img = Image.new("RGB", (W, H), WARM_WHITE)
    draw = ImageDraw.Draw(img)
    # Faint grid — every 30px
    for x in range(0, W, 30):
        draw.line([(x, 0), (x, H)], fill=GRID_FAINT, width=1)
    for y in range(0, H, 30):
        draw.line([(0, y), (W, y)], fill=GRID_FAINT, width=1)
    return img


def draw_dashed_line(draw, x1, y1, x2, y2, fill, width=1, dash=8, gap=5):
    """Draw a dashed line between two points."""
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


def draw_arch_masthead(draw, sheet_label):
    """Top architectural drawing title strip."""
    # Top thin rule
    draw.line([(MARGIN, 55), (W - MARGIN, 55)], fill=WALL_INK, width=2)
    # Title
    f_title = mono(13, bold=True)
    draw.text((MARGIN, 70), "PROJECT: MARGIN RECOVERY  /  CLIENT: THE OPERATOR  /  ISSUE 014",
              fill=TEXT_INK, font=f_title)
    # Sheet label right
    bbox = draw.textbbox((0, 0), sheet_label, font=f_title)
    tw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - tw, 70), sheet_label, fill=TEXT_INK, font=f_title)
    # Lower thin rule
    draw.line([(MARGIN, 95), (W - MARGIN, 95)], fill=WALL_INK, width=1)


def draw_arch_footer(draw, sheet_num, total=9):
    """Bottom title block — architectural standard."""
    # Frame
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


def draw_compass_rose(draw, cx, cy, size=40):
    """Architectural compass rose — north arrow."""
    # Outer circle
    draw.ellipse([cx - size, cy - size, cx + size, cy + size], outline=WALL_INK, width=2)
    # North arrow (filled triangle)
    n_pts = [(cx, cy - size + 4), (cx - size * 0.25, cy), (cx + size * 0.25, cy)]
    draw.polygon(n_pts, fill=WALL_INK)
    # South arrow (outline)
    s_pts = [(cx, cy + size - 4), (cx - size * 0.25, cy), (cx + size * 0.25, cy)]
    draw.polygon(s_pts, outline=WALL_INK, width=2)
    # "N" label
    f = mono(11, bold=True)
    bbox = draw.textbbox((0, 0), "N", font=f)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, cy - size - 22), "N", fill=WALL_INK, font=f)


def draw_scale_bar(draw, x, y):
    """Architectural scale bar."""
    # Bar segments alternating black/white
    seg_w = 24
    for i in range(4):
        fill = WALL_INK if i % 2 == 0 else WARM_WHITE
        draw.rectangle([x + i * seg_w, y, x + (i + 1) * seg_w, y + 8],
                       outline=WALL_INK, fill=fill, width=1)
    # Labels
    f = mono(10, bold=True)
    for i, label in enumerate(["0", "10", "20", "30", "40"]):
        draw.text((x + i * seg_w - 4, y + 12), label, fill=TEXT_INK, font=f)
    draw.text((x, y - 18), "SCALE BAR (FT)", fill=TEXT_SOFT, font=f)


def draw_furniture_desks(draw, x0, y0, x1, y1, count_x=2, count_y=2):
    """Draw simple desk rectangles inside a room."""
    rw = (x1 - x0)
    rh = (y1 - y0)
    pad = 30
    avail_w = rw - pad * 2
    avail_h = rh - pad * 2
    cell_w = avail_w // count_x
    cell_h = avail_h // count_y
    desk_w = int(cell_w * 0.55)
    desk_h = int(cell_h * 0.32)
    for i in range(count_x):
        for j in range(count_y):
            dx = x0 + pad + i * cell_w + (cell_w - desk_w) // 2
            dy = y0 + pad + j * cell_h + (cell_h - desk_h) // 2
            draw.rectangle([dx, dy, dx + desk_w, dy + desk_h],
                           outline=LINE_MID, width=1)


def draw_room(draw, x0, y0, x1, y1, label, sublabel=None, desk_pattern=(2, 2),
              door_side="bottom", door_pos=0.5, label_pos="top-left"):
    """Draw a room: thick wall outline + door opening + label + light furniture."""
    # Walls (thick) — draw 4 sides, leaving a gap for the door
    wall_w = 5
    door_w = 28
    # Top wall
    draw.line([(x0, y0), (x1, y0)], fill=WALL_INK, width=wall_w)
    # Bottom wall
    if door_side == "bottom":
        gap_x = x0 + (x1 - x0) * door_pos
        draw.line([(x0, y1), (gap_x - door_w // 2, y1)], fill=WALL_INK, width=wall_w)
        draw.line([(gap_x + door_w // 2, y1), (x1, y1)], fill=WALL_INK, width=wall_w)
    else:
        draw.line([(x0, y1), (x1, y1)], fill=WALL_INK, width=wall_w)
    # Left wall
    if door_side == "left":
        gap_y = y0 + (y1 - y0) * door_pos
        draw.line([(x0, y0), (x0, gap_y - door_w // 2)], fill=WALL_INK, width=wall_w)
        draw.line([(x0, gap_y + door_w // 2), (x0, y1)], fill=WALL_INK, width=wall_w)
    else:
        draw.line([(x0, y0), (x0, y1)], fill=WALL_INK, width=wall_w)
    # Right wall
    if door_side == "right":
        gap_y = y0 + (y1 - y0) * door_pos
        draw.line([(x1, y0), (x1, gap_y - door_w // 2)], fill=WALL_INK, width=wall_w)
        draw.line([(x1, gap_y + door_w // 2), (x1, y1)], fill=WALL_INK, width=wall_w)
    else:
        draw.line([(x1, y0), (x1, y1)], fill=WALL_INK, width=wall_w)
    # Room label
    f_label = big_shoulders(22)
    f_sub = mono(11)
    if label_pos == "top-left":
        draw.text((x0 + 12, y0 + 10), label, fill=TEXT_INK, font=f_label)
        if sublabel:
            draw.text((x0 + 12, y0 + 38), sublabel, fill=TEXT_SOFT, font=f_sub)
    # Furniture
    if desk_pattern:
        draw_furniture_desks(draw, x0, y0, x1, y1, *desk_pattern)


def draw_leak_marker(draw, cx, cy, leak_num, dollar, label, dim=False):
    """Red leak marker at a seam: dashed circle + $ symbol + label box."""
    color = LEAK_RED_DIM if dim else LEAK_RED
    glow = LEAK_BG if not dim else None
    # Soft glow background
    if glow:
        for r in range(34, 22, -2):
            alpha_layer = Image.new("RGBA", (r * 4, r * 4), (0, 0, 0, 0))
            ad = ImageDraw.Draw(alpha_layer)
            opa = max(0, 30 - (34 - r) * 3)
            ad.ellipse([0, 0, r * 2, r * 2], fill=glow + (opa,))
            # We just blot directly with low alpha by drawing solid circles into a buffer
            # Simpler: draw a few light circles
        # Simple approach: solid lighter ellipse behind
        draw.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=glow)
    # Outer dashed circle
    draw_dashed_circle(draw, cx, cy, 26, color, width=2, dash_count=12)
    # Inner solid circle
    draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], outline=color, width=2)
    # Leak number inside
    f_num = mono(13, bold=True)
    bbox = draw.textbbox((0, 0), leak_num, font=f_num)
    nw = bbox[2] - bbox[0]
    nh = bbox[3] - bbox[1]
    draw.text((cx - nw // 2, cy - nh // 2 - 4), leak_num, fill=color, font=f_num)


def draw_dashed_circle(draw, cx, cy, r, color, width=2, dash_count=12):
    """Draw a dashed circle outline."""
    arc_each = 360 / dash_count
    arc_on = arc_each * 0.55
    for i in range(dash_count):
        start = i * arc_each
        end = start + arc_on
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=start, end=end, fill=color, width=width)


def draw_leak_callout(draw, x, y, leak_num, dollar, label, color=LEAK_RED):
    """A small data callout box next to a leak."""
    # Bracket / line
    draw.line([(x, y), (x + 30, y)], fill=color, width=2)
    f_num = mono(11, bold=True)
    f_dollar = work(20, bold=True)
    f_label = mono(11)
    draw.text((x + 38, y - 16), f"LEAK {leak_num}", fill=color, font=f_num)
    draw.text((x + 38, y - 2), dollar, fill=TEXT_INK, font=f_dollar)
    draw.text((x + 38, y + 26), label, fill=TEXT_SOFT, font=f_label)


# Floor plan layout for the hero slides
PLAN_X0, PLAN_Y0 = 110, 280
PLAN_W, PLAN_H = 860, 720
ROOM_W = PLAN_W // 3
ROOM_H = PLAN_H // 2

ROOMS = [
    # (col, row, label, sublabel)
    (0, 0, "MARKETING",       "lead gen / brand"),
    (1, 0, "SALES",           "pipeline / close"),
    (2, 0, "OPERATIONS",      "delivery / tools"),
    (0, 1, "CUSTOMER SUCCESS","retention / expansion"),
    (1, 1, "FOUNDER'S OFFICE","decisions"),
    (2, 1, "FINANCE",         "books / P&L"),
]

LEAKS = [
    # (label, dollar, position relative to room grid, room category)
    ("01", "$200-400K", "CAC LEAK", (0, 0.5, 1)),    # between MKTG col0 row0 and CS col0 row1
    ("02", "$300-500K", "PRICING POSITION", (2.0, 0.5, 1)),  # right edge col2 between SALES and FINANCE
    ("03", "$100-300K", "DECISION LATENCY", (1.5, 1.0, 0)),  # inside founder's office area
    ("04", "$200-300K", "DUPLICATE SYSTEMS", (1.0, 0.5, 1)),  # between SALES and FNDR
    ("05", "$300-400K", "HANDOFF FIDELITY", (0.5, 1.0, 0)),  # between MKTG and SALES top row
]


def get_leak_position(layout_xy):
    """Convert a (col, row, kind) tuple to absolute pixel coordinates on the floor plan."""
    col, row, kind = layout_xy
    # col, row are positions in the 3x2 grid (can be fractional for seams)
    x = PLAN_X0 + col * ROOM_W
    y = PLAN_Y0 + row * ROOM_H
    return int(x), int(y)


def draw_floor_plan(img, draw, highlight_leak=None):
    """Draw the 6-room floor plan with leak markers. If highlight_leak is set, dim others."""
    # Faint blueprint background — slight blue tint inside the floor plan bounds
    draw.rectangle([(PLAN_X0, PLAN_Y0), (PLAN_X0 + PLAN_W, PLAN_Y0 + PLAN_H)],
                   fill=(244, 246, 250))
    # Draw rooms
    for col, row, label, sublabel in ROOMS:
        x0 = PLAN_X0 + col * ROOM_W
        y0 = PLAN_Y0 + row * ROOM_H
        x1 = x0 + ROOM_W
        y1 = y0 + ROOM_H
        door_side = "bottom" if row == 0 else "top" if row == 1 else "right"
        draw_room(draw, x0, y0, x1, y1, label, sublabel, desk_pattern=(2, 2))
    # Draw leak markers
    for i, (num, dollar, lbl, pos) in enumerate(LEAKS):
        cx, cy = get_leak_position(pos)
        dim = highlight_leak is not None and highlight_leak != i
        draw_leak_marker(draw, cx, cy, num, dollar, lbl, dim=dim)


# ────────────────────────────────────────────────────────────────────
# SLIDE 1 — COVER
# ────────────────────────────────────────────────────────────────────
def slide_1():
    img = make_blueprint_canvas()
    draw = ImageDraw.Draw(img)
    draw_arch_masthead(draw, "SHEET 01 / COVER")

    # Big serif title
    f_eyebrow = mono(14, bold=True)
    draw.text((MARGIN, 160), "FLOOR PLAN —", fill=DRAFT_BLUE, font=f_eyebrow)
    f_title = plex_serif(82, bold=True)
    draw.text((MARGIN, 195), "Where your", fill=TEXT_INK, font=f_title)
    draw.text((MARGIN, 285), "margin", fill=TEXT_INK, font=f_title)
    draw.text((MARGIN, 375), "actually", fill=TEXT_INK, font=f_title)
    draw.text((MARGIN, 465), "lives.", fill=LEAK_RED, font=f_title)

    # Subtitle
    f_sub = work(22)
    draw.text((MARGIN, 590), "5 leaks. 6 rooms. Most operators are losing", fill=TEXT_SOFT, font=f_sub)
    draw.text((MARGIN, 622), "12-18% of revenue through the seams between them.", fill=TEXT_SOFT, font=f_sub)

    # Mini schematic preview — small 3x2 grid of rooms with leak dots
    mini_x0, mini_y0 = MARGIN, 720
    mini_w, mini_h = W - 2 * MARGIN, 320
    mini_room_w = mini_w // 3
    mini_room_h = mini_h // 2
    # Background tint
    draw.rectangle([(mini_x0, mini_y0), (mini_x0 + mini_w, mini_y0 + mini_h)], fill=(244, 246, 250))
    for c in range(3):
        for r in range(2):
            rx0 = mini_x0 + c * mini_room_w
            ry0 = mini_y0 + r * mini_room_h
            rx1 = rx0 + mini_room_w
            ry1 = ry0 + mini_room_h
            draw.rectangle([rx0 + 4, ry0 + 4, rx1 - 4, ry1 - 4], outline=WALL_INK, width=4)
    # Mini leak markers at the seams
    for c in [0.5, 1.5, 2.5]:
        cx = mini_x0 + int(c * mini_room_w)
        cy = mini_y0 + mini_room_h
        draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=LEAK_RED, outline=WARM_WHITE, width=2)
    for r in [1.0]:
        for c in [1.0, 2.0]:
            cx = mini_x0 + int(c * mini_room_w)
            cy = mini_y0 + int(r * mini_room_h)
            draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=LEAK_RED, outline=WARM_WHITE, width=2)

    # Compass + scale bar
    draw_compass_rose(draw, W - 110, 175, size=32)

    # Title block bottom-right area (architectural standard)
    f_block = mono(11, bold=True)
    block_x = MARGIN
    block_y = 1080
    draw.text((block_x, block_y), "DRAWING:    OFFICE FLOOR PLAN, OPERATIONAL", fill=TEXT_INK, font=f_block)
    draw.text((block_x, block_y + 20), "SUBJECT:    THE 5 SEAMS", fill=TEXT_INK, font=f_block)
    draw.text((block_x, block_y + 40), "AUTHORITY:  OPERATOR'S DESK / DUX MACHINA", fill=TEXT_INK, font=f_block)
    draw.text((block_x, block_y + 60), "DRAWING NO: DM-014-MON-01", fill=TEXT_INK, font=f_block)

    draw_arch_footer(draw, 1)
    return img


# ────────────────────────────────────────────────────────────────────
# SLIDE 2 — THE PIERCE
# ────────────────────────────────────────────────────────────────────
def slide_2():
    img = make_blueprint_canvas()
    draw = ImageDraw.Draw(img)
    draw_arch_masthead(draw, "SHEET 02 / FINDING")

    # Eyebrow
    f_eyebrow = mono(13, bold=True)
    draw.text((MARGIN, 160), "FINDING —", fill=DRAFT_BLUE, font=f_eyebrow)

    # Pierce
    f_lead = plex_serif(58, bold=True)
    y = 210
    pierce = [
        "The waste",
        "is not theft.",
        "It is structural.",
    ]
    for line in pierce:
        color = LEAK_RED if "structural" in line else TEXT_INK
        draw.text((MARGIN, y), line, fill=color, font=f_lead)
        y += 76

    # Two-column diagram concept
    y = 580
    # Two boxes side by side representing departments
    box_w = (W - MARGIN * 2 - 80) // 2
    box_h = 180
    # Left box
    draw.rectangle([MARGIN, y, MARGIN + box_w, y + box_h], outline=WALL_INK, width=4)
    f_box_lbl = big_shoulders(24)
    text = "DEPT A"
    bbox = draw.textbbox((0, 0), text, font=f_box_lbl)
    tw = bbox[2] - bbox[0]
    draw.text((MARGIN + (box_w - tw) // 2, y + 70), text, fill=TEXT_INK, font=f_box_lbl)
    f_box_sub = mono(13)
    text2 = "owns its work"
    bbox = draw.textbbox((0, 0), text2, font=f_box_sub)
    tw = bbox[2] - bbox[0]
    draw.text((MARGIN + (box_w - tw) // 2, y + 105), text2, fill=TEXT_SOFT, font=f_box_sub)
    # Right box
    rx = MARGIN + box_w + 80
    draw.rectangle([rx, y, rx + box_w, y + box_h], outline=WALL_INK, width=4)
    text = "DEPT B"
    bbox = draw.textbbox((0, 0), text, font=f_box_lbl)
    tw = bbox[2] - bbox[0]
    draw.text((rx + (box_w - tw) // 2, y + 70), text, fill=TEXT_INK, font=f_box_lbl)
    text2 = "owns its work"
    bbox = draw.textbbox((0, 0), text2, font=f_box_sub)
    tw = bbox[2] - bbox[0]
    draw.text((rx + (box_w - tw) // 2, y + 105), text2, fill=TEXT_SOFT, font=f_box_sub)
    # Leak indicator BETWEEN them
    seam_cx = MARGIN + box_w + 40
    seam_cy = y + box_h // 2
    draw_dashed_circle(draw, seam_cx, seam_cy, 36, LEAK_RED, width=3, dash_count=14)
    draw.ellipse([seam_cx - 18, seam_cy - 18, seam_cx + 18, seam_cy + 18], fill=LEAK_RED)
    f_leak_lbl = mono(11, bold=True)
    draw.text((seam_cx - 50, seam_cy + 60), "THE LEAK LIVES HERE", fill=LEAK_RED, font=f_leak_lbl)

    # Caption below
    f_cap = work(20)
    cap = "Every leak in your business lives in the seam between two departments that each think the other owns the fix."
    lines = []
    words = cap.split()
    cur = []
    max_w = W - MARGIN * 2
    for w in words:
        test = " ".join(cur + [w])
        bbox = draw.textbbox((0, 0), test, font=f_cap)
        if bbox[2] - bbox[0] <= max_w:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur: lines.append(" ".join(cur))
    cy = 1100
    for line in lines:
        draw.text((MARGIN, cy), line, fill=TEXT_INK, font=f_cap)
        cy += 30

    draw_arch_footer(draw, 2)
    return img


# ────────────────────────────────────────────────────────────────────
# SLIDE 3 — HERO FLOOR PLAN (all leaks visible)
# ────────────────────────────────────────────────────────────────────
def slide_3():
    img = make_blueprint_canvas()
    draw = ImageDraw.Draw(img)
    draw_arch_masthead(draw, "SHEET 03 / PLAN VIEW")

    # Title above plan
    f_eyebrow = mono(13, bold=True)
    draw.text((MARGIN, 130), "OFFICE FLOOR PLAN  /  OPERATIONAL", fill=DRAFT_BLUE, font=f_eyebrow)
    f_title = plex_serif(40, bold=True)
    draw.text((MARGIN, 160), "5 leak points marked at the seams.", fill=TEXT_INK, font=f_title)

    # Draw the floor plan
    draw_floor_plan(img, draw, highlight_leak=None)
    draw = ImageDraw.Draw(img)

    # Compass rose top right of plan
    draw_compass_rose(draw, PLAN_X0 + PLAN_W - 40, PLAN_Y0 + 40, size=22)

    # Scale bar bottom-left of plan
    draw_scale_bar(draw, PLAN_X0, PLAN_Y0 + PLAN_H + 18)

    # Legend bottom-right
    legend_x = PLAN_X0 + PLAN_W - 280
    legend_y = PLAN_Y0 + PLAN_H + 24
    f_leg_t = mono(12, bold=True)
    draw.text((legend_x, legend_y), "LEGEND", fill=TEXT_INK, font=f_leg_t)
    draw.line([(legend_x, legend_y + 18), (legend_x + 200, legend_y + 18)], fill=WALL_INK, width=1)
    f_leg = mono(10)
    # Leak marker example
    draw.ellipse([legend_x, legend_y + 28, legend_x + 16, legend_y + 44], outline=LEAK_RED, width=2)
    draw.text((legend_x + 22, legend_y + 30), "MARGIN LEAK POINT", fill=TEXT_INK, font=f_leg)
    # Wall example
    draw.line([(legend_x, legend_y + 54), (legend_x + 16, legend_y + 54)], fill=WALL_INK, width=5)
    draw.text((legend_x + 22, legend_y + 48), "DEPT. WALL (OWNED)", fill=TEXT_INK, font=f_leg)

    draw_arch_footer(draw, 3)
    return img


# ────────────────────────────────────────────────────────────────────
# SLIDES 4-8 — Focused leak slides
# ────────────────────────────────────────────────────────────────────
def make_leak_slide(slide_num, leak_idx, body_text, dollar, category):
    img = make_blueprint_canvas()
    draw = ImageDraw.Draw(img)
    draw_arch_masthead(draw, f"SHEET {slide_num:02d} / LEAK {leak_idx+1:02d}")

    # Eyebrow + title
    f_eyebrow = mono(13, bold=True)
    draw.text((MARGIN, 130), f"LEAK {leak_idx+1:02d}  /  {category}", fill=LEAK_RED, font=f_eyebrow)
    f_amount = plex_serif(56, bold=True)
    draw.text((MARGIN, 160), dollar, fill=TEXT_INK, font=f_amount)
    f_per = work(15)
    draw.text((MARGIN, 232), "per year. on a 10M revenue company.", fill=TEXT_SOFT, font=f_per)

    # Mini floor plan in middle (smaller than hero)
    global PLAN_X0, PLAN_Y0, PLAN_W, PLAN_H, ROOM_W, ROOM_H
    saved = (PLAN_X0, PLAN_Y0, PLAN_W, PLAN_H, ROOM_W, ROOM_H)
    PLAN_X0, PLAN_Y0 = 110, 290
    PLAN_W, PLAN_H = 860, 520
    ROOM_W = PLAN_W // 3
    ROOM_H = PLAN_H // 2
    draw_floor_plan(img, draw, highlight_leak=leak_idx)
    draw = ImageDraw.Draw(img)
    PLAN_X0, PLAN_Y0, PLAN_W, PLAN_H, ROOM_W, ROOM_H = saved

    # The mechanism
    body_y = 860
    f_mech_lbl = mono(13, bold=True)
    draw.text((MARGIN, body_y), "THE MECHANISM —", fill=LEAK_RED, font=f_mech_lbl)
    f_body = work(20)
    # Wrap body
    lines = []
    words = body_text.split()
    cur = []
    max_w = W - MARGIN * 2
    for w in words:
        test = " ".join(cur + [w])
        bbox = draw.textbbox((0, 0), test, font=f_body)
        if bbox[2] - bbox[0] <= max_w:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur: lines.append(" ".join(cur))
    cy = body_y + 28
    for line in lines:
        draw.text((MARGIN, cy), line, fill=TEXT_INK, font=f_body)
        cy += 30

    draw_arch_footer(draw, slide_num)
    return img


def slide_4():
    return make_leak_slide(
        4, 0,
        "CFO sees acquisition cost in one P&L and churn in another. Never runs them together. The actual cost per kept customer is 2-3x the reported number.",
        "$200-400K",
        "CUSTOMER ACQUISITION LEAK",
    )


def slide_5():
    return make_leak_slide(
        5, 1,
        "Price set 3 years ago based on competitors. Buyers paying without negotiation = the floor moved up. Each closed deal at the old price is a transfer from your company to the buyer.",
        "$300-500K",
        "PRICING POSITION LEAK",
    )


def slide_6():
    return make_leak_slide(
        6, 2,
        "Authorization queues stack up on the founder's desk. Work behind them stalls. Each day of stall has a dollar cost. Paused work IS the leak.",
        "$100-300K",
        "DECISION LATENCY LEAK",
    )


def slide_7():
    return make_leak_slide(
        7, 3,
        "Marketing has a CRM. Sales has another. Customer success uses a third. Data does not sync. Licenses overlap. Nobody owns the consolidation.",
        "$200-300K",
        "DUPLICATE SYSTEMS LEAK",
    )


def slide_8():
    return make_leak_slide(
        8, 4,
        "Sales hands customer to onboarding without context. Onboarding hands the relationship to CS without contract terms. Every handoff is a chance for the customer to feel like they are starting over.",
        "$300-400K",
        "HANDOFF FIDELITY LEAK",
    )


# ────────────────────────────────────────────────────────────────────
# SLIDE 9 — TOTAL + QUESTION CLOSE
# ────────────────────────────────────────────────────────────────────
def slide_9():
    img = make_blueprint_canvas()
    draw = ImageDraw.Draw(img)
    draw_arch_masthead(draw, "SHEET 09 / TOTAL")

    # Eyebrow
    f_eyebrow = mono(13, bold=True)
    draw.text((MARGIN, 150), "AGGREGATE / 10M REVENUE COMPANY", fill=DRAFT_BLUE, font=f_eyebrow)

    # MASSIVE total number
    f_total = plex_serif(190, bold=True)
    draw.text((MARGIN, 195), "$1.2-1.8M", fill=LEAK_RED, font=f_total)
    f_per = work(24)
    draw.text((MARGIN, 410), "walking out the door inside a year.", fill=TEXT_INK, font=f_per)
    draw.text((MARGIN, 444), "nobody is fighting for it.", fill=TEXT_SOFT, font=f_per)

    # The fix
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

    # Question close
    q_y = 880
    draw.line([(MARGIN, q_y), (W - MARGIN, q_y)], fill=LEAK_RED, width=2)
    f_q_lbl = mono(13, bold=True)
    draw.text((MARGIN, q_y + 20), "FOR THE OPERATOR —", fill=LEAK_RED, font=f_q_lbl)
    f_q = plex_serif(30, bold=True)
    # Wrap question
    q_text = "What is the dollar value of one seam between two departments in your company right now that nobody owns?"
    words = q_text.split()
    cur = []
    lines = []
    for w in words:
        test = " ".join(cur + [w])
        bbox = draw.textbbox((0, 0), test, font=f_q)
        if bbox[2] - bbox[0] <= W - MARGIN * 2:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur: lines.append(" ".join(cur))
    cy = q_y + 56
    for line in lines:
        draw.text((MARGIN, cy), line, fill=TEXT_INK, font=f_q)
        cy += 42

    draw_arch_footer(draw, 9)
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
