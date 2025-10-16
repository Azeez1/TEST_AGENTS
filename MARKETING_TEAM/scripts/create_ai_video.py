"""
Create AI Video using Sora-2
12-second video about the future of AI
"""

import asyncio
import os
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = "https://api.openai.com/v1"


async def create_ai_video():
    """Generate 12-second AI video"""

    print("=" * 70)
    print("[VIDEO] Creating AI Video with Sora-2")
    print("=" * 70)
    print()

    # Video specs
    prompt = """A stunning visualization of artificial intelligence transforming the world.

Opening shot: An abstract neural network with glowing blue and purple nodes, data streams flowing through connections like rivers of light. Camera slowly zooms forward through the network.

Mid-section: The network transforms seamlessly into real-world AI applications - holographic medical imaging scanning a patient, autonomous vehicles on futuristic highways, robotic arms precision-manufacturing in a clean factory. Smooth cinematic camera movements with gentle transitions.

Closing shot: Pull back to reveal a diverse team of professionals working alongside AI systems in a modern glass office, collaborative and optimistic atmosphere. Natural lighting from large windows creates warm golden tones.

Style: Cinematic, high production value, professional color grading, shallow depth of field. Transitions from cool blue tones to warm golden light. Medium pacing with smooth camera movements."""

    seconds = "12"  # Must be string
    orientation = "landscape"
    resolution = "1280x720"
    filename = "ai_future_video.mp4"
    model = "sora-2"
    cost = 1.20  # $0.10 per second

    print(f"Model: {model}")
    print(f"Duration: {seconds} seconds")
    print(f"Resolution: {resolution} ({orientation})")
    print(f"Cost: ${cost:.2f}")
    print()
    print(f"Prompt: {prompt[:150]}...")
    print()

    if not API_KEY:
        print(" Error: OPENAI_API_KEY not found in .env file")
        return

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            # Step 1: Create video generation request
            print("[1/3] Sending request to Sora API...")

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": model,
                "prompt": prompt.strip(),
                "size": resolution,
                "seconds": seconds
            }

            response = await client.post(
                f"{OPENAI_BASE_URL}/videos",
                headers=headers,
                json=payload
            )

            if response.status_code == 404:
                print()
                print(" Sora API endpoint not found (404)")
                print()
                print("The Sora video generation API may not be available for your account yet.")
                print()
                print("To get access:")
                print("1. Visit https://platform.openai.com/settings/organization/general")
                print("2. Ensure your organization is verified")
                print("3. Check your usage tier at https://platform.openai.com/usage")
                print()
                print("Alternative: Use visual-designer to create storyboard images")
                return

            if response.status_code == 401:
                print(" Authentication failed. Check your OPENAI_API_KEY")
                return

            if response.status_code != 200:
                print(f" API Error ({response.status_code}):")
                print(response.text)
                return

            result = response.json()
            video_id = result.get('id')

            if not video_id:
                print(f" No video ID in response: {result}")
                return

            print(f" Video generation started (ID: {video_id})")
            print()

            # Step 2: Poll for completion
            print("[2/3] Waiting for video generation to complete...")
            print("(This may take 2-5 minutes)")
            print()

            import time
            start_time = time.time()
            max_wait = 300  # 5 minutes

            while True:
                elapsed = time.time() - start_time
                if elapsed > max_wait:
                    print(" Timeout: Video generation took too long")
                    return

                status_response = await client.get(
                    f"{OPENAI_BASE_URL}/videos/{video_id}",
                    headers=headers
                )

                if status_response.status_code != 200:
                    print(f" Failed to check status: {status_response.text}")
                    return

                status_result = status_response.json()
                status = status_result.get('status')

                print(f"  Status: {status} (elapsed: {int(elapsed)}s)", end='\r')

                if status == 'completed':
                    print()
                    print(" Video generation completed!")
                    print()
                    break
                elif status == 'failed':
                    print()
                    print(f" Video generation failed: {status_result.get('error', 'Unknown error')}")
                    return

                await asyncio.sleep(5)

            # Step 3: Download video
            print("[3/3] Downloading video...")

            output_dir = Path("outputs/videos")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / filename

            video_response = await client.get(
                f"{OPENAI_BASE_URL}/videos/{video_id}/content",
                headers=headers
            )

            if video_response.status_code != 200:
                print(f" Failed to download video: {video_response.status_code}")
                return

            output_path.write_bytes(video_response.content)

            file_size = len(video_response.content) / (1024 * 1024)  # MB

            print()
            print("=" * 70)
            print("[SUCCESS] AI Video Created!")
            print("=" * 70)
            print()
            print(f"Saved to: {output_path}")
            print(f"File size: {file_size:.2f} MB")
            print(f"Duration: {seconds} seconds")
            print(f"Cost: ${cost:.2f}")
            print(f"Video ID: {video_id}")
            print()
            print("Ready to share!")
            print()

    except Exception as e:
        print(f" Error: {str(e)}")
        print()
        print("Troubleshooting:")
        print("1. Check your OPENAI_API_KEY is valid")
        print("2. Ensure your account has Sora access")
        print("3. Visit https://platform.openai.com/docs/guides/video-generation")


if __name__ == "__main__":
    asyncio.run(create_ai_video())
