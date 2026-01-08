import os
import subprocess

INPUT_DIR = "input"
OUTPUT_DIR = "output"
MAX_CLIP_DURATION = 6  # seconds

def split_with_ffmpeg(input_path, output_dir, max_duration):
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    out_pattern = os.path.join(output_dir, f"{base_name}_part%03d.mp4")

    # ffmpeg: fix SAR + segment
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vf", "setsar=1",     # force square pixels
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "18",          # near-lossless visually
        "-c:a", "aac",
        "-b:a", "128k",
        "-f", "segment",
        "-segment_time", str(max_duration),
        "-break_non_keyframes", "1",  # split at exact time, not keyframes
        "-reset_timestamps", "1",
        "-y",  # overwrite
        out_pattern
    ]

    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"Done splitting: {input_path}")

def process_all_videos():
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
    if not files:
        print(f"No videos found in '{INPUT_DIR}'")
        return

    for file in files:
        input_path = os.path.join(INPUT_DIR, file)
        split_with_ffmpeg(input_path, OUTPUT_DIR, MAX_CLIP_DURATION)

if __name__ == "__main__":
    process_all_videos()
