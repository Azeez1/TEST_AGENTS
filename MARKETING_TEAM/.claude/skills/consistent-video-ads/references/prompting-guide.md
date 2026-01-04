# Sora Prompting Guide for Consistent Video Ads

Best practices compiled from OpenAI Cookbook and production experience.

## Core Principles

### 1. Detail Beats Brevity

**Bad:** "Woman holding product in kitchen"

**Good:** "A woman in her late 20s with shoulder-length dark brown hair, wearing a sage green oversized sweater, standing in a modern minimalist kitchen with white marble countertops. Soft morning sunlight streams through large windows. She picks up [product] from the counter with both hands, bringing it closer to examine with a warm, genuine smile. Medium shot, slight camera push-in, natural lighting."

### 2. Consistent Phrasing Across Clips

To maintain character/scene consistency:
- Write your character description ONCE
- Copy-paste EXACTLY into every clip prompt
- Never paraphrase or reword
- Sora responds to literal text matching

### 3. Camera Language

Specify camera behavior explicitly:

| Term | Meaning |
|------|---------|
| Static shot | Camera doesn't move |
| Push-in | Camera moves toward subject |
| Pull-out | Camera moves away from subject |
| Pan left/right | Camera rotates horizontally |
| Tilt up/down | Camera rotates vertically |
| Tracking shot | Camera follows moving subject |
| Dolly | Camera moves on a track |
| Handheld | Slight natural shake |

**Example:** "Medium shot, slight handheld movement, slow push-in toward product"

### 4. Shot Types

| Type | Description | Use For |
|------|-------------|---------|
| Wide shot | Full scene, subject small | Establishing, context |
| Medium shot | Waist-up | Dialogue, demos |
| Close-up | Face/product fills frame | Emotion, detail |
| Extreme close-up | Eyes or small detail | Dramatic emphasis |
| Over-the-shoulder | Behind one person looking at another | Conversation |

### 5. Lighting Descriptions

Be specific about lighting:

- "Soft natural daylight from large windows"
- "Golden hour warmth, long shadows"
- "Bright, even studio lighting"
- "Moody, low-key lighting with single key light"
- "Backlit silhouette against bright background"

### 6. Multi-Shot Prompts (Single Generation)

For clips with scene changes, use timestamps:

```
[0:00-0:03] Wide shot: Woman walks into modern kitchen, morning light
[0:03-0:06] Medium shot: She reaches for [product] on marble counter
[0:06-0:08] Close-up: Her hands opening the package, genuine smile
```

**Note:** Results vary - test for your use case.

## UGC-Specific Tips

### Authentic Feel

- "Slightly imperfect framing"
- "Natural, unposed body language"
- "Genuine reaction, not performed"
- "Casual home environment, lived-in feel"

### Platform Optimization

**TikTok (9:16 portrait):**
- Fast cuts, high energy
- Text overlay space at top/bottom
- Face in upper third

**Instagram Reels (9:16 portrait):**
- Slightly more polished
- Brand-safe environments
- Clean backgrounds

**Facebook (16:9 landscape or 1:1 square):**
- Slower pace acceptable
- More context/story
- Sound-off friendly (captions)

## Prompt Templates

### Product Demo

```
[CHARACTER BIBLE HERE]

She picks up [PRODUCT] from the counter, examining it with genuine curiosity.
Close-up of her hands as she [INTERACTION ACTION].
Cut to medium shot of her [REACTION] with authentic enthusiasm.
Bright, natural kitchen lighting. Handheld camera feel, slight movement.
```

### Testimonial

```
[CHARACTER BIBLE HERE]

Direct to camera, warm genuine expression. She speaks naturally about
[PRODUCT], gesturing casually with her hands. Soft smile, nodding slightly.
Natural home environment visible in background. Soft, diffused lighting.
Medium shot, static camera with slight depth of field.
```

### Unboxing

```
[CHARACTER BIBLE HERE]

Top-down shot of [PRODUCT] box on clean surface. Her hands enter frame,
carefully opening the packaging. Cut to her face showing genuine excitement.
Close-up of product reveal moment. Bright, even lighting, clean aesthetic.
```

## Common Mistakes

1. **Vague descriptions** - "Person uses product" (too generic)
2. **Inconsistent phrasing** - Different words for same character
3. **Missing lighting** - Sora defaults unpredictably
4. **No camera direction** - Random shot choices
5. **Too many actions** - One clear action per 4s is better
6. **Ignoring aspect ratio** - Prompt should match orientation

## Advanced: Remix API

After generating a base clip, use remix for variations:

```
POST /v1/videos/{video_id}/remix
{
  "prompt": "Same scene but with warmer color grading and slower pace"
}
```

Remix preserves structure while allowing style changes.

## Stitching Strategy

For 15-30 second ads:

| Duration | Recommended Strategy |
|----------|---------------------|
| 15 sec | 2x8s clips |
| 20 sec | 3x8s clips (trim middle) |
| 24 sec | 3x8s clips |
| 30 sec | 4x8s clips OR 3x12s clips |

**Pro tip:** 4x4s clips often have better consistency than 2x8s for the same duration, though at same cost.
