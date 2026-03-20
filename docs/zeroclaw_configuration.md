# ZeroClaw Configuration & Providers Reference

ZeroClaw si configura primariamente tramite il file `~/.zeroclaw/config.toml`. Il runtime si aspetta che tutte le opzioni importanti siano centralizzate lì.

## Struttura Base del `config.toml`

I parametri core root decidono il comportamento autonomo:
```toml
default_provider = "openrouter"          # ID del Provider Principale
default_model = "anthropic/claude-sonnet-4-6"  # Modello del provider
default_temperature = 0.7                # Temperatura di base
api_url = "http://172.20.80.1:11434"     # Opzionale, l'URL specifico (es per Ollama su host Windows)
```

## `[autonomy]` - Sicurezza e Comandi Bash
Regola quanto potere ha l'LLM quando utilizza strumenti nativi come la shell bash o l'interazione su filesystem:
```toml
[autonomy]
level = "supervised"               # "read_only", "supervised", "full" (full riduce le interruzioni per conferma)
workspace_only = true              # Se true, limita i file e comandi dentro lo spazio locale dell'agente.
allowed_commands = ["git", "node", "python3"] # Comandi permessi nell'esecuzione bash. Il livello "full" richiede sempre questo. "*" lo permette tutto.
forbidden_paths = ["/etc", "/root", "~/.ssh"]
require_approval_for_medium_risk = true
```

## `[agent]` - Loop di Esecuzione Tool
```toml
[agent]
max_tool_iterations = 10     # Quanti turni di tool-call può fare al massimo per singolo prompt utente.
max_history_messages = 50    # Storico mantenuto nel breve termine.
parallel_tools = false       # Esecuzione parallela di chiamate tool simultanee.
```

## `[memory]` e Router

### Memoria ed Embedding
ZeroClaw possiede un sistema Ibrido SQL+Vettoriale:
```toml
[memory]
backend = "sqlite"            # "sqlite", "lucid", "markdown", "none"
embedding_provider = "openai" # oppure custom
embedding_model = "text-embedding-3-small"
vector_weight = 0.7
keyword_weight = 0.3
```

### Route: Selezione Modelli Dinamica (`[[model_routes]]`)
Permette al sistema di invocare modelli specifici in base ad hint (es. chiamare un modello di reasoning avanzato vs un modello rapido/veloce), utile nei tool personalizzati o negli script.
```toml
[[model_routes]]
hint = "reasoning"
provider = "openrouter"
model = "anthropic/claude-opus-4-20250514"

[[model_routes]]
hint = "code"
provider = "ollama"
model = "qwen2.5-coder:32b"
```

In uso basterà dire `hint:reasoning` quando si passa il parametro model al livello LLM API.

## Sub-Agents e Delega (`[agents.<name>]`)
Puoi definire all'interno di `config.toml` interi sub-agenti che il main bot può invocare:
```toml
[agents.coder]
provider = "ollama"
model = "qwen2.5-coder:32b"
system_prompt = "Sei un programmatore senior Python."
agentic = true
allowed_tools = ["shell", "file_read", "file_write"]
max_iterations = 5
```

## Lista dei Principali Provider ID Supportati
- `openrouter` (usa `OPENROUTER_API_KEY`)
- `anthropic` (usa `ANTHROPIC_API_KEY`)
- `openai` (usa `OPENAI_API_KEY`)
- `ollama` (usa `api_url` se remoto. Nessuna app key richiesta di base, accessibile in locale/Windows)
- `gemini` / `google` (usa `GEMINI_API_KEY`)
- Altri supportati: `moonshot` (kimi), `zai` (z.ai), `qwen` / `dashscope`, `groq`, `mistral`, `deepseek`, `xai` (grok).

## Provider Customizzati o Compatibili OpenAI
È possibile usare `custom:https://...` per fare overriding:
```toml
default_provider = "custom:https://your-api.example.com/v1"
```

## `[observability]`
Gestione dei TRACE per il debug di fallimenti dei tool call e dei formati output:
```toml
[observability]
runtime_trace_mode = "rolling" # Mantiene log locali su disco di ogni interazione
runtime_trace_path = "state/runtime-trace.jsonl"
```
Poi consultabile con `zeroclaw doctor traces --limit 20`.
