#!/bin/bash

mode="$1"
shift

case "$mode" in
    -convert-webm)
        cmd='ffmpeg -i "$file" -map_metadata 0 -movflags -o "$out"'
        ext="webm"
        ;;

    -convert-mp4-x264)
        cmd='ffmpeg -i "$file" -c:v libx264 -c:a copy -map_metadata 0 -movflags +faststart "$out"'
        ext="x264.mp4"
        ;;

    -convert-mp4-x265)
        cmd='ffmpeg -i "$file" -c:v libx265 -crf 28 -c:a copy -map_metadata 0 -movflags +faststart "$out"'
        ext="x265.mp4"
        ;;

    -convert-mp4-av1)
        cmd='ffmpeg -i "$file" -c:v librav1e -crf 28 -c:a copy -map_metadata 0 -movflags +faststart "$out"'
        ext="av1.mp4"
        ;;

    *)
        echo "Неизвестный режим"
        exit 1
        ;;
esac

for file in "$@"; do
    base="${file%.*}"
    out="${base}.${ext}"

    notify-send -u low -i media-playback-start \
        "Конвертация" "Файл: $(basename "$file")"

    eval $cmd

    touch -r "$file" "$out"

    notify-send -u normal -i media-playback-stop \
        "Готово" "Сконвертирован: $(basename "$file")"
done
