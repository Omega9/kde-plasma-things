#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

HYPR_SCRIPT="$SCRIPT_DIR/toggle-monitor-hypr.sh"
KDE_SCRIPT="$SCRIPT_DIR/toggle-monitor-kde.sh"

# Hyprland
if [[ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]]; then
    exec "$HYPR_SCRIPT"
fi

# KDE Plasma
if [[ "${XDG_CURRENT_DESKTOP:-}" == *KDE* ]]; then
    exec "$KDE_SCRIPT"
fi

echo "Unsupported environment" >&2
exit 1
