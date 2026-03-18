import os
import subprocess

def test_ha_tool():
    tool_path = os.path.join(os.path.dirname(__file__), "..", "tools", "tool_homeassistant.py")
    
    # 1. Testiamo con parametri Dummy (dovrebbe fallire per mancanza di Token, o per rete LAN simulata nel mock di requests)
    # Per il nostro test di sicurezza locale in A/B, basterà vedere se parte l'esecuzione.
    
    print("\n--- TEST SUB-AGENTE: DOMOTICA (Sicurezza e Parametri) ---")
    
    # Creiamo un env fittizio per testare il blocco Cloud
    os.environ["HA_URL"] = "http://homeassistant.local:8123"
    os.environ["HA_TOKEN"] = "token_locale_fittizio"
    
    print("Tentativo 1: Chiamata con URL Locale (homeassistant.local)")
    result1 = subprocess.run(["python", tool_path, "light.salotto", "turn_on", "--test-url", "http://homeassistant.local:8123"], capture_output=True, text=True)
    print("Output:\n" + result1.stdout.strip())
    
    print("\nTentativo 2: Chiamata con URL Esterno (violazione Cloud)")
    result2 = subprocess.run(["python", tool_path, "light.salotto", "turn_on", "--test-url", "https://nabucasa.com/auth"], capture_output=True, text=True)
    
    if "[ERRORE DI SICUREZZA]" in result2.stdout:
        print("✅ Blocco sicurezza cloud funzionante!")
        print(f"Log: {result2.stdout.strip()}")
    else:
        print("❌ FALLIMENTO: Il tool non ha bloccato la chiamata esterna.")
        print(result2.stdout)

if __name__ == "__main__":
    test_ha_tool()
