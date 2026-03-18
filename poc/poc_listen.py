import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel
import os

DURATION = 5
SAMPLE_RATE = 16000
FILENAME = "temp_audio.wav"

def record_audio():
    print(f"\n🎤 INIZIO REGISTRAZIONE ({DURATION} secondi)... Parla ora!")
    audio_data = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    sf.write(FILENAME, audio_data, SAMPLE_RATE)
    print("✅ Registrazione completata.")

def transcribe_audio():
    print("\n🧠 Caricamento modello in memoria (su CPU)...")
    model = WhisperModel("Systran/faster-distil-whisper-large-v3", device="cpu", compute_type="int8")

    print("📝 Trascrizione in corso (con VAD attivato)...")
    segments, info = model.transcribe(FILENAME, beam_size=5, language="it", vad_filter=True)

    print(f"\n🌍 Lingua rilevata: {info.language} (probabilità: {info.language_probability:.2f})")
    print("-" * 50)
    for segment in segments:
        print(f"🗣️ Testo: {segment.text}")
    print("-" * 50)

if __name__ == "__main__":
    record_audio()
    transcribe_audio()
    if os.path.exists(FILENAME):
        os.remove(FILENAME)
