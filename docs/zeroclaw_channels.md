# ZeroClaw Channels Reference

Questa guida illustra la configurazione e gestione dei "Canali" (Telegram, Discord, Nextcloud Talk, ecc.), i front-end di comunicazione attraverso i quali gli utenti o i demoni conversano con ZeroClaw.

Tutte queste configurazioni risiedono in `config.toml` sotto la namespace `[channels_config]`.

> **Nota Fondamentale:** 
> I canali necessitano del comando `zeroclaw daemon` o `zeroclaw gateway` in esecuzione per poter operare in ascolto. (In alternativa `zeroclaw channel start`).

## Regole di Sicurezza: Allowlist
Ogni canale usa una logica "Deny-by-default". Se l'allowlist è vuota, blocca tutto.
- Per permettere un ID Telegram specifico: `allowed_users = ["12345678", "admin_username"]`
- Disabilitare i controlli (sconsigliato in prod): `allowed_users = ["*"]`

## Configurazione dei Canali Principali

### Telegram
Lavora tramite "polling", non serve una porta esposta o IP pubblico.
```toml
[channels_config.telegram]
bot_token = "IL_TUO_BOT_TOKEN_TELEGRAM"
allowed_users = ["il_tuo_username_senza_chiocciola"]
stream_mode = "off"               # off | partial (streaming live parziale della risposta)
interrupt_on_new_message = false  # Se true, annulla processamenti lunghi all'arrivo di nuovo messaggio per aggiornare contesto
```

### Discord
Lavora via Gateway/WebSocket. Zero esposizione in porta.
```toml
[channels_config.discord]
bot_token = "discord-bot-token"
guild_id = "123456789012345678"   # opzionale, limita ad un server
allowed_users = ["*"]
mention_only = false              # se true, ZeroClaw risponderà solo se direttamente taggato.
```

### Nextcloud Talk
Utilizza un Webhook interno di ricezione (`POST /nextcloud-talk`). **Serve una porta esposta o Reverse Proxy / Tunnel verso la porta del gateway ZeroClaw (default `42617`)**.
```toml
[channels_config.nextcloud_talk]
base_url = "https://tuo-cloud.domain.com"
app_token = "nextcloud-talk-app-token"      # Il token del Bot su Nextcloud (da creare)
webhook_secret = "segreto_personale"         # Firma webhook, consigliato.
allowed_users = ["nuno"]                    # L'utente ammesso al dialogo su NC Talk.
```

### Altri canali Supportati
- **Slack**, **Mattermost**: Via Event API o Webhook/Polling.
- **WhatsApp**: Modalità Cloud API o Web Mode (headless browser).
- **Email**: Polling IMAP, Invio MQTT.
- **Matrix**: Integrazione profonda (inclusiva di E2EE end-to-end encryption device).
- **Signal**: Tramite signal-cli e http bridge.

## Troubleshooting Rapido
Se il canale sembra avviato ma il demone non risponde ai messaggi:
1. **Allowlist Mismatch**: Controllare i log di `zeroclaw daemon`. Se appare _"ignoring message from unauthorized user"_, allora il nome utente/numero inserito nell'allowlist è incorretto o manca.
2. **Tunneling su Webhook**: Se si usa Nextcloud Talk, Linq o un Webhook custom, assicurarsi che URL HTTPS punti esattamente al server ZeroClaw (es tramite Ngrok, Nginx proxy su WSL).
3. **Mancanza Riavvio**: Ogni cambio a `config.toml` sui canali richiede il riavvio manuale del deamon: `zeroclaw service restart` o riavviando il terminale attivo di `zeroclaw daemon`.
