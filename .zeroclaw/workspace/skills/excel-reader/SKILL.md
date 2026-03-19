---
name: excel-reader
description: Leggi e analizza file Excel (.xlsx/.xls) nel workspace
---

# Excel Reader

Usa questo skill quando l'utente chiede di leggere, analizzare o estrarre dati da file Excel.

## Quando usarlo

- L'utente menziona **Excel**, **foglio di calcolo**, **spreadsheet**, **.xlsx**, **.xls**
- L'utente chiede di vedere **dati**, **tabelle**, **quotazioni** da un file
- L'utente chiede di **convertire** Excel in CSV o JSON

## Come usarlo

Invoca lo script tramite il tool `shell`:

```bash
# Leggi il file (prime 100 righe, formato markdown)
python3 ~/.zeroclaw/workspace/excel_reader.py /percorso/file.xlsx

# Elenca i fogli disponibili
python3 ~/.zeroclaw/workspace/excel_reader.py /percorso/file.xlsx --list-sheets

# Leggi un foglio specifico
python3 ~/.zeroclaw/workspace/excel_reader.py /percorso/file.xlsx --sheet "Foglio2"

# Leggi un range di celle
python3 ~/.zeroclaw/workspace/excel_reader.py /percorso/file.xlsx --range A1:D20

# Output in formato JSON
python3 ~/.zeroclaw/workspace/excel_reader.py /percorso/file.xlsx --format json --max-rows 50

# Output in formato CSV
python3 ~/.zeroclaw/workspace/excel_reader.py /percorso/file.xlsx --format csv

# Senza intestazione (colonne numerate)
python3 ~/.zeroclaw/workspace/excel_reader.py /percorso/file.xlsx --no-header
```

## Opzioni complete

| Opzione         | Descrizione                               | Default    |
|-----------------|-------------------------------------------|------------|
| `--sheet NOME`  | Nome del foglio da leggere                | primo      |
| `--range A1:D10`| Range celle da estrarre                   | tutto      |
| `--format FMT`  | markdown, csv, json                       | markdown   |
| `--max-rows N`  | Numero massimo righe                      | 100        |
| `--header ROW`  | Riga intestazione (1-indexed)             | 1          |
| `--no-header`   | Non usare intestazione                    | false      |
| `--list-sheets` | Elenca fogli disponibili                  | false      |

## Posizione file Excel nel workspace

I file Excel dell'utente si trovano tipicamente in:
- `~/.zeroclaw/workspace/` — workspace corrente
- Percorsi assoluti forniti dall'utente

## Note

- L'output è limitato a 50KB per evitare overflow di contesto
- Il default è 100 righe; usa `--max-rows` per aumentare se necessario
- Per file grandi, consiglia all'utente di usare `--range` o `--max-rows`
