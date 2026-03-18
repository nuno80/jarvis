import tomli
from pathlib import Path

def test_config_syntax():
    workspace_path = Path(__file__).parent.parent / ".zeroclaw" / "workspace"
    config_file = workspace_path / "config.toml"
    
    print(f"Test di validazione syntax TOML per: {config_file}")
    
    if not config_file.exists():
        print(f"❌ ERRORE: Il file {config_file} non esiste!")
        return
        
    try:
        with open(config_file, "rb") as f:
            config_data = tomli.load(f)
            
        print("✅ Sintassi TOML valida!")
        print("Parametri principali trovati:")
        print(f" - Modello: {config_data.get('llm', {}).get('model')}")
        print(f" - Memoria type: {config_data.get('memory', {}).get('type')}")
        print(f" - Sandboxing directories: {config_data.get('security', {}).get('allowed_directories')}")
        print(f" - Human in the loop: {config_data.get('security', {}).get('human_in_the_loop')}")
        print(f" - Numero Tools registrati: {len(config_data.get('tools', []))}")
        print("\nPronto per l'esecuzione del demone ZeroClaw.")
        
    except tomli.TOMLDecodeError as e:
        print(f"❌ ERRORE: Errore di sintassi nel file TOML:\n{e}")
    except Exception as e:
        print(f"❌ ERRORE IMPREVISTO: {e}")

if __name__ == "__main__":
    test_config_syntax()
