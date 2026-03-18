import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
import codecs

# Fix per console Windows (cp1252) che crasha con Emoji e Markdown
# Intercettiamo i chunk in write e sostituiamo i caratteri problematici
class SafeConsoleWriter:
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        if not isinstance(data, str):
            self.stream.write(data)
            return
            
        try:
            self.stream.write(data)
        except UnicodeEncodeError:
            # Codifica in ascii ignorando (o rimpiazzando) i caratteri problematici
            # per evitare crash completi dell'app
            safe_str = data.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
            self.stream.write(safe_str)

    def flush(self):
        self.stream.flush()
        
    def __getattr__(self, name):
        return getattr(self.stream, name)

_console_stream = SafeConsoleWriter(sys.stdout)

# Directory log sempre relativa alla root del progetto
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "jarvis.log"

LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_initialized = False

def get_logger(name: str) -> logging.Logger:
    """Restituisce un logger preconfigurato con rotazione file e console sicura per Windows."""
    global _initialized
    if not _initialized:
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)  # Il livello fine-grained è nei handler

        # Handler console: INFO e superiori
        console_handler = logging.StreamHandler(_console_stream)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

        # Handler file: DEBUG e superiori (log completi per diagnostica)
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=5_000_000,
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

        root.addHandler(console_handler)
        root.addHandler(file_handler)
        _initialized = True

    return logging.getLogger(name)
