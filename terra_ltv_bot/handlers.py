import asyncio
import logging

from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions import Throttled
from beanie.operators import All

from .models import Address
from .terra import FINDER_URL, Terra
from .utils import is_account_address

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
            "Currently only supports Anchor loans.\n"
            "\n"
            "/help\nDisplay this message.\n\n"
            "/subscribe account_address\nSubscribe to an address LTV alerts.\n\n"
            "/list\nList all subscribed addresses and their current LTV.\n\n"
            "/unsubscribe account_address\nUnsubscribe to an address LTV alerts.\n\n"
            "/ltv account_address\nRetreive LTV for an arbitrary address."
            "\n\n"
            "made with ♥ by Terra validator "
            "<a href='https://terra.setten.io/'>setten.io</a>"
        )

    async def subscribe(self, message: types.Message) -> None:
        try:
            await self.dp.throttle("add", rate=1)
        except Throttled:
            await message.reply("too many requests")
        else:
            log.info(f"@{message.from_user.username} {message.get_args()}")
            account_address = message.get_args().split(" ")[0]
            user_id = message.from_user.id
            if account_address:
                if is_account_address(account_address):
                    address = await Address.get_or_create(account_address)
                    if user_id in address.subscribers:
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
                        address.subscribers.append(user_id)
                        await address.save()
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
                else:
                    await message.reply("invalid account address")
            else:
                await message.reply("invalid format")

    async def list_(self, message: types.Message) -> None:
        try:
            await self.dp.throttle("add", rate=1)
        except Throttled:
            await message.reply("too many requests")
        else:
            log.info(f"@{message.from_user.username} {message.get_args()}")
            user_id = message.from_user.id
            reply = ""
            addresses = await Address.find(
                All(Address.subscribers, [user_id])
            ).to_list()
            ltvs = await asyncio.gather(
                *[self.terra.ltv(address.account_address) for address in addresses]
            )
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
            log.info(f"@{message.from_user.username} {message.get_args()}")
            account_address = message.get_args().split(" ")[0]
            user_id = message.from_user.id
            if account_address:
                if is_account_address(account_address):
                    address = await Address.get_or_create(account_address)
                    if user_id in address.subscribers:
                        address.subscribers.remove(user_id)
                        if not address.subscribers:
                            await address.delete()
                        else:
                            await address.save()
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
                        await message.reply(
                            "not subscribed to "
                            "<a href='{}{}/address/{}'>{}...{}</a>".format(
                                FINDER_URL,
                                self.terra.lcd.chain_id,
                                address.account_address,
                                address.account_address[:13],
                                address.account_address[-5:],
                            )
                        )
                else:
                    await message.reply("invalid account address")
            else:
                await message.reply("invalid format")

    async def ltv(self, message: types.Message) -> None:
        try:
            await self.dp.throttle("add", rate=1)
        except Throttled:
            await message.reply("too many requests")
        else:
            log.info(f"@{message.from_user.username} {message.get_args()}")
            account_address = message.get_args().split(" ")[0]
            if account_address:
                if is_account_address(account_address):
                    ltv = await self.terra.ltv(account_address)
                    await message.reply(f"{ltv}%" if ltv else "no loan found")
                else:
                    await message.reply("invalid account address")
            else:
                await message.reply("invalid format")
