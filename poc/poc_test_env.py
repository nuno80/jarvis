import os
from dotenv import load_dotenv

def test_secrets():
    print("Avvio caricamento segreti...")
    # Carica il file .env
    load_dotenv()

    # Prova a leggere una variabile
    ha_url = os.getenv("HA_URL")

    if ha_url:
        print(f"[SUCCESS] File .env letto correttamente!")
        print(f"URL Home Assistant configurato: {ha_url}")
        print("I segreti sono al sicuro in memoria.")
    else:
        print("[ERROR] Impossibile trovare la variabile HA_URL. Il file .env esiste?")

if __name__ == "__main__":
    test_secrets()
