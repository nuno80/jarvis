# 🛠️ ZeroClaw: Manuale dei Comandi

Benvenuto nella guida rapida ai comandi di **ZeroClaw**. Questo documento raccoglie tutte le istruzioni necessarie per gestire l'infrastruttura IA locale, il servizio daemon e la risoluzione dei problemi comuni.

---

## 🚀 1. Comandi Essenziali (Core)

Questi sono i comandi principali per l'interazione quotidiana con ZeroClaw.

| Comando | Descrizione | Utilizzo Tipico |
| :--- | :--- | :--- |
| `zeroclaw doctor` | **Diagnostica di Sistema.** Verifica la salute dei componenti e la validità del `config.toml`. | Dopo ogni modifica alla configurazione. |
| `zeroclaw daemon` | **Avvio del Cuore.** Lancia il Gateway, lo Scheduler e i canali di comunicazione. | Inizializzazione del sistema in background. |
| `zeroclaw agent` | **Chat Interattiva.** Apre un'interfaccia di conversazione testuale nel terminale. | Test rapido della personalità (SOUL) e dei tool. |
| `zeroclaw onboard` | **Procedura Guidata.** Configura automaticamente Ollama e i canali (es. Telegram). | Prima installazione o aggiunta nuovi canali. |

---

## ⚙️ 2. Gestione del Servizio (Linux/WSL)

Per mantenere ZeroClaw attivo in modo persistente come servizio di sistema.

- **Installazione:** `zeroclaw service install`
- **Avvio:** `zeroclaw service start`
- **Arresto:** `zeroclaw service stop`
- **Stato:** `zeroclaw service status`

---

## 🛡️ 3. Sicurezza e Gateway (Pairing)

ZeroClaw utilizza un sistema di pairing per autorizzare dispositivi e applicazioni esterne.

### Gestione Accessi
- **Nuovo Pairing:** `zeroclaw gateway --new-pairing`
  - *Nota: Richiede l'inserimento del codice a 6 cifre nella Dashboard Web (`http://127.0.0.1:42617`).*
- **Revoca Accessi:** Utile se si sospetta una violazione della sicurezza o se si desidera resettare i token.

---

## 🕵️ 4. Risoluzione Problemi (Troubleshooting)

Se il sistema risponde con errori di porta occupata o processi zombie.

### Pulizia Processi Zombie
Se ricevi l'errore `Address already in use (os error 98)`, usa questa sequenza:

1. **Identifica il processo sulla porta 42617:**
   ```bash
   sudo ss -tulpn | grep 42617
   ```
2. **Uccidi forzatamente tutti i processi ZeroClaw:**
   ```bash
   ps aux | grep zeroclaw | grep -v grep | awk '{print $2}' | xargs -r kill --9
   ```

### Diagnostica Avanzata
- **Stato Scheduler:** Se ricevi `heartbeat stale`, riavvia il demone.
- **Validazione Config:** `zeroclaw doctor` è il tuo migliore amico per errori di sintassi TOML.

---

## 🎙️ 5. Audio Bridge (Windows Side)

Comandi per gestire l'interfaccia vocale su Windows (Hardware Level).

- **Esecuzione Bridge:**
  ```powershell
  python jarvis_audio_bridge.py
  ```
- **Wake Words supportate:** "Jarvis", "Ok Jarvis", "Ehi Jarvis".
- **Requisito .env:** Assicurati che `ZEROCLAW_SECRET` sia correttamente impostato con il token `zc_...`.

---

## 📂 6. Struttura Workspace

L'agente risiede in `~/.zeroclaw/workspace/`:
- `SOUL.md`: Definisce il carattere e le direttive.
- `AGENTS.md`: Gestisce il routing dei sub-agenti.
- `config.toml`: La configurazione tecnica (Porte, API, Autonomia).

---

> [!TIP]
> Per ottenere le massime prestazioni su hardware NVIDIA (es. RTX 5070), assicurati che Whisper sia configurato per usare `cuda` con `large-v3-turbo`.

---
*Ultimo aggiornamento: 2026-03-19*
