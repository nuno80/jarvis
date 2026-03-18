"""
tool_email.py — Tool di invio email per JARVIS
Supporta Yahoo (SMTP) e Gmail (SMTP con App Password).

Sicurezza:
  - Legge credenziali dal .env (mai hardcoded)
  - Whitelist destinatari autorizzati (EMAIL_WHITELIST nel .env)
  - Human-in-the-Loop obbligatorio prima di ogni invio
  - Nessuna connessione a server esterni non SMTP autorizzati

Argomenti CLI:
  --to       Indirizzo email destinatario
  --subject  Oggetto del messaggio
  --body     Corpo del messaggio
  --account  (opzionale) 'yahoo' o 'gmail' (default: yahoo)
"""

import sys
import os
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# Logger e env centralizzati
sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")
logger = get_logger("jarvis.tool.email")

# ==========================================
# CONFIGURAZIONE SMTP
# ==========================================
SMTP_CONFIG = {
    "yahoo": {
        "host": "smtp.mail.yahoo.com",
        "port": 587,
        "user_env": "YAHOO_EMAIL",
        "pass_env": "YAHOO_APP_PASSWORD",
    },
    "gmail": {
        "host": "smtp.gmail.com",
        "port": 587,
        "user_env": "GMAIL_EMAIL",
        "pass_env": "GMAIL_APP_PASSWORD",
    },
}


def get_whitelist() -> list[str]:
    """Legge la whitelist dei destinatari autorizzati dal .env."""
    raw = os.getenv("EMAIL_WHITELIST", "")
    return [addr.strip().lower() for addr in raw.split(",") if addr.strip()]


def is_recipient_allowed(to_address: str) -> bool:
    """Verifica che il destinatario sia nella whitelist."""
    whitelist = get_whitelist()
    if not whitelist:
        logger.warning("EMAIL_WHITELIST vuota — nessun destinatario autorizzato!")
        return False
    return to_address.strip().lower() in whitelist


def human_verification(to: str, subject: str, body: str) -> bool:
    """Mostra anteprima email e chiede conferma esplicita prima dell'invio."""
    logger.warning(f"[HUMAN-IN-THE-LOOP] Richiesta invio email a: {to}")
    print("\n" + "=" * 50)
    print("⚠️  CONFERMA INVIO EMAIL — HUMAN IN THE LOOP")
    print("=" * 50)
    print(f"  A:        {to}")
    print(f"  Oggetto:  {subject}")
    print(f"  Corpo:\n{body}")
    print("=" * 50)

    while True:
        scelta = input("Inviare questa email? (yes/no): ").strip().lower()
        if scelta in ['y', 'yes', 'si', 'sì']:
            logger.info("Invio email autorizzato dall'utente.")
            return True
        elif scelta in ['n', 'no']:
            logger.info("Invio email rifiutato dall'utente.")
            return False
        else:
            print("Risposta non valida. Digita 'yes' o 'no'.")


def send_email(to: str, subject: str, body: str, account: str = "yahoo") -> str:
    """Invia un'email tramite SMTP dopo verifica whitelist e conferma utente."""

    # 1. Validazione account
    if account not in SMTP_CONFIG:
        msg = f"[ERRORE] Account non supportato: '{account}'. Usa 'yahoo' o 'gmail'."
        logger.error(msg)
        return msg

    config = SMTP_CONFIG[account]
    user = os.getenv(config["user_env"])
    password = os.getenv(config["pass_env"])

    if not user or not password:
        msg = f"[ERRORE] Credenziali {account.upper()} non configurate nel .env ({config['user_env']}, {config['pass_env']})."
        logger.error(msg)
        return msg

    # 2. Whitelist check
    if not is_recipient_allowed(to):
        whitelist = get_whitelist()
        msg = (
            f"[ERRORE DI SICUREZZA] Destinatario '{to}' non è nella whitelist autorizzata.\n"
            f"Destinatari consentiti: {', '.join(whitelist) if whitelist else 'NESSUNO'}"
        )
        logger.critical(msg)
        return msg

    # 3. Human-in-the-Loop
    if not human_verification(to, subject, body):
        return "[ANNULLATO] Invio email annullato dall'utente."

    # 4. Invio SMTP
    logger.info(f"Invio email a {to} via {account.upper()} ({config['host']}:{config['port']})")

    try:
        msg_obj = MIMEMultipart()
        msg_obj["From"] = user
        msg_obj["To"] = to
        msg_obj["Subject"] = subject
        msg_obj.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(config["host"], config["port"], timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(user, password)
            server.sendmail(user, to, msg_obj.as_string())

        msg = f"[SUCCESSO] Email inviata a '{to}' con oggetto '{subject}'."
        logger.info(msg)
        return msg

    except smtplib.SMTPAuthenticationError:
        msg = f"[ERRORE AUTH] Credenziali {account.upper()} non valide. Verifica App Password nel .env."
        logger.error(msg)
        return msg
    except smtplib.SMTPException as e:
        msg = f"[ERRORE SMTP] {str(e)}"
        logger.error(msg)
        return msg
    except Exception as e:
        msg = f"[ERRORE IMPREVISTO] {str(e)}"
        logger.exception(msg)
        return msg


def main():
    parser = argparse.ArgumentParser(
        description="Tool Email Jarvis — Invio SMTP con whitelist e Human-in-the-Loop"
    )
    parser.add_argument("--to", required=True, help="Indirizzo email destinatario")
    parser.add_argument("--subject", required=True, help="Oggetto del messaggio")
    parser.add_argument("--body", required=True, help="Corpo del messaggio")
    parser.add_argument(
        "--account",
        default="yahoo",
        choices=["yahoo", "gmail"],
        help="Account mittente (default: yahoo)"
    )

    args = parser.parse_args()
    risultato = send_email(args.to, args.subject, args.body, args.account)
    print(f"\n{risultato}")


if __name__ == "__main__":
    main()
