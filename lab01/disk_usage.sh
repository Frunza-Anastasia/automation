#!/bin/bash

if [ $# -lt 2 ] || [ $# -gt 4 ]; then
   echo "Numarul min de argumente trebuie sa fie 2, iar max 4"
   exit 1
fi

DIRECTORUL="$1"
MAX_SIZE_MB="$2"
THRESHOLD="${3:-80}"
EMAIL="$4"

if [ ! -d "${DIRECTORUL}" ]; then
   echo "Directorul ${DIRECTORUL} nu exista"
   exit 1
fi

if ! [[ "${MAX_SIZE_MB}" =~ ^[0-9]+$ ]]; then
   echo "Lungimea maxima trebuie sa fie un numar pozitiv"
   exit 1
fi 

if ! [[ "${THRESHOLD}" =~ ^[0-9]+$ ]] || [ "${THRESHOLD}" -lt 1 ] || [ "${THRESHOLD}" -gt 100 ]; then
   echo "Threshold trebuie sa fi un numar intre 1 si 100"
   exit 1
fi 

if [ "${MAX_SIZE_MB}" = 0 ]; then
   echo "Lungimea maxima nu poate fi 0"
   exit 1
fi

USED_BYTES=$(du -sb "${DIRECTORUL}" | cut -f1)
USED_MB=$((USED_BYTES / 1024 / 1024))
USAGE_PERCENT=$((USED_MB * 100 / MAX_SIZE_MB))

LOG_FILE="disk_usage.log"

echo "Directorul: $DIRECTORUL" >> "${LOG_FILE}"
echo "Spatiul folosit: ${USED_MB} MB" >> "${LOG_FILE}"
echo "Max spatiu rezervat: ${MAX_SIZE_MB} MB" >> "${LOG_FILE}"
echo "Procent folosit: ${USAGE_PERCENT}%" >> "${LOG_FILE}"
echo "Threshold: ${THRESHOLD}%" >> "${LOG_FILE}"

if [ "${USAGE_PERCENT}" -gt "${THRESHOLD}" ]; then
   if [ -n "$EMAIL" ]; then

        if command -v mail >/dev/null 2>&1; then
            echo "Spatiul pentru ${DIRECTORUL} este ${USAGE_PERCENT}%, ce extinde ${THRESHOLD}%." \
            | mail -s "Spatiul ocupat in disk" "$EMAIL"

            echo "Notificarea a fost trimisa la  $EMAIL"
        else
            echo "Nu e posibila trimiterea la emailul specificat"
        fi

    else
        echo "Emailul nu e specificat."
    fi
else
    echo "Spatiul din disk nu extinde limita de 80 procente"
fi

