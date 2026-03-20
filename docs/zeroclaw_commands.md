# ZeroClaw CLI Commands Reference

Questa guida espone i comandi principali per operare e diagnosticare ZeroClaw via terminale (CLI).

## Comandi Principali (Top-Level)
- `zeroclaw onboard`: Inizializza il workspace/config in modo rapido o interattivo. Usa `--channels-only` per aggiornare solo i token. Usa `--force` se il config esiste già.
- `zeroclaw agent`: Esegue la chat interattiva (o invia un singolo messaggio tramite `-m`). Opzioni utili: `--provider <ID>`, `--model <MODEL>`, `--temperature <0.0-2.0>`.
- `zeroclaw gateway`: Avvia il server webhook/HTTP per la gestione di integrazioni esterne.
- `zeroclaw daemon`: Avvia il runtime supervisionato (gateway + canali + schedulatore opzionale). **Essenziale per eseguire canali come Telegram o Discord in background.**
- `zeroclaw service`: Gestione OS livello utente del lifecycle del servizio (`install`, `start`, `stop`, `restart`, `status`).
- `zeroclaw doctor`: Avvia la diagnostica e verifica la salute del sistema. Sottocomandi utili: `models` (per i modelli) e `traces` (per le tracce runtime).
- `zeroclaw status`: Stampa un sommario del sistema e della configurazione in uso.
- `zeroclaw estop`: Gestione del sistema di emergenza e "kill-switch".
- `zeroclaw cron`: Gestione dei task programmati schedulati (`list`, `add`, `remove`, `pause`).
- `zeroclaw models`: Aggiorna i cataloghi dei modelli dal provider. Es. `zeroclaw models refresh --provider ollama`.
- `zeroclaw channel`: Gestisce canali e salute (`list`, `start`, `doctor`, `bind-telegram`).
- `zeroclaw skills`: Installa e gestisci le skill custom (`list`, `audit`, `install`, `remove`). In fase di installazione esegue un audit di sicurezza automatico.
- `zeroclaw hardware` e `zeroclaw peripheral`: Gestione accessi hardware e board fisiche (STM32, Raspberry GPIO, ecc.).

## Comandi Operativi durante le sessioni attive (Chat Telegram / Discord)
Quando il demone (o `zeroclaw channel start`) è in esecuzione, l'agente risponde a questi comandi diretti in chat:
- `/models`: Mostra i provider disponibili e la selezione corrente.
- `/models <provider>`: Cambia il provider specificato per la sessione corrente dell'utente.
- `/model`: Mostra il modello corrente e la lista dei modelli in cache.
- `/model <model-id>`: Passa ad un modello specifico per l'utente corrente.
- `/new`: Cancella la memoria conversazionale e inizia una nuova sessione pulita.

> **Nota:** Il cambio in chat di provider/modello resetta solo la cronologia dell'utente per evitare contaminazione di contesto tra modelli.

## Autenticazione Subscription-Native (Es. OpenAI Codex / Claude Code)
I profili risiedono crittografati in `~/.zeroclaw/auth-profiles.json`.

```bash
# OpenAI Codex (ChatGPT Plus / Pro)
zeroclaw auth login --provider openai-codex --device-code
# Usare il profilo dedicato
zeroclaw agent --provider openai-codex --auth-profile openai-codex:work

# Anthropic (Claude)
zeroclaw auth paste-token --provider anthropic --profile default --auth-kind authorization
```
