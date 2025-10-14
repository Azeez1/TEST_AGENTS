"""
Image Generation Tool using ChatGPT-4o (DALL-E 3)
Generates professional images for presentation slides
"""

import os
import requests
from openai import OpenAI

def generate_slide_image(prompt, style="professional", size="1024x1024", output_dir="outputs/presentations/images"):
    """
    Generate an image for a presentation slide using ChatGPT-4o image generation

    Args:
        prompt (str): Description of the image to generate
        style (str): Visual style - "professional", "minimalist", "corporate", "vibrant"
        size (str): Image size - "1024x1024" (default), "1792x1024" (wide), "1024x1792" (tall)
        output_dir (str): Directory to save generated images

    Returns:
        str: Path to the generated image file

    Example:
        image_path = generate_slide_image(
            prompt="Modern AI marketing dashboard with analytics charts",
            style="professional"
        )
    """

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Get OpenAI API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = OpenAI(api_key=api_key)

    # Enhance prompt with style guidelines
    style_prompts = {
        "professional": "professional, clean, business-appropriate, corporate style, high quality",
        "minimalist": "minimalist, simple, clean lines, lots of white space, modern",
        "corporate": "corporate, professional, business setting, formal, polished",
        "vibrant": "vibrant colors, energetic, modern, eye-catching, dynamic"
    }

    enhanced_prompt = f"{prompt}, {style_prompts.get(style, style_prompts['professional'])}"

    try:
        # Generate image using DALL-E 3
        response = client.images.generate(
            model="dall-e-3",
            prompt=enhanced_prompt,
            size=size,
            quality="standard",  # or "hd" for higher quality
            n=1
        )

        # Get image URL
        image_url = response.data[0].url

        # Download image
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        # Generate filename
        safe_filename = "".join(c for c in prompt[:50] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_filename = safe_filename.replace(' ', '_')
        image_filename = f"{safe_filename}.png"
        image_path = os.path.join(output_dir, image_filename)

        # Save image
        with open(image_path, 'wb') as f:
            f.write(image_response.content)

        print(f"[OK] Image generated: {image_path}")
        return image_path

    except Exception as e:
        print(f"[ERROR] Error generating image: {str(e)}")
        raise


def generate_chart_image(chart_type, data, title, output_dir="outputs/presentations/images"):
    """
    Generate a chart image using matplotlib

    Args:
        chart_type (str): "bar", "line", "pie", "area"
        data (dict): Chart data {"labels": [...], "values": [...]}
        title (str): Chart title
        output_dir (str): Directory to save chart images

    Returns:
        str: Path to the generated chart image

    Example:
        chart_path = generate_chart_image(
            chart_type="bar",
            data={"labels": ["Q1", "Q2", "Q3", "Q4"], "values": [100, 150, 120, 180]},
            title="Quarterly Revenue Growth"
        )
    """
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    labels = data.get("labels", [])
    values = data.get("values", [])

    # Generate chart based on type
    if chart_type == "bar":
        ax.bar(labels, values, color='#4472C4')
    elif chart_type == "line":
        ax.plot(labels, values, marker='o', linewidth=2, color='#4472C4')
    elif chart_type == "pie":
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
    elif chart_type == "area":
        ax.fill_between(range(len(values)), values, alpha=0.7, color='#4472C4')
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels)
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    # Set title and styling
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    if chart_type != "pie":
        ax.grid(axis='y', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines('right').set_visible(False)

    plt.tight_layout()

    # Save chart
    safe_filename = "".join(c for c in title[:50] if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_filename = safe_filename.replace(' ', '_')
    chart_filename = f"chart_{safe_filename}.png"
    chart_path = os.path.join(output_dir, chart_filename)

    plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"[OK] Chart generated: {chart_path}")
    return chart_path


# Test function
if __name__ == "__main__":
    # Test image generation
    try:
        img_path = generate_slide_image(
            prompt="Futuristic AI marketing dashboard with data visualization",
            style="professional"
        )
        print(f"Test image generated: {img_path}")
    except Exception as e:
        print(f"Test failed: {e}")

    # Test chart generation
    try:
        chart_path = generate_chart_image(
            chart_type="bar",
            data={"labels": ["Q1", "Q2", "Q3", "Q4"], "values": [100, 150, 120, 180]},
            title="Quarterly Performance"
        )
        print(f"Test chart generated: {chart_path}")
    except Exception as e:
        print(f"Test failed: {e}")
