Lab03 - Automatizarea scriptului cu cron

In acest laborator am facut ca scriptul currency_exchange_rate.py din lab02 sa ruleze automat cu cron, intr-un container Docker.

Sarcinile din fisierul cronjob:

in fiecare zi la 06:00 se ia cursul MDL -> EUR pentru ziua de ieri
in fiecare vineri la 17:00 se ia cursul MDL -> USD pentru saptamana trecuta (data de acum 7 zile)

Data se calculeaza automat cu comanda date. Tot ce afiseaza scriptul se scrie in /var/log/cron.log. Containerul foloseste ora Moldovei (Europe/Chisinau).

Cum se construieste si se porneste containerul

Mai intai pornesc Docker Desktop si astept sa scrie "Engine running".

Pornesc API-ul din lab02prep:

cd "C:\Users\naste\Downloads\lab02prep\lab02prep" Copy-Item sample.env .env docker compose up -d --build

Verific in browser ca merge: http://localhost:8080

Pornesc containerul cu cron:

cd "C:\Users\naste\Downloads\lab02_automation\automation\lab03" docker compose up -d --build

Oprire:

docker compose down

Cum verific ca sarcinile cron ruleaza

Vad sarcinile inregistrate:

docker exec currency-cron crontab -l

Vad ca procesul cron ruleaza (trebuie sa apara "cron -f"):

docker top currency-cron

Vad logul:

docker exec currency-cron cat /var/log/cron.log

Ca sa nu astept pana la ora programata, rulez manual aceeasi comanda:

docker exec currency-cron sh -c 'cd /app && python /app/lab03/currency_exchange_rate.py --from MDL --to EUR --date $(date -d yesterday +%Y-%m-%d) --base-url $API_BASE_URL >> /var/log/cron.log 2>&1' docker exec currency-cron cat /var/log/cron.log

Rezultatele JSON se salveaza in folderul lab03\data.

API-ul are date doar intre 2025-01-01 si 2025-09-15, asa ca pentru zilele de acum apare o eroare in log. Asta arata totusi ca sarcina cron a rulat.

Structura proiectului

currency_exchange_rate.py - scriptul din lab02 care ia cursul valutar si il salveaza in JSON requirements.txt - biblioteca requests necesara scriptului cronjob - cele doua sarcini cron entrypoint.sh - salveaza variabilele de mediu pentru cron, creeaza /var/log/cron.log si porneste cron Dockerfile - imaginea pe baza python:3.12-slim, instaleaza cron, copiaza fisierele si configureaza cron docker-compose.yml - construieste imaginea, seteaza cheia API si adresa API-ului si porneste containerul readme.md - acest fisier