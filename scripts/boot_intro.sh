#!/bin/bash

set -e

INTRO_VIDEO="/home/pi/intro.mp4"
INTRO_IMAGE="/home/pi/intro.png"
INTRO_AUDIO="/home/pi/intro.wav"

echo "Reproduciendo intro personalizada..."

if [ -f "$INTRO_VIDEO" ]; then
    if command -v mpv >/dev/null 2>&1; then
        mpv --fs --no-terminal --really-quiet "$INTRO_VIDEO"
    fi
elif [ -f "$INTRO_IMAGE" ] && [ -f "$INTRO_AUDIO" ]; then
    if command -v mpv >/dev/null 2>&1; then
        mpv --fs --no-terminal --really-quiet --audio-file="$INTRO_AUDIO" "$INTRO_IMAGE"
    fi
else
    echo "No se encontró intro personalizada. Continuando..."
fi

exit 0
