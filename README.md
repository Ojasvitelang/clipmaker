# ClipMaker Web UI

A simple, lightweight web interface for converting videos into clips and optimized GIFs.

## Overview

This web UI wraps two existing Python scripts (`clip_maker.py` and `convert.py`) **WITHOUT modifying their internal logic**. Both scripts are treated as black boxes and executed exactly as they were originally designed.

### What It Does

1. **Upload** a video file through your browser
2. **Generate** multiple outputs:
   - Short 6-second MP4 clips (via `clip_maker.py`)
   - Optimized GIFs under 20MB (via `convert.py`)
3. **Download** all results as a single ZIP file

### Performance Features

- Handles 200-300 clips without loading them into memory
- Background processing with progress tracking
- Session-based isolation (multiple users can upload simultaneously)
- Automatic cleanup after download
- Lightweight UI with no heavy frameworks

---

## Prerequisites

Before running this application, ensure you have:

1. **Python 3.8+** installed
2. **FFmpeg** installed and available in your PATH
   - macOS: `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt install ffmpeg`
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/)

---

## Installation

### 1. Clone or navigate to the project directory

```bash
cd /Users/ojasvitelang/Desktop/clipmaker
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **Flask** - Web framework
- **Werkzeug** - File handling utilities
- **MoviePy** - Required by `convert.py`

---

## Running the Application

### Start the server

```bash
python app.py
```

You should see:

```
============================================================
ClipMaker Web UI
============================================================
Server starting on http://localhost:5000
============================================================
```

### Access the web interface

Open your browser and navigate to:

```
http://localhost:5000
```

---

## How to Use

1. **Upload a video**:
   - Click the upload area or drag & drop a video file
   - Supported formats: MP4, MOV, AVI, MKV, WEBM (max 500MB)

2. **Click "Upload & Process"**:
   - The video will be uploaded to the server
   - Processing will start automatically

3. **Wait for processing**:
   - Progress bar shows current status
   - Step 1: Creating clips (6-second segments)
   - Step 2: Creating GIFs (optimized, under 20MB each)

4. **Download results**:
   - Once complete, click "Download All (ZIP)"
   - ZIP file contains all generated clips and GIFs

---

## File Flow Diagram

```
User Upload
    ↓
┌─────────────────────────────────────────────────┐
│ Flask Backend (app.py)                          │
├─────────────────────────────────────────────────┤
│ 1. Create session directory:                    │
│    sessions/{session_id}/                       │
│    ├── input/      ← video saved here          │
│    ├── output/     ← results saved here        │
│    ├── temp/       ← temporary files           │
│    ├── clip_maker.py  (copied)                 │
│    └── convert.py     (copied)                 │
│                                                  │
│ 2. Run clip_maker.py (as subprocess)            │
│    → Reads from input/                          │
│    → Writes clips to output/                    │
│    → BLACK BOX: No logic changes                │
│                                                  │
│ 3. Run convert.py (as subprocess)               │
│    → Reads from input/                          │
│    → Writes GIFs to output/                     │
│    → BLACK BOX: No logic changes                │
│                                                  │
│ 4. Create ZIP from output/                      │
│    → Streams file to browser                    │
│    → Cleanup after download                     │
└─────────────────────────────────────────────────┘
    ↓
User Downloads ZIP
```

---

## Architecture Details

### Session Isolation

Each upload creates a unique session with its own directory structure:

```
sessions/
├── abc123-uuid/
│   ├── input/
│   │   └── user_video.mp4
│   ├── output/
│   │   ├── user_video_part001.mp4
│   │   ├── user_video_part002.mp4
│   │   ├── ...
│   │   └── user_video.gif
│   ├── temp/
│   │   └── (temporary files)
│   ├── clip_maker.py
│   └── convert.py
└── xyz789-uuid/
    └── (another user's session)
```

### Script Execution

Both scripts are executed **exactly as they were written**:

```python
# NO MODIFICATIONS - Scripts run as black boxes
subprocess.run(['python', 'clip_maker.py'], cwd=session_dir)
subprocess.run(['python', 'convert.py'], cwd=session_dir)
```

**Critical Point**: The web UI does NOT:
- Modify any parameters in the scripts
- Change durations, FPS, quality settings, or encoding
- Rewrite or optimize the processing logic
- Interfere with FFmpeg commands

The scripts receive video files and produce outputs **exactly as originally designed**.

### Memory Efficiency

The application handles large numbers of outputs efficiently:

- **No in-memory preview generation**: Videos are not loaded into RAM for display
- **Streaming ZIP creation**: Files are added to ZIP on-the-fly
- **Background processing**: Uses threads to avoid blocking the UI
- **Automatic cleanup**: Session files deleted 5 seconds after download starts

---

## API Endpoints

### `GET /`
Serves the HTML interface

### `POST /upload`
Accepts video upload and starts processing

**Request**: `multipart/form-data` with `video` file

**Response**:
```json
{
  "session_id": "abc123-uuid",
  "message": "Processing started"
}
```

### `GET /status/<session_id>`
Polls processing status

**Response**:
```json
{
  "status": "processing",
  "step": "Creating clips...",
  "progress": 50
}
```

**On completion**:
```json
{
  "status": "completed",
  "step": "Done!",
  "progress": 100,
  "clips_count": 250,
  "gifs_count": 1
}
```

### `GET /download/<session_id>`
Creates and serves ZIP file of all outputs

**Response**: `application/zip` file

---

## Configuration

All video processing settings remain in the original scripts:

### clip_maker.py settings
- Clip duration: **6 seconds** (`MAX_CLIP_DURATION`)
- Video codec: **libx264**
- Quality: **CRF 18** (near-lossless)
- Audio codec: **AAC 128k**

### convert.py settings
- Max GIF width: **480px**
- Frame rate: **10 FPS**
- Max file size: **20 MB**
- Duration attempts: **7s, 6s, 5s, 4s, 3s, 2s, 1s**

**To modify these settings**: Edit the original scripts directly. The web UI will use whatever values are in the scripts.

---

## Troubleshooting

### "FFmpeg not found"
- Install FFmpeg: `brew install ffmpeg` (macOS) or `sudo apt install ffmpeg` (Linux)
- Verify installation: `ffmpeg -version`

### "ModuleNotFoundError: moviepy"
- Install dependencies: `pip install -r requirements.txt`

### "Processing failed"
- Check server logs in terminal
- Ensure uploaded video is not corrupted
- Verify FFmpeg is working: `ffmpeg -version`

### Large video uploads timing out
- Increase Flask timeout in `app.py` if needed
- Current limit: 500MB

### Port 5000 already in use
- Change port in `app.py`: `app.run(port=5001)`

---

## Project Structure

```
clipmaker/
├── app.py                  # Flask backend (NEW)
├── templates/
│   └── index.html          # Web UI (NEW)
├── requirements.txt        # Python dependencies (NEW)
├── README.md              # This file (NEW)
├── clip_maker.py          # Original script (UNTOUCHED)
├── convert.py             # Original script (UNTOUCHED)
└── sessions/              # Runtime directory (auto-created)
    └── {session-ids}/     # Isolated processing directories
```

---

## Original Scripts Confirmation

✅ **clip_maker.py** - UNTOUCHED
- No logic modifications
- No parameter changes
- Executed as-is via subprocess

✅ **convert.py** - UNTOUCHED
- No logic modifications
- No parameter changes
- Executed as-is via subprocess

The web UI acts only as a wrapper layer that:
- Handles file uploads
- Creates isolated working directories
- Invokes scripts as black boxes
- Packages results for download

---

## Security Notes

- File uploads limited to 500MB
- Only allowed extensions: mp4, mov, avi, mkv, webm
- Session directories automatically cleaned after download
- Filenames sanitized using `werkzeug.utils.secure_filename`

---

## License

This web UI wrapper is provided as-is. The original video processing scripts (`clip_maker.py` and `convert.py`) retain their original functionality and ownership.

---

## Support

For issues or questions:
1. Check terminal logs for error messages
2. Verify FFmpeg and Python dependencies are installed
3. Ensure video files are valid and not corrupted
