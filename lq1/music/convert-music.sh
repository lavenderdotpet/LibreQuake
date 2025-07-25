#!/bin/bash

FFMPEG="ffmpeg"
FFMPEG_OPTS="-ar 44100 -ac 2 -c:a libvorbis -q:a 2 -y -loglevel quiet"
SRCDIR="./src/"

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
    src=${MUSICFILES[$dst]}

    echo "converting music track $dst..."

    command="${FFMPEG} -i ${SRCDIR}${src} ${FFMPEG_OPTS} ${dst}.ogg"

    $command
done
