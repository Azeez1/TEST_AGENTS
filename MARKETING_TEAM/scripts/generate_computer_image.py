"""
Generate Realistic Computer Image using GPT-4o
Visual Designer Agent - Computer Image Generation
"""

from openai import OpenAI
import base64
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_computer_image():
    """Generate a realistic computer image using GPT-4o"""

    prompt = """Professional product photography of a modern high-end desktop computer setup.
    Sleek black gaming PC tower with RGB lighting, dual 4K monitors displaying beautiful abstract wallpapers,
    mechanical keyboard with backlighting, wireless mouse, on a clean minimalist desk.
    Studio lighting with soft shadows, photorealistic, 8K quality, depth of field,
    professional tech product photography style"""

    size = "1536x1024"  # Landscape format - great for presentations and social media

    print("=" * 70)
    print("VISUAL DESIGNER AGENT - Computer Image Generation")
    print("=" * 70)
    print(f"\nGenerating realistic computer image with GPT-4o (gpt-image-1)...")
    print(f"Size: {size}")
    print(f"Style: Professional product photography")
    print(f"Prompt: {prompt[:100]}...\n")

    try:
        # Call GPT-4o image generation API
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=size,
            n=1
        )

        print("Image generated successfully with GPT-4o!")

        # GPT-4o returns base64-encoded images
        image_b64 = response.data[0].b64_json

        if image_b64:
            print("Decoding base64 image data...")
            image_data = base64.b64decode(image_b64)
        else:
            # Fallback to URL if provided
            image_url = response.data[0].url
            print(f"Downloading from URL: {image_url}")
            import httpx
            image_response = httpx.get(image_url, timeout=30.0)
            image_data = image_response.content

        # Save locally
        output_dir = Path("outputs/images/final")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "realistic_computer.png"

        with open(output_path, "wb") as f:
            f.write(image_data)

        print(f"Image saved to: {output_path}")
        print(f"File size: {len(image_data) / 1024:.2f} KB")
        print(f"Cost: $0.06 USD")
        print("\n" + "=" * 70)
        print("SUCCESS! Realistic computer image created!")
        print("=" * 70 + "\n")

        return {
            "status": "success",
            "model": "gpt-image-1 (GPT-4o)",
            "image_path": str(output_path),
            "size": size,
            "cost_usd": 0.06
        }

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("=" * 70 + "\n")
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    result = generate_computer_image()

    if result["status"] == "success":
        print(f"Image ready at: {result['image_path']}")
        print("\nNext: Use video-producer agent to create a video!")
