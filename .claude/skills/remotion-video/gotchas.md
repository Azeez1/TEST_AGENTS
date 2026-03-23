# Gotchas — Remotion Video

> Built from real failures. If you hit one of these, the fix is here.

## 1. Missing Keyframes Crash (Sora 2 / Veo Clips)
**Symptom:** Remotion compositor crashes with "No frame found at position" when embedding AI-generated video clips.
**Root Cause:** Sora 2 and Veo outputs lack keyframes needed for frame-accurate seeking.
**Fix:** Re-encode all source clips before use:
```bash
ffmpeg -y -i input.mp4 -c:v libx264 -g 1 -pix_fmt yuv420p -c:a aac output.mp4
```
The `-g 1` flag inserts a keyframe at every frame.
**Discovered:** 2026-03-08

---

## 2. Parallel Seek Collision
**Symptom:** Glitchy, stuttery playback. Frames appear out of order. Random visual artifacts.
**Root Cause:** Default `--concurrency 6` causes multiple render threads to seek the same video file simultaneously.
**Fix:** Always render with single concurrency:
```bash
npx remotion render ... --codec h264 --concurrency 1
```
**Discovered:** 2026-03-08

---

## 3. Resolution Mismatch Blur
**Symptom:** Output video looks blurry or has upscaling artifacts.
**Root Cause:** Canvas resolution (e.g., 1080x1920) doesn't match source clip resolution (e.g., 720x1280). Remotion upscales, causing blur.
**Fix:** Match your Remotion composition dimensions to the source clip resolution. If Sora outputs 720x1280 portrait, set your canvas to 720x1280.
**Discovered:** 2026-03-08

---

## 4. Audio Stripping False Fix
**Symptom:** Someone suggests stripping audio to fix compositor errors.
**Root Cause:** This is a misdiagnosis. The real problem is missing keyframes (Gotcha #1) and parallel seeking (Gotcha #2).
**Fix:** Do NOT strip audio. Apply the `-g 1` keyframe fix and `--concurrency 1` instead. Audio must be preserved for final output.
**Discovered:** 2026-03-08

---

## 5. Cache Corruption
**Symptom:** Errors persist even after applying the correct fixes above.
**Root Cause:** Remotion caches processed frames. Stale cache from failed renders can persist.
**Fix:** Clear the Remotion cache:
```bash
rm -rf "$TEMP/remotion-v4*"
```
Then re-render.
**Discovered:** 2026-03-08

---

## 6. Use OffthreadVideo, Not Video
**Symptom:** Video component causes rendering hangs or memory issues with large/multiple clips.
**Root Cause:** The `<Video>` component loads the entire video into memory. With AI-generated clips (often large files), this overwhelms the renderer.
**Fix:** Always use `<OffthreadVideo>` instead of `<Video>`:
```tsx
import { OffthreadVideo } from 'remotion';
// NOT: import { Video } from 'remotion';
```
`<OffthreadVideo>` streams frames on demand instead of loading everything upfront.
**Discovered:** 2026-03-08
