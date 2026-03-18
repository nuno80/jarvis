"""
test_tools.py — Test unitari per i tool critici di JARVIS.
Focus: sicurezza (sandboxing, whitelist) senza side-effect reali.

Esecuzione:
    python test_tools.py
    oppure:
    python -m pytest test_tools.py -v
"""

import sys
import os
from pathlib import Path

# Aggiunge la root al path per importare logger
sys.path.insert(0, str(Path(__file__).parent))

# Imposta variabili d'ambiente di test PRIMA degli import dei tool
os.environ.setdefault("ZEROCLAW_SECRET", "test_secret")
os.environ.setdefault("HA_URL", "http://homeassistant.local:8123")
os.environ.setdefault("HA_TOKEN", "fake_token_for_testing")
os.environ.setdefault("YAHOO_EMAIL", "test@yahoo.it")
os.environ.setdefault("YAHOO_APP_PASSWORD", "fake_pass")
os.environ.setdefault("GMAIL_EMAIL", "test@gmail.com")
os.environ.setdefault("GMAIL_APP_PASSWORD", "fake_pass")
os.environ.setdefault("EMAIL_WHITELIST", "armandoluongo@yahoo.it,nuno.80.al@gmail.com")


# ==========================================
# TEST tool_homeassistant.py
# ==========================================
def test_ha_local_network_valid():
    """URL locali devono essere accettati."""
    sys.path.insert(0, str(Path(__file__).parent / "tools"))
    from tool_homeassistant import is_local_network
    assert is_local_network("http://192.168.1.100:8123") is True
    assert is_local_network("http://homeassistant.local:8123") is True
    assert is_local_network("http://127.0.0.1:8123") is True
    assert is_local_network("http://10.0.0.5:8123") is True
    print("✅ test_ha_local_network_valid — OK")


def test_ha_local_network_invalid():
    """URL non locali devono essere rifiutati (sicurezza)."""
    from tool_homeassistant import is_local_network
    assert is_local_network("https://external-api.com") is False
    assert is_local_network("http://8.8.8.8:8123") is False
    assert is_local_network("") is False
    assert is_local_network(None) is False
    print("✅ test_ha_local_network_invalid — OK")


# ==========================================
# TEST tool_riordino.py
# ==========================================
def test_riordino_sandbox_blocks_system_paths():
    """Path di sistema non devono essere autorizzati."""
    from tool_riordino import is_path_allowed
    assert is_path_allowed("C:/Windows/System32") is False
    assert is_path_allowed("C:/Users/Nuno/Documents") is False
    assert is_path_allowed("C:/") is False
    print("✅ test_riordino_sandbox_blocks_system_paths — OK")


def test_riordino_sandbox_allows_drop_subpath():
    """Il path autorizzato (Jarvis_Drop) deve essere permesso."""
    from tool_riordino import is_path_allowed
    # Nota: la directory non deve esistere per il test del path check
    result = is_path_allowed("C:/Users/Nuno/Desktop/Jarvis_Drop/test")
    assert result is True
    print("✅ test_riordino_sandbox_allows_drop_subpath — OK")


def test_riordino_sandbox_blocks_traversal():
    """Path traversal non deve bypassare il sandboxing."""
    from tool_riordino import is_path_allowed
    assert is_path_allowed("C:/Users/Nuno/Desktop/Jarvis_Drop/../../Documents") is False
    print("✅ test_riordino_sandbox_blocks_traversal — OK")


# ==========================================
# TEST tool_email.py
# ==========================================
def test_email_whitelist_valid():
    """Destinatari nella whitelist devono essere permessi."""
    from tool_email import is_recipient_allowed
    assert is_recipient_allowed("armandoluongo@yahoo.it") is True
    assert is_recipient_allowed("nuno.80.al@gmail.com") is True
    # Case insensitive
    assert is_recipient_allowed("ARMANDOLUONGO@YAHOO.IT") is True
    print("✅ test_email_whitelist_valid — OK")


def test_email_whitelist_invalid():
    """Destinatari non in whitelist devono essere bloccati."""
    from tool_email import is_recipient_allowed
    assert is_recipient_allowed("hacker@evil.com") is False
    assert is_recipient_allowed("random@test.it") is False
    assert is_recipient_allowed("") is False
    print("✅ test_email_whitelist_invalid — OK")


def test_email_unknown_account():
    """Account non supportato deve restituire errore senza crash."""
    from tool_email import send_email
    # Bypassa HitL per test — l'errore account viene prima del HitL
    result = send_email("armandoluongo@yahoo.it", "Test", "Corpo", account="hotmail")
    assert "[ERRORE]" in result
    print("✅ test_email_unknown_account — OK")


def test_email_blocked_recipient():
    """Destinatario non in whitelist deve essere bloccato prima del HitL."""
    from tool_email import send_email
    result = send_email("stranger@danger.com", "Test", "Corpo", account="yahoo")
    assert "[ERRORE DI SICUREZZA]" in result
    print("✅ test_email_blocked_recipient — OK")


# ==========================================
# RUNNER
# ==========================================
if __name__ == "__main__":
    print("\n=== Test Suite JARVIS Tools ===\n")
    tests = [
        test_ha_local_network_valid,
        test_ha_local_network_invalid,
        test_riordino_sandbox_blocks_system_paths,
        test_riordino_sandbox_allows_drop_subpath,
        test_riordino_sandbox_blocks_traversal,
        test_email_whitelist_valid,
        test_email_whitelist_invalid,
        test_email_unknown_account,
        test_email_blocked_recipient,
    ]

    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"❌ {test.__name__} — FALLITO: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} — ERRORE: {e}")
            import traceback; traceback.print_exc()
            failed += 1

    print(f"\n{'🎉 Tutti i test superati!' if failed == 0 else f'⚠️ {failed} test falliti.'}")
    sys.exit(failed)
