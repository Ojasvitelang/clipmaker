#!/bin/bash
#
# ClipMaker Build Script
# Builds a standalone macOS .app bundle with PyInstaller
#

set -e  # Exit on error

echo "=========================================="
echo "ClipMaker - Build Standalone macOS App"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Verify FFmpeg is installed
echo -e "\n${YELLOW}[1/5]${NC} Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}ERROR:${NC} FFmpeg not found. Please install it:"
    echo "  brew install ffmpeg"
    exit 1
fi

FFMPEG_PATH=$(which ffmpeg)
echo -e "${GREEN}✓${NC} FFmpeg found at: $FFMPEG_PATH"

# Step 2: Install PyInstaller if not present
echo -e "\n${YELLOW}[2/5]${NC} Checking PyInstaller..."
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller
else
    echo -e "${GREEN}✓${NC} PyInstaller already installed"
fi

# Step 3: Install dependencies
echo -e "\n${YELLOW}[3/5]${NC} Installing Python dependencies..."
pip3 install -r requirements.txt

# Step 4: Clean previous builds
echo -e "\n${YELLOW}[4/5]${NC} Cleaning previous builds..."
rm -rf build dist __pycache__ *.pyc
echo -e "${GREEN}✓${NC} Cleaned build directories"

# Step 5: Build the app
echo -e "\n${YELLOW}[5/5]${NC} Building ClipMaker.app..."
echo "This may take 2-5 minutes..."
pyinstaller ClipMaker.spec --clean

# Verify build
if [ -d "dist/ClipMaker.app" ]; then
    echo ""
    echo "=========================================="
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo "=========================================="
    echo ""
    echo "Your standalone app is ready at:"
    echo "  dist/ClipMaker.app"
    echo ""
    echo "Next steps:"
    echo "  1. Test the app:"
    echo "     open dist/ClipMaker.app"
    echo ""
    echo "  2. To distribute to others:"
    echo "     cd dist"
    echo "     zip -r ClipMaker.zip ClipMaker.app"
    echo ""
    echo "  3. Recipients just:"
    echo "     - Unzip"
    echo "     - Right-click → Open (first time only, to bypass Gatekeeper)"
    echo "     - Double-click thereafter"
    echo ""
    echo "App size: $(du -sh dist/ClipMaker.app | cut -f1)"
    echo ""
else
    echo -e "${RED}ERROR:${NC} Build failed. Check output above for errors."
    exit 1
fi
