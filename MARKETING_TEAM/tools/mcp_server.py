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
from pathlib import Path

# CRITICAL: Load environment variables FIRST (before any OpenAI/Google imports)
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# NOW safe to import OpenAI/Google (after environment is ready)
from openai import AsyncOpenAI
import httpx
import base64

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
        output_dir = Path("MARKETING_TEAM/outputs/images")
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
            output_dir = Path("MARKETING_TEAM/outputs/videos")
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
    print(f"   Google Drive: {'✓ Available' if GOOGLE_DRIVE_AVAILABLE else '✗ Not installed'}", file=sys.stderr)
    print("", file=sys.stderr)
    asyncio.run(main())
