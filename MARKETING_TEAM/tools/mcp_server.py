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
# LOAD UGC PROMPT TEMPLATES FROM MEMORY (DYNAMIC CONFIGURATION)
# ============================================================================

def load_ugc_templates_from_memory():
    """
    Load UGC prompt templates from memory/ugc_prompt_templates.json
    Returns: (ugc_templates_dict, list_of_style_names)
    """
    try:
        memory_path = Path(__file__).parent.parent / 'memory' / 'ugc_prompt_templates.json'

        if not memory_path.exists():
            print(f"⚠️  UGC templates not found at {memory_path}, using defaults", file=sys.stderr)
            return None, ["testimonial", "demo", "unboxing", "lifestyle"]

        with open(memory_path, 'r', encoding='utf-8') as f:
            templates_data = json.load(f)

        # Convert JSON format to UGC_TEMPLATES format
        # Templates are nested under "base_templates" and "expert_optimized_templates"
        ugc_templates = {}
        style_names = []

        # Combine both base and expert templates
        all_templates = {}
        if 'base_templates' in templates_data and isinstance(templates_data['base_templates'], dict):
            all_templates.update(templates_data['base_templates'])

        if 'expert_optimized_templates' in templates_data and isinstance(templates_data['expert_optimized_templates'], dict):
            all_templates.update(templates_data['expert_optimized_templates'])

        # Process all templates
        for style_name, template_data in all_templates.items():
            # Skip metadata fields (non-dictionary values)
            if not isinstance(template_data, dict):
                continue

            # Check if template has platform_optimized field
            if 'platform_optimized' in template_data and isinstance(template_data['platform_optimized'], dict):
                style_names.append(style_name)
                ugc_templates[style_name] = {
                    'tiktok': template_data['platform_optimized'].get('tiktok', ''),
                    'instagram': template_data['platform_optimized'].get('instagram', ''),
                    'facebook': template_data['platform_optimized'].get('facebook', '')
                }
            else:
                print(f"⚠️  Template '{style_name}' missing platform_optimized, skipping", file=sys.stderr)

        print(f"✅ Loaded {len(style_names)} UGC styles from memory/ugc_prompt_templates.json", file=sys.stderr)
        print(f"   Available styles: {', '.join(sorted(style_names)[:10])}{'...' if len(style_names) > 10 else ''}", file=sys.stderr)

        return ugc_templates, sorted(style_names)

    except Exception as e:
        print(f"⚠️  Error loading UGC templates: {e}, using defaults", file=sys.stderr)
        return None, ["testimonial", "demo", "unboxing", "lifestyle"]

# Load templates at module startup
LOADED_UGC_TEMPLATES, AVAILABLE_UGC_STYLES = load_ugc_templates_from_memory()


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
        output_dir = Path("MARKETING_TEAM/outputs/images").resolve()
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


async def generate_sora_video_mcp(
    prompt: str = None,
    seconds: str = "4",
    orientation: str = "landscape",
    filename: str = "video.mp4",
    input_reference: str = None,
    auto_analyze_image: bool = False,
    # NEW UGC parameters:
    ugc_style: str = None,
    product_name: str = None,
    platform: str = "tiktok",
    icp: str = None,
    product_features: str = None,
    video_setting: str = None
) -> list[TextContent]:
    """
    Generate video using Sora-2 - MCP native implementation with UGC support

    Model: sora-2
    Pricing: $0.10 per second + optional $0.01 for image analysis
    Resolutions: 1280x720 (landscape) or 720x1280 (portrait)

    Optional image-to-video:
    - Provide input_reference with path to image file
    - Set auto_analyze_image=True to analyze image with GPT-4o Vision (+$0.01)

    NEW UGC Styles (50 available):
    - Provide ugc_style (testimonial, demo, unboxing, lifestyle, etc.)
    - Automatically builds authentic UGC prompt from templates
    - Requires product_name parameter
    - Optional: platform, icp, product_features, video_setting
    """

    # Validation: If ugc_style provided, product_name is required
    if ugc_style and not product_name:
        return [TextContent(type="text", text="❌ Error: 'product_name' is required when using 'ugc_style'.")]

    # NEW: Build UGC prompt from template if ugc_style provided
    custom_prompt_addition = prompt  # Save custom prompt for later appending
    if ugc_style:
        try:
            # Load UGC templates
            template_path = Path(__file__).parent.parent / "memory" / "ugc_prompt_templates.json"
            with open(template_path, 'r', encoding='utf-8') as f:
                templates = json.load(f)

            # Get base template
            if ugc_style not in templates.get("base_templates", {}):
                available_styles = ", ".join(templates.get("base_templates", {}).keys())
                return [TextContent(
                    type="text",
                    text=f"❌ Error: Unknown UGC style '{ugc_style}'. Available: {available_styles}"
                )]

            template = templates["base_templates"][ugc_style]

            # Build UGC prompt (Sora-optimized version - no native audio)
            platform_desc = template["platform_optimized"].get(platform, template["platform_optimized"]["tiktok"])
            execution = template["execution_approach"]

            # Start building prompt
            prompt = f"UGC-STYLE VIDEO ({ugc_style.upper()}):\n\n"
            prompt += f"{platform_desc}\n\n"
            prompt += f"PRODUCT: {product_name}\n\n"

            if icp:
                prompt += f"TARGET AUDIENCE: {icp}\n\n"

            if product_features:
                prompt += f"KEY FEATURES: {product_features}\n\n"

            if video_setting:
                prompt += f"SETTING: {video_setting}\n\n"

            prompt += f"EXECUTION: {execution}\n\n"
            prompt += "AUTHENTICITY REQUIREMENTS:\n"
            prompt += "- Handheld camera feel (natural shake, not stabilized)\n"
            prompt += "- Natural lighting (window light, outdoor, no studio)\n"
            prompt += "- Casual settings (home, kitchen, outdoors, everyday)\n"
            prompt += "- Real people vibe (casual clothes, relatable environment)\n"
            prompt += "- NO professional production, NO perfect lighting\n"
            prompt += "- NO corporate polish (authentic > perfect)\n"

            # Append custom prompt if provided (combine UGC template + custom instructions)
            if custom_prompt_addition:
                prompt += f"\n\nADDITIONAL INSTRUCTIONS:\n{custom_prompt_addition}\n"
                print(f"✅ Built UGC prompt from '{ugc_style}' template for {platform} + custom additions", file=sys.stderr)
            else:
                print(f"✅ Built UGC prompt from '{ugc_style}' template for {platform}", file=sys.stderr)

        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error building UGC prompt: {str(e)}")]

    # Validation: Must have prompt at this point
    if not prompt:
        return [TextContent(type="text", text="❌ Error: Must provide either 'prompt' or 'ugc_style' parameter.")]

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
    analysis_cost = 0.0
    image_description = None

    try:
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return [TextContent(
                type="text",
                text="❌ Error: OPENAI_API_KEY not found in environment variables.\n\nPlease add it to MARKETING_TEAM/.env file."
            )]

        # Optional: Analyze image with GPT-4o Vision
        if input_reference and auto_analyze_image:
            image_path = Path(input_reference)
            if not image_path.exists():
                return [TextContent(
                    type="text",
                    text=f"❌ Error: Image file not found: {input_reference}"
                )]

            print(f"🔍 Analyzing image with GPT-4o Vision for better consistency...", file=sys.stderr)
            try:
                # Read and encode image as base64
                with open(image_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')

                # Determine image format
                image_format = image_path.suffix.lower().replace('.', '')
                if image_format == 'jpg':
                    image_format = 'jpeg'

                # Create data URL
                image_url = f"data:image/{image_format};base64,{image_data}"

                # Call GPT-4o Vision
                vision_client = AsyncOpenAI(api_key=api_key)
                vision_response = await vision_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe this product in detail for video generation: include colors, shapes, textures, materials, design elements, and overall composition. Focus on visual characteristics that would help maintain consistency in a video."
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url, "detail": "high"}
                            }
                        ]
                    }],
                    max_tokens=300
                )

                image_description = vision_response.choices[0].message.content.strip()
                print(f"✅ Image analysis complete (+$0.01)", file=sys.stderr)
                print(f"📝 Description: {image_description[:100]}...", file=sys.stderr)

                # Enhance prompt with image description
                prompt = f"{prompt}\n\nVisual reference: {image_description}"
                analysis_cost = 0.01

            except Exception as e:
                print(f"⚠️  Image analysis failed: {str(e)}, continuing with original prompt", file=sys.stderr)

        # Make direct HTTP API call to Sora
        async with httpx.AsyncClient(timeout=300.0) as http_client:
            # Step 1: Create video generation request
            if input_reference:
                # Image-to-video: Use multipart/form-data
                image_path = Path(input_reference)
                with open(image_path, 'rb') as f:
                    image_file_data = f.read()

                files = {
                    'input_reference': (image_path.name, image_file_data, 'image/png')
                }
                data = {
                    "model": "sora-2",
                    "prompt": prompt,
                    "size": resolution,
                    "seconds": seconds
                }
                headers = {
                    "Authorization": f"Bearer {api_key}",
                }

                response = await http_client.post(
                    "https://api.openai.com/v1/videos",
                    headers=headers,
                    data=data,
                    files=files
                )
            else:
                # Text-to-video: Use JSON
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
            output_dir = Path("MARKETING_TEAM/outputs/videos").resolve()
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
            generation_type = "Image-to-video" if input_reference else "Text-to-video"
            total_cost = estimated_cost + analysis_cost
            cost_breakdown = f"${estimated_cost:.2f}"
            if analysis_cost > 0:
                cost_breakdown += f" + ${analysis_cost:.2f} (image analysis)"

            result_text = (
                f"✅ Video generated successfully!\n\n"
                f"**Model:** sora-2\n"
                f"**Type:** {generation_type}\n"
                f"**Prompt:** {prompt}\n"
                f"**Duration:** {seconds}s\n"
                f"**Resolution:** {resolution} ({orientation})\n"
                f"**Cost:** ${total_cost:.2f} ({cost_breakdown})\n\n"
            )

            if input_reference:
                result_text += f"**Reference Image:** {input_reference}\n"
                if image_description:
                    result_text += f"**Visual Analysis:** GPT-4o Vision enabled ✓\n"

            result_text += (
                f"\n**Saved to:** {output_path}\n"
                f"**Video ID:** {video_id}"
            )

            if input_reference and not auto_analyze_image:
                result_text += "\n\n💡 Tip: Enable auto_analyze_image=True for better product consistency (+$0.01)"

            return [TextContent(type="text", text=result_text)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Error generating video: {str(e)}\n\nCheck your OPENAI_API_KEY and Sora API access."
        )]


# Removed upload_file_to_drive_mcp - Use google-workspace MCP instead:
# mcp__google-workspace__create_drive_file


async def analyze_ugc_image_mcp(image_url: str) -> list[TextContent]:
    """
    Analyze a generated UGC image with GPT-4o Vision to extract details for consistent video generation.

    Use this tool when:
    - Creating Veo video from Nano Banana image (ensures visual consistency)
    - User wants "analysis of generated image"
    - Preparing reference description for UGC video

    Workflow:
    1. generate_nano_banana_image() → image_url
    2. analyze_ugc_image(image_url) → description
    3. generate_veo_ugc_from_image(..., reference_image_description=description)

    Args:
        image_url: URL or local path to generated image (from Nano Banana)

    Returns:
        Detailed description: human appearance, product details, environment, composition

    Cost: ~$0.01 per analysis (GPT-4o Vision)
    """

    try:
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return [TextContent(
                type="text",
                text="❌ Error: OPENAI_API_KEY not found in environment variables.\n\nPlease add it to MARKETING_TEAM/.env file."
            )]

        client = AsyncOpenAI(api_key=api_key)

        # Determine if image_url is local file or URL
        if os.path.exists(image_url):
            # Local file - read and encode to base64
            with open(image_url, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
                image_input = f"data:image/png;base64,{image_data}"
        else:
            # Assume it's a URL
            image_input = image_url

        # Call GPT-4o Vision API with N8n-style prompt
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe what is in the image. Describe the environment and the human who is the focus of the image, as well as what the human is holding."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_input,
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )

        description = response.choices[0].message.content

        result_text = (
            f"✅ Image Analysis Complete!\n\n"
            f"**Model:** GPT-4o Vision\n"
            f"**Cost:** ~$0.01\n\n"
            f"**Description:**\n{description}\n\n"
            f"Use this description as `reference_image_description` parameter in generate_veo_ugc_from_image for maximum visual consistency."
        )

        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Error analyzing image: {str(e)}\n\nCheck that image_url is valid and OPENAI_API_KEY is set."
        )]


async def generate_nano_banana_image_mcp(prompt: str, aspect_ratio: str, filename: str) -> list[TextContent]:
    """
    Generate product image optimized for Veo 3.1 UGC video conversion using Gemini 2.5 Flash Image.

    Use this tool when user requests:
    - "Product image for UGC video"
    - "Nano Banana image"
    - "Generate image for TikTok/Instagram ad"
    - Character-consistent product photography

    NOT for standalone high-quality images - use generate_gpt4o_image instead.

    Model: gemini-2.5-flash-image
    Pricing: $0.039 per image (97.5% cheaper than GPT-4o)

    Optimized for:
    - Character consistency across multiple images
    - Veo 3.1 video input (image-to-video)
    - Lifestyle photography with natural settings
    - Hyper-realistic UGC-style product shots

    Args:
        prompt: Natural language image description (emphasize: human holding product, selfie-style)
        aspect_ratio: "9:16" (default), "16:9", "1:1", etc.
        filename: Output filename (without extension, .png added automatically)

    Returns:
        Image saved to outputs/images/, ready for Veo 3.1 UGC video generation
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


async def generate_veo_text_to_video_mcp(
    prompt: str,
    seconds: str,
    orientation: str,
    resolution: str,
    filename: str,
    negative_prompt: str = None,
    icp: str = None,
    product_features: str = None,
    video_setting: str = None
) -> list[TextContent]:
    """
    Generate video from text prompt using Veo 3.1 text-to-video with native audio.

    Use this tool when user requests:
    - "Create video from text" (no image input)
    - "Generate cinematic video about [topic]"
    - "Professional video ad" (non-UGC style)
    - "Explainer video", "product showcase" (polished, not UGC)

    NOT for UGC ads - use generate_veo_ugc_from_image instead.

    Model: veo-3.1-generate-preview
    Pricing: $0.75 per second
    Native audio: dialogue cues (quotes), sound effects, ambient audio descriptions

    Args:
        prompt: Detailed video description (scene, camera, lighting, audio cues)
        filename: Output filename (no extension)
        orientation: "portrait" (9:16) or "landscape" (16:9)
        seconds: "4", "6", or "8" (default: "8")
        resolution: "720p" or "1080p" (1080p only for 8s)
        negative_prompt: Elements to exclude (optional)

        # ENHANCED PARAMETERS (Optional):
        icp: Ideal Customer Profile for scene composition
        product_features: Features to visualize in video
        video_setting: Environment description

    Returns:
        Video saved to outputs/videos/, cost summary, technical specs

    Cost: $3.00 (4s), $4.50 (6s), $6.00 (8s)
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

        # Enhance prompt with optional parameters
        enhanced_prompt = prompt
        if any([icp, product_features, video_setting]):
            enhancements = []
            if icp:
                enhancements.append(f"Target audience: {icp}")
            if product_features:
                enhancements.append(f"Emphasize: {product_features}")
            if video_setting:
                enhancements.append(f"Setting: {video_setting}")

            enhanced_section = ". ".join(enhancements)
            enhanced_prompt = f"{prompt}\n\nProduction details: {enhanced_section}"
            print(f"   ✨ Using enhanced parameters for targeted messaging", file=sys.stderr)

        # Start generation
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=enhanced_prompt,
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
        output_dir = Path("MARKETING_TEAM/outputs/videos").resolve()
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


async def generate_veo_ugc_from_image_mcp(
    image_path: str,
    ugc_style: str,
    platform: str,
    seconds: str,
    product_name: str,
    filename: str,
    custom_prompt: str = None,
    icp: str = None,
    product_features: str = None,
    video_setting: str = None,
    reference_image_description: str = None,
    auto_analyze_image: bool = True
) -> list[TextContent]:
    """
    Generate authentic UGC-style ad video from product image using Veo 3.1 image-to-video.

    **PRIMARY TOOL for User-Generated Content (UGC) ad creation.**

    Use this tool when user requests:
    - "UGC video", "UGC ad", "UGC-style content"
    - "Testimonial", "demo", "unboxing", "lifestyle" video
    - "TikTok", "Instagram", "Facebook" ad from image
    - "Authentic", "influencer-style", "selfie-style" video
    - "Video from product image" with social media context

    Veo 3.1 required because:
    - Only reliable image-to-video model for authentic UGC quality
    - Native audio generation (dialogue, sound effects, ambient)
    - Superior character/product consistency from image input

    Args:
        image_path: Path to product image (from visual-designer or user)
        ugc_style: "testimonial", "demo", "unboxing", or "lifestyle"
        platform: "tiktok", "instagram", or "facebook" (auto-optimizes specs)
        product_name: Product name for dialogue generation
        filename: Output filename (no extension)
        seconds: "6" or "8" (default: "8") - duration in seconds
        custom_prompt: Override built-in templates (advanced use)

        # ENHANCED PARAMETERS (Optional - for better quality):
        icp: Ideal Customer Profile (e.g., "Young women 25-35, health-conscious")
        product_features: Specific features to highlight (e.g., "Increases shine, lightweight")
        video_setting: Custom environment (e.g., "Bright modern bathroom, morning")
        reference_image_description: Manual override for image description (auto-analyzed if None)
        auto_analyze_image: Automatically analyze image with GPT-4o Vision for maximum visual consistency (default: True, +$0.01)

    Returns:
        Video saved to outputs/videos/, cost summary, platform specs

    Cost: $4.50 (6s) or $6.00 (8s) + $0.01 (automatic analysis)
    Total UGC workflow: $4.55-$6.05 (image + automatic analysis + video)
    Opt-out: Set auto_analyze_image=False for $4.54-$6.04 (testing only)
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

    # UGC prompt templates - Load from memory or use hardcoded fallback
    # Priority: LOADED_UGC_TEMPLATES (from JSON) → Hardcoded UGC_TEMPLATES (fallback)
    if LOADED_UGC_TEMPLATES:
        UGC_TEMPLATES = LOADED_UGC_TEMPLATES
        print(f"   Using {len(UGC_TEMPLATES)} UGC styles from memory/ugc_prompt_templates.json", file=sys.stderr)
    else:
        # FALLBACK: Hardcoded templates if JSON loading failed
        print(f"   Using hardcoded UGC templates (JSON load failed)", file=sys.stderr)
        UGC_TEMPLATES = {
        # ===== ORIGINAL 4 CORE STYLES =====
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
        },

        # ===== EDUCATIONAL & TUTORIAL STYLES =====
        "tutorial": {
            "tiktok": f"""Step-by-step tutorial using {product_name}, hands-only demonstration with quick cuts.
'Here's how to do it!' Fast-paced, educational. Native audio: clear instructions,
upbeat energy, product interaction sounds.""",
            "instagram": f"""Quick how-to guide with {product_name}, hands showing each step clearly.
'Follow along!' Tutorial style, phone camera. Native audio: friendly teaching voice,
step callouts, ambient sounds.""",
            "facebook": f"""Detailed tutorial demonstrating {product_name} use, hands-on instruction.
'Let me teach you the right way.' Native audio: patient explanation, product sounds."""
        },
        "how_to": {
            "tiktok": f"""Quick how-to video, hands using {product_name} to solve a problem.
'Want to know the trick?' Fast solution reveal. Native audio: excited explanation,
'aha moment' reactions.""",
            "instagram": f"""Problem-solving how-to with {product_name}, hands demonstrating the solution.
Natural lighting, casual setting. Native audio: helpful tips, product sounds.""",
            "facebook": f"""Comprehensive how-to guide using {product_name}, detailed demonstration.
'Here's the easiest way.' Native audio: clear instructions, ambient sounds."""
        },
        "quick_tips": {
            "tiktok": f"""Rapid-fire tips using {product_name}, hands showing each hack quickly.
'Tip #1!' Fast cuts, energetic. Native audio: enthusiastic voiceover, quick callouts.""",
            "instagram": f"""Quick tips and tricks with {product_name}, hands demonstrating each one.
Snappy editing, helpful vibe. Native audio: friendly advice, product interaction.""",
            "facebook": f"""Practical tips using {product_name}, hands-on demonstrations.
'Here are my top tips.' Native audio: helpful commentary, ambient sounds."""
        },

        # ===== COMPARISON & TRANSFORMATION STYLES =====
        "before_after": {
            "tiktok": f"""Before and after using {product_name}, split screen showing transformation.
'Watch the difference!' Dramatic reveal. Native audio: excited commentary,
transition sound effects.""",
            "instagram": f"""Transformation with {product_name}, before/after comparison with hands.
'The results speak for themselves.' Native audio: amazed reactions, ambient sounds.""",
            "facebook": f"""Before and after demonstration using {product_name}, clear comparison.
'See the change for yourself.' Native audio: detailed explanation, product sounds."""
        },
        "comparison": {
            "tiktok": f"""Side-by-side comparison, hands testing {product_name} vs alternative.
'Let's compare!' Quick test results. Native audio: objective commentary,
comparison reactions.""",
            "instagram": f"""Product comparison featuring {product_name}, hands showing differences.
'Which one wins?' Fair test, natural setting. Native audio: honest review, ambient sounds.""",
            "facebook": f"""Detailed comparison with {product_name}, hands demonstrating each option.
'Here's what I found.' Native audio: balanced commentary, product interaction."""
        },
        "transformation": {
            "tiktok": f"""Amazing transformation using {product_name}, time-lapse style.
'Wait for it!' Dramatic change reveal. Native audio: buildup music, reveal reactions.""",
            "instagram": f"""Product transformation showcase with {product_name}, hands showing progress.
'The glow up!' Natural lighting. Native audio: excited commentary, ambient sounds.""",
            "facebook": f"""Complete transformation using {product_name}, detailed process.
'From start to finish.' Native audio: narrated journey, product sounds."""
        },

        # ===== EXPERIENCE & REACTION STYLES =====
        "first_time": {
            "tiktok": f"""First time trying {product_name}, hands opening with genuine curiosity.
'Let's try this!' Authentic first reactions. Native audio: surprise reactions,
honest commentary.""",
            "instagram": f"""First impressions of {product_name}, hands exploring product naturally.
'Never tried this before!' Real-time discovery. Native audio: genuine reactions, ambient sounds.""",
            "facebook": f"""First-time user experience with {product_name}, hands testing carefully.
'My honest first impression.' Native audio: unfiltered reactions, product interaction."""
        },
        "reaction": {
            "tiktok": f"""Real reaction to {product_name} results, hands showing outcome with surprise.
'I can't believe it!' Genuine shock. Native audio: spontaneous reactions,
excited exclamations.""",
            "instagram": f"""Authentic reaction using {product_name}, hands revealing results.
'This is insane!' Unscripted response. Native audio: real emotions, ambient sounds.""",
            "facebook": f"""Honest reaction to {product_name}, hands demonstrating while responding.
'Wow, just wow.' Native audio: genuine commentary, product sounds."""
        },
        "challenge": {
            "tiktok": f"""Challenge accepted with {product_name}, hands attempting trending test.
'Let's see if it works!' Competitive energy. Native audio: challenge commentary,
success reactions.""",
            "instagram": f"""Product challenge featuring {product_name}, hands following trend.
'Challenge mode activated!' Fun vibe. Native audio: playful commentary, ambient sounds.""",
            "facebook": f"""Testing {product_name} in a challenge, hands showing each step.
'Can it pass the test?' Native audio: engaging narration, product interaction."""
        },

        # ===== ROUTINE & INTEGRATION STYLES =====
        "morning_routine": {
            "tiktok": f"""Morning routine with {product_name}, hands incorporating product naturally.
'5 AM essentials!' Quick cuts, energetic. Native audio: upbeat morning vibes,
product use sounds.""",
            "instagram": f"""Morning ritual featuring {product_name}, hands showing daily integration.
'Part of my morning.' Golden hour lighting. Native audio: calm morning commentary, ambient sounds.""",
            "facebook": f"""Complete morning routine including {product_name}, hands demonstrating flow.
'How I start my day.' Native audio: relaxed narration, morning ambience."""
        },
        "night_routine": {
            "tiktok": f"""Night routine with {product_name}, hands winding down with product.
'PM ritual!' Cozy lighting, relaxed pace. Native audio: calming commentary,
nighttime ambience.""",
            "instagram": f"""Evening routine featuring {product_name}, hands showing nighttime use.
'Before bed essentials.' Soft lighting. Native audio: soothing voiceover, ambient sounds.""",
            "facebook": f"""Nighttime routine with {product_name}, hands demonstrating evening ritual.
'My nightly must-have.' Native audio: peaceful commentary, product sounds."""
        },
        "grwm": {
            "tiktok": f"""Get ready with me using {product_name}, hands prepping in real-time.
'GRWM!' Fast-paced, energetic. Native audio: upbeat commentary, product application sounds.""",
            "instagram": f"""GRWM featuring {product_name}, hands getting ready naturally.
'Come get ready!' Casual vibe. Native audio: chatty commentary, ambient sounds.""",
            "facebook": f"""Get ready with me showcasing {product_name}, hands in preparation mode.
'Join my routine!' Native audio: friendly narration, product interaction."""
        },
        "day_in_life": {
            "tiktok": f"""Day in the life with {product_name}, hands using product throughout day.
'24 hours!' Quick montage style. Native audio: voiceover narration, ambient sounds.""",
            "instagram": f"""A day with {product_name}, hands showing multiple use moments.
'From AM to PM.' Natural progression. Native audio: casual commentary, environment sounds.""",
            "facebook": f"""Full day featuring {product_name}, hands demonstrating various scenarios.
'How I use it daily.' Native audio: detailed narration, product sounds."""
        },

        # ===== SHOWCASE & FEATURE STYLES =====
        "product_showcase": {
            "tiktok": f"""Product showcase of {product_name}, hands highlighting every angle.
'Check this out!' Dynamic camera movement. Native audio: enthusiastic presentation,
product details.""",
            "instagram": f"""Detailed showcase of {product_name}, hands revealing features slowly.
'Let me show you everything.' Clean aesthetic. Native audio: thorough commentary, ambient sounds.""",
            "facebook": f"""Complete product showcase for {product_name}, hands demonstrating capabilities.
'Full tour!' Native audio: comprehensive explanation, product interaction."""
        },
        "feature_highlight": {
            "tiktok": f"""Highlighting best feature of {product_name}, hands focusing on one aspect.
'This feature though!' Close-up shots. Native audio: excited feature callout,
demonstration sounds.""",
            "instagram": f"""Feature spotlight on {product_name}, hands showing specific benefit.
'My favorite part!' Focused demonstration. Native audio: detailed feature explanation, ambient sounds.""",
            "facebook": f"""Key feature demonstration of {product_name}, hands isolating one element.
'Here's why it's special.' Native audio: feature-focused commentary, product sounds."""
        },
        "results_showcase": {
            "tiktok": f"""Results showcase using {product_name}, hands revealing final outcome.
'The results!' Satisfying reveal. Native audio: amazed commentary,
success reactions.""",
            "instagram": f"""Showing results with {product_name}, hands displaying achievement.
'Look at this!' Natural lighting. Native audio: proud presentation, ambient sounds.""",
            "facebook": f"""Results demonstration using {product_name}, hands proving effectiveness.
'Here's proof it works.' Native audio: results-focused narration, product sounds."""
        },

        # ===== PROBLEM-SOLVING STYLES =====
        "problem_solving": {
            "tiktok": f"""Solving a problem with {product_name}, hands showing pain point then solution.
'Here's the fix!' Quick problem reveal. Native audio: relatable frustration,
solution excitement.""",
            "instagram": f"""Problem to solution using {product_name}, hands demonstrating the answer.
'Finally found the fix!' Natural progression. Native audio: helpful commentary, ambient sounds.""",
            "facebook": f"""Problem-solving demonstration with {product_name}, hands addressing common issue.
'No more struggles!' Native audio: solution-focused narration, product interaction."""
        },
        "hack": {
            "tiktok": f"""Product hack using {product_name}, hands showing unexpected use.
'This hack!' Mind-blown energy. Native audio: excited discovery sharing,
'you need to try this!' reactions.""",
            "instagram": f"""Life hack featuring {product_name}, hands demonstrating clever use.
'Game changer hack!' Creative application. Native audio: enthusiastic hack reveal, ambient sounds.""",
            "facebook": f"""Useful hack with {product_name}, hands showing alternative application.
'Genius hack alert!' Native audio: detailed hack explanation, product sounds."""
        },
        "myth_busting": {
            "tiktok": f"""Myth busting with {product_name}, hands testing common misconception.
'Let's test this myth!' Experiment vibe. Native audio: testing commentary,
myth reveal reactions.""",
            "instagram": f"""Busting myths about {product_name}, hands proving facts.
'Truth time!' Evidence-based demonstration. Native audio: factual commentary, ambient sounds.""",
            "facebook": f"""Myth vs reality using {product_name}, hands showing actual performance.
'Setting the record straight.' Native audio: honest testing narration, product interaction."""
        },

        # ===== HAUL & COLLECTION STYLES =====
        "haul": {
            "tiktok": f"""Product haul featuring {product_name}, hands showing acquisition excitement.
'New haul!' Fast reveals, high energy. Native audio: shopping excitement,
package opening sounds.""",
            "instagram": f"""Shopping haul with {product_name}, hands displaying new purchase.
'What I got!' Satisfying unpack. Native audio: haul commentary, ambient sounds.""",
            "facebook": f"""Product haul showcasing {product_name}, hands revealing shopping results.
'Haul time!' Native audio: purchase story, product sounds."""
        },
        "favorites": {
            "tiktok": f"""Current favorites featuring {product_name}, hands showing top pick.
'My fave!' Quick highlights. Native audio: enthusiastic endorsement,
favorite callouts.""",
            "instagram": f"""Favorite products including {product_name}, hands demonstrating why it's loved.
'All-time favorite!' Genuine appreciation. Native audio: heartfelt commentary, ambient sounds.""",
            "facebook": f"""Top favorites with {product_name}, hands explaining preference.
'Why I love this.' Native audio: detailed favorite explanation, product interaction."""
        },
        "must_haves": {
            "tiktok": f"""Must-have products featuring {product_name}, hands showing essentials.
'You NEED this!' Urgent energy. Native audio: must-have emphasis,
convincing commentary.""",
            "instagram": f"""Essential must-haves with {product_name}, hands displaying necessities.
'Can't live without!' Strong recommendation. Native audio: passionate endorsement, ambient sounds.""",
            "facebook": f"""Must-have demonstration of {product_name}, hands proving necessity.
'Absolute essential!' Native audio: necessity-focused narration, product sounds."""
        },

        # ===== REVIEW & OPINION STYLES =====
        "honest_review": {
            "tiktok": f"""Brutally honest review of {product_name}, hands showing real testing.
'The truth!' No-filter approach. Native audio: candid commentary,
honest reactions.""",
            "instagram": f"""Honest review of {product_name}, hands demonstrating actual experience.
'My real thoughts.' Authentic testing. Native audio: unbiased commentary, ambient sounds.""",
            "facebook": f"""Comprehensive honest review using {product_name}, hands showing pros and cons.
'Here's what you should know.' Native audio: balanced review narration, product interaction."""
        },
        "worth_it": {
            "tiktok": f"""Is it worth it? Testing {product_name}, hands showing value assessment.
'Worth the hype?' Value test. Native audio: skeptical then convinced commentary,
verdict reactions.""",
            "instagram": f"""Worth it or not with {product_name}, hands evaluating value.
'Let's find out!' Fair assessment. Native audio: value-focused commentary, ambient sounds.""",
            "facebook": f"""Worth it review of {product_name}, hands demonstrating cost-benefit.
'My verdict.' Native audio: value analysis narration, product sounds."""
        },
        "hype_test": {
            "tiktok": f"""Testing the hype around {product_name}, hands putting claims to test.
'Does it live up?' Skeptical energy. Native audio: testing commentary,
hype validation reactions.""",
            "instagram": f"""Hype test for {product_name}, hands verifying viral claims.
'Is the hype real?' Honest testing. Native audio: fair assessment commentary, ambient sounds.""",
            "facebook": f"""Testing {product_name} hype, hands demonstrating actual performance.
'Separating hype from reality.' Native audio: objective testing narration, product interaction."""
        },

        # ===== INSTALLATION & SETUP STYLES =====
        "setup": {
            "tiktok": f"""Quick setup of {product_name}, hands showing easy installation.
'Setup in seconds!' Fast assembly. Native audio: setup instructions,
completion satisfaction.""",
            "instagram": f"""Setting up {product_name}, hands demonstrating installation process.
'Easy setup!' Step-by-step. Native audio: helpful setup guide, ambient sounds.""",
            "facebook": f"""Complete setup guide for {product_name}, hands showing full installation.
'How to set it up.' Native audio: detailed setup narration, product sounds."""
        },
        "installation": {
            "tiktok": f"""Installing {product_name}, hands showing mounting/assembly.
'Installation time!' DIY energy. Native audio: installation commentary,
tool sounds.""",
            "instagram": f"""Installation process with {product_name}, hands demonstrating placement.
'Let me install this!' Hands-on approach. Native audio: installation tips, ambient sounds.""",
            "facebook": f"""Full installation of {product_name}, hands showing complete process.
'Installation guide.' Native audio: thorough installation narration, product interaction."""
        },
        "maintenance": {
            "tiktok": f"""Maintaining {product_name}, hands showing care routine.
'Keep it fresh!' Maintenance tips. Native audio: care instructions,
cleaning sounds.""",
            "instagram": f"""Product maintenance for {product_name}, hands demonstrating upkeep.
'How I care for it.' Regular maintenance. Native audio: care commentary, ambient sounds.""",
            "facebook": f"""Maintenance guide for {product_name}, hands showing proper care.
'Maintenance made easy.' Native audio: care routine narration, product sounds."""
        },

        # ===== TREND & VIRAL STYLES =====
        "trending": {
            "tiktok": f"""Trending use of {product_name}, hands following viral format.
'On trend!' Viral energy. Native audio: trend audio overlay,
participation excitement.""",
            "instagram": f"""Trending content with {product_name}, hands joining popular format.
'Hopping on the trend!' Current vibe. Native audio: trend-aware commentary, ambient sounds.""",
            "facebook": f"""Trending demonstration of {product_name}, hands showing popular use.
'What's trending.' Native audio: trend explanation narration, product interaction."""
        },
        "viral": {
            "tiktok": f"""Viral moment with {product_name}, hands recreating viral sensation.
'Going viral!' High energy. Native audio: viral audio snippet,
excited participation.""",
            "instagram": f"""Viral product moment featuring {product_name}, hands showing why it's viral.
'Viral for a reason!' Shareable content. Native audio: viral context commentary, ambient sounds.""",
            "facebook": f"""Viral demonstration using {product_name}, hands explaining viral appeal.
'Why everyone's talking about this.' Native audio: viral analysis narration, product sounds."""
        },
        "duet_response": {
            "tiktok": f"""Duet response using {product_name}, hands showing reaction/addition.
'Duet this!' Interactive energy. Native audio: response commentary,
interaction sounds.""",
            "instagram": f"""Response video with {product_name}, hands adding to conversation.
'My take!' Conversation participation. Native audio: response commentary, ambient sounds.""",
            "facebook": f"""Video response featuring {product_name}, hands demonstrating answer.
'Here's my response.' Native audio: response narration, product interaction."""
        },

        # ===== SEASONAL & OCCASION STYLES =====
        "seasonal": {
            "tiktok": f"""Seasonal use of {product_name}, hands showing timely application.
'Perfect for [season]!' Seasonal energy. Native audio: seasonal commentary,
relevant ambience.""",
            "instagram": f"""Seasonal showcase with {product_name}, hands demonstrating seasonal fit.
'[Season] essential!' Time-appropriate. Native audio: seasonal context, ambient sounds.""",
            "facebook": f"""Seasonal demonstration using {product_name}, hands showing occasion use.
'Just in time for [season].' Native audio: seasonal narration, product sounds."""
        },
        "holiday": {
            "tiktok": f"""Holiday special featuring {product_name}, hands showing festive use.
'Holiday must-have!' Festive vibes. Native audio: holiday excitement,
celebration sounds.""",
            "instagram": f"""Holiday content with {product_name}, hands demonstrating festive application.
'Holiday edition!' Celebratory mood. Native audio: holiday commentary, ambient sounds.""",
            "facebook": f"""Holiday demonstration using {product_name}, hands showing seasonal gift.
'Perfect holiday gift!' Native audio: festive narration, product interaction."""
        },
        "gift_guide": {
            "tiktok": f"""Gift guide featuring {product_name}, hands showing perfect gift.
'Gift idea!' Gifting excitement. Native audio: gift suggestion commentary,
wrapping sounds.""",
            "instagram": f"""Gift recommendation with {product_name}, hands presenting as ideal gift.
'Great gift alert!' Thoughtful presentation. Native audio: gift commentary, ambient sounds.""",
            "facebook": f"""Gift guide showcasing {product_name}, hands demonstrating gift appeal.
'Gift guide favorite.' Native audio: gift explanation narration, product sounds."""
        },

        # ===== BEHIND-THE-SCENES & AUTHENTIC STYLES =====
        "behind_scenes": {
            "tiktok": f"""Behind the scenes with {product_name}, hands showing real usage off-camera.
'BTS!' Authentic peek. Native audio: candid commentary,
real-life sounds.""",
            "instagram": f"""Behind-the-scenes featuring {product_name}, hands in natural workflow.
'What you don't see!' Raw authenticity. Native audio: honest BTS commentary, ambient sounds.""",
            "facebook": f"""BTS demonstration with {product_name}, hands showing actual use.
'The real story.' Native audio: authentic narration, product interaction."""
        },
        "real_talk": {
            "tiktok": f"""Real talk about {product_name}, hands showing while being honest.
'Let's be real!' No filter energy. Native audio: candid honest commentary,
real reactions.""",
            "instagram": f"""Real talk featuring {product_name}, hands demonstrating with honesty.
'The honest truth!' Authentic conversation. Native audio: real talk commentary, ambient sounds.""",
            "facebook": f"""Real talk review of {product_name}, hands showing genuine experience.
'Being completely honest.' Native audio: truthful narration, product sounds."""
        },
        "unpopular_opinion": {
            "tiktok": f"""Unpopular opinion on {product_name}, hands showing controversial take.
'Hot take!' Bold energy. Native audio: confident opinion sharing,
debate-worthy reactions.""",
            "instagram": f"""Unpopular opinion about {product_name}, hands demonstrating unique view.
'Might be unpopular but...' Honest perspective. Native audio: opinion commentary, ambient sounds.""",
            "facebook": f"""Unpopular opinion review using {product_name}, hands proving point.
'My unpopular take.' Native audio: opinion explanation narration, product interaction."""
        },

        # ===== EDUCATIONAL DEEP-DIVE STYLES =====
        "explainer": {
            "tiktok": f"""Quick explainer on {product_name}, hands showing how it works.
'Let me explain!' Educational energy. Native audio: clear explanation,
teaching tone.""",
            "instagram": f"""Explainer video for {product_name}, hands demonstrating mechanics.
'Here's how!' Educational approach. Native audio: informative commentary, ambient sounds.""",
            "facebook": f"""Detailed explainer using {product_name}, hands showing inner workings.
'Understanding [product].' Native audio: thorough explanation narration, product sounds."""
        },
        "science_behind": {
            "tiktok": f"""The science behind {product_name}, hands showing technical aspects.
'Science time!' Educational but fun. Native audio: simplified science explanation,
'aha' reactions.""",
            "instagram": f"""Science explanation for {product_name}, hands demonstrating principles.
'The science!' Informative content. Native audio: educational commentary, ambient sounds.""",
            "facebook": f"""Science behind {product_name}, hands showing technical demonstration.
'How it actually works.' Native audio: scientific narration, product interaction."""
        },
        "ingredients_breakdown": {
            "tiktok": f"""Ingredients breakdown of {product_name}, hands showing what's inside.
'What's in it?' Transparency focus. Native audio: ingredient callouts,
education commentary.""",
            "instagram": f"""Ingredient analysis for {product_name}, hands highlighting components.
'Breaking down ingredients!' Informed content. Native audio: ingredient commentary, ambient sounds.""",
            "facebook": f"""Complete ingredients breakdown using {product_name}, hands showing details.
'Ingredient deep dive.' Native audio: ingredient explanation narration, product sounds."""
        },

        # ===== SPECIALTY & NICHE STYLES =====
        "asmr": {
            "tiktok": f"""ASMR unboxing of {product_name}, hands moving slowly with product.
'ASMR vibes!' Whisper-quiet energy. Native audio: soft whispers, product sounds amplified,
crinkling, tapping.""",
            "instagram": f"""ASMR product experience with {product_name}, hands exploring textures.
'Satisfying sounds!' Gentle movements. Native audio: whispered commentary, enhanced product sounds.""",
            "facebook": f"""ASMR demonstration using {product_name}, hands creating relaxing sounds.
'ASMR edition.' Native audio: soft-spoken narration, amplified product interaction."""
        },
        "pov": {
            "tiktok": f"""POV using {product_name}, hands showing first-person perspective.
'POV:' Immersive angle. Native audio: situational commentary,
first-person reactions.""",
            "instagram": f"""POV content with {product_name}, hands from user perspective.
'POV experience!' Personal viewpoint. Native audio: POV narration, ambient sounds.""",
            "facebook": f"""POV demonstration of {product_name}, hands showing personal angle.
'From my POV.' Native audio: first-person narration, product interaction."""
        },
        "satisfying": {
            "tiktok": f"""Oddly satisfying {product_name} moment, hands creating perfect action.
'So satisfying!' Perfect execution. Native audio: satisfying sound emphasis,
completion reactions.""",
            "instagram": f"""Satisfying content featuring {product_name}, hands in perfect motion.
'Satisfying to watch!' Visual pleasure. Native audio: satisfaction commentary, ambient sounds.""",
            "facebook": f"""Satisfying demonstration with {product_name}, hands showing perfect result.
'Perfectly satisfying.' Native audio: satisfaction narration, product sounds."""
        },
        "minimalist": {
            "tiktok": f"""Minimalist approach to {product_name}, hands showing simple use.
'Keep it simple!' Clean aesthetic. Native audio: minimal commentary,
essential sounds only.""",
            "instagram": f"""Minimalist showcase of {product_name}, hands in clean presentation.
'Less is more!' Simple elegance. Native audio: quiet commentary, ambient sounds.""",
            "facebook": f"""Minimalist demonstration using {product_name}, hands showing essentials.
'Minimalist lifestyle.' Native audio: simple narration, product sounds."""
        },
        "luxury": {
            "tiktok": f"""Luxury unboxing of {product_name}, hands treating product preciously.
'Luxury vibes!' Premium feel. Native audio: appreciative commentary,
elegant ambience.""",
            "instagram": f"""Luxury experience with {product_name}, hands showcasing premium quality.
'Luxury edition!' High-end presentation. Native audio: sophisticated commentary, ambient sounds.""",
            "facebook": f"""Luxury demonstration of {product_name}, hands highlighting premium features.
'Premium experience.' Native audio: luxury-focused narration, product interaction."""
        },
        "budget_friendly": {
            "tiktok": f"""Budget-friendly option {product_name}, hands showing affordable value.
'Budget win!' Value excitement. Native audio: price-conscious commentary,
savings celebration.""",
            "instagram": f"""Budget-friendly showcase of {product_name}, hands demonstrating affordability.
'Affordable find!' Value content. Native audio: budget commentary, ambient sounds.""",
            "facebook": f"""Budget-friendly review using {product_name}, hands proving value.
'Won't break the bank.' Native audio: value-focused narration, product sounds."""
        }
        }  # End of hardcoded UGC_TEMPLATES fallback

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

        # Automatic image analysis if not provided and enabled
        if reference_image_description is None and auto_analyze_image:
            print(f"🔍 Automatically analyzing image for visual consistency...", file=sys.stderr)
            try:
                analysis_result = await analyze_ugc_image_mcp(image_path)
                # Extract description from TextContent response
                if analysis_result and len(analysis_result) > 0:
                    result_text = analysis_result[0].text
                    # Parse description after "**Description:**\n"
                    if "**Description:**" in result_text:
                        reference_image_description = result_text.split("**Description:**\n")[1].split("\n\n")[0]
                        print(f"✅ Image analysis complete (+$0.01)", file=sys.stderr)
                        print(f"📝 Extracted description: {reference_image_description[:100]}...", file=sys.stderr)
            except Exception as e:
                print(f"⚠️  Image analysis failed, continuing without: {str(e)}", file=sys.stderr)
                # Continue without description (graceful degradation)

        # Build comprehensive N8n-style prompt with enhanced parameters
        def build_comprehensive_prompt(retry_attempt=0):
            """Build production-quality prompt using N8n workflow patterns"""
            if custom_prompt:
                return custom_prompt

            # Start with base template
            base_prompt = UGC_TEMPLATES[ugc_style][platform]

            # Build comprehensive N8n-style system prompt
            system_instructions = []

            # QUALITY REQUIREMENTS (N8n pattern)
            system_instructions.append(
                "VIDEO QUALITY REQUIREMENTS:\n"
                "- Hyper-realistic UGC aesthetic with natural imperfections\n"
                "- Handheld camera feel (slight shake, not stabilized)\n"
                "- Natural lighting (window light, not studio)\n"
                "- Authentic reactions and casual delivery\n"
                "- Native audio (dialogue, ambient sounds, product sounds)\n"
                "- Product clearly visible throughout (70% of frames)\n"
                "- Matches reference image exactly if provided"
            )

            # TARGET AUDIENCE & MESSAGING (if provided)
            if icp:
                system_instructions.append(
                    f"\nTARGET AUDIENCE:\n"
                    f"{icp}\n"
                    f"- Scene, language, and setting must resonate with this demographic\n"
                    f"- Use appropriate tone, pacing, and visual style for audience\n"
                    f"- Show relatable use case scenarios"
                )

            # PRODUCT FEATURES (if provided)
            if product_features:
                system_instructions.append(
                    f"\nPRODUCT FEATURES TO HIGHLIGHT:\n"
                    f"{product_features}\n"
                    f"- Weave features into natural conversation/demonstration\n"
                    f"- Show features visually when possible\n"
                    f"- Avoid overly promotional language (stay authentic)"
                )

            # VIDEO SETTING (if provided)
            if video_setting:
                system_instructions.append(
                    f"\nVIDEO SETTING:\n"
                    f"{video_setting}\n"
                    f"- Match lighting, environment, and atmosphere exactly\n"
                    f"- Maintain casual, lived-in feel (not staged)"
                )

            # VISUAL CONSISTENCY (if provided)
            if reference_image_description:
                system_instructions.append(
                    f"\nVISUAL CONSISTENCY REQUIREMENTS:\n"
                    f"{reference_image_description}\n"
                    f"- Product packaging must match reference image 100%\n"
                    f"- Colors, branding, and design elements identical\n"
                    f"- Maintain visual continuity from reference image"
                )

            # RETRY WORDING VARIATIONS (keep comprehensive, change approach)
            if retry_attempt == 0:
                # ATTEMPT 1: Original comprehensive prompt
                execution_approach = (
                    "\n\nEXECUTION APPROACH:\n"
                    "- Show authentic user interaction with product\n"
                    "- Capture genuine reactions and enthusiasm\n"
                    "- Natural dialogue and conversational tone\n"
                    "- Demonstrate product benefits through real use"
                )
            elif retry_attempt == 1:
                # ATTEMPT 2: Reword with "hands-only demonstration" focus
                execution_approach = (
                    "\n\nEXECUTION APPROACH:\n"
                    "- FOCUS: Close-up hands-only product demonstration\n"
                    "- Voice narration off-camera with excited energy\n"
                    "- Show product handling, opening, and interaction\n"
                    "- Emphasize tactile elements and product details\n"
                    "- Natural hand movements demonstrate features and benefits"
                )
            else:
                # ATTEMPT 3: Reword with "product-centric tutorial" focus
                execution_approach = (
                    "\n\nEXECUTION APPROACH:\n"
                    "- FOCUS: Product-centric tutorial with hands interaction\n"
                    "- Enthusiastic voice-over provides context and excitement\n"
                    "- Highlight package design, branding, and product presentation\n"
                    "- Show step-by-step product use in casual environment\n"
                    "- Maintain authentic, relatable demonstration style"
                )

            # Combine all sections with comprehensive prompts for ALL attempts
            if system_instructions:
                comprehensive_prompt = (
                    f"{base_prompt}\n\n"
                    f"{'=' * 60}\n"
                    f"PRODUCTION SYSTEM PROMPT (N8n Enhanced)\n"
                    f"{'=' * 60}\n\n"
                    + "\n".join(system_instructions)
                    + execution_approach
                    + "\n\nREMINDER: Maintain all quality requirements, target audience alignment, "
                    "and product feature integration throughout the execution."
                )
            else:
                comprehensive_prompt = base_prompt + execution_approach

            return comprehensive_prompt

        print(f"🎬 Starting Veo 3.1 image-to-video UGC generation...", file=sys.stderr)
        print(f"   Style: {ugc_style} | Platform: {platform} | Duration: {seconds}s", file=sys.stderr)
        if any([icp, product_features, video_setting, reference_image_description]):
            print(f"   ✨ Using enhanced N8n-style comprehensive prompts", file=sys.stderr)

        # Create image parameter using correct Google GenAI format (imageBytes in camelCase)
        image_param = types.Image(
            imageBytes=image_bytes,
            mimeType=mime_type
        )

        # 3-RETRY LOGIC: Automatically retry with prompt variations if blocked
        max_retries = 3
        operation = None
        poll_count = 0

        for retry_attempt in range(max_retries):
            # Build prompt with retry variation
            final_prompt = build_comprehensive_prompt(retry_attempt)

            if retry_attempt > 0:
                print(f"\n🔄 Retry attempt {retry_attempt + 1}/{max_retries} with modified prompt...", file=sys.stderr)

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
            if hasattr(operation.response, 'generated_videos') and operation.response.generated_videos:
                # SUCCESS! Video generated
                if retry_attempt > 0:
                    print(f"✅ Success on retry attempt {retry_attempt + 1}", file=sys.stderr)
                break
            else:
                # BLOCKED by safety filters
                if retry_attempt < max_retries - 1:
                    print(f"⚠️  Attempt {retry_attempt + 1} blocked by safety filters, retrying with variation...", file=sys.stderr)
                else:
                    # Final attempt failed
                    return [TextContent(
                        type="text",
                        text=f"❌ Video generation blocked by safety filters after {max_retries} attempts (no charge)\n\n"
                             f"Tried variations:\n"
                             f"1. Original prompt with full details\n"
                             f"2. Hands-only focus (no face)\n"
                             f"3. Product-centric close-up\n\n"
                             f"Suggestion: Try different ugc_style ('demo', 'unboxing', 'lifestyle') or simplify enhanced parameters."
                    )]

        # If we get here, operation succeeded (either first try or after retry)

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

        # Calculate total cost including automatic analysis
        total_cost = cost
        analysis_cost_note = ""
        if auto_analyze_image and reference_image_description:
            total_cost += 0.01
            analysis_cost_note = " + $0.01 (automatic image analysis)"

        # Build visual consistency note
        visual_note = "- Visual consistency: GPT-4o analyzed reference image\n" if reference_image_description else ""

        result_text = (
            f"✅ UGC Video Generated Successfully!\n\n"
            f"**Model:** veo-3.1-generate-preview\n"
            f"**Style:** {ugc_style} ({platform} optimized)\n"
            f"**Duration:** {seconds} seconds\n"
            f"**Cost:** ${total_cost:.2f} (Veo 3.1{analysis_cost_note})\n"
            f"**Resolution:** {config_settings['resolution']} {config_settings['aspect_ratio']}\n"
            f"**Audio:** Native dialogue + sound effects + ambient\n"
            f"**Generation time:** {poll_count * 10}s\n\n"
            f"**Saved to:** {output_path}\n\n"
            f"✨ UGC Characteristics:\n"
            f"- Handheld camera aesthetic\n"
            f"- Natural lighting and setting\n"
            f"- Authentic reactions and dialogue\n"
            f"- Native audio (not added post)\n"
            f"{visual_note}"
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
        output_dir = Path("MARKETING_TEAM/outputs/videos").resolve()
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
            description="Generate video using OpenAI's Sora-2 model ($0.10/second, 720p) - supports text-to-video, image-to-video with GPT-4o Vision analysis, AND 50 UGC styles",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Optional: Custom video prompt. Can be used ALONE (manual prompt) OR WITH ugc_style (adds custom instructions to UGC template)."
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
                    },
                    "input_reference": {
                        "type": "string",
                        "description": "Optional: path to reference image for image-to-video generation"
                    },
                    "auto_analyze_image": {
                        "type": "boolean",
                        "description": "Analyze image with GPT-4o Vision for better consistency (default: false, +$0.01)",
                        "default": False
                    },
                    "ugc_style": {
                        "type": "string",
                        "description": "Optional: UGC style (testimonial, demo, unboxing, lifestyle, tutorial, how_to, quick_tips, before_after, comparison, transformation, first_time, reaction, challenge, morning_routine, night_routine, grwm, day_in_life, product_showcase, feature_highlight, results_showcase, problem_solving, hack, myth_busting, haul, favorites, must_haves, honest_review, worth_it, hype_test, setup, installation, maintenance, trending, viral, duet_response, seasonal, holiday, gift_guide, behind_scenes, real_talk, unpopular_opinion, explainer, science_behind, ingredients_breakdown, asmr, pov, satisfying, minimalist, luxury, budget_friendly). Automatically builds authentic UGC prompt. Can be combined with 'prompt' parameter to add custom instructions."
                    },
                    "product_name": {
                        "type": "string",
                        "description": "Required if ugc_style used: Product name for UGC video"
                    },
                    "platform": {
                        "type": "string",
                        "description": "Platform optimization: tiktok, instagram, facebook (default: tiktok)",
                        "enum": ["tiktok", "instagram", "facebook"],
                        "default": "tiktok"
                    },
                    "icp": {
                        "type": "string",
                        "description": "Optional: Ideal Customer Profile (e.g., 'Young women 25-35, health-conscious')"
                    },
                    "product_features": {
                        "type": "string",
                        "description": "Optional: Product features to highlight (e.g., 'Increases energy, natural ingredients')"
                    },
                    "video_setting": {
                        "type": "string",
                        "description": "Optional: Custom environment (e.g., 'Bright modern kitchen, morning light')"
                    }
                },
                "required": ["filename"]
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
            name="analyze_ugc_image",
            description="Analyze UGC image with GPT-4o Vision for consistent Veo video generation - ~$0.01/analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string",
                        "description": "URL or local path to generated image (from Nano Banana or GPT-4o)"
                    }
                },
                "required": ["image_url"]
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
                    },
                    "icp": {
                        "type": "string",
                        "description": "Optional: Ideal Customer Profile for scene composition"
                    },
                    "product_features": {
                        "type": "string",
                        "description": "Optional: Features to visualize in video"
                    },
                    "video_setting": {
                        "type": "string",
                        "description": "Optional: Environment description"
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
                        "description": f"UGC style - {len(AVAILABLE_UGC_STYLES)} styles available from memory/ugc_prompt_templates.json",
                        "enum": AVAILABLE_UGC_STYLES,  # Dynamically loaded from JSON!
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
                    },
                    "icp": {
                        "type": "string",
                        "description": "Optional: Ideal Customer Profile (e.g., 'Young women 25-35, health-conscious')"
                    },
                    "product_features": {
                        "type": "string",
                        "description": "Optional: Specific features to highlight (e.g., 'Increases shine, lightweight')"
                    },
                    "video_setting": {
                        "type": "string",
                        "description": "Optional: Custom environment (e.g., 'Bright modern bathroom, morning')"
                    },
                    "reference_image_description": {
                        "type": "string",
                        "description": "Optional: Manual override for image description (auto-analyzed if None)"
                    },
                    "auto_analyze_image": {
                        "type": "boolean",
                        "description": "Automatically analyze image with GPT-4o Vision for maximum visual consistency (default: true, +$0.01)",
                        "default": True
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
                prompt=arguments.get("prompt"),
                seconds=arguments.get("seconds", "4"),
                orientation=arguments.get("orientation", "landscape"),
                filename=arguments["filename"],
                input_reference=arguments.get("input_reference"),
                auto_analyze_image=arguments.get("auto_analyze_image", False),
                # NEW UGC parameters:
                ugc_style=arguments.get("ugc_style"),
                product_name=arguments.get("product_name"),
                platform=arguments.get("platform", "tiktok"),
                icp=arguments.get("icp"),
                product_features=arguments.get("product_features"),
                video_setting=arguments.get("video_setting")
            )

        elif name == "generate_nano_banana_image":
            return await generate_nano_banana_image_mcp(
                prompt=arguments["prompt"],
                aspect_ratio=arguments.get("aspect_ratio", "9:16"),
                filename=arguments["filename"]
            )

        elif name == "analyze_ugc_image":
            return await analyze_ugc_image_mcp(
                image_url=arguments["image_url"]
            )

        elif name == "generate_veo_text_to_video":
            return await generate_veo_text_to_video_mcp(
                prompt=arguments["prompt"],
                seconds=arguments.get("seconds", "8"),
                orientation=arguments.get("orientation", "portrait"),
                resolution=arguments.get("resolution", "720p"),
                filename=arguments["filename"],
                negative_prompt=arguments.get("negative_prompt"),
                icp=arguments.get("icp"),
                product_features=arguments.get("product_features"),
                video_setting=arguments.get("video_setting")
            )

        elif name == "generate_veo_ugc_from_image":
            return await generate_veo_ugc_from_image_mcp(
                image_path=arguments["image_path"],
                ugc_style=arguments.get("ugc_style", "testimonial"),
                platform=arguments.get("platform", "tiktok"),
                seconds=arguments.get("seconds", "8"),
                product_name=arguments["product_name"],
                filename=arguments["filename"],
                custom_prompt=arguments.get("custom_prompt"),
                icp=arguments.get("icp"),
                product_features=arguments.get("product_features"),
                video_setting=arguments.get("video_setting"),
                reference_image_description=arguments.get("reference_image_description"),
                auto_analyze_image=arguments.get("auto_analyze_image", True)
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
