# TOOLS.md — Local Notes

Skills define HOW tools work. This file is for YOUR specifics —
the stuff that's unique to your setup.

## What Goes Here

Things like:
- SSH hosts and aliases
- Device nicknames
- Preferred voices for TTS
- Anything environment-specific

## Built-in Tools

- **shell** — Execute terminal commands
- Use when: running local checks, build/test commands, or diagnostics.
- Don't use when: a safer dedicated tool exists, or command is destructive without approval.
- **file_read** — Read file contents
- Use when: inspecting project files, configs, or logs.
- Don't use when: you only need a quick string search (prefer targeted search first).
- **file_write** — Write file contents
- Use when: applying focused edits, scaffolding files, or updating docs/code.
- Don't use when: unsure about side effects or when the file should remain user-owned.
- **memory_store** — Save to memory
- Use when: preserving durable preferences, decisions, or key context.
- Don't use when: info is transient, noisy, or sensitive without explicit need.
- **memory_recall** — Search memory
- Use when: you need prior decisions, user preferences, or historical context.
- Don't use when: the answer is already in current files/conversation.
- **memory_forget** — Delete a memory entry
- Use when: memory is incorrect, stale, or explicitly requested to be removed.
- Don't use when: uncertain about impact; verify before deleting.

- **excel_reader** — Leggi e analizza file Excel (.xlsx/.xls)
  - Use when: l'utente chiede di leggere dati da file Excel, tabelle, quotazioni.
  - How: `python3 ~/.zeroclaw/workspace/excel_reader.py <file> [--sheet NOME] [--range A1:D10] [--format markdown|csv|json]`
  - Skill: `skills/excel-reader/SKILL.md` per dettagli completi.
  - Don't use when: il file non è Excel (usa `file_read` per testo).

---
*Add whatever helps you do your job. This is your cheat sheet.*
