# Currency Exchange Rate — Script CLI

Script Python în linia de comandă care interacționează cu API-ul Currency
Exchange Rate (furnizat în `lab02prep`) pentru a obține cursul de schimb
dintre două monede, la o dată specificată, și salvează rezultatul într-un
fișier JSON.

## 1. Cum se instalează dependențele necesare

Scriptul are nevoie de Python 3.8+ și de biblioteca `requests`.

Mai întâi, opțional dar recomandat, se creează și se activează un mediu
virtual:

```bash
python -m venv venv
```

Pe Windows se activează cu `.\venv\Scripts\Activate.ps1`, iar pe Linux/Mac
cu `source venv/bin/activate`.

Apoi se instalează dependențele din fișierul `requirements.txt`:

```bash
pip install -r requirements.txt
```

Acest fișier conține o singură dependență: `requests`.

Înainte de a folosi scriptul, trebuie pornit și serviciul API propriu-zis,
din proiectul `lab02prep`:

```bash
cp sample.env .env
docker-compose up --build
```

Serviciul va fi disponibil la adresa `http://localhost:8080`.

## 2. Cum se rulează scriptul

Sintaxa generală este următoarea:

```bash
python currency_exchange_rate.py --from <MONEDA_SURSA> --to <MONEDA_DESTINATIE> --date <YYYY-MM-DD> [--key <API_KEY>] [--base-url <URL>]
```
ex: python automation\lab02\currency_exchange_rate.py --from USD --to MDL --date 2025-09-15

Parametrul `--from` este obligatoriu și reprezintă codul monedei sursă, scris
cu 3 litere mari, de exemplu `USD`. Parametrul `--to` este de asemenea
obligatoriu și reprezintă codul monedei destinație, în același format, de
exemplu `EUR`. Parametrul `--date` este obligatoriu și reprezintă data
pentru care se cere cursul, în formatul `YYYY-MM-DD`. Parametrul `--key`
este opțional; dacă lipsește, cheia API este citită automat din variabila
de mediu `API_KEY`. Parametrul `--base-url` este de asemenea opțional și
reprezintă adresa serviciului, implicit fiind `http://localhost:8080`.

Cheia API se poate seta o singură dată, pentru toată sesiunea de terminal:

```bash
$env:API_KEY="EXAMPLE_API_KEY"
```

(pe Windows, în PowerShell) sau, pe Linux/Mac:

```bash
export API_KEY=EXAMPLE_API_KEY
```

Exemplu simplu — cursul USD către EUR pentru data de 5 ianuarie 2025:

```bash
python currency_exchange_rate.py --from USD --to EUR --date 2025-01-05
```

Exemplu în care cheia API este dată explicit, fără variabilă de mediu:

```bash
python currency_exchange_rate.py --from USD --to MDL --date 2025-06-04 --key EXAMPLE_API_KEY
```

Exemplu de rulare pentru mai multe date la rând, în intervalul acceptat de
serviciu (2025-01-01 – 2025-09-15):

```bash
for d in 2025-01-01 2025-02-21 2025-04-14 2025-06-04 2025-07-26 2025-09-15; do
    python currency_exchange_rate.py --from USD --to MDL --date "$d"
done
```

La succes, scriptul afișează cursul în consolă și salvează un fișier JSON
numit după modelul `<FROM>_<TO>_<DATA>.json`, în directorul `data/` de la
rădăcina proiectului (creat automat dacă nu există), de exemplu
`data/USD_EUR_2025-01-05.json`, cu un conținut de forma:

```json
{
  "from": "USD",
  "to": "EUR",
  "date": "2025-01-05",
  "rate": 1.032801089243718,
  "retrieved_at": "2026-09-27T16:58:32"
}
```

La eroare (parametri invalizi, cheie API greșită, serviciu indisponibil
etc.), scriptul afișează un mesaj clar în consolă și adaugă o linie cu
timestamp în fișierul `error.log`, tot la rădăcina proiectului. Codul de
ieșire este `1` la eroare și `0` la succes.

## 3. Cum este structurat scriptul (funcțiile principale și logica)

Scriptul este organizat în funcții mici, fiecare cu o singură
responsabilitate.

Funcția `parse_arguments()` definește și citește parametrii din linia de
comandă (`--from`, `--to`, `--date`, `--key`, `--base-url`), folosind
biblioteca `argparse`.

Funcția `is_valid_currency_code(code)` validează, printr-o expresie
regulată, că un cod de monedă are formatul corect, adică 3 litere mari.

Funcția `is_valid_date(date_str)` validează atât formatul (`YYYY-MM-DD`),
cât și corectitudinea calendaristică a datei primite.

Funcția `fetch_exchange_rate(...)` trimite cererea HTTP către API, cu
`from`, `to` și `date` ca parametri GET și `key` ca parametru POST, exact
cum cere serviciul, apoi interpretează răspunsul primit. Aceasta ridică o
excepție proprie, `CurrencyApiError`, pentru orice problemă apărută:
conexiune eșuată, timeout, cod HTTP diferit de 200, răspuns care nu este
JSON valid, sau câmpul `error` completat în răspunsul primit de la server.

Funcția `save_result_to_json(...)` creează directorul `data/` la rădăcina
proiectului, dacă acesta nu există deja, și salvează rezultatul într-un
fișier JSON, numit după monedele folosite și data cerută.

Funcția `log_error(message)` afișează mesajul de eroare în consolă și îl
adaugă, cu timestamp, în fișierul `error.log`, la rădăcina proiectului.

Funcția `main()` coordonează întregul flux al programului: citește
parametrii din linia de comandă, îi validează pe rând, apelează API-ul,
salvează rezultatul în caz de succes, sau apelează funcția `log_error` și
încheie execuția cu codul `1` în caz de eroare.

O observație legată de serviciul API folosit: în urma testării, s-a
constatat că moneda `RUS`, definită în `lib/currency.php` din serviciu, nu
corespunde cu cheia `rub` folosită efectiv în `data.json`, astfel încât
orice cerere care implică moneda `RUS` va eșua mereu, cu mesajul
`"Unknown currency rus"`. Aceasta este o inconsistență a serviciului
furnizat, nu a scriptului — scriptul tratează corect această situație,
afișând eroarea primită de la API și scriind-o în `error.log`.