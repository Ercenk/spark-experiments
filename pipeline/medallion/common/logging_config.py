import logging
import sys

_DEF_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"

_configured = False

def configure_logging(level: str = "INFO"):
    global _configured
    if _configured:
        return
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(_DEF_FORMAT)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)
    _configured = True
