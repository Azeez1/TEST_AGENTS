# Branded Intro Template

A professional, customizable intro animation for consistent branding across all videos.

## Preview

```
[Frame 0-15]   Logo scales in with spring animation
[Frame 15-30]  Company name fades in
[Frame 30-45]  Tagline slides up
[Frame 45-90]  Hold for beat, then ready for transition
```

## Full Component

```tsx
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

interface BrandedIntroProps {
  /**
   * Path to logo image in public/ folder
   * @example "logo.png"
   */
  logoSrc: string;

  /**
   * Company or brand name
   */
  companyName: string;

  /**
   * Optional tagline displayed below company name
   */
  tagline?: string;

  /**
   * Primary brand color (hex)
   * @default "#4F46E5" (indigo)
   */
  brandColor?: string;

  /**
   * Secondary color for accents
   * @default "rgba(255,255,255,0.8)"
   */
  accentColor?: string;

  /**
   * Logo size in pixels
   * @default 180
   */
  logoSize?: number;

  /**
   * Animation style preset
   * @default "spring"
   */
  animationStyle?: "spring" | "smooth" | "bouncy" | "elegant";
}

export const BrandedIntro: React.FC<BrandedIntroProps> = ({
  logoSrc,
  companyName,
  tagline,
  brandColor = "#4F46E5",
  accentColor = "rgba(255,255,255,0.8)",
  logoSize = 180,
  animationStyle = "spring",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Animation config based on style
  const springConfig = {
    spring: { damping: 12, stiffness: 200, mass: 1 },
    smooth: { damping: 20, stiffness: 100, mass: 1 },
    bouncy: { damping: 8, stiffness: 250, mass: 0.5 },
    elegant: { damping: 15, stiffness: 80, mass: 1.2 },
  }[animationStyle];

  // Logo animation - scale in with spring
  const logoScale = spring({
    frame,
    fps,
    from: 0,
    to: 1,
    config: springConfig,
  });

  const logoRotation = spring({
    frame,
    fps,
    from: -10,
    to: 0,
    config: { ...springConfig, stiffness: springConfig.stiffness * 0.5 },
  });

  // Company name - fade and slide in (delayed)
  const nameOpacity = interpolate(frame, [20, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const nameY = interpolate(frame, [20, 40], [15, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Tagline - fade and slide up (more delayed)
  const taglineOpacity = interpolate(frame, [35, 55], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const taglineY = interpolate(frame, [35, 55], [20, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Subtle background glow animation
  const glowOpacity = interpolate(frame, [0, 45, 90], [0, 0.3, 0.2], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: brandColor,
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
      }}
    >
      {/* Background glow effect */}
      <div
        style={{
          position: "absolute",
          width: "150%",
          height: "150%",
          background: `radial-gradient(circle, white ${glowOpacity * 100}%, transparent 70%)`,
          opacity: glowOpacity,
        }}
      />

      {/* Logo */}
      <Img
        src={staticFile(logoSrc)}
        style={{
          width: logoSize,
          height: logoSize,
          objectFit: "contain",
          transform: `scale(${logoScale}) rotate(${logoRotation}deg)`,
        }}
      />

      {/* Company Name */}
      <h1
        style={{
          color: "white",
          fontSize: 64,
          fontWeight: 700,
          fontFamily: "system-ui, -apple-system, sans-serif",
          marginTop: 24,
          opacity: nameOpacity,
          transform: `translateY(${nameY}px)`,
          textShadow: "0 2px 10px rgba(0,0,0,0.2)",
          letterSpacing: "-0.02em",
        }}
      >
        {companyName}
      </h1>

      {/* Tagline */}
      {tagline && (
        <p
          style={{
            color: accentColor,
            fontSize: 24,
            fontWeight: 400,
            fontFamily: "system-ui, -apple-system, sans-serif",
            marginTop: 8,
            opacity: taglineOpacity,
            transform: `translateY(${taglineY}px)`,
          }}
        >
          {tagline}
        </p>
      )}
    </AbsoluteFill>
  );
};
```

## Usage in Composition

```tsx
import { Composition } from "remotion";
import { BrandedIntro } from "./BrandedIntro";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 3-second intro at 30fps */}
      <Composition
        id="BrandedIntro"
        component={BrandedIntro}
        durationInFrames={90}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          logoSrc: "logo.png",
          companyName: "Your Brand",
          tagline: "Innovation Redefined",
          brandColor: "#4F46E5",
        }}
      />

      {/* TikTok vertical format */}
      <Composition
        id="BrandedIntroVertical"
        component={BrandedIntro}
        durationInFrames={90}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          logoSrc: "logo.png",
          companyName: "Your Brand",
          tagline: "Innovation Redefined",
          brandColor: "#4F46E5",
          logoSize: 150,
        }}
      />
    </>
  );
};
```

## Variations

### Minimal (Logo Only)

```tsx
<BrandedIntro
  logoSrc="logo.png"
  companyName=""
  brandColor="#000000"
  logoSize={250}
  animationStyle="elegant"
/>
```

### Corporate

```tsx
<BrandedIntro
  logoSrc="logo.png"
  companyName="Acme Corporation"
  tagline="Building Tomorrow, Today"
  brandColor="#1E3A5F"
  animationStyle="smooth"
/>
```

### Playful/Startup

```tsx
<BrandedIntro
  logoSrc="logo.png"
  companyName="StartupName"
  tagline="Move Fast. Build Things."
  brandColor="#FF6B6B"
  animationStyle="bouncy"
/>
```

### Luxury/Premium

```tsx
<BrandedIntro
  logoSrc="logo-gold.png"
  companyName="LUXE"
  tagline="Timeless Elegance"
  brandColor="#1A1A1A"
  accentColor="#C9A962"
  animationStyle="elegant"
  logoSize={200}
/>
```

## Customization Options

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `logoSrc` | string | required | Path to logo in public/ folder |
| `companyName` | string | required | Brand name text |
| `tagline` | string | undefined | Optional tagline text |
| `brandColor` | string | "#4F46E5" | Background color (hex) |
| `accentColor` | string | "rgba(255,255,255,0.8)" | Tagline text color |
| `logoSize` | number | 180 | Logo dimensions in pixels |
| `animationStyle` | string | "spring" | Animation preset |

## Animation Styles

| Style | Damping | Stiffness | Feel |
|-------|---------|-----------|------|
| `spring` | 12 | 200 | Balanced, professional |
| `smooth` | 20 | 100 | Subtle, understated |
| `bouncy` | 8 | 250 | Energetic, playful |
| `elegant` | 15 | 80 | Slow, luxurious |

## Extending the Template

### Add Particle Effect

```tsx
import { Confetti } from "./particles/Confetti";

// Inside BrandedIntro component, add after tagline:
<Sequence from={60}>
  <Confetti count={30} colors={["#fff", brandColor]} />
</Sequence>
```

### Add Sound Effect

```tsx
import { Audio, staticFile } from "remotion";

// Add audio for intro sound
<Audio
  src={staticFile("intro-whoosh.mp3")}
  volume={0.5}
/>
```

### Add Animated Underline

```tsx
// Below company name
const underlineWidth = interpolate(frame, [40, 60], [0, 100], {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
});

<div
  style={{
    width: `${underlineWidth}%`,
    height: 3,
    backgroundColor: accentColor,
    marginTop: 8,
    borderRadius: 2,
  }}
/>
```

## Integration with Video Pipeline

```tsx
import { AbsoluteFill, Sequence, Video, staticFile } from "remotion";
import { BrandedIntro } from "./BrandedIntro";

export const FullVideo: React.FC<{ aiClipPath: string }> = ({ aiClipPath }) => {
  return (
    <AbsoluteFill>
      {/* Branded Intro (first 3 seconds) */}
      <Sequence from={0} durationInFrames={90}>
        <BrandedIntro
          logoSrc="logo.png"
          companyName="Brand Name"
          tagline="Your Tagline Here"
          brandColor="#4F46E5"
        />
      </Sequence>

      {/* AI-generated content (after intro) */}
      <Sequence from={90}>
        <Video src={staticFile(aiClipPath)} />
      </Sequence>
    </AbsoluteFill>
  );
};
```

## Render Command

```bash
# Render branded intro
npx remotion render src/index.tsx BrandedIntro intro.mp4

# With custom props
npx remotion render src/index.tsx BrandedIntro intro.mp4 \
  --props '{"logoSrc":"my-logo.png","companyName":"My Brand","brandColor":"#FF0000"}'
```
