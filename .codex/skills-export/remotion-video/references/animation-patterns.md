# Remotion Animation Patterns

A collection of reusable animation patterns for common video production needs.

---

## Text Animations

### Typewriter Effect

```tsx
import { useCurrentFrame, useVideoConfig } from "remotion";

interface TypewriterProps {
  text: string;
  startFrame?: number;
  framesPerChar?: number;
}

export const Typewriter: React.FC<TypewriterProps> = ({
  text,
  startFrame = 0,
  framesPerChar = 3,
}) => {
  const frame = useCurrentFrame();
  const adjustedFrame = Math.max(0, frame - startFrame);
  const charsToShow = Math.floor(adjustedFrame / framesPerChar);
  const displayText = text.slice(0, charsToShow);

  return (
    <span style={{ fontFamily: "monospace" }}>
      {displayText}
      {charsToShow < text.length && (
        <span style={{ opacity: frame % 20 < 10 ? 1 : 0 }}>|</span>
      )}
    </span>
  );
};
```

### Word-by-Word Reveal

```tsx
import { interpolate, useCurrentFrame } from "remotion";

interface WordRevealProps {
  text: string;
  framesPerWord?: number;
}

export const WordReveal: React.FC<WordRevealProps> = ({
  text,
  framesPerWord = 8,
}) => {
  const frame = useCurrentFrame();
  const words = text.split(" ");

  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
      {words.map((word, index) => {
        const startFrame = index * framesPerWord;
        const opacity = interpolate(
          frame,
          [startFrame, startFrame + 10],
          [0, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );
        const y = interpolate(
          frame,
          [startFrame, startFrame + 10],
          [20, 0],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );

        return (
          <span
            key={index}
            style={{
              opacity,
              transform: `translateY(${y}px)`,
              display: "inline-block",
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};
```

### Character Stagger

```tsx
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

interface CharStaggerProps {
  text: string;
  delayPerChar?: number;
}

export const CharStagger: React.FC<CharStaggerProps> = ({
  text,
  delayPerChar = 2,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div style={{ display: "flex" }}>
      {text.split("").map((char, index) => {
        const delay = index * delayPerChar;
        const scale = spring({
          frame: frame - delay,
          fps,
          from: 0,
          to: 1,
          config: { damping: 10, stiffness: 200 },
        });

        return (
          <span
            key={index}
            style={{
              transform: `scale(${scale})`,
              display: "inline-block",
              minWidth: char === " " ? "0.25em" : undefined,
            }}
          >
            {char}
          </span>
        );
      })}
    </div>
  );
};
```

---

## Transition Effects

### Fade Transition

```tsx
import { AbsoluteFill, interpolate, useCurrentFrame, Sequence } from "remotion";

interface FadeTransitionProps {
  children: React.ReactNode;
  fadeInFrames?: number;
  fadeOutFrames?: number;
  durationInFrames: number;
}

export const FadeTransition: React.FC<FadeTransitionProps> = ({
  children,
  fadeInFrames = 15,
  fadeOutFrames = 15,
  durationInFrames,
}) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(
    frame,
    [0, fadeInFrames, durationInFrames - fadeOutFrames, durationInFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill style={{ opacity }}>
      {children}
    </AbsoluteFill>
  );
};
```

### Slide Transition

```tsx
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

type Direction = "left" | "right" | "up" | "down";

interface SlideTransitionProps {
  children: React.ReactNode;
  direction?: Direction;
  durationInFrames?: number;
}

export const SlideIn: React.FC<SlideTransitionProps> = ({
  children,
  direction = "left",
  durationInFrames = 20,
}) => {
  const frame = useCurrentFrame();

  const getTransform = () => {
    const progress = interpolate(frame, [0, durationInFrames], [100, 0], {
      extrapolateRight: "clamp",
    });

    switch (direction) {
      case "left": return `translateX(-${progress}%)`;
      case "right": return `translateX(${progress}%)`;
      case "up": return `translateY(-${progress}%)`;
      case "down": return `translateY(${progress}%)`;
    }
  };

  return (
    <AbsoluteFill style={{ transform: getTransform() }}>
      {children}
    </AbsoluteFill>
  );
};
```

### Scale Zoom Transition

```tsx
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

interface ZoomTransitionProps {
  children: React.ReactNode;
  type?: "in" | "out";
}

export const ZoomTransition: React.FC<ZoomTransitionProps> = ({
  children,
  type = "in",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({
    frame,
    fps,
    from: type === "in" ? 0 : 1.5,
    to: 1,
    config: { damping: 12, stiffness: 100 },
  });

  const opacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{
      transform: `scale(${scale})`,
      opacity,
    }}>
      {children}
    </AbsoluteFill>
  );
};
```

### Wipe Transition

```tsx
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

interface WipeTransitionProps {
  children: React.ReactNode;
  direction?: "left" | "right" | "up" | "down";
  durationInFrames?: number;
}

export const WipeIn: React.FC<WipeTransitionProps> = ({
  children,
  direction = "left",
  durationInFrames = 20,
}) => {
  const frame = useCurrentFrame();

  const progress = interpolate(frame, [0, durationInFrames], [0, 100], {
    extrapolateRight: "clamp",
  });

  const getClipPath = () => {
    switch (direction) {
      case "left": return `inset(0 ${100 - progress}% 0 0)`;
      case "right": return `inset(0 0 0 ${100 - progress}%)`;
      case "up": return `inset(0 0 ${100 - progress}% 0)`;
      case "down": return `inset(${100 - progress}% 0 0 0)`;
    }
  };

  return (
    <AbsoluteFill style={{ clipPath: getClipPath() }}>
      {children}
    </AbsoluteFill>
  );
};
```

---

## Motion Patterns

### Float/Hover Animation

```tsx
import { useCurrentFrame, useVideoConfig } from "remotion";

interface FloatProps {
  children: React.ReactNode;
  amplitude?: number;
  speed?: number;
}

export const Float: React.FC<FloatProps> = ({
  children,
  amplitude = 10,
  speed = 0.05,
}) => {
  const frame = useCurrentFrame();
  const y = Math.sin(frame * speed) * amplitude;

  return (
    <div style={{ transform: `translateY(${y}px)` }}>
      {children}
    </div>
  );
};
```

### Pulse Animation

```tsx
import { interpolate, useCurrentFrame } from "remotion";

interface PulseProps {
  children: React.ReactNode;
  minScale?: number;
  maxScale?: number;
  cycleFrames?: number;
}

export const Pulse: React.FC<PulseProps> = ({
  children,
  minScale = 1,
  maxScale = 1.1,
  cycleFrames = 30,
}) => {
  const frame = useCurrentFrame();
  const cycleProgress = (frame % cycleFrames) / cycleFrames;

  // Smooth sine wave for pulsing
  const scale = minScale + (maxScale - minScale) *
    (Math.sin(cycleProgress * Math.PI * 2) * 0.5 + 0.5);

  return (
    <div style={{ transform: `scale(${scale})` }}>
      {children}
    </div>
  );
};
```

### Shake Animation

```tsx
import { random, useCurrentFrame } from "remotion";

interface ShakeProps {
  children: React.ReactNode;
  intensity?: number;
  seed?: string;
}

export const Shake: React.FC<ShakeProps> = ({
  children,
  intensity = 5,
  seed = "shake",
}) => {
  const frame = useCurrentFrame();

  const x = (random(`${seed}-x-${frame}`) - 0.5) * intensity * 2;
  const y = (random(`${seed}-y-${frame}`) - 0.5) * intensity * 2;
  const rotation = (random(`${seed}-r-${frame}`) - 0.5) * intensity * 0.5;

  return (
    <div style={{
      transform: `translate(${x}px, ${y}px) rotate(${rotation}deg)`,
    }}>
      {children}
    </div>
  );
};
```

### Orbit Animation

```tsx
import { useCurrentFrame } from "remotion";

interface OrbitProps {
  children: React.ReactNode;
  radius?: number;
  speed?: number;
  startAngle?: number;
}

export const Orbit: React.FC<OrbitProps> = ({
  children,
  radius = 100,
  speed = 0.02,
  startAngle = 0,
}) => {
  const frame = useCurrentFrame();
  const angle = startAngle + frame * speed;

  const x = Math.cos(angle) * radius;
  const y = Math.sin(angle) * radius;

  return (
    <div style={{
      transform: `translate(${x}px, ${y}px)`,
      position: "absolute",
    }}>
      {children}
    </div>
  );
};
```

---

## UI Element Patterns

### Progress Bar

```tsx
import { interpolate, useCurrentFrame } from "remotion";

interface ProgressBarProps {
  progress: number;  // 0-1
  width?: number;
  height?: number;
  backgroundColor?: string;
  fillColor?: string;
  animationFrames?: number;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  width = 400,
  height = 20,
  backgroundColor = "#333",
  fillColor = "#4F46E5",
  animationFrames = 30,
}) => {
  const frame = useCurrentFrame();

  const animatedProgress = interpolate(
    frame,
    [0, animationFrames],
    [0, progress],
    { extrapolateRight: "clamp" }
  );

  return (
    <div style={{
      width,
      height,
      backgroundColor,
      borderRadius: height / 2,
      overflow: "hidden",
    }}>
      <div style={{
        width: `${animatedProgress * 100}%`,
        height: "100%",
        backgroundColor: fillColor,
        borderRadius: height / 2,
      }} />
    </div>
  );
};
```

### Countdown Timer

```tsx
import { useCurrentFrame, useVideoConfig } from "remotion";

interface CountdownProps {
  startNumber: number;
  fontSize?: number;
}

export const Countdown: React.FC<CountdownProps> = ({
  startNumber,
  fontSize = 120,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const seconds = Math.max(0, startNumber - Math.floor(frame / fps));
  const progress = (frame % fps) / fps;

  // Scale animation within each second
  const scale = 1 + (1 - progress) * 0.3;
  const opacity = 0.5 + progress * 0.5;

  return (
    <div style={{
      fontSize,
      fontWeight: "bold",
      transform: `scale(${scale})`,
      opacity,
    }}>
      {seconds}
    </div>
  );
};
```

### Notification Badge

```tsx
import { spring, useCurrentFrame, useVideoConfig } from "remotion";

interface BadgeProps {
  count: number;
  color?: string;
}

export const NotificationBadge: React.FC<BadgeProps> = ({
  count,
  color = "#EF4444",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({
    frame,
    fps,
    from: 0,
    to: 1,
    config: { damping: 8, stiffness: 200 },
  });

  return (
    <div style={{
      backgroundColor: color,
      color: "white",
      borderRadius: "50%",
      width: 32,
      height: 32,
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      fontWeight: "bold",
      fontSize: 16,
      transform: `scale(${scale})`,
    }}>
      {count}
    </div>
  );
};
```

---

## Particle Systems

### Confetti

```tsx
import { random, useCurrentFrame } from "remotion";

interface ConfettiProps {
  count?: number;
  colors?: string[];
}

export const Confetti: React.FC<ConfettiProps> = ({
  count = 50,
  colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FED766", "#2AB7CA"],
}) => {
  const frame = useCurrentFrame();

  const particles = Array.from({ length: count }, (_, i) => {
    const x = random(`x-${i}`) * 100;
    const startY = random(`startY-${i}`) * -20 - 10;
    const speed = 2 + random(`speed-${i}`) * 3;
    const rotation = random(`rotation-${i}`) * 360;
    const rotationSpeed = (random(`rotSpeed-${i}`) - 0.5) * 10;
    const color = colors[Math.floor(random(`color-${i}`) * colors.length)];
    const size = 8 + random(`size-${i}`) * 8;

    const y = startY + frame * speed;
    const currentRotation = rotation + frame * rotationSpeed;

    return (
      <div
        key={i}
        style={{
          position: "absolute",
          left: `${x}%`,
          top: `${y}%`,
          width: size,
          height: size * 0.6,
          backgroundColor: color,
          transform: `rotate(${currentRotation}deg)`,
          borderRadius: 2,
        }}
      />
    );
  });

  return <>{particles}</>;
};
```

### Particle Burst

```tsx
import { interpolate, random, useCurrentFrame } from "remotion";

interface ParticleBurstProps {
  particleCount?: number;
  burstFrame?: number;
  color?: string;
}

export const ParticleBurst: React.FC<ParticleBurstProps> = ({
  particleCount = 30,
  burstFrame = 0,
  color = "#FFD700",
}) => {
  const frame = useCurrentFrame();
  const elapsed = frame - burstFrame;

  if (elapsed < 0) return null;

  const particles = Array.from({ length: particleCount }, (_, i) => {
    const angle = (i / particleCount) * Math.PI * 2;
    const speed = 5 + random(`speed-${i}`) * 5;
    const distance = elapsed * speed;

    const x = Math.cos(angle) * distance;
    const y = Math.sin(angle) * distance;

    const opacity = interpolate(elapsed, [0, 30], [1, 0], {
      extrapolateRight: "clamp",
    });

    const scale = interpolate(elapsed, [0, 30], [1, 0.3], {
      extrapolateRight: "clamp",
    });

    return (
      <div
        key={i}
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          width: 10,
          height: 10,
          borderRadius: "50%",
          backgroundColor: color,
          transform: `translate(${x}px, ${y}px) scale(${scale})`,
          opacity,
        }}
      />
    );
  });

  return <>{particles}</>;
};
```

---

## Data Visualization Patterns

### Animated Number Counter

```tsx
import { interpolate, useCurrentFrame } from "remotion";

interface CounterProps {
  from?: number;
  to: number;
  durationInFrames?: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
}

export const AnimatedCounter: React.FC<CounterProps> = ({
  from = 0,
  to,
  durationInFrames = 60,
  prefix = "",
  suffix = "",
  decimals = 0,
}) => {
  const frame = useCurrentFrame();

  const value = interpolate(frame, [0, durationInFrames], [from, to], {
    extrapolateRight: "clamp",
  });

  return (
    <span>
      {prefix}
      {value.toFixed(decimals)}
      {suffix}
    </span>
  );
};

// Usage: <AnimatedCounter to={1000000} prefix="$" suffix="+" />
```

### Pie Chart Segment

```tsx
import { interpolate, useCurrentFrame } from "remotion";

interface PieSegmentProps {
  percentage: number;
  color: string;
  animationDelay?: number;
  size?: number;
}

export const PieSegment: React.FC<PieSegmentProps> = ({
  percentage,
  color,
  animationDelay = 0,
  size = 200,
}) => {
  const frame = useCurrentFrame();

  const animatedPercentage = interpolate(
    frame - animationDelay,
    [0, 30],
    [0, percentage],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const rotation = animatedPercentage * 3.6;  // 360 degrees = 100%

  return (
    <div style={{
      width: size,
      height: size,
      borderRadius: "50%",
      background: `conic-gradient(${color} 0deg ${rotation}deg, #333 ${rotation}deg 360deg)`,
    }} />
  );
};
```

---

## Audio Reactive Patterns

### Volume Visualizer (requires audio analysis)

```tsx
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";

interface VisualizerProps {
  barCount?: number;
  // In real use, pass audio analysis data
  getVolume?: (index: number, frame: number) => number;
}

export const VolumeVisualizer: React.FC<VisualizerProps> = ({
  barCount = 20,
  getVolume = (i, f) => Math.sin(f * 0.1 + i * 0.5) * 0.5 + 0.5,  // Fake data
}) => {
  const frame = useCurrentFrame();

  return (
    <div style={{ display: "flex", gap: 4, alignItems: "flex-end", height: 100 }}>
      {Array.from({ length: barCount }, (_, i) => {
        const volume = getVolume(i, frame);
        const height = 20 + volume * 80;

        return (
          <div
            key={i}
            style={{
              width: 8,
              height,
              backgroundColor: `hsl(${200 + volume * 60}, 70%, 50%)`,
              borderRadius: 4,
            }}
          />
        );
      })}
    </div>
  );
};
```

---

## Combining Patterns Example

```tsx
import { AbsoluteFill, Sequence, Video, staticFile } from "remotion";
import { FadeTransition } from "./transitions/FadeTransition";
import { CharStagger } from "./text/CharStagger";
import { Confetti } from "./particles/Confetti";
import { AnimatedCounter } from "./data/AnimatedCounter";

export const CelebrationVideo: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#1a1a2e" }}>
      {/* Background video */}
      <Video src={staticFile("background.mp4")} style={{ opacity: 0.3 }} />

      {/* Intro text */}
      <Sequence from={0} durationInFrames={90}>
        <FadeTransition durationInFrames={90}>
          <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
            <CharStagger text="Congratulations!" />
          </AbsoluteFill>
        </FadeTransition>
      </Sequence>

      {/* Stats reveal */}
      <Sequence from={90} durationInFrames={120}>
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
          <div style={{ fontSize: 72, color: "white" }}>
            <AnimatedCounter to={1000000} prefix="$" durationInFrames={60} />
          </div>
          <div style={{ fontSize: 24, color: "#888", marginTop: 10 }}>
            Revenue Milestone
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* Confetti celebration */}
      <Sequence from={120}>
        <Confetti count={100} />
      </Sequence>
    </AbsoluteFill>
  );
};
```
