#!/bin/sh

if [ "$PROGRAM_TYPE" = "worker" ]; then
    python3 worker.py && exit
fi
if [ "$PROGRAM_TYPE" = "notify" ]; then
    python3 notify.py && exit
fi
if [ "$PROGRAM_TYPE" = "bot" ]; then
    python3 db_init.py
    python3 main.py && exit
else
    echo "Invalid env value - $PROGRAM_TYPE"
    exit 1
fi
