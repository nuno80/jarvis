import os
import subprocess
from pathlib import Path

def test_sandbox_security():
    tool_path = os.path.join(os.path.dirname(__file__), "..", "tools", "tool_riordino.py")
    
    # Cartella NON autorizzata (Documenti)
    forbidden_path = str(Path.home() / "Documents")
    
    print("\n--- TEST: SICUREZZA SANDBOXING ---")
    print(f"Tentativo di riordino nella cartella non autorizzata: {forbidden_path}")
    
    result = subprocess.run(["python", tool_path, forbidden_path], capture_output=True, text=True)
    
    # Mi aspetto che il sandboxing blocchi l'esecuzione senza chiedere conferma
    if "[ERRORE DI SICUREZZA]" in result.stdout:
        print("✅ Sandboxing funzionante. Operazione bloccata con successo.")
        print(f"Log ricevuto: {result.stdout.strip()}")
    else:
        print("❌ FALLIMENTO SANDBOXING! Il tool ha bypassato la sicurezza.")
        print(f"Output: {result.stdout}")

if __name__ == "__main__":
    test_sandbox_security()
