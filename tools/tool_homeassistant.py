import sys
import os
import argparse
import requests
from pathlib import Path

# Logger centralizzato JARVIS
sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")
logger = get_logger("jarvis.tool.homeassistant")

# ==========================================
# RESTRIZIONI ELABORAZIONE LOCALE
# ==========================================
# Il tool DEVE operare SOLTANTO su connessioni locali (es. 192.168.x.x o homeassistant.local)

def is_local_network(url):
    """Verifica di sicurezza che la chiamata sia limitata alla rete locale."""
    if not url:
        return False
    url = url.lower()
    return any(x in url for x in ["192.168.", "127.0.0.1", "localhost", ".local", "10.0."])


def home_assistant_action(entity_id, service):
    """Esegue un servizio su una determinata entità di Home Assistant."""
    current_ha_url = os.getenv("HA_URL")
    current_ha_token = os.getenv("HA_TOKEN")

    if not current_ha_url or not current_ha_token:
        msg = "[ERRORE] Le variabili HA_URL o HA_TOKEN non sono configurate nel file .env."
        logger.error(msg)
        return msg

    if not is_local_network(current_ha_url):
        msg = f"[ERRORE DI SICUREZZA] L'URL configurato ({current_ha_url}) non è locale. Operazione bloccata."
        logger.critical(msg)
        return msg

    headers = {
        "Authorization": f"Bearer {current_ha_token}",
        "content-type": "application/json",
    }

    domain = entity_id.split('.')[0]
    api_url = f"{current_ha_url.rstrip('/')}/api/services/{domain}/{service}"
    payload = {"entity_id": entity_id}

    logger.info(f"HA action: {service} su {entity_id} → {api_url}")

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=5)
        response.raise_for_status()
        msg = f"[SUCCESSO] Azione '{service}' eseguita su '{entity_id}'."
        logger.info(msg)
        return msg
    except requests.exceptions.ConnectionError:
        msg = "[ERRORE] Impossibile connettersi a Home Assistant. Verifica che sia acceso e sulla stessa rete."
        logger.error(msg)
        return msg
    except requests.exceptions.HTTPError as err:
        msg = f"[ERRORE API] Errore da Home Assistant: {err}"
        logger.error(msg)
        return msg
    except Exception as e:
        msg = f"[ERRORE IMPREVISTO] {str(e)}"
        logger.exception(msg)
        return msg


def main():
    parser = argparse.ArgumentParser(description="Tool Domotica Jarvis (Home Assistant in Locale)")
    parser.add_argument("entity_id", type=str, help="L'ID dell'entità di HA (es. light.sala, switch.tv)")
    parser.add_argument("service", type=str, help="L'azione da compiere (es. turn_on, turn_off, toggle)")
    args = parser.parse_args()
    risultato = home_assistant_action(args.entity_id, args.service)
    print(risultato)


if __name__ == "__main__":
    main()
