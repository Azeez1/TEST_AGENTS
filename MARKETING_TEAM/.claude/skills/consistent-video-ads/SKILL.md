---
name: consistent-video-ads
description: Create consistent 15-30 second video ads with character and story continuity using Sora API. This skill should be used when generating multi-clip video ads, ensuring character consistency across scenes, or creating longer-format video content (15-30+ seconds) that requires visual coherence. Works for ANY product.
---

# Consistent Video Ads

This skill provides workflows for creating video ads with character and story consistency using Sora API. Sora's max clip length is 12 seconds, so longer ads require multi-clip strategies.

## When to Use This Skill

- Creating video ads longer than 12 seconds
- Need character consistency across multiple shots
- Product demos with multiple scenes
- Story-driven ads with beginning/middle/end
- UGC-style content with same "creator" across clips

## 4 Consistency Approaches

### Approach 1: Character Bible (Universal)

**Best for:** All multi-clip videos

Create a "character bible" with exact phrasing reused across ALL prompts. Sora responds to consistent language.

**Workflow:**
1. Define character/product description ONCE using `references/character-bible-template.md`
2. Copy-paste exact description into every clip prompt
3. Never paraphrase - use identical wording

**Example:**
```
CHARACTER BIBLE:
"A woman in her late 20s with shoulder-length dark brown hair, wearing a sage
green oversized sweater. She has warm olive skin, natural makeup with subtle
pink lip gloss. Bright, genuine smile. In a modern minimalist kitchen with
white marble countertops and morning sunlight streaming through large windows."
```

Use this EXACT text in every clip prompt.

### Approach 2: Image Reference Chain (Product Shots)

**Best for:** Product-focused ads, unboxing, demos

Use the same product image as the first frame reference for every clip.

**Workflow:**
1. Create/obtain high-quality product image (720x1280 for portrait)
2. Use `input_reference` parameter with same image for ALL clips
3. Product appears consistently across entire ad

**Example:**
```python
# Same image for all clips
generate_sora_video(
    input_reference="outputs/images/product_hero.png",
    auto_analyze_image=True,
    prompt="Hands reaching for [product] on kitchen counter...",
    ...
)
```

### Approach 3: Multi-Clip Stitching (15-30s Ads)

**Best for:** Standard ad lengths (15s, 30s)

Generate multiple 4-8 second clips, then stitch with FFmpeg.

**Workflow:**
1. Plan shot sequence (hook → demo → benefits → CTA)
2. Generate each clip with Character Bible consistency
3. Use `scripts/stitch_clips.py` to combine
4. Add crossfades or hard cuts as needed

**Cost Breakdown:**
| Target Duration | Clip Strategy | Cost |
|-----------------|---------------|------|
| 15 sec | 2x8s clips | $1.60 |
| 24 sec | 3x8s clips | $2.40 |
| 30 sec | 4x8s clips | $3.20 |
| 30 sec | 3x12s clips | $3.60 |

**Pro Tip:** 4-second clips often have better consistency than 8-second clips. Consider 4x4s for 16 seconds instead of 2x8s.

### Approach 4: Remix Chain (Style Variations)

**Best for:** B-roll, alternate angles, style exploration

Generate a base clip, then use Sora's remix API to create variations.

**Workflow:**
1. Generate base clip with ideal composition
2. Use remix endpoint to modify: `POST /v1/videos/{video_id}/remix`
3. Remix preserves structure while changing style/angle/lighting

**Note:** Remix API is available but less documented. Test carefully.

## Standard Multi-Clip Ad Structure

For a 24-second ad (3 clips):

| Clip | Duration | Purpose | Prompt Focus |
|------|----------|---------|--------------|
| 1 | 8s | Hook | Attention-grabbing opening, show product |
| 2 | 8s | Demo | Product in use, benefits visible |
| 3 | 8s | CTA | Emotional payoff, call to action |

**All clips use the same Character Bible description.**

## Integration with Existing Tools

This skill works with the `generate_sora_video` MCP tool:

```python
mcp__marketing-tools__generate_sora_video(
    prompt="...",                    # Include Character Bible text
    input_reference="...",           # Same image for all clips
    ugc_style="demo",                # Or: testimonial, unboxing, etc.
    product_name="Product Name",
    platform="tiktok",               # tiktok, instagram, facebook
    seconds="8",                     # "4", "8", or "12"
    orientation="portrait",          # portrait or landscape
    auto_analyze_image=True,
    filename="clip_1"
)
```

## Post-Production with FFmpeg

After generating clips, use `scripts/stitch_clips.py`:

```bash
python scripts/stitch_clips.py \
    --clips clip_1.mp4 clip_2.mp4 clip_3.mp4 \
    --output final_ad.mp4 \
    --transition crossfade \
    --duration 0.5
```

## Anti-Morphing Stability Mode (NEW)

All video generation functions now include a `stability_mode` parameter that automatically injects anti-morphing directives into prompts:

| Mode | When to Use | What It Does |
|------|-------------|--------------|
| `"auto"` (default) | Always — smart detection | Detects UGC keywords → authentic, else → cinematic |
| `"cinematic"` | Brand videos, product showcases | Static camera triple-emphasis, style anchor, spatial anchoring |
| `"authentic"` | UGC, testimonials, demos | Preserves handheld feel, adds subtle anti-morph keywords |
| `"off"` | Legacy behavior, full control | No enhancement — raw prompt passed through |

**Usage:**
```python
mcp__marketing-tools__generate_sora_video(
    prompt="...",
    stability_mode="cinematic",   # Maximum anti-morphing
    seconds="8",
    ...
)
```

**What gets injected (cinematic mode):**
- Style anchor prefix (camera/lens reference for visual consistency)
- Static camera triple-emphasis (stationary, fixed, no drift)
- Anti-morphing keywords (no warping, consistent appearance, stable lighting)
- Spatial anchoring (foreground/midground/background layer hints)
- Duration-aware pacing (fewer actions for shorter clips)
- Physics stability (natural material behavior)

**Veo 3.1 bonus:** Also auto-injects negative_prompt with anti-morphing terms (warping, flickering, face drift, etc.)

## Best Practices (from OpenAI Cookbook + Community Research)

1. **Detailed descriptions beat short prompts** - More detail = more consistency
2. **Reuse exact phrasing** - Don't paraphrase between clips
3. **Specify camera angles** - "Medium shot", "Close-up", "Over-the-shoulder"
4. **Include lighting** - "Soft natural lighting", "Golden hour warmth"
5. **4s clips often better** - More coherent than longer clips
6. **Multi-shot timestamps** - Can include `[0:00-0:04]...[0:04-0:08]` in single prompt
7. **One action per shot** - Limit to one subject action + one camera move max
8. **Style anchor at start** - Open with era/film/device reference to lock visual consistency
9. **Generate 3-5 variants** - Same prompt has ~50% quality variance, pick the best
10. **24fps over 60fps** - Higher FPS makes temporal artifacts more visible

## References

- `references/prompting-guide.md` - Detailed prompting best practices
- `references/character-bible-template.md` - Template for consistent characters

## Cost Calculator

| Duration | Strategy | Clips | Total Cost |
|----------|----------|-------|------------|
| 4 sec | Single | 1x4s | $0.40 |
| 8 sec | Single | 1x8s | $0.80 |
| 12 sec | Single | 1x12s | $1.20 |
| 16 sec | Multi | 2x8s | $1.60 |
| 16 sec | Multi | 4x4s | $1.60 |
| 24 sec | Multi | 3x8s | $2.40 |
| 30 sec | Multi | 4x8s | $3.20 |
| 30 sec | Multi | 3x12s | $3.60 |

**Add $0.01 per clip if using `auto_analyze_image=True`**
