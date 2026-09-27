# Lab02 — Currency Exchange Rate CLI

Script Python care interacționează cu serviciul **Currency Exchange Rate**
(furnizat în `lab02prep`) pentru a obține cursul de schimb dintre două
monede, la o dată specificată, și pentru a salva rezultatul într-un fișier
JSON.

## Cerințe preliminare

Serviciul API trebuie să ruleze înainte de a folosi scriptul. Din proiectul
`lab02prep`:

```bash
cp sample.env .env
docker-compose up --build
```

Serviciul va fi disponibil implicit la `http://localhost:8080`.

## Instalare dependențe

Scriptul are nevoie de Python 3.8+ și de biblioteca `requests`.

1. (Opțional, dar recomandat) creează un mediu virtual:

   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Linux/Mac
   venv\Scripts\activate           # Windows
   ```

2. Instalează dependențele din `requirements.txt`:

   ```bash
   pip install -r lab02/requirements.txt
   ```

## Configurare cheie API

Serviciul cere o cheie API (`API_KEY`) trimisă la fiecare cerere. Poți seta
cheia în două moduri:

- ca variabilă de mediu:

  ```bash
  export API_KEY=EXAMPLE_API_KEY        # Linux/Mac
  set API_KEY=EXAMPLE_API_KEY           # Windows (cmd)
  ```

- sau direct ca parametru la rulare, cu `--key` (vezi exemplele de mai jos).

## Cum se rulează scriptul

Sintaxă generală:

```bash
python lab02/currency_exchange_rate.py --from <MONEDA_SURSA> --to <MONEDA_DESTINATIE> --date <YYYY-MM-DD> [--key <API_KEY>] [--base-url <URL>]
```

Parametri:

| Parametru     | Obligatoriu | Descriere                                                             |
|---------------|:-----------:|-------------------------------------------------------------------------|
| `--from`      | da          | Codul monedei sursă, 3 litere mari (ex: `USD`)                          |
| `--to`        | da          | Codul monedei destinație, 3 litere mari (ex: `EUR`)                     |
| `--date`      | da          | Data pentru care se cere cursul, format `YYYY-MM-DD`                    |
| `--key`       | nu          | Cheia API. Dacă lipsește, se citește din variabila de mediu `API_KEY`.  |
| `--base-url`  | nu          | URL-ul serviciului (implicit `http://localhost:8080`)                   |

### Exemple

Curs USD → EUR pentru 5 ianuarie 2025:

```bash
python lab02/currency_exchange_rate.py --from USD --to EUR --date 2025-01-05
```

Curs USD → MDL, cu cheia API dată explicit:

```bash
python lab02/currency_exchange_rate.py --from USD --to MDL --date 2025-06-04 --key EXAMPLE_API_KEY
```

Rulare pe mai multe date (exemplu, în Bash), pentru intervalul suportat de
serviciu (`2025-01-01` – `2025-09-15`):

```bash
for d in 2025-01-01 2025-02-21 2025-04-14 2025-06-04 2025-07-26 2025-09-15; do
    python lab02/currency_exchange_rate.py --from USD --to MDL --date "$d"
done
```

### Rezultate

- La succes, scriptul afișează cursul în consolă și salvează un fișier JSON
  în directorul `data/` (creat automat la rădăcina proiectului, dacă nu
  există deja), cu numele `<FROM>_<TO>_<DATE>.json`, de exemplu:

  ```
  data/USD_EUR_2025-01-05.json
  ```

  Conținut exemplu:

  ```json
  {
    "from": "USD",
    "to": "EUR",
    "date": "2025-01-05",
    "rate": 1.032801089243718,
    "retrieved_at": "2026-09-27T16:58:32"
  }
  ```

- La eroare (parametri invalizi, cheie API greșită, serviciu indisponibil
  etc.), scriptul afișează un mesaj clar în consolă (pe `stderr`) și scrie o
  linie cu timestamp în fișierul `error.log`, creat la rădăcina proiectului.
  Codul de ieșire (`exit code`) este `1` la eroare și `0` la succes.

## Structura scriptului

Scriptul (`currency_exchange_rate.py`) este organizat în funcții mici, fiecare
cu o singură responsabilitate:

- **`parse_arguments()`** — definește și citește parametrii din linia de
  comandă (`--from`, `--to`, `--date`, `--key`, `--base-url`) folosind
  `argparse`.
- **`is_valid_currency_code(code)`** — validează, printr-o expresie
  regulată, că un cod de monedă are formatul corect (3 litere mari).
- **`is_valid_date(date_str)`** — validează formatul (`YYYY-MM-DD`) și
  corectitudinea calendaristică a datei primite.
- **`fetch_exchange_rate(...)`** — trimite cererea HTTP (POST, cu `from`,
  `to`, `date` ca parametri GET și `key` ca parametru POST, conform API-ului)
  și interpretează răspunsul; ridică excepția `CurrencyApiError` pentru orice
  problemă (conexiune eșuată, timeout, cod HTTP diferit de 200, JSON invalid,
  câmp `error` completat în răspuns).
- **`save_result_to_json(...)`** — creează (dacă nu există) directorul
  `data/` la rădăcina proiectului și salvează rezultatul într-un fișier JSON
  cu numele derivat din monede și dată.
- **`log_error(message)`** — afișează mesajul de eroare în consolă și îl
  adaugă, cu timestamp, în `error.log`, la rădăcina proiectului.
- **`main()`** — orchestrează întregul flux: citește parametrii, îi
  validează, apelează API-ul, salvează rezultatul sau, în caz de eroare,
  apelează `log_error` și încheie execuția cu codul `1`.

### Notă despre serviciul API

Din testele efectuate asupra serviciului `lab02prep`, moneda `RUS` (definită
în `lib/currency.php`) nu corespunde cu cheia `rub` folosită efectiv în
`data.json`, astfel încât orice cerere care implică `RUS` va returna eroarea
`"Unknown currency rus"`. Aceasta este o inconsistență a serviciului furnizat,
nu a scriptului — scriptul tratează corect această situație, afișând eroarea
primită de la API și scriind-o în `error.log`.
