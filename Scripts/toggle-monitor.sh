#!/bin/bash
 
set -euo pipefail

# Paths to scripts
HYPR_SCRIPT="./toggle-monitor-hypr.sh"
KDE_SCRIPT="./toggle-monitor-kde.sh"

detect_and_run() {
    # --- Detecting Hyprland ---
    if [[ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]] || \
       pgrep -x Hyprland >/dev/null 2>&1; then
        echo "Detected Hyprland environment"
        exec "$HYPR_SCRIPT"
        return 0
    fi

    # --- Detecting KDE (KScreen) ---
    if command -v kscreen-doctor >/dev/null 2>&1 && \
       qdbus org.kde.KScreen /org/kde/KScreen org.kde.KScreen.version >/dev/null 2>&1; then
        echo "Detected KDE environment"
        exec "$KDE_SCRIPT"
        return 0
    fi

    # No supported desktop environment
    echo "Error: No supported desktop environment detected" >&2
    echo "Supported: Hyprland, KDE (with KScreen)" >&2
    exit 1
}

# Detect and run 🤷‍♂️
detect_and_run
