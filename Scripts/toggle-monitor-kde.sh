#!/bin/bash

MON="DVI-D-1" # or HDMI-A-1

if kscreen-doctor -o | awk "/Output: .* $MON/{f=1} f && /enabled/{print; exit}" | grep -q enabled; then
    kscreen-doctor output.$MON.disable
else
    kscreen-doctor output.$MON.enable
fi
