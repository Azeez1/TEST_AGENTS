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
ENVELOPE_DARK = (230, 122, 54)     # Darker orange
GPT_COLOR = (138, 109, 255)        # Playful purple
GPT_LIGHT = (168, 144, 255)        # Lighter purple
SLACK_COLOR = (77, 182, 172)       # Soft teal
SLACK_DARK = (52, 157, 147)        # Darker teal
ARROW_COLOR = (100, 100, 100)      # Soft gray
TEXT_COLOR = (60, 60, 60)          # Warm dark gray
TITLE_COLOR = (40, 40, 40)         # Almost black

def draw_wobbly_line(draw, start, end, color, width=4, wobble=3):
    """Draw a hand-drawn style wobbly line"""
    x1, y1 = start
    x2, y2 = end
    steps = 25
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
    segments = 48

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

def draw_wobbly_rectangle(draw, bbox, color, fill=True, width=4, wobble=2):
    """Draw a hand-drawn style rectangle"""
    x1, y1, x2, y2 = bbox

    # Create corner points with slight wobble
    top_left = (x1 + random.uniform(-wobble, wobble), y1 + random.uniform(-wobble, wobble))
    top_right = (x2 + random.uniform(-wobble, wobble), y1 + random.uniform(-wobble, wobble))
    bottom_right = (x2 + random.uniform(-wobble, wobble), y2 + random.uniform(-wobble, wobble))
    bottom_left = (x1 + random.uniform(-wobble, wobble), y2 + random.uniform(-wobble, wobble))

    corners = [top_left, top_right, bottom_right, bottom_left]

    if fill:
        draw.polygon(corners, fill=color, outline=color)

    # Draw wobbly edges for outline
    for i in range(4):
        start = corners[i]
        end = corners[(i + 1) % 4]
        draw_wobbly_line(draw, start, end, color, width, wobble)

def draw_envelope(draw, center, size, color):
    """Draw a cartoonish envelope icon with enhanced detail"""
    x, y = center
    w, h = size, size * 0.65

    # Envelope body with subtle shading
    draw_wobbly_rectangle(draw,
                         (x - w/2, y - h/2, x + w/2, y + h/2),
                         color, fill=True, wobble=1.5)

    # Envelope flap (triangle) - darker shade
    flap_points = [
        (x - w/2 + random.uniform(-1.5, 1.5), y - h/2 + random.uniform(-1.5, 1.5)),
        (x + random.uniform(-1.5, 1.5), y + h/5 + random.uniform(-1.5, 1.5)),
        (x + w/2 + random.uniform(-1.5, 1.5), y - h/2 + random.uniform(-1.5, 1.5))
    ]

    draw.polygon(flap_points, fill=ENVELOPE_DARK, outline=ENVELOPE_DARK)

    # Add subtle detail lines
    draw_wobbly_line(draw, flap_points[0], flap_points[1], (0, 0, 0, 60), width=2, wobble=1)
    draw_wobbly_line(draw, flap_points[1], flap_points[2], (0, 0, 0, 60), width=2, wobble=1)

    # Add a cute stamp in corner
    stamp_x, stamp_y = x + w/3, y - h/5
    stamp_size = size/8
    draw_wobbly_rectangle(draw,
                         (stamp_x - stamp_size/2, stamp_y - stamp_size/2,
                          stamp_x + stamp_size/2, stamp_y + stamp_size/2),
                         ENVELOPE_DARK, fill=True, wobble=1)

def draw_brain(draw, center, size, color):
    """Draw a cartoonish brain/AI icon with sparkles"""
    x, y = center

    # Main brain circle with light glow effect
    draw_wobbly_circle(draw, center, size/2 + 3, GPT_LIGHT, fill=True, wobble=2)
    draw_wobbly_circle(draw, center, size/2, color, fill=True, wobble=2.5)

    # Add "brain wrinkles" - organic bumpy texture
    bump_positions = [
        (x - size/3.5, y - size/7),
        (x + size/3.5, y - size/7),
        (x - size/4, y + size/6),
        (x + size/4, y + size/6),
        (x, y - size/3.5),
        (x - size/6, y),
        (x + size/6, y)
    ]

    lighter_color = tuple(min(255, c + 50) for c in color)
    for pos in bump_positions:
        bump_size = random.uniform(size/8, size/6)
        draw_wobbly_circle(draw, pos, bump_size, lighter_color, fill=True, wobble=1.5)

    # Add sparkle lines (AI magic effect) - 4 main directions
    sparkle_length = size/2.8
    sparkle_angles = [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]

    for angle in sparkle_angles:
        start_x = x + (size/2 + 10) * math.cos(angle)
        start_y = y + (size/2 + 10) * math.sin(angle)
        end_x = start_x + sparkle_length * math.cos(angle)
        end_y = start_y + sparkle_length * math.sin(angle)
        draw_wobbly_line(draw, (start_x, start_y), (end_x, end_y), color, width=4, wobble=1.5)

        # Add small dots at sparkle ends
        draw_wobbly_circle(draw, (end_x, end_y), 3, color, fill=True, wobble=0.5)

def draw_chat_bubble(draw, center, size, color):
    """Draw a cartoonish Slack chat bubble with messages"""
    x, y = center
    w, h = size * 1.3, size * 0.9

    # Main bubble with rounded feel
    bubble_rect = (x - w/2, y - h/2, x + w/2, y + h/2)
    draw_wobbly_rectangle(draw, bubble_rect, color, fill=True, wobble=1.5)

    # Add rounded corner circles for smooth edges
    corner_radius = size/7
    corners = [
        (x - w/2 + corner_radius, y - h/2 + corner_radius),
        (x + w/2 - corner_radius, y - h/2 + corner_radius),
        (x - w/2 + corner_radius, y + h/2 - corner_radius),
        (x + w/2 - corner_radius, y + h/2 - corner_radius)
    ]

    for corner in corners:
        draw_wobbly_circle(draw, corner, corner_radius, color, fill=True, wobble=1)

    # Chat bubble tail (small triangle pointing left)
    tail_height = size/3
    tail_points = [
        (x - w/2 + 2, y + h/4),
        (x - w/2 - tail_height/1.5, y + h/2 + tail_height/3),
        (x - w/2 + 2, y + h/2 - tail_height/4)
    ]
    draw.polygon(tail_points, fill=color, outline=color)

    # Add message lines inside (3 lines)
    line_color = SLACK_DARK
    line_spacing = h/5
    line_start_y = y - h/3.5

    for i in range(3):
        line_y = line_start_y + i * line_spacing
        # Make lines different lengths for variety
        if i == 0:
            line_width = w * 0.6
        elif i == 1:
            line_width = w * 0.7
        else:
            line_width = w * 0.5

        draw_wobbly_line(draw,
                        (x - line_width/2, line_y),
                        (x + line_width/2, line_y),
                        line_color, width=3, wobble=0.8)

def draw_arrow(draw, start, end, color, size=24):
    """Draw a cartoonish curved arrow with personality"""
    x1, y1 = start
    x2, y2 = end

    # Draw curved line with control point (bouncy curve)
    control_x = (x1 + x2) / 2
    control_y = (y1 + y2) / 2 - 35  # Upward curve

    # Quadratic Bezier curve
    steps = 30
    points = []
    for i in range(steps + 1):
        t = i / steps
        px = (1-t)**2 * x1 + 2*(1-t)*t * control_x + t**2 * x2
        py = (1-t)**2 * y1 + 2*(1-t)*t * control_y + t**2 * y2
        points.append((px, py))

    # Draw the curve
    for i in range(len(points) - 1):
        draw_wobbly_line(draw, points[i], points[i + 1], color, width=6, wobble=1.5)

    # Arrow head (triangle)
    arrow_angle = math.atan2(y2 - points[-2][1], x2 - points[-2][0])
    arrow_size = size

    arrow_points = [
        (x2, y2),
        (x2 - arrow_size * math.cos(arrow_angle - math.pi/5),
         y2 - arrow_size * math.sin(arrow_angle - math.pi/5)),
        (x2 - arrow_size * 0.6 * math.cos(arrow_angle),
         y2 - arrow_size * 0.6 * math.sin(arrow_angle)),
        (x2 - arrow_size * math.cos(arrow_angle + math.pi/5),
         y2 - arrow_size * math.sin(arrow_angle + math.pi/5))
    ]

    draw.polygon(arrow_points, fill=color, outline=color)

# Layout positions - better spacing
icon_y = HEIGHT / 2 + 20
icon_size = 90

envelope_x = WIDTH * 0.18
gpt_x = WIDTH * 0.50
slack_x = WIDTH * 0.82

# Draw workflow elements
print("Drawing envelope...")
draw_envelope(draw, (envelope_x, icon_y), icon_size, ENVELOPE_COLOR)

print("Drawing GPT brain...")
draw_brain(draw, (gpt_x, icon_y), icon_size, GPT_COLOR)

print("Drawing Slack bubble...")
draw_chat_bubble(draw, (slack_x, icon_y), icon_size, SLACK_COLOR)

# Draw arrows with better positioning
print("Drawing arrows...")
arrow1_start = (envelope_x + icon_size/2 + 25, icon_y)
arrow1_end = (gpt_x - icon_size/2 - 35, icon_y)
draw_arrow(draw, arrow1_start, arrow1_end, ARROW_COLOR, size=28)

arrow2_start = (gpt_x + icon_size/2 + 35, icon_y)
arrow2_end = (slack_x - icon_size/2 - 40, icon_y)
draw_arrow(draw, arrow2_start, arrow2_end, ARROW_COLOR, size=28)

# Load fonts - use friendly, rounded fonts
try:
    title_font = ImageFont.truetype("c:\\Users\\sabaa\\OneDrive\\Desktop\\TEST_AGENTS\\.claude\\skills\\canvas-design\\canvas-fonts\\BricolageGrotesque-Bold.ttf", 56)
    label_font = ImageFont.truetype("c:\\Users\\sabaa\\OneDrive\\Desktop\\TEST_AGENTS\\.claude\\skills\\canvas-design\\canvas-fonts\\WorkSans-Bold.ttf", 26)
    print("Loaded custom fonts successfully!")
except Exception as e:
    print(f"Custom fonts error: {e}")
    title_font = ImageFont.load_default()
    label_font = ImageFont.load_default()

# Add title at top with better positioning
title_text = "Example: AI Email Summary Workflow"
print("Adding title...")

bbox = draw.textbbox((0, 0), title_text, font=title_font)
text_width = bbox[2] - bbox[0]

title_x = (WIDTH - text_width) / 2
title_y = 50

draw.text((title_x, title_y), title_text, fill=TITLE_COLOR, font=title_font)

# Add labels below each icon with color accents
print("Adding labels...")
labels = [
    (envelope_x, "Email Arrives", ENVELOPE_COLOR),
    (gpt_x, "GPT Summarizes", GPT_COLOR),
    (slack_x, "Posts to Slack", SLACK_COLOR)
]

for x, label, accent_color in labels:
    bbox = draw.textbbox((0, 0), label, font=label_font)
    label_width = bbox[2] - bbox[0]
    label_x = x - label_width / 2
    label_y = icon_y + icon_size/2 + 45

    # Draw text
    draw.text((label_x, label_y), label, fill=TEXT_COLOR, font=label_font)

    # Add subtle underline accent in icon color
    underline_y = label_y + bbox[3] - bbox[1] + 4
    underline_width = label_width * 0.4
    underline_x_center = x
    draw_wobbly_line(draw,
                    (underline_x_center - underline_width/2, underline_y),
                    (underline_x_center + underline_width/2, underline_y),
                    accent_color, width=3, wobble=0.5)

# Save the image
output_path = "c:\\Users\\sabaa\\OneDrive\\Desktop\\TEST_AGENTS\\MARKETING_TEAM\\outputs\\images\\community_post_workflow.png"
print(f"Saving to {output_path}...")
img.save(output_path, "PNG", quality=98, optimize=True)
print("Cartoonish workflow snapshot created successfully!")