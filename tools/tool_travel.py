"""
tool_travel.py — Tool di ricerca voli per JARVIS (con Cache)
Cerca voli, tariffe e genera link di acquisto via Google Flights (RapidAPI).
Salva risultati in data/travel_cache/ con TTL di 4 ore.

Ogni tool file esporta una lista TOOLS con i @tool disponibili.
jarvis_agent.py li scopre automaticamente.
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")
logger = get_logger("jarvis.tool.travel")

from zeroclaw_tools import tool

# ==========================================
# CONFIGURAZIONE
# ==========================================
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
HEADERS = {
    "x-rapidapi-host": "google-flights2.p.rapidapi.com",
    "x-rapidapi-key": RAPIDAPI_KEY or ""
}

PROJECT_ROOT = Path(__file__).parent.parent
CACHE_DIR = PROJECT_ROOT / "data" / "travel_cache"
CACHE_TTL_SECONDS = 4 * 60 * 60  # 4 ore


# ==========================================
# CACHE: Gestione lettura/scrittura
# ==========================================

def _cache_key(origine: str, destinazione: str, data: str, giorni: str) -> str:
    """Genera il nome della cartella cache per questa ricerca."""
    return f"{origine}_{destinazione}_{data}_{giorni}gg"


def _cache_path(key: str) -> Path:
    """Ritorna il path della cartella cache."""
    return CACHE_DIR / key


def _cache_is_valid(key: str) -> bool:
    """Controlla se la cache esiste e non è scaduta."""
    meta_file = _cache_path(key) / "metadata.json"
    if not meta_file.exists():
        return False
    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        cached_at = meta.get("timestamp", 0)
        return (time.time() - cached_at) < CACHE_TTL_SECONDS
    except Exception:
        return False


def _cache_save(key: str, flights: dict, booking: dict, url_data: dict, riepilogo: str):
    """Salva i risultati nella cache."""
    folder = _cache_path(key)
    folder.mkdir(parents=True, exist_ok=True)

    (folder / "flights.json").write_text(json.dumps(flights, indent=2, ensure_ascii=False), encoding="utf-8")
    (folder / "booking.json").write_text(json.dumps(booking, indent=2, ensure_ascii=False), encoding="utf-8")
    (folder / "url.json").write_text(json.dumps(url_data, indent=2, ensure_ascii=False), encoding="utf-8")

    meta = {
        "timestamp": time.time(),
        "data_ora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tratta": key,
        "ttl_ore": CACHE_TTL_SECONDS / 3600,
        "riepilogo": riepilogo
    }
    (folder / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Cache salvata: {key}")


def _cache_read_riepilogo(key: str) -> str:
    """Legge il riepilogo dalla cache."""
    meta_file = _cache_path(key) / "metadata.json"
    if not meta_file.exists():
        return ""
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    return meta.get("riepilogo", "")


def _format_riepilogo(origine, destinazione, data, giorni, voli, tariffa_info, link_info) -> str:
    """Formatta il riepilogo testuale dei risultati."""
    risultati = []
    for i, volo in enumerate(voli[:3]):
        prezzo = volo.get("price", "N/A")
        airline = volo.get("flights", [{}])[0].get("airline", "")
        durata = volo.get("duration", {}).get("text", "")
        risultati.append(f"Volo {i+1}: ${prezzo} ({airline}, {durata})")

    riepilogo = f"Tratta: {origine} → {destinazione} | Data: {data} | Durata: {giorni} giorni\n"
    riepilogo += "\n".join(risultati)
    if tariffa_info:
        riepilogo += f"\n{tariffa_info}"
    if link_info:
        riepilogo += f"\n{link_info}"
    return riepilogo


# ==========================================
# TOOL 1: RICERCA VOLI (con cache)
# ==========================================

@tool
def cerca_voli_completo(origine: str, destinazione: str, data: str, giorni: str) -> str:
    """Cerca voli di andata e ritorno, ottiene tariffe e link di acquisto.
    Richiede: origine (codice aeroporto es. FCO, LAX), destinazione (codice aeroporto es. JFK),
    data di partenza (formato YYYY-MM-DD), e numero di giorni di viaggio.
    Se l'utente fornisce nomi di citta', converti in codici aeroporto
    (es. Roma=FCO, Milano=MXP, New York=JFK, Londra=LHR, Parigi=CDG, Los Angeles=LAX).
    I risultati vengono salvati in cache per 4 ore."""

    if not RAPIDAPI_KEY:
        return "Errore: chiave RAPIDAPI_KEY non configurata nel file .env."

    # --- CHECK CACHE ---
    key = _cache_key(origine.upper(), destinazione.upper(), data, giorni)
    if _cache_is_valid(key):
        logger.info(f"Cache HIT: {key}")
        riepilogo = _cache_read_riepilogo(key)
        return f"[Da cache recente]\n{riepilogo}" if riepilogo else "Cache trovata ma vuota."

    logger.info(f"Cache MISS: {key} — chiamo API...")

    # --- STEP 1: Ricerca voli ---
    flights_data = {}
    booking_data = {}
    url_data = {}

    try:
        resp = requests.get(
            "https://google-flights2.p.rapidapi.com/api/v1/searchFlights",
            headers=HEADERS,
            params={
                "departure_id": origine, "arrival_id": destinazione,
                "outbound_date": data, "trip_type": "ROUND",
                "trip_days": giorni, "travel_class": "ECONOMY",
                "adults": "1", "currency": "USD", "country_code": "US"
            },
            timeout=15
        )
        if resp.status_code != 200:
            return f"Errore API ricerca voli: HTTP {resp.status_code}"

        flights_data = resp.json()
        voli = flights_data.get("data", {}).get("itineraries", {}).get("topFlights", [])
        if not voli:
            return "Nessun volo trovato per questa tratta e data."

        booking_token = voli[0].get("booking_token")
        miglior_prezzo = voli[0].get("price")
    except Exception as e:
        return f"Errore nella ricerca voli: {e}"

    # --- STEP 2: Dettagli tariffe ---
    tariffa_info = ""
    token_tariffa = None
    if booking_token:
        try:
            resp2 = requests.get(
                "https://google-flights2.p.rapidapi.com/api/v1/getBookingDetails",
                headers=HEADERS,
                params={"booking_token": booking_token},
                timeout=15
            )
            if resp2.status_code == 200:
                booking_data = resp2.json()
                opzioni = booking_data.get("data", [])
                if opzioni:
                    classe = opzioni[0].get("cabin", "Economy")
                    prezzo_tariffa = opzioni[0].get("price", miglior_prezzo)
                    token_tariffa = opzioni[0].get("token")
                    tariffa_info = f"Tariffa migliore: {classe} a ${prezzo_tariffa}"
        except Exception:
            tariffa_info = "Dettagli tariffa non disponibili."

    # --- STEP 3: Link di pagamento ---
    link_info = ""
    if token_tariffa:
        try:
            resp3 = requests.get(
                "https://google-flights2.p.rapidapi.com/api/v1/getBookingURL",
                headers=HEADERS,
                params={"token": token_tariffa},
                timeout=15
            )
            if resp3.status_code == 200:
                url_data = resp3.json()
                link = "non disponibile"
                if isinstance(url_data, dict):
                    if "data" in url_data:
                        if isinstance(url_data["data"], str):
                            link = url_data["data"]
                        elif isinstance(url_data["data"], dict):
                            link = url_data["data"].get("url", "non disponibile")
                    elif "url" in url_data:
                        link = url_data["url"]
                link_info = f"Link acquisto: {link}"
        except Exception:
            link_info = "Link di acquisto non disponibile."

    # --- Composizione + salvataggio cache ---
    riepilogo = _format_riepilogo(origine, destinazione, data, giorni, voli, tariffa_info, link_info)
    _cache_save(key, flights_data, booking_data, url_data, riepilogo)

    logger.info(f"Travel: pipeline completata, {len(voli)} voli trovati")
    return riepilogo


# ==========================================
# TOOL 2: CONSULTA RICERCHE PRECEDENTI
# ==========================================

@tool
def consulta_ricerche_voli(tratta: str = "") -> str:
    """Consulta le ricerche voli precedenti salvate in cache, senza fare nuove chiamate API.
    Parametro 'tratta' opzionale: filtra per tratta (es. 'LAX_JFK' o 'Roma' o 'New York').
    Se vuoto, mostra tutte le ricerche disponibili.
    Usa questo tool quando l'utente chiede 'quali voli avevi trovato?' o 'quanto costava?'."""

    if not CACHE_DIR.exists():
        return "Nessuna ricerca voli salvata in cache."

    ricerche = []
    for folder in sorted(CACHE_DIR.iterdir()):
        if not folder.is_dir():
            continue
        meta_file = folder / "metadata.json"
        if not meta_file.exists():
            continue

        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception:
            continue

        nome = folder.name
        # Filtra per tratta se specificato
        if tratta and tratta.upper() not in nome.upper():
            continue

        # Controlla se scaduta
        cached_at = meta.get("timestamp", 0)
        scaduta = (time.time() - cached_at) >= CACHE_TTL_SECONDS
        stato = "⚠️ SCADUTA" if scaduta else "✅ Valida"

        ricerche.append(
            f"📋 {nome} ({stato} — {meta.get('data_ora', '?')})\n"
            f"   {meta.get('riepilogo', 'Nessun riepilogo')}"
        )

    if not ricerche:
        msg = "Nessuna ricerca trovata"
        if tratta:
            msg += f" per '{tratta}'"
        return msg + ". Usa 'cerca_voli_completo' per fare una nuova ricerca."

    return f"Ricerche voli in cache ({len(ricerche)}):\n\n" + "\n\n".join(ricerche)


# ==========================================
# EXPORT
# ==========================================
TOOLS = [cerca_voli_completo, consulta_ricerche_voli]


# ==========================================
# TEST STANDALONE
# ==========================================
if __name__ == "__main__":
    print("Test tool travel con cache...\n")

    # Test ricerca (prima volta = API, seconda = cache)
    risultato = cerca_voli_completo.invoke({
        "origine": "LAX", "destinazione": "JFK",
        "data": "2026-04-13", "giorni": "13"
    })
    print(f"Ricerca:\n{risultato}\n")

    # Test consultazione cache
    cache = consulta_ricerche_voli.invoke({"tratta": ""})
    print(f"Cache:\n{cache}")
