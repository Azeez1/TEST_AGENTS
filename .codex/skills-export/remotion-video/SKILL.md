---
name: "remotion-video"
description: "Create programmatic .mp4 videos with React using Remotion \u2014 motion graphics, animated text, branded intros/outros, caption overlays, data visualizations, and post-production editing of AI-generated clips (Sora 2, Veo). Outputs rendered video files. Use when the final output is a VIDEO, not a GIF (use slack-gif-creator) or static image (use canvas-design). See gotchas.md for critical Sora/Veo integration fixes."
---

# Remotion Video Skill

## Overview

Remotion lets you create videos programmatically using React components. Instead of timeline-based editors, you write code that defines every frame, enabling precise control over motion graphics, animations, and compositions.

**Key Benefits:**
- **Code-based:** Version control, reusable components, dynamic data binding
- **React ecosystem:** Use any npm package, React patterns, existing skills
- **Programmatic:** Generate variations, batch processing, template systems
- **Precise timing:** Frame-accurate control (30fps = 30 frames per second)

## When to Use Remotion

**Use Remotion for:**
- Motion graphics, animated text, titles, lower thirds
- Branded intros/outros (consistent across all videos)
- Caption overlays (TikTok/Instagram style animated captions)
- Data visualizations (animated charts, graphs, metrics)
- Post-production on AI clips (add branding, transitions, text overlays)
- UI/product demos with simulated interactions
- Video templates with dynamic data binding
- Batch video generation (100+ videos from data)

**Use Sora/Veo Instead for:**
- Realistic footage with people, faces, emotions
- Cinematic scenes, landscapes, environments
- Product in real-world environments (UGC-style)
- Authentic content requiring AI generation
- Complex motion that's hard to animate manually

## Combined Pipeline (Remotion + AI Video)

```
┌─────────────────────────────────────────────────────────────┐
│                    video-producer Agent                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐   │
│  │   Sora 2    │   │   Veo 3.1   │   │    Remotion     │   │
│  │  (Budget)   │   │  (Premium)  │   │ (Motion/Edit)   │   │
│  └──────┬──────┘   └──────┬──────┘   └────────┬────────┘   │
│         │                 │                    │            │
│         ▼                 ▼                    ▼            │
│  ┌──────────────────────────────────────────────────┐      │
│  │              OUTPUT: MP4 Videos                  │      │
│  │  • AI footage (Sora/Veo)                         │      │
│  │  • Motion graphics (Remotion)                    │      │
│  │  • Combined: AI clips + Remotion editing         │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

**Typical Combined Workflow:**
1. Generate AI footage with Sora/Veo (product demo, UGC scene)
2. Use Remotion to add branded intro (3 sec)
3. Use Remotion to add animated captions overlay
4. Use Remotion to add outro with CTA
5. Render final composite video

---

## Quick Start

### Project Setup

```bash
# Create new Remotion project
npx create-video@latest my-video

# Or add to existing project
npm install remotion @remotion/cli @remotion/bundler

# Start development server
npm run dev

# Render video
npx remotion render src/index.tsx MyComposition out/video.mp4
```

### Project Structure

```
my-video/
├── src/
│   ├── Root.tsx              # Root component with compositions
│   ├── Composition.tsx       # Main video component
│   ├── components/           # Reusable components
│   │   ├── Intro.tsx
│   │   ├── Caption.tsx
│   │   └── Outro.tsx
│   └── index.tsx             # Entry point
├── public/                   # Static assets (images, fonts, AI clips)
├── remotion.config.ts        # Build configuration
└── package.json
```

### Basic Configuration (remotion.config.ts)

```typescript
import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
```

---

## Core Concepts

### 1. Composition

A `<Composition>` defines a video's metadata: dimensions, frame rate, duration.

```tsx
import { Composition } from "remotion";
import { MyVideo } from "./MyVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MyVideo"
        component={MyVideo}
        durationInFrames={300}    // 10 seconds at 30fps
        fps={30}
        width={1920}
        height={1080}
      />

      {/* TikTok vertical format */}
      <Composition
        id="TikTokVideo"
        component={MyVideo}
        durationInFrames={240}    // 8 seconds
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};
```

### 2. useCurrentFrame & useVideoConfig

Access current frame and video settings in any component.

```tsx
import { useCurrentFrame, useVideoConfig } from "remotion";

export const MyComponent: React.FC = () => {
  const frame = useCurrentFrame();           // Current frame (0, 1, 2, ...)
  const { fps, durationInFrames, width, height } = useVideoConfig();

  // Convert frame to seconds
  const seconds = frame / fps;

  return (
    <div style={{ fontSize: 48 }}>
      Frame: {frame} | Time: {seconds.toFixed(2)}s
    </div>
  );
};
```

### 3. Sequence

`<Sequence>` controls when components appear and for how long.

```tsx
import { Sequence } from "remotion";

export const MyVideo: React.FC = () => {
  return (
    <>
      {/* Intro: frames 0-90 (0-3 seconds) */}
      <Sequence from={0} durationInFrames={90}>
        <Intro />
      </Sequence>

      {/* Main content: frames 90-270 (3-9 seconds) */}
      <Sequence from={90} durationInFrames={180}>
        <MainContent />
      </Sequence>

      {/* Outro: frames 270-300 (9-10 seconds) */}
      <Sequence from={270}>
        <Outro />
      </Sequence>
    </>
  );
};
```

### 4. interpolate

The `interpolate` function maps frame numbers to animated values.

```tsx
import { interpolate, useCurrentFrame } from "remotion";

export const FadeIn: React.FC = () => {
  const frame = useCurrentFrame();

  // Fade in from 0 to 1 over first 30 frames
  const opacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: "clamp",  // Don't go above 1
  });

  // Slide in from -100 to 0 over first 30 frames
  const translateX = interpolate(frame, [0, 30], [-100, 0], {
    extrapolateRight: "clamp",
  });

  return (
    <div style={{
      opacity,
      transform: `translateX(${translateX}px)`
    }}>
      Hello World
    </div>
  );
};
```

**Easing Functions:**

```tsx
import { interpolate, Easing } from "remotion";

// Ease out (fast start, slow end)
const value = interpolate(frame, [0, 30], [0, 100], {
  easing: Easing.out(Easing.ease),
});

// Ease in-out (slow start and end)
const value2 = interpolate(frame, [0, 30], [0, 100], {
  easing: Easing.inOut(Easing.cubic),
});

// Bounce
const value3 = interpolate(frame, [0, 30], [0, 100], {
  easing: Easing.bounce,
});
```

### 5. spring

Spring physics for natural-feeling animations.

```tsx
import { spring, useCurrentFrame, useVideoConfig } from "remotion";

export const SpringAnimation: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Spring animation starting at frame 0
  const scale = spring({
    frame,
    fps,
    from: 0,
    to: 1,
    config: {
      damping: 10,      // Lower = more bouncy
      stiffness: 100,   // Higher = faster
      mass: 1,          // Higher = slower, more momentum
    },
  });

  return (
    <div style={{ transform: `scale(${scale})` }}>
      Bouncy!
    </div>
  );
};
```

---

## Common Patterns

### Branded Intro Template

```tsx
import { AbsoluteFill, Sequence, spring, useCurrentFrame, useVideoConfig } from "remotion";

interface IntroProps {
  logoSrc: string;
  companyName: string;
  tagline?: string;
  brandColor?: string;
}

export const BrandedIntro: React.FC<IntroProps> = ({
  logoSrc,
  companyName,
  tagline = "",
  brandColor = "#4F46E5",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Logo scale with spring
  const logoScale = spring({
    frame,
    fps,
    from: 0,
    to: 1,
    config: { damping: 12, stiffness: 200 },
  });

  // Company name fade in (delayed)
  const nameOpacity = interpolate(frame, [20, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Tagline slide up (more delayed)
  const taglineY = interpolate(frame, [35, 55], [20, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const taglineOpacity = interpolate(frame, [35, 55], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{
      backgroundColor: brandColor,
      justifyContent: "center",
      alignItems: "center",
    }}>
      {/* Logo */}
      <img
        src={logoSrc}
        style={{
          width: 200,
          height: 200,
          transform: `scale(${logoScale})`,
        }}
      />

      {/* Company Name */}
      <h1 style={{
        color: "white",
        fontSize: 72,
        fontWeight: "bold",
        marginTop: 30,
        opacity: nameOpacity,
      }}>
        {companyName}
      </h1>

      {/* Tagline */}
      {tagline && (
        <p style={{
          color: "rgba(255,255,255,0.8)",
          fontSize: 24,
          opacity: taglineOpacity,
          transform: `translateY(${taglineY}px)`,
        }}>
          {tagline}
        </p>
      )}
    </AbsoluteFill>
  );
};
```

### TikTok-Style Caption Overlay

```tsx
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

interface CaptionWord {
  text: string;
  startFrame: number;
  endFrame: number;
}

interface CaptionOverlayProps {
  words: CaptionWord[];
  highlightColor?: string;
}

export const CaptionOverlay: React.FC<CaptionOverlayProps> = ({
  words,
  highlightColor = "#FFFF00",
}) => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{
      justifyContent: "flex-end",
      alignItems: "center",
      paddingBottom: 150,
    }}>
      <div style={{
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        maxWidth: "80%",
        gap: "8px",
      }}>
        {words.map((word, i) => {
          const isActive = frame >= word.startFrame && frame <= word.endFrame;
          const scale = isActive
            ? interpolate(
                frame,
                [word.startFrame, word.startFrame + 5],
                [1, 1.2],
                { extrapolateRight: "clamp" }
              )
            : 1;

          return (
            <span
              key={i}
              style={{
                fontSize: 48,
                fontWeight: "bold",
                color: isActive ? highlightColor : "white",
                textShadow: "2px 2px 8px rgba(0,0,0,0.8)",
                transform: `scale(${scale})`,
                transition: "color 0.1s",
              }}
            >
              {word.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// Usage with Whisper transcript
const captionWords: CaptionWord[] = [
  { text: "This", startFrame: 0, endFrame: 15 },
  { text: "product", startFrame: 15, endFrame: 30 },
  { text: "changed", startFrame: 30, endFrame: 45 },
  { text: "my", startFrame: 45, endFrame: 55 },
  { text: "life!", startFrame: 55, endFrame: 75 },
];
```

### Animated Data Visualization

```tsx
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

interface BarChartProps {
  data: { label: string; value: number; color: string }[];
  animationDelay?: number;  // Frames between each bar animation
}

export const AnimatedBarChart: React.FC<BarChartProps> = ({
  data,
  animationDelay = 10,
}) => {
  const frame = useCurrentFrame();
  const maxValue = Math.max(...data.map(d => d.value));

  return (
    <AbsoluteFill style={{
      backgroundColor: "#1a1a2e",
      padding: 60,
      justifyContent: "center",
    }}>
      {data.map((item, index) => {
        const startFrame = index * animationDelay;
        const progress = interpolate(
          frame,
          [startFrame, startFrame + 30],
          [0, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );

        const barWidth = (item.value / maxValue) * 100 * progress;

        return (
          <div key={index} style={{ marginBottom: 20 }}>
            <div style={{ color: "white", marginBottom: 8, fontSize: 20 }}>
              {item.label}
            </div>
            <div style={{
              height: 40,
              width: `${barWidth}%`,
              backgroundColor: item.color,
              borderRadius: 4,
              display: "flex",
              alignItems: "center",
              justifyContent: "flex-end",
              paddingRight: 10,
            }}>
              <span style={{ color: "white", fontWeight: "bold" }}>
                {Math.round(item.value * progress)}
              </span>
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
```

### Video Composition (Combining AI Clips + Graphics)

```tsx
import { AbsoluteFill, Sequence, Video, staticFile } from "remotion";
import { BrandedIntro } from "./BrandedIntro";
import { CaptionOverlay } from "./CaptionOverlay";
import { CallToAction } from "./CallToAction";

interface FullVideoProps {
  aiClipPath: string;      // Path to Sora/Veo generated clip
  introLogo: string;
  captions: CaptionWord[];
  ctaText: string;
}

export const FullVideo: React.FC<FullVideoProps> = ({
  aiClipPath,
  introLogo,
  captions,
  ctaText,
}) => {
  // Total: 3s intro + 8s AI clip + 2s outro = 13s @ 30fps = 390 frames

  return (
    <AbsoluteFill>
      {/* AI-generated clip as background (full duration) */}
      <Video
        src={staticFile(aiClipPath)}
        style={{ width: "100%", height: "100%" }}
      />

      {/* Branded intro overlay (first 3 seconds) */}
      <Sequence from={0} durationInFrames={90}>
        <BrandedIntro
          logoSrc={staticFile(introLogo)}
          companyName="Brand Name"
          brandColor="#4F46E5"
        />
      </Sequence>

      {/* Caption overlay during main content */}
      <Sequence from={90} durationInFrames={240}>
        <CaptionOverlay words={captions} />
      </Sequence>

      {/* Call-to-action outro (last 2 seconds) */}
      <Sequence from={330}>
        <CallToAction text={ctaText} />
      </Sequence>
    </AbsoluteFill>
  );
};
```

---

## Working with External Assets

### Images

```tsx
import { Img, staticFile } from "remotion";

// From public/ folder
<Img src={staticFile("logo.png")} />

// From URL
<Img src="https://example.com/image.png" />
```

### Videos (AI-generated clips)

```tsx
import { Video, staticFile, OffthreadVideo } from "remotion";

// Basic video
<Video src={staticFile("ai-clip.mp4")} />

// OffthreadVideo for better performance with multiple videos
<OffthreadVideo src={staticFile("ai-clip.mp4")} />

// With start/end times (trimming)
<Video
  src={staticFile("ai-clip.mp4")}
  startFrom={30}        // Start at frame 30 of source
  endAt={90}            // End at frame 90 of source
/>
```

### Audio

```tsx
import { Audio, staticFile } from "remotion";

// Background music
<Audio src={staticFile("music.mp3")} volume={0.5} />

// Voiceover with start time
<Sequence from={30}>
  <Audio src={staticFile("voiceover.mp3")} />
</Sequence>
```

### Fonts

```tsx
// In your component or global CSS
import { loadFont } from "@remotion/google-fonts/Inter";

const { fontFamily } = loadFont();

// Use in styles
<div style={{ fontFamily }}>Text with Inter font</div>
```

---

## Rendering

### CLI Rendering

```bash
# Render to MP4
npx remotion render src/index.tsx CompositionId out/video.mp4

# Render with custom settings
npx remotion render src/index.tsx CompositionId out/video.mp4 \
  --codec h264 \
  --crf 18 \
  --fps 30

# Render specific frame range
npx remotion render src/index.tsx CompositionId out/video.mp4 \
  --frames 0-90

# Render with props
npx remotion render src/index.tsx CompositionId out/video.mp4 \
  --props '{"title": "My Video", "color": "#FF0000"}'
```

### Programmatic Rendering

```typescript
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";

const bundled = await bundle({
  entryPoint: require.resolve("./src/index.tsx"),
});

const composition = await selectComposition({
  serveUrl: bundled,
  id: "MyComposition",
});

await renderMedia({
  composition,
  serveUrl: bundled,
  codec: "h264",
  outputLocation: "out/video.mp4",
});
```

---

## Integration with video-producer Workflow

### Workflow 1: Pure Remotion (Motion Graphics)

```
User: "Create animated intro with our logo"
→ video-producer uses Remotion skill
→ Writes React component with spring animations
→ Renders to MP4
→ Uploads to Drive
```

### Workflow 2: AI + Remotion (Post-Production)

```
User: "Create product video with branded intro and captions"
→ video-producer:
  1. Generate product demo with Veo UGC ($6)
  2. Write Remotion composition:
     - 3s branded intro (Remotion)
     - 8s AI clip (Video component)
     - Caption overlay (Remotion)
     - 2s CTA outro (Remotion)
  3. Render composite video
  4. Upload final video to Drive
```

### Workflow 3: Batch Template Generation

```
User: "Generate 50 personalized video ads from this CSV"
→ video-producer uses Remotion skill
→ Creates template with dynamic props
→ Renders 50 variations with different data
→ Uploads batch to Drive folder
```

---

## Best Practices

### Performance

1. **Use OffthreadVideo** for multiple video sources
2. **Preload assets** with `prefetch()` for faster rendering
3. **Avoid expensive calculations** in render - memoize with `useMemo`
4. **Use PNG over SVG** for complex graphics during render

### Animation Quality

1. **60fps for smooth motion** (or 30fps for standard)
2. **Use spring for natural feel** instead of linear interpolation
3. **Ease animations** - never use linear for UI motion
4. **Stagger animations** for visual interest

### Code Organization

1. **One component per animation** - keeps code manageable
2. **Use props for customization** - enables templates
3. **Extract timing to constants** - easier to adjust
4. **Create a shared styles file** - consistent branding

### Common Timing Patterns

```typescript
// Frame rate: 30fps
const SECOND = 30;

// Common durations
const INTRO_DURATION = 3 * SECOND;      // 90 frames
const MAIN_CONTENT = 8 * SECOND;        // 240 frames
const OUTRO_DURATION = 2 * SECOND;      // 60 frames

// Animation durations
const FADE_DURATION = 0.5 * SECOND;     // 15 frames
const SLIDE_DURATION = 0.75 * SECOND;   // 22 frames
const SPRING_SETTLE = 1 * SECOND;       // 30 frames
```

---

## Reference Documentation

- **API Reference:** `references/api-reference.md`
- **Animation Patterns:** `references/animation-patterns.md`
- **Templates:**
  - `templates/branded-intro.md` - Intro animation template
  - `templates/caption-overlay.md` - TikTok-style captions
  - `templates/product-showcase.md` - Product demo template

---

## External Resources

- [Remotion Documentation](https://www.remotion.dev/docs/)
- [Remotion Examples](https://www.remotion.dev/docs/examples)
- [Remotion GitHub](https://github.com/remotion-dev/remotion)
- [Remotion Templates](https://www.remotion.dev/templates)
