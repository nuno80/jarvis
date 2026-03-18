"""
travel_agent.py — Travel Agent ibrido per JARVIS.

Architettura:
  1. Python chiama direttamente le API RapidAPI (Google Flights) → genera file JSON
  2. L'agente JARVIS (LLM via Ollama) legge i JSON e prende decisioni

Requisiti:
  - File .env con RAPIDAPI_KEY e ZEROCLAW_API_KEY
  - Ollama attivo con modello qwen3.5:9b (porta 11434)
"""

import os
import sys
import json
import asyncio
import requests
from pathlib import Path
from dotenv import load_dotenv
from zeroclaw_tools import create_agent, tool
from langchain_core.messages import HumanMessage

# ==========================================
# CONFIGURAZIONE
# ==========================================
load_dotenv()
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
HEADERS = {
    "x-rapidapi-host": "google-flights2.p.rapidapi.com",
    "x-rapidapi-key": RAPIDAPI_KEY
}

# Cartella dove salvare i JSON generati dalle API
DATA_DIR = Path(__file__).parent
FLIGHTS_FILE = DATA_DIR / "mock_flights.json"
BOOKING_FILE = DATA_DIR / "mock_booking.json"
URL_FILE = DATA_DIR / "mock_url.json"


# ══════════════════════════════════════════════════════════════
# STEP 1-2-3: CHIAMATE API DIRETTE (Python puro, niente LLM)
# ══════════════════════════════════════════════════════════════

def step1_cerca_voli(origine: str, destinazione: str, data: str, giorni: str) -> dict:
    """STEP 1: Cerca voli e salva in mock_flights.json"""
    print("1️⃣  Ricerca voli in corso...")
    url = "https://google-flights2.p.rapidapi.com/api/v1/searchFlights"
    params = {
        "departure_id": origine, "arrival_id": destinazione,
        "outbound_date": data, "trip_type": "ROUND",
        "trip_days": giorni, "travel_class": "ECONOMY",
        "adults": "1", "currency": "USD", "country_code": "US"
    }

    resp = requests.get(url, headers=HEADERS, params=params)
    if resp.status_code != 200:
        print(f"   ❌ Errore API: {resp.status_code}")
        return {}

    dati = resp.json()
    with open(FLIGHTS_FILE, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=4, ensure_ascii=False)

    quota = resp.headers.get("x-ratelimit-requests-remaining", "?")
    print(f"   ✅ Voli salvati in {FLIGHTS_FILE.name} (quota rimanente: {quota})")
    return dati


def step2_dettagli_tariffe(booking_token: str) -> dict:
    """STEP 2: Ottiene tariffe e salva in mock_booking.json"""
    print("2️⃣  Recupero opzioni tariffarie...")
    url = "https://google-flights2.p.rapidapi.com/api/v1/getBookingDetails"
    params = {"booking_token": booking_token}

    resp = requests.get(url, headers=HEADERS, params=params)
    if resp.status_code != 200:
        print(f"   ❌ Errore API: {resp.status_code}")
        return {}

    dati = resp.json()
    with open(BOOKING_FILE, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=4, ensure_ascii=False)

    quota = resp.headers.get("x-ratelimit-requests-remaining", "?")
    print(f"   ✅ Tariffe salvate in {BOOKING_FILE.name} (quota rimanente: {quota})")
    return dati


def step3_link_pagamento(token_tariffa: str) -> dict:
    """STEP 3: Genera link di checkout e salva in mock_url.json"""
    print("3️⃣  Generazione link di pagamento...")
    url = "https://google-flights2.p.rapidapi.com/api/v1/getBookingURL"
    params = {"token": token_tariffa}

    resp = requests.get(url, headers=HEADERS, params=params)
    if resp.status_code != 200:
        print(f"   ❌ Errore API: {resp.status_code}")
        return {}

    dati = resp.json()
    with open(URL_FILE, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=4, ensure_ascii=False)

    quota = resp.headers.get("x-ratelimit-requests-remaining", "?")
    print(f"   ✅ Link salvato in {URL_FILE.name} (quota rimanente: {quota})")
    return dati


def esegui_pipeline_api(origine, destinazione, data, giorni):
    """Esegue i 3 step API in sequenza, estraendo i token automaticamente."""

    # STEP 1: Ricerca voli
    dati_voli = step1_cerca_voli(origine, destinazione, data, giorni)
    voli = dati_voli.get("data", {}).get("itineraries", {}).get("topFlights", [])
    if not voli:
        print("   ⚠️ Nessun volo trovato. Pipeline interrotta.")
        return False

    booking_token = voli[0].get("booking_token")
    prezzo = voli[0].get("price")
    print(f"   📋 Miglior volo: ${prezzo} — token estratto")

    # STEP 2: Dettagli tariffe
    dati_tariffe = step2_dettagli_tariffe(booking_token)
    opzioni = dati_tariffe.get("data", [])
    if not opzioni:
        print("   ⚠️ Nessuna tariffa trovata. Pipeline interrotta.")
        return False

    token_tariffa = opzioni[0].get("token")
    classe = opzioni[0].get("cabin")
    prezzo_finale = opzioni[0].get("price")
    print(f"   📋 Tariffa: {classe} a ${prezzo_finale} — token estratto")

    # STEP 3: Link pagamento
    dati_url = step3_link_pagamento(token_tariffa)
    if not dati_url:
        print("   ⚠️ Link non generato. Pipeline interrotta.")
        return False

    print(f"   📋 Link checkout generato e salvato")
    return True


# ══════════════════════════════════════════════════════════════
# TOOL PER JARVIS: Legge i file JSON generati dalla pipeline
# ══════════════════════════════════════════════════════════════

@tool
def leggi_risultati_voli() -> str:
    """Legge il file mock_flights.json con i risultati della ricerca voli.
    Restituisce un riepilogo dei voli disponibili con prezzi e compagnie."""
    try:
        with open(FLIGHTS_FILE, "r", encoding="utf-8") as f:
            dati = json.load(f)
        voli = dati.get("data", {}).get("itineraries", {}).get("topFlights", [])
        if not voli:
            return "Nessun volo trovato nel file."

        righe = []
        for i, volo in enumerate(voli[:5]):  # Max 5 voli
            prezzo = volo.get("price", "N/A")
            legs = volo.get("legs", [])
            info_gambe = []
            for leg in legs:
                compagnia = leg.get("airline", "N/A")
                partenza = leg.get("departure", "N/A")
                arrivo = leg.get("arrival", "N/A")
                durata = leg.get("duration", "N/A")
                scali = leg.get("stops", 0)
                info_gambe.append(f"  {compagnia}: {partenza} -> {arrivo} ({durata}min, {scali} scali)")
            righe.append(f"Volo {i+1}: ${prezzo}\n" + "\n".join(info_gambe))
        return "\n\n".join(righe)
    except FileNotFoundError:
        return "File mock_flights.json non trovato. Esegui prima la ricerca voli."
    except Exception as e:
        return f"Errore lettura: {e}"


@tool
def leggi_tariffe() -> str:
    """Legge il file mock_booking.json con le opzioni tariffarie disponibili.
    Restituisce classe, prezzo e dettagli bagaglio per ogni opzione."""
    try:
        with open(BOOKING_FILE, "r", encoding="utf-8") as f:
            dati = json.load(f)
        opzioni = dati.get("data", [])
        if not opzioni:
            return "Nessuna tariffa trovata nel file."

        righe = []
        for i, opt in enumerate(opzioni[:5]):
            classe = opt.get("cabin", "N/A")
            prezzo = opt.get("price", "N/A")
            bagagli = opt.get("extensions", [])
            bagagli_str = ", ".join(bagagli[:3]) if bagagli else "Non specificato"
            righe.append(f"Tariffa {i+1}: {classe} a ${prezzo} — Bagagli: {bagagli_str}")
        return "\n".join(righe)
    except FileNotFoundError:
        return "File mock_booking.json non trovato. Esegui prima il recupero tariffe."
    except Exception as e:
        return f"Errore lettura: {e}"


@tool
def leggi_link_pagamento() -> str:
    """Legge il file mock_url.json con il link di checkout per acquistare il biglietto."""
    try:
        with open(URL_FILE, "r", encoding="utf-8") as f:
            dati = json.load(f)

        link = "URL non trovato"
        if isinstance(dati, dict):
            if "data" in dati:
                if isinstance(dati["data"], str):
                    link = dati["data"]
                elif isinstance(dati["data"], dict):
                    link = dati["data"].get("url", "URL mancante")
            elif "url" in dati:
                link = dati["url"]
        elif isinstance(dati, str):
            link = dati
        return f"Link di acquisto: {link}"
    except FileNotFoundError:
        return "File mock_url.json non trovato. Esegui prima la generazione del link."
    except Exception as e:
        return f"Errore lettura: {e}"


# ══════════════════════════════════════════════════════════════
# ESECUZIONE PRINCIPALE
# ══════════════════════════════════════════════════════════════

async def main():
    print("=" * 60)
    print("  JARVIS Travel Agent — Modalita' ibrida")
    print("  (API dirette + analisi LLM)")
    print("=" * 60)

    if not RAPIDAPI_KEY:
        print("❌ RAPIDAPI_KEY mancante nel file .env!")
        sys.exit(1)

    # ── FASE 1: Pipeline API (Python puro) ──
    print("\n📡 FASE 1: Chiamate API dirette a Google Flights\n")
    successo = esegui_pipeline_api(
        origine="LAX",
        destinazione="JFK",
        data="2026-04-13",
        giorni="13"
    )

    if not successo:
        print("\n❌ Pipeline API fallita. Controlla la chiave RapidAPI e riprova.")
        sys.exit(1)

    # ── FASE 2: JARVIS analizza i risultati ──
    print("\n\n🧠 FASE 2: JARVIS analizza i risultati\n")

    agent = create_agent(
        tools=[leggi_risultati_voli, leggi_tariffe, leggi_link_pagamento],
        model="qwen3.5:9b",
        api_key=os.environ.get("ZEROCLAW_API_KEY", "ollama"),
        base_url="http://localhost:11434/v1",
        system_prompt=(
            "Sei JARVIS, un assistente di viaggio esperto. "
            "Hai a disposizione dei tool per leggere i dati sui voli gia' scaricati. "
            "Usa SEMPRE i tool per leggere i file prima di rispondere. "
            "Rispondi in italiano, in modo chiaro e conciso."
        ),
    )

    prompt = (
        "Ho cercato voli da Los Angeles (LAX) a New York (JFK) per il 13 aprile 2026, "
        "13 giorni di viaggio. Leggi i risultati dei voli, le tariffe disponibili e il "
        "link di pagamento dai file generati, poi fammi un riepilogo completo con la "
        "tua raccomandazione."
    )

    print(f"👤 Utente: {prompt}\n")
    print("⏳ JARVIS sta leggendo e analizzando i dati...\n")

    risultato = await agent.ainvoke({
        "messages": [HumanMessage(content=prompt)]
    })

    print("=" * 60)
    print("✈️  RISPOSTA DI JARVIS:")
    print("=" * 60)
    print(risultato["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
