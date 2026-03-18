import pyttsx3

def speak_windows_native(text):
    print(f"\n🗣️ Jarvis sta parlando (motore nativo offline): '{text}'")

    # Inizializza il motore TTS nativo di Windows
    engine = pyttsx3.init()

    # Imposta la velocità (rate) - 170 è un buon ritmo naturale
    engine.setProperty('rate', 170)

    # Esegue la sintesi e la riproduce istantaneamente sulle casse
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    try:
        test_phrase = "Buongiorno signore. I sistemi di comunicazione sono online e funzionanti."
        speak_windows_native(test_phrase)
        print("\n✅ Test vocale concluso con successo.")
    except Exception as e:
        print(f"\n❌ Errore: {e}")
