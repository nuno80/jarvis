import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel
import ollama
import pyttsx3
import os

# ==========================================
# CONFIGURAZIONI SISTEMA
# ==========================================
# Audio IN
DURATION = 5
SAMPLE_RATE = 16000
FILENAME = "temp_audio.wav"
WHISPER_MODEL = "Systran/faster-distil-whisper-large-v3" # Modello Whisper su CPU

# LLM Locale
OLLAMA_MODEL = "qwen3.5:9b" # Il tuo modello Qwen

# ==========================================
# INIZIALIZZAZIONE (Si fa una volta sola)
# ==========================================
print("\n[INIT] Inizializzazione sistemi in corso... Attendi.")

print("1/3 Caricamento modulo vocale (SAPI5/Pyttsx3)...")
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 170) # Velocità di crociera

print("2/3 Caricamento modulo uditivo (Whisper su CPU)...")
whisper_model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")

print(f"3/3 Connessione neurale e riscaldamento ({OLLAMA_MODEL})... ci vorrà un attimo...")
# Chiamata a vuoto per caricare i 9GB di Qwen nella RAM prima di iniziare
ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": "test"}])

print("\n✅ TUTTI I SISTEMI SONO OPERATIVI.\n")
print("-" * 50)

# ==========================================
# FUNZIONI CORE
# ==========================================
def ascolta():
    """Registra l'audio e lo converte in testo."""
    print(f"\n🎤 Jarvis in ascolto ({DURATION}s)... Parla ora!")
    audio_data = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    sf.write(FILENAME, audio_data, SAMPLE_RATE)

    print("📝 Trascrizione in corso...")
    segments, _ = whisper_model.transcribe(FILENAME, beam_size=5, language="it", vad_filter=True)
    testo = " ".join([segment.text for segment in segments]).strip()

    if os.path.exists(FILENAME):
        os.remove(FILENAME)

    return testo

def pensa(testo_utente):
    """Invia la richiesta al LLM locale."""
    print("🧠 Elaborazione...")
    messaggi = [
        {"role": "system", "content": "Sei Jarvis, un assistente IA sarcastico ma utile. Rispondi in italiano. Sii estremamente conciso, massimo 2 frasi."},
        {"role": "user", "content": testo_utente}
    ]
    risposta = ollama.chat(model=OLLAMA_MODEL, messages=messaggi)
    return risposta['message']['content']

def parla(testo):
    """Legge il testo ad alta voce."""
    print(f"🗣️ JARVIS: {testo}")
    tts_engine.say(testo)
    tts_engine.runAndWait()

# ==========================================
# MAIN LOOP (CICLO VITALE)
# ==========================================
if __name__ == "__main__":
    parla("Sistemi online. Sono pronto agli ordini.")

    while True:
        try:
            # 1. ASCOLTA
            comando = ascolta()

            if not comando: # Se il VAD taglia il silenzio e non c'è testo
                continue

            print(f"👤 TU: {comando}")

            # Comando di emergenza per uscire dal ciclo
            if "spegniti" in comando.lower() or "addio" in comando.lower():
                parla("Disattivazione protocolli in corso. Arrivederci signore.")
                break

            # 2. PENSA
            risposta = pensa(comando)

            # 3. PARLA
            parla(risposta)

        except KeyboardInterrupt:
            # Permette di chiudere premendo Ctrl+C
            print("\n[!] Interruzione manuale rilevata. Chiusura.")
            break
        except Exception as e:
            print(f"\n❌ Errore nel ciclo: {e}")
