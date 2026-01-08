# ClipMaker - Build Instructions

## Quick Start (macOS)

```bash
# 1. Install dependencies (first time only)
brew install ffmpeg
pip3 install pyinstaller

# 2. Build the standalone app
./build_app.sh

# 3. Test it
open dist/ClipMaker.app

# 4. Distribute it
cd dist
zip -r ClipMaker.zip ClipMaker.app
```

That's it! Share `ClipMaker.zip` with anyone - no installation needed.

---

## Detailed Instructions

### Prerequisites

#### 1. Install FFmpeg (if not already installed)

```bash
brew install ffmpeg
```

Verify:
```bash
ffmpeg -version
```

#### 2. Install Python Dependencies

```bash
pip3 install -r requirements.txt
pip3 install pyinstaller
```

### Building

#### Option 1: Automated Build (Recommended)

```bash
./build_app.sh
```

This script:
- ✅ Checks FFmpeg installation
- ✅ Installs PyInstaller if needed
- ✅ Cleans previous builds
- ✅ Builds ClipMaker.app
- ✅ Provides next steps

#### Option 2: Manual Build

```bash
# Clean previous builds
rm -rf build dist

# Build the app
pyinstaller ClipMaker.spec --clean

# Output will be at: dist/ClipMaker.app
```

### Testing the Build

#### Test Locally

```bash
# Open the app
open dist/ClipMaker.app

# Your browser should open automatically to http://127.0.0.1:5000
# Test upload and processing workflow
```

#### Test Distribution Package

```bash
# Create ZIP
cd dist
zip -r ClipMaker-v1.0.zip ClipMaker.app

# Move to Downloads and test as end user would
mv ClipMaker-v1.0.zip ~/Downloads/
cd ~/Downloads
unzip ClipMaker-v1.0.zip
open ClipMaker.app  # Should work without issues
```

---

## Distribution

### Creating Release Package

1. **Build the app** (see above)
2. **Test thoroughly** on your machine
3. **Create ZIP**:
   ```bash
   cd dist
   zip -r ClipMaker-v1.0.0.zip ClipMaker.app
   ```
4. **Upload** to file sharing service (Google Drive, Dropbox, etc.)
5. **Share** the download link with users

### User Instructions (Include with Distribution)

**For First-Time Users:**

1. Download and unzip `ClipMaker.zip`
2. **Right-click** on ClipMaker.app → **Open** (do NOT double-click first time)
3. Click **"Open"** in the security warning
4. Browser opens automatically
5. Upload video and process

**For Subsequent Use:**
- Just double-click ClipMaker.app

---

## Troubleshooting Build Issues

### Issue: "FFmpeg not found"

**Solution:**
```bash
# Install FFmpeg
brew install ffmpeg

# Update spec file if installed in custom location
which ffmpeg  # Copy this path
# Edit ClipMaker.spec line 14 with the correct path
```

### Issue: "ModuleNotFoundError" during runtime

**Solution:** Add missing module to `hiddenimports` in `ClipMaker.spec`:

```python
hiddenimports=[
    # ... existing imports ...
    'your.missing.module',
],
```

Then rebuild:
```bash
pyinstaller ClipMaker.spec --clean
```

### Issue: Large app size (>300MB)

**Normal:** The app bundles Python + FFmpeg + MoviePy, typically 150-250MB.

**To reduce:**
1. Exclude unused packages in `ClipMaker.spec`:
   ```python
   excludes=[
       'matplotlib',
       'tkinter',
       'test',
       'unittest',
       'scipy',  # Add more if not needed
   ],
   ```

2. Rebuild:
   ```bash
   pyinstaller ClipMaker.spec --clean
   ```

### Issue: "Gatekeeper" blocks app for users

**This is expected** for unsigned apps. Users must:
1. Right-click → Open (first time only)
2. Click "Open" in warning dialog

**To avoid (advanced):**
- Obtain Apple Developer Account ($99/year)
- Code sign the app:
  ```bash
  codesign --deep --force --sign "Developer ID Application: Your Name" dist/ClipMaker.app
  ```

### Issue: App crashes on startup

**Debug:**
```bash
# Run from terminal to see errors
cd dist/ClipMaker.app/Contents/MacOS
./ClipMaker
```

Look for:
- Missing FFmpeg
- Module import errors
- Path issues

**Fix:** Update `ClipMaker.spec` with missing dependencies.

---

## Architecture

### File Structure

```
clipmaker/
├── launcher.py              # Entry point (sets up environment)
├── app.py                   # Flask server (DO NOT MODIFY)
├── clip_maker.py            # Video splitting (DO NOT MODIFY)
├── convert.py               # GIF generation (DO NOT MODIFY)
├── ClipMaker.spec           # PyInstaller configuration
├── build_app.sh             # Automated build script
├── requirements.txt         # Python dependencies
├── templates/               # Flask HTML templates
│   └── index.html
├── USER_GUIDE.md            # End user documentation
└── BUILD_INSTRUCTIONS.md    # This file
```

### Build Output Structure

```
dist/ClipMaker.app/
├── Contents/
│   ├── MacOS/
│   │   └── ClipMaker                    # Main executable
│   ├── Resources/
│   │   ├── ffmpeg/
│   │   │   └── ffmpeg                   # Bundled FFmpeg binary
│   │   ├── templates/
│   │   │   └── index.html               # Web UI
│   │   ├── clip_maker.py                # Processing script
│   │   ├── convert.py                   # GIF generation script
│   │   └── ... (other bundled files)
│   ├── Frameworks/
│   │   └── ... (Python runtime)
│   └── Info.plist                       # macOS app metadata
```

### Runtime Behavior

1. User double-clicks `ClipMaker.app`
2. macOS launches `Contents/MacOS/ClipMaker`
3. `launcher.py` starts:
   - Detects it's running as bundled app (`sys.frozen = True`)
   - Sets `PATH` to include bundled FFmpeg
   - Sets `IMAGEIO_FFMPEG_EXE` for MoviePy
4. Imports and starts Flask from `app.py`
5. Opens browser to `http://127.0.0.1:5000`
6. User uploads video
7. Flask calls `clip_maker.py` via subprocess
8. Flask calls `convert.py` via subprocess
9. ZIP created and downloaded
10. Session cleaned up automatically

---

## Windows Build (Future)

### Requirements (Windows)
- Windows 10 or later
- Python 3.8+ for Windows
- FFmpeg for Windows ([download](https://www.gyan.dev/ffmpeg/builds/))
- PyInstaller for Windows

### Build Steps (Windows)

1. **Install Prerequisites:**
   ```cmd
   # Install Python from python.org
   # Download FFmpeg and extract to C:\ffmpeg
   pip install pyinstaller
   pip install -r requirements.txt
   ```

2. **Update ClipMaker.spec for Windows:**
   ```python
   # Line 14: Update FFmpeg path
   ffmpeg_bin = 'C:/ffmpeg/bin/ffmpeg.exe'

   # Line 85: Enable console for debugging
   console=True,  # Change to False when done testing
   ```

3. **Build:**
   ```cmd
   pyinstaller ClipMaker.spec --clean
   ```

4. **Output:**
   - Folder: `dist\ClipMaker\`
   - Executable: `dist\ClipMaker\ClipMaker.exe`
   - Distribute entire `ClipMaker` folder

5. **Test:**
   ```cmd
   dist\ClipMaker\ClipMaker.exe
   ```

### Windows Distribution

```cmd
# Create ZIP of entire folder
cd dist
powershell Compress-Archive -Path ClipMaker -DestinationPath ClipMaker-Windows.zip
```

**User Instructions (Windows):**
1. Unzip `ClipMaker-Windows.zip`
2. Double-click `ClipMaker.exe` inside the folder
3. Browser opens automatically

---

## Advanced Configuration

### Changing App Name

1. Edit `ClipMaker.spec`:
   ```python
   name='YourAppName',  # Line 75 and 95
   bundle_identifier='com.yourcompany.yourapp',  # Line 109
   ```

2. Rename spec file:
   ```bash
   mv ClipMaker.spec YourAppName.spec
   ```

3. Update `build_app.sh` line 47:
   ```bash
   pyinstaller YourAppName.spec --clean
   ```

### Adding App Icon

1. **Create icon:**
   - Design 1024x1024 PNG
   - Convert to .icns (macOS):
     ```bash
     # Use online converter or:
     mkdir MyIcon.iconset
     sips -z 512 512   icon.png --out MyIcon.iconset/icon_512x512.png
     # ... (add other sizes)
     iconutil -c icns MyIcon.iconset
     ```

2. **Add to project:**
   ```bash
   cp MyIcon.icns icon.icns
   ```

3. **Update spec:**
   ```python
   icon='icon.icns',  # Line 111
   ```

4. **Rebuild**

### Code Signing (macOS)

**Requires:** Apple Developer Account ($99/year)

```bash
# 1. Install certificate from Apple Developer
# 2. Find your identity
security find-identity -v -p codesigning

# 3. Sign the app
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/ClipMaker.app

# 4. Verify
spctl -a -t exec -vv dist/ClipMaker.app

# 5. Notarize (optional, for Gatekeeper approval)
# Follow Apple's notarization guide
```

---

## Maintenance

### Updating Dependencies

```bash
# Update requirements.txt
pip3 install --upgrade flask moviepy werkzeug

# Test locally
python3 launcher.py

# Rebuild if all works
./build_app.sh
```

### Version Updates

1. Update version in `ClipMaker.spec`:
   ```python
   'CFBundleVersion': '1.1.0',
   'CFBundleShortVersionString': '1.1.0',
   ```

2. Update `USER_GUIDE.md` version history

3. Rebuild and create new ZIP:
   ```bash
   ./build_app.sh
   cd dist
   zip -r ClipMaker-v1.1.0.zip ClipMaker.app
   ```

---

## Support

For build issues:
1. Check this guide
2. Run build script with verbose output
3. Check PyInstaller logs in `build/` folder
4. Test FFmpeg binary: `dist/ClipMaker.app/Contents/Resources/ffmpeg/ffmpeg -version`

---

## License

Include your license information here.
