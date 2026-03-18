# 📖 ZEROCLAW REFERENCE & ARCHITETTURA PROGETTO JARVIS

**Core Engine:** Rust / 100% Locale (<5MB RAM, Cold Start <10ms)
**Orchestrazione:** Ollama (Qwen 9B). Assicurati di settare il config di zeroclaw inserendo :
```toml
default_provider = "ollama"
default_model = "qwen3.5:9b"
api_url = "http://172.20.80.1:11434"
```

## 1. Architettura del Sistema (WSL2 + Windows)
ZeroClaw è un'infrastruttura a tre livelli:
* **Ollama (Cervello):** Gira su Windows per sfruttare la GPU (RTX 5070).
* **ZeroClaw Daemon (Cuore):** Gestisce memoria, scheduler e gateway all'interno di WSL.
* **ZeroClaw Agent (Azione):** L'interfaccia CLI/Bridge Audio per interagire con l'IA.

### Workspace (I File dell'Anima)
L'agente risiede in `.zeroclaw/workspace/`:
* `config.toml`: Routing LLM, porte, API keys e dichiarazione Tool/Sub-Agenti.
* `SOUL.md`: Il prompt di sistema principale (Personalità e direttive di Jarvis).
* `AGENTS.md`: Routing dei sub-agenti e spiegazione semantica dei tool.

## 2. Configurazione Ollama (Modello Locale)
Per far comunicare ZeroClaw (WSL) con Ollama (Windows):
1. **Verifica connessione:** `curl http://localhost:11434`
2. **Accesso Esterno:** Se non risponde da WSL, imposta `OLLAMA_HOST=0.0.0.0` nelle variabili d'ambiente di Windows per permettere connessioni da WSL.
3. **Modello:** Assicurati di aver scaricato il modello: `ollama pull qwen3.5:9b`.

## 3. Gestione Gateway e Pairing
ZeroClaw SOLO PER LA SUA PRIMA ESECUZIONE richiede autorizzazione per sicurezza:
1. **Generare Codice:** `zeroclaw gateway --new-pairing` (uccidere eventuali demoni attivi prima).
2. **Dashboard Web:** Accedi a `http://127.0.0.1:42617` e inserisci il codice a 6 cifre fornito dal terminale.
3. Quando devi rifare il pairing?
  Dovrai usare di nuovo il comando --new-pairing solo se:
  * Cambi browser o dispositivo e vuoi aggiungerne uno nuovo.
  * Cancelli manualmente la cartella della configurazione (~/.zeroclaw).
  * Sospetti una violazione della sicurezza e vuoi revocare l'accesso a tutti i dispositivi precedentemente collegati.

## 4. Memoria e Dati
* **Ricerca Ibrida:** SQLite con Vettoriale + FTS5.
* **Breve termine:** Rolling Summary (max 500 token).
* **Lungo termine:** Query vettoriali silenti sul database locale.

## 5. Gestione Servizio e Daemons (Troubleshooting)
### Comandi di Servizio
`zeroclaw service install / start / stop / status`

### Risoluzione Errori Comuni
* **Errore: Address already in use (os error 98):** Un processo zombie tiene occupata la porta 42617.
  * *Identifica:* `sudo ss -tulpn | grep 42617`
  * *Pulisci:* `ps aux | grep zeroclaw | grep -v grep | awk '{print $2}' | xargs -r kill --9`
* **Errore: heartbeat stale / scheduler unhealthy:** Il `zeroclaw daemon` non è attivo o non risponde. Esegui `zeroclaw doctor` per diagnosi.

## 6. Sicurezza (Sandboxing Critico)
ZeroClaw eredita i permessi dell'utente. È **tassativo**:
1. Configurare `allowed_commands` in `config.toml` (es. `["python.exe", "git"]`).
2. Limitare il File Manager a directory specifiche (es. `C:\Users\Nome\Desktop\Jarvis_Drop`).
3. Mantenere l'Human-in-the-Loop per azioni critiche.

## 7. Comandi Operativi Rapidi
| Azione | Comando |
| :--- | :--- |
| Check salute | `zeroclaw doctor` |
| Avvio Demone | `zeroclaw daemon` |
| Chat Interattiva | `zeroclaw agent` |
| Comando Diretto | `zeroclaw agent -m "fai X..."` |
| Onboarding | `zeroclaw onboard` |

## 8. Test di Verifica (Turing Test)
Chiedi a Jarvis: *"Crea un file test.py, scrivi uno script che analizzi il sistema e lo spazio disco, eseguilo e dimmi il risultato."*
Se Jarvis risponde con la sua personalità tipica (es. sarcasmo), l'integrazione Memoria + Shel  l è operativa.

## reference link:
https://www.zeroclawlabs.ai/docs

---
