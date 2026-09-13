#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Niciun argument nu a fost scris"
  exit 1
fi

DIRECTOR="$1"
shift

if [ ! -d "$DIRECTOR" ]; then
   echo "Directorul ${DIRECTOR} nu exista"
   exit 1
fi

if [ $# -eq 0 ]; then
  EXTENSIONS=(".tmp")
else
  EXTENSIONS=("$@")
fi

DELETED=0

for EXTENSION in "${EXTENSIONS[@]}"; do
   if [[ "${EXTENSION}" != .* ]]; then
      EXTENSION=".${EXTENSION}"
   fi
 
   while IFS= read -r -d '' FILE; do
      rm -- "${FILE}"

      if [ $? -eq 0 ]; then
         echo "Fisierul ${FILE}  a fost sters"
         ((DELETED++))
      fi
   done < <(find "${DIRECTOR}" -type f -name "*${EXTENSION}" -print0)
done

echo "Numarul de fisiere sterse este: ${DELETED}"
