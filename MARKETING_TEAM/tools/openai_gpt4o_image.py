"""
GPT-4o Image Generation Tool
Uses OpenAI's latest gpt-image-1 model (GPT-4o)
"""

from openai import AsyncOpenAI
from claude_agent_sdk import tool
import json
import httpx
import os
from pathlib import Path

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@tool(
    "generate_gpt4o_image",
    "Generate high-quality image using GPT-4o (gpt-image-1) - latest multimodal model",
    {
        "prompt": str,
        "aspect_ratio": str,  # "1:1", "2:3", "3:2"
        "detail": str,  # "low", "medium", "high"
        "filename": str
    }
)
async def generate_gpt4o_image(args):
    """
    Generate image using GPT-4o (gpt-image-1)

    GPT-4o Advantages over DALL-E 3:
    - Better text rendering (sharp, accurate)
    - Superior prompt understanding
    - Context-aware generation
    - Higher resolution support (up to 4096x4096)
    - Native multimodal understanding

    Aspect Ratios:
    - "1:1" - Square (1024x1024, 2048x2048, 4096x4096)
    - "2:3" - Portrait
    - "3:2" - Landscape
    """

    prompt = args["prompt"]
    aspect_ratio = args.get("aspect_ratio", "1:1")
    detail = args.get("detail", "high")
    filename = args["filename"]

    # Map aspect ratio to size
    size_map = {
        "1:1": "1024x1024",
        "2:3": "1024x1536",
        "3:2": "1536x1024"
    }
    size = size_map.get(aspect_ratio, "1024x1024")

    try:
        # Call GPT-4o image generation
        response = await openai_client.images.generate(
            model="gpt-image-1",  # GPT-4o image model
            prompt=prompt,
            size=size,
            n=1
        )

        # GPT-4o returns base64-encoded images, not URLs
        import base64
        image_b64 = response.data[0].b64_json

        if image_b64:
            # Decode base64 image data
            image_data = base64.b64decode(image_b64)
            image_url = "Generated via base64 (GPT-4o)"
        else:
            # Fallback to URL if provided
            image_url = response.data[0].url
            async with httpx.AsyncClient() as client:
                image_response = await client.get(image_url, timeout=30.0)
                image_data = image_response.content

        # Save locally
        output_path = f"outputs/images/final/{filename}.png"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(image_data)

        # Upload to Google Drive
        try:
            from tools.google_drive import upload_file_to_drive
            drive_result = await upload_file_to_drive({
                "file_path": output_path,
                "folder_type": "images",
                "description": f"GPT-4o generated: {prompt[:100]}"
            })
            drive_url = json.loads(drive_result["content"][0]["text"]).get("google_drive_url")
        except:
            drive_url = "Not uploaded (Google Drive not configured)"

        # Calculate cost
        cost_map = {
            "1024x1024": 0.04,
            "1024x1536": 0.06,
            "1536x1024": 0.06
        }
        cost = cost_map.get(size, 0.04)

        result = {
            "status": "success",
            "model": "gpt-image-1 (GPT-4o)",
            "image_path": output_path,
            "image_url": image_url,
            "google_drive_url": drive_url,
            "prompt": prompt,
            "size": size,
            "aspect_ratio": aspect_ratio,
            "cost_usd": cost
        }

        return {
            "content": [{
                "type": "text",
                "text": json.dumps(result, indent=2)
            }]
        }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error generating image: {str(e)}\n\nMake sure OPENAI_API_KEY is set in environment."
            }]
        }
