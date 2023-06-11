#!/bin/sh

if [ "$PROGRAM_TYPE" = "worker" ]; then
    python3 worker.py
fi
if [ "$PROGRAM_TYPE" = "bot" ]; then
    python3 main.py
else
    echo "Invalid env value - $PROGRAM_TYPE"
    exit 1
fi
