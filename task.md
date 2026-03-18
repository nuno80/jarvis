PROJECT JARVIS - Roadmap (v6.0 ZeroClaw Native)
Stato Progetto: Inizializzazione
Architettura: ZeroClaw (Rust) + Ollama (Qwen) + Python Tools

🟢 FASE 0: Base e Struttura
[x] Creazione directory base (/docs, /tools, /logs, /poc, .zeroclaw/workspace).

[x] Task 0.1 - Dipendenze: Creazione requirements.txt per i moduli Python.

[x] Task 0.2 - Validazione Base: Verifica python, ollama e tesseract su Windows.

🟠 FASE 1: I Mattoncini Sensoriali (Audio IN/OUT Python)
[x] Task 1.1 - PoC Audio IN: Script poc_listen.py (VAD + faster-whisper ITA).

[x] Task 1.2 - PoC Audio OUT: Test comparativo Piper TTS vs Kokoro TTS.

🟡 FASE 2: Core e Workspace ZeroClaw
[ ] Task 2.1 - Setup Qwen: Configurazione Ollama (qwen:9b).

[ ] Task 2.2 - Inizializzazione ZeroClaw: Esecuzione zeroclaw onboard e setup di base config.toml.

[ ] Task 2.3 - L'Anima di Jarvis: Stesura del prompt di sistema nel file SOUL.md.

🔵 FASE 3: Sviluppo Tools & Sub-Agenti
[ ] Task 3.1 - Tool OCR: tool_lettura.py (Tesseract/PyMuPDF).

[ ] Task 3.2 - Tool File System: tool_riordino.py con sandboxing forzato e attivazione Human-in-the-Loop (Yes/No).

[ ] Task 3.3 - Sub-Agente Domotica: Agente in AGENTS.md + tool_homeassistant.py forzato su elaborazione 100% locale.

🟣 FASE 4: Integrazione e Deploy H24
[ ] Task 4.1 - Audio Channeling: Connessione dei moduli Audio IN/OUT all'engine ZeroClaw.

[ ] Task 4.2 - Security Test: Tentare intenzionalmente violazioni di directory dal tool File System per verificare il blocco.

[ ] Task 4.3 - Demone Nativo: Installazione servizio via zeroclaw service install per esecuzione silente all'avvio.

5. PRIMO COMANDO ESECUTIVO (FASE 0)
Per iniziare:

Crea la cartella /docs e genera i tre file, copiando la roadmap in task.md.

Fornisci i comandi PowerShell per farmi eseguire il Task 0.2 (Validazione Base).

Fermati e chiedimi: "Documentazione creata. Hai verificato Python, Ollama e Tesseract?"
