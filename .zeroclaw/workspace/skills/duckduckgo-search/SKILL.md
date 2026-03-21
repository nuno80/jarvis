---
name: duckduckgo-search
description: Esegue una ricerca web veloce e gratuita usando DuckDuckGo per trovare le ultime notizie o fatti su internet.
---

# DuckDuckGo Web Search

## Quando usarlo
- Quando l'utente ti chiede di cercare online, trovare le ultime notizie, o fare una ricerca su internet.
- Qualsiasi query su fatti recenti che non conosci, che non richiede "Ricerca Profonda".

## Come usarlo
Invoca lo script tramite il tool nativo `shell`. L'output tornerà formattato in Markdown con i 3 risultati principali pronti da leggere.

```bash
# Esempio pratico
python3 ~/.zeroclaw/workspace/tools/duckduckgo_search.py ultime notizie intelligenza artificiale
```

## Opzioni / Flag disponibili
- **`<query>`**: Tutto il testo passato dopo il comando è la tua chiave di ricerca (non c'è bisogno di mettere le virgolette in modo stretto).
- Cerca di inserire termini chiave, come su Google.

**Attenzione:** Se questo script fallisce per limite rate, o non trova risultati utili, informa l'utente o valuta la delega al Sub-Agente "deep_researcher" (che ha Google).
