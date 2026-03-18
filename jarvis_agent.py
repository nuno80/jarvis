"""
jarvis_agent.py — Hub centrale dell'agente LLM locale per JARVIS.

Auto-scopre i tool dalla directory tools/ e crea un agente LangGraph
con Ollama diretto per tool calling affidabile.

Convenzione:
  Ogni file tools/tool_*.py esporta una lista TOOLS = [@tool, ...]
  Questo modulo li raccoglie tutti automaticamente.
"""

import os
import sys
import asyncio
import importlib
import importlib.util
import glob
from pathlib import Path
from dotenv import load_dotenv

# Assicura che la directory del progetto sia nel path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env", override=True)

from zeroclaw_tools import create_agent
# Tool built-in di zeroclaw-tools
from zeroclaw_tools import shell, file_read, file_write, http_request, memory_store, memory_recall
from langchain_core.messages import HumanMessage
from logger import get_logger

logger = get_logger("jarvis.agent")

# ==========================================
# CONFIGURAZIONE
# ==========================================
OLLAMA_BASE_URL = "http://localhost:11434/v1"
MODEL = "qwen3.5:9b"

SYSTEM_PROMPT = (
    "Sei JARVIS, un assistente personale intelligente che risponde in italiano. "
    "Hai a disposizione dei tool per eseguire azioni concrete. "
    "Usa i tool SOLO quando l'utente chiede qualcosa che richiede un'azione specifica "
    "(cercare voli, leggere/scrivere file, eseguire comandi, fare richieste HTTP, ecc.). "
    "Per domande generiche rispondi direttamente. "
    "Sii conciso e chiaro nelle risposte, massimo 3-4 frasi."
)


# ==========================================
# AUTO-DISCOVERY DEI TOOL
# ==========================================

def discover_tools() -> list:
    """
    Scansiona tools/tool_*.py e raccoglie tutti i TOOLS esportati.
    Ogni file deve definire: TOOLS = [tool1, tool2, ...]
    """
    tools_dir = PROJECT_ROOT / "tools"
    custom_tools = []

    if not tools_dir.exists():
        logger.warning(f"Directory tools/ non trovata in {PROJECT_ROOT}")
        return custom_tools

    for filepath in sorted(tools_dir.glob("tool_*.py")):
        module_name = filepath.stem  # es. "tool_travel"
        try:
            # Import dinamico del modulo
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Cerca la lista TOOLS nel modulo
            if hasattr(module, "TOOLS") and isinstance(module.TOOLS, list):
                custom_tools.extend(module.TOOLS)
                tool_names = [t.name for t in module.TOOLS]
                logger.info(f"  📦 {module_name}: {tool_names}")
            else:
                logger.debug(f"  ⏭️  {module_name}: nessun TOOLS esportato (skip)")

        except Exception as e:
            logger.warning(f"  ❌ {module_name}: errore import — {e}")

    return custom_tools


# ==========================================
# REGISTRO TOOL COMPLETO
# ==========================================

logger.info("Scoperta tool in corso...")

# 1. Tool custom dalla directory tools/
CUSTOM_TOOLS = discover_tools()

# 2. Tool built-in zeroclaw-tools
BUILTIN_TOOLS = [shell, file_read, file_write, http_request, memory_store, memory_recall]

# 3. Tutti i tool combinati
JARVIS_TOOLS = CUSTOM_TOOLS + BUILTIN_TOOLS

logger.info(f"Tool totali: {len(JARVIS_TOOLS)} ({len(CUSTOM_TOOLS)} custom + {len(BUILTIN_TOOLS)} built-in)")


# ==========================================
# CREAZIONE AGENTE (lazy, singleton)
# ==========================================

_agent = None


def _get_agent():
    """Crea l'agente al primo utilizzo."""
    global _agent
    if _agent is None:
        logger.info(f"Creazione agente: {MODEL} con {len(JARVIS_TOOLS)} tool...")
        _agent = create_agent(
            tools=JARVIS_TOOLS,
            model=MODEL,
            api_key=os.environ.get("ZEROCLAW_API_KEY", "ollama"),
            base_url=OLLAMA_BASE_URL,
            system_prompt=SYSTEM_PROMPT,
        )
        logger.info("Agente pronto.")
    return _agent


def ask_jarvis(text: str) -> str:
    """
    Invia un messaggio all'agente JARVIS locale.
    L'LLM decide autonomamente se usare un tool o rispondere direttamente.

    Returns:
        Risposta testuale, oppure None se l'agente fallisce (segnala fallback).
    """
    agent = _get_agent()

    try:
        result = asyncio.run(agent.ainvoke({
            "messages": [HumanMessage(content=text)]
        }))
        risposta = result["messages"][-1].content
        return risposta if risposta else "Non ho una risposta per questo."
    except Exception as e:
        logger.error(f"Errore agente: {e}", exc_info=True)
        return None  # Segnala al chiamante di usare il fallback


# ==========================================
# TEST STANDALONE
# ==========================================
if __name__ == "__main__":
    print("🧠 Test agente JARVIS locale\n")
    print(f"Tool registrati: {len(JARVIS_TOOLS)}")
    for t in JARVIS_TOOLS:
        print(f"  - {t.name}")

    print("\n" + "=" * 50)
    q = "Che ore sono?"
    print(f"👤 {q}")
    print(f"🤖 {ask_jarvis(q)}")
