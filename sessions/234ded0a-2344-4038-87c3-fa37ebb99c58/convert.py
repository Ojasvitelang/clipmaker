import os
import subprocess
from moviepy.editor import VideoFileClip

# === Settings ===
INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"
TEMP_FOLDER = "temp"

VIDEO_EXTS = (".mp4", ".mov", ".avi", ".mkv", ".webm")
MAX_WIDTH = 480
FPS = 10
MAX_SIZE_MB = 20
DURATION_TRIES = [7, 6, 5, 4, 3, 2, 1]

# === Ensure folders exist ===
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

def make_gif_with_ffmpeg(temp_mp4_path, output_gif_path):
    palette_path = os.path.join(TEMP_FOLDER, "palette.png")

    # Step 1: Generate palette
    subprocess.run([
        "ffmpeg", "-y", "-i", temp_mp4_path,
        "-vf", f"fps={FPS},scale={MAX_WIDTH}:-1:flags=lanczos,palettegen=max_colors=128",
        palette_path
    ], check=True)

    # Step 2: Create gif using palette
    subprocess.run([
        "ffmpeg", "-y", "-i", temp_mp4_path, "-i", palette_path,
        "-filter_complex", f"fps={FPS},scale={MAX_WIDTH}:-1:flags=lanczos[x];[x][1:v]paletteuse",
        output_gif_path
    ], check=True)

def convert_clip_to_gif(clip, filename):
    for duration in DURATION_TRIES:
        if clip.duration < duration:
            continue

        print(f"⏳ Trying duration: {duration}s for {filename}")
        trimmed = clip.subclip(0, duration)
        temp_mp4 = os.path.join(TEMP_FOLDER, f"{filename}_temp.mp4")
        output_gif = os.path.join(OUTPUT_FOLDER, f"{filename}.gif")

        try:
            # export temporary mp4 quickly
            trimmed.write_videofile(
                temp_mp4,
                fps=FPS,
                codec="libx264",
                audio=False,
                preset="ultrafast",
                threads=8,
                verbose=False,
                logger=None
            )

            make_gif_with_ffmpeg(temp_mp4, output_gif)

            # check size
            size_mb = os.path.getsize(output_gif) / (1024 * 1024)
            if size_mb <= MAX_SIZE_MB:
                print(f"✅ Saved: {filename}.gif ({size_mb:.2f} MB)")
                return True
            else:
                os.remove(output_gif)
                print(f"❌ Too big ({size_mb:.2f} MB), trying shorter duration...")

        except Exception as e:
            print(f"⚠️ Error processing {filename} at {duration}s: {e}")
            return False

    print(f"❌ Could not compress {filename} under {MAX_SIZE_MB} MB")
    return False

# === Batch Convert ===
if __name__ == "__main__":
    files = os.listdir(INPUT_FOLDER)
    print(f"Found files: {files}")

    any_found = False

    for file in files:
        if not file.lower().endswith(VIDEO_EXTS):
            continue

        any_found = True
        input_path = os.path.join(INPUT_FOLDER, file)
        name, _ = os.path.splitext(file)

        print(f"\n🎬 Processing: {file}")
        try:
            clip = VideoFileClip(input_path)
            convert_clip_to_gif(clip, name)
            clip.close()
        except Exception as e:
            print(f"❌ Failed to process {file}: {e}")

    if not any_found:
        print("⚠️ No supported video files found in the input folder.")
