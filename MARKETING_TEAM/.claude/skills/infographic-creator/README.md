# Infographic Creator Skill

**Create stunning static, animated, and interactive infographics that drive 3x more engagement than regular content.**

## 🚀 Quick Start

```bash
# Basic infographic
python scripts/generate_infographic.py --data metrics.csv --title "Q4 Results"

# With brand and style
python scripts/generate_infographic.py \
    --data metrics.csv \
    --style glassmorphism \
    --brand "Dux Machina" \
    --output q4-infographic.html

# LinkedIn-optimized with AI content
python scripts/generate_infographic.py \
    --data metrics.csv \
    --export linkedin-post \
    --generate-content
```

## 📋 What's Included

### **7 Infographic Types**
- **Statistical** - Metrics, KPIs, dashboards
- **Timeline** - Roadmaps, history, milestones
- **Comparison** - Side-by-side, versus, features
- **Process** - Step-by-step, workflows
- **Hierarchical** - Pyramids, org charts
- **Geographic** - Maps, regional data
- **List** - Top 10, tips, features

### **6 Visual Styles**
- **Glassmorphism** - Modern, premium frosted glass
- **Neon** - Bold, cyberpunk, attention-grabbing
- **Hand-Drawn** - Friendly, sketch-style
- **Vibrant** - Bold gradients, maximalist
- **Corporate** - Clean, professional
- **Animated** - Dynamic particles

### **Features**
✅ AI-powered design intelligence
✅ Brand customization suite
✅ Content AI assistant (headlines, captions)
✅ Advanced animations (Anime.js)
✅ Interactive features (charts, hover effects)
✅ Social media presets (LinkedIn, Instagram, Twitter)
✅ Multiple export formats (HTML, PNG, PDF, GIF, MP4)
✅ Integration with flow-diagram, canvas-design, theme-factory

## 📖 Usage Examples

### Example 1: Statistical Infographic
```bash
python scripts/generate_infographic.py \
    --type statistical \
    --title "Q4 2024 Highlights" \
    --data q4_metrics.csv \
    --style glassmorphism \
    --brand "Dux Machina" \
    --output q4-stats.html
```

**Input (q4_metrics.csv):**
```csv
metric,value,change
Revenue,$2.5M,127
Customers,50000,45
Satisfaction,95%,5
```

**Output:** Professional infographic with animated counters, brand colors, logo placement

### Example 2: Timeline Infographic
```bash
python scripts/generate_infographic.py \
    --type timeline \
    --title "2025 Product Roadmap" \
    --style neon \
    --interactive \
    --output roadmap.html
```

### Example 3: Comparison Infographic
```bash
python scripts/generate_infographic.py \
    --type comparison \
    --data product_comparison.json \
    --title "Why Choose Us?" \
    --style vibrant \
    --export linkedin-post
```

## 🎨 Brand Customization

### Create a Brand Kit
```bash
python scripts/brand_kit.py create "My Company" \
    --primary "#B8860B" \
    --secondary "#0A0E14" \
    --accent "#FFFFFF" \
    --headline-font "Inter" \
    --body-font "Inter" \
    --logo "path/to/logo.png" \
    --watermark "© 2025 My Company"
```

### List Brand Kits
```bash
python scripts/brand_kit.py list
```

### Use Brand Kit
```bash
python scripts/generate_infographic.py \
    --data metrics.csv \
    --brand "My Company" \
    --output branded-infographic.html
```

## 📱 Social Media Presets

Export directly to platform-optimized dimensions:

```bash
# LinkedIn post (1200x627)
--export linkedin-post

# LinkedIn carousel (1080x1080)
--export linkedin-carousel

# Instagram post (1080x1080)
--export instagram-post

# Instagram story (1080x1920)
--export instagram-story

# Twitter post (1200x675)
--export twitter-post

# Facebook post (1200x630)
--export facebook-post

# Pinterest pin (1000x1500)
--export pinterest-pin
```

## 🤖 AI Content Generation

Generate headlines, captions, and hashtags automatically:

```bash
python scripts/generate_infographic.py \
    --data metrics.csv \
    --title "Q4 Results" \
    --generate-content
```

**Output:**
- `content/headlines.txt` - 5 headline variations
- `content/captions.txt` - LinkedIn, Twitter, Instagram captions
- Hashtag suggestions for each platform

## 🎬 Animation Options

Control animation behavior:

```bash
# Enable animations (default)
python scripts/generate_infographic.py --data metrics.csv

# Disable animations
python scripts/generate_infographic.py --data metrics.csv --no-animation

# Custom duration (milliseconds)
python scripts/generate_infographic.py --data metrics.csv --animation-duration 3000
```

## 🖱️ Interactive Features

Add interactivity:

```bash
python scripts/generate_infographic.py \
    --data metrics.csv \
    --interactive \
    --output dashboard.html
```

**Interactive elements:**
- Hover tooltips
- Clickable elements
- Chart interactions
- Scroll animations

## 📊 Data Formats

### CSV Format
```csv
metric,value,change
Revenue,$2.5M,127
Customers,50000,45
```

### JSON Format
```json
{
  "title": "Q4 Performance",
  "metrics": [
    {"name": "Revenue", "value": 2500000, "change": 127},
    {"name": "Customers", "value": 50000, "change": 45}
  ]
}
```

## 🎓 Best Practices

### Design Principles
1. **Maximize data, minimize decoration** (Data-Ink Ratio)
2. **Clear visual hierarchy** (guide attention)
3. **Meaningful color coding** (consistent meaning)
4. **Typography hierarchy** (clear sizing)
5. **Generous whitespace** (minimum 20%)

### Animation Guidelines
- Keep under 10 seconds total
- Stagger related elements (100-200ms)
- Use natural easing (easeOutExpo)
- Provide still frame fallback

### Social Media Optimization
- Large text (minimum 18px)
- High contrast for mobile
- LinkedIn: Professional, data-driven
- Instagram: Bold, colorful
- Twitter: Punchy, concise

**See `references/infographic-best-practices.md` for complete guidelines.**

## 📁 File Structure

```
infographic-creator/
├── SKILL.md                    # Complete skill documentation
├── README.md                   # This file
├── templates/                  # 7 HTML templates
│   ├── statistical-template.html
│   ├── timeline-template.html
│   ├── comparison-template.html
│   ├── process-template.html
│   ├── hierarchical-template.html
│   ├── geographic-template.html
│   └── list-template.html
├── scripts/                    # Python scripts
│   ├── generate_infographic.py # Main generator
│   ├── brand_kit.py            # Brand kit manager
│   ├── animate_infographic.py  # Animation tools
│   └── export_social.py        # Export utilities
├── assets/                     # Icons, fonts, charts
├── examples/                   # Example infographics
└── references/                 # Best practices docs
```

## 🔗 Integration with Other Skills

### flow-diagram
Uses the same 6 visual styles and animation engine
```bash
python scripts/generate_infographic.py --style neon  # Same neon style
```

### canvas-design
Applies artistic design philosophy
```bash
# Inherits canvas-design aesthetic principles
python scripts/generate_infographic.py --style hand-drawn
```

### theme-factory
Use pre-built theme color palettes
```bash
python scripts/generate_infographic.py --theme "Ocean Depths"
```

## 🚧 Advanced Usage

### Custom Dimensions
```bash
--canvas-width 1920     # Custom width
--title-size 64         # Custom title font size
--subtitle-size 28      # Custom subtitle font size
```

### Multiple Exports
```bash
--export linkedin-post,instagram-post,twitter-post
```

### Full Custom Example
```bash
python scripts/generate_infographic.py \
    --data metrics.csv \
    --type statistical \
    --title "Unprecedented Growth" \
    --subtitle "Q4 2024 Performance Metrics" \
    --style glassmorphism \
    --brand "Dux Machina" \
    --canvas-width 1600 \
    --title-size 56 \
    --interactive \
    --generate-content \
    --export linkedin-post,png,pdf \
    --output reports/q4-performance.html
```

## 📝 Command Reference

### generate_infographic.py

```
Options:
  --data FILE               Data file (CSV, JSON)
  --type TYPE               Infographic type (auto-detected if omitted)
  --title TEXT              Infographic title
  --subtitle TEXT           Infographic subtitle
  --style STYLE             Visual style (glassmorphism, neon, etc.)
  --brand NAME              Brand kit to apply
  --theme NAME              Theme-factory theme to apply
  --canvas-width INT        Canvas width in pixels (default: 1200)
  --title-size INT          Title font size
  --subtitle-size INT       Subtitle font size
  --no-animation            Disable animations
  --animation-duration INT  Animation duration in milliseconds
  --interactive             Enable interactive features
  --generate-content        Generate AI headlines and captions
  --output FILE             Output HTML file path
  --export FORMAT           Export format or social preset
```

## 💡 Tips & Tricks

1. **Start simple** - Use defaults, then customize
2. **Auto-detect type** - Omit --type to let AI choose
3. **Test on mobile** - 70%+ viewers are on mobile
4. **Use brand kits** - Save time with consistent branding
5. **Generate content** - Let AI write headlines and captions
6. **Export multiple** - Create versions for each platform
7. **Iterate** - First version is rarely the best

## 🆘 Troubleshooting

**Problem:** Text too small
```bash
Solution: --title-size 64 --canvas-width 1600
```

**Problem:** Colors look washed out
```bash
Solution: Use --style vibrant or create custom brand kit
```

**Problem:** Animation is choppy
```bash
Solution: --animation-duration 2500  # Slower = smoother
```

**Problem:** File size too large
```bash
Solution: Use --export png and compress with optimization tools
```

## 📞 Support

- **Documentation:** See `SKILL.md` for complete details
- **Best Practices:** See `references/infographic-best-practices.md`
- **Examples:** Check `examples/` directory

## 🎯 Success Metrics

Track your infographic performance:
- Views / Impressions
- Shares / Retweets
- Comments / Discussions
- Click-through rate
- Download rate
- Time spent viewing

**Infographics get 3x more engagement than text posts!** 🚀

---

**Ready to create scroll-stopping infographics?**

```bash
python scripts/generate_infographic.py --data your-data.csv --title "Your Amazing Title"
```
