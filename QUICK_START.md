# ClipMaker - Quick Start

## For Developers: Build the App

```bash
# One command to rule them all:
./build_app.sh
```

That's it! Output: `dist/ClipMaker.app`

---

## For End Users: Use the App

```bash
# First time only:
# Right-click ClipMaker.app → Open

# Then:
# Double-click ClipMaker.app
```

Browser opens automatically → Upload video → Download ZIP

---

## Files You Need to Know

| File | Purpose |
|------|---------|
| `launcher.py` | App entry point (sets up FFmpeg) |
| `ClipMaker.spec` | PyInstaller build config |
| `build_app.sh` | Automated build script |
| `app.py` | Flask server (don't modify) |
| `clip_maker.py` | Video splitter (don't modify) |
| `convert.py` | GIF generator (don't modify) |

---

## Distribute the App

```bash
cd dist
zip -r ClipMaker.zip ClipMaker.app
# Share ClipMaker.zip with users
```

---

## Troubleshooting

**Build fails?**
- Check: `brew install ffmpeg`
- Check: `pip3 install pyinstaller`

**App crashes?**
- Run from terminal: `open dist/ClipMaker.app`
- Check console output for errors

**Gatekeeper warning?**
- Tell users: Right-click → Open (first time only)

---

## What Gets Bundled

✅ Python runtime
✅ Flask + MoviePy
✅ FFmpeg binary
✅ Processing scripts
❌ No source code
❌ No external dependencies needed

**Size:** ~150-250MB

---

## Support

- Build issues → `BUILD_INSTRUCTIONS.md`
- User issues → `USER_GUIDE.md`
- Architecture → See `BUILD_INSTRUCTIONS.md`
