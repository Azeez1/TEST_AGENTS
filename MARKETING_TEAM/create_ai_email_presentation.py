"""
Create AI Email Marketing Tools Presentation
5-slide professional marketing presentation with QA workflow
"""
import sys
import os
sys.path.append('tools')

from create_presentation import create_presentation

# Absolute path to generated image
hero_image_path = os.path.abspath("outputs/presentations/images/Modern_professional_AI_email_marketing_concept_fu.png")

# Define all slides
slides_data = [
    # Slide 2: Key Benefits
    {
        "type": "content",
        "title": "Key Benefits",
        "bullets": [
            "Personalization at Scale: Tailor messages to each subscriber automatically",
            "Predictive Analytics: Optimize send times and content for maximum engagement",
            "ROI Boost: Increase conversion rates by 41% with AI-powered campaigns"
        ]
    },
    # Slide 3: Top Features
    {
        "type": "content",
        "title": "Top Features",
        "bullets": [
            "Smart Segmentation: AI analyzes behavior patterns and groups audiences intelligently",
            "A/B Testing Automation: Continuously learns and optimizes subject lines and content",
            "Natural Language Generation: Creates compelling copy that resonates with your audience"
        ]
    },
    # Slide 4: Testimonial Quote
    {
        "type": "quote",
        "quote": "AI email marketing transformed our campaigns. We saw a 63% increase in open rates and 41% more conversions within 3 months. The predictive analytics alone saved us 10 hours per week.",
        "author": "Sarah Chen, Marketing Director at TechFlow Inc."
    },
    # Slide 5: Get Started Today (CTA)
    {
        "type": "content",
        "title": "Get Started Today",
        "bullets": [
            "Start your free 14-day trial",
            "No credit card required",
            "Join 10,000+ marketers leveraging AI"
        ]
    }
]

# Create presentation
print("Creating presentation...")
presentation_path = create_presentation(
    title="AI Email Marketing Tools",
    subtitle="Revolutionizing Customer Engagement",
    slides_data=slides_data,
    output_dir="outputs/presentations"
)

print(f"\n✓ Presentation created successfully!")
print(f"Path: {presentation_path}")
print(f"\nNext step: Hand off to Editor agent for QA review")
