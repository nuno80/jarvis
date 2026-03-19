"""
test_tts.py — Test del modulo TTS Piper per JARVIS.
Verifica che il modello it_IT-paola-medium.onnx sia correttamente caricato
e che il sistema audio produca output vocale.
"""

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

from tts_piper import speak_sync, is_speaking

def test_tts_basic():
    print("\n=== Test 1: Riproduzione sincrona ===")
    speak_sync("Test del sistema vocale. Il modello Piper è operativo.")
    assert not is_speaking(), "Il TTS dovrebbe essere fermo dopo speak_sync"
    print("✅ Test 1 superato.\n")

def test_tts_async():
    import time
    from tts_piper import speak, is_speaking, wait_done
    print("=== Test 2: Riproduzione asincrona ===")
    speak("Questo è un test asincrono. Il listener non viene bloccato durante il parlato.")
    # Breve attesa per assicurarsi che il thread parta
    time.sleep(0.1)
    print(f"  is_speaking() durante TTS: {is_speaking()}")
    wait_done()
    assert not is_speaking(), "Il TTS dovrebbe essere fermo dopo wait_done"
    print("✅ Test 2 superato.\n")

def test_tts_empty():
    print("=== Test 3: Testo vuoto (non deve crashare) ===")
    speak_sync("")
    speak_sync("   ")
    print("✅ Test 3 superato.\n")

if __name__ == "__main__":
    try:
        test_tts_basic()
        test_tts_async()
        test_tts_empty()
        print("🎉 Tutti i test TTS superati!")
    except FileNotFoundError as e:
        print(f"\n❌ MODELLO NON TROVATO: {e}")
        print("  Assicurati che 'it_IT-paola-medium.onnx' sia nella root del progetto.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test fallito: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)
