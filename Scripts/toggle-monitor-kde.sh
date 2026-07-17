#!/bin/bash

MON="DVI-D-1" # or HDMI-A-1

if kscreen-doctor --json | jq -e ".outputs[] | select(.name==\"$MON\") | .enabled" >/dev/null; then
    kscreen-doctor output.$MON.disable
else
    kscreen-doctor output.$MON.enable
fi
