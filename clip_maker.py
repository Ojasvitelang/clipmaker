import os
import subprocess

INPUT_DIR = "input"
OUTPUT_DIR = "output"
MAX_CLIP_DURATION = 6  # seconds

def split_with_ffmpeg(input_path, output_dir, max_duration):
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    temp_pattern = os.path.join(output_dir, f"{base_name}_temp%03d.mp4")

    # Step 1: Generate clips with forced keyframes at regular intervals
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vf", "setsar=1",     # force square pixels
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "18",          # near-lossless visually
        "-g", "72",            # force keyframe every 72 frames (6s at 12fps, 3s at 24fps)
        "-force_key_frames", f"expr:gte(t,n_forced*{max_duration})",  # keyframe every N seconds
        "-c:a", "aac",
        "-b:a", "128k",
        "-f", "segment",
        "-segment_time", str(max_duration),
        "-break_non_keyframes", "1",  # split at exact time, not keyframes
        "-reset_timestamps", "1",
        "-y",  # overwrite
        temp_pattern
    ]

    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    # Step 2: Post-process each clip to move moov atom to beginning for QuickTime compatibility
    print("Post-processing clips for QuickTime/Finder compatibility...")
    import glob
    temp_files = sorted(glob.glob(os.path.join(output_dir, f"{base_name}_temp*.mp4")))

    for i, temp_file in enumerate(temp_files):
        final_file = os.path.join(output_dir, f"{base_name}_part{i:03d}.mp4")

        # Use ffmpeg to copy and add faststart flag
        faststart_cmd = [
            "ffmpeg",
            "-i", temp_file,
            "-c", "copy",          # no re-encoding, just remux
            "-movflags", "+faststart",  # move moov atom to beginning
            "-y",
            final_file
        ]

        subprocess.run(faststart_cmd, check=True, capture_output=True)
        os.remove(temp_file)  # remove temp file

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
