import os
import sys
import json
import urllib.request
import urllib.error

def do_research(query):
    # Prova entrambe le chiavi possibili dal .env
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Errore: GEMINI_API_KEY mancante nel file .env")
        return

    # Usiamo il modello pro testato funzionante per le ricerche serie
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"Agisci come un analista OSINT esperto. Effettua una ricerca profonda e iper-aggiornata sul seguente argomento: '{query}'. Restituisci un report dettagliato con cause, conseguenze, ultime notizie e fonti trovate sul web. Scrivi in markdown puro e formatta bene le tabelle se ci sono dati numerici."}]
        }],
        "tools": [{"googleSearch": {}}] # Abilita il Grounding nativo della Rete Google
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    
    try:
        print(f"📡 *Inoltro la query a Gemini 1.5 Pro sul cloud Google... Attendi...*\n")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            candidate = data.get('candidates', [{}])[0]
            content = candidate.get('content', {}).get('parts', [{}])[0].get('text', 'Nessun risultato testuale trovato.')
            
            print("=== 📝 REPORT DI DEEP RESEARCH ===\n")
            print(content)
            print("\n==================================")
            
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8')
        print(f"Errore API Gemini: {e.code} - {err_msg}")
    except Exception as e:
        print(f"Errore critico dello script di ricerca: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python deep_research.py \"tuo argomento\"")
    else:
        query = sys.argv[1]
        do_research(query)
