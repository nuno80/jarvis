import requests

# Attenzione: l'URL ora finisce con /pair, non con /webhook!
URL = "http://127.0.0.1:42617/pair"

# Inserisci qui il PIN che vedi su WSL (se è cambiato, aggiornalo!)
headers = {
    "X-Pairing-Code": "509617"
}

print("🚀 Bussa alla porta con il PIN segreto...")

try:
    response = requests.post(URL, headers=headers, timeout=10)

    if response.status_code == 200:
        print("\n✅ VITTORIA! ZeroClaw ha accettato il PIN!")
        print("👇 ECCO LA TUA CHIAVE PERMANENTE 👇")
        print(response.json())
    else:
        print(f"\n❌ Errore {response.status_code}: Il PIN potrebbe essere scaduto o sbagliato.")
        print(response.text)

except Exception as e:
    print(f"❌ Errore di connessione: {e}")
