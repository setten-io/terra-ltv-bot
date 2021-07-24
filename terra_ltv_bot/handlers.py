import asyncio
import logging

from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions import Throttled
from pymongo.errors import DuplicateKeyError

from .models import Address, Subscription
from .terra import FINDER_URL, Terra

log = logging.getLogger(__name__)


class Handlers:
    def __init__(self, dp: Dispatcher, terra: Terra) -> None:
        self.dp = dp
        self.terra = terra
        dp.register_message_handler(self.start, commands=["start", "help"])
        dp.register_message_handler(self.subscribe, commands=["subscribe"])
        dp.register_message_handler(self.list_, commands=["list"])
        dp.register_message_handler(self.unsubscribe, commands=["unsubscribe"])
        dp.register_message_handler(self.ltv, commands=["ltv"])

    async def start(self, message: types.Message) -> None:
        log.info(f"@{message.from_user.username} {message.get_args()}")
        await message.reply(
            "Terra LTV bot lets you subscribe to Terra addresses and receive "
            "alerts when they are close to liquidation on a spcific protocol.\n"
            "\n"
            "Supported protocols:\n"
            " - <a href='https://anchorprotocol.com'>Anchor</a> borrow "
            "(threshold: 35%)\n"
            "\n"
            "/help\nDisplay this message.\n\n"
            "/subscribe account_address\nSubscribe to an address LTV alerts.\n\n"
            "/list\nList all subscribed addresses and their current LTV.\n\n"
            "/unsubscribe account_address\nUnsubscribe to an address LTV alerts.\n\n"
            "/ltv account_address\nRetreive LTV for an arbitrary address."
            "\n\n"
            "made with ♥ by Terra validator "
            "<a href='https://terra.setten.io/'>setten.io</a>"
            " - "
            "<a href='https://github.com/setten-io/terra-ltv-bot'>source</a>"
        )

    async def subscribe(self, message: types.Message) -> None:
        try:
            await self.dp.throttle("add", rate=1)
        except Throttled:
            await message.reply("too many requests")
        else:
            user_id = message.from_user.id
            user_name = message.from_user.username
            args = message.get_args().split(" ")
            account_address = args[0] if 0 < len(args) else None
            alert_threshold = args[1] if 1 < len(args) else None
            log.info(f"{user_id} {user_name} {args}")
            if account_address:
                try:
                    address = await Address.find_one(
                        Address.account_address == account_address
                    )
                    if not address:
                        address = Address(account_address=account_address)
                        await address.insert()
                    subscription = await Subscription.find_one(
                        Subscription.address_id == address.id,
                        Subscription.protocol == "anchor",
                        Subscription.telegram_id == user_id,
                    )
                    if subscription:
                        if alert_threshold != subscription.alert_threshold:
                            subscription.alert_threshold = alert_threshold
                    else:
                        subscription = Subscription(
                            address_id=address.id,
                            protocol="anchor",
                            alert_threshold=alert_threshold or 45,
                            telegram_id=user_id,
                        )
                    await subscription.save()
                    await message.reply(
                        "subscribed to "
                        "<a href='{}{}/address/{}'>{}...{}</a>".format(
                            FINDER_URL,
                            self.terra.lcd.chain_id,
                            address.account_address,
                            address.account_address[:13],
                            address.account_address[-5:],
                        )
                    )
                except ValueError:
                    await message.reply(
                        "incorrect format, use:\n"
                        "<pre>/subscribe account_address "
                        "alert_threshold(optional, default=45)</pre>"
                    )
                except DuplicateKeyError:
                    await message.reply(
                        "already subscribed to "
                        "<a href='{}{}/address/{}'>{}...{}</a>".format(
                            FINDER_URL,
                            self.terra.lcd.chain_id,
                            address.account_address,
                            address.account_address[:13],
                            address.account_address[-5:],
                        )
                    )
            else:
                await message.reply("invalid format, missing account address")

    async def list_(self, message: types.Message) -> None:
        try:
            await self.dp.throttle("add", rate=1)
        except Throttled:
            await message.reply("too many requests")
        else:
            user_id = message.from_user.id
            user_name = message.from_user.username
            args = message.get_args().split(" ")
            log.info(f"{user_id} {user_name} {args}")
            addresses = [
                await Address.get(subscription.address_id)
                async for subscription in Subscription.find(
                    Subscription.telegram_id == user_id
                )
            ]
            ltvs = await asyncio.gather(
                *[self.terra.ltv(address.account_address) for address in addresses]
            )
            reply = ""
            for index, address in enumerate(addresses):
                ltv = str(ltvs[index])
                reply += "<a href='{}{}/address/{}'>{}...{}</a> {}%\n".format(
                    FINDER_URL,
                    self.terra.lcd.chain_id,
                    address.account_address,
                    address.account_address[:13],
                    address.account_address[-5:],
                    ltv if ltv else "-",
                )
            await message.reply(reply or "not subscribed to any address")

    async def unsubscribe(self, message: types.Message) -> None:
        try:
            await self.dp.throttle("add", rate=1)
        except Throttled:
            await message.reply("too many requests")
        else:
            user_id = message.from_user.id
            user_name = message.from_user.username
            args = message.get_args().split(" ")
            account_address = args[0] if 0 < len(args) else None
            log.info(f"{user_id} {user_name} {args}")
            if account_address:
                address = await Address.find_one(
                    Address.account_address == account_address
                )
                subscription = (
                    await Subscription.find_one(
                        Subscription.address_id == address.id,
                        Subscription.protocol == "anchor",
                        Subscription.telegram_id == user_id,
                    )
                    if address
                    else None
                )
                if subscription:
                    await subscription.delete()
                    await message.reply(
                        "unsubscribed from "
                        "<a href='{}{}/address/{}'>{}...{}</a>".format(
                            FINDER_URL,
                            self.terra.lcd.chain_id,
                            address.account_address,
                            address.account_address[:13],
                            address.account_address[-5:],
                        )
                    )
                else:
                    await message.reply("subscription not found")
            else:
                await message.reply("invalid format, missing account address")

    async def ltv(self, message: types.Message) -> None:
        try:
            await self.dp.throttle("add", rate=1)
        except Throttled:
            await message.reply("too many requests")
        else:
            user_id = message.from_user.id
            user_name = message.from_user.username
            args = message.get_args().split(" ")
            account_address = args[0] if 0 < len(args) else None
            log.info(f"{user_id} {user_name} {args}")
            if account_address:
                ltv = await self.terra.ltv(account_address)
                await message.reply(f"{ltv}%" if ltv else "no loan found")
            else:
                await message.reply("invalid format, missing account address")
