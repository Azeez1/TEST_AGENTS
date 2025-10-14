"""
Generate LinkedIn Header Image for Accenture AI Post
Uses OpenAI API directly to call gpt-image-1 (GPT-4o)
"""

import asyncio
import os
import httpx
from pathlib import Path
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def create_linkedin_header():
    """Create professional LinkedIn header image"""

    print("[*] Creating LinkedIn header image for Accenture AI post...")
    print()

    # LinkedIn optimal size: 1200x627 (close to 3:2 ratio - 1536x1024)
    # We'll use 3:2 which is 1536x1024

    prompt = """
Professional LinkedIn header image for a business article about Accenture's AI strategy.

Design style: Modern, sleek, corporate but innovative

Visual elements:
- Abstract AI/technology motifs (neural networks, data streams, geometric patterns)
- Color palette: Deep blue (#0000FF), white, accents of electric blue and silver
- Accenture-inspired professional aesthetic
- Text overlay space reserved (left third of image)
- Subtle gradient background from dark blue to lighter blue
- Floating digital elements suggesting autonomous AI
- Clean, minimalist composition
- High-tech feel with glowing elements
- 3D geometric shapes suggesting data and connectivity

Mood: Forward-thinking, authoritative, innovative, enterprise-grade

Style: Photo-realistic with digital overlay, sharp and clean, suitable for LinkedIn professional audience
"""

    print("[*] Calling OpenAI GPT-4o image generation...")
    print(f"[*] Model: gpt-image-1")
    print(f"[*] Size: 1536x1024 (3:2 ratio, perfect for LinkedIn)")
    print()

    try:
        # Generate image using GPT-4o
        response = await client.images.generate(
            model="gpt-image-1",  # GPT-4o image model
            prompt=prompt.strip(),
            size="1536x1024",
            n=1
        )

        # Debug: print full response
        print(f"[DEBUG] Response: {response}")
        print()

        # GPT-4o returns base64 encoded image
        import base64
        b64_data = response.data[0].b64_json
        print(f"[OK] Image generated successfully!")
        print(f"[*] Format: Base64 encoded PNG")
        print()

        # Decode base64 image
        print("[*] Decoding image data...")
        image_data = base64.b64decode(b64_data)

        # Save locally
        output_path = "outputs/images/final/accenture-ai-linkedin-header.png"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(image_data)

        print(f"[OK] Image saved to: {output_path}")
        print()
        print("=" * 60)
        print("[SUCCESS] LinkedIn header image created!")
        print("=" * 60)
        print()
        print(f"File: {output_path}")
        print(f"Size: 1536x1024 (optimized for LinkedIn)")
        print(f"Cost: $0.06 USD")
        print()
        print("Ready to upload with your LinkedIn post!")
        print()

    except Exception as e:
        print(f"[X] Error: {str(e)}")
        print()
        print("Common issues:")
        print("  - Invalid API key")
        print("  - Insufficient credits")
        print("  - Network connectivity")
        print()


if __name__ == "__main__":
    asyncio.run(create_linkedin_header())
