#!/bin/bash
# Script to uninstall the Mac OS version of the Ragam App

echo "=== Ragam App MacOS Uninstaller ==="

# Define the installation paths
# By default, Mac users will drag the .app to /Applications/RagamApp.app
APP_DIR="/Applications/RagamApp.app"

if [ -d "$APP_DIR" ]; then
    echo "Found RagamApp in Applications folder. Removing..."
    rm -rf "$APP_DIR"
    echo "RagamApp removed from Applications."
else
    echo "RagamApp not found in Applications folder."
fi

# Clean up build artifacts if run from source directory
if [ -d "./dist" ]; then
    echo "Removing dist/ build artifacts..."
    rm -rf "./dist"
fi

if [ -d "./build" ]; then
    echo "Removing build/ artifacts..."
    rm -rf "./build"
fi

echo "=== Uninstall Complete ==="
