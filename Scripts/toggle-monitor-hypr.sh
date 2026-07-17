#!/usr/bin/env bash
set -euo pipefail

MON="DVI-D-1" # or HDMI-A-1

DISABLED=$(
    hyprctl monitors all -j |
    jq -r ".[] | select(.name == \"$MON\") | .disabled"
)

if [[ "$DISABLED" == "true" ]]; then
    hyprctl eval "
        hl.monitor({
            output = \"$MON\",
            disabled = false
        })
    "
else
    hyprctl eval "
        hl.monitor({
            output = \"$MON\",
            disabled = true
        })
    "
fi