"""
jarvis_audio_bridge.py — Ponte Audio/Vocale per JARVIS v3.2
Pipeline ottimizzata: STT (Whisper) → Agente locale (Ollama + @tool) → TTS (Piper)
"""

import os
import sys
import re
import time
import atexit
import requests
import numpy as np
import sounddevice as sd
import threading
import queue
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
try:
    from scipy import signal as scipy_signal
except ImportError:
    scipy_signal = None
from faster_whisper import WhisperModel

# Modulo TTS locale (Piper ONNX)
sys.path.insert(0, str(Path(__file__).parent))
from tts_piper import speak, speak_sync, is_speaking

# ==========================================
# CONFIGURAZIONE (PULITA)
# ==========================================
from dotenv import load_dotenv

# 1. Carica il file .env
load_dotenv(override=True)

# 2. Assegna le variabili UNA SOLA VOLTA
SECRET = os.getenv("ZEROCLAW_SECRET")
ZEROCLAW_URL = "http://127.0.0.1:42617/webhook"

# 3. Verifica immediata
if not SECRET:
    raise RuntimeError("ZEROCLAW_SECRET non trovato nel .env!")

# Log di controllo (apparirà all'avvio)
# Se vedi "enc2:", siamo a cavallo!
print(f"[DEBUG] Token caricato: {SECRET[:15]}...")
# --- Parametri Audio ---
FS = 16000          # Sample rate Whisper (non modificare)
CHANNELS = 1
BLOCK_SIZE = 512    # ~32ms per blocco (bassa latenza)

# --- VAD (Voice Activity Detection) ---
# Energia minima per considerare un frame come "parlato"
# Valore suggerito: 0.005 in ambienti silenziosi, 0.015 in ambienti rumorosi
VAD_ENERGY_THRESHOLD = 0.008
# Quanti frame di silenzio consecutivi prima di considerare il parlato finito
# 50 frame × 32ms ≈ 1.6 secondi di silenzio
VAD_SILENCE_FRAMES = 50
# Quanti frame di parlato minimo per avviare la registrazione (evita click)
VAD_SPEECH_MIN_FRAMES = 5
# Durata massima di una singola utterance (secondi)
MAX_UTTERANCE_SECONDS = 15

# --- Whisper ---
# Con RTX 5070 (12GB VRAM, ~5GB liberi dopo Ollama), sfruttiamo i Tensor Core!
# 'large-v3-turbo' = top di gamma, ~2GB VRAM, trascrizione quasi perfetta in italiano
# Fallback: 'small' su CPU se CUDA non disponibile
WHISPER_MODEL = "large-v3-turbo"
WHISPER_DEVICE = "cuda"         # 'cpu' per fallback senza GPU
WHISPER_COMPUTE = "float16"     # 'int8' per CPU
LANGUAGE = "it"

# Prompt iniziale: contestualizza Whisper sull'italiano e sul dominio
# Questo riduce drasticamente le allucinazioni e migliora la punteggiatura
INITIAL_PROMPT = (
    "Jarvis, assistente vocale. Comandi in italiano. "
    "Luci, domotica, email, file, documenti, calendario."
)

# Wake word (almeno una deve essere nella trascrizione)
WAKE_WORDS = ["jarvis", "ok jarvis", "ehi jarvis"]

# Contatore utterance globale (per debug/monitoring)
utterance_count = 0

# ==========================================
# LOGGING
# ==========================================
from logger import get_logger
logger = get_logger("jarvis.bridge")

# ==========================================
# INIZIALIZZAZIONE WHISPER
# ==========================================
logger.info(f"Caricamento modello Whisper '{WHISPER_MODEL}' su {WHISPER_DEVICE}...")
logger.info("  (prima esecuzione: download automatico ~1.5GB)")
try:
    whisper_model = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE)
    logger.info(f"Whisper pronto su {WHISPER_DEVICE.upper()} ({WHISPER_COMPUTE}).")
except Exception as e:
    logger.warning(f"CUDA non disponibile ({e}), fallback su CPU con modello small...")
    WHISPER_MODEL = "small"
    WHISPER_DEVICE = "cpu"
    WHISPER_COMPUTE = "int8"
    whisper_model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    logger.info("Whisper pronto su CPU (fallback).")

# ==========================================
# PREPROCESSING AUDIO
# ==========================================

def preprocess_audio(audio: np.ndarray, fs: int = FS) -> np.ndarray:
    """
    Migliora la qualità audio prima della trascrizione:
    1. Normalizzazione ampiezza (porta il segnale a -3dBFS)
    2. Filtro passa-banda voce umana (300-3400 Hz)
    3. Pre-enfasi (boost delle alte frequenze, migliora chiarezza consonanti)
    """
    # 1. Normalizzazione
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.7  # Normalizza a 70% per headroom

    # 2. Filtro passa-banda voce (300-3400 Hz)
    # Elimina rumori a bassa frequenza (HVAC, vibrazioni) e alte frequenze (sibili microfono)
    try:
        if scipy_signal is not None:
            nyquist = fs / 2
            low = 300 / nyquist
            high = 3400 / nyquist
            b, a = scipy_signal.butter(4, [low, high], btype='band')
            audio = scipy_signal.filtfilt(b, a, audio)
    except Exception:
        pass  # Se scipy non disponibile o in errore, continua senza filtro

    # 3. Pre-enfasi: y[n] = x[n] - 0.97 * x[n-1]
    # Migliora la chiarezza senza distorcere
    audio = np.append(audio[0], audio[1:] - 0.97 * audio[:-1])

    return audio.astype(np.float32)


def compute_rms(audio_block: np.ndarray) -> float:
    """Calcola l'energia RMS di un blocco audio."""
    return float(np.sqrt(np.mean(audio_block.astype(np.float64) ** 2)))


# ==========================================
# TRASCRIZIONE WHISPER
# ==========================================

def transcribe(audio: np.ndarray) -> str:
    """
    Trascrive l'audio con faster-whisper.
    Restituisce il testo oppure stringa vuota.
    """
    audio = preprocess_audio(audio)

    segments, info = whisper_model.transcribe(
        audio,
        language=LANGUAGE,
        beam_size=5,
        best_of=5,
        temperature=0.0,           # Deterministico = più preciso
        condition_on_previous_text=False,  # Evita que si "trascini" errori
        initial_prompt=INITIAL_PROMPT,
        vad_filter=True,
        vad_parameters={
            "min_silence_duration_ms": 500,
            "speech_pad_ms": 400,
            "threshold": 0.4,
        },
        word_timestamps=False,
    )

    text = "".join(s.text for s in segments).strip()

    # Filtra allucinazioni comuni di Whisper (testo ripetuto o simboli)
    HALLUCINATIONS = [
        "sottotitoli a cura di", "sottotitoli e revisione a cura di",
        "grazie per l'ascolto", "fine", "[musica]", "[applausi]",
    ]
    text_lower = text.lower()
    for hall in HALLUCINATIONS:
        if hall in text_lower and len(text) < 60:
            logger.debug(f"Allucinazione filtrata: '{text}'")
            return ""

    return text


def strip_wake_word(text: str) -> str:
    """Rimuove la wake word dal testo prima di inviarlo a ZeroClaw."""
    original = text
    text_lower = text.lower()
    for ww in sorted(WAKE_WORDS, key=len, reverse=True):  # Più lunghe prima
        idx = text_lower.find(ww)
        if idx != -1:
            text = text[idx + len(ww):].strip(" ,.")
            break
    return text if text else original  # Fallback al testo originale se vuoto


# ==========================================
# INVIO ALL'AGENTE JARVIS
# ==========================================

# Import lazy dell'agente locale (evita rallentare l'avvio con import pesanti)
_jarvis_agent_loaded = False
_ask_jarvis_fn = None

def _load_agent():
    """Carica l'agente locale al primo utilizzo (lazy init)."""
    global _jarvis_agent_loaded, _ask_jarvis_fn
    if not _jarvis_agent_loaded:
        try:
            from jarvis_agent import ask_jarvis
            _ask_jarvis_fn = ask_jarvis
            logger.info("Agente locale JARVIS caricato (Ollama + tool calling)")
        except ImportError as e:
            logger.warning(f"Agente locale non disponibile: {e}. Uso solo webhook.")
            _ask_jarvis_fn = None
        _jarvis_agent_loaded = True
    return _ask_jarvis_fn


def _fallback_zeroclaw(clean_text: str) -> None:
    """Fallback: invia al webhook ZeroClaw (senza tool calling)."""
    logger.info(f"→ Fallback ZeroClaw webhook: '{clean_text}'")

    payload = {"message": clean_text, "sender": "user_local"}
    headers = {
        "Authorization": f"Bearer {SECRET}",
        "Content-Type": "application/json"
    }

    try:
        response = None
        for attempt in range(2):
            try:
                response = requests.post(ZEROCLAW_URL, json=payload, headers=headers, timeout=30)
                break
            except requests.exceptions.ConnectionError:
                if attempt == 0:
                    logger.warning("Connessione fallita, retry tra 1s...")
                    time.sleep(1)
                else:
                    raise

        if response is None:
            speak("Non riesco a connettermi.")
            return

        if response.status_code == 200:
            data = response.json()
            reply = data.get("response") or data.get("text") or str(data)
            logger.info(f"← '{reply[:100]}{'...' if len(reply) > 100 else ''}'")
            speak(reply)
        else:
            logger.warning(f"Errore ZeroClaw HTTP {response.status_code}")
            speak("Il mio cervello ha avuto un momento di incertezza.")

    except Exception as e:
        logger.error(f"Errore webhook: {e}", exc_info=True)
        speak("Errore imprevisto di rete.")


def send_to_jarvis(text: str) -> None:
    """Processa il comando vocale: agente locale (con tool) → fallback webhook."""

    # Pulisci il testo dalla wake word
    clean_text = strip_wake_word(text)
    logger.info(f"→ JARVIS: '{clean_text}'")

    # Tentativo 1: Agente locale (Ollama diretto + tool calling)
    ask_fn = _load_agent()
    if ask_fn is not None:
        try:
            reply = ask_fn(clean_text)
            if reply is not None:
                logger.info(f"← Agente locale: '{reply[:100]}{'...' if len(reply) > 100 else ''}'")
                speak(reply)
                return
            else:
                logger.warning("Agente locale ha restituito None, fallback su webhook...")
        except Exception as e:
            logger.warning(f"Errore agente locale ({e}), fallback su webhook...")

    # Tentativo 2: Fallback webhook ZeroClaw
    _fallback_zeroclaw(clean_text)

# ==========================================
# VAD REAL-TIME + LOOP DI ASCOLTO
# ==========================================

def listen_loop() -> None:
    """
    Loop principale con VAD real-time via InputStream callback.

    Stato macchina:
      IDLE     → in ascolto, nessun parlato
      SPEAKING → parlato rilevato, sto registrando
      DONE     → silenzio post-parlato, pronto per trascrizione
    """
    audio_buffer: list = []
    speech_frames = 0
    silence_frames = 0
    is_capturing = False

    # Threshold adattiva: si aggiorna ogni N frame di silenzio
    # Parte dal valore configurato e si adatta al rumore ambiente
    adaptive_threshold = VAD_ENERGY_THRESHOLD
    background_rms_samples = []

    audio_queue: queue.Queue = queue.Queue()

    def audio_callback(indata, frames, time_info, status):
        """Callback real-time: riceve blocchi audio e li mette in coda."""
        if status:
            logger.debug(f"Audio status: {status}")
        audio_queue.put(indata[:, 0].copy())  # Mono, float32

    logger.info("Jarvis in ascolto — wake word: 'Jarvis, ...'")
    logger.info(f"Threshold VAD: {VAD_ENERGY_THRESHOLD} | Silenzio max: {VAD_SILENCE_FRAMES} frame")

    with sd.InputStream(
        samplerate=FS,
        channels=CHANNELS,
        dtype="float32",
        blocksize=BLOCK_SIZE,
        callback=audio_callback,
    ):
        while True:
            try:
                block = audio_queue.get(timeout=2.0)
            except queue.Empty:
                continue
            except KeyboardInterrupt:
                raise

            # Skip feedback: se Jarvis sta parlando, svuota la coda e ignora
            if is_speaking():
                # Svuota la coda per non accumulare audio del TTS
                try:
                    while True:
                        audio_queue.get_nowait()
                except queue.Empty:
                    pass
                is_capturing = False
                audio_buffer.clear()
                speech_frames = 0
                silence_frames = 0
                continue

            rms = compute_rms(block)

            # Aggiornamento threshold adattiva (solo in silenzio)
            if not is_capturing:
                background_rms_samples.append(rms)
                if len(background_rms_samples) > 200:  # ~6 secondi
                    background_rms_samples.pop(0)
                    background_median = float(np.median(background_rms_samples))
                    # Threshold = 3× il rumore di fondo, con minimo configurato
                    adaptive_threshold = max(
                        VAD_ENERGY_THRESHOLD,
                        background_median * 3.0
                    )

            threshold = adaptive_threshold

            if rms > threshold:
                # PARLATO RILEVATO
                speech_frames += 1
                silence_frames = 0
                audio_buffer.append(block)

                if not is_capturing and speech_frames >= VAD_SPEECH_MIN_FRAMES:
                    is_capturing = True
                    logger.info(f"🎤 Parlato! (RMS={rms:.4f}, thr={threshold:.4f})")

            elif is_capturing:
                # SILENZIO DOPO PARLATO
                audio_buffer.append(block)
                silence_frames += 1

                if silence_frames >= VAD_SILENCE_FRAMES:
                    # Fine utterance: trascrivi
                    audio_data = np.concatenate(audio_buffer)
                    audio_buffer.clear()
                    speech_frames = 0
                    silence_frames = 0
                    is_capturing = False

                    # Durata minima/massima
                    duration = len(audio_data) / FS
                    if duration < 0.5:
                        logger.debug(f"Utterance troppo corta ({duration:.1f}s) — skip.")
                        continue
                    if duration > MAX_UTTERANCE_SECONDS:
                        logger.warning(f"Utterance troppo lunga ({duration:.1f}s) — tronco.")
                        audio_data = audio_data[:int(MAX_UTTERANCE_SECONDS * FS)]

                    logger.info(f"📝 Trascrizione ({duration:.1f}s di audio)...")
                    text = transcribe(audio_data)

                    if not text:
                        logger.debug("Nessun testo estratto.")
                        continue

                    global utterance_count
                    utterance_count += 1
                    logger.info(f"👤 [{utterance_count}] Trascritto: '{text}'")

                    # Filtro wake word
                    text_lower = text.lower()
                    if not any(ww in text_lower for ww in WAKE_WORDS):
                        logger.debug(f"Wake word assente — ignorato.")
                        continue

                    # Feedback sonoro immediato: l'utente sa che è stato sentito
                    speak("Ricevuto.")

                    # Invia all'agente JARVIS in background
                    threading.Thread(
                        target=send_to_jarvis,
                        args=(text,),
                        daemon=True
                    ).start()

            else:
                # Silenzio puro: reset counter parlato
                if speech_frames > 0:
                    speech_frames = 0
                    if not is_capturing:
                        audio_buffer.clear()


# ==========================================
# ENTRY POINT
# ==========================================
def _shutdown():
    """Cleanup al termine del processo."""
    logger.info(f"Shutdown completo. Utterance elaborate: {utterance_count}")

atexit.register(_shutdown)


if __name__ == "__main__":
    logger.info("=== JARVIS Audio Bridge v3.2 ===")
    logger.info(f"Modello Whisper  : {WHISPER_MODEL} ({WHISPER_DEVICE}/{WHISPER_COMPUTE})")
    logger.info(f"VAD threshold    : {VAD_ENERGY_THRESHOLD} (adattivo)")
    logger.info(f"Wake words       : {WAKE_WORDS}")
    logger.info(f"ZeroClaw URL     : {ZEROCLAW_URL}")

    try:
        speak_sync("Sistemi operativi. Sono in ascolto.")
        listen_loop()
    except KeyboardInterrupt:
        logger.info("Arresto manuale (Ctrl+C).")
    except RuntimeError as e:
        logger.critical(f"Errore configurazione: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"ERRORE FATALE: {e}", exc_info=True)
        sys.exit(1)
