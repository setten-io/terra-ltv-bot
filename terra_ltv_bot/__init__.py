import logging

__version__ = "0.1.0"

handler = logging.StreamHandler()
formater = logging.Formatter(
    "%(asctime)s - %(module)s.%(funcName)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formater)
logger = logging.getLogger()
logger.addHandler(handler)
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger(__name__).setLevel(logging.INFO)
