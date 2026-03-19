# ZeroClaw Tools: Architettura e Integrazione Custom

Questa guida documenta come integrare strumenti personalizzati nell'ecosistema ZeroClaw corrente (che gira come binario Rust in WSL), basato sull'esperienza dell'integrazione del tool Excel.

## Architettura dei Tool in ZeroClaw

ZeroClaw supporta i tool a due livelli completamente diversi:

1. **Livello Nativo (Rust)**
   - I tool "core" (come `shell`, `file_read`, `memory_store`, ecc.) sono scritti in Rust.
   - Si trovano nella directory `src/tools/` del codice sorgente di ZeroClaw e implementano il trait `Tool`.
   - Vantaggi: Massima velocità, integrazione profonda col runtime, consistenza garantita del tool-calling tramite LangGraph.
   - Svantaggi: Richiedono la ricompilazione dell'intero eseguibile di ZeroClaw (`cargo build`) per aggiungere un nuovo tool.

2. **Livello Utente (Script + Skills in WSL)** *(L'approccio raccomandato)*
   - I tool custom vengono creati come script indipendenti (es. Python, Bash) all'interno del workspace di ZeroClaw (es. `~/.zeroclaw/workspace/`).
   - L'intelligenza artificiale (JARVIS) viene **istruita** su come e quando usarli tramite il sistema delle **Skills**.
   - JARVIS sfrutta il tool nativo `shell` per eseguire gli script custom passandogli gli argomenti appropriati.
   - Vantaggi: Sviluppo rapido, nessuna ricompilazione, facile testing manuale, debug immediato.

---

## Come Creare un Tool Custom (Il Metodo Script + Skill)

Questo è il workflow esatto usato per creare il tool `excel_reader`:

### Step 1: Creare lo Script "Strumento" (Backend)

Crea uno script robusto nel tuo workspace (es. `~/.zeroclaw/workspace/mio_tool.py`).
Lo script deve avere tre caratteristiche fondamentali per lavorare bene con un LLM:

1. **Gestione degli argomenti CLI**: Usa `argparse` o simili per ricevere input puliti dalla shell.
2. **Formattazione Output LLM-Friendly**: L'output deve essere facilmente interpretabile dal modello. Formati come tabelle Markdown, liste formattate o piccoli JSON sono ideali.
3. **Protezione contro l'Overflow di Contesto**: I file possono essere enormi (es. Excel con 100k righe). L'LLM crasherà o perderà il contesto se riceve tutto. Lo script DEVE testare la dimensione dell'output o forzare una paginazione/limite di righe rigido (es. limitare sempre l'output a max 50KB o 100 righe di default).

*Esempio: L'`excel_reader.py` espone flag come `--max-rows`, `--range A1:B10` e un limite hardcoded di 50_000 byte per sicurezza.*

### Step 2: Insegnare all'Agente ad usarlo (La Skill)

Crea un file in `~/.zeroclaw/workspace/skills/<nome-tool>/SKILL.md`. 
Questo file usa il formato standard di ZeroClaw per definire una skill.

```markdown
---
name: nome-del-mio-tool
description: Breve descrizione di cosa fa
---

# Titolo Tool

## Quando usarlo
- (Scrivi qui l'elenco dei trigger testuali o logici. Es. "L'utente parla di fogli di calcolo")
- (Cosa l'utente deve aver chiesto)

## Come usarlo
Invoca lo script tramite il tool nativo `shell`:

```bash
# Esempio pratico 1
python3 ~/.zeroclaw/workspace/mio_tool.py <argomenti>

# Esempio pratico 2 (opzioni diverse)
python3 ~/.zeroclaw/workspace/mio_tool.py --flag
```

## Opzioni / Flag disponibili
- Dettaglia le opzioni che hai inserito in `argparse`. Questo fa sì che l'LLM capisca come adattare i comandi alle richieste dell'utente.
```

### Step 3: Mappatura Rapida in TOOLS.md

Per facilitare il fetch rapido da parte di JARVIS, aggiungi il nuovo tool al dizionario locale `TOOLS.md` presente nella radice del workspace:

```markdown
- **nome_tool** — (Descrizione rapida)
  - Use when: (caso d'uso principale)
  - How: `python3 ~/.zeroclaw/workspace/mio_tool.py <args>`
  - Skill: `skills/nome-tool/SKILL.md` (riferimento al file completo)
```

### Step 4: Testing

Testa rigorosamente lo script in WSL usando esattamente lo stesso runtime/environment di JARVIS. Assicurati che eventuali librerie esterne (es. `openpyxl`, `pandas`) siano installate nel WSL o nell'ambiente Python usato da `python3` nel workspace.

---

## Riepilogo Tool Custom Correnti

| Nome Tool | Script Backend | Descrizione | Path Skill |
|-----------|----------------|-------------|------------|
| **excel_reader** | `excel_reader.py` | Estrae e formatta dati da `.xlsx/.xls` con supporto a selezione foglio e range. Output in MD, CSV, JSON. | `skills/excel-reader/SKILL.md` |
