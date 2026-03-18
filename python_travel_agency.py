#STEP 1: Ricerca dei Voli (La Mappa Generale)

import requests
import json

# --- 1. CHIAMATA ONLINE (Consuma 1 quota) ---
url_search = "https://google-flights2.p.rapidapi.com/api/v1/searchFlights"
querystring_search = {
    "departure_id": "LAX",
    "arrival_id": "JFK",
    "outbound_date": "2026-04-13",
    "trip_type": "ROUND",
    "trip_days": "13",
    "travel_class": "ECONOMY",
    "adults": "1",
    "currency": "USD",
    "country_code": "US"
}
headers = {
    "x-rapidapi-host": "google-flights2.p.rapidapi.com",
    "x-rapidapi-key": "INSERISCI_LA_TUA_CHIAVE_API_QUI"
}

print("1. Ricerca dei voli in corso...")
risposta_voli = requests.get(url_search, headers=headers, params=querystring_search)

if risposta_voli.status_code == 200:
    dati_voli = risposta_voli.json()

    # Salva il file per uso offline
    with open("mock_flights.json", "w", encoding="utf-8") as f:
        json.dump(dati_voli, f, indent=4)
    print(f"📊 Quota rimanente: {risposta_voli.headers.get('x-ratelimit-requests-remaining')}")
else:
    print(f"Errore: {risposta_voli.status_code}")

# --- 2. LETTURA OFFLINE ED ESTRAZIONE ---
print("\n--- RISULTATI RICERCA ---")
with open("mock_flights.json", "r", encoding="utf-8") as f:
    dati_salvati = json.load(f)

# Prendiamo i voli migliori
voli = dati_salvati.get("data", {}).get("itineraries", {}).get("topFlights", [])

if voli:
    # Simuliamo che l'utente scelga la PRIMA opzione (Indice 0)
    volo_scelto = voli[0]
    prezzo = volo_scelto.get("price")
    token_volo = volo_scelto.get("booking_token")

    print(f"L'utente ha scelto il volo da ${prezzo}.")
    print(f"Token estratto: {token_volo[:20]}...")
else:
    print("Nessun volo trovato.")


# STEP 2: Scelta della Tariffa e Bagagli (I Dettagli)
# Ora usiamo il token_volo ottenuto dallo script precedente per chiedere all'API le varie opzioni (es. Basic Economy vs Main Cabin) per quello specifico aereo.import requests

import json

# NOTA: In un'app vera, 'token_volo' passerebbe dinamicamente dallo Step 1 a qui.
# Qui lo rileggiamo dal file locale per simulazione.
with open("mock_flights.json", "r", encoding="utf-8") as f:
    token_volo = json.load(f)["data"]["itineraries"]["topFlights"][0]["booking_token"]

# --- 1. CHIAMATA ONLINE (Consuma 1 quota) ---
url_details = "https://google-flights2.p.rapidapi.com/api/v1/getBookingDetails"
querystring_details = {"booking_token": token_volo}
headers = {
    "x-rapidapi-host": "google-flights2.p.rapidapi.com",
    "x-rapidapi-key": "INSERISCI_LA_TUA_CHIAVE_API_QUI"
}

print("2. Recupero delle opzioni tariffarie in corso...")
risposta_dettagli = requests.get(url_details, headers=headers, params=querystring_details)

if risposta_dettagli.status_code == 200:
    dati_dettagli = risposta_dettagli.json()

    # Salva il file per uso offline
    with open("mock_booking.json", "w", encoding="utf-8") as f:
        json.dump(dati_dettagli, f, indent=4)
    print(f"📊 Quota rimanente: {risposta_dettagli.headers.get('x-ratelimit-requests-remaining')}")
else:
    print(f"Errore: {risposta_dettagli.status_code}")

# --- 2. LETTURA OFFLINE ED ESTRAZIONE ---
print("\n--- OPZIONI DI ACQUISTO ---")
with open("mock_booking.json", "r", encoding="utf-8") as f:
    dati_salvati_dettagli = json.load(f)

opzioni_tariffarie = dati_salvati_dettagli.get("data", [])

if opzioni_tariffarie:
    # Simuliamo che l'utente scelga la PRIMA tariffa (Basic Economy)
    tariffa_scelta = opzioni_tariffarie[0]
    classe = tariffa_scelta.get("cabin")
    prezzo_finale = tariffa_scelta.get("price")
    token_tariffa = tariffa_scelta.get("token") # ECCO IL TOKEN FINALE!

    print(f"L'utente ha scelto la classe {classe} a ${prezzo_finale}.")
    print(f"Token finale estratto: {token_tariffa[:20]}...")
else:
    print("Nessuna opzione tariffaria trovata.")


# STEP 3: Generazione del Link di Pagamento (Il Checkout)
# Ultimo miglio! Usiamo il token_tariffa appena estratto per farci dare da Google/RapidAPI il link diretto al sito della compagnia aerea, gestendo lo scherzetto della "stringa grezza".

import requests
import json

# Rileggiamo il token finale dal file (simulando il passaggio dal frontend)
with open("mock_booking.json", "r", encoding="utf-8") as f:
    token_tariffa = json.load(f)["data"][0]["token"]

# --- 1. CHIAMATA ONLINE (Consuma 1 quota) ---
url_url = "https://google-flights2.p.rapidapi.com/api/v1/getBookingURL"
querystring_url = {"token": token_tariffa}
headers = {
    "x-rapidapi-host": "google-flights2.p.rapidapi.com",
    "x-rapidapi-key": "INSERISCI_LA_TUA_CHIAVE_API_QUI"
}

print("3. Generazione link di pagamento in corso...")
risposta_url = requests.get(url_url, headers=headers, params=querystring_url)

if risposta_url.status_code == 200:
    dati_url = risposta_url.json()
    link_acquisto = "URL non trovato"

    # --- LA LOGICA INTELLIGENTE PER ESTRARRE IL LINK ---
    if isinstance(dati_url, dict):
        if "data" in dati_url:
            if isinstance(dati_url["data"], str):
                link_acquisto = dati_url["data"]
            elif isinstance(dati_url["data"], dict):
                link_acquisto = dati_url["data"].get("url", "URL mancante")
        elif "url" in dati_url:
            link_acquisto = dati_url["url"]
    elif isinstance(dati_url, str):
        link_acquisto = dati_url

    print(f"\n✅ REINDIRIZZA L'UTENTE QUI: \n{link_acquisto}")
    print(f"\n📊 Quota rimanente: {risposta_url.headers.get('x-ratelimit-requests-remaining')}")
else:
    print(f"Errore: {risposta_url.status_code}")
