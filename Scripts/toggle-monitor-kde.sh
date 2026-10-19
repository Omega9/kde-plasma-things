#!/bin/bash

MON="DVI-D-1"
echo "MON=$MON"

if kscreenctl list-outputs | grep -A 1 "Output:.*$MON" | grep -q "enabled"; then
    echo "$MON is on, turning off"
    kscreenctl "$MON" set-enabled false
else
    echo "$MON is off, turning off"
    kscreenctl "$MON" set-enabled true
fi
