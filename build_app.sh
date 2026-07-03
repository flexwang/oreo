#!/bin/bash
# Build Oreo.app — standalone macOS application
set -e

cd "$(dirname "$0")"

echo "Building Oreo.app..."
pyinstaller \
    --windowed \
    --name Oreo \
    --icon icon.png \
    --add-data "assets:assets" \
    --add-data "frames/walking3:frames/walking3" \
    --add-data "frames/walking-to-stretching:frames/walking-to-stretching" \
    --add-data "frames/stretching:frames/stretching" \
    --noconfirm \
    --clean \
    main.py

echo ""
echo "Done! Oreo.app is at: dist/Oreo.app"
echo "You can drag it to /Applications or double-click to run."
