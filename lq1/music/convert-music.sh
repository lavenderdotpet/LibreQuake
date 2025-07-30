#!/bin/bash

FFMPEG="ffmpeg"
FFMPEG_OPTS=(
    "-ar" "44100"
    "-ac" "2"
    "-c:a" "libvorbis"
    "-q:a" "2"
    "-y"
    "-loglevel" "quiet"
)
SRCDIR="./src"

# Declare associative array (key: output filename, value: source filename)
declare -A MUSICFILES
MUSICFILES["track02"]="track02.ogg"
MUSICFILES["track03"]="track03.ogg"
MUSICFILES["track04"]="track04.ogg"
MUSICFILES["track05"]="track05.ogg"
MUSICFILES["track06"]="track06.ogg"
MUSICFILES["track07"]="track07.ogg"
MUSICFILES["track08"]="track08.ogg"
MUSICFILES["track09"]="track09.ogg"
MUSICFILES["track10"]="track10.ogg"
MUSICFILES["track11"]="track11.ogg"

for dst in "${!MUSICFILES[@]}"; do
    src="${MUSICFILES[$dst]}"
    output="${dst}.ogg"

    echo "converting music track $dst..."

    # Build command as array
    ffmpeg_cmd=(
        "$FFMPEG"
        "-i" "${SRCDIR}/${src}"
        "${FFMPEG_OPTS[@]}"
        "$output"
    )

    # Execute command
    if ! "${ffmpeg_cmd[@]}"; then
        echo "Error converting $src" >&2
        exit 1
    fi
done

