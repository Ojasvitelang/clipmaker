# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for ClipMaker macOS application.
Bundles Python runtime, dependencies, FFmpeg, and web assets.
"""

import os
from pathlib import Path

# Get the project directory
project_dir = Path(SPECPATH)

# Define paths
ffmpeg_bin = '/opt/homebrew/bin/ffmpeg'  # Your dev machine FFmpeg location
templates_dir = project_dir / 'templates'

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=[str(project_dir)],
    binaries=[
        # Bundle FFmpeg binary
        (ffmpeg_bin, 'ffmpeg'),  # Copy ffmpeg to ffmpeg/ folder in bundle
    ],
    datas=[
        # Bundle the Flask templates directory
        (str(templates_dir), 'templates'),
        # Bundle the processing scripts (treated as data, not code)
        ('clip_maker.py', '.'),
        ('convert.py', '.'),
    ],
    hiddenimports=[
        # Flask and its dependencies
        'flask',
        'werkzeug',
        'jinja2',
        'click',
        'itsdangerous',

        # MoviePy and its dependencies
        'moviepy',
        'moviepy.video.io.VideoFileClip',
        'moviepy.video.fx',
        'moviepy.editor',

        # ImageIO (used by MoviePy)
        'imageio',
        'imageio.core',
        'imageio.plugins',
        'imageio_ffmpeg',

        # Pillow (used by MoviePy for GIF optimization)
        'PIL',
        'PIL.Image',

        # NumPy (MoviePy dependency)
        'numpy',
        'numpy.core',
        'numpy.core._multiarray_umath',

        # Proglog (MoviePy progress bar)
        'proglog',
        'tqdm',

        # Decorator (MoviePy dependency)
        'decorator',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary packages to reduce size
        'matplotlib',
        'tkinter',
        'test',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ClipMaker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ClipMaker',
)

app = BUNDLE(
    coll,
    name='ClipMaker.app',
    icon=None,  # TODO: Add icon file if you have one (e.g., 'icon.icns')
    bundle_identifier='com.clipmaker.app',
    info_plist={
        'CFBundleName': 'ClipMaker',
        'CFBundleDisplayName': 'ClipMaker',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '10.13.0',  # macOS High Sierra or later
        'NSRequiresAquaSystemAppearance': 'False',
    },
)
