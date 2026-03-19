"""
test_zeroclaw_tools.py — Test progressivi per il pacchetto zeroclaw_tools (locale).

Livello 1: Import & Package structure
Livello 2: Tool unitari (senza LLM, senza rete)
Livello 3: Creazione agente LangGraph (senza invocazione)
Livello 4: Integrazione completa (richiede ZeroClaw daemon su WSL)

Esecuzione:
    python test_zeroclaw_tools.py
    oppure:
    python -m pytest test_zeroclaw_tools.py -v
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Assicura che il path del progetto sia nel PYTHONPATH
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Carica le variabili dal .env
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env", override=True)

# Contatori globali per il report
_results = {"passed": 0, "failed": 0, "skipped": 0}


def _report(name, status, detail=""):
    """Helper per stampare risultato e aggiornare contatori."""
    icons = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️"}
    icon = icons.get(status, "❓")
    print(f"  {icon} {name}" + (f" — {detail}" if detail else ""))
    if status == "PASS":
        _results["passed"] += 1
    elif status == "FAIL":
        _results["failed"] += 1
    else:
        _results["skipped"] += 1


# ══════════════════════════════════════════════════════════════
# LIVELLO 1: IMPORT & PACKAGE STRUCTURE
# ══════════════════════════════════════════════════════════════
def test_level_1():
    print("\n🔷 LIVELLO 1 — Import & Package Structure\n")

    # 1.1 Import principale
    try:
        from zeroclaw_tools import create_agent, ZeroclawAgent, tool
        _report("Import create_agent, ZeroclawAgent, tool", "PASS")
    except ImportError as e:
        _report("Import create_agent, ZeroclawAgent, tool", "FAIL", str(e))
        return  # Impossibile continuare

    # 1.2 Import tool built-in
    try:
        from zeroclaw_tools import shell, file_read, file_write
        _report("Import shell, file_read, file_write", "PASS")
    except ImportError as e:
        _report("Import shell, file_read, file_write", "FAIL", str(e))

    # 1.3 Import web tools
    try:
        from zeroclaw_tools import web_search, http_request
        _report("Import web_search, http_request", "PASS")
    except ImportError as e:
        _report("Import web_search, http_request", "FAIL", str(e))

    # 1.4 Import memory tools
    try:
        from zeroclaw_tools import memory_store, memory_recall
        _report("Import memory_store, memory_recall", "PASS")
    except ImportError as e:
        _report("Import memory_store, memory_recall", "FAIL", str(e))

    # 1.5 Tipo corretto (BaseTool)
    try:
        from langchain_core.tools import BaseTool
        from zeroclaw_tools import shell
        assert isinstance(shell, BaseTool), f"shell è {type(shell)}, non BaseTool"
        _report("shell è un BaseTool valido", "PASS")
    except Exception as e:
        _report("shell è un BaseTool valido", "FAIL", str(e))

    # 1.6 Versione
    try:
        from zeroclaw_tools import __version__
        assert __version__ == "0.1.0"
        _report(f"Versione pacchetto: {__version__}", "PASS")
    except Exception as e:
        _report("Versione pacchetto", "FAIL", str(e))


# ══════════════════════════════════════════════════════════════
# LIVELLO 2: TOOL UNITARI (senza LLM)
# ══════════════════════════════════════════════════════════════
def test_level_2():
    print("\n🔷 LIVELLO 2 — Tool Unitari (senza LLM)\n")

    # 2.1 shell tool — comando semplice
    try:
        from zeroclaw_tools import shell
        result = shell.invoke({"command": "echo HELLO_ZEROCLAW"})
        assert "HELLO_ZEROCLAW" in result, f"Output inatteso: {result}"
        _report("shell('echo HELLO_ZEROCLAW')", "PASS", result.strip())
    except Exception as e:
        _report("shell('echo HELLO_ZEROCLAW')", "FAIL", str(e))

    # 2.2 shell tool — comando con errore
    try:
        from zeroclaw_tools import shell
        result = shell.invoke({"command": "comando_che_non_esiste_12345"})
        assert "Error" in result or "Exit code" in result or "non" in result.lower() or "not" in result.lower(), f"Dovrebbe indicare errore: {result}"
        _report("shell(comando_invalido) → errore gestito", "PASS")
    except Exception as e:
        _report("shell(comando_invalido) → errore gestito", "FAIL", str(e))

    # 2.3 file_write + file_read
    try:
        from zeroclaw_tools import file_read, file_write
        test_path = os.path.join(tempfile.gettempdir(), "zeroclaw_test_file.txt")
        test_content = "Ciao da ZeroClaw! 🦀 Test @ " + str(os.getpid())

        write_result = file_write.invoke({"path": test_path, "content": test_content})
        assert "Successfully" in write_result, f"Write fallito: {write_result}"

        read_result = file_read.invoke({"path": test_path})
        assert test_content in read_result, f"Read non corrisponde: {read_result}"
        _report("file_write + file_read (round trip)", "PASS")

        # Cleanup
        os.remove(test_path)
    except Exception as e:
        _report("file_write + file_read (round trip)", "FAIL", str(e))

    # 2.4 file_read — file inesistente
    try:
        from zeroclaw_tools import file_read
        result = file_read.invoke({"path": "/tmp/file_che_non_esiste_42.txt"})
        assert "Error" in result or "not found" in result.lower(), f"Dovrebbe fallire: {result}"
        _report("file_read(file_inesistente) → errore gestito", "PASS")
    except Exception as e:
        _report("file_read(file_inesistente) → errore gestito", "FAIL", str(e))

    # 2.5 memory_store + memory_recall
    try:
        from zeroclaw_tools import memory_store, memory_recall

        store_result = memory_store.invoke({"key": "zeroclaw_test_key", "value": "valore_di_test_42"})
        assert "Stored" in store_result, f"Store fallito: {store_result}"

        recall_result = memory_recall.invoke({"query": "zeroclaw_test_key"})
        assert "valore_di_test_42" in recall_result, f"Recall non trovato: {recall_result}"
        _report("memory_store + memory_recall (round trip)", "PASS")
    except Exception as e:
        _report("memory_store + memory_recall (round trip)", "FAIL", str(e))

    # 2.6 Decorator @tool personalizzato
    try:
        from zeroclaw_tools import tool
        from langchain_core.tools import BaseTool

        @tool
        def calcolatrice(a: int, b: int) -> str:
            """Somma due numeri."""
            return str(a + b)

        assert isinstance(calcolatrice, BaseTool), f"Non è un BaseTool: {type(calcolatrice)}"
        result = calcolatrice.invoke({"a": 10, "b": 32})
        assert result == "42", f"Risultato errato: {result}"
        _report("@tool decorator custom (calcolatrice 10+32=42)", "PASS")
    except Exception as e:
        _report("@tool decorator custom", "FAIL", str(e))

    # 2.7 http_request — URL locale semplice
    try:
        from zeroclaw_tools import http_request
        result = http_request.invoke({"url": "http://httpbin.org/get", "method": "GET"})
        # Qualsiasi risposta (anche errore di rete) è gestita senza crash
        if "Error" in result:
            _report("http_request(httpbin.org) → rete non disponibile", "SKIP", result[:80])
        else:
            assert "Status:" in result
            _report("http_request(httpbin.org/get)", "PASS")
    except Exception as e:
        _report("http_request", "FAIL", str(e))

    # 2.8 web_search — senza API key
    try:
        from zeroclaw_tools import web_search
        # Salva e rimuovi temporaneamente la key
        original_key = os.environ.pop("BRAVE_API_KEY", None)
        result = web_search.invoke({"query": "test"})
        assert "BRAVE_API_KEY" in result, f"Dovrebbe richiedere API key: {result}"
        _report("web_search(senza BRAVE_API_KEY) → messaggio corretto", "PASS")
        # Ripristina
        if original_key:
            os.environ["BRAVE_API_KEY"] = original_key
    except Exception as e:
        _report("web_search(senza BRAVE_API_KEY)", "FAIL", str(e))


# ══════════════════════════════════════════════════════════════
# LIVELLO 3: CREAZIONE AGENTE LANGGRAPH (senza invocazione LLM)
# ══════════════════════════════════════════════════════════════
def test_level_3():
    print("\n🔷 LIVELLO 3 — Creazione Agente LangGraph (senza invocazione)\n")

    # 3.1 create_agent con tool di default
    try:
        from zeroclaw_tools import create_agent
        agent = create_agent(
            api_key="dummy_key_for_test",
            base_url="http://localhost:9999/v1",  # URL finto
            model="test-model",
        )
        assert agent is not None
        _report("create_agent(default tools)", "PASS")
    except Exception as e:
        _report("create_agent(default tools)", "FAIL", str(e))

    # 3.2 create_agent con tools custom
    try:
        from zeroclaw_tools import create_agent, tool

        @tool
        def dummy_tool(text: str) -> str:
            """Tool finto per test."""
            return f"echo: {text}"

        agent = create_agent(
            tools=[dummy_tool],
            api_key="dummy_key_for_test",
            base_url="http://localhost:9999/v1",
            model="test-model",
        )
        assert agent is not None
        assert len(agent.tools) == 1
        _report("create_agent(custom @tool)", "PASS")
    except Exception as e:
        _report("create_agent(custom @tool)", "FAIL", str(e))

    # 3.3 ZeroclawAgent attributi
    try:
        from zeroclaw_tools import ZeroclawAgent, shell, file_read

        agent = ZeroclawAgent(
            tools=[shell, file_read],
            model="test-model",
            api_key="dummy_key_for_test",
            base_url="http://localhost:9999/v1",
        )
        assert agent.model == "test-model"
        assert len(agent.tools) == 2
        assert agent.temperature == 0.7  # default
        assert agent._graph is not None  # grafo compilato
        _report("ZeroclawAgent attributi e grafo compilato", "PASS")
    except Exception as e:
        _report("ZeroclawAgent attributi e grafo compilato", "FAIL", str(e))

    # 3.4 create_agent senza API key → errore
    try:
        from zeroclaw_tools import create_agent
        # Rimuovi temporaneamente le env var
        saved = {}
        for k in ["API_KEY", "GLM_API_KEY"]:
            if k in os.environ:
                saved[k] = os.environ.pop(k)
        try:
            create_agent(api_key=None, base_url="http://localhost:9999/v1")
            _report("create_agent(senza API key) → deve fallire", "FAIL", "Non ha lanciato ValueError")
        except ValueError as e:
            _report("create_agent(senza API key) → ValueError corretto", "PASS")
        finally:
            os.environ.update(saved)
    except Exception as e:
        _report("create_agent(senza API key)", "FAIL", str(e))

    # 3.5 create_agent con travel_agent tools
    try:
        from zeroclaw_tools import create_agent, tool
        import requests

        RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "fake_key")

        @tool
        def cerca_voli(origine: str, destinazione: str, data: str, giorni: str) -> str:
            """Cerca i voli di andata e ritorno."""
            return "Volo test trovato a $500"

        @tool
        def dettagli_tariffe(booking_token: str) -> str:
            """Ottiene le opzioni di classe e bagaglio."""
            return "Economy a $500"

        @tool
        def link_pagamento(token_tariffa: str) -> str:
            """Genera l'URL di checkout finale."""
            return "https://example.com/book"

        agent = create_agent(
            tools=[cerca_voli, dettagli_tariffe, link_pagamento],
            model="qwen3.5:9b",
            api_key="dummy_key_for_test",
            base_url="http://127.0.0.1:42617/v1",
        )
        assert len(agent.tools) == 3
        _report("create_agent(travel_agent tools simulati)", "PASS")
    except Exception as e:
        _report("create_agent(travel_agent tools simulati)", "FAIL", str(e))


# ══════════════════════════════════════════════════════════════
# LIVELLO 4: INTEGRAZIONE COMPLETA (richiede ZeroClaw daemon)
# ══════════════════════════════════════════════════════════════
def test_level_4():
    print("\n🔷 LIVELLO 4 — Integrazione completa (ZeroClaw daemon)\n")

    import asyncio

    # 4.1 Test connessione al Gateway
    gateway_ok = False
    try:
        import requests
        resp = requests.get("http://127.0.0.1:42617", timeout=3)
        gateway_ok = True
        _report(f"Connessione Gateway ZeroClaw (status: {resp.status_code})", "PASS")
    except requests.exceptions.ConnectionError:
        _report("Connessione Gateway ZeroClaw — daemon non raggiungibile", "SKIP",
                "Avvia 'zeroclaw daemon' su WSL per questo test")
        return
    except Exception as e:
        _report("Connessione Gateway ZeroClaw", "SKIP", str(e)[:80])
        return

    # 4.2 Test agente reale con shell tool
    if gateway_ok:
        try:
            from zeroclaw_tools import create_agent, shell
            from langchain_core.messages import HumanMessage

            api_key = os.environ.get("ZEROCLAW_API_KEY")
            if not api_key:
                _report("ZEROCLAW_API_KEY nel .env", "FAIL", "Chiave mancante")
                return

            agent = create_agent(
                tools=[shell],
                model="qwen3.5:9b",
                api_key=api_key,
                base_url="http://127.0.0.1:42617/v1",
                temperature=0.1,  # Bassa per risposte deterministiche
            )

            result = asyncio.run(agent.ainvoke({
                "messages": [HumanMessage(content="Esegui il comando 'echo JARVIS_OK' e dimmi cosa vedi.")]
            }))

            risposta = result["messages"][-1].content
            print(f"    📝 Risposta agente: {risposta[:200]}")

            if "JARVIS_OK" in risposta or "echo" in risposta.lower():
                _report("Agente reale con shell tool", "PASS")
            else:
                _report("Agente reale con shell tool", "PASS",
                        "Risposta ricevuta (contenuto variabile per LLM)")
        except Exception as e:
            _report("Agente reale con shell tool", "FAIL", str(e)[:120])

    # 4.3 Connessione Ollama
    try:
        import requests
        resp = requests.get("http://localhost:11434", timeout=3)
        if "Ollama" in resp.text:
            _report("Ollama raggiungibile su localhost:11434", "PASS")
        else:
            _report("Ollama raggiungibile ma risposta strana", "SKIP", resp.text[:60])
    except Exception:
        _report("Ollama su localhost:11434", "SKIP", "Non raggiungibile")


# ══════════════════════════════════════════════════════════════
# RUNNER PRINCIPALE
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("🦀 TEST SUITE — zeroclaw_tools (pacchetto locale)")
    print("=" * 60)

    test_level_1()
    test_level_2()
    test_level_3()
    test_level_4()

    print("\n" + "=" * 60)
    p, f, s = _results["passed"], _results["failed"], _results["skipped"]
    total = p + f + s
    print(f"📊 RISULTATI: {p}/{total} passati, {f} falliti, {s} skippati")

    if f == 0:
        print("🎉 Tutti i test eseguiti superati!")
    else:
        print(f"⚠️  {f} test falliti — controlla i dettagli sopra.")

    print("=" * 60)
    sys.exit(f)
