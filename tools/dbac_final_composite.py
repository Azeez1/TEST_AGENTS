"""DBAC final composite — EP02 pattern.
Base: Original recording (slides) — cut-synced, MUTED, 1920x1080
PIP:  HeyGen avatar video — bottom-right, scaled
Audio: HeyGen audio (cleaned narration)
"""
import json, subprocess
from pathlib import Path

ORIGINAL = r"C:\Users\sabaa\Downloads\The_DBAC_Diagnostic_Framework_(3).mp4"
HEYGEN = r"C:\Users\sabaa\Downloads\YOUTUBE VID1 _1080p.mp4"
KEEPS_JSON = r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\videos\DBAC_Episode\src\dbac-keeps.json"
EP_DIR = Path(r"C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\videos\DBAC_Episode")

SLIDES_CLEAN = EP_DIR / "output" / "dbac_slides_cleaned.mp4"
FINAL_OUT = EP_DIR / "output" / "dbac_final.mp4"

# PIP sizing (HeyGen is 1080x1920 vertical 9:16)
# Scale down to fit corner of 1920x1080 horizontal canvas
PIP_W = 270
PIP_H = 480
MARGIN = 24

def build_concat_list(keeps, src):
    list_path = EP_DIR / "output" / ".dbac_concat.txt"
    src_norm = src.replace("\\", "/")
    with open(list_path, "w", encoding="utf-8") as f:
        for s, e in keeps:
            f.write(f"file '{src_norm}'\n")
            f.write(f"inpoint {s:.3f}\n")
            f.write(f"outpoint {e:.3f}\n")
    return list_path

def main():
    EP_DIR.joinpath("output").mkdir(parents=True, exist_ok=True)
    data = json.loads(Path(KEEPS_JSON).read_text())
    keeps = data["keeps"]
    print(f"Keeps: {len(keeps)} segments")

    # STAGE 1: cut-synced slides at full 1920x1080, MUTED
    print("\nStage 1: Cleaning original recording (slides) at 1920x1080, muted...")
    list_path = build_concat_list(keeps, ORIGINAL)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "warning",
        "-f", "concat", "-safe", "0", "-i", str(list_path),
        "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-pix_fmt", "yuv420p", "-r", "30",
        str(SLIDES_CLEAN)
    ], check=True)
    list_path.unlink()
    slides_size = SLIDES_CLEAN.stat().st_size / 1024 / 1024
    print(f"  -> {SLIDES_CLEAN.name} ({slides_size:.0f} MB)")

    # STAGE 2: composite slides (base) + HeyGen (PIP overlay) + HeyGen audio
    print("\nStage 2: Compositing final output...")
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "warning",
        "-i", str(SLIDES_CLEAN),
        "-i", HEYGEN,
        "-filter_complex",
        f"[1:v]scale={PIP_W}:{PIP_H}[pip];"
        f"[0:v][pip]overlay=W-w-{MARGIN}:H-h-{MARGIN}[v]",
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        str(FINAL_OUT)
    ], check=True)

    actual = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(FINAL_OUT)
    ]).strip())
    final_size = FINAL_OUT.stat().st_size / 1024 / 1024
    print(f"\nFinal: {FINAL_OUT}")
    print(f"Duration: {actual:.1f}s ({actual/60:.2f} min)")
    print(f"Size: {final_size:.0f} MB")

if __name__ == "__main__":
    main()
