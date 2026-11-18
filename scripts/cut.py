"""Build and run the ffmpeg command: trim -> 9:16 crop -> burn captions."""
import shutil, subprocess

def build_cmd(video, start, end, ass, out, w=1080, h=1920):
    vf = f"crop=ih*9/16:ih,scale={w}:{h},ass={ass}"
    return ["ffmpeg", "-y", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", video,
            "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out]

def run(cmd, dry=False):
    if dry:
        return " ".join(cmd)
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg not found. Install it (apt/brew install ffmpeg) or use --dry-run.")
    subprocess.run(cmd, check=True)
