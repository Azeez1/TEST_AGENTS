# Caption Overlay Template

TikTok/Instagram-style animated captions with word-by-word highlighting. Perfect for adding engaging text overlays to AI-generated video content.

## Preview

```
[Word 1 highlighted]  "This"
[Word 2 highlighted]  "This product"
[Word 3 highlighted]  "This product changed"
[Word 4 highlighted]  "This product changed my"
[Word 5 highlighted]  "This product changed my life!"
```

## Full Component

```tsx
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

/**
 * Represents a single word in the caption with timing
 */
interface CaptionWord {
  /** The word text */
  text: string;
  /** Frame when this word becomes active */
  startFrame: number;
  /** Frame when this word stops being active */
  endFrame: number;
}

/**
 * Caption style presets
 */
type CaptionStyle = "tiktok" | "instagram" | "youtube" | "minimal" | "bold";

interface CaptionOverlayProps {
  /**
   * Array of words with timing information
   * Can be generated from Whisper transcription
   */
  words: CaptionWord[];

  /**
   * Color for highlighted (active) words
   * @default "#FFFF00" (yellow)
   */
  highlightColor?: string;

  /**
   * Color for non-active words
   * @default "#FFFFFF" (white)
   */
  textColor?: string;

  /**
   * Font size in pixels
   * @default 48
   */
  fontSize?: number;

  /**
   * Caption style preset
   * @default "tiktok"
   */
  style?: CaptionStyle;

  /**
   * Vertical position from bottom (percentage)
   * @default 15
   */
  bottomOffset?: number;

  /**
   * Maximum width as percentage of screen
   * @default 85
   */
  maxWidth?: number;

  /**
   * Show background behind captions
   * @default true
   */
  showBackground?: boolean;

  /**
   * Background color (with alpha)
   * @default "rgba(0,0,0,0.6)"
   */
  backgroundColor?: string;
}

export const CaptionOverlay: React.FC<CaptionOverlayProps> = ({
  words,
  highlightColor = "#FFFF00",
  textColor = "#FFFFFF",
  fontSize = 48,
  style = "tiktok",
  bottomOffset = 15,
  maxWidth = 85,
  showBackground = true,
  backgroundColor = "rgba(0,0,0,0.6)",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Style presets
  const styleConfig = {
    tiktok: {
      fontWeight: 800,
      textTransform: "uppercase" as const,
      letterSpacing: 2,
      scale: 1.15,
      shadowIntensity: 3,
    },
    instagram: {
      fontWeight: 700,
      textTransform: "none" as const,
      letterSpacing: 0,
      scale: 1.1,
      shadowIntensity: 2,
    },
    youtube: {
      fontWeight: 600,
      textTransform: "none" as const,
      letterSpacing: 0,
      scale: 1.05,
      shadowIntensity: 1,
    },
    minimal: {
      fontWeight: 500,
      textTransform: "none" as const,
      letterSpacing: 1,
      scale: 1,
      shadowIntensity: 1,
    },
    bold: {
      fontWeight: 900,
      textTransform: "uppercase" as const,
      letterSpacing: 4,
      scale: 1.2,
      shadowIntensity: 4,
    },
  }[style];

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: `${bottomOffset}%`,
      }}
    >
      {/* Optional background */}
      {showBackground && (
        <div
          style={{
            position: "absolute",
            bottom: `${bottomOffset - 2}%`,
            left: "50%",
            transform: "translateX(-50%)",
            backgroundColor,
            padding: "16px 24px",
            borderRadius: 12,
            maxWidth: `${maxWidth}%`,
          }}
        />
      )}

      {/* Caption container */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          maxWidth: `${maxWidth}%`,
          gap: "8px 12px",
          padding: "16px 24px",
        }}
      >
        {words.map((word, index) => {
          const isActive = frame >= word.startFrame && frame <= word.endFrame;
          const wasActive = frame > word.endFrame;

          // Scale animation for active word
          const scale = isActive
            ? spring({
                frame: frame - word.startFrame,
                fps,
                from: 1,
                to: styleConfig.scale,
                config: { damping: 12, stiffness: 300 },
              })
            : wasActive
              ? 1
              : 0.95;

          // Opacity for words not yet shown
          const opacity = frame >= word.startFrame ? 1 : 0.3;

          // Determine current color
          const color = isActive ? highlightColor : textColor;

          // Text shadow intensity based on style
          const shadow = `
            0 2px ${styleConfig.shadowIntensity * 2}px rgba(0,0,0,0.8),
            0 0 ${styleConfig.shadowIntensity * 4}px rgba(0,0,0,0.5)
          `;

          return (
            <span
              key={index}
              style={{
                fontSize,
                fontWeight: styleConfig.fontWeight,
                fontFamily: "system-ui, -apple-system, sans-serif",
                color,
                textShadow: shadow,
                transform: `scale(${scale})`,
                opacity,
                textTransform: styleConfig.textTransform,
                letterSpacing: styleConfig.letterSpacing,
                display: "inline-block",
                transition: "color 0.1s ease-out",
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
```

## Helper: Generate Caption Words from Text

```tsx
/**
 * Generates CaptionWord array from plain text
 * Useful when you don't have Whisper transcription
 */
export function generateCaptionWords(
  text: string,
  options: {
    startFrame?: number;
    framesPerWord?: number;
    holdFrames?: number;
  } = {}
): CaptionWord[] {
  const { startFrame = 0, framesPerWord = 12, holdFrames = 6 } = options;

  const words = text.split(/\s+/).filter(Boolean);

  return words.map((word, index) => ({
    text: word,
    startFrame: startFrame + index * framesPerWord,
    endFrame: startFrame + index * framesPerWord + framesPerWord + holdFrames,
  }));
}

// Usage:
const words = generateCaptionWords("This product changed my life!", {
  startFrame: 0,
  framesPerWord: 15,
  holdFrames: 8,
});
```

## Helper: Convert Whisper Transcript

```tsx
interface WhisperWord {
  word: string;
  start: number;  // seconds
  end: number;    // seconds
}

/**
 * Converts Whisper transcription to CaptionWord format
 */
export function whisperToCaptionWords(
  whisperWords: WhisperWord[],
  fps: number = 30
): CaptionWord[] {
  return whisperWords.map((w) => ({
    text: w.word.trim(),
    startFrame: Math.round(w.start * fps),
    endFrame: Math.round(w.end * fps),
  }));
}

// Usage with Whisper JSON:
const whisperOutput = [
  { word: "This", start: 0.0, end: 0.3 },
  { word: "product", start: 0.3, end: 0.7 },
  { word: "changed", start: 0.7, end: 1.1 },
  { word: "my", start: 1.1, end: 1.3 },
  { word: "life!", start: 1.3, end: 1.8 },
];

const captionWords = whisperToCaptionWords(whisperOutput, 30);
```

## Usage in Composition

```tsx
import { Composition } from "remotion";
import { CaptionOverlay, generateCaptionWords } from "./CaptionOverlay";

const demoWords = generateCaptionWords(
  "This product changed my life and I can't believe how amazing it is",
  { framesPerWord: 12 }
);

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="CaptionOverlay"
      component={CaptionOverlay}
      durationInFrames={180}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{
        words: demoWords,
        highlightColor: "#FFFF00",
        style: "tiktok",
      }}
    />
  );
};
```

## Style Variations

### TikTok Style

```tsx
<CaptionOverlay
  words={words}
  style="tiktok"
  highlightColor="#FFFF00"
  fontSize={52}
  bottomOffset={20}
/>
```

### Instagram Reels Style

```tsx
<CaptionOverlay
  words={words}
  style="instagram"
  highlightColor="#FF6B6B"
  textColor="#FFFFFF"
  fontSize={44}
  showBackground={true}
  backgroundColor="rgba(0,0,0,0.5)"
/>
```

### YouTube Shorts Style

```tsx
<CaptionOverlay
  words={words}
  style="youtube"
  highlightColor="#FF0000"
  textColor="#FFFFFF"
  fontSize={40}
  bottomOffset={10}
/>
```

### Minimal/Clean Style

```tsx
<CaptionOverlay
  words={words}
  style="minimal"
  highlightColor="#4F46E5"
  textColor="rgba(255,255,255,0.9)"
  fontSize={36}
  showBackground={false}
/>
```

### Bold/Impact Style

```tsx
<CaptionOverlay
  words={words}
  style="bold"
  highlightColor="#00FF00"
  textColor="#FFFFFF"
  fontSize={56}
  maxWidth={90}
/>
```

## Props Reference

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `words` | CaptionWord[] | required | Array of words with timing |
| `highlightColor` | string | "#FFFF00" | Active word color |
| `textColor` | string | "#FFFFFF" | Inactive word color |
| `fontSize` | number | 48 | Font size in pixels |
| `style` | CaptionStyle | "tiktok" | Style preset |
| `bottomOffset` | number | 15 | Position from bottom (%) |
| `maxWidth` | number | 85 | Max width (%) |
| `showBackground` | boolean | true | Show background box |
| `backgroundColor` | string | "rgba(0,0,0,0.6)" | Background color |

## Integration with AI Video

```tsx
import { AbsoluteFill, Sequence, Video, staticFile } from "remotion";
import { CaptionOverlay, whisperToCaptionWords } from "./CaptionOverlay";

// Whisper transcription from AI video
const transcript = [
  { word: "Watch", start: 0.0, end: 0.4 },
  { word: "how", start: 0.4, end: 0.6 },
  { word: "easy", start: 0.6, end: 0.9 },
  { word: "this", start: 0.9, end: 1.1 },
  { word: "is", start: 1.1, end: 1.4 },
  // ... more words
];

export const VideoWithCaptions: React.FC<{ videoPath: string }> = ({
  videoPath,
}) => {
  const captionWords = whisperToCaptionWords(transcript, 30);

  return (
    <AbsoluteFill>
      {/* AI-generated video (Sora/Veo) */}
      <Video src={staticFile(videoPath)} />

      {/* Caption overlay on top */}
      <CaptionOverlay
        words={captionWords}
        style="tiktok"
        highlightColor="#FFFF00"
      />
    </AbsoluteFill>
  );
};
```

## Advanced: Karaoke-Style (Line by Line)

```tsx
interface CaptionLine {
  text: string;
  startFrame: number;
  endFrame: number;
}

interface KaraokeCaptionProps {
  lines: CaptionLine[];
}

export const KaraokeCaption: React.FC<KaraokeCaptionProps> = ({ lines }) => {
  const frame = useCurrentFrame();

  // Find active line
  const activeLine = lines.find(
    (line) => frame >= line.startFrame && frame <= line.endFrame
  );

  if (!activeLine) return null;

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: "15%",
      }}
    >
      <div
        style={{
          fontSize: 42,
          fontWeight: 700,
          color: "#FFFFFF",
          textAlign: "center",
          padding: "16px 32px",
          backgroundColor: "rgba(0,0,0,0.7)",
          borderRadius: 8,
          maxWidth: "80%",
        }}
      >
        {activeLine.text}
      </div>
    </AbsoluteFill>
  );
};
```

## Render Command

```bash
# Render with captions
npx remotion render src/index.tsx CaptionOverlay captions.mp4

# With custom words via props file
npx remotion render src/index.tsx CaptionOverlay captions.mp4 \
  --props-from-file captions-data.json
```

## Tips for Best Results

1. **Timing:** Keep words visible for at least 10-15 frames (0.3-0.5 seconds)
2. **Font Size:** Larger for vertical videos (52-56px), smaller for landscape (40-44px)
3. **Contrast:** Ensure highlight color contrasts with both text color and video
4. **Position:** Keep captions in lower third to not obscure main content
5. **Background:** Use semi-transparent background if video has varied colors
