# AGENTS DIRECTORY

Questo file mappa i sub-agenti che Jarvis può invocare quando il task esula dalle sue competenze primarie (Gestione File System e Lettura), delegando il compito a strumenti o LLM specializzati.

---

## 1. Sub-Agente Domotica (Home Assistant)
**ID**: `sub_agente_domotica`
**Descrizione per il Router**:
"Chiama questo agente se e SOLO se l'utente richiede esplicitamente di interagire con il mondo fisico, controllare luci, accendere la televisione, avviare elettrodomestici, o conoscere lo stato dei sensori di casa."

**Tool di riferimento**:
Fa riferimento al tool descritto in `config.toml` alla voce `[[agents]]` di nome `sub_agente_domotica`, che eseguirà lo script `tool_homeassistant.py`.
Il tool prenderà in ingresso due parametri ("entity_id" e "service") e l'output verrà riversato nel contesto del sub-agente, che a sua volta risponderà all'utente.

**Direttive Esecutive Ereditate:**
- Tu e questo sub-agente condividete il vincolo tassativo per l'elaborazione **100% locale**.
- Non inviare *nessun* dato domotico all'esterno della rete LAN. L'API invocata dal tool validerà questo indirizzo in prima persona e causerà un blocco di sicurezza se violato.

---

## 2. Tool Email (SMTP Locale)
**ID**: `tool_email`
**Descrizione per il Router**:
"Chiama questo tool se e SOLO se l'utente chiede ESPLICITAMENTE di inviare un'email, un messaggio di posta, o di comunicare via email con qualcuno. NON usarlo per semplici ricerche di informazioni o per rispondere a messaggi. Il tool richiederà sempre conferma umana prima dell'invio."

**Tool di riferimento**:
Fa riferimento al tool descritto in `config.toml` alla voce `[tools.tool_email]`, che eseguirà lo script `tool_email.py`.
Il tool prenderà in ingresso i parametri `--to`, `--subject`, `--body` e opzionalmente `--account` (yahoo/gmail).

**Direttive di Sicurezza:**
- Inviare email SOLO a destinatari presenti nella `EMAIL_WHITELIST` nel `.env`.
- Richiedere SEMPRE conferma esplicita dall'utente prima dell'invio (Human-in-the-Loop).
- Non includere mai dati sensibili come password o token nel corpo dell'email.
- Preferire account 'yahoo' come default se non specificato.
