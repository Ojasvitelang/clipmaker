# ClipMaker - User Guide

## What is ClipMaker?

ClipMaker is a desktop application that automatically splits your videos into 6-second clips and creates optimized GIFs. Perfect for creating social media content, highlights, or breaking down long videos.

---

## For End Users (Non-Technical)

### First Time Setup

1. **Download** the ClipMaker.zip file
2. **Unzip** the file (double-click it)
3. **First Launch** - Important!
   - **Right-click** on `ClipMaker.app`
   - Select **"Open"** from the menu
   - Click **"Open"** in the security dialog that appears
   - This is only needed the first time (macOS Gatekeeper security)

4. **Browser Opens Automatically**
   - The app will open your web browser automatically
   - You'll see the ClipMaker upload page

### How to Use

1. **Double-click** ClipMaker.app (after first-time setup)
2. **Wait** for your browser to open (takes 2-3 seconds)
3. **Upload** your video file
   - Supported formats: MP4, MOV, AVI, MKV, WEBM
   - Maximum size: 500MB
4. **Wait** for processing
   - Progress bar shows current status
   - Time depends on video length (usually 1-3 minutes)
5. **Download** the ZIP file containing:
   - All your 6-second MP4 clips
   - Optimized GIF versions

### Tips

- **Keep the app running** while processing
- **Don't close the browser tab** during upload/processing
- **Large videos** (100+ clips) may take several minutes
- **Close the app** by pressing Ctrl+C in the terminal window or just quit the app

### Troubleshooting

**Problem: "App can't be opened" error**
- **Solution**: Right-click → Open (don't double-click the first time)

**Problem: Browser doesn't open**
- **Solution**: Manually open http://127.0.0.1:5000 in your browser

**Problem: Upload fails**
- **Solution**: Check file size (must be under 500MB) and format (MP4, MOV, AVI, MKV, WEBM only)

**Problem: Processing stuck**
- **Solution**: Refresh the browser page. If still stuck, quit and restart the app

---

## For Developers

### Building from Source

#### Prerequisites
- macOS 10.13 or later
- Python 3.8+
- FFmpeg (install with: `brew install ffmpeg`)
- pip3

#### Build Steps

1. **Clone/Download** the project
2. **Run** the build script:
   ```bash
   ./build_app.sh
   ```
3. **Wait** 2-5 minutes for build to complete
4. **Test** the app:
   ```bash
   open dist/ClipMaker.app
   ```

#### Build Output
- **Location**: `dist/ClipMaker.app`
- **Size**: ~150-250MB (includes Python runtime + FFmpeg)
- **Contents**:
  - Python 3 runtime
  - Flask web server
  - MoviePy library
  - FFmpeg binary
  - All processing scripts

### Distribution

#### Creating a Distributable Package

```bash
cd dist
zip -r ClipMaker-v1.0.zip ClipMaker.app
```

#### What Gets Bundled
- ✅ Python runtime (no installation needed)
- ✅ All pip packages (Flask, MoviePy, etc.)
- ✅ FFmpeg binary
- ✅ Processing scripts (clip_maker.py, convert.py)
- ✅ Web templates
- ❌ Source code (compiled to bytecode)

### Architecture

```
ClipMaker.app/
├── Contents/
│   ├── MacOS/
│   │   └── ClipMaker          # Main executable
│   ├── Resources/
│   │   └── ... (bundled files)
│   └── Frameworks/
│       └── ... (Python runtime)
```

**Execution Flow:**
1. `launcher.py` starts
2. Sets up FFmpeg environment variables
3. Imports Flask app from `app.py`
4. Starts Flask server on port 5000
5. Opens browser to http://127.0.0.1:5000
6. User uploads video
7. `app.py` calls `clip_maker.py` (subprocess)
8. `app.py` calls `convert.py` (subprocess)
9. ZIP file created and downloaded

### Windows Build (Future)

To build for Windows, you'll need:

1. **Windows machine** with Python 3.8+
2. **FFmpeg** for Windows ([download](https://ffmpeg.org/download.html))
3. **PyInstaller** (same version as macOS build)

**Build command:**
```bash
pyinstaller ClipMaker.spec --clean
```

**Output:** `dist/ClipMaker/ClipMaker.exe`

**Note:** The spec file may need minor adjustments for Windows:
- Change `ffmpeg_bin` path to Windows FFmpeg location
- Change `console=False` to `console=True` for debugging
- Test with Windows paths (backslashes)

### Customization

#### Change Port
Edit `launcher.py` line 63:
```python
app.run(host="127.0.0.1", port=5000, ...)
```

#### Change Clip Duration
**DO NOT EDIT clip_maker.py directly** - it's designed as a black box.
Instead, contact the developer for changes.

#### Add App Icon
1. Create/obtain an `.icns` file (macOS icon format)
2. Add to project root as `icon.icns`
3. Edit `ClipMaker.spec` line 111:
   ```python
   icon='icon.icns',
   ```
4. Rebuild

### Known Limitations

- **macOS only** (Windows build requires separate testing)
- **No code signing** (users see Gatekeeper warning first time)
- **Large file size** (~200MB) due to bundled dependencies
- **Offline only** (no network features)
- **Single user** (localhost only, no multi-user support)

### Security Notes

- **No external network access** - fully offline app
- **No data collection** - everything stays local
- **Session data** stored in `~/Library/Application Support/ClipMaker/sessions/` (automatically cleaned after download)
- **Temporary files** cleaned up automatically

---

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Verify FFmpeg is bundled: look for `ClipMaker.app/Contents/Resources/ffmpeg/ffmpeg`
3. Check logs: Run from terminal to see detailed output

---

## Version History

### v1.0.0 (Initial Release)
- macOS standalone app
- 6-second clip generation
- GIF optimization
- ZIP download
- Bundled FFmpeg
- No dependencies required
