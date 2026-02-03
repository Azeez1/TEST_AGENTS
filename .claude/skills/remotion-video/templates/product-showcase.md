# Product Showcase Template

A professional template for showcasing products with animated features, specifications, and call-to-action. Ideal for e-commerce, product launches, and demo videos.

## Preview

```
[Frames 0-60]    Product entrance with scale/rotation animation
[Frames 60-120]  Feature highlights appear one by one
[Frames 120-180] Specs/price reveal
[Frames 180-240] CTA with button animation
```

## Full Component

```tsx
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

interface ProductFeature {
  icon: string;  // Emoji or icon character
  title: string;
  description?: string;
}

interface ProductShowcaseProps {
  /**
   * Path to product image in public/ folder
   */
  productImage: string;

  /**
   * Product name/title
   */
  productName: string;

  /**
   * Short tagline or description
   */
  tagline?: string;

  /**
   * Product price (formatted string)
   * @example "$99.99"
   */
  price?: string;

  /**
   * Original price for showing discount
   * @example "$149.99"
   */
  originalPrice?: string;

  /**
   * List of features to highlight
   */
  features?: ProductFeature[];

  /**
   * Call-to-action text
   * @default "Shop Now"
   */
  ctaText?: string;

  /**
   * Primary brand color
   * @default "#4F46E5"
   */
  primaryColor?: string;

  /**
   * Background color or gradient
   * @default "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)"
   */
  background?: string;

  /**
   * Layout style
   * @default "centered"
   */
  layout?: "centered" | "left" | "right" | "split";
}

export const ProductShowcase: React.FC<ProductShowcaseProps> = ({
  productImage,
  productName,
  tagline,
  price,
  originalPrice,
  features = [],
  ctaText = "Shop Now",
  primaryColor = "#4F46E5",
  background = "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
  layout = "centered",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Product entrance animation
  const productScale = spring({
    frame,
    fps,
    from: 0.8,
    to: 1,
    config: { damping: 12, stiffness: 100 },
  });

  const productRotation = spring({
    frame,
    fps,
    from: -5,
    to: 0,
    config: { damping: 15, stiffness: 80 },
  });

  const productOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Floating animation (subtle continuous motion)
  const floatY = Math.sin(frame * 0.05) * 5;

  // Title animation
  const titleOpacity = interpolate(frame, [30, 50], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const titleY = interpolate(frame, [30, 50], [20, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Price animation
  const priceScale = spring({
    frame: frame - 80,
    fps,
    from: 0,
    to: 1,
    config: { damping: 10, stiffness: 200 },
  });

  // CTA button animation
  const ctaScale = spring({
    frame: frame - 140,
    fps,
    from: 0,
    to: 1,
    config: { damping: 8, stiffness: 150 },
  });

  const ctaPulse = 1 + Math.sin(frame * 0.1) * 0.03;

  return (
    <AbsoluteFill
      style={{
        background,
        justifyContent: "center",
        alignItems: "center",
        padding: 60,
      }}
    >
      {/* Background glow effect */}
      <div
        style={{
          position: "absolute",
          width: 400,
          height: 400,
          background: `radial-gradient(circle, ${primaryColor}40 0%, transparent 70%)`,
          filter: "blur(60px)",
        }}
      />

      {/* Product Image */}
      <Img
        src={staticFile(productImage)}
        style={{
          width: 350,
          height: 350,
          objectFit: "contain",
          transform: `
            scale(${productScale})
            rotate(${productRotation}deg)
            translateY(${floatY}px)
          `,
          opacity: productOpacity,
          filter: "drop-shadow(0 20px 40px rgba(0,0,0,0.4))",
        }}
      />

      {/* Product Name */}
      <h1
        style={{
          color: "#FFFFFF",
          fontSize: 56,
          fontWeight: 800,
          fontFamily: "system-ui, -apple-system, sans-serif",
          marginTop: 30,
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
          textAlign: "center",
          letterSpacing: "-0.02em",
        }}
      >
        {productName}
      </h1>

      {/* Tagline */}
      {tagline && (
        <p
          style={{
            color: "rgba(255,255,255,0.7)",
            fontSize: 24,
            marginTop: 10,
            opacity: titleOpacity,
            transform: `translateY(${titleY}px)`,
            textAlign: "center",
          }}
        >
          {tagline}
        </p>
      )}

      {/* Features */}
      <Sequence from={60}>
        <FeatureList
          features={features}
          primaryColor={primaryColor}
        />
      </Sequence>

      {/* Price */}
      {price && (
        <div
          style={{
            marginTop: 30,
            display: "flex",
            alignItems: "center",
            gap: 16,
            transform: `scale(${priceScale})`,
          }}
        >
          {originalPrice && (
            <span
              style={{
                color: "rgba(255,255,255,0.5)",
                fontSize: 28,
                textDecoration: "line-through",
              }}
            >
              {originalPrice}
            </span>
          )}
          <span
            style={{
              color: primaryColor,
              fontSize: 48,
              fontWeight: 800,
            }}
          >
            {price}
          </span>
        </div>
      )}

      {/* CTA Button */}
      <div
        style={{
          marginTop: 40,
          transform: `scale(${ctaScale * ctaPulse})`,
        }}
      >
        <div
          style={{
            backgroundColor: primaryColor,
            color: "#FFFFFF",
            padding: "18px 48px",
            borderRadius: 50,
            fontSize: 24,
            fontWeight: 700,
            cursor: "pointer",
            boxShadow: `0 10px 30px ${primaryColor}60`,
          }}
        >
          {ctaText}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Feature List Sub-component
interface FeatureListProps {
  features: ProductFeature[];
  primaryColor: string;
}

const FeatureList: React.FC<FeatureListProps> = ({
  features,
  primaryColor,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (features.length === 0) return null;

  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        gap: 20,
        marginTop: 30,
        maxWidth: 800,
      }}
    >
      {features.map((feature, index) => {
        const delay = index * 10;
        const scale = spring({
          frame: frame - delay,
          fps,
          from: 0,
          to: 1,
          config: { damping: 12, stiffness: 200 },
        });

        return (
          <div
            key={index}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              backgroundColor: "rgba(255,255,255,0.1)",
              padding: "12px 20px",
              borderRadius: 30,
              transform: `scale(${scale})`,
            }}
          >
            <span style={{ fontSize: 24 }}>{feature.icon}</span>
            <span
              style={{
                color: "#FFFFFF",
                fontSize: 18,
                fontWeight: 600,
              }}
            >
              {feature.title}
            </span>
          </div>
        );
      })}
    </div>
  );
};
```

## Usage in Composition

```tsx
import { Composition } from "remotion";
import { ProductShowcase } from "./ProductShowcase";

const sampleFeatures = [
  { icon: "⚡", title: "Fast Charging" },
  { icon: "🔋", title: "48hr Battery" },
  { icon: "💧", title: "Waterproof" },
  { icon: "🎵", title: "Hi-Fi Audio" },
];

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Landscape (YouTube, Facebook) */}
      <Composition
        id="ProductShowcase"
        component={ProductShowcase}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          productImage: "headphones.png",
          productName: "ProSound X1",
          tagline: "Premium Wireless Headphones",
          price: "$299",
          originalPrice: "$399",
          features: sampleFeatures,
          ctaText: "Shop Now",
          primaryColor: "#6366F1",
        }}
      />

      {/* Vertical (TikTok, Instagram) */}
      <Composition
        id="ProductShowcaseVertical"
        component={ProductShowcase}
        durationInFrames={240}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          productImage: "headphones.png",
          productName: "ProSound X1",
          tagline: "Premium Wireless Headphones",
          price: "$299",
          features: sampleFeatures,
          primaryColor: "#6366F1",
        }}
      />
    </>
  );
};
```

## Variations

### Tech Product (Dark Theme)

```tsx
<ProductShowcase
  productImage="smartphone.png"
  productName="Galaxy Pro Max"
  tagline="The Future in Your Hands"
  price="$1,199"
  originalPrice="$1,399"
  features={[
    { icon: "📱", title: "6.8\" Display" },
    { icon: "📷", title: "200MP Camera" },
    { icon: "⚡", title: "5G Ready" },
  ]}
  primaryColor="#00D9FF"
  background="linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 100%)"
/>
```

### Beauty/Cosmetics (Light Theme)

```tsx
<ProductShowcase
  productImage="skincare.png"
  productName="Glow Serum"
  tagline="Your Daily Radiance Ritual"
  price="$65"
  features={[
    { icon: "✨", title: "Vitamin C" },
    { icon: "🌿", title: "Natural" },
    { icon: "💎", title: "Hyaluronic" },
  ]}
  primaryColor="#E91E63"
  background="linear-gradient(135deg, #FFF5F5 0%, #FFE4E4 100%)"
/>
```

### Food/Beverage

```tsx
<ProductShowcase
  productImage="energy-drink.png"
  productName="Nano Banana"
  tagline="Natural Energy, No Crash"
  price="$3.99"
  features={[
    { icon: "🍌", title: "Real Banana" },
    { icon: "⚡", title: "Clean Energy" },
    { icon: "🌱", title: "Plant-Based" },
  ]}
  ctaText="Try Now"
  primaryColor="#FFD93D"
  background="linear-gradient(135deg, #1a1a2e 0%, #2d3436 100%)"
/>
```

### SaaS/Software

```tsx
<ProductShowcase
  productImage="app-icon.png"
  productName="TaskFlow Pro"
  tagline="Your Work, Simplified"
  price="$12/mo"
  originalPrice="$24/mo"
  features={[
    { icon: "🚀", title: "10x Faster" },
    { icon: "🔒", title: "Secure" },
    { icon: "👥", title: "Team Sync" },
  ]}
  ctaText="Start Free Trial"
  primaryColor="#7C3AED"
  background="linear-gradient(135deg, #0F172A 0%, #1E293B 100%)"
/>
```

## Props Reference

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `productImage` | string | required | Path to product image |
| `productName` | string | required | Product name/title |
| `tagline` | string | undefined | Short description |
| `price` | string | undefined | Current price |
| `originalPrice` | string | undefined | Original price (for discount) |
| `features` | ProductFeature[] | [] | Feature highlights |
| `ctaText` | string | "Shop Now" | CTA button text |
| `primaryColor` | string | "#4F46E5" | Brand/accent color |
| `background` | string | gradient | Background CSS |
| `layout` | string | "centered" | Layout style |

## Integration with AI Video

### As Outro After AI Clip

```tsx
import { AbsoluteFill, Sequence, Video, staticFile } from "remotion";
import { ProductShowcase } from "./ProductShowcase";

export const ProductVideo: React.FC = () => {
  return (
    <AbsoluteFill>
      {/* AI-generated product demo (8 seconds) */}
      <Sequence from={0} durationInFrames={240}>
        <Video src={staticFile("veo-product-demo.mp4")} />
      </Sequence>

      {/* Product showcase outro (8 seconds) */}
      <Sequence from={240}>
        <ProductShowcase
          productImage="product.png"
          productName="Amazing Product"
          price="$99"
          features={[
            { icon: "✨", title: "Feature 1" },
            { icon: "🚀", title: "Feature 2" },
          ]}
          ctaText="Buy Now"
        />
      </Sequence>
    </AbsoluteFill>
  );
};
```

### With Caption Overlay

```tsx
import { CaptionOverlay } from "./CaptionOverlay";

// Add captions on top of product showcase
<AbsoluteFill>
  <ProductShowcase {...props} />
  <CaptionOverlay
    words={captionWords}
    style="minimal"
    bottomOffset={5}
  />
</AbsoluteFill>
```

## Extending the Template

### Add Animated Badge

```tsx
// Add a "NEW" or "SALE" badge
const BadgeComponent: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const rotation = Math.sin(frame * 0.1) * 5;

  return (
    <div
      style={{
        position: "absolute",
        top: 100,
        right: 100,
        backgroundColor: "#EF4444",
        color: "white",
        padding: "10px 20px",
        borderRadius: 8,
        fontWeight: 800,
        fontSize: 20,
        transform: `rotate(${rotation}deg)`,
      }}
    >
      {text}
    </div>
  );
};
```

### Add Product Rotation

```tsx
// 360-degree product rotation
const productRotationY = interpolate(
  frame,
  [0, durationInFrames],
  [0, 360],
  { extrapolateRight: "clamp" }
);

<div style={{ transform: `rotateY(${productRotationY}deg)` }}>
  <Img src={staticFile(productImage)} />
</div>
```

## Render Command

```bash
# Render product showcase
npx remotion render src/index.tsx ProductShowcase product-ad.mp4

# With custom props
npx remotion render src/index.tsx ProductShowcase product-ad.mp4 \
  --props '{"productImage":"my-product.png","productName":"My Product","price":"$49.99"}'

# Vertical format
npx remotion render src/index.tsx ProductShowcaseVertical product-ad-vertical.mp4
```
