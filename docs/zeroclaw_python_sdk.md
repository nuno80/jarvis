# Sviluppo Script Python e Integrazione Custom (Windows \+ WSL)

Questa guida illustra come sviluppare script Python complessi (come un Voice Assistant o agenti che chiamano API pesanti) nell'ecosistema JARVIS, usando il dualismo Windows-WSL e il pacchetto `zeroclaw-tools`.

## 1. Architettura Windows vs WSL
A differenza delle Skill scritte nel workspace WSL che dipendono nativamente dal demone Linux, gli **script Python pesanti vanno eseguiti su Windows**.
Questo permette l'accesso diretto ai dispositivi hardware (es. Microfono per il Voice Activity Detection) e accelera i loop senza passare per le costrizioni del bridge audio/video di Virtual Machine.

Quindi la divisione netta è:
- **Windows:** Contiene lo script Python, l'ambiente, la cattura Microfono, il Text-to-Speech (TTS), e l'endpoint hardware del modello Ollama.
- **WSL (ZeroClaw):** Il runtime di ZeroClaw espone il gateway (porta 42617) a cui lo script Windows può lanciare testi trascritti dal mic per l'elaborazione dell'agente o la delega a canali.

## 2. Il Pacchetto `zeroclaw-tools` (Sviluppo LangGraph)
Al posto delle classiche skill di base, per workflow complessi si deve usare in Python la libreria `zeroclaw-tools` installata nell'ambiente Windows. Questa sfrutta un framework LangGraph assicurando che l'IA non abbia allucinazioni quando invoca strumenti (e cicla gli errori autonomamente).

### Definizione Strumenti con Decoratori
Per creare una competenza che l'IA possa usare in questo setup Windows, basta creare una semplice funzione annotata con `@tool`:

```python
from zeroclaw_tools import create_agent, tool

@tool
def verifica_condizioni_bancarie(conto_id: str) -> str:
    """Usa questo tool ogni volta che l'utente chiede il saldo. Ritorna il bilancio disponibile."""
    # Logica in python
    pass
```

### ⚠️ NOTA ARCHITETTURALE CRITICA PER IL TOOL CALLING: Gateway vs Ollama
C'è un limite tecnologico severo da conoscere: Il **gateway ZeroClaw (`127.0.0.1:42617`) NON inoltra le definizioni dei tool** esposti tramite Python/LangGraph al modello LLM.
Se in Python crei un agente puntando l'API al gateway, l'IA converserà ma NON userà i tuoi tool di Python.

Regola:
- **Per tool-calling complesso via Python (`zeroclaw-tools`):** Fai puntare la `base_url` dello script Python direttamente a **Ollama** (`http://localhost:11434/v1`).
- **Per inviare stringhe webhook o audio trascritto a ZeroClaw:** Fai puntare la chiamate HTTP `POST` a **ZeroClaw Gateway** (`http://127.0.0.1:42617/webhook`), autenticandoti.

Esempio Corretto Tool-Calling (bypassa il gateway, va dritto al cervello):
```python
agent = create_agent(
    tools=[mio_strumento_python],
    model="qwen3.5:9b",
    api_key="ollama", # Token Placeholder
    base_url="http://localhost:11434/v1" # CORRETTO!
)
```

## 3. Autenticazione Gateway (Il Token `zc_...`)
Per permettere a script Windows di inoltrare messaggi testuali (come nell'architettura Bridge Audio - dove il microfono Windows fa STT su GPU locale e butta la frase nel demone), devi autenticare lo script.

1. Lancia su WSL: `zeroclaw gateway --new-pairing`
2. Si genera un token tipo `zc_39fk20d...`. Mettilo nel file `.env` dello script Python su Windows.
3. Affinché WSL accetti input da Windows, nel `config.toml` su WSL occorre sbloccare la porta pubblica locale (se non era già fatto in automatico via WSL proxy):
```toml
[gateway]
port = 42617
host = "0.0.0.0"               # Accetta chiamate bridge
require_pairing = true         # Richiede token zc_
allow_public_bind = true       # Permette il binding su WSl
```

Chiamata bridge tipica via script python usando `requests`:
```python
import requests
headers = {"Content-Type": "application/json", "Authorization": "Bearer zc_IL_TOKEN"}
payload = {"message": "Trascrizione di quello che l'umano ha detto", "sender": "user_local_mic"}
response = requests.post("http://127.0.0.1:42617/webhook", headers=headers, json=payload)
print(response.json().get("response"))
```

## 4. Architettura Ibrida (Es. Il Bridge Vocale)
Un pattern comune in JARVIS è lo stack a tre componenti audio su RTX 5070:
1. **Orecchio (VAD + Whisper):** Gira su Windows in background, traccia i Root Mean Square (RMS) per captare la voce. Usa Whisper (su CUDA) o Faster Whisper estraendo audio via `sounddevice`.
2. **Cervello (Ollama):** Il modello puro. Consuma gran parte della VRAM (6+ GB). Risponde ai context hook esposti dal gateway (127.0.0.1:42617) o da LangGraph.
3. **Bocca (Text-to-Speech):** Soluzioni leggere (es. Piper TTS) o avanzate via API interne XTTSv2 in locale (consumo ~1.5 GB VRAM).
