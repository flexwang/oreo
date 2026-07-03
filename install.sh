#!/bin/bash
# Install Oreo as a background Launch Agent (no .app needed, avoids Airlock)
set -e

PLIST_NAME="com.oreo.deskpet"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"
PYTHON_PATH=$(which python3)
SCRIPT_PATH="$HOME/oreo/main.py"

echo "Installing Oreo as a Launch Agent..."

cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON_PATH}</string>
        <string>${SCRIPT_PATH}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$HOME/oreo</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/oreo/oreo.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/oreo/oreo.log</string>
</dict>
</plist>
EOF

echo "Starting Oreo..."
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"

echo ""
echo "Done! Oreo is now running in the background."
echo "  - Starts automatically on login"
echo "  - No terminal needed"
echo "  - To stop:    launchctl unload ~/Library/LaunchAgents/com.oreo.deskpet.plist"
echo "  - To restart: launchctl unload ... && launchctl load ..."
echo "  - To uninstall: run ./uninstall.sh"
