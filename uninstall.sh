#!/bin/bash
# Uninstall Oreo Launch Agent
set -e

PLIST_PATH="$HOME/Library/LaunchAgents/com.oreo.deskpet.plist"

echo "Stopping Oreo..."
launchctl unload "$PLIST_PATH" 2>/dev/null || true
rm -f "$PLIST_PATH"
echo "Done. Oreo has been uninstalled."
