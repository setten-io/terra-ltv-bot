import logging

from . import __version__ as version
from .bot import Bot
from .config import Config

log = logging.getLogger(__name__)


def entrypoint() -> None:
    log.info(f"starting terra-ltv-bot v{version}")
    config = Config.from_env()
    bot = Bot(config)
    bot.run()
