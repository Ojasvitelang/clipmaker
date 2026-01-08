#!/usr/bin/env python3
"""
ClipMaker Launcher
Standalone app entry point that bundles FFmpeg and launches the web server.
"""

import os
import sys
import time
import webbrowser
import threading
from pathlib import Path


def setup_environment():
    """
    Configure environment for bundled FFmpeg.
    This is critical for PyInstaller apps which don't inherit shell PATH.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled app (PyInstaller)
        bundle_dir = Path(sys._MEIPASS)

        # Add bundled ffmpeg to PATH
        ffmpeg_dir = bundle_dir / "ffmpeg"
        if ffmpeg_dir.exists():
            os.environ["PATH"] = str(ffmpeg_dir) + os.pathsep + os.environ.get("PATH", "")

            # Set explicit path for MoviePy/imageio
            ffmpeg_bin = ffmpeg_dir / "ffmpeg"
            if ffmpeg_bin.exists():
                os.environ["IMAGEIO_FFMPEG_EXE"] = str(ffmpeg_bin)
                print(f"[Launcher] FFmpeg configured at: {ffmpeg_bin}")
            else:
                print(f"[Launcher] WARNING: FFmpeg binary not found at {ffmpeg_bin}")
        else:
            print(f"[Launcher] WARNING: FFmpeg directory not found at {ffmpeg_dir}")
    else:
        # Running in development mode
        print("[Launcher] Running in development mode (not bundled)")


def open_browser(url, delay=1.5):
    """
    Open the default web browser after a short delay.
    """
    def _open():
        time.sleep(delay)
        print(f"[Launcher] Opening browser: {url}")
        webbrowser.open(url)

    thread = threading.Thread(target=_open, daemon=True)
    thread.start()


def main():
    """
    Main launcher function.
    """
    print("=" * 60)
    print("ClipMaker - Video to Clips & GIFs")
    print("=" * 60)

    # Step 1: Setup environment (FFmpeg paths)
    setup_environment()

    # Step 2: Import and configure Flask app
    # Import here AFTER environment is set up
    from app import app

    # Step 3: Schedule browser to open
    server_url = "http://127.0.0.1:5000"
    open_browser(server_url)

    # Step 4: Start Flask server (blocking call)
    print(f"[Launcher] Starting web server on {server_url}")
    print("[Launcher] Press Ctrl+C to quit")
    print("=" * 60)

    try:
        # Run Flask in production mode for standalone app
        # Use threaded=True for concurrent request handling
        app.run(
            host="127.0.0.1",
            port=5000,
            debug=False,  # No debug mode in production
            threaded=True,
            use_reloader=False  # No auto-reload in standalone app
        )
    except KeyboardInterrupt:
        print("\n[Launcher] Shutting down...")
    except Exception as e:
        print(f"\n[Launcher] Error: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
