# Design Reference - Agent Status Card Components

Visual design specifications and implementation details for consistent styling across the dashboard.

---

## Color Palette

### Status Colors

**Active (Green):**
```
Primary: #10B981 (green-500)
Light: #D1FAE5 (green-100)
Dark: #047857 (green-700)
Ring: rgba(16, 185, 129, 0.2)
```

**Idle (Blue):**
```
Primary: #3B82F6 (blue-500)
Light: #DBEAFE (blue-100)
Dark: #1D4ED8 (blue-700)
Ring: rgba(59, 130, 246, 0.2)
```

**Error (Red):**
```
Primary: #EF4444 (red-500)
Light: #FEE2E2 (red-100)
Dark: #B91C1C (red-700)
Ring: rgba(239, 68, 68, 0.2)
```

**Offline (Gray):**
```
Primary: #9CA3AF (gray-400)
Light: #F3F4F6 (gray-100)
Dark: #374151 (gray-700)
Ring: rgba(156, 163, 175, 0.2)
```

---

### Neutral Colors

**Background:**
```
Page: #F9FAFB (gray-50)
Card: #FFFFFF (white)
Border: #E5E7EB (gray-200)
Hover Border: #D1D5DB (gray-300)
```

**Text:**
```
Primary: #111827 (gray-900)
Secondary: #4B5563 (gray-600)
Tertiary: #9CA3AF (gray-400)
```

**Focus:**
```
Ring: #3B82F6 (blue-500)
Ring Offset: 2px
Ring Width: 2px
```

---

## Typography

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
  'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
  sans-serif;
```

### Font Sizes

**Agent Name (Heading):**
```
Size: 18px (1.125rem) - text-lg
Weight: 600 (Semibold) - font-semibold
Line Height: 28px (1.75rem)
Color: #111827 (gray-900)
```

**Status Label:**
```
Size: 14px (0.875rem) - text-sm
Weight: 500 (Medium) - font-medium
Line Height: 20px (1.25rem)
Color: Varies by status (green-700, blue-700, etc.)
```

**Last Run Time:**
```
Size: 14px (0.875rem) - text-sm
Weight: 400 (Normal) - font-normal
Line Height: 20px (1.25rem)
Color: #4B5563 (gray-600)
```

**Description:**
```
Size: 14px (0.875rem) - text-sm
Weight: 400 (Normal) - font-normal
Line Height: 20px (1.25rem)
Color: #4B5563 (gray-600)
Max Lines: 2 (line-clamp-2)
```

---

## Spacing & Layout

### Card Dimensions

**Padding:**
```
Card: 16px (1rem) - p-4
Top Accent Bar: 4px (0.25rem) - h-1
```

**Margins:**
```
Agent Name Bottom: 12px (0.75rem) - mb-3
Last Run Top: 0px
Description Top (if shown): 12px (0.75rem) - mt-3
```

**Gap:**
```
Name & Status: 12px (0.75rem) - gap-3
Icon & Text: 8px (0.5rem) - gap-2
```

---

### Grid Layout

**Responsive Breakpoints:**
```css
/* Mobile (< 640px) */
grid-template-columns: repeat(1, minmax(0, 1fr));

/* Tablet (640px+) */
@media (min-width: 640px) {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

/* Laptop (1024px+) */
@media (min-width: 1024px) {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

/* Desktop (1280px+) */
@media (min-width: 1280px) {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
```

**Grid Gap:**
```
Gap: 16px (1rem) - gap-4
```

---

## Border & Shadows

### Card Border

**Default:**
```
Width: 1px
Color: #E5E7EB (gray-200)
Radius: 8px (0.5rem) - rounded-lg
```

**Hover:**
```
Width: 1px
Color: #D1D5DB (gray-300)
Shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1)
```

---

### Shadow Elevations

**Default (sm):**
```css
box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
```

**Hover (md):**
```css
box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
```

---

### Focus Ring

**Keyboard Focus:**
```
Ring Width: 2px
Ring Color: #3B82F6 (blue-500)
Ring Offset: 2px
Ring Opacity: 100%
Border Radius: 8px (rounded-lg)
```

---

## Icons & Indicators

### Status Dot

**Size:**
```
Width: 12px (0.75rem) - w-3
Height: 12px (0.75rem) - h-3
Border Radius: 50% (rounded-full)
```

**Pulse Ring (Active Status Only):**
```
Width: 12px (same as dot)
Height: 12px (same as dot)
Border Radius: 50%
Opacity: 75%
Animation: pulse (2s cubic-bezier(0.4, 0, 0.6, 1) infinite)
```

---

### Clock Icon

**Size:**
```
Width: 16px (1rem) - w-4
Height: 16px (1rem) - h-4
```

**Stroke:**
```
Width: 2px (strokeWidth={2})
Color: currentColor (inherits from parent)
Cap: round (strokeLinecap="round")
Join: round (strokeLinejoin="round")
```

---

## Animations & Transitions

### Pulse Animation (Active Status)

**Keyframes:**
```css
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
```

**Timing:**
```
Duration: 2s
Timing Function: cubic-bezier(0.4, 0, 0.6, 1)
Iteration: infinite
```

---

### Hover Transition

**Properties:**
```css
transition-property: all;
transition-duration: 200ms;
transition-timing-function: ease-in-out;
```

**Affected:**
- Shadow (sm → md)
- Border color (gray-200 → gray-300)

---

## Interactive States

### Default State

```css
background: white;
border: 1px solid #E5E7EB;
box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
cursor: default;
```

---

### Hover State (Interactive Cards)

```css
background: white;
border: 1px solid #D1D5DB;
box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
cursor: pointer;
transition: all 200ms ease-in-out;
```

---

### Focus State (Keyboard)

```css
outline: none;
box-shadow: 0 0 0 2px white, 0 0 0 4px #3B82F6;
border-radius: 8px;
```

---

### Active State (Click)

```css
transform: scale(0.98);
transition: transform 100ms ease-in-out;
```

---

## Responsive Behavior

### Mobile (< 640px)

**Layout:**
- Single column grid
- Full-width cards
- Padding: 16px (1rem)
- Font sizes unchanged (already mobile-optimized)

**Touch Targets:**
- Minimum 44x44px (exceeds 44px with padding)
- Adequate spacing between cards (16px gap)

---

### Tablet (640px - 1024px)

**Layout:**
- 2-column grid
- Cards max-width based on grid
- Padding: 24px (1.5rem) container

**Typography:**
- Same as mobile (no scaling)

---

### Desktop (1024px+)

**Layout:**
- 3-4 column grid (3 at 1024px, 4 at 1280px)
- Container max-width: 1280px (centered)
- Padding: 48px (3rem) container

**Typography:**
- Same (no desktop-specific scaling)

---

## Accessibility Features

### Color Contrast Ratios

**All text meets WCAG AA:**
```
Agent Name (gray-900): 16.1:1 ✅ AAA
Status Label (green-700): 6.2:1 ✅ AAA
Last Run (gray-600): 7.5:1 ✅ AAA
Description (gray-600): 7.5:1 ✅ AAA
```

---

### Status Indicators

**Multiple Signals (Not Color-Only):**
1. **Color:** Green/Blue/Red/Gray dot
2. **Text:** "Active", "Idle", "Error", "Offline"
3. **Position:** Consistent top-right placement
4. **Animation:** Pulse for active (additional visual cue)

---

### Focus Indicators

**Always Visible:**
- 2px blue ring
- 2px white offset (separation from card)
- High contrast (4.5:1+)
- Rounded corners match card

---

## Component Anatomy

```
┌─────────────────────────────────────────┐
│ ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ │ ← Status Accent Bar (4px)
├─────────────────────────────────────────┤
│                                         │
│  Agent Name ──────────┐    ● Active    │ ← Header Row
│                       └─── Status      │
│                                         │
│  🕒 Last run: 2 minutes ago             │ ← Time Row
│                                         │
│  Description text here if showDetails  │ ← Optional Description
│  is enabled (max 2 lines)              │
│                                         │
└─────────────────────────────────────────┘
```

**Measurements:**
```
Total Height: ~130px (without description)
Total Height: ~170px (with description)
Min Width: 280px (mobile)
Max Width: Determined by grid container
```

---

## CSS Class Reference

### Card Container
```html
<article class="
  relative overflow-hidden
  rounded-lg border border-gray-200 bg-white
  shadow-sm hover:shadow-md
  transition-all duration-200 ease-in-out
  cursor-pointer hover:border-gray-300
">
```

---

### Status Accent Bar
```html
<div class="h-1 bg-green-500" />
```

---

### Header Container
```html
<div class="flex items-start justify-between gap-3 mb-3">
```

---

### Agent Name
```html
<h3 class="text-lg font-semibold text-gray-900 truncate flex-1">
  Copywriter
</h3>
```

---

### Status Indicator
```html
<div class="flex items-center gap-2 flex-shrink-0">
  <span class="relative flex h-3 w-3">
    {/* Pulse ring (active only) */}
    <span class="absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75 animate-pulse" />

    {/* Status dot */}
    <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500" />
  </span>

  {/* Status label */}
  <span class="text-sm font-medium text-green-700">
    Active
  </span>
</div>
```

---

### Last Run Time
```html
<div class="flex items-center gap-2 text-sm text-gray-600">
  <svg class="w-4 h-4">
    {/* Clock icon */}
  </svg>
  <time datetime="2025-10-22T10:00:00.000Z">
    Last run: 2 minutes ago
  </time>
</div>
```

---

### Description (Optional)
```html
<p class="mt-3 text-sm text-gray-600 line-clamp-2">
  Blog posts, articles, web copy (2000+ words)
</p>
```

---

## Grid Container Classes

```html
<div class="
  grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4
  gap-4
">
  {/* Agent cards */}
</div>
```

---

## Dark Mode Support (Future)

**Recommended color adjustments:**

```css
@media (prefers-color-scheme: dark) {
  /* Backgrounds */
  .bg-gray-50 { background-color: #1F2937; }  /* Page */
  .bg-white { background-color: #111827; }    /* Card */

  /* Borders */
  .border-gray-200 { border-color: #374151; }

  /* Text */
  .text-gray-900 { color: #F9FAFB; }
  .text-gray-600 { color: #D1D5DB; }

  /* Shadows */
  .shadow-sm {
    box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.5);
  }
}
```

---

## Figma Design Tokens

**For design handoff:**

```json
{
  "colors": {
    "status": {
      "active": "#10B981",
      "idle": "#3B82F6",
      "error": "#EF4444",
      "offline": "#9CA3AF"
    },
    "text": {
      "primary": "#111827",
      "secondary": "#4B5563",
      "tertiary": "#9CA3AF"
    },
    "background": {
      "page": "#F9FAFB",
      "card": "#FFFFFF"
    },
    "border": {
      "default": "#E5E7EB",
      "hover": "#D1D5DB"
    }
  },
  "spacing": {
    "card-padding": "16px",
    "grid-gap": "16px",
    "element-gap": "12px"
  },
  "typography": {
    "agent-name": {
      "size": "18px",
      "weight": 600,
      "lineHeight": "28px"
    },
    "status-label": {
      "size": "14px",
      "weight": 500,
      "lineHeight": "20px"
    }
  },
  "effects": {
    "shadow-sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    "shadow-md": "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
  }
}
```

---

## Print Styles (Future)

**Recommended for printable dashboards:**

```css
@media print {
  /* Remove shadows and borders for cleaner print */
  .shadow-sm, .shadow-md {
    box-shadow: none;
  }

  /* Use borders for structure */
  article {
    border: 1px solid #000;
  }

  /* Remove animations */
  .animate-pulse {
    animation: none;
  }

  /* Hide interactive states */
  .hover\:shadow-md {
    box-shadow: none;
  }
}
```

---

## Implementation Notes

### Tailwind Configuration

**Required in `tailwind.config.js`:**
```javascript
module.exports = {
  theme: {
    extend: {
      // All default Tailwind utilities are used
      // No custom extensions needed
    },
  },
}
```

---

### Browser-Specific Considerations

**Safari (iOS):**
- `-webkit-overflow-scrolling: touch` for smooth scroll
- Test focus indicators (may need `-webkit-focus-ring-color`)

**Firefox:**
- Ensure `outline: none` works properly on focus
- Test animation performance (may need `will-change`)

**Chrome:**
- No specific considerations (reference browser)

---

## Performance Budgets

**Target Metrics:**
- First Contentful Paint: < 1.5s
- Largest Contentful Paint: < 2.5s
- Cumulative Layout Shift: < 0.1
- Total Blocking Time: < 300ms

**Component Contribution:**
- Render time: < 50ms (100 agents)
- Re-render time: < 10ms (with memoization)
- Paint time: < 16ms (60fps)

---

## Resources

**Design Tools:**
- Figma: Component library available
- Sketch: Export Tailwind classes
- Adobe XD: Design tokens JSON

**Color Tools:**
- [Tailwind Color Generator](https://tailwindshades.com/)
- [Contrast Checker](https://webaim.org/resources/contrastchecker/)

**Accessibility:**
- [WCAG Color Contrast](https://webaim.org/resources/contrastchecker/)
- [Focus Indicators](https://www.sarasoueidan.com/blog/focus-indicators/)

---

**Last Updated:** 2025-10-22
**Maintained by:** frontend-developer (ENGINEERING_TEAM)
