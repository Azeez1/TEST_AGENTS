"""
Marketing Tools MCP Server
Provides GPT-4o image generation, Sora video generation, and Google Drive uploads
as MCP tools for Claude Code agents.

Architecture:
- MCP-native async functions (no @tool decorator)
- Environment loaded BEFORE any imports
- Direct API calls to OpenAI and Google
- Returns MCP TextContent format
"""

import sys
import os
import asyncio
import json
import mimetypes
import traceback
from pathlib import Path

# CRITICAL: Load environment variables FIRST (before any OpenAI/Google imports)
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# NOW safe to import OpenAI/Google (after environment is ready)
from openai import AsyncOpenAI
import httpx
import base64

# Google Gen AI imports for Veo 3.1 and Nano Banana
try:
    from google import genai
    from google.genai import types
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False

# Google Drive imports (optional - graceful degradation if not configured)
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    import pickle
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

# Global variable to cache the last Nano Banana image for Veo 3.1
_last_generated_image = None

# MCP Server imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Create MCP server
app = Server("marketing-tools")

# Google Drive OAuth scopes
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.file']


# ============================================================================
# MCP-NATIVE TOOL FUNCTIONS (Direct API calls, no @tool decorator)
# ============================================================================

async def generate_gpt4o_image_mcp(prompt: str, aspect_ratio: str, detail: str, filename: str) -> list[TextContent]:
    """
    Generate image using GPT-4o (gpt-image-1) - MCP native implementation

    Advantages over DALL-E 3:
    - Better text rendering
    - Superior prompt understanding
    - Higher resolution support (up to 4096x4096)
    """

    # Map aspect ratio to size
    size_map = {
        "1:1": "1024x1024",
        "2:3": "1024x1536",
        "3:2": "1536x1024"
    }
    size = size_map.get(aspect_ratio, "1024x1024")

    # Cost calculation
    cost_map = {
        "1024x1024": 0.04,
        "1024x1536": 0.06,
        "1536x1024": 0.06
    }
    cost = cost_map.get(size, 0.04)

    try:
        # Initialize OpenAI client (inside function, not at module level)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return [TextContent(
                type="text",
                text="❌ Error: OPENAI_API_KEY not found in environment variables.\n\nPlease add it to MARKETING_TEAM/.env file."
            )]

        client = AsyncOpenAI(api_key=api_key)

        # Call GPT-4o image generation
        response = await client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=size,
            n=1
        )

        # GPT-4o returns base64-encoded images
        image_b64 = response.data[0].b64_json

        if image_b64:
            # Decode base64 image data
            image_data = base64.b64decode(image_b64)
            image_url = "Generated via base64 (GPT-4o)"
        else:
            # Fallback to URL if provided
            image_url = response.data[0].url
            async with httpx.AsyncClient() as http_client:
                image_response = await http_client.get(image_url, timeout=30.0)
                image_data = image_response.content

        # Save locally
        output_dir = Path("outputs/images")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{filename}.png"

        with open(output_path, "wb") as f:
            f.write(image_data)

        # Prepare result
        result = {
            "status": "success",
            "model": "gpt-image-1 (GPT-4o)",
            "image_path": str(output_path),
            "prompt": prompt,
            "size": size,
            "aspect_ratio": aspect_ratio,
            "detail": detail,
            "cost_usd": cost,
            "message": f"✅ Image generated successfully and saved to {output_path}"
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Error generating image: {str(e)}\n\nMake sure OPENAI_API_KEY is valid and set in environment."
        )]


async def generate_sora_video_mcp(prompt: str, seconds: str, orientation: str, filename: str) -> list[TextContent]:
    """
    Generate video using Sora-2 - MCP native implementation

    Model: sora-2
    Pricing: $0.10 per second
    Resolutions: 1280x720 (landscape) or 720x1280 (portrait)
    """

    # Validate seconds (must be string "4", "8", or "12")
    valid_seconds = ["4", "8", "12"]
    if seconds not in valid_seconds:
        return [TextContent(
            type="text",
            text=f"❌ Error: seconds must be one of {valid_seconds} (as STRING).\n\nGot: {seconds}\n\nExamples:\n- '4' = 4 seconds = $0.40\n- '8' = 8 seconds = $0.80\n- '12' = 12 seconds = $1.20"
        )]

    # Validate orientation
    valid_orientations = ["portrait", "landscape"]
    if orientation not in valid_orientations:
        return [TextContent(
            type="text",
            text=f"❌ Error: orientation must be one of {valid_orientations}. Got: {orientation}"
        )]

    # Map orientation to resolution
    resolution_map = {
        "portrait": "720x1280",
        "landscape": "1280x720"
    }
    resolution = resolution_map[orientation]

    # Calculate cost
    duration_int = int(seconds)
    estimated_cost = duration_int * 0.10

    try:
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return [TextContent(
                type="text",
                text="❌ Error: OPENAI_API_KEY not found in environment variables.\n\nPlease add it to MARKETING_TEAM/.env file."
            )]

        # Make direct HTTP API call to Sora
        async with httpx.AsyncClient(timeout=300.0) as http_client:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "sora-2",
                "prompt": prompt,
                "size": resolution,
                "seconds": seconds  # Must be string
            }

            # Step 1: Create video generation request
            response = await http_client.post(
                "https://api.openai.com/v1/videos",
                headers=headers,
                json=payload
            )

            if response.status_code == 404:
                return [TextContent(
                    type="text",
                    text=(
                        "❌ Sora API not available (404)\n\n"
                        "The Sora video API may not be available for your account yet.\n\n"
                        "**To get access:**\n"
                        "1. Visit https://platform.openai.com/settings/organization/general\n"
                        "2. Verify your organization\n"
                        "3. Apply for Sora access if needed\n\n"
                        "**Alternative:** Use visual-designer to create storyboard images with GPT-4o"
                    )
                )]

            if response.status_code != 200:
                error_detail = response.json() if 'application/json' in response.headers.get('content-type', '') else response.text
                return [TextContent(
                    type="text",
                    text=f"❌ API Error ({response.status_code}):\n\n{json.dumps(error_detail, indent=2)}"
                )]

            result = response.json()
            video_id = result.get('id')

            if not video_id:
                return [TextContent(
                    type="text",
                    text=f"⚠️ No video ID in response:\n\n{json.dumps(result, indent=2)}"
                )]

            # Step 2: Poll for completion
            await _poll_for_video_completion(http_client, headers, video_id)

            # Step 3: Download video
            output_dir = Path("outputs/videos")
            output_dir.mkdir(parents=True, exist_ok=True)

            if not filename.endswith('.mp4'):
                filename = f"{filename}.mp4"
            output_path = output_dir / filename

            video_content_response = await http_client.get(
                f"https://api.openai.com/v1/videos/{video_id}/content",
                headers=headers
            )

            if video_content_response.status_code != 200:
                return [TextContent(
                    type="text",
                    text=f"❌ Failed to download video: {video_content_response.status_code}"
                )]

            output_path.write_bytes(video_content_response.content)

            # Success response
            result_text = (
                f"✅ Video generated successfully!\n\n"
                f"**Model:** sora-2\n"
                f"**Prompt:** {prompt}\n"
                f"**Duration:** {seconds}s\n"
                f"**Resolution:** {resolution} ({orientation})\n"
                f"**Cost:** ${estimated_cost:.2f}\n\n"
                f"**Saved to:** {output_path}\n"
                f"**Video ID:** {video_id}"
            )

            return [TextContent(type="text", text=result_text)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Error generating video: {str(e)}\n\nCheck your OPENAI_API_KEY and Sora API access."
        )]


# Removed upload_file_to_drive_mcp - Use google-workspace MCP instead:
# mcp__google-workspace__create_drive_file


async def generate_nano_banana_image_mcp(prompt: str, aspect_ratio: str, filename: str) -> list[TextContent]:
    """
    Generate image using Nano Banana (Gemini 2.5 Flash Image)

    Model: gemini-2.5-flash-image
    Pricing: $0.039 per image ($30/1M tokens, 1290 tokens/image)

    Optimized for creating product images for Veo 3.1 image-to-video conversion.
    Excellent character consistency across multiple images.
    """

    if not GOOGLE_GENAI_AVAILABLE:
        return [TextContent(
            type="text",
            text="❌ Error: google-genai package not installed.\n\nRun: pip install google-genai"
        )]

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return [TextContent(
            type="text",
            text="❌ Error: GEMINI_API_KEY not found in environment variables.\n\nPlease add it to MARKETING_TEAM/.env file."
        )]

    try:
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)

        # Generate image
        print(f"🎨 Generating Nano Banana image ({aspect_ratio})...", file=sys.stderr)

        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=aspect_ratio)
            )
        )

        # Extract the Image object from the response (THIS is what Veo 3.1 needs!)
        image_part = response.candidates[0].content.parts[0]

        # Also save to disk for user reference
        image_data = image_part.inline_data.data
        output_dir = Path("outputs/images")
        output_dir.mkdir(parents=True, exist_ok=True)

        if not filename.endswith('.png'):
            filename = f"{filename}.png"
        output_path = output_dir / filename

        # Decode base64 if needed
        if isinstance(image_data, str):
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data

        with open(output_path, "wb") as f:
            f.write(image_bytes)

        # Store the Image Part globally so Veo can use it
        # For Nano Banana (Gemini Flash Image), the Part is at response.candidates[0].content.parts[0]
        global _last_generated_image
        _last_generated_image = image_part

        result_text = (
            f"✅ Product Image Generated!\n\n"
            f"**Model:** gemini-2.5-flash-image (Nano Banana)\n"
            f"**Aspect ratio:** {aspect_ratio}\n"
            f"**Cost:** $0.039\n\n"
            f"**Saved to:** {str(output_path)}\n\n"
            f"✨ This image is optimized for Veo 3.1 image-to-video conversion.\n"
            f"✨ Image object cached in memory for immediate Veo 3.1 use.\n\n"
            f"**Next step:** Use generate_veo_ugc_from_nano_banana to create UGC ad video"
        )

        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Error generating Nano Banana image: {str(e)}"
        )]


async def generate_veo_text_to_video_mcp(prompt: str, seconds: str, orientation: str, resolution: str, filename: str, negative_prompt: str = None) -> list[TextContent]:
    """
    Generate video from text using Veo 3.1

    Model: veo-3.1-generate-preview
    Pricing: $0.75 per second
    Supports dialogue cues, sound effects, ambient audio in prompts
    """

    if not GOOGLE_GENAI_AVAILABLE:
        return [TextContent(
            type="text",
            text="❌ Error: google-genai package not installed.\n\nRun: pip install google-genai"
        )]

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return [TextContent(
            type="text",
            text="❌ Error: GEMINI_API_KEY not found in environment variables.\n\nPlease add it to MARKETING_TEAM/.env file."
        )]

    # Validate seconds
    valid_seconds = ["4", "6", "8"]
    if seconds not in valid_seconds:
        return [TextContent(
            type="text",
            text=f"❌ Error: seconds must be one of {valid_seconds}. Got: {seconds}"
        )]

    # Map orientation to aspect ratio
    aspect_ratio = "9:16" if orientation == "portrait" else "16:9"

    # Calculate cost
    cost = float(seconds) * 0.75

    try:
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)

        print(f"🎬 Starting Veo 3.1 text-to-video generation...", file=sys.stderr)
        print(f"   Duration: {seconds}s | Resolution: {resolution} | Aspect: {aspect_ratio}", file=sys.stderr)

        # Build config
        config = types.GenerateVideosConfig(
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            duration_seconds=int(seconds),
            person_generation="allow_all"  # For text-to-video
        )

        if negative_prompt:
            config.negative_prompt = negative_prompt

        # Start generation
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
            config=config
        )

        # Poll for completion
        print("⏳ Video generating (this takes 11s - 6 minutes)...", file=sys.stderr)
        poll_count = 0

        while not operation.done:
            await asyncio.sleep(10)
            operation = client.operations.get(operation)
            poll_count += 1
            if poll_count % 6 == 0:
                print(f"   Still generating... ({poll_count * 10}s elapsed)", file=sys.stderr)

        # Check if blocked by safety
        if not hasattr(operation.response, 'generated_videos') or not operation.response.generated_videos:
            return [TextContent(
                type="text",
                text="❌ Video generation blocked by safety filters (no charge)"
            )]

        # Get video
        video = operation.response.generated_videos[0]

        # Download video
        client.files.download(file=video.video)

        # Save to outputs
        output_dir = Path("outputs/videos")
        output_dir.mkdir(parents=True, exist_ok=True)

        if not filename.endswith('.mp4'):
            filename = f"{filename}.mp4"
        output_path = output_dir / filename

        video.video.save(str(output_path))

        result_text = (
            f"✅ Veo 3.1 Video Generated!\n\n"
            f"**Model:** veo-3.1-generate-preview\n"
            f"**Duration:** {seconds} seconds\n"
            f"**Cost:** ${cost:.2f}\n"
            f"**Resolution:** {resolution} {aspect_ratio}\n"
            f"**Audio:** Native audio included\n"
            f"**Generation time:** {poll_count * 10}s\n\n"
            f"**Saved to:** {output_path}\n\n"
            f"Next: Upload to Google Drive or review video"
        )

        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Error: {str(e)}\n\nNote: You are not charged if video blocked by safety filters"
        )]


async def generate_veo_ugc_from_image_mcp(image_path: str, ugc_style: str, platform: str, seconds: str, product_name: str, filename: str, custom_prompt: str = None) -> list[TextContent]:
    """
    Generate UGC-style ad video from product image using Veo 3.1 image-to-video

    PRIMARY TOOL for UGC ad creation.
    Veo 3.1 required because: image-to-video, native audio, superior UGC styling

    UGC Styles: testimonial, demo, unboxing, lifestyle
    Platforms: tiktok, instagram, facebook
    """

    if not GOOGLE_GENAI_AVAILABLE:
        return [TextContent(
            type="text",
            text="❌ Error: google-genai package not installed.\n\nRun: pip install google-genai"
        )]

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return [TextContent(
            type="text",
            text="❌ Error: GEMINI_API_KEY not found in environment variables.\n\nPlease add it to MARKETING_TEAM/.env file."
        )]

    # UGC prompt templates with audio cues
    UGC_TEMPLATES = {
        "testimonial": {
            "tiktok": f"""Authentic selfie video, person excitedly talking to camera about {product_name},
holding product naturally with genuine enthusiasm. 'This changed my morning routine!'
Casual clothes, natural home lighting, slight handheld camera shake.
Native audio: person speaking naturally with enthusiasm, ambient home sounds.""",

            "instagram": f"""Person holding {product_name} in golden hour natural lighting,
talking to camera casually with genuine excitement. 'I've been using this every day.'
Authentic testimonial style, real emotions, handheld phone aesthetic.
Native audio: clear dialogue, warm tone, ambient sounds.""",

            "facebook": f"""Authentic customer testimonial, person with {product_name} in natural home setting,
conversational tone sharing real experience. 'It actually works, here's why...'
Genuine reactions, casual environment. Native audio: friendly conversational dialogue."""
        },
        "demo": {
            "tiktok": f"""Quick hands-on demo, person using {product_name}, showing key feature with enthusiasm.
Fast-paced, natural environment, handheld phone camera. Sound effects: product use sounds,
quick verbal callouts 'Watch this!' Authentic interaction.""",

            "instagram": f"""Casual demonstration of {product_name}, hands showing product use in natural lighting,
real-time application. Authentic interaction, phone-filmed aesthetic.
Native audio: ambient sounds, brief verbal cues, product interaction sounds.""",

            "facebook": f"""Real user demonstrating {product_name} benefits, natural home setting,
hands showing product with genuine reactions. 'Let me show you how this works.'
Native audio: clear explanation, ambient home sounds."""
        },
        "unboxing": {
            "tiktok": f"""Excited unboxing of {product_name}, hands opening package with genuine surprise.
'Oh wow!' Fast-paced reveal, natural lighting, phone camera.
Sound effects: package rustling, tape pulling, excited verbal reactions.""",

            "instagram": f"""Unboxing {product_name} with authentic first reactions, natural lighting,
handheld camera following hands. 'This looks amazing!' Genuine excitement.
Native audio: package sounds, spontaneous reactions, ambient room noise.""",

            "facebook": f"""Unboxing experience with {product_name}, casual home setting, genuine first impressions.
'Let's see what's inside!' Natural reactions. Native audio: package opening sounds,
authentic commentary."""
        },
        "lifestyle": {
            "tiktok": f"""Person casually using {product_name} in morning routine, natural home environment,
authentic lifestyle integration. Handheld camera, natural movement.
Native audio: ambient morning sounds, brief casual comments.""",

            "instagram": f"""Everyday moment with {product_name}, natural setting showing real-life usage,
casual authentic vibe, gentle camera movement. Native audio: ambient sounds,
natural environment audio.""",

            "facebook": f"""{product_name} integrated into daily life, natural home environment,
real everyday use showing product naturally. Native audio: ambient home sounds,
brief natural commentary."""
        }
    }

    # Platform settings
    platform_config = {
        "tiktok": {"aspect_ratio": "9:16", "resolution": "720p"},
        "instagram": {"aspect_ratio": "9:16", "resolution": "720p"},
        "facebook": {"aspect_ratio": "16:9", "resolution": "1080p" if seconds == "8" else "720p"}
    }

    config_settings = platform_config.get(platform, {"aspect_ratio": "9:16", "resolution": "720p"})
    cost = float(seconds) * 0.75

    try:
        # Load image file
        if not Path(image_path).exists():
            return [TextContent(
                type="text",
                text=f"❌ Error: Image not found at {image_path}"
            )]

        # Initialize client
        client = genai.Client(api_key=api_key)

        # Upload image file to get File object (required for reference images from disk)
        print(f"🖼️  Uploading reference image: {image_path}", file=sys.stderr)

        # Determine mime type
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/png"

        # Read image bytes
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        print(f"✅ Image loaded ({len(image_bytes)} bytes)", file=sys.stderr)

        # Get prompt
        final_prompt = custom_prompt if custom_prompt else UGC_TEMPLATES[ugc_style][platform]

        print(f"🎬 Starting Veo 3.1 image-to-video UGC generation...", file=sys.stderr)
        print(f"   Style: {ugc_style} | Platform: {platform} | Duration: {seconds}s", file=sys.stderr)

        # Create image parameter using correct Google GenAI format (imageBytes in camelCase)
        image_param = types.Image(
            imageBytes=image_bytes,
            mimeType=mime_type
        )

        # Generate video with image as first frame (image-to-video animation)
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=final_prompt,
            image=image_param,  # types.Image with imageBytes field
            config=types.GenerateVideosConfig(
                aspect_ratio=config_settings["aspect_ratio"],
                resolution=config_settings["resolution"],
                duration_seconds=int(seconds),
                person_generation="allow_adult"  # For image-to-video
            )
        )

        # Poll for completion
        print("⏳ Video generating (1-6 minutes for image-to-video)...", file=sys.stderr)
        poll_count = 0

        while not operation.done:
            await asyncio.sleep(10)
            operation = client.operations.get(operation)
            poll_count += 1
            if poll_count % 6 == 0:
                print(f"   Still generating... ({poll_count * 10}s elapsed)", file=sys.stderr)

        # Check result
        if not hasattr(operation.response, 'generated_videos') or not operation.response.generated_videos:
            return [TextContent(
                type="text",
                text="❌ Video generation blocked by safety filters (no charge)"
            )]

        # Download and save
        video = operation.response.generated_videos[0]
        client.files.download(file=video.video)

        # Use absolute path from the script location
        script_dir = Path(__file__).parent.parent  # MARKETING_TEAM folder
        output_dir = script_dir / "outputs" / "videos"
        output_dir.mkdir(parents=True, exist_ok=True)

        if not filename.endswith('.mp4'):
            filename = f"{filename}.mp4"
        output_path = output_dir / filename

        video.video.save(str(output_path))

        result_text = (
            f"✅ UGC Video Generated Successfully!\n\n"
            f"**Model:** veo-3.1-generate-preview\n"
            f"**Style:** {ugc_style} ({platform} optimized)\n"
            f"**Duration:** {seconds} seconds\n"
            f"**Cost:** ${cost:.2f} (Veo 3.1)\n"
            f"**Resolution:** {config_settings['resolution']} {config_settings['aspect_ratio']}\n"
            f"**Audio:** Native dialogue + sound effects + ambient\n"
            f"**Generation time:** {poll_count * 10}s\n\n"
            f"**Saved to:** {output_path}\n\n"
            f"✨ UGC Characteristics:\n"
            f"- Handheld camera aesthetic\n"
            f"- Natural lighting and setting\n"
            f"- Authentic reactions and dialogue\n"
            f"- Native audio (not added post)\n\n"
            f"Next: Review video, upload to Google Drive, test on {platform}"
        )

        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Error: {str(e)}"
        )]


@app.call_tool()
async def generate_veo_ugc_from_nano_banana(
    ugc_style: str,
    platform: str,
    seconds: str,
    product_name: str,
    filename: str
) -> list[TextContent]:
    """
    Generate UGC video ad using cached Nano Banana image + Veo 3.1

    THIS IS THE CORRECT WORKFLOW:
    1. First call generate_nano_banana_image_mcp to create product image
    2. Then immediately call this function to convert to UGC video
    3. The image Part object is passed directly from Nano Banana to Veo

    Args:
        ugc_style: testimonial, demo, unboxing, lifestyle
        platform: tiktok, instagram, facebook
        seconds: "4", "6", or "8"
        product_name: Name of product for context
        filename: Output filename (without .mp4)
    """
    try:
        from google.genai import types
        import base64
        from pathlib import Path
        import tempfile

        global _last_generated_image

        if _last_generated_image is None:
            return [TextContent(
                type="text",
                text=(
                    "❌ No cached image found!\n\n"
                    "**Required workflow:**\n"
                    "1. First call generate_nano_banana_image_mcp to create a product image\n"
                    "2. Then immediately call this function to convert it to UGC video\n\n"
                    "The image must be freshly generated from Nano Banana - cannot load from disk."
                )
            )]

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return [TextContent(type="text", text="❌ GEMINI_API_KEY not found")]

        client = genai.Client(api_key=api_key)

        # Platform-specific configurations
        platform_configs = {
            "tiktok": {"aspect_ratio": "9:16", "resolution": "720p", "optimal_seconds": "6"},
            "instagram": {"aspect_ratio": "9:16", "resolution": "720p", "optimal_seconds": "8"},
            "facebook": {"aspect_ratio": "16:9", "resolution": "720p", "optimal_seconds": "8"}
        }

        config = platform_configs.get(platform.lower(), platform_configs["tiktok"])

        # UGC-style prompts
        ugc_prompts = {
            "testimonial": f"Authentic testimonial-style video of someone showing {product_name} to camera with excited, genuine reactions. Handheld camera feel, natural lighting, person speaking directly to camera.",
            "demo": f"Natural product demonstration of {product_name} in everyday setting. Person casually showing features, handheld camera, authentic reactions.",
            "unboxing": f"Excited unboxing experience of {product_name}. Genuine reactions, handheld camera, natural home lighting.",
            "lifestyle": f"Lifestyle shot showing {product_name} in authentic daily use. Natural setting, handheld camera movement, real-world context."
        }

        prompt = ugc_prompts.get(ugc_style.lower(), ugc_prompts["testimonial"])

        # Calculate cost
        seconds_int = int(seconds)
        cost = seconds_int * 0.75

        # Build config for video generation
        veo_config = types.GenerateVideosConfig(
            aspect_ratio=config["aspect_ratio"],
            resolution=config["resolution"],
            duration_seconds=seconds_int,
            person_generation="allow_adult"  # For UGC videos with people
        )

        # Start generation - Veo 3.1 requires uploading the image as a File first
        # The Part object from Nano Banana needs to be uploaded to Google's servers
        print("📤 Uploading image to Google's servers for Veo 3.1...", file=sys.stderr)

        # Extract image data from the cached Part object
        image_data = _last_generated_image.inline_data.data
        mime_type = _last_generated_image.inline_data.mime_type

        # Decode base64 if needed
        if isinstance(image_data, str):
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data

        print(f"✅ Using cached image from Nano Banana ({len(image_bytes)} bytes)", file=sys.stderr)

        # Use the cached Part object directly from Nano Banana
        # The SDK should accept Part objects for image-to-video
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
            image=_last_generated_image,  # Use the Part object from Nano Banana cache
            config=veo_config
        )

        # Poll for completion (same pattern as text-to-video)
        print("⏳ UGC video generating (this takes 11s - 6 minutes)...", file=sys.stderr)
        poll_count = 0

        while not operation.done:
            await asyncio.sleep(10)
            operation = client.operations.get(operation)
            poll_count += 1
            if poll_count % 6 == 0:
                print(f"   Still generating... ({poll_count * 10}s elapsed)", file=sys.stderr)

        # Check if blocked by safety
        if not hasattr(operation.response, 'generated_videos') or not operation.response.generated_videos:
            return [TextContent(
                type="text",
                text="❌ Video generation blocked by safety filters (no charge)"
            )]

        # Get video
        video = operation.response.generated_videos[0]

        # Download video
        client.files.download(file=video.video)

        # Save to outputs
        output_dir = Path("outputs/videos")
        output_dir.mkdir(parents=True, exist_ok=True)

        if not filename.endswith('.mp4'):
            filename = f"{filename}.mp4"
        output_path = output_dir / filename

        video.video.save(str(output_path))

        # Clear the cached image after successful use
        _last_generated_image = None

        result_text = (
            f"✅ UGC Video Generated Successfully!\n\n"
            f"**Model:** veo-3.1-generate-preview\n"
            f"**Style:** {ugc_style} ({platform} optimized)\n"
            f"**Duration:** {seconds} seconds\n"
            f"**Cost:** ${cost:.2f} (Veo 3.1)\n"
            f"**Resolution:** {config['resolution']} {config['aspect_ratio']}\n"
            f"**Audio:** Native dialogue + sound effects + ambient\n"
            f"**Generation time:** {poll_count * 10}s\n\n"
            f"**Saved to:** {output_path}\n\n"
            f"✨ UGC Characteristics:\n"
            f"- Handheld camera aesthetic\n"
            f"- Natural lighting and setting\n"
            f"- Authentic reactions and dialogue\n"
            f"- Native audio (not added post)\n"
            f"- Reference image from Nano Banana integrated seamlessly\n\n"
            f"Next: Review video, upload to Google Drive, test on {platform}"
        )

        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Error: {str(e)}\n\nTraceback: {traceback.format_exc()}"
        )]


async def _poll_for_video_completion(http_client, headers, video_id, max_wait=300):
    """Poll the API for video generation completion"""
    import time
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed > max_wait:
            raise TimeoutError(f"Video generation timed out after {max_wait} seconds")

        response = await http_client.get(
            f"https://api.openai.com/v1/videos/{video_id}",
            headers=headers
        )

        if response.status_code != 200:
            raise Exception(f"Failed to check video status: {response.text}")

        result = response.json()
        status = result.get('status')

        if status == 'completed':
            return  # Video is ready
        elif status == 'failed':
            raise Exception(f"Video generation failed: {result.get('error', 'Unknown error')}")

        # Wait before polling again
        await asyncio.sleep(5)


# ============================================================================
# MCP SERVER TOOL REGISTRATION
# ============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available marketing tools"""
    return [
        Tool(
            name="generate_gpt4o_image",
            description="Generate high-quality image using GPT-4o (gpt-image-1) - latest multimodal model with superior text rendering",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Detailed image generation prompt (style, colors, composition, text)"
                    },
                    "aspect_ratio": {
                        "type": "string",
                        "description": "Aspect ratio: 1:1 (square), 2:3 (portrait), or 3:2 (landscape)",
                        "enum": ["1:1", "2:3", "3:2"],
                        "default": "1:1"
                    },
                    "detail": {
                        "type": "string",
                        "description": "Detail level: low, medium, or high",
                        "enum": ["low", "medium", "high"],
                        "default": "high"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Output filename (without .png extension)"
                    }
                },
                "required": ["prompt", "filename"]
            }
        ),
        Tool(
            name="generate_sora_video",
            description="Generate video using OpenAI's Sora-2 model ($0.10/second, 720p)",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Detailed video prompt (scene, camera movement, lighting, pacing)"
                    },
                    "seconds": {
                        "type": "string",
                        "description": "Video duration: '4', '8', or '12' (MUST be string)",
                        "enum": ["4", "8", "12"],
                        "default": "4"
                    },
                    "orientation": {
                        "type": "string",
                        "description": "Video orientation: portrait (720x1280) or landscape (1280x720)",
                        "enum": ["portrait", "landscape"],
                        "default": "landscape"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Output filename (will add .mp4 extension)"
                    }
                },
                "required": ["prompt", "filename"]
            }
        ),
        Tool(
            name="generate_nano_banana_image",
            description="Generate image using Nano Banana (Gemini 2.5 Flash Image) - $0.039/image, excellent character consistency, optimized for Veo 3.1 image-to-video",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Image generation prompt with natural language description"
                    },
                    "aspect_ratio": {
                        "type": "string",
                        "description": "Aspect ratio: 1:1, 16:9, 9:16, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 21:9",
                        "enum": ["1:1", "16:9", "9:16", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "21:9"],
                        "default": "9:16"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Output filename (without extension, .png will be added)"
                    }
                },
                "required": ["prompt", "filename"]
            }
        ),
        Tool(
            name="generate_veo_text_to_video",
            description="Generate video from text using Veo 3.1 ($0.75/second, 720p/1080p, native audio with dialogue and sound effects)",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Video prompt with dialogue cues (quotes), sound effects, ambient audio descriptions"
                    },
                    "seconds": {
                        "type": "string",
                        "description": "Video duration: '4', '6', or '8' (MUST be string)",
                        "enum": ["4", "6", "8"],
                        "default": "8"
                    },
                    "orientation": {
                        "type": "string",
                        "description": "Video orientation",
                        "enum": ["portrait", "landscape"],
                        "default": "portrait"
                    },
                    "resolution": {
                        "type": "string",
                        "description": "Video resolution (1080p only available for 8s videos)",
                        "enum": ["720p", "1080p"],
                        "default": "720p"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Output filename (without extension, .mp4 will be added)"
                    },
                    "negative_prompt": {
                        "type": "string",
                        "description": "Optional: Elements to exclude from generation"
                    }
                },
                "required": ["prompt", "filename"]
            }
        ),
        Tool(
            name="generate_veo_ugc_from_image",
            description="PRIMARY UGC TOOL: Generate authentic UGC-style ad video from product image using Veo 3.1 image-to-video ($0.75/second, native audio, 4 styles, 3 platforms)",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to product image (e.g., MARKETING_TEAM/outputs/images/product.png)"
                    },
                    "ugc_style": {
                        "type": "string",
                        "description": "UGC style",
                        "enum": ["testimonial", "demo", "unboxing", "lifestyle"],
                        "default": "testimonial"
                    },
                    "platform": {
                        "type": "string",
                        "description": "Target platform (auto-optimizes aspect ratio and duration)",
                        "enum": ["tiktok", "instagram", "facebook"],
                        "default": "tiktok"
                    },
                    "seconds": {
                        "type": "string",
                        "description": "Video duration: '6' or '8' (MUST be string, 8 recommended)",
                        "enum": ["6", "8"],
                        "default": "8"
                    },
                    "product_name": {
                        "type": "string",
                        "description": "Product name for UGC prompt generation"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Output filename (without extension, .mp4 will be added)"
                    },
                    "custom_prompt": {
                        "type": "string",
                        "description": "Optional: Override default UGC template with custom prompt"
                    }
                },
                "required": ["image_path", "ugc_style", "platform", "product_name", "filename"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a marketing tool"""

    try:
        if name == "generate_gpt4o_image":
            return await generate_gpt4o_image_mcp(
                prompt=arguments["prompt"],
                aspect_ratio=arguments.get("aspect_ratio", "1:1"),
                detail=arguments.get("detail", "high"),
                filename=arguments["filename"]
            )

        elif name == "generate_sora_video":
            return await generate_sora_video_mcp(
                prompt=arguments["prompt"],
                seconds=arguments.get("seconds", "4"),
                orientation=arguments.get("orientation", "landscape"),
                filename=arguments["filename"]
            )

        elif name == "generate_nano_banana_image":
            return await generate_nano_banana_image_mcp(
                prompt=arguments["prompt"],
                aspect_ratio=arguments.get("aspect_ratio", "9:16"),
                filename=arguments["filename"]
            )

        elif name == "generate_veo_text_to_video":
            return await generate_veo_text_to_video_mcp(
                prompt=arguments["prompt"],
                seconds=arguments.get("seconds", "8"),
                orientation=arguments.get("orientation", "portrait"),
                resolution=arguments.get("resolution", "720p"),
                filename=arguments["filename"],
                negative_prompt=arguments.get("negative_prompt")
            )

        elif name == "generate_veo_ugc_from_image":
            return await generate_veo_ugc_from_image_mcp(
                image_path=arguments["image_path"],
                ugc_style=arguments.get("ugc_style", "testimonial"),
                platform=arguments.get("platform", "tiktok"),
                seconds=arguments.get("seconds", "8"),
                product_name=arguments["product_name"],
                filename=arguments["filename"],
                custom_prompt=arguments.get("custom_prompt")
            )

        else:
            return [TextContent(
                type="text",
                text=f"❌ Unknown tool: {name}"
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Error executing {name}: {str(e)}\n\nArguments: {json.dumps(arguments, indent=2)}"
        )]


# ============================================================================
# MCP SERVER MAIN
# ============================================================================

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    print("🚀 Marketing Tools MCP Server starting...", file=sys.stderr)
    print(f"   Environment loaded from: {env_path}", file=sys.stderr)
    print(f"   OpenAI API Key: {'✓ Found' if os.getenv('OPENAI_API_KEY') else '✗ Missing'}", file=sys.stderr)
    print(f"   Gemini API Key: {'✓ Found' if os.getenv('GEMINI_API_KEY') else '✗ Missing'}", file=sys.stderr)
    print(f"   Google GenAI: {'✓ Available' if GOOGLE_GENAI_AVAILABLE else '✗ Not installed'}", file=sys.stderr)
    print(f"   Google Drive: {'✓ Available' if GOOGLE_DRIVE_AVAILABLE else '✗ Not installed'}", file=sys.stderr)
    print("", file=sys.stderr)
    asyncio.run(main())
