# Guida Definitiva a ZeroClaw per LLM

Questa directory contiene la documentazione specializzata e modulare per **ZeroClaw** e il progetto **JARVIS**.

Questa struttura è stata progettata affinché gli **LLM** che supportano JARVIS (o altri tool) possano ricevere solo il contesto necessario e pertinente al loro compito attuale, risparmiando token e massimizzando il focus operativo.

## Indice Modulare (Scegli la guida corretta in base al Task)

Se ti viene richiesto di operare su ZeroClaw, usa quest'indice per determinare quale file consultare per completare il tuo lavoro.

### 1. Architettura Core
👉 **[Leggi `zeroclaw_reference.md`](./zeroclaw_reference.md)**

*Da consultare quando:* 
- L'utente chiede come è fatto ZeroClaw a livello di sistema.
- Devi capire come comunicano WSL2 e Windows, l'endpoint di Ollama, e i principi del sandboxing / E-stop.
- Ti servono le basi sul funzionamento della memoria ibrida (RAG vettoriale e SQLite).

### 2. Configurazione, Provider e Memoria
👉 **[Leggi `zeroclaw_configuration.md`](./zeroclaw_configuration.md)**

*Da consultare quando:*
- Devi configurare il file `~/.zeroclaw/config.toml`.
- Devi aggiungere un nuovo Provider AI (OpenAI, Anthropic, Gemini, Z.AI, local Ollama, ecc.).
- Devi capire i parametri base (`default_model`, `default_provider`, parametri RAG).
- Devi applicare un Routing (`[[model_routes]]`) o creare l'entry per un *Sub-Agent*.
- Devi disabilitare o gestire limitazioni sulle esecuzioni shell Bash dell'agente.

### 3. Sviluppo di Agenti e Orchestrazione
👉 **[Leggi `zeroclaw_agents.md`](./zeroclaw_agents.md)**

*Da consultare quando:*
- L'utente ti chiede di **"creare un nuovo agente"** o un workflow multi-agent.
- Devi scrivere o modificare i file `SOUL.md` (personalità, istruzioni sistema) e `AGENTS.md` (routing, trigger, cron job).
- Devi orchestrare più agenti per comunicare tra loro.

### 4. Sviluppo di Input / Output Canali (Telegram, Webhook, Discord)
👉 **[Leggi `zeroclaw_channels.md`](./zeroclaw_channels.md)**

*Da consultare quando:*
- Devi far comunicare un demone ZeroClaw tramite interfaccia chat o webhook (Telegram, Discord, Nextcloud Talk, WhatsApp, ecc.).
- Devi configurare o fare troubleshooting dell'`allowed_users` (Allowlist), dei token dei bot e del `[channels_config]`.

### 5. Sviluppo e Integrazione Tool (Skill / Custom Script)
👉 **[Leggi `zeroclaw_tools.md`](./zeroclaw_tools.md)**

*Da consultare quando:*
- L'utente ti chiede di creare, integrare o correggere un **Tool (Skill)**.
- Devi capire come l'agente esegue lo script backend (es. Python, Bash).
- Devi creare e strutturare il file `SKILL.md` in `~/.zeroclaw/workspace/skills/` affinché il LLM impari la competenza tramite il tool nativo `shell`.

### 6. Comandi CLI, Diagnostica e Diagnosi Operativa
👉 **[Leggi `zeroclaw_commands.md`](./zeroclaw_commands.md)**

*Da consultare quando:*
- Devi usare o suggerire l'utilizzo del terminale per operare su `zeroclaw`.
- Devi sapere a cosa servono comandi come `zeroclaw daemon`, `zeroclaw gateway`, `zeroclaw onboard`, `zeroclaw estop`, `zeroclaw channel start`.
- L'utente ti chiede di fare debugging via terminale o log in caso di crash o freeze del sistema.

### 7. Sviluppo Python, SDK (`zeroclaw-tools`) e Integrazione Hardware Windows
👉 **[Leggi `zeroclaw_python_sdk.md`](./zeroclaw_python_sdk.md)**

*Da consultare quando:*
- L'utente vuole creare uno script Python complesso su Windows (es. Agenti specifici API o l'Assistente Vocale / Audio Bridge).
- Devi sfruttare il pacchetto `zeroclaw-tools` con `@tool` via LangGraph.
- Ti serve capire quando l'API Base URL deve puntare al Gateway ZeroClaw (porta 42617) o direttamente ad Ollama (porta 11434).
- Devi autenticare uno script esterno usando il generatore dei token di pairing (`zc_...`).

---
**Regola per gli LLM**: Non tentare di processare tutte le guide insieme se non è strettamente necessario. Richiedi all'utente (o richiama l'abilità RAG) solo il/i file menzionato sopra coerente con la richiesta in corso.