"""
Generate images for AI Email Marketing Tools presentation
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append('tools')

from generate_image import generate_slide_image

# Ensure output directory exists
os.makedirs('outputs/presentations/images', exist_ok=True)

print("Generating hero image for title slide...")
hero_image = generate_slide_image(
    prompt="Modern professional AI email marketing concept, futuristic digital interface showing emails and AI neural networks, corporate tech aesthetic, blue and white color scheme, clean minimalist design",
    style="professional",
    size="1792x1024",  # Wide format for presentation
    output_dir="outputs/presentations/images"
)

print(f"\nImage generated successfully!")
print(f"Path: {hero_image}")
