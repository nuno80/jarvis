import argparse
import imaplib
import email
from email.header import decode_header
import json
import os
import sys

try:
    from dotenv import load_dotenv
    # Il file .env solitamente si trova nella root jarvis/ (due livelli sopra rispetto a email_reader.py)
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        load_dotenv()
except ImportError:
    pass

def decode_str(s):
    if not s:
        return ""
    try:
        if isinstance(s, bytes):
            return s.decode("utf-8", errors="ignore")
        decoded_list = decode_header(s)
        final_str = ""
        for decoded_bytes, charset in decoded_list:
            if isinstance(decoded_bytes, bytes):
                final_str += decoded_bytes.decode(charset if charset else "utf-8", errors="ignore")
            else:
                final_str += str(decoded_bytes)
        return final_str
    except:
        return str(s)

def fetch_emails(provider, folder="INBOX", limit=5, unread=False):
    if provider == "gmail":
        host = "imap.gmail.com"
        user = os.environ.get("GMAIL_USER")
        password = os.environ.get("GMAIL_PASS")
    elif provider == "yahoo":
        host = "imap.mail.yahoo.com"
        user = os.environ.get("YAHOO_USER")
        password = os.environ.get("YAHOO_PASS")
    else:
        raise ValueError("Provider must be 'gmail' or 'yahoo'")

    if not user or not password:
        raise ValueError(f"Credenziali per {provider} non trovate in .env (Richiesti: {provider.upper()}_USER e {provider.upper()}_PASS)")

    # Accesso IMAP
    mail = imaplib.IMAP4_SSL(host)
    mail.login(user, password)
    
    # Selezione Cartella
    status, messages = mail.select('"' + folder + '"')
    if status != 'OK':
        raise ValueError(f"Cartella IMAP '{folder}' non trovata o inaccessibile.")

    # Ricerca
    search_str = "UNSEEN" if unread else "ALL"
    status, messages = mail.search(None, search_str)
    
    if status != "OK":
        return []

    mail_ids = messages[0].split()
    if not mail_ids:
        return []
    
    # Prendi solo ultime 'limit' per non scoppiare la memoria dell'IA
    mail_ids = mail_ids[-limit:]
    results = []

    for num in reversed(mail_ids):
        res, msg_data = mail.fetch(num, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                
                subject = decode_str(msg.get("Subject"))
                from_ = decode_str(msg.get("From"))
                date_ = msg.get("Date")

                body = ""
                # Parse multipart
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        
                        # Prendi solo il plain text pulito (no HTML o allegati se possibile)
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            try:
                                body = part.get_payload(decode=True).decode(errors="ignore")
                                break # Trovato body testuale, esci dal loop
                            except:
                                pass
                else:
                    try:
                        body = msg.get_payload(decode=True).decode(errors="ignore")
                    except:
                        pass
                
                # Truncate to save tokens (1000 characters per body max)
                body_snippet = body[:1000] + ("\n[...] Truncato" if len(body) > 1000 else "")
                results.append({"From": from_, "Date": str(date_), "Subject": subject, "Body": body_snippet})
    
    mail.logout()
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["gmail", "yahoo"], required=True, help="Specifica il provider (gmail o yahoo)")
    parser.add_argument("--folder", default="INBOX", help="Cartella IMAP da spulciare")
    parser.add_argument("--limit", type=int, default=5, help="Numero max di messaggi da tornare")
    parser.add_argument("--unread", action="store_true", help="Cerca solo le mail NON lette")
    args = parser.parse_args()

    try:
        emails = fetch_emails(args.provider, args.folder, args.limit, args.unread)
        if not emails:
            print("Nessuna email trovata in questa cartella.")
        else:
            print(f"Ho trovato {len(emails)} email:\n")
            for i, e in enumerate(emails, 1):
                print(f"### EMAIL {i}")
                print(f"**Da:** {e['From']}")
                print(f"**Data:** {e['Date']}")
                print(f"**Oggetto:** {e['Subject']}\n")
                print(f"{e['Body']}\n-----------------------------------\n")
    except Exception as ex:
        print(f"Errore durante la connessione/lettura: {ex}", file=sys.stderr)
