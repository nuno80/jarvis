---
name: email-reader
description: Leggi le email da account Gmail o Yahoo configurati nel file .env via IMAP.
---

# Email Reader Tool

Usa questo tool quando l'utente ti chiede di controllare la posta in arrivo, leggere l'ultima email, o verificare messaggi da parte di qualcuno.
Il backend interroga i provider IMAP in modo locale e ti ritorna solo il testo utile decodificato.

## Quando usarlo

- L'utente dice: "ZeroClaw controllami le email", "Leggi la posta da Gmail", "Ci sono nuovi messaggi su Yahoo?"
- Ti viene chiesto di recuperare codici OTP, newsletter ricevute ultimamente o appunti di posta.

## Come usarlo

Invoca lo script python sottostante usando il tool primario `shell`:

```bash
# Leggi le ultime 3 email dalla inbox principale di Gmail
python3 ~/.zeroclaw/workspace/email_reader.py --provider gmail --limit 3

# Leggi tutte (fino a 5) le email NON LETTE su Yahoo
python3 ~/.zeroclaw/workspace/email_reader.py --provider yahoo --unread

# Cerca in una cartella personalizzata (es. Spam di Google)
python3 ~/.zeroclaw/workspace/email_reader.py --provider gmail --folder "[Gmail]/Spam"
```

## Opzioni (CLI Args)

| Flag            | Info                             | Default    |
|-----------------|----------------------------------|------------|
| `--provider X`  | Obbligatorio. `gmail` o `yahoo`  | (Nessuno)  |
| `--limit N`     | Quante email estrarre (da recenti) | 5        |
| `--unread`      | Leggi solo i messaggi Non Letti  | Falso      |
| `--folder X`    | Quale cartella IMAP interrogare  | INBOX      |

## Note Importanti

1. Se ricevi l'errore `Credenziali... non trovate in .env`, devi dire all'Utente: *"Non riesco ad accedere perché nel file `.env` di JARVIS mancano le password! Assicurati di impostare `GMAIL_USER` e `GMAIL_PASS` (o YAHOO). Ricorda di usare le 'App Passwords' a 16 cifre fornite dalla sicurezza Google/Yahoo e non le password dirette dell'account!"*
2. Ogni body testuale stampato dal tool è limitato a 1000 caratteri per evitare di sovraccaricare il contesto di conversazione. Leggi solo l'essenziale per riassumere all'utente la posta in arrivo.
