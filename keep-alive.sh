#!/bin/bash

PROCESS=$1

echo -e "Starting $PROCESS...\n"

until $PROCESS; do
    echo "Process '$PROCESS' crashed with exit code $?. Respawning..." >&2
    sleep 1
done