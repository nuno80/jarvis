import requests
import sys

# La versione 9b ufficiale per Qwen non esiste su Ollama (spesso si confonde con gemma2:9b o qwen ha 7b/14b).
# Utilizziamo qwen2.5:7b come fallback primario per il testing, in quanto è il più bilanciato e simile.
MODEL_NAME = "qwen2.5:7b"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

def test_qwen():
    print(f"Test connessione a Ollama per il modello {MODEL_NAME}...")
    
    payload = {
        "model": MODEL_NAME,
        "prompt": "Ciao Jarvis, sei online? Rispondi in italiano in modo molto conciso.",
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        print("\n--- RISPOSTA DI JARVIS ---")
        print(result.get("response", "Nessuna risposta dal modello."))
        print("--------------------------\n")
        print("✅ Test Ollama completato con successo!")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERRORE: Impossibile connettersi a Ollama. Assicurati che il servizio Ollama sia in esecuzione (porta 11434).")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("❌ ERRORE: Timeout della richiesta. Il modello potrebbe essere in fase di caricamento o il sistema è troppo carico.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERRORE IMPREVISTO: {str(e)}")
        print(f"\nSe ottieni un errore di 'model not found', esegui prima: ollama pull {MODEL_NAME}")
        sys.exit(1)

if __name__ == "__main__":
    test_qwen()
