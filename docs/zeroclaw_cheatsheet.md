# ⚡ ZeroClaw & JARVIS: Cheat Sheet Rapido

Un riferimento rapido per te. Usa questi comandi dal terminale WSL (o Windows, ove specificato) per operare rapidamente su JARVIS senza dover rileggere le guide lunghe o interrogare sistematicamente l'LLM.

## 🛠️ Comandi di Ciclo di Vita (ZeroClaw su WSL)

| Comando | A cosa serve |
|---------|--------------|
| `zeroclaw daemon` | Avvia il cuore del sistema in background. Senza questo, i bot Telegram/Discord non rispondono e il gateway webhook (porta 42617) è spento. |
| `zeroclaw status` | Mostra se il demone è attivo, quale provider/modello stai usando, l'uso della memoria e i parametri base. |
| `zeroclaw doctor` | Lancia una diagnostica. Fondamentale per capire se c'è un errore di sintassi nel file `config.toml` o se Ollama è irraggiungibile. |
| `zeroclaw agent` | Apre la chat interattiva (Terminale) diretta con JARVIS. Ottimo per testare le API prima di lanciare i canali. |
| `jarvis-restart` | Applica le modifiche fatte a `config.toml` o `SOUL.md` riavviando rapidamente il servizio. |
| `jarvis-stop` | Spegne il demone JARVIS. |

## 🔑 Sicurezza e Autenticazione (WSL)

| Comando | A cosa serve |
|---------|--------------|
| `zeroclaw gateway --new-pairing` | Genera un nuovo token (`zc_...`). Da usare **UNA** sola volta e salvare nel `.env`. Ti serve per far comunicare gli script Python/IronMan su Windows con il demone su WSL. |
| `zeroclaw onboard` | Procedura guidata veloce per aggiornare un token Telegram o cambiare provider AI rapidamente. |
| `zeroclaw estop` | Blocca tutte le esecuzioni "Tool". Utile se l'AI impazzisce e inizia a fare operazioni bash o leggere file a raffica. |

## 💬 Gestione Canali e Chat (Telegram / Discord)

| Azione / Comando | A cosa serve |
|-----------------|--------------|
| `zeroclaw channel list` | Mostra tutti i canali configurati nel file `.toml` e il loro stato (Online/Offline). |
| `zeroclaw channel start telegram` | Forza l'avvio e l'ascolto per il solo canale Telegram. |
| **Digita:** `/new` | (Dentro la chat Telegram). Cancella la memoria a breve termine e resetta il loop per iniziare un nuovo discorso pulito. |
| **Digita:** `/model ollama qwen3.5:9b` | (Dentro la chat Telegram). Cambia modello al volo durante la sessione utente. |

## 🐍 Sviluppo e Script (Windows PowerShell)

Comandi per lanciare i moduli "Sensoriali" su Windows per accedere a Mic e GPU:

| Comando | A cosa serve |
|---------|--------------|
| `python jarvis_audio_bridge.py` | Avvia "Le orecchie e la bocca". Si mette in ascolto sul microfono Windows, usa Whisper, e invia richieste a ZeroClaw WSL. |
| `python travel_agent.py` | Lancia l'agente specializzato nei voli che hai creato con LangGraph (`zeroclaw-tools`). |
| `OLLAMA_HOST=0.0.0.0` | (Variabile di Sistema Windows). Vitale. Obbliga Ollama ad accettare connessioni da macchine virtuali, assicurando che WSL lo "veda". |

## 📁 Posizioni Chiave dei File (Il "Cervello")

Dove si trovano i file che contano:

1. **Il Comportamento**: `~/.zeroclaw/workspace/SOUL.md` (Qui vive l'anima e il prompt di sistema di JARVIS).
2. **Le Regole del Gioco**: `~/.zeroclaw/config.toml` (Provider, livelli di Sicurezza CLI, porte Gateway).
3. **Le Password Locali**: `c:\Users\nuno8\Documents\JARVIS\jarvis\.env` (Le app-passwords di Gmail/Yahoo e i Token `zc_...`).
4. **Le Tue Modifiche ai Tool**: `~/.zeroclaw/workspace/` (Metti qui file Python da eseguire come Skill).
