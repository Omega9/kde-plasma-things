#!/bin/bash

for file in "$@"; do
    base="${file%.*}"
    out="${base}.container.mp4"

    notify-send -u low -i media-playback-start \
        "Ремультиплексирование" "Файл: $(basename "$file")"

    if ffmpeg -v error -i "$file" \
        -map 0 \
        -c copy \
        -map_metadata 0 \
        -movflags +faststart \
        "$out"; then

        touch -r "$file" "$out"

        notify-send -u normal -i media-playback-stop \
            "Готово" "Сконвертирован: $(basename "$file")"

    else
        echo "WARN: несовместимые кодеки для MP4: $file" >&2

        notify-send -u critical -i dialog-warning \
            "Ошибка ремультиплексирования" \
            "MP4 не поддерживает кодеки файла:\n$(basename "$file")"

        rm -f "$out"
    fi
done
