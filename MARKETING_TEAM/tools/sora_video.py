"""
Sora Video Generation Tool
Creates videos using OpenAI's Sora model

Note: As of January 2025, Sora API access via OpenAI platform.openai.com is public.
This implementation uses direct HTTP requests until the Python SDK adds native support.
"""

from claude_agent_sdk import tool
from openai import AsyncOpenAI
import httpx
import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Import Google Drive upload functionality
try:
    from .google_drive import get_drive_manager
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = "https://api.openai.com/v1"

# FFmpeg path detection for Windows
FFMPEG_CMD = "ffmpeg"  # Default for Linux/Mac
if os.name == 'nt':  # Windows
    # Check common Windows installation paths
    windows_ffmpeg_paths = [
        r"C:\Users\sabaa\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
    ]
    for path in windows_ffmpeg_paths:
        if Path(path).exists():
            FFMPEG_CMD = path
            break


@tool(
    "generate_sora_video",
    "Generate video using Sora-2 (OpenAI video generation model)",
    {
        "prompt": str,
        "seconds": str,  # Duration: "4", "8", or "12" (MUST be string)
        "orientation": str,  # "portrait" or "landscape"
        "filename": str,
        "upload_to_drive": bool  # Optional: upload to Google Drive videos folder
    }
)
async def generate_sora_video(args):
    """
    Generate video using Sora-2 API

    Model: sora-2
    Pricing: $0.10 per second

    Duration OPTIONS (must be string):
    - "4" = 4 seconds = $0.40
    - "8" = 8 seconds = $0.80
    - "12" = 12 seconds = $1.20

    Resolutions:
    - Portrait: 720x1280
    - Landscape: 1280x720

    Storage:
    - Saves locally to outputs/videos/
    - Optionally uploads to Google Drive (default: True)
    - Returns both local path and shareable Drive link

    API Docs: https://platform.openai.com/docs/guides/video-generation
    API Endpoint: POST https://api.openai.com/v1/videos
    """

    prompt = args["prompt"]
    seconds = args.get("seconds", "4")  # Default 4 seconds
    orientation = args.get("orientation", "landscape")  # Default landscape
    filename = args.get("filename", "video.mp4")
    upload_to_drive = args.get("upload_to_drive", True)  # Default: upload to Drive
    model = "sora-2"  # Only use sora-2

    # Validate seconds (MUST be string!)
    valid_seconds = ["4", "8", "12"]
    if seconds not in valid_seconds:
        return {
            "content": [{
                "type": "text",
                "text": f"Error: seconds must be one of {valid_seconds} (as a STRING). Got: {seconds}\n\nExamples:\n- '4' = 4 seconds = $0.40\n- '8' = 8 seconds = $0.80\n- '12' = 12 seconds = $1.20"
            }]
        }

    # Validate orientation
    valid_orientations = ["portrait", "landscape"]
    if orientation not in valid_orientations:
        return {
            "content": [{
                "type": "text",
                "text": f"Error: Orientation must be one of {valid_orientations}"
            }]
        }

    # Map orientation to resolution
    resolution_map = {
        "portrait": "720x1280",
        "landscape": "1280x720"
    }
    resolution = resolution_map[orientation]

    # Calculate cost ($0.10 per second)
    price_per_sec = 0.10
    duration_int = int(seconds)
    estimated_cost = duration_int * price_per_sec

    if not API_KEY:
        return {
            "content": [{
                "type": "text",
                "text": "Error: OPENAI_API_KEY not found in environment variables. Please add it to your .env file."
            }]
        }

    try:
        # Try using the native Python SDK first (in case it gets updated)
        if hasattr(client, 'videos'):
            video_response = await client.videos.create(
                model=model,
                prompt=prompt,
                size=resolution,
                seconds=seconds  # Must be string: "4", "8", or "12"
            )

            video_url = video_response.url if hasattr(video_response, 'url') else video_response.get('url')

            # Download video
            output_dir = Path("outputs/videos")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / filename

            async with httpx.AsyncClient() as http_client:
                video_data = await http_client.get(video_url)
                output_path.write_bytes(video_data.content)

            # Upload to Google Drive if requested
            drive_url = None
            if upload_to_drive and GOOGLE_DRIVE_AVAILABLE:
                try:
                    drive_manager = get_drive_manager()
                    drive_url = drive_manager.upload_file(
                        str(output_path),
                        "videos",
                        f"Sora-2 video: {prompt[:100]}"
                    )
                except Exception as e:
                    drive_url = f"Upload failed: {str(e)}"

            result_text = f"✅ Video generated successfully!\n\nModel: {model}\nPrompt: {prompt}\nDuration: {seconds}s\nResolution: {resolution} ({orientation})\nEstimated Cost: ${estimated_cost:.2f}\n\nSaved to: {output_path}"

            if drive_url:
                result_text += f"\n\n📤 Google Drive: {drive_url}"

            return {
                "content": [{
                    "type": "text",
                    "text": result_text
                }]
            }

        # Fall back to direct HTTP API call
        else:
            async with httpx.AsyncClient(timeout=300.0) as http_client:
                # Step 1: Create video generation request
                headers = {
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": model,
                    "prompt": prompt,
                    "size": resolution,
                    "seconds": seconds  # MUST be string: "4", "8", or "12"
                }

                # Make API request to CORRECT endpoint
                response = await http_client.post(
                    f"{OPENAI_BASE_URL}/videos",  # NOT /videos/generations!
                    headers=headers,
                    json=payload
                )

                if response.status_code == 404:
                    return {
                        "content": [{
                            "type": "text",
                            "text": (
                                "❌ Sora API endpoint not found (404)\n\n"
                                "The Sora video generation API may not be available for your account yet.\n\n"
                                "**To get access:**\n"
                                "1. Visit https://platform.openai.com/settings/organization/general\n"
                                "2. Ensure your organization is verified\n"
                                "3. Check usage limits at https://platform.openai.com/usage\n"
                                "4. Apply for Sora access if needed\n\n"
                                "**Alternative workflow:**\n"
                                "- Use the visual-designer agent to create storyboard frames with GPT-4o\n"
                                "- Use external tools like Runway, Pika Labs, or Stability AI for video generation\n\n"
                                f"Your API key is configured ({'✓' if API_KEY else '✗'})"
                            )
                        }]
                    }

                if response.status_code == 401:
                    return {
                        "content": [{
                            "type": "text",
                            "text": "❌ Authentication failed. Check your OPENAI_API_KEY in the .env file."
                        }]
                    }

                if response.status_code != 200:
                    error_detail = response.json() if response.headers.get('content-type') == 'application/json' else response.text
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"❌ API Error ({response.status_code}):\n\n{json.dumps(error_detail, indent=2)}"
                        }]
                    }

                result = response.json()
                video_id = result.get('id')

                if not video_id:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"⚠️ No video ID in response:\n\n{json.dumps(result, indent=2)}"
                        }]
                    }

                # Step 2: Poll for completion
                await _poll_for_video_completion(http_client, headers, video_id)

                # Step 3: Download video using /videos/{id}/content endpoint
                output_dir = Path("outputs/videos")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / filename

                video_content_response = await http_client.get(
                    f"{OPENAI_BASE_URL}/videos/{video_id}/content",
                    headers=headers
                )

                if video_content_response.status_code != 200:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"❌ Failed to download video: {video_content_response.status_code}"
                        }]
                    }

                output_path.write_bytes(video_content_response.content)

                # Upload to Google Drive if requested
                drive_url = None
                if upload_to_drive and GOOGLE_DRIVE_AVAILABLE:
                    try:
                        drive_manager = get_drive_manager()
                        drive_url = drive_manager.upload_file(
                            str(output_path),
                            "videos",
                            f"Sora-2 video: {prompt[:100]}"
                        )
                    except Exception as e:
                        drive_url = f"Upload failed: {str(e)}"

                result_text = (
                    f"✅ Video generated successfully!\n\n"
                    f"**Model:** {model}\n"
                    f"**Prompt:** {prompt}\n"
                    f"**Duration:** {seconds}s\n"
                    f"**Resolution:** {resolution} ({orientation})\n"
                    f"**Cost:** ${estimated_cost:.2f} (@ $0.10/second)\n\n"
                    f"**Saved to:** {output_path}\n"
                    f"**Video ID:** {video_id}\n"
                )

                if drive_url:
                    result_text += f"\n**📤 Google Drive:** {drive_url}\n"

                result_text += "\n💡 For longer videos, cost scales linearly: 8s = $0.80, 12s = $1.20"

                return {
                    "content": [{
                        "type": "text",
                        "text": result_text
                    }]
                }

    except httpx.HTTPStatusError as e:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ HTTP Error: {e.response.status_code}\n\n{e.response.text}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": (
                    f"❌ Error generating video: {str(e)}\n\n"
                    f"**Troubleshooting:**\n"
                    f"1. Check your OPENAI_API_KEY is valid\n"
                    f"2. Ensure your account has Sora access\n"
                    f"3. Visit https://platform.openai.com/docs/guides/video-generation\n"
                    f"4. Check usage limits at https://platform.openai.com/usage\n\n"
                    f"**Alternative:** Use visual-designer to create images and external tools for video"
                )
            }]
        }


async def _poll_for_video_completion(http_client, headers, video_id, max_wait=300):
    """
    Poll the API for video generation completion
    Max wait: 300 seconds (5 minutes)
    """
    start_time = asyncio.get_event_loop().time()

    while True:
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > max_wait:
            raise TimeoutError(f"Video generation timed out after {max_wait} seconds")

        response = await http_client.get(
            f"{OPENAI_BASE_URL}/videos/{video_id}",
            headers=headers
        )

        if response.status_code != 200:
            raise Exception(f"Failed to check video status: {response.text}")

        result = response.json()
        status = result.get('status')

        if status == 'completed':
            return  # Video is ready, download it separately
        elif status == 'failed':
            raise Exception(f"Video generation failed: {result.get('error', 'Unknown error')}")

        # Wait before polling again
        await asyncio.sleep(5)


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
    "generate_multi_clip_video",
    "Generate longer videos (30+ seconds) by creating multiple Sora clips and stitching them together",
    {
        "script_segments": list,  # List of dicts with "prompt" and "duration" ("4", "8", or "12")
        "orientation": str,  # "portrait" or "landscape"
        "output_filename": str,
        "style_consistency": str,  # Common visual style instructions (camera, lighting, mood)
        "upload_to_drive": bool  # Optional: upload to Google Drive videos folder
    }
)
async def generate_multi_clip_video(args):
    """
    Generate longer videos by stitching multiple Sora clips together.

    This tool overcomes Sora's 12-second limit by:
    1. Generating multiple clips with consistent visual style
    2. Stitching them together using ffmpeg
    3. Creating seamless 30-second (or longer) ads

    Example usage for 30-second ad:
    script_segments = [
        {"prompt": "Hook scene description", "duration": "12"},
        {"prompt": "Value prop scene description", "duration": "12"},
        {"prompt": "CTA scene description", "duration": "8"}
    ]

    Duration combinations for ~30 seconds:
    - 12s + 12s + 8s = 32 seconds
    - 12s + 12s + 4s = 28 seconds
    - 8s + 8s + 8s + 8s = 32 seconds

    Style consistency tips:
    - Use the same camera movement style across all segments
    - Specify consistent lighting (e.g., "golden hour sunlight")
    - Maintain the same visual mood (e.g., "cinematic, warm tones")
    - Keep color grading consistent (e.g., "vibrant colors, high contrast")

    Requirements:
    - ffmpeg must be installed on the system
    - Each segment prompt should include the style_consistency instructions
    """

    script_segments = args["script_segments"]
    orientation = args.get("orientation", "landscape")
    output_filename = args.get("output_filename", "stitched_video.mp4")
    style_consistency = args.get("style_consistency", "Cinematic style, smooth camera movements, professional lighting")
    upload_to_drive = args.get("upload_to_drive", True)

    # Validate segments
    if not script_segments or len(script_segments) < 2:
        return {
            "content": [{
                "type": "text",
                "text": "Error: Need at least 2 segments to stitch. For single clips, use generate_sora_video instead."
            }]
        }

    # Check ffmpeg availability
    import subprocess
    try:
        subprocess.run([FFMPEG_CMD, "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {
            "content": [{
                "type": "text",
                "text": "❌ ffmpeg not found. Please install ffmpeg:\n\nUbuntu/Debian: sudo apt-get install ffmpeg\nMac: brew install ffmpeg\nWindows: Download from https://ffmpeg.org/download.html"
            }]
        }

    try:
        output_dir = Path("outputs/videos")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate each clip
        clip_paths = []
        total_cost = 0.0
        total_duration = 0

        for i, segment in enumerate(script_segments):
            segment_prompt = segment["prompt"]
            segment_duration = segment.get("duration", "12")

            # Add style consistency to each prompt
            full_prompt = f"{segment_prompt}. {style_consistency}"

            # Generate filename for this clip
            clip_filename = f"clip_{i+1}_{segment_duration}s.mp4"

            print(f"Generating clip {i+1}/{len(script_segments)}: {segment_duration}s...")

            # Generate the clip using existing tool
            result = await generate_sora_video({
                "prompt": full_prompt,
                "seconds": segment_duration,
                "orientation": orientation,
                "filename": clip_filename,
                "upload_to_drive": False  # Don't upload individual clips
            })

            # Extract the file path from result
            clip_path = output_dir / clip_filename
            if not clip_path.exists():
                return {
                    "content": [{
                        "type": "text",
                        "text": f"❌ Failed to generate clip {i+1}. Check the error above."
                    }]
                }

            clip_paths.append(str(clip_path))
            total_cost += int(segment_duration) * 0.10
            total_duration += int(segment_duration)

            print(f"✅ Clip {i+1} generated: {clip_path}")

        # Create ffmpeg concat file
        concat_file = output_dir / "concat_list.txt"
        with open(concat_file, 'w') as f:
            for clip_path in clip_paths:
                f.write(f"file '{os.path.basename(clip_path)}'\n")

        # Stitch videos together using ffmpeg
        final_output_path = output_dir / output_filename

        ffmpeg_cmd = [
            FFMPEG_CMD,
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file.name,
            "-c", "copy",  # Copy without re-encoding for speed
            "-y",  # Overwrite output file
            output_filename
        ]

        print(f"Stitching {len(clip_paths)} clips together...")

        result = subprocess.run(
            ffmpeg_cmd,
            cwd=str(output_dir),
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            # If copy fails, try re-encoding
            print("Copy mode failed, trying with re-encoding...")
            ffmpeg_cmd = [
                FFMPEG_CMD,
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file.name,
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-y",
                output_filename
            ]

            result = subprocess.run(
                ffmpeg_cmd,
                cwd=str(output_dir),
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"❌ ffmpeg stitching failed:\n\n{result.stderr}"
                    }]
                }

        # Clean up temporary files
        concat_file.unlink()
        for clip_path in clip_paths:
            Path(clip_path).unlink()

        # Upload to Google Drive if requested
        drive_url = None
        if upload_to_drive and GOOGLE_DRIVE_AVAILABLE:
            try:
                drive_manager = get_drive_manager()
                drive_url = drive_manager.upload_file(
                    str(final_output_path),
                    "videos",
                    f"Multi-clip Sora video ({total_duration}s)"
                )
            except Exception as e:
                drive_url = f"Upload failed: {str(e)}"

        result_text = (
            f"✅ Multi-clip video generated successfully!\n\n"
            f"**Segments:** {len(script_segments)} clips\n"
            f"**Total Duration:** {total_duration} seconds\n"
            f"**Orientation:** {orientation}\n"
            f"**Total Cost:** ${total_cost:.2f} (@ $0.10/second)\n\n"
            f"**Saved to:** {final_output_path}\n"
        )

        if drive_url:
            result_text += f"\n**📤 Google Drive:** {drive_url}\n"

        result_text += "\n💡 Tips for next time:\n- Keep visual style consistent across all segments\n- Use similar camera movements and lighting\n- Consider transitions between scenes in your prompts"

        return {
            "content": [{
                "type": "text",
                "text": result_text
            }]
        }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error in multi-clip generation: {str(e)}"
            }]
        }


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


@tool(
    "stitch_existing_videos",
    "Stitch pre-existing video files together using FFmpeg (no video generation - just stitching)",
    {
        "video_files": list,  # List of video filenames in outputs/videos/ folder
        "output_filename": str,  # Final stitched video filename
        "upload_to_drive": bool  # Optional: upload to Google Drive videos folder
    }
)
async def stitch_existing_videos(args):
    """
    Stitch pre-existing video files together using FFmpeg.

    This tool is for when you already have video clips and just need to combine them.
    Unlike generate_multi_clip_video, this does NOT generate any new videos via Sora.

    Use cases:
    - Combining separately generated Sora clips
    - Stitching manually edited video segments
    - Combining clips from different sources

    Requirements:
    - FFmpeg must be installed on the system
    - Video files must exist in MARKETING_TEAM/outputs/videos/ folder
    - All videos should ideally have same resolution/codec for best results

    Example usage:
    video_files = [
        "segment_1_intro.mp4",
        "segment_2_demo.mp4",
        "segment_3_cta.mp4"
    ]
    output_filename = "final_video_30s.mp4"
    """
    import subprocess

    video_files = args["video_files"]
    output_filename = args.get("output_filename", "stitched_video.mp4")
    upload_to_drive = args.get("upload_to_drive", True)

    # Validate inputs
    if not video_files or len(video_files) < 2:
        return {
            "content": [{
                "type": "text",
                "text": "❌ Error: Need at least 2 video files to stitch together"
            }]
        }

    # Setup paths
    output_dir = Path("MARKETING_TEAM/outputs/videos").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Validate all video files exist
    video_paths = []
    missing_files = []
    for video_file in video_files:
        video_path = output_dir / video_file
        if not video_path.exists():
            missing_files.append(video_file)
        else:
            video_paths.append(video_path)

    if missing_files:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error: Video files not found:\n" + "\n".join(f"- {f}" for f in missing_files)
            }]
        }

    # Check FFmpeg is available
    try:
        subprocess.run([FFMPEG_CMD, "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {
            "content": [{
                "type": "text",
                "text": "❌ ffmpeg not found. Please install ffmpeg first."
            }]
        }

    print(f"[OK] Stitching {len(video_files)} video files together...")
    print(f"[OK] Input files:")
    for i, vf in enumerate(video_files, 1):
        print(f"  {i}. {vf}")

    try:
        # Create ffmpeg concat file
        concat_file = output_dir / "concat_list.txt"
        with open(concat_file, 'w', encoding='utf-8') as f:
            for video_path in video_paths:
                f.write(f"file '{video_path.name}'\n")

        # Stitch videos together using ffmpeg
        final_output_path = output_dir / output_filename

        # Try with copy codec first (fastest, no re-encoding)
        ffmpeg_cmd = [
            FFMPEG_CMD,
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",  # Copy without re-encoding
            "-y",  # Overwrite output file
            str(final_output_path)
        ]

        print(f"[OK] Running FFmpeg (copy mode)...")
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            # If copy fails, try re-encoding (slower but more compatible)
            print("[OK] Copy mode failed, trying with re-encoding...")
            ffmpeg_cmd = [
                FFMPEG_CMD,
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-y",
                str(final_output_path)
            ]

            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                # Clean up and return error
                concat_file.unlink(missing_ok=True)
                return {
                    "content": [{
                        "type": "text",
                        "text": f"❌ FFmpeg stitching failed:\n\n{result.stderr}"
                    }]
                }

        # Clean up temporary concat file (keep original video files)
        concat_file.unlink(missing_ok=True)

        print(f"[OK] Video stitching complete: {final_output_path}")

        # Get video file size
        file_size_mb = final_output_path.stat().st_size / (1024 * 1024)

        # Upload to Google Drive if requested
        drive_url = None
        if upload_to_drive and GOOGLE_DRIVE_AVAILABLE:
            try:
                print("[OK] Uploading to Google Drive...")
                drive_manager = get_drive_manager()
                drive_url = drive_manager.upload_file(
                    str(final_output_path),
                    "videos",
                    f"Stitched video - {len(video_files)} clips"
                )
                print(f"[OK] Upload complete: {drive_url}")
            except Exception as e:
                drive_url = f"Upload failed: {str(e)}"

        # Build success message
        result_text = (
            f"[OK] Video stitching complete!\n\n"
            f"**Input Segments:** {len(video_files)} clips\n"
            f"**Input Files:**\n"
        )

        for i, vf in enumerate(video_files, 1):
            result_text += f"  {i}. {vf}\n"

        result_text += (
            f"\n**Output File:** {output_filename}\n"
            f"**File Size:** {file_size_mb:.2f} MB\n"
            f"**Saved to:** {final_output_path}\n"
        )

        if drive_url:
            result_text += f"\n**[UPLOAD] Google Drive:** {drive_url}\n"

        result_text += (
            "\n[INFO] Tips:\n"
            "- Original segment files are preserved (not deleted)\n"
            "- Use same resolution/codec across segments for best results\n"
            "- FFmpeg will try copy mode first (fast), then re-encode if needed"
        )

        return {
            "content": [{
                "type": "text",
                "text": result_text
            }]
        }

    except Exception as e:
        # Clean up on error
        if concat_file.exists():
            concat_file.unlink(missing_ok=True)

        return {
            "content": [{
                "type": "text",
                "text": f"❌ Error during video stitching: {str(e)}"
            }]
        }

