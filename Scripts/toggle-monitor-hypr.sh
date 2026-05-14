#!/usr/bin/env bash
set -euo pipefail

MON="DVI-D-1" # or HDMI-A-1

if hyprctl monitors all | grep -A30 "^Monitor $MON" | grep -q "disabled: false"; then
    hyprctl keyword monitor "$MON,disable"
else
    # back to default settings (preferred mode, automatic positioning, scale 1)
    hyprctl keyword monitor "$MON,preferred,auto,1"
fi
