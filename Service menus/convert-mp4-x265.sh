#!/bin/bash

for file in "$@"; do
    base="${file%.*}"
    out="${base}.x265.mp4"

    notify-send -u low -i media-playback-start \
        "Конвертация" "Файл: $(basename "$file")"

    ffmpeg -i "$file" \
        -c:v libx265 -crf 28 \
        -c:a copy \
        -map_metadata 0 \
        -movflags +faststart \
        "$out"

    touch -r "$file" "$out"

    notify-send -u normal -i media-playback-stop \
        "Готово" "Сконвертирован: $(basename "$file")"
done
