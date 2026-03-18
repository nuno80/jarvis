import ollama
import time

# Inserisci qui il nome esatto del modello che hai scaricato su Ollama
# (es. "llama3.2", "qwen2.5", "mistral")
MODELLO = "qwen3.5:9b"

def test_brain():
    print(f"🧠 Tentativo di connessione a Ollama (Modello: {MODELLO})...")

    messaggi = [
        {"role": "system", "content": "Sei Jarvis, un assistente IA sarcastico ma efficiente. Rispondi in italiano con una sola frase breve."},
        {"role": "user", "content": "Jarvis, sei online? Qual è il tuo stato?"}
    ]

    # Inizializza il client con l'IP locale esplicito per evitare problemi di risoluzione di localhost
    client = ollama.Client(host='http://127.0.0.1:11434')

    start_time = time.time()
    try:
        # Chiamata con timeout esplicito di 60 secondi
        print("⏳ In attesa di risposta (può richiedere tempo)...")
        risposta = client.chat(
            model=MODELLO, 
            messages=messaggi
        )
        end_time = time.time()

        print("\n" + "="*50)
        print(f"🗣️ JARVIS: {risposta['message']['content']}")
        print(f"⏱️ Tempo impiegato: {end_time - start_time:.2f} secondi")
        print("="*50)
        print("\n✅ Connessione neurale stabilita con successo.")

    except Exception as e:
        print(f"\n❌ Errore critico: {e}")
        print("💡 Suggerimento: Ollama è avviato? La porta 11434 è aperta su 127.0.0.1?")

if __name__ == "__main__":
    test_brain()
