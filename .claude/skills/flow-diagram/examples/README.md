# Flow Diagram Examples - Enhanced Edition

This directory contains example diagrams showcasing the stunning visual styles available.

## Quick Start

### 1. Generate a Glassmorphism Diagram (Modern, Premium)

```bash
python ../scripts/generate_diagram.py modern-architecture.mmd \
    --style glassmorphism \
    --title "Modern Architecture" \
    -o architecture-glass.html
```

**Perfect for:** Tech products, SaaS platforms, modern architecture
**LinkedIn Performance:** High engagement with tech audiences

### 2. Generate a Neon/Cyberpunk Diagram (Bold, Attention-Grabbing)

```bash
python ../scripts/generate_diagram.py modern-architecture.mmd \
    --style neon \
    --title "System Architecture" \
    -o architecture-neon.html
```

**Perfect for:** Developer tools, blockchain, AI/ML topics
**LinkedIn Performance:** Maximum scroll-stopping power

### 3. Generate a Hand-Drawn Diagram (Friendly, Approachable)

```bash
python ../scripts/generate_diagram.py modern-architecture.mmd \
    --style hand-drawn \
    --title "Our Tech Stack" \
    -o architecture-sketch.html
```

**Perfect for:** Tutorials, educational content, creative industries
**LinkedIn Performance:** High engagement, feels authentic

## LinkedIn Carousel (45.85% Engagement!)

Generate a LinkedIn carousel from any diagram:

```bash
python ../scripts/generate_carousel.py modern-architecture.mmd \
    --slides 8 \
    --style glassmorphism \
    --title "Building Modern Architecture" \
    -o my_carousel/
```

This creates 8 progressive slides perfect for LinkedIn:
- Slide 0: Eye-catching title slide
- Slides 1-8: Progressive revelation of your architecture

### LinkedIn Carousel Best Practices

1. **Optimal slide count:** 6-10 slides
2. **Text per slide:** Under 50 words
3. **Posting time:** Business hours for B2B content
4. **Call-to-action:** Add on the last slide
5. **First slide:** Make it attention-grabbing (your title slide does this!)

## Style Comparison

| Style | Best For | Vibe | Engagement |
|-------|----------|------|------------|
| **Glassmorphism** | Tech, SaaS, Modern | Premium, Professional | High (Tech) |
| **Neon** | Dev Tools, Blockchain | Bold, Futuristic | Very High (Scroll-stopping) |
| **Hand-Drawn** | Education, Creative | Friendly, Approachable | High (Authentic) |
| **Classic** | Enterprise, Formal | Clean, Professional | Medium (Traditional) |

## Social Media Sizing

### LinkedIn Post (Square)
```bash
python ../scripts/generate_carousel.py diagram.mmd --size linkedin
# 1080x1080px - Perfect for LinkedIn feed
```

### LinkedIn Article (Wide)
```bash
python ../scripts/generate_carousel.py diagram.mmd --size linkedin-wide
# 1200x628px - Perfect for LinkedIn article headers
```

### Twitter
```bash
python ../scripts/generate_carousel.py diagram.mmd --size twitter
# 1200x675px - Twitter's recommended size
```

### Instagram
```bash
python ../scripts/generate_carousel.py diagram.mmd --size instagram
# 1080x1080px - Instagram feed
```

## Advanced Tips

### Combining Styles for Maximum Impact

1. **Tech Launch**: Use Neon style for bold announcement
2. **Tutorial Series**: Use Hand-drawn for friendly, educational feel
3. **Product Demo**: Use Glassmorphism for premium, modern look
4. **Case Study**: Use Carousel with professional corporate style

### Export High-Quality Images

All styles support export to:
- **PNG** (High quality, 3x resolution for crisp visuals)
- **SVG** (Vector format, infinite scaling)

Open any generated HTML in your browser and click the export buttons!

### Creating Viral Content

1. **Start with Neon or Glassmorphism** - Maximum attention
2. **Use Carousel Format** - 45.85% engagement rate
3. **Add Bold Title** - Make first slide count
4. **Keep It Simple** - Less is more
5. **End with CTA** - Drive action

## Example Diagram Types

The `modern-architecture.mmd` example demonstrates:
- ✅ Subgraphs for logical grouping
- ✅ Emoji icons for visual interest
- ✅ Color coding by layer
- ✅ Clear connection flows
- ✅ Multi-tier architecture

## Need More Examples?

Check out the main skill documentation at `../SKILL.md` for:
- 7 complete use case examples
- Best practices guide
- Complete Mermaid syntax reference
- Architecture-specific patterns

## Questions?

The enhanced flow diagram skill makes it easy to create:
- Eye-popping diagrams that stop the scroll
- LinkedIn carousels with 45.85% engagement
- Professional visualizations for any platform
- Stunning portfolio pieces

Start with the examples above and experiment with different styles to find what works best for your audience!
