#!/bin/bash

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "Trebuie sa fie min 1 argument"
    exit 1
fi

PDF_FILE="$1"
LANGUAGE="${2:-en}"

if [ ! -f "$PDF_FILE" ]; then
    echo "PDF file '$PDF_FILE' nu exista."
    exit 1
fi

if [ ! -r "$PDF_FILE" ]; then
    echo "PDF file '$PDF_FILE' nu e citibil."
    exit 1
fi

if ! command -v pdftotext >/dev/null 2>&1; then
    echo "'pdftotext' utility nu e instalat"
    exit 1
fi

if ! command -v tesseract >/dev/null 2>&1; then
    echo "'tesseract' utility nu e instalat"
    exit 1
fi

OUTPUT_FILE="${PDF_FILE%.pdf}.txt"
echo "Language: $LANGUAGE"

pdftotext "$PDF_FILE" "$OUTPUT_FILE"

if [ $? -eq 0 ] && [ -s "$OUTPUT_FILE" ]; then
    echo "Text extras cu succes."
    exit 0
fi


for IMAGE in "$TEMP_DIR"/page-*.png; do
    if [ -f "$IMAGE" ]; then
        tesseract "$IMAGE" stdout -l "$LANGUAGE" 2>errors.log >> "$OUTPUT_FILE"

        if [ $? -ne 0 ]; then
            echo "OCR a esuat pentru $IMAGE"
            exit 1
        fi

        echo "" >> "$OUTPUT_FILE"
    fi
done

rm -rf "$TEMP_DIR"

echo "OCR a fost completat cu succes"

