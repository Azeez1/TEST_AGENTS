"""
Create an excited celebration GIF for Arnica Massage Oil product
"""
from PIL import Image, ImageDraw, ImageFont
import math
from core.gif_builder import GIFBuilder
from core.frame_composer import create_gradient_background, draw_emoji_enhanced
from core.visual_effects import ParticleSystem, create_impact_flash
from core.typography import draw_text_with_outline, TYPOGRAPHY_SCALE
from core.color_palettes import get_palette
from core.easing import interpolate

# Load the product image
product_img = Image.open(r'c:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS\MARKETING_TEAM\outputs\images\arnica_massage_oil_product.png')

# Settings for message GIF (larger, more detailed)
WIDTH = 480
HEIGHT = 480
FPS = 20
NUM_FRAMES = 60  # 3 seconds

# Color palette - warm oranges to match product
palette = get_palette('vibrant')
bg_top = (255, 248, 240)  # Warm cream
bg_bottom = (255, 235, 205)  # Peach

# Create builder
builder = GIFBuilder(WIDTH, HEIGHT, FPS)

# Particle system for sparkles and confetti
particles = ParticleSystem()

# Animation phases:
# Phase 1 (0-20): Product bounces in from top
# Phase 2 (20-40): Product pulses with sparkles
# Phase 3 (40-60): Confetti burst and text appears

for i in range(NUM_FRAMES):
    # Create background
    frame = create_gradient_background(WIDTH, HEIGHT, bg_top, bg_bottom)

    t = i / NUM_FRAMES

    # Phase 1: Bounce in (frames 0-20)
    if i < 20:
        # Bounce down from top
        t_bounce = i / 19
        product_y = interpolate(-200, 180, t_bounce, 'bounce_out')
        product_scale = interpolate(0.6, 0.4, t_bounce, 'ease_out')

    # Phase 2: Pulse (frames 20-40)
    elif i < 40:
        product_y = 180
        # Pulsing scale
        pulse_t = (i - 20) / 20
        product_scale = 0.4 + math.sin(pulse_t * math.pi * 4) * 0.05

        # Emit sparkles around product
        if i % 3 == 0:
            particles.emit_sparkles(
                x=WIDTH // 2 + (math.sin(i * 0.3) * 60),
                y=int(product_y) + 100,
                count=3
            )

    # Phase 3: Celebration (frames 40-60)
    else:
        product_y = 180
        product_scale = 0.4

        # Big confetti burst at start of phase
        if i == 40:
            particles.emit_confetti(x=WIDTH // 2, y=HEIGHT // 2, count=30)

        # Add flash effect at burst
        if i >= 40 and i < 43:
            frame = create_impact_flash(frame, (WIDTH // 2, HEIGHT // 2), radius=200, intensity=0.4)

    # Resize and paste product image
    product_width = int(product_img.width * product_scale)
    product_height = int(product_img.height * product_scale)
    product_resized = product_img.resize((product_width, product_height), Image.Resampling.LANCZOS)

    # Center the product
    product_x = (WIDTH - product_width) // 2
    product_y_int = int(product_y)

    # Paste product (handling transparency)
    if product_resized.mode == 'RGBA':
        frame.paste(product_resized, (product_x, product_y_int), product_resized)
    else:
        frame.paste(product_resized, (product_x, product_y_int))

    # Update and render particles
    particles.update()
    particles.render(frame)

    # Add celebratory emojis floating around (phase 2+3)
    if i >= 20:
        # Floating emojis
        emoji_offset = (i - 20) * 5

        # Left sparkle
        sparkle_y = 100 + math.sin((i - 20) * 0.2) * 30
        draw_emoji_enhanced(frame, '✨', position=(60, int(sparkle_y)), size=40, shadow=False)

        # Right sparkle
        sparkle_y2 = 120 + math.sin((i - 20) * 0.25 + 1) * 25
        draw_emoji_enhanced(frame, '✨', position=(380, int(sparkle_y2)), size=40, shadow=False)

    # Add text in phase 3
    if i >= 45:
        text_alpha = min(1.0, (i - 45) / 10)  # Fade in

        # "NEW!" text at top
        draw_text_with_outline(
            frame, "NEW!",
            position=(WIDTH // 2, 50),
            font_size=TYPOGRAPHY_SCALE['h1'],
            text_color=(255, 100, 50),  # Orange
            outline_color=(0, 0, 0),
            outline_width=4,
            centered=True
        )

        # Product benefit text at bottom
        draw_text_with_outline(
            frame, "Muscle Relief",
            position=(WIDTH // 2, 420),
            font_size=TYPOGRAPHY_SCALE['h3'],
            text_color=(80, 80, 80),
            outline_color=(255, 255, 255),
            outline_width=3,
            centered=True
        )

    builder.add_frame(frame)

# Save the GIF
output_path = r'c:\Users\sabaa\OneDrive\Desktop\TEST_AGENTS\MARKETING_TEAM\outputs\images\arnica_celebration.gif'
info = builder.save(output_path, num_colors=128, optimize_for_emoji=False)

print(f"\n✅ GIF created successfully!")
print(f"📁 Location: {output_path}")
print(f"📊 Size: {info['size_mb']:.2f} MB ({info['size_kb']:.1f} KB)")
print(f"🎬 Frames: {info['frame_count']}")
print(f"⏱️  Duration: {info['duration_seconds']:.1f}s")

# Validate for Slack
from core.validators import check_slack_size, is_slack_ready

passes, size_info = check_slack_size(output_path, is_emoji=False)
if passes:
    print(f"✅ Ready for Slack! ({size_info['size_kb']:.1f} KB)")
else:
    print(f"⚠️  Warning: {size_info['size_kb']:.1f} KB (recommended: <2048 KB)")