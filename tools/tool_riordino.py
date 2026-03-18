import sys
import os
import shutil
import argparse
from pathlib import Path

# Logger centralizzato JARVIS
sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger

logger = get_logger("jarvis.tool.riordino")

# ==========================================
# RESTRIZIONI TASSATIVE (Sandboxing)
# ==========================================
# Il tool DEVE operare SOLTANTO all'interno di questa lista di directory autorizzate.
ALLOWED_DIRECTORIES = [
    Path("C:/Users/Nuno/Desktop/Jarvis_Drop").resolve()
]


def is_path_allowed(target_path):
    """Verifica che il path di destinazione sia all'interno delle directory autorizzate."""
    try:
        resolved_target = Path(target_path).resolve()
        for allowed_dir in ALLOWED_DIRECTORIES:
            if resolved_target.is_relative_to(allowed_dir):
                return True
        return False
    except Exception:
        return False


def human_verification(action_desc):
    """Implementa l'Human-in-the-Loop bloccando l'esecuzione finché l'utente non approva."""
    logger.warning(f"[HUMAN-IN-THE-LOOP] Richiesta autorizzazione: {action_desc}")
    print(f"\n[⚠️ SECURITY ALERT - HUMAN IN THE LOOP]")
    print(f"Richiesta di autorizzazione per: {action_desc}")

    while True:
        scelta = input("Approvi questa operazione? (yes/no): ").strip().lower()
        if scelta in ['y', 'yes', 'si', 'sì']:
            logger.info("Operazione autorizzata dall'utente.")
            return True
        elif scelta in ['n', 'no']:
            logger.info("Operazione rifiutata dall'utente.")
            return False
        else:
            print("Risposta non valida. Digita 'yes' o 'no'.")


def riordina_directory(dir_path):
    """
    Legge una directory, categorizza i file per estensione e li sposta in sottocartelle.
    """
    dir_path = Path(dir_path).resolve()
    logger.info(f"Richiesta riordino directory: {dir_path}")

    # 1. SANDBOXING CHECK
    if not is_path_allowed(dir_path):
        msg = f"[ERRORE DI SICUREZZA] La directory '{dir_path}' NON È AUTORIZZATA. Operazione bloccata dal Sandboxing."
        logger.critical(msg)
        return msg

    if not dir_path.exists() or not dir_path.is_dir():
        msg = f"[ERRORE] Il percorso '{dir_path}' non è una directory valida o non esiste."
        logger.error(msg)
        return msg

    # Mappa estensioni → Categorie
    categorie = {
        'Immagini': ['.img', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'],
        'Documenti': ['.pdf', '.doc', '.docx', '.txt', '.csv', '.xlsx', '.md'],
        'Archivi': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'Audio': ['.wav', '.mp3', '.ogg', '.flac'],
        'Video': ['.mp4', '.avi', '.mkv', '.mov']
    }

    file_da_spostare = []

    # Scansione non ricorsiva (solo la root della directory passata)
    for f in dir_path.iterdir():
        if f.is_file():
            estensione = f.suffix.lower()
            categoria_dest = 'Altro'
            for cat, estensioni in categorie.items():
                if estensione in estensioni:
                    categoria_dest = cat
                    break

            dest_dir = dir_path / categoria_dest
            dest_file = dest_dir / f.name
            file_da_spostare.append((f, dest_dir, dest_file))

    if not file_da_spostare:
        msg = "[INFO] Nessun file trovato da riordinare nella directory specificata."
        logger.info(msg)
        return msg

    # 2. HUMAN-IN-THE-LOOP CHECK
    logger.info(f"Trovati {len(file_da_spostare)} file da riordinare in {dir_path.name}.")
    print(f"\nSono stati trovati {len(file_da_spostare)} file da riordinare in {dir_path.name}.")
    for f, dest_dir, dest_file in file_da_spostare:
        print(f"  - Moverò: {f.name} → {dest_dir.name}/")

    autorizzato = human_verification(f"Spostamento di {len(file_da_spostare)} file in {dir_path}")

    if not autorizzato:
        return "[ANNULLATO] Operazione annullata dall'utente."

    # 3. ESECUZIONE ALGORITMO DI RIORDINO
    file_spostati = 0
    try:
        for f, dest_dir, dest_file in file_da_spostare:
            dest_dir.mkdir(exist_ok=True)
            shutil.move(str(f), str(dest_file))
            logger.debug(f"Spostato: {f.name} → {dest_dir.name}/")
            file_spostati += 1

        msg = f"[SUCCESSO] Riordino completato. {file_spostati} file posizionati nelle rispettive categorie."
        logger.info(msg)
        return msg

    except Exception as e:
        msg = f"[ERRORE DURANTE IL RIORDINO] Impossibile completare l'operazione: {str(e)}"
        logger.exception(msg)
        return msg


def main():
    parser = argparse.ArgumentParser(description="Tool File System Jarvis (Riordino File con Sandboxing e HitL)")
    parser.add_argument("directory", type=str, help="Il percorso della directory da riordinare.")
    args = parser.parse_args()
    risultato = riordina_directory(args.directory)
    print(f"\n{risultato}")


if __name__ == "__main__":
    main()
