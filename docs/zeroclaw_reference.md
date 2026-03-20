# 📖 ZEROCLAW & JARVIS: ARCHITETTURA E REFERENCE (CORE)

Questa è la guida architetturale principale sul motore ZeroClaw e sul modo in cui interagisce nativamente con l'ambiente JARVIS e Windows/WSL2.

## 1. ZeroClaw - I Principi del Sistema
ZeroClaw non è un semplice "chatbot", è un sistema operativo runtime autonomo per i flussi di lavoro agentici. È costruito al 100% in **Rust** seguendo rigide performance ed efficienze:
* **Zero Overhead**: Richiede < 5MB di RAM e ha un Cold Start < 10ms.
* **Architettura a Trait**: È basato su un design completamente modulare. Provider, Canali, Tool (azioni), Memoria e Tunnels sono "plug & play", descritti da trait di programmazione (es: `src/providers/traits.rs` / `src/channels/traits.rs` in sorgente).
* **Cross-Hardware**: Può girare persino su board periferiche come Raspberry e chip ARM poveri, massimizzando le performance sulla macchina WSL2 ospite.

## 2. Configurazione Ottimizzata per JARVIS (Server WSL2 + Client Ollama Windows)
JARVIS utilizza ZeroClaw installato sotto sottosistema WSL2 (Debian) che invoca dinamicamente i modelli ospitati nell'istanza di Windows (che gestisce l'hardware della GPU, es. RTX 5070).

### Ollama Endpoint nel `config.toml`
Essendo Ollama in esecuzione su host Windows (accessibile via network bridging), il file `~/.zeroclaw/config.toml` DEVE puntare all'indirizzo WSL Gateway:
```toml
default_provider = "ollama"
default_model = "qwen3.5:9b"  # Oppure "qwen2.5-coder:32b" e altri
api_url = "http://172.20.80.1:11434" # Usa l'IP di bridge WSL2 di localhost host se necessario, o localhost 0.0.0.0 in Windows.
```

**Permessi in Windows:**
Affinchè WSL veda Ollama, nelle Variabili D'ambiente Windows inserire:
`OLLAMA_HOST=0.0.0.0`
E riavviare il servizio Ollama. Verificabile in WSL con `curl http://172.20.80.1:11434` o gli IP designati dal `resolve.conf`.

## 3. Gestione Sicurezza (Sandboxing e Permessi)
ZeroClaw ha la libertà di agire sulla macchina as-is, dipendendo e operando sull'ecosistema permissivo del demone:

* A differenza di framework isolati, i tool nativi scritti in shell o bash da JARVIS lavorano a **Livello OS Utente**. 
* **Controllo Autonomia**: Sotto `[autonomy]` del `config.toml`, limitare `allowed_commands` ad un array esplicito come `["python", "node", "git", "bash"]` protegge da escalation arbitrarie sui comandi core del terminale. C'è anche l'Emergency Stop (`estop`).
* **Protezione Dati Sensibili (`estop`)**: Il controllo E-Stop isola l'agente o disabilita tool temporanei senza spegnerlo (es. `zeroclaw estop --level network-kill`). 

## 4. Gestione Memoria (Hybrid RAG Vector/SQLite)
A differenza dei normali script agentici che si perdono token rapidamente, la `Memory` di ZeroClaw implementa un framework a due layer:
1. **Breve Termine (Session Context & Rolling Summary):** Aggregando dinamicamente il contenuto nei messaggi sistema, per default le ultime 50 conversazioni con una rielaborazione intelligente in caso scatti overflow context token.
2. **Lungo Termine (SQLite Vettoriale + FTS5):** Qualsiasi file di progetto salvato o tool invocato scrive in locale stringhe vettorializzate. Le ricerche future `memory_store` o query RAG fondono match semantici "Keyword Weight" a "Vector Weight" (Default nel config: 30% Keyword, 70% Vettori) offrendo altissima predizione anche via embedder locali.

## 5. Directory dell'Anima (`.zeroclaw/workspace`)
Il Workspace definisce come l'Agente e i Tool interagiscono:
* `config.toml`: Cuore di rotte, API keys, limiti, setup dei Canali.
* `SOUL.md`: Il prompt di sistema "master", la direttiva personale di JARVIS primordiale per quel singolo runtime.
* `AGENTS.md` o File di De-Delegazione: Configura istruzioni di workflow aggiuntive.
* Directory `skills/` : Contiene `.md` referenzianti i tool esterni sviluppati come script.

Per integrare nuovi skill e tool, consulta [ZeroClaw Tools (zeroclaw_tools.md)](./zeroclaw_tools.md).

## Reference Ufficiale
* OpenSource Repository: https://github.com/zeroclaw-labs/zeroclaw
* ZeroClaw Ufficial WebSite: https://zeroclawlabs.ai
