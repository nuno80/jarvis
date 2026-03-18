"""
tts_piper.py — Modulo TTS per JARVIS basato su Piper ONNX
Usa il modello it_IT-paola-medium.onnx presente nella root del progetto.

Interfaccia pubblica:
    speak(text)         → Non bloccante: genera audio in thread separato
    speak_sync(text)    → Bloccante: usa in contesti non-thread
    is_speaking()       → True se TTS attivo
    wait_done()         → Attende fine del parlato corrente
"""
import re
import os
import io
import wave
import struct
import threading
import json
from pathlib import Path

from logger import get_logger
logger = get_logger("jarvis.tts")

# ==========================================
# CONFIGURAZIONE PERCORSI (relativi alla root del progetto)
# ==========================================
_SCRIPT_DIR = Path(__file__).parent
MODEL_PATH = _SCRIPT_DIR / "it_IT-paola-medium.onnx"
MODEL_CONFIG = _SCRIPT_DIR / "it_IT-paola-medium.onnx.json"

# ==========================================
# STATO INTERNO
# ==========================================
_speaking_event = threading.Event()   # SET  = Jarvis sta parlando
_tts_lock = threading.Lock()           # Previene sovrapposizioni TTS
_engine = None


def _init_engine():
    """Inizializza il motore Piper ONNX (lazy, una volta sola)."""
    global _engine
    if _engine is not None:
        return _engine

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Modello Piper non trovato: {MODEL_PATH}\n"
            f"Assicurati che it_IT-paola-medium.onnx sia nella root del progetto."
        )

    logger.info(f"Caricamento modello Piper: {MODEL_PATH.name}")

    try:
        # Usiamo piper-tts installabile con: pip install piper-tts
        from piper import PiperVoice
        _engine = PiperVoice.load(str(MODEL_PATH), config_path=str(MODEL_CONFIG))
        logger.info("Modello Piper caricato con successo (piper-tts).")
    except ImportError:
        # Fallback: subprocess con il binario piper (scaricato separatamente)
        logger.warning("piper-tts non installato, uso subprocess fallback.")
        _engine = "subprocess"

    return _engine


def _synthesize_subprocess(text: str) -> None:
    """Fallback: usa il binario piper via subprocess + sounddevice."""
    import subprocess
    import sounddevice as sd
    import numpy as np

    piper_bin = Path(_SCRIPT_DIR) / "piper" / "piper.exe"
    if not piper_bin.exists():
        piper_bin = "piper"  # Tenta dal PATH

    cmd = [
        str(piper_bin),
        "--model", str(MODEL_PATH),
        "--config", str(MODEL_CONFIG),
        "--output-raw",
    ]

    try:
        proc = subprocess.run(
            cmd,
            input=text.encode("utf-8"),
            capture_output=True,
            timeout=30
        )
        if proc.returncode != 0:
            logger.error(f"Piper subprocess error: {proc.stderr.decode()}")
            return

        # Audio raw: PCM 16-bit, 22050 Hz mono (default Piper)
        raw = proc.stdout
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        sd.play(samples, samplerate=22050)
        sd.wait()
    except Exception as e:
        logger.error(f"Errore TTS subprocess: {e}")


def _synthesize_piper(text: str, engine) -> None:
    """Usa piper-tts Python API per generare e riprodurre audio."""
    try:
        import sounddevice as sd
        import numpy as np

        # Genera audio in memoria
        audio_buffer = io.BytesIO()
        with wave.open(audio_buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)   # 16-bit
            wav_file.setframerate(engine.config.sample_rate)
            engine.synthesize_wav(text, wav_file)

        # Leggi e riproduci
        audio_buffer.seek(44)  # Salta header WAV
        raw = audio_buffer.read()
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        sd.play(samples, samplerate=engine.config.sample_rate)
        sd.wait()
    except Exception as e:
        logger.error(f"Errore TTS piper-tts: {e}")


def _tts_worker(text: str) -> None:
    """Eseguito in thread separato. Gestisce il ciclo vita del parlato."""
    with _tts_lock:
        _speaking_event.set()
        logger.info(f"TTS → {text[:60]}{'...' if len(text) > 60 else ''}")
        try:
            engine = _init_engine()
            if engine == "subprocess":
                _synthesize_subprocess(text)
            else:
                _synthesize_piper(text, engine)
        except Exception as e:
            logger.error(f"Errore critico TTS: {e}")
        finally:
            _speaking_event.clear()


def _clean_text_for_tts(text: str) -> str:
    """Rimuove markdown, emoji e simboli incomprensibili per Piper TTS."""
    if not text:
        return ""

    # Rimuovi bold/italic markdown (**testo**, *testo*, __testo__)
    text = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', text)

    # Rimuovi header (### Testo)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)

    # Rimuovi link markdown [testo](url) -> testo
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # Rimuovi url "nudi" (http://...)
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 'link', text)

    # Rimuovi emoji base (spesso vengono pronunciate a sproposito o lette come codici)
    text = re.sub(r'[^\w\s,.:;!?\'"-àèéìòù]', ' ', text)

    # Pulisci spazi extra residui
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def speak(text: str) -> None:
    """
    Avvia il TTS in un thread separato (non bloccante).
    Il chiamante può continuare senza aspettare.
    """
    if not text or not text.strip():
        return
    text = _clean_text_for_tts(text)
    if not text:
        return
    t = threading.Thread(target=_tts_worker, args=(text,), daemon=True)
    t.start()


def speak_sync(text: str) -> None:
    """
    Avvia il TTS e ATTENDE che finisca (bloccante).
    Usare per messaggi di avvio/shutdown.
    """
    if not text or not text.strip():
        return
    text = _clean_text_for_tts(text)
    if not text:
        return
    _tts_worker(text)


def is_speaking() -> bool:
    """Restituisce True se Jarvis sta producendo audio in questo momento."""
    return _speaking_event.is_set()


def wait_done() -> None:
    """Attende che il parlato corrente finisca."""
    _speaking_event.wait()
    # Attende che l'evento venga CLEARED (= fine parlato)
    while is_speaking():
        threading.Event().wait(0.05)


# ==========================================
# TEST RAPIDO (python tts_piper.py)
# ==========================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    print("Test Piper TTS — Inizializzazione...")
    try:
        speak_sync("Sistemi vocali Piper operativi. Sono pronto agli ordini, signore.")
        print("✅ Test TTS completato con successo.")
    except FileNotFoundError as e:
        print(f"❌ Errore: {e}")
    except Exception as e:
        print(f"❌ Errore inatteso: {e}")
        import traceback; traceback.print_exc()
