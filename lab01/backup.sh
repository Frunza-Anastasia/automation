#!/bin/bash

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "Trebuie sa fie maximum 2 argumente transmise"
    exit 1
fi

SOURCE_DIR="$1"
BACKUP_DIR="${2:-/backup}"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "Director sursa '${SOURCE_DIR}' nu exista."
    exit 1
fi

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Backup director '${BACKUP_DIR}' nu exista."
    exit 1
fi

DATE=$(date +"%Y-%m-%d_%H-%M-%S")
DIR_NAME=$(basename "$SOURCE_DIR")
ARCHIVE="$BACKUP_DIR/${DIR_NAME}_${DATE}.tar.gz"

tar -czf "$ARCHIVE" -C "$(dirname "$SOURCE_DIR")" "$DIR_NAME"

if [ $? -eq 0 ]; then
    echo "Backup a fost creat!:"
    echo "$ARCHIVE"
else
    echo "Backup a esuat."
    exit 1
fi
