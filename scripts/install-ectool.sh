#!/bin/bash
# install-ectool.sh
# This script installs the Framework ectool binary to /usr/bin/ectool/ectool with correct permissions.

set -e

# Source and destination
SRC_PATH="$(realpath ./app/tools/ectool)"
DEST_DIR="/usr/bin"
DEST_PATH="$DEST_DIR/ectool"

# Create destination directory if it doesn't exist
if [ ! -d "$DEST_DIR" ]; then
    echo "Creating $DEST_DIR..."
    sudo mkdir -p "$DEST_DIR"
fi

# Copy ectool
echo "Copying $SRC_PATH to $DEST_PATH..."
sudo cp "$SRC_PATH" "$DEST_PATH"

# Ensure it is executable
sudo chmod 755 "$DEST_PATH"

echo "ectool installed to $DEST_PATH."
