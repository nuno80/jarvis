import requests
import time

URL = "http://localhost:42617/webhook"
SECRET = "jarvis_internal_secret"

def verify():
    payload = {"message": "Jarvis, che ore sono?", "sender": "user_local"}
    headers = {"X-Webhook-Secret": SECRET, "Content-Type": "application/json"}
    
    print(f"🚀 Invio richiesta a {URL}...")
    start_time = time.time()
    
    try:
        response = requests.post(URL, json=payload, headers=headers, timeout=120)
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"✅ Risposta ricevuta in {end_time - start_time:.2f} secondi:")
            print(f"📄 {response.json()}")
        else:
            print(f"❌ Errore HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Errore di connessione: {e}")

if __name__ == "__main__":
    verify()
