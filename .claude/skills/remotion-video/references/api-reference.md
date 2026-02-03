# Remotion API Quick Reference

## Core Hooks

### useCurrentFrame()

Returns the current frame number (0-indexed).

```tsx
import { useCurrentFrame } from "remotion";

const frame = useCurrentFrame();  // 0, 1, 2, ...
```

### useVideoConfig()

Returns video configuration object.

```tsx
import { useVideoConfig } from "remotion";

const {
  fps,              // Frames per second (e.g., 30)
  durationInFrames, // Total frames
  width,            // Video width in pixels
  height,           // Video height in pixels
  id,               // Composition ID
  defaultProps,     // Default props
} = useVideoConfig();

// Common calculations
const durationInSeconds = durationInFrames / fps;
const currentTime = frame / fps;
```

---

## Animation Functions

### interpolate()

Maps an input range to an output range.

```tsx
import { interpolate } from "remotion";

// Basic usage
const opacity = interpolate(
  frame,           // Input value
  [0, 30],         // Input range
  [0, 1],          // Output range
);

// With options
const value = interpolate(frame, [0, 30], [0, 100], {
  extrapolateLeft: "clamp",   // "clamp" | "wrap" | "identity" | "extend"
  extrapolateRight: "clamp",
  easing: Easing.ease,        // Optional easing function
});
```

**Extrapolation Options:**
- `"clamp"` - Clamp to output range (most common)
- `"extend"` - Continue linearly beyond range
- `"identity"` - Return input value unchanged
- `"wrap"` - Wrap around range

### spring()

Physics-based spring animation.

```tsx
import { spring, useCurrentFrame, useVideoConfig } from "remotion";

const frame = useCurrentFrame();
const { fps } = useVideoConfig();

const value = spring({
  frame,
  fps,
  from: 0,           // Start value (optional, default: 0)
  to: 1,             // End value (optional, default: 1)
  durationInFrames: 60,  // Optional, otherwise animates until settled
  config: {
    damping: 10,     // Lower = more bouncy (default: 10)
    stiffness: 100,  // Higher = faster (default: 100)
    mass: 1,         // Higher = slower, more momentum (default: 1)
    overshootClamping: false,  // Clamp to target value
  },
});
```

**Common Presets:**

```tsx
// Bouncy (UI elements)
{ damping: 8, stiffness: 200, mass: 0.5 }

// Gentle (fade-ins)
{ damping: 20, stiffness: 80, mass: 1 }

// Snappy (buttons, interactions)
{ damping: 15, stiffness: 300, mass: 0.8 }

// Heavy (large elements)
{ damping: 12, stiffness: 60, mass: 2 }
```

---

## Easing Functions

```tsx
import { Easing, interpolate } from "remotion";

// Built-in easing
Easing.linear      // No easing
Easing.ease        // Subtle ease
Easing.quad        // Quadratic
Easing.cubic       // Cubic
Easing.sin         // Sinusoidal
Easing.circle      // Circular
Easing.exp         // Exponential
Easing.bounce      // Bounce effect
Easing.back        // Overshoot
Easing.elastic     // Elastic/springy

// Modifiers
Easing.in(Easing.ease)      // Apply to start
Easing.out(Easing.ease)     // Apply to end
Easing.inOut(Easing.ease)   // Apply to both

// Example usage
const value = interpolate(frame, [0, 30], [0, 100], {
  easing: Easing.out(Easing.cubic),
});
```

**Bezier Curves:**

```tsx
const easing = Easing.bezier(0.25, 0.1, 0.25, 1);  // CSS ease
const easing2 = Easing.bezier(0.4, 0, 0.2, 1);    // Material Design
```

---

## Layout Components

### AbsoluteFill

Full-size container positioned absolutely.

```tsx
import { AbsoluteFill } from "remotion";

<AbsoluteFill style={{
  backgroundColor: "#000",
  justifyContent: "center",
  alignItems: "center",
}}>
  <h1>Centered Content</h1>
</AbsoluteFill>
```

### Sequence

Controls timing of child components.

```tsx
import { Sequence } from "remotion";

<Sequence
  from={0}              // Start frame
  durationInFrames={90} // Duration (optional, until end if omitted)
  name="Intro"          // Debug name (optional)
  layout="none"         // "none" | "absolute-fill" (default)
>
  <Intro />
</Sequence>
```

**Nested Sequences:**

```tsx
// Inner sequence frame count resets to 0
<Sequence from={30}>
  {/* frame here is relative to sequence start */}
  <Sequence from={0} durationInFrames={30}>
    <Part1 />
  </Sequence>
  <Sequence from={30}>
    <Part2 />
  </Sequence>
</Sequence>
```

### Series

Sequences in series (auto-calculates start times).

```tsx
import { Series } from "remotion";

<Series>
  <Series.Sequence durationInFrames={60}>
    <Part1 />
  </Series.Sequence>
  <Series.Sequence durationInFrames={90}>
    <Part2 />
  </Series.Sequence>
  <Series.Sequence durationInFrames={60}>
    <Part3 />
  </Series.Sequence>
</Series>
```

---

## Media Components

### Img

Image component with preloading.

```tsx
import { Img, staticFile } from "remotion";

// From public/ folder
<Img src={staticFile("logo.png")} />

// From URL
<Img src="https://example.com/image.png" />

// With styles
<Img
  src={staticFile("photo.jpg")}
  style={{ width: 300, borderRadius: 8 }}
/>
```

### Video

Embed video files.

```tsx
import { Video, staticFile } from "remotion";

<Video
  src={staticFile("clip.mp4")}
  startFrom={0}          // Start frame of source video
  endAt={90}             // End frame of source video
  volume={1}             // 0-1
  muted={false}
  playbackRate={1}       // Speed multiplier
  style={{ width: "100%" }}
/>
```

### OffthreadVideo

Better performance for multiple videos.

```tsx
import { OffthreadVideo, staticFile } from "remotion";

<OffthreadVideo
  src={staticFile("background.mp4")}
  style={{ width: "100%", height: "100%" }}
/>
```

### Audio

Audio component.

```tsx
import { Audio, staticFile } from "remotion";

<Audio
  src={staticFile("music.mp3")}
  volume={0.5}           // 0-1 or function: (f) => Math.min(1, f / 30)
  startFrom={0}          // Start frame
  endAt={300}            // End frame
  muted={false}
  playbackRate={1}
/>

// Volume fade
<Audio
  src={staticFile("music.mp3")}
  volume={(f) =>
    interpolate(f, [0, 30, 270, 300], [0, 0.8, 0.8, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  }
/>
```

---

## Static Files

### staticFile()

Reference files in `public/` folder.

```tsx
import { staticFile } from "remotion";

const logoPath = staticFile("images/logo.png");
// Returns: "/images/logo.png" (during preview)
// Returns: absolute path (during render)
```

### prefetch()

Preload assets for faster rendering.

```tsx
import { prefetch, staticFile } from "remotion";

// In component
useEffect(() => {
  const { free } = prefetch(staticFile("large-video.mp4"));
  return () => free();
}, []);
```

---

## Utility Functions

### random()

Deterministic random number (same across renders).

```tsx
import { random } from "remotion";

const value = random("my-seed");           // 0-1
const value2 = random("seed", 0, 100);     // 0-100
const value3 = random(`particle-${i}`);    // Per-particle seed
```

### measureText()

Measure text dimensions.

```tsx
import { measureText } from "@remotion/layout-utils";

const { width, height } = measureText({
  text: "Hello World",
  fontFamily: "Arial",
  fontSize: 48,
  fontWeight: "bold",
});
```

### delayRender() / continueRender()

Pause render until async operation completes.

```tsx
import { delayRender, continueRender } from "remotion";

useEffect(() => {
  const handle = delayRender();

  fetchData().then((data) => {
    setData(data);
    continueRender(handle);
  });
}, []);
```

---

## Common Resolution Presets

```tsx
// Standard HD (YouTube, general)
{ width: 1920, height: 1080 }

// Vertical/Mobile (TikTok, Instagram Reels)
{ width: 1080, height: 1920 }

// Square (Instagram, LinkedIn)
{ width: 1080, height: 1080 }

// 4K
{ width: 3840, height: 2160 }

// 720p (faster renders)
{ width: 1280, height: 720 }
```

---

## TypeScript Interfaces

```typescript
// Composition props
interface CompositionProps {
  title: string;
  subtitle?: string;
  backgroundColor: string;
}

// Caption word
interface CaptionWord {
  text: string;
  startFrame: number;
  endFrame: number;
}

// Data point for charts
interface DataPoint {
  label: string;
  value: number;
  color: string;
}

// Video segment
interface VideoSegment {
  src: string;
  startFrame: number;
  durationInFrames: number;
}
```

---

## CLI Commands

```bash
# Development
npm run dev                    # Start preview server
npx remotion studio           # Open Remotion Studio

# Rendering
npx remotion render src/index.tsx CompositionId out.mp4
npx remotion render src/index.tsx CompositionId out.mp4 --codec h264
npx remotion render src/index.tsx CompositionId out.mp4 --crf 18
npx remotion render src/index.tsx CompositionId out.mp4 --frames 0-90

# With props
npx remotion render src/index.tsx CompositionId out.mp4 \
  --props '{"title":"Hello"}'

# Still image
npx remotion still src/index.tsx CompositionId out.png --frame 30

# Lambda (serverless)
npx remotion lambda render ...
```
