#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ERROR_LOG_PATH = PROJECT_ROOT / "error.log"

DEFAULT_BASE_URL = "http://localhost:8080"
CURRENCY_REGEX = re.compile(r"^[A-Z]{3}$")
DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class CurrencyApiError(Exception):
    """Exceptie ridicata atuncieaza o eroare sau un raspuns invalid."""
    
def is_valid_currency_code(code: str) -> bool:
    return bool(CURRENCY_REGEX.match(code))


def is_valid_date(date_str: str) -> bool:
    """Verifica daca data respecta formatul YYYY-MM-DD si este o data calendaristica valida."""
    if not DATE_REGEX.match(date_str):
        return False
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def parse_arguments(argv=None) -> argparse.Namespace:
    """Defineste si citeste parametrii din linia de comanda."""
    parser = argparse.ArgumentParser(
        description="Obtine cursul de schimb valutar intre doua monede, la o data specificata."
    )
    parser.add_argument(
        "--from", dest="from_currency", required=True,
        help="Moneda sursa, format 3 litere mari (ex: USD)",
    )
    parser.add_argument(
        "--to", dest="to_currency", required=True,
        help="Moneda destinatie, format 3 litere mari (ex: EUR)",
    )
    parser.add_argument(
        "--date", dest="date", required=True,
        help="Data pentru care se cere cursul, format YYYY-MM-DD (ex: 2025-01-05)",
    )
    parser.add_argument(
        "--key", dest="api_key", default=os.environ.get("API_KEY"),
        help="Cheia API. Daca lipseste, se foloseste variabila de mediu API_KEY.",
    )
    parser.add_argument(
        "--base-url", dest="base_url", default=DEFAULT_BASE_URL,
        help=f"URL-ul de baza al serviciului (implicit: {DEFAULT_BASE_URL})",
    )
    return parser.parse_args(argv)


def fetch_exchange_rate(base_url: str, api_key: str, from_currency: str,
                         to_currency: str, date: str, timeout: int = 10) -> dict:
    """
    Trimite cererea catre API si intoarce dictionarul cu datele cursului valutar.

    Ridica CurrencyApiError daca:
        - nu se poate realiza conexiunea catre server;
        - serverul raspunde cu o eroare HTTP;
        - raspunsul nu este un JSON valid;
        - campul "error" din raspuns nu este gol.
    """
    url = f"{base_url}/"
    params = {"from": from_currency, "to": to_currency, "date": date}
    payload = {"key": api_key}

    try:
        response = requests.post(url, params=params, data=payload, timeout=timeout)
    except requests.exceptions.ConnectionError as exc:
        raise CurrencyApiError(
            f"Nu se poate realiza conexiunea la server ({base_url}). "
            f"Verifica daca serviciul ruleaza. Detalii: {exc}"
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise CurrencyApiError(f"Cererea catre server a expirat (timeout). Detalii: {exc}") from exc
    except requests.exceptions.RequestException as exc:
        raise CurrencyApiError(f"Eroare la trimiterea cererii catre server: {exc}") from exc

    if response.status_code != 200:
        raise CurrencyApiError(
            f"Serverul a raspuns cu codul HTTP {response.status_code} "
            f"pentru {from_currency}->{to_currency} la data {date}."
        )

    try:
        body = response.json()
    except ValueError as exc:
        raise CurrencyApiError(
            f"Raspunsul primit de la server nu este un JSON valid: {exc}"
        ) from exc

    error_message = body.get("error", "")
    if error_message:
        raise CurrencyApiError(f"API a returnat o eroare: {error_message}")

    data = body.get("data")
    if not data:
        raise CurrencyApiError("Raspunsul API nu contine date valide (campul 'data' este gol).")

    return data

# Salvare rezultat / erori

def save_result_to_json(data: dict, from_currency: str, to_currency: str, date: str) -> Path:
    """Salveaza rezultatul intr-un fisier JSON in directorul data/, la radacina proiectului."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    file_name = f"{from_currency}_{to_currency}_{date}.json"
    file_path = DATA_DIR / file_name

    output = {
        "from": from_currency,
        "to": to_currency,
        "date": date,
        "rate": data.get("rate"),
        "retrieved_at": datetime.now().isoformat(timespec="seconds"),
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return file_path


def log_error(message: str) -> None:
    """Afiseaza mesajul de eroare in consola (stderr) si il salveaza in error.log."""
    print(f"Eroare: {message}", file=sys.stderr)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ERROR_LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")


# Punct de intrare

def main(argv=None) -> int:
    args = parse_arguments(argv)

    from_currency = args.from_currency.strip().upper()
    to_currency = args.to_currency.strip().upper()
    date = args.date.strip()

    if not is_valid_currency_code(from_currency):
        log_error(f"Parametrul 'from' este invalid: '{args.from_currency}'. "
                   f"Foloseste un cod de 3 litere mari, ex: USD.")
        return 1

    if not is_valid_currency_code(to_currency):
        log_error(f"Parametrul 'to' este invalid: '{args.to_currency}'. "
                   f"Foloseste un cod de 3 litere mari, ex: EUR.")
        return 1

    if not is_valid_date(date):
        log_error(f"Parametrul 'date' este invalid: '{args.date}'. "
                   f"Foloseste formatul YYYY-MM-DD, ex: 2025-01-05.")
        return 1

    if not args.api_key:
        log_error("Cheia API lipseste. Seteaz-o cu variabila de mediu API_KEY "
                   "sau cu parametrul --key.")
        return 1

    try:
        data = fetch_exchange_rate(
            base_url=args.base_url,
            api_key=args.api_key,
            from_currency=from_currency,
            to_currency=to_currency,
            date=date,
        )
    except CurrencyApiError as exc:
        log_error(str(exc))
        return 1

    try:
        file_path = save_result_to_json(data, from_currency, to_currency, date)
    except OSError as exc:
        log_error(f"Nu s-a putut salva fisierul JSON: {exc}")
        return 1

    print(f"Cursul {from_currency} -> {to_currency} la data {date} este {data.get('rate')}.")
    print(f"Rezultatul a fost salvat in: {file_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
