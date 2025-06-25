#!/bin/bash

PRESET="Fast  x265"

for file in "$@"; do
    # Базовое имя и имя выходного файла
    base="${file%.*}"
    out="${base}.x265.mp4"

    # Уведомление о начале
    notify-send -u low -i media-playback-start \
        "Конвертация" "Файл: $(basename "$file")"

    # Конвертация
    HandBrakeCLI -i "$file" -o "$out" --preset-import-gui --preset "$PRESET"

    # Сохраняем дату/время оригинала
    touch -r "$file" "$out"

    # Уведомление об окончании
    notify-send -u normal -i media-playback-stop \
        "Готово" "Сконвертирован: $(basename "$file")"
done
