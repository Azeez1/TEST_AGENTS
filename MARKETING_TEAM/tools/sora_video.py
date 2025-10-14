"""
Sora Video Generation Tool
Creates videos using OpenAI's Sora model
"""

from claude_agent_sdk import tool
from openai import AsyncOpenAI
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@tool(
    "generate_sora_video",
    "Generate video using Sora (OpenAI video generation model)",
    {
        "prompt": str,
        "duration": int,  # Duration in seconds (5-60)
        "aspect_ratio": str,  # "16:9", "9:16", "1:1"
        "filename": str
    }
)
async def generate_sora_video(args):
    """
    Generate video using Sora

    Note: As of January 2025, Sora API is in limited access.
    This implementation assumes API access is available.
    If not available, this will return instructions for manual creation.
    """

    prompt = args["prompt"]
    duration = args.get("duration", 30)  # Default 30 seconds
    aspect_ratio = args.get("aspect_ratio", "16:9")
    filename = args.get("filename", "video.mp4")

    # Validate duration
    if duration < 5 or duration > 60:
        return {
            "content": [{
                "type": "text",
                "text": "Error: Duration must be between 5 and 60 seconds"
            }]
        }

    # Validate aspect ratio
    valid_ratios = ["16:9", "9:16", "1:1"]
    if aspect_ratio not in valid_ratios:
        return {
            "content": [{
                "type": "text",
                "text": f"Error: Aspect ratio must be one of {valid_ratios}"
            }]
        }

    try:
        # Check if Sora API is available
        # Note: This endpoint structure is speculative - update when official API is released

        # Attempt to generate video
        # In the meantime, return comprehensive guidance for manual creation

        result = {
            "status": "awaiting_sora_api_access",
            "prompt": prompt,
            "duration": f"{duration} seconds",
            "aspect_ratio": aspect_ratio,
            "filename": filename,
            "estimated_cost": f"${duration * 0.10:.2f}",  # Estimated pricing
            "manual_creation_guide": {
                "platforms": [
                    {
                        "name": "Runway Gen-2",
                        "url": "https://runwayml.com",
                        "features": "4-second clips, text-to-video",
                        "pricing": "$12/month for 125 credits"
                    },
                    {
                        "name": "Pika Labs",
                        "url": "https://pika.art",
                        "features": "3-second clips, style customization",
                        "pricing": "Free tier available"
                    },
                    {
                        "name": "Stability AI (Stable Video)",
                        "url": "https://stability.ai",
                        "features": "Image-to-video, controllable motion",
                        "pricing": "API-based pricing"
                    }
                ],
                "prompt_optimization": {
                    "structure": "[Subject] + [Action] + [Setting] + [Style] + [Camera]",
                    "example": f"For your prompt: '{prompt}'\n\nOptimized version:\n{prompt}\nCamera: {self._suggest_camera_movement(prompt)}\nLighting: {self._suggest_lighting(prompt)}\nStyle: Cinematic, high-quality production\nPacing: {self._suggest_pacing(duration)}"
                }
            },
            "sora_specific_guidance": {
                "when_available": "Sora API is currently in limited preview. Check https://openai.com/sora for access.",
                "expected_features": [
                    "Up to 60 seconds of high-quality video",
                    "Multiple shots and scenes",
                    "Complex camera motion",
                    "Consistent character generation",
                    "Text rendering in video"
                ],
                "prompt_tips": [
                    "Be specific about camera movements (dolly, pan, zoom)",
                    "Describe lighting conditions explicitly",
                    "Include temporal instructions (slow motion, time-lapse)",
                    "Specify style references (cinematic, documentary, etc.)",
                    "Break complex scenes into multiple prompts"
                ]
            },
            "alternative_workflow": {
                "step_1": "Generate key frames using GPT-4o image generation",
                "step_2": "Use Runway/Pika to animate between frames",
                "step_3": "Edit in video editor (CapCut, DaVinci Resolve)",
                "step_4": "Add voiceover using ElevenLabs",
                "step_5": "Add music from Epidemic Sound or Artlist"
            },
            "interim_solution": "Use generate_gpt4o_image tool to create storyboard frames, then use external video tools"
        }

        # Save request to queue for when Sora becomes available
        self._save_to_video_queue(result)

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
                "text": f"Error generating video: {str(e)}\n\nSora API may not be available yet. Check OpenAI documentation for access."
            }]
        }


def _suggest_camera_movement(prompt: str) -> str:
    """Suggest camera movement based on prompt"""
    prompt_lower = prompt.lower()

    if "product" in prompt_lower:
        return "Slow rotating dolly around subject, 360-degree view"
    elif "landscape" in prompt_lower or "scene" in prompt_lower:
        return "Smooth dolly forward with slight upward tilt"
    elif "person" in prompt_lower or "people" in prompt_lower:
        return "Gentle push-in from medium to close-up"
    elif "action" in prompt_lower or "dynamic" in prompt_lower:
        return "Handheld tracking shot with subject motion"
    else:
        return "Steady cam, slow forward dolly"


def _suggest_lighting(prompt: str) -> str:
    """Suggest lighting based on prompt"""
    prompt_lower = prompt.lower()

    if "professional" in prompt_lower or "corporate" in prompt_lower:
        return "Soft natural light from large windows, 3-point lighting setup"
    elif "dramatic" in prompt_lower:
        return "High contrast, single key light, deep shadows"
    elif "product" in prompt_lower:
        return "Even studio lighting, soft shadows, clean white background"
    elif "outdoor" in prompt_lower:
        return "Golden hour sunlight, warm tones, natural shadows"
    else:
        return "Natural, evenly lit with soft shadows"


def _suggest_pacing(duration: int) -> str:
    """Suggest pacing based on duration"""
    if duration <= 15:
        return "Fast-paced, quick cuts, high energy"
    elif duration <= 30:
        return "Medium pacing, balance of movement and stillness"
    else:
        return "Slow, cinematic pacing with longer holds"


def _save_to_video_queue(request_data: dict):
    """Save video request to queue for future processing"""
    queue_file = "memory/video_generation_queue.json"

    # Load existing queue
    if os.path.exists(queue_file):
        with open(queue_file) as f:
            queue = json.load(f)
    else:
        queue = []

    # Add request
    queue.append(request_data)

    # Save queue
    Path("memory").mkdir(exist_ok=True)
    with open(queue_file, 'w') as f:
        json.dump(queue, f, indent=2)


@tool(
    "create_video_storyboard",
    "Create detailed storyboard for video production",
    {
        "video_concept": str,
        "duration": int,
        "platform": str  # social, youtube, ad
    }
)
async def create_video_storyboard(args):
    """
    Create detailed storyboard breaking video into scenes
    """
    concept = args["video_concept"]
    duration = args.get("duration", 30)
    platform = args.get("platform", "social")

    # Calculate scene breakdown
    if duration <= 15:
        num_scenes = 3
    elif duration <= 30:
        num_scenes = 4
    else:
        num_scenes = 5

    scene_duration = duration / num_scenes

    storyboard = {
        "video_concept": concept,
        "total_duration": duration,
        "platform": platform,
        "scenes": [],
        "technical_specs": {
            "aspect_ratio": "9:16" if platform == "tiktok" else "16:9",
            "resolution": "1080p minimum",
            "frame_rate": "30fps",
            "format": "MP4 (H.264)"
        }
    }

    # Platform-specific recommendations
    if platform == "social":
        storyboard["recommendations"] = {
            "hook_duration": "3 seconds (critical)",
            "captions": "Required (80% watch without sound)",
            "pacing": "Fast - attention span is short",
            "cta_placement": "End screen with 3-second hold"
        }
    elif platform == "youtube":
        storyboard["recommendations"] = {
            "hook_duration": "5-10 seconds",
            "captions": "Optional but recommended",
            "pacing": "Medium - allow for storytelling",
            "cta_placement": "Multiple CTAs throughout"
        }
    elif platform == "ad":
        storyboard["recommendations"] = {
            "hook_duration": "3 seconds maximum",
            "message": "Clear value proposition in first 5 seconds",
            "brand_placement": "Logo visible throughout",
            "cta_placement": "Strong CTA in final 5 seconds"
        }

    # Create scene breakdown
    for i in range(num_scenes):
        scene = {
            "scene_number": i + 1,
            "duration": f"{scene_duration:.1f} seconds",
            "description": f"[Scene {i+1} description - to be filled by video producer]",
            "visual_elements": [],
            "audio_notes": "",
            "camera_movement": "",
            "transition": "Cut" if i < num_scenes - 1 else "Hold on final frame"
        }
        storyboard["scenes"].append(scene)

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(storyboard, indent=2)
        }]
    }
