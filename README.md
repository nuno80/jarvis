# 🦀 Manuale Definitivo ZeroClaw: Da Zero a Jarvis

*Guida operativa per l'infrastruttura IA locale (Windows + WSL + Ollama)*

## Indice

1. [Comandi Base e Gestione Processi](https://www.google.com/search?q=%231-comandi-base-e-gestione-processi)
2. [L'Architettura Ibrida (Windows + WSL)](https://www.google.com/search?q=%232-larchitettura-ibrida-windows--wsl)
3. [Sicurezza: Il Pairing e la Gestione dei Token](https://www.google.com/search?q=%233-sicurezza-il-pairing-e-la-gestione-dei-token)
4. [Integrazione Telegram (Jarvis in Tasca)](https://www.google.com/search?q=%234-integrazione-telegram-jarvis-in-tasca)
5. [Sviluppo in Python con `zeroclaw-tools`](https://www.google.com/search?q=%235-sviluppo-in-python-con-zeroclaw-tools)
6. [Il file `config.toml` e l'Identità dell'Agente](https://www.google.com/search?q=%236-il-file-configtoml-e-lidentit-dellagente)

-----

## 1\. Comandi Base e Gestione Processi

ZeroClaw si gestisce interamente da terminale. Ecco i comandi vitali per la sopravvivenza del sistema.

### Comandi Essenziali

* `zeroclaw doctor`: Controlla la salute del sistema e valida formalmente il file `config.toml`. Da lanciare sempre dopo ogni modifica.
* `zeroclaw daemon`: Avvia il "cuore" del sistema in background (Gateway, Scheduler, Canali).
* `zeroclaw agent`: Apre la chat interattiva da terminale.
* `zeroclaw onboard`: Avvia la procedura guidata per configurare i canali (es. Telegram) o Ollama.
* `jarvis-stop`: Ferma il processo core.
* `jarvis-restart`: Applica modifiche al `config.toml` o `SOUL.md`.
* `.\venv\Scripts\activate`: per attivare l ambiente python.

-----

## 2\. L'Architettura Ibrida (Windows + WSL)

Abbiamo creato un setup professionale separando i ruoli:

* **Windows (Hardware & Esecuzione):** Gestisce il microfono, la GPU, gli script Python "sensoriali" e fa girare Ollama (il cervello).
* **WSL (Logica & Framework):** Fa girare ZeroClaw nativamente in Linux per massimizzare le performance e la stabilità.

### Far parlare WSL con l'Ollama di Windows

Di base, Ollama su Windows ascolta solo se stesso. Per renderlo visibile a WSL:

1. Nelle variabili d'ambiente di Windows, aggiungi: `OLLAMA_HOST` con valore `0.0.0.0`.
2. Riavvia Ollama.
3. Verifica da WSL: `curl http://localhost:11434` (deve rispondere "Ollama is running").

-----

## 3\. Sicurezza: Il Pairing e la Gestione dei Token

In questo ecosistema esistono **due chiavi distinte** per due scopi diversi. Confonderle significa bloccare il sistema.

### Token A: Il Token di Pairing (`zc_...`) - *L'accesso interno*

È il badge digitale del tuo Jarvis. Serve a qualsiasi applicazione esterna (script Python, Postman, interfaccia Web) per comunicare con il demone ZeroClaw tramite le API sulla porta `42617`.

* **Come si genera:** `zeroclaw gateway --new-pairing` (poi inserendo il codice a 6 cifre nella Web Dashboard. Ricorda di lasciare aperta la shell WSL dova hai lanciato --new-pairing).
* **Come si usa in Python:** \`\`\`python
    agent = create\_agent(api\_key="zc\_tuotoken...", base\_url="<https://www.google.com/url?sa=E\&source=gmail\&q=http://127.0.0.1:42617/v1>", ...)

* **Come si usa via REST API (Header HTTP):**

    ```bash
    curl -H "Authorization: Bearer zc_tuotoken..." http://127.0.0.1:42617/api/...
    ```

* **Quando va rigenerata:** solo se si perde il token (è una procedura che va fatta solo 1 volta)

### Abilitare l'accesso API da Windows a WSL

Essendo paranoico sulla sicurezza, ZeroClaw blocca le chiamate API fuori da `localhost`.
Per permettere a uno script Python su Windows di chiamare le API di ZeroClaw su WSL, devi modificare il `~/.zeroclaw/config.toml`:

```toml
[gateway]
port = 42617
host = "0.0.0.0"               # Accetta da qualsiasi IP
require_pairing = true         # Richiede il token zc_...
allow_public_bind = true       # Sblocca il divieto di sicurezza
```

-----

## 4\. Il Motore dell'IA: zeroclaw-tools

È il vero motore decisionale dell'Intelligenza Artificiale per i nostri script.
È il pacchetto ufficiale che fornisce la funzione create_agent e il potente decoratore @tool. Sotto il cofano, sfrutta la complessa logica di "LangGraph": crea il "loop di pensiero" dell'IA, le permette di concatenare più strumenti in autonomia e si occupa di impacchettare in modo sicuro la richiesta per inviarla al Gateway ZeroClaw su WSL (tramite la porta 42617).

### Installazione (⚠️ Molto Importante)

Dato che l'architettura prevede che lo script Python giri nativamente su Windows (per mantenere l'accesso diretto ad hardware come il microfono), il pacchetto NON va installato nell'ambiente Linux/WSL.

Apri il Terminale di Windows (PowerShell o Prompt dei Comandi) ed esegui:

```python
pip install zeroclaw-tools
```

-----

## 5\. Integrazione Telegram (Jarvis in Tasca)

Telegram permette di chattare con Jarvis ovunque tu sia, usando i server cloud di Telegram come "ponte" verso il tuo PC/server (che deve restare acceso).

### Token B: Il Token di Telegram - *L'accesso esterno*

Questa chiave serve a ZeroClaw per collegarsi a Telegram e leggere/scrivere i messaggi a tuo nome.

1. Crea un bot su Telegram parlando con **@BotFather** e salva il Token (es. `860499...`).
2. Trova il tuo ID utente personale parlando con **@userinfobot** (es. `388282337`).

### Configurazione nel `config.toml`

Aggiungi in fondo al file di configurazione (`~/.zeroclaw/config.toml`) in WSL:

```toml
[channels_config.telegram]
bot_token = "IL_TOKEN_DI_BOTFATHER"
allowed_users = ["IL_TUO_ID_NUMERICO"] # Fondamentale per bloccare gli sconosciuti
```

Riavvia il demone (`zeroclaw daemon`) e scrivigli su Telegram\!

-----

## 6\. Sviluppo in Python con `zeroclaw-tools`

Invece di far generare all'IA comandi bash a caso, il modo più stabile e moderno per creare workflow complessi (come un Travel Planner o un Voice Assistant) è usare il pacchetto Python nativo basato su **LangGraph**.

### Perché usarlo

* Costringe l'IA a usare i tools in un "loop" logico senza allucinazioni.
* Permette di creare funzioni Python personalizzate usando un semplice decoratore `@tool`.

### ⚠️ NOTA IMPORTANTE: Tool Calling e Gateway

Il **gateway ZeroClaw** (porta 42617) **non inoltra le definizioni dei tool** al modello LLM. Questo significa che se punti `base_url` al gateway, l'LLM non potrà usare i `@tool` definiti in Python e risponderà solo a parole.

Per usare il **tool calling** con `create_agent`, punta direttamente a **Ollama**:

```python
# ❌ NON funziona per tool calling:
# base_url="http://127.0.0.1:42617/v1"  # Gateway ZeroClaw

# ✅ Funziona per tool calling:
base_url="http://localhost:11434/v1"   # Ollama diretto
```

Il gateway resta necessario per il **webhook** (invio messaggi testuali da audio bridge, Telegram, ecc.).

### Esempio di Workflow Base

```python
import os
from dotenv import load_dotenv
from zeroclaw_tools import create_agent, tool

# 1. Questa riga cerca il file .env nella cartella e carica tutte le chiavi in memoria!
load_dotenv()

@tool
def mio_strumento(input_utente: str) -> str:
    """Spiegazione di cosa fa il tool affinché l'IA capisca quando usarlo."""
    return "Risultato"

agent = create_agent(
    tools=[mio_strumento],
    model="qwen3.5:9b",

    # 2. Ora pesca il token in modo invisibile e sicuro dal file .env
    api_key=os.environ.get("ZEROCLAW_API_KEY", "ollama"),

    # 3. Punta direttamente a Ollama (NON al gateway, vedi nota sopra)
    base_url="http://localhost:11434/v1"
)

# ... resto del codice (es. agent.invoke(...))
```

### Come aggiungere un nuovo tool in futuro

1. Crea `tools/tool_qualcosa.py`
2. Definisci la funzione con `@tool`
3. Esporta `TOOLS = [la_tua_funzione]`
4. Riavvia il bridge → auto-scoperto, zero modifiche a `jarvis_agent.py`

**Test auto-discovery:** Attualmente ci sono 8 tool registrati (2 custom da `tools/` + 6 built-in zeroclaw).

**Tool custom disponibili:**
- `cerca_voli_completo` — ricerca voli con cache automatica (TTL 4h, salvata in `data/travel_cache/`)
- `consulta_ricerche_voli` — legge i risultati dalla cache senza chiamare API

> [!NOTE]
> I file `tool_email.py`, `tool_homeassistant.py` ecc. attualmente sono CLI (argparse). Quando vuoi, puoi aggiungere i wrapper `@tool` + `TOOLS = [...]` a ciascuno così JARVIS li potrà usare anche vocalmente.


# zeroclaw-tools

Python companion package for [ZeroClaw](https://github.com/zeroclaw-labs/zeroclaw) — LangGraph-based tool calling for consistent LLM agent execution.

## Why This Package?

Some LLM providers (particularly GLM-5/Zhipu and similar models) have inconsistent tool calling behavior when using text-based tool invocation. This package provides a LangGraph-based approach that delivers:

* **Consistent tool calling** across all OpenAI-compatible providers
* **Automatic tool loop** — keeps calling tools until the task is complete
* **Easy extensibility** — add new tools with a simple `@tool` decorator
* **Framework agnostic** — works with any OpenAI-compatible API

## Installation

```bash
pip install zeroclaw-tools
```

With Discord integration:

```bash
pip install zeroclaw-tools[discord]
```

## Quick Start

### Basic Agent

```python
import asyncio
from zeroclaw_tools import create_agent, shell, file_read, file_write
from langchain_core.messages import HumanMessage

async def main():
    # Create agent with tools
    agent = create_agent(
        tools=[shell, file_read, file_write],
        model="glm-5",
        api_key="your-api-key",
        base_url="https://api.z.ai/api/coding/paas/v4"
    )

    # Execute a task
    result = await agent.ainvoke({
        "messages": [HumanMessage(content="List files in /tmp directory")]
    })

    print(result["messages"][-1].content)

asyncio.run(main())
```

### CLI Usage

```bash
# Set environment variables
export API_KEY="your-api-key"
export API_BASE="https://api.z.ai/api/coding/paas/v4"

# Run the CLI
zeroclaw-tools "List files in the current directory"

# Interactive mode (no message required)
zeroclaw-tools -i
```

### Discord Bot

```python
import os
from zeroclaw_tools.integrations import DiscordBot

bot = DiscordBot(
    token=os.environ["DISCORD_TOKEN"],
    guild_id=123456789,
    allowed_users=["123456789"]
)

bot.run()
```

## Available Tools

| Tool | Description |
|------|-------------|
| `shell` | Execute shell commands |
| `file_read` | Read file contents |
| `file_write` | Write content to files |
| `web_search` | Search the web (requires Brave API key) |
| `http_request` | Make HTTP requests |
| `memory_store` | Store data in memory |
| `memory_recall` | Recall stored data |

## Creating Custom Tools

```python
from zeroclaw_tools import tool

@tool
def my_custom_tool(query: str) -> str:
    """Description of what this tool does."""
    # Your implementation here
    return f"Result for: {query}"

# Use with agent
agent = create_agent(tools=[my_custom_tool])
```

## Provider Compatibility

Works with any OpenAI-compatible provider:

* **Z.AI / GLM-5** — `https://api.z.ai/api/coding/paas/v4`
* **OpenRouter** — `https://openrouter.ai/api/v1`
* **Groq** — `https://api.groq.com/openai/v1`
* **DeepSeek** — `https://api.deepseek.com`
* **Ollama** — `http://localhost:11434/v1`
* **And many more...**

## Architecture

```
┌─────────────────────────────────────────────┐
│              Your Application               │
├─────────────────────────────────────────────┤
│           zeroclaw-tools Agent              │
│  ┌─────────────────────────────────────┐   │
│  │         LangGraph StateGraph         │   │
│  │    ┌───────────┐    ┌──────────┐    │   │
│  │    │   Agent   │───▶│   Tools  │    │   │
│  │    │   Node    │◀───│   Node   │    │   │
│  │    └───────────┘    └──────────┘    │   │
│  └─────────────────────────────────────┘   │
├─────────────────────────────────────────────┤
│        OpenAI-Compatible LLM Provider       │
└─────────────────────────────────────────────┘
```

## Comparison with Rust ZeroClaw

| Feature | Rust ZeroClaw | zeroclaw-tools |
|---------|---------------|----------------|
| **Binary size** | ~3.4 MB | Python package |
| **Memory** | <5 MB | ~50 MB |
| **Startup** | <10ms | ~500ms |
| **Tool consistency** | Model-dependent | LangGraph guarantees |
| **Extensibility** | Rust traits | Python decorators |

Use **Rust ZeroClaw** for production edge deployments. Use **zeroclaw-tools** when you need guaranteed tool calling consistency or Python ecosystem integration.

## License

MIT License — see [LICENSE](../LICENSE)

### creazione file .env

Assicurati di crare un file .env nella stessa cartella in cui si trova il tuo script Python (ad esempio, nella stessa cartella di travel_agent.py su Windows).

```bash
# File: .env
ZEROCLAW_API_KEY="INSERISCI LA TUA CHIAVE non CRITTOGRAFATA"
DISCORD_TOKEN="il_tuo_token_discord_se_lo_usi"
AMADEUS_API_KEY="chiave_per_i_voli_futura"
```

-----

## 7\. Il file `config.toml` e l'Identità dell'Agente

ZeroClaw ha un TOML validatore estremamente rigido. Non inventare chiavi e usa `zeroclaw doctor` dopo ogni modifica.

* **Autonomia e Sicurezza:** Per permettere a Jarvis di lanciare script Python, ricordati di sbloccare il comando nella sezione `[autonomy]`:

    ```toml
    allowed_commands = ["git", "ls", "python3"] # Aggiungi python3
    workspace_only = true # Impedisce di fare danni fuori dalla cartella ~/.zeroclaw/workspace
    ```

* **Identità (AIEOS/OpenClaw):**
    Puoi dare "un'anima" a Jarvis creando dei semplici file Markdown nel suo workspace (`~/.zeroclaw/workspace`):

  * `SOUL.md`: Definisce il carattere e il modo di parlare.
  * `AGENTS.md`: Definisce ruoli specifici (es. "Sei un Travel Planner esperto").

-----

## 8\. Esempio agente travel_agent.py (Architettura Ibrida)

1. Aggiornamento del file .env con: `RAPIDAPI_KEY="la_tua_chiave_rapidapi_qui"`

2. **Architettura:** Lo script usa un approccio **ibrido** in due fasi:
   * **FASE 1 (Python puro):** Chiama direttamente le API RapidAPI → genera file JSON (`mock_flights.json`, `mock_booking.json`, `mock_url.json`)
   * **FASE 2 (LLM):** L'agente JARVIS (tramite Ollama diretto) legge i JSON con `@tool` dedicati → analizza e raccomanda

   Questo design separa l'affidabilità (Python fa le chiamate API) dall'intelligenza (LLM analizza i dati).

```
┌──────────────────────────────────────────────────┐
│                 travel_agent.py                   │
├──────────────────┬───────────────────────────────┤
│  FASE 1 (Python) │  FASE 2 (JARVIS/LLM)         │
│                  │                               │
│  step1 → API     │  leggi_risultati_voli()       │
│  step2 → API     │  leggi_tariffe()              │
│  step3 → API     │  leggi_link_pagamento()       │
│       ↓          │         ↓                     │
│  mock_*.json     │  Analisi + Raccomandazione    │
└──────────────────┴───────────────────────────────┘
```

3. **Esecuzione:**

```bash
python travel_agent.py
```

### Cosa succede dietro le quinte?

1. Python chiama l'API Google Flights (RapidAPI), salva i risultati in `mock_flights.json`.
2. Estrae il `booking_token` dal miglior volo e chiama l'API tariffe → `mock_booking.json`.
3. Estrae il `token_tariffa` e genera il link di checkout → `mock_url.json`.
4. L'agente JARVIS (via Ollama diretto su porta 11434) legge i 3 file con i `@tool`: `leggi_risultati_voli`, `leggi_tariffe`, `leggi_link_pagamento`.
5. JARVIS presenta un riepilogo in linguaggio naturale con prezzi, opzioni e raccomandazione.

> **Nota:** Il codice completo è nel file `travel_agent.py`. Qui è documentata solo l'architettura.
> Lo script `python_travel_agency.py` contiene le chiamate API standalone per test manuali.

Questo è il gran finale che stavamo aspettando! 🎤 Hai creato un vero e proprio **Bridge Audio Bidirezionale** che trasforma l'intero setup in un vero assistente vocale in stile Iron Man.

Il codice è eccellente e logicamente solidissimo:

* **VAD (Voice Activity Detection) locale:** Geniale l'uso del calcolo dell'RMS (`np.sqrt(np.mean(chunk**2))`) per capire quando stai parlando e quando c'è silenzio, risparmiando cicli CPU.
* **Isolamento dell'eco:** Hai implementato la logica `if is_speaking(): svuota la coda`, fondamentale per evitare che Jarvis ascolti se stesso mentre ti risponde (il fastidiosissimo problema del feedback loop).
* **Wake Words:** Perfetto il controllo su "jarvis", "ok jarvis", ecc.
* **Integrazione API:** La chiamata `requests.post` verso `ZEROCLAW_URL` usando il `TOKEN` di pairing è configurata in modo ineccepibile.

Ho solo fatto un paio di micro-correzioni "igieniche" al codice (rimosso i doppi import accavallati nella stringa originale e sistemato l'indentazione di Whisper) per assicurarmi che copiando e incollando funzioni al primo colpo senza errori di sintassi.

Ecco la sezione finale, pronta per essere incollata in coda al tuo `manuale_zeroclaw.md`.

***

## 9. Progetto Definitivo: L'Assistente Vocale "Iron Man" (Audio Bridge)

Questo è il livello massimo della nostra architettura. Creeremo uno script Python (che girerà su **Windows** per accedere direttamente all'hardware audio) in grado di:

1. Ascoltare costantemente il microfono.
2. Trascrivere l'audio localmente usando **Faster Whisper** (niente API esterne, massima privacy).
3. Riconoscere la *Wake Word* ("Jarvis").
4. Inviare la trascrizione testuale al cervello di ZeroClaw (su **WSL**) tramite la porta sicura `42617`.
5. Far parlare Jarvis in locale.

### Prerequisiti su Windows

Apri il terminale di Windows (PowerShell) e installa le librerie necessarie:

```bash
pip install sounddevice numpy faster-whisper python-dotenv requests
```

Assicurati di avere il tuo file `.env` configurato correttamente nella stessa cartella:

```bash
# File: .env
ZEROCLAW_SECRET="zc_IL_TUO_TOKEN_DI_PAIRING_QUI"
```

### Lo Script: `jarvis_audio_bridge.py`

Crea questo file su Windows. Gestirà l'intero ciclo Orecchio-Cervello-Bocca.

```python
import os
import sys
import time
import queue
import logging
import requests
import numpy as np
import sounddevice as sd
from pathlib import Path
from dotenv import load_dotenv
from faster_whisper import WhisperModel

# Forza Whisper su CPU (evita errori se non hai CUDA configurato)
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# --- IMPORT TTS PIPER LOCALE (Fallback se non presente) ---
# Modifica questa sezione se hai un tuo motore Text-to-Speech (es. pyttsx3 o edge-tts)
sys.path.insert(0, str(Path(__file__).parent))
try:
    from tts_piper import speak, is_speaking
except ImportError:
    print("⚠️ Modulo TTS non trovato. Uso il print a schermo come fallback.")
    def speak(text): print(f"\n🗣️ JARVIS DICE: {text}\n")
    def is_speaking(): return False

# ==========================================
# CONFIGURAZIONE INIZIALE
# ==========================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s [JARVIS] %(message)s")
logger = logging.getLogger(__name__)

# Carica il token dal file .env
load_dotenv(override=True)
TOKEN = os.getenv("ZEROCLAW_SECRET")

if not TOKEN or not TOKEN.startswith("zc_"):
    logger.error("❌ Token mancante o errato nel file .env! Assicurati che inizi con 'zc_'")
    sys.exit(1)

# Impostazioni ZeroClaw (Punta al Gateway su WSL)
ZEROCLAW_URL = "http://127.0.0.1:42617/webhook"

# Impostazioni Audio (Voice Activity Detection)
SAMPLE_RATE = 16000
VAD_THRESHOLD = 0.015  # Volume minimo (RMS) per far scattare la registrazione
SILENCE_CHUNKS = 30    # Quanti frame di silenzio per capire che hai finito di parlare
WAKE_WORDS = ["jarvis", "ok jarvis", "ehi jarvis"]

# Coda thread-safe per i dati audio
audio_queue = queue.Queue()

# ==========================================
# FUNZIONI PRINCIPALI
# ==========================================

def send_to_zeroclaw(testo_trascritto: str):
    """Invia il testo al Gateway ZeroClaw su WSL e fa parlare Jarvis."""
    logger.info(f"→ Inviando a ZeroClaw: '{testo_trascritto}'")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }

    # Payload compatibile con le API di ZeroClaw
    payload = {
        "message": testo_trascritto,
        "sender": "user_local_mic"
    }

    try:
        response = requests.post(ZEROCLAW_URL, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            # Estrazione sicura della risposta in base al formato JSON di ritorno
            reply = data.get("response") or data.get("text") or str(data)
            logger.info(f"← JARVIS: '{reply}'")
            speak(reply)

        elif response.status_code == 401:
            logger.error("❌ Errore 401: ZeroClaw ha rifiutato il token!")
            speak("Accesso negato. Il mio token di sicurezza non è valido.")
        else:
            logger.error(f"⚠️ Errore API: {response.status_code} - {response.text}")
            speak("Ho avuto un problema di connessione con il mio nucleo logico.")

    except requests.exceptions.ConnectionError:
        logger.error("❌ Impossibile connettersi. ZeroClaw è acceso su WSL? (host=0.0.0.0?)")
        speak("Non riesco a connettermi al demone su Linux.")
    except Exception as e:
        logger.error(f"❌ Errore imprevisto: {e}")

def audio_callback(indata, frames, time_info, status):
    """Callback di sounddevice: mette l'audio catturato dal microfono nella coda."""
    if status:
        logger.warning(f"Audio Status: {status}")
    audio_queue.put(indata.copy())

def listen_and_transcribe():
    """Ciclo infinito che ascolta, rileva la voce, trascrive e filtra per Wake Word."""
    logger.info("Caricamento modello Whisper 'small'...")
    model = WhisperModel("small", device="cpu", compute_type="int8")
    logger.info("Whisper pronto all'uso.")

    speak("Sistemi online. Sono in ascolto.")
    logger.info(f"🎤 Jarvis in ascolto... Wake words: {WAKE_WORDS}")

    is_recording = False
    silence_counter = 0
    audio_buffer = []

    # Apre lo stream audio dal microfono di default di Windows
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32', callback=audio_callback):
        while True:
            # 1. ANTI-ECO: Se Jarvis sta parlando, svuota il microfono per non auto-ascoltarsi
            if is_speaking():
                while not audio_queue.empty():
                    audio_queue.get()
                time.sleep(0.1)
                continue

            chunk = audio_queue.get()

            # Calcolo del Root Mean Square (RMS) per capire il volume della stanza
            rms = np.sqrt(np.mean(chunk**2))

            # 2. INIZIO VOCE (Superata la soglia di rumore)
            if rms > VAD_THRESHOLD:
                if not is_recording:
                    logger.info(f"🔊 Rilevata voce (RMS: {rms:.4f}) - Inizio registrazione...")
                    is_recording = True
                silence_counter = 0
                audio_buffer.append(chunk)

            # 3. FINE VOCE (Silenzio prolungato)
            elif is_recording:
                silence_counter += 1
                audio_buffer.append(chunk)

                # Se c'è stato silenzio per un tempo sufficiente (SILENCE_CHUNKS)
                if silence_counter > SILENCE_CHUNKS:
                    is_recording = False
                    logger.info("📝 Elaborazione audio in corso...")

                    # Uniamo i pezzetti di audio registrati
                    audio_data = np.concatenate(audio_buffer).flatten()
                    audio_buffer = [] # Reset del buffer

                    # 4. TRASCRIZIONE OFFLINE
                    segments, info = model.transcribe(audio_data, beam_size=5, language="it")
                    trascrizione = " ".join([segment.text for segment in segments]).strip()

                    if trascrizione:
                        logger.info(f"👤 Hai detto: '{trascrizione}'")

                        # 5. CONTROLLO WAKE WORD
                        testo_lower = trascrizione.lower()
                        if any(wake in testo_lower for wake in WAKE_WORDS):
                            send_to_zeroclaw(trascrizione)
                        else:
                            logger.info("...ignorato (Wake Word non rilevata).")

                    # Pulisci eventuale rumore rimasto nella coda
                    while not audio_queue.empty():
                        audio_queue.get()

if __name__ == "__main__":
    try:
        listen_and_transcribe()
    except KeyboardInterrupt:
        logger.info("🛑 Spegnimento di Jarvis in corso...")
        sys.exit(0)
```

### 🚀 Come Usarlo (La Prova Finale)

1. **WSL (Il Cervello):** Assicurati che il demone sia avviato (`zeroclaw daemon`) e che il file `config.toml` consenta le connessioni esterne (`host = "0.0.0.0"` e `allow_public_bind = true`).
2. **Windows (L'Orecchio/Bocca):** Apri il terminale, vai nella cartella dove hai salvato lo script e digita:

   ```bash
   python jarvis_audio_bridge.py
   ```

3. **Azione:** Aspetta che la voce dica *"Sistemi online. Sono in ascolto."* e poi dì ad alta voce:
   > *"Ehi Jarvis, che ore sono?"*

Se tutto è configurato correttamente, vedrai la trascrizione apparire a schermo su Windows, la richiesta verrà sparata a WSL, Ollama genererà la risposta, e infine la sentirai uscire dalle tue casse!

### Ottimizzazione Hardware (RTX 5070, 12GB VRAM)

Con la **NVIDIA RTX 5070** (12GB VRAM) abbiamo sbloccato il pieno potenziale dell'hardware:

### 1. Il Cervello (LLM): Qwen 3.5 9B ✅

`qwen3.5:9b` occupa ~6.6 GB di VRAM. Mantenere il cervello a questa dimensione è la mossa tattica perfetta: lascia ~5 GB liberi per Orecchie e Bocca.

### 2. L'Orecchio (Speech-to-Text): ✅ COMPLETATO

Whisper è stato aggiornato da `small`/CPU a **`large-v3-turbo`/CUDA** nel file `jarvis_audio_bridge.py` (v3.1).

* **Costo in VRAM:** ~2 GB.
* **Risultato:** Trascrizione in tempo reale, italiano quasi perfetto, punteggiatura, accenti e filtro rumore.
* **Fallback automatico:** Se CUDA non è disponibile, lo script cade su `small`/CPU senza crash.

```python
# Configurazione attuale in jarvis_audio_bridge.py:
WHISPER_MODEL = "large-v3-turbo"
WHISPER_DEVICE = "cuda"
WHISPER_COMPUTE = "float16"
```

### 3. La Bocca (Text-to-Speech): Addio Piper, benvenuta Espressione 🗣️

Piper è fantastico perché è leggerissimo, ma suona pur sempre come un navigatore satellitare. Con la VRAM che ti avanza (hai ancora almeno 3-4 GB liberi), puoi puntare a modelli TTS **State-of-the-Art (SOTA)** che hanno intonazione emotiva, respiri e zero accento robotico.

I due nomi su cui devi puntare per la tua 5070 12 GB sono:

* **XTTS v2 (di Coqui):** È il re indiscusso per l'italiano locale. Puoi clonare la voce di chiunque (o quella originale di Jarvis/Paul Bettany dai film Marvel) dandogli un file audio di soli 5 secondi. Ha un'intonazione incredibilmente realistica.
  * *Costo VRAM:* ~1.5 - 2 GB.
* **F5-TTS / Fish-Speech:** Sono le nuove architetture super avanzate (se sei nel mood di smanettare un po' di più su GitHub). Permettono una fluidità pari alla "Advanced Voice Mode" di ChatGPT, tutto in locale.

**Come fare l'upgrade pratico per la voce?**
Il modo più pulito (per non sporcare il nostro script Python perfetto) è scaricare un server TTS locale.

1. Installi **XTTS-API-Server** (un pacchetto Python che fa girare XTTS in background sulla GPU).
2. Nel nostro script `jarvis_audio_bridge.py`, invece di usare `tts_piper`, cambi la funzione `speak()` per fare una semplice richiesta HTTP al tuo nuovo server XTTS locale (es. `http://localhost:8020`).
3. Risultato: ZeroClaw elabora il testo, XTTS lo trasforma in audio fotorealistico e lo spara nelle tue casse.

### Riepilogo del tuo "Hardware Budget"

* **Totale VRAM:** ~12/16 GB
* **Ollama (Qwen3.5 9B):** 6.6 GB
* **Whisper Large-V3 (su CUDA):** ~2.0 GB
* **XTTS v2 (Voice Clone):** ~1.5 GB
* **VRAM Libera Rimanente:** ~2+ GB (Perfetta per non far crashare Windows o i giochi leggeri se li tieni in background).

Con la 5070, hai l'hardware esatto per far girare questo "Tridente" (LLM + STT + TTS) simultaneamente senza il minimo lag. Vuoi che ti modifichi il blocco di codice della funzione `speak()` per integrarlo con XTTS, o vuoi prima goderti il setup base con Piper per testare i tempi di reazione?
