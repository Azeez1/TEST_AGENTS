from PIL import Image, ImageDraw, ImageFont
import math
import random

# Set seed for consistent "randomness" in hand-drawn effect
random.seed(42)

# Canvas dimensions (LinkedIn/social optimized)
WIDTH = 1200
HEIGHT = 627
BACKGROUND_COLOR = (255, 251, 245)  # Warm off-white

# Create canvas
img = Image.new('RGB', (WIDTH, HEIGHT), BACKGROUND_COLOR)
draw = ImageDraw.Draw(img)

# Color palette - warm, friendly, playful
ENVELOPE_COLOR = (255, 147, 79)    # Warm orange
GPT_COLOR = (138, 109, 255)        # Playful purple
SLACK_COLOR = (77, 182, 172)       # Soft teal
ARROW_COLOR = (100, 100, 100)      # Soft gray
TEXT_COLOR = (60, 60, 60)          # Warm dark gray
TITLE_COLOR = (40, 40, 40)         # Almost black

def draw_wobbly_line(draw, start, end, color, width=4, wobble=3):
    """Draw a hand-drawn style wobbly line"""
    x1, y1 = start
    x2, y2 = end
    steps = 20
    points = []

    for i in range(steps + 1):
        t = i / steps
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t

        # Add wobble (less in the middle, more at ends for natural feel)
        wobble_factor = math.sin(t * math.pi) * wobble
        x += random.uniform(-wobble_factor, wobble_factor)
        y += random.uniform(-wobble_factor, wobble_factor)

        points.append((x, y))

    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill=color, width=width)

def draw_wobbly_circle(draw, center, radius, color, fill=True, width=4, wobble=2):
    """Draw a hand-drawn style circle"""
    x, y = center
    points = []
    segments = 36

    for i in range(segments + 1):
        angle = (i / segments) * 2 * math.pi
        wobble_r = radius + random.uniform(-wobble, wobble)
        px = x + wobble_r * math.cos(angle)
        py = y + wobble_r * math.sin(angle)
        points.append((px, py))

    if fill:
        draw.polygon(points, fill=color, outline=color)
    else:
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=color, width=width)

def draw_wobbly_rectangle(draw, bbox, color, fill=True, width=4, wobble=3):
    """Draw a hand-drawn style rectangle"""
    x1, y1, x2, y2 = bbox

    # Create slightly wobbly corners
    corners = [
        (x1 + random.uniform(-wobble, wobble), y1 + random.uniform(-wobble, wobble)),
        (x2 + random.uniform(-wobble, wobble), y1 + random.uniform(-wobble, wobble)),
        (x2 + random.uniform(-wobble, wobble), y2 + random.uniform(-wobble, wobble)),
        (x1 + random.uniform(-wobble, wobble), y2 + random.uniform(-wobble, wobble))
    ]

    if fill:
        draw.polygon(corners, fill=color, outline=color)

    # Draw wobbly edges
    for i in range(4):
        start = corners[i]
        end = corners[(i + 1) % 4]
        draw_wobbly_line(draw, start, end, color, width)

def draw_envelope(draw, center, size, color):
    """Draw a cartoonish envelope icon"""
    x, y = center
    w, h = size, size * 0.7

    # Envelope body
    draw_wobbly_rectangle(draw,
                         (x - w/2, y - h/2, x + w/2, y + h/2),
                         color, fill=True, wobble=2)

    # Envelope flap (triangle)
    flap_points = [
        (x - w/2 + random.uniform(-2, 2), y - h/2 + random.uniform(-2, 2)),
        (x + random.uniform(-2, 2), y + h/6 + random.uniform(-2, 2)),
        (x + w/2 + random.uniform(-2, 2), y - h/2 + random.uniform(-2, 2))
    ]

    # Slightly darker flap
    darker_color = tuple(max(0, c - 30) for c in color)
    draw.polygon(flap_points, fill=darker_color, outline=darker_color)

    # Add wobbly outline
    draw_wobbly_line(draw, flap_points[0], flap_points[1], (0, 0, 0, 80), width=3)
    draw_wobbly_line(draw, flap_points[1], flap_points[2], (0, 0, 0, 80), width=3)

def draw_brain(draw, center, size, color):
    """Draw a cartoonish brain/AI icon"""
    x, y = center

    # Main brain circle
    draw_wobbly_circle(draw, center, size/2, color, fill=True, wobble=3)

    # Add "brain wrinkles" - smaller wobbly circles overlapping
    positions = [
        (x - size/4, y - size/6),
        (x + size/4, y - size/6),
        (x - size/5, y + size/6),
        (x + size/5, y + size/6),
        (x, y - size/4)
    ]

    lighter_color = tuple(min(255, c + 40) for c in color)
    for pos in positions:
        draw_wobbly_circle(draw, pos, size/6, lighter_color, fill=True, wobble=2)

    # Add sparkle lines (AI effect)
    sparkle_length = size/3
    angles = [0, math.pi/2, math.pi, 3*math.pi/2, math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]

    for angle in angles[:4]:  # Just 4 sparkles to keep it clean
        start_x = x + (size/2 + 8) * math.cos(angle)
        start_y = y + (size/2 + 8) * math.sin(angle)
        end_x = start_x + sparkle_length * math.cos(angle)
        end_y = start_y + sparkle_length * math.sin(angle)
        draw_wobbly_line(draw, (start_x, start_y), (end_x, end_y), color, width=3, wobble=2)

def draw_chat_bubble(draw, center, size, color):
    """Draw a cartoonish Slack chat bubble"""
    x, y = center
    w, h = size * 1.2, size

    # Main bubble (rounded rectangle approximation with circles)
    draw_wobbly_rectangle(draw,
                         (x - w/2, y - h/2, x + w/2, y + h/2),
                         color, fill=True, wobble=2)

    # Add rounded corners effect with circles
    corner_radius = size/6
    corners = [
        (x - w/2 + corner_radius, y - h/2 + corner_radius),
        (x + w/2 - corner_radius, y - h/2 + corner_radius),
        (x - w/2 + corner_radius, y + h/2 - corner_radius),
        (x + w/2 - corner_radius, y + h/2 - corner_radius)
    ]

    for corner in corners:
        draw_wobbly_circle(draw, corner, corner_radius, color, fill=True, wobble=1)

    # Chat bubble tail (small triangle)
    tail_points = [
        (x - w/2, y + h/3),
        (x - w/2 - size/4, y + h/2 + size/6),
        (x - w/2, y + h/2)
    ]
    draw.polygon(tail_points, fill=color, outline=color)

    # Add message lines inside
    line_color = tuple(max(0, c - 60) for c in color)
    line_y_start = y - h/4
    for i in range(3):
        line_y = line_y_start + i * (h/6)
        line_width = w/2 if i < 2 else w/3
        draw_wobbly_line(draw,
                        (x - line_width/2, line_y),
                        (x + line_width/2, line_y),
                        line_color, width=3, wobble=1)

def draw_arrow(draw, start, end, color, size=20):
    """Draw a cartoonish curved arrow"""
    x1, y1 = start
    x2, y2 = end

    # Draw curved line with control point
    control_x = (x1 + x2) / 2
    control_y = (y1 + y2) / 2 - 30  # Slight upward curve

    # Bezier-like curve with multiple segments
    steps = 20
    points = []
    for i in range(steps + 1):
        t = i / steps
        # Quadratic bezier
        px = (1-t)**2 * x1 + 2*(1-t)*t * control_x + t**2 * x2
        py = (1-t)**2 * y1 + 2*(1-t)*t * control_y + t**2 * y2
        points.append((px, py))

    # Draw curved line with wobble
    for i in range(len(points) - 1):
        draw_wobbly_line(draw, points[i], points[i + 1], color, width=5, wobble=2)

    # Arrow head
    arrow_angle = math.atan2(y2 - points[-2][1], x2 - points[-2][0])
    arrow_size = size

    arrow_points = [
        (x2, y2),
        (x2 - arrow_size * math.cos(arrow_angle - math.pi/6),
         y2 - arrow_size * math.sin(arrow_angle - math.pi/6)),
        (x2 - arrow_size * math.cos(arrow_angle + math.pi/6),
         y2 - arrow_size * math.sin(arrow_angle + math.pi/6))
    ]

    draw.polygon(arrow_points, fill=color, outline=color)

# Layout positions
icon_y = HEIGHT / 2
icon_size = 80

envelope_x = WIDTH * 0.20
gpt_x = WIDTH * 0.50
slack_x = WIDTH * 0.80

# Draw workflow elements
print("Drawing envelope...")
draw_envelope(draw, (envelope_x, icon_y), icon_size, ENVELOPE_COLOR)

print("Drawing GPT brain...")
draw_brain(draw, (gpt_x, icon_y), icon_size, GPT_COLOR)

print("Drawing Slack bubble...")
draw_chat_bubble(draw, (slack_x, icon_y), icon_size, SLACK_COLOR)

# Draw arrows
print("Drawing arrows...")
draw_arrow(draw, (envelope_x + icon_size/2 + 20, icon_y),
          (gpt_x - icon_size/2 - 20, icon_y), ARROW_COLOR, size=25)

draw_arrow(draw, (gpt_x + icon_size/2 + 20, icon_y),
          (slack_x - icon_size/2 - 30, icon_y), ARROW_COLOR, size=25)

# Load fonts - use friendly, rounded fonts
try:
    # BricolageGrotesque for title (friendly and bold)
    title_font = ImageFont.truetype("c:\\Users\\sabaa\\OneDrive\\Desktop\\TEST_AGENTS\\.claude\\skills\\canvas-design\\canvas-fonts\\BricolageGrotesque-Bold.ttf", 52)
    # WorkSans for labels (clean and approachable)
    label_font = ImageFont.truetype("c:\\Users\\sabaa\\OneDrive\\Desktop\\TEST_AGENTS\\.claude\\skills\\canvas-design\\canvas-fonts\\WorkSans-Bold.ttf", 24)
    print("Loaded custom fonts successfully!")
except Exception as e:
    print(f"Custom fonts not found: {e}, using default...")
    title_font = ImageFont.load_default()
    label_font = ImageFont.load_default()

# Add title at top
title_text = "Example: AI Email Summary Workflow"
print("Adding title...")

# Get text bounding box
bbox = draw.textbbox((0, 0), title_text, font=title_font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

title_x = (WIDTH - text_width) / 2
title_y = 60

draw.text((title_x, title_y), title_text, fill=TITLE_COLOR, font=title_font)

# Add labels below each icon
print("Adding labels...")
labels = [
    (envelope_x, "Email Arrives", ENVELOPE_COLOR),
    (gpt_x, "GPT Summarizes", GPT_COLOR),
    (slack_x, "Posts to Slack", SLACK_COLOR)
]

for x, label, color in labels:
    bbox = draw.textbbox((0, 0), label, font=label_font)
    label_width = bbox[2] - bbox[0]
    label_x = x - label_width / 2
    label_y = icon_y + icon_size/2 + 30

    draw.text((label_x, label_y), label, fill=TEXT_COLOR, font=label_font)

# Save the image
output_path = "c:\\Users\\sabaa\\OneDrive\\Desktop\\TEST_AGENTS\\MARKETING_TEAM\\outputs\\images\\community_post_workflow.png"
print(f"Saving to {output_path}...")
img.save(output_path, "PNG", quality=95)
print("Workflow snapshot created successfully!")