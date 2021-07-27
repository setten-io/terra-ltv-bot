import logging

from aiogram import types
from aiogram.dispatcher import Dispatcher

# from .models import Address, Subscription
# from .terra import FINDER_URL, Terra
from .protocols import Protocol
from .utils import linkify

# from aiogram.utils.exceptions import Throttled
# from pymongo.errors import DuplicateKeyError


log = logging.getLogger(__name__)


class Handlers:
    def __init__(self, dp: Dispatcher, protocols: dict[str, Protocol]) -> None:
        self.dp = dp
        self.protocols = protocols
        dp.register_message_handler(self.subscribe, commands=["sub", "subscribe"])

    async def subscribe(self, message: types.Message) -> None:
        telregram_id = message.from_user.id
        args = message.get_args().split(" ")
        account_address = args[0] if 0 < len(args) else None
        protocol = self.protocols["anchor"]
        if account_address:
            subscription = await protocol.subscribe(
                account_address=account_address,
                alert_threshold=None,
                telegram_id=telregram_id,
            )
            await message.reply(
                "Subscribed:\n\n"
                f"{protocol.EMOJI} {protocol.SLUG.capitalize()}\n"
                f"Address: {linkify(account_address)}\n"
                f"Alert threshold: {subscription.alert_threshold}%\n"
            )
