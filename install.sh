#!/bin/bash
# install-ectool.sh
# This script installs the Framework ectool binary to /usr/bin/ectool/ectool with correct permissions.

set -e

# Prevent running as root
if [ "$(id -u)" -eq 0 ]; then
    echo "Error: Do not run this script as root. Run as your normal user." >&2
    exit 1
fi

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



# Create ectool group if it doesn't exist
if ! getent group ectool > /dev/null; then
    echo "Creating group 'ectool'..."
    sudo groupadd ectool
else
    echo "Group 'ectool' already exists."
fi

# Add current user to ectool group
CURRENT_USER="$(id -un)"
echo "Adding $CURRENT_USER to group 'ectool'..."
sudo usermod -aG ectool "$CURRENT_USER"

# PolicyKit rule file
RULE_FILE="/etc/polkit-1/rules.d/50-framework-ectool.rules"

# Create the PolicyKit rule

sudo bash -c "cat > $RULE_FILE" <<EOF
polkit.addRule(function(action, subject) {
    if (
        action.id == "org.freedesktop.policykit.exec" &&
        action.lookup("program") == "/usr/bin/ectool" &&
        subject.isInGroup("ectool")
    ) {
        return polkit.Result.YES;
    }
});
EOF

echo "PolicyKit rule installed at $RULE_FILE for /usr/bin/ectool."
echo "All users in the 'ectool' group can now run ectool via pkexec without a password prompt."
echo "You may need to log out and back in for the group change to take effect."
